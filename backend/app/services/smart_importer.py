"""Smart CSV/Excel Importer with Heuristic Analysis

A robust file importer using chardet and csv.Sniffer for automatic detection.
"""

import os
import csv
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

import pandas as pd
import numpy as np

# Optional chardet for better encoding detection
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

logger = logging.getLogger(__name__)


class FileType(Enum):
    CSV = "csv"
    TSV = "tsv"
    XLSX = "xlsx"
    XLS = "xls"
    ODS = "ods"
    XLSB = "xlsb"
    UNKNOWN = "unknown"


class ImportSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ImportMessage:
    severity: ImportSeverity
    code: str
    message: str
    suggestion: str = ""


@dataclass
class FileAnalysis:
    file_path: str
    file_size_bytes: int
    file_type: FileType
    encoding: Optional[str] = None
    delimiter: Optional[str] = None
    has_header: bool = True
    header_row_index: int = 0
    column_names: List[str] = field(default_factory=list)
    dtypes_detected: Dict[str, str] = field(default_factory=dict)
    sheet_names: List[str] = field(default_factory=list)
    recommended_sheet: Optional[str] = None
    messages: List[ImportMessage] = field(default_factory=list)
    is_importable: bool = True

    def add_message(self, severity: ImportSeverity, code: str, message: str, suggestion: str = ""):
        self.messages.append(ImportMessage(severity, code, message, suggestion))
        if severity == ImportSeverity.ERROR:
            self.is_importable = False


class SmartImporter:
    """Smart file importer using chardet and csv.Sniffer."""

    COMMON_NA_VALUES = {
        '', 'null', 'NULL', 'Null', 'NA', 'N/A', 'n/a', 'NaN', 'nan', 
        'None', 'none', 'NONE', '#N/A', '#NA', '#NULL!', '#REF!', '#VALUE!',
        '-', '--', '---', '.', '..', 'missing', 'MISSING', 'Missing',
    }

    ENCODING_SAMPLE_SIZE = 1024 * 1024
    ANALYSIS_SAMPLE_ROWS = 100

    def __init__(self, max_file_size_gb: float = 1.0):
        self.max_file_size_bytes = int(max_file_size_gb * 1024 * 1024 * 1024)

    def analyze(self, file_path: str) -> FileAnalysis:
        """Analyze a file and return detected properties."""
        file_path = str(Path(file_path).resolve())
        
        analysis = self._validate_file(file_path)
        if not analysis.is_importable:
            return analysis

        analysis.file_type = self._detect_file_type(file_path, analysis)
        
        try:
            if analysis.file_type in (FileType.CSV, FileType.TSV):
                self._analyze_csv(file_path, analysis)
            else:
                self._analyze_excel(file_path, analysis)
        except Exception as e:
            analysis.add_message(
                ImportSeverity.ERROR, "ANALYSIS_FAILED", 
                f"Failed to analyze file: {str(e)}",
                "The file may be corrupted or in an unsupported format."
            )
            logger.exception("File analysis failed for %s", file_path)
        
        return analysis

    def import_file(
        self,
        file_path: str,
        analysis: Optional[FileAnalysis] = None,
        delimiter: Optional[str] = None,
        encoding: Optional[str] = None,
        has_header: Optional[bool] = None,
        sheet_name: Optional[str] = None,
    ) -> pd.DataFrame:
        """Import a file into a pandas DataFrame."""
        file_path = str(Path(file_path).resolve())
        
        if analysis is None:
            analysis = self.analyze(file_path)
        
        if not analysis.is_importable:
            error_msgs = [m.message for m in analysis.messages if m.severity == ImportSeverity.ERROR]
            raise ValueError(f"File cannot be imported: {'; '.join(error_msgs)}")

        if delimiter:
            analysis.delimiter = delimiter
        if encoding:
            analysis.encoding = encoding
        if has_header is not None:
            analysis.has_header = has_header
        if sheet_name:
            analysis.recommended_sheet = sheet_name

        try:
            if analysis.file_type in (FileType.CSV, FileType.TSV):
                df = self._import_csv(file_path, analysis)
            else:
                df = self._import_excel(file_path, analysis)
        except UnicodeDecodeError as e:
            raise ValueError(
                f"Encoding Issue: Could not read the file using '{analysis.encoding}' encoding. "
                "The file might contain special characters. "
                "Action: Try re-saving the file as 'UTF-8', or specify a different encoding (e.g., 'latin1', 'cp1252')."
            ) from e
        except pd.errors.ParserError as e:
            raise ValueError(
                f"Parsing Issue: The file contains inconsistent rows. "
                f"Detected delimiter was '{analysis.delimiter}'. "
                "Action: Ensure all rows have the same number of columns."
            ) from e
        except pd.errors.EmptyDataError as e:
            raise ValueError(
                "Empty File Issue: The file appears to be empty. Action: Check the file content."
            ) from e
        except Exception as e:
            raise ValueError(f"Import failed: {str(e)}")

        logger.info("Successfully imported '%s': %d rows x %d columns", 
                    os.path.basename(file_path), len(df), len(df.columns))
        
        return df

    def _validate_file(self, file_path: str) -> FileAnalysis:
        """Validate file existence, readability, and size."""
        analysis = FileAnalysis(
            file_path=file_path,
            file_size_bytes=0,
            file_type=FileType.UNKNOWN,
        )

        if not os.path.exists(file_path):
            analysis.add_message(ImportSeverity.ERROR, "FILE_NOT_FOUND", 
                                f"File not found: {file_path}", "")
            return analysis

        if not os.path.isfile(file_path):
            analysis.add_message(ImportSeverity.ERROR, "NOT_A_FILE",
                               f"Path is not a file: {file_path}", "")
            return analysis

        if not os.access(file_path, os.R_OK):
            analysis.add_message(ImportSeverity.ERROR, "PERMISSION_DENIED",
                               f"Cannot read file: {file_path}", "")
            return analysis

        file_size = os.path.getsize(file_path)
        analysis.file_size_bytes = file_size

        if file_size == 0:
            analysis.add_message(ImportSeverity.ERROR, "EMPTY_FILE",
                               "The file is empty (0 bytes).", "")
            return analysis

        if file_size > self.max_file_size_bytes:
            analysis.add_message(ImportSeverity.ERROR, "FILE_TOO_LARGE",
                               f"File size exceeds maximum.", "")
            return analysis

        return analysis

    def _detect_file_type(self, file_path: str, analysis: FileAnalysis) -> FileType:
        """Detect file type using extension and magic bytes."""
        ext = Path(file_path).suffix.lower()
        
        ext_map = {
            '.csv': FileType.CSV, '.tsv': FileType.TSV, '.tab': FileType.TSV,
            '.txt': FileType.CSV, '.dat': FileType.CSV,
            '.xlsx': FileType.XLSX, '.xls': FileType.XLS,
            '.xlsb': FileType.XLSB, '.ods': FileType.ODS,
        }

        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
            
            if header[:4] == b'PK\x03\x04':
                return FileType.XLSX
            if header[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
                return FileType.XLS
        except Exception:
            pass

        return ext_map.get(ext, FileType.CSV)

    def _analyze_csv(self, file_path: str, analysis: FileAnalysis) -> None:
        """Analyze CSV file using chardet and csv.Sniffer."""
        analysis.encoding = self._detect_encoding(file_path)
        lines = self._read_lines(file_path, analysis)
        
        if not lines:
            analysis.add_message(ImportSeverity.ERROR, "NO_DATA", 
                               "File contains no readable data lines.", "")
            return

        analysis.delimiter = self._detect_delimiter(lines)
        analysis.has_header, analysis.column_names = self._detect_header(lines, analysis.delimiter)
        analysis.dtypes_detected = self._detect_dtypes(lines, analysis)

    def _detect_encoding(self, file_path: str) -> str:
        """Detect encoding using chardet."""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(self.ENCODING_SAMPLE_SIZE)
            
            if HAS_CHARDET:
                result = chardet.detect(raw_data)
                encoding = result.get('encoding')
                confidence = result.get('confidence', 0)
                
                if encoding and confidence >= 0.5:
                    encoding = encoding.lower()
                    if encoding in ('ascii', 'utf-8'):
                        return 'utf-8'
                    return encoding
            
            # Check for BOM
            if raw_data[:3] == b'\xef\xbb\xbf':
                return 'utf-8-sig'
            if raw_data[:2] in (b'\xff\xfe', b'\xfe\xff'):
                return 'utf-16'
                
        except Exception:
            pass
        
        return 'utf-8'

    def _read_lines(self, file_path: str, analysis: FileAnalysis, num_lines: int = None) -> List[str]:
        """Read raw text lines from file."""
        if num_lines is None:
            num_lines = self.ANALYSIS_SAMPLE_ROWS
        
        encoding = analysis.encoding or 'utf-8'
        lines = []
        
        for enc in [encoding, 'utf-8', 'latin1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=enc, errors='replace') as f:
                    for i, line in enumerate(f):
                        if i >= num_lines:
                            break
                        lines.append(line.rstrip('\r\n'))
                if enc != encoding:
                    analysis.encoding = enc
                return lines
            except UnicodeDecodeError:
                continue
        
        return lines

    def _detect_delimiter(self, lines: List[str]) -> str:
        """Detect delimiter using csv.Sniffer."""
        if not lines:
            return ','
        
        data_lines = [l for l in lines if l.strip()]
        if not data_lines:
            return ','
        
        sample_text = "".join(data_lines[:30])
        
        # Use csv.Sniffer
        try:
            dialect = csv.Sniffer().sniff(sample_text)
            return dialect.delimiter
        except csv.Error:
            pass
        
        # Fallback: count delimiters
        candidates = [',', '\t', ';', '|']
        best_delim = ','
        best_score = -1
        
        for delim in candidates:
            counts = [line.count(delim) for line in data_lines[:20]]
            if not counts or max(counts) == 0:
                continue
            
            avg_count = sum(counts) / len(counts)
            variance = sum((c - avg_count) ** 2 for c in counts) / len(counts)
            consistency = 1.0 / (1.0 + variance / (avg_count ** 2)) if avg_count > 0 else 0
            score = consistency * avg_count
            
            if score > best_score:
                best_score = score
                best_delim = delim
        
        return best_delim

    def _detect_header(self, lines: List[str], delimiter: str) -> tuple[bool, List[str]]:
        """Detect header using csv.Sniffer."""
        if not lines or len(lines) < 2:
            return True, []
        
        try:
            sample_text = "\n".join(lines[:20])
            has_header = csv.Sniffer().has_header(sample_text)
            
            reader = csv.reader(lines[:10], delimiter=delimiter)
            rows = list(reader)
            
            if has_header and rows:
                return True, [str(v).strip() for v in rows[0]]
            
            if rows:
                return False, [f"Column_{i}" for i in range(len(rows[0]))]
        except csv.Error:
            pass
        
        return True, []

    def _detect_dtypes(self, lines: List[str], analysis: FileAnalysis) -> Dict[str, str]:
        """Detect column data types."""
        delim = analysis.delimiter or ','
        
        try:
            reader = csv.reader(lines[:20], delimiter=delim)
            rows = list(reader)
        except csv.Error:
            rows = [line.split(delim) for line in lines[:20]]
        
        if not rows:
            return {}
        
        start = 1 if analysis.has_header else 0
        data_rows = rows[start:] if start < len(rows) else []
        
        if not data_rows:
            return {}
        
        num_cols = len(rows[0]) if rows else 0
        dtypes = {}
        
        for col_idx in range(num_cols):
            col_values = []
            for row in data_rows:
                if col_idx < len(row):
                    val = row[col_idx].strip()
                    if val and val.lower() not in self.COMMON_NA_VALUES:
                        col_values.append(val)
            
            if not col_values:
                dtypes[f"col_{col_idx}"] = 'empty'
            elif all(self._is_numeric(v) for v in col_values):
                dtypes[f"col_{col_idx}"] = 'numeric'
            else:
                dtypes[f"col_{col_idx}"] = 'string'
        
        if analysis.column_names:
            dtypes = {analysis.column_names[i]: v for i, v in enumerate(dtypes.values()) if i < len(analysis.column_names)}
        
        return dtypes

    def _is_numeric(self, value: str) -> bool:
        if not value:
            return False
        try:
            float(value.replace(',', '').strip())
            return True
        except ValueError:
            return False

    def _analyze_excel(self, file_path: str, analysis: FileAnalysis) -> None:
        """Analyze Excel file."""
        try:
            xl_file = pd.ExcelFile(file_path)
            analysis.sheet_names = xl_file.sheet_names
            
            if not analysis.sheet_names:
                analysis.add_message(ImportSeverity.ERROR, "NO_SHEETS",
                                   "The Excel file contains no sheets.", "")
                return
            
            analysis.recommended_sheet = analysis.sheet_names[0]
            
            df_sample = pd.read_excel(file_path, sheet_name=analysis.recommended_sheet, nrows=10)
            analysis.column_names = [str(c) for c in df_sample.columns]
            
            for col in df_sample.columns:
                dtype = str(df_sample[col].dtype)
                if 'int' in dtype or 'float' in dtype:
                    analysis.dtypes_detected[str(col)] = 'numeric'
                else:
                    analysis.dtypes_detected[str(col)] = 'string'
                    
        except Exception as e:
            error_str = str(e).lower()
            if 'openpyxl' in error_str:
                analysis.add_message(ImportSeverity.ERROR, "MISSING_OPENPYXL",
                                   "Missing 'openpyxl' library.", "pip install openpyxl")
            elif 'xlrd' in error_str:
                analysis.add_message(ImportSeverity.ERROR, "MISSING_XLRD",
                                   "Missing 'xlrd' library.", "pip install xlrd")
            else:
                analysis.add_message(ImportSeverity.ERROR, "EXCEL_READ_ERROR",
                                   f"Error: {str(e)}", "")

    def _import_csv(self, file_path: str, analysis: FileAnalysis) -> pd.DataFrame:
        """Import CSV file."""
        kwargs = {
            'filepath_or_buffer': file_path,
            'sep': analysis.delimiter or ',',
            'encoding': analysis.encoding or 'utf-8',
        }
        
        if analysis.has_header:
            kwargs['header'] = analysis.header_row_index
        else:
            kwargs['header'] = None
        
        na_values = list(self.COMMON_NA_VALUES)
        kwargs['na_values'] = na_values
        
        df = pd.read_csv(**kwargs)
        
        if not analysis.has_header and analysis.column_names:
            df.columns = analysis.column_names
        
        return df

    def _import_excel(self, file_path: str, analysis: FileAnalysis) -> pd.DataFrame:
        """Import Excel file."""
        sheet = analysis.recommended_sheet or 0
        return pd.read_excel(file_path, sheet_name=sheet, header=0 if analysis.has_header else None)


def smart_import(
    file_path: str,
    delimiter: Optional[str] = None,
    encoding: Optional[str] = None,
    has_header: Optional[bool] = None,
    sheet_name: Optional[str] = None,
    auto_detect: bool = True,
) -> pd.DataFrame:
    """Smart import function."""
    importer = SmartImporter()
    
    if auto_detect:
        analysis = importer.analyze(file_path)
        return importer.import_file(
            file_path,
            analysis=analysis,
            delimiter=delimiter,
            encoding=encoding,
            has_header=has_header,
            sheet_name=sheet_name,
        )
    else:
        file_type = Path(file_path).suffix.lower()
        
        if file_type in ('.csv', '.tsv', '.txt', '.tab', '.dat'):
            kwargs = {
                'filepath_or_buffer': file_path,
                'sep': delimiter or ',',
                'encoding': encoding or 'utf-8',
                'header': 0 if has_header else None,
            }
            return pd.read_csv(**kwargs)
        elif file_type in ('.xlsx', '.xls', '.xlsb', '.ods'):
            return pd.read_excel(file_path, sheet_name=sheet_name, header=0 if has_header else None)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
