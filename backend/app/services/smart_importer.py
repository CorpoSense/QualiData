"""Smart CSV/Excel Importer with Heuristic Analysis

A robust file importer that uses heuristic analysis to automatically detect 
file format, encoding, delimiters, headers, data types, and other properties.
"""

import os
import re
import csv
import io
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

import pandas as pd
import numpy as np

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
    """Represents a message/issue detected during import analysis."""
    severity: ImportSeverity
    code: str
    message: str
    suggestion: str = ""


@dataclass
class FileAnalysis:
    """Complete analysis result of a file before importing."""
    file_path: str
    file_size_bytes: int
    file_type: FileType
    encoding: Optional[str] = None
    delimiter: Optional[str] = None
    has_header: bool = True
    header_row_index: int = 0
    column_names: List[str] = field(default_factory=list)
    dtypes_detected: Dict[str, str] = field(default_factory=dict)
    decimal_char: str = "."
    thousands_separator: Optional[str] = None
    sheet_names: List[str] = field(default_factory=list)
    recommended_sheet: Optional[str] = None
    na_values_detected: List[str] = field(default_factory=list)
    date_columns: List[str] = field(default_factory=list)
    messages: List[ImportMessage] = field(default_factory=list)
    is_importable: bool = True

    def add_message(self, severity: ImportSeverity, code: str, message: str, suggestion: str = ""):
        self.messages.append(ImportMessage(severity, code, message, suggestion))
        if severity == ImportSeverity.ERROR:
            self.is_importable = False


class SmartImporter:
    """Smart file importer with heuristic analysis."""

    COMMON_NA_VALUES = {
        '', 'null', 'NULL', 'Null', 'NA', 'N/A', 'n/a', 'NaN', 'nan', 
        'None', 'none', 'NONE', '#N/A', '#NA', '#NULL!', '#REF!', '#VALUE!',
        '-', '--', '---', '.', '..', 'missing', 'MISSING', 'Missing',
    }

    COMMENT_CHARS = ['#', '//', ';', '%', '!']
    DATE_PATTERNS = [
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
        r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',
        r'\d{1,2}[-/]\d{1,2}[-/]\d{2}',
    ]

    ENCODING_SAMPLE_SIZE = 1024 * 1024  # 1MB
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

        # Apply overrides
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
        except Exception as e:
            raise ValueError(f"Failed to import file: {str(e)}")

        logger.info("Successfully imported '%s': %d rows × %d columns", 
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
                               f"File size exceeds maximum ({self.max_file_size_bytes / (1024**3):.2f} GB).", "")
            return analysis

        return analysis

    def _detect_file_type(self, file_path: str, analysis: FileAnalysis) -> FileType:
        """Detect file type using extension and magic bytes."""
        ext = Path(file_path).suffix.lower()
        
        ext_map = {
            '.csv': FileType.CSV,
            '.tsv': FileType.TSV,
            '.tab': FileType.TSV,
            '.txt': FileType.CSV,
            '.dat': FileType.CSV,
            '.xlsx': FileType.XLSX,
            '.xls': FileType.XLS,
            '.xlsb': FileType.XLSB,
            '.ods': FileType.ODS,
        }

        # Check magic bytes
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
            
            if header[:4] == b'PK\x03\x04':
                if ext in ('.xlsx', '.xlsb'):
                    return FileType.XLSX if ext == '.xlsx' else FileType.XLSB
                return FileType.XLSX  # Default to xlsx for ZIP-based
            
            if header[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
                return FileType.XLS
        except Exception:
            pass

        return ext_map.get(ext, FileType.CSV)  # Default to CSV for unknown text files

    def _analyze_csv(self, file_path: str, analysis: FileAnalysis) -> None:
        """Analyze CSV file properties."""
        # Detect encoding
        analysis.encoding = self._detect_encoding(file_path)
        
        # Read sample lines
        lines = self._read_lines(file_path, analysis)
        if not lines:
            analysis.add_message(ImportSeverity.ERROR, "NO_DATA", 
                               "File contains no readable data lines.", "")
            return

        # Detect delimiter
        analysis.delimiter = self._detect_delimiter(lines)
        
        # Detect header
        analysis.has_header, analysis.column_names = self._detect_header(lines, analysis.delimiter)
        
        # Detect data types
        analysis.dtypes_detected = self._detect_dtypes(lines, analysis)
        
        # Estimate total lines
        analysis.total_lines_estimate = self._estimate_total_lines(file_path, analysis, len(lines))

    def _detect_encoding(self, file_path: str) -> str:
        """Detect file encoding."""
        # Check for BOM
        try:
            with open(file_path, 'rb') as f:
                raw = f.read(4)
            
            if raw[:3] == b'\xef\xbb\xbf':
                return 'utf-8-sig'
            if raw[:2] == b'\xff\xfe':
                return 'utf-16-le'
            if raw[:2] == b'\xfe\xff':
                return 'utf-16-be'
        except Exception:
            pass
        
        # Default to UTF-8
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
        """Detect the field delimiter."""
        if not lines:
            return ','
        
        # Filter empty lines
        data_lines = [l for l in lines if l.strip()]
        if not data_lines:
            return ','
        
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
        """Detect if first row is a header."""
        if not lines or len(lines) < 2:
            return True, []
        
        # Parse first few rows
        try:
            reader = csv.reader(lines[:10], delimiter=delimiter)
            rows = list(reader)
        except csv.Error:
            rows = [line.split(delimiter) for line in lines[:10]]
        
        if len(rows) < 2:
            return True, []
        
        first_row = rows[0]
        data_rows = rows[1:]
        
        # Heuristic: check if first row has different types than data
        first_numeric = sum(1 for v in first_row if self._is_numeric(v.strip())) / max(len(first_row), 1)
        data_numeric = []
        for row in data_rows[:5]:
            if len(row) == len(first_row):
                data_numeric.append(sum(1 for v in row if self._is_numeric(v.strip())) / len(row))
        
        avg_data_numeric = sum(data_numeric) / len(data_numeric) if data_numeric else 0
        
        # If first row is mostly text and data is numeric → header
        has_header = first_numeric < 0.3 and avg_data_numeric > 0.5
        
        if has_header:
            return True, [str(v).strip() for v in first_row]
        
        # Generate column names
        column_names = [f"Column_{i}" for i in range(len(first_row))]
        return False, column_names

    def _is_numeric(self, value: str) -> bool:
        """Check if a value is numeric."""
        if not value:
            return False
        try:
            float(value.replace(',', '').strip())
            return True
        except ValueError:
            return False

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
            elif all(self._is_date_like(v) for v in col_values[:10]):
                dtypes[f"col_{col_idx}"] = 'date'
            else:
                dtypes[f"col_{col_idx}"] = 'string'
        
        # Use column names if available
        if analysis.column_names:
            dtypes = {analysis.column_names[i]: v for i, v in enumerate(dtypes.values()) if i < len(analysis.column_names)}
        
        return dtypes

    def _is_date_like(self, value: str) -> bool:
        """Check if value looks like a date."""
        patterns = [
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',
        ]
        return any(re.match(p, value) for p in patterns)

    def _estimate_total_lines(self, file_path: str, analysis: FileAnalysis, sample_lines: int) -> int:
        """Estimate total number of lines."""
        if sample_lines == 0:
            return 0
        
        try:
            with open(file_path, 'rb') as f:
                file_size = os.path.getsize(file_path)
            
            with open(file_path, 'r', encoding=analysis.encoding or 'utf-8', errors='replace') as f:
                sample_size = sum(len(line) for line in f.readlines(sample_lines))
            
            if sample_size > 0:
                return int(file_size / (sample_size / sample_lines))
        except Exception:
            pass
        
        return sample_lines * 10  # Rough estimate

    def _analyze_excel(self, file_path: str, analysis: FileAnalysis) -> None:
        """Analyze Excel file properties."""
        try:
            xl_file = pd.ExcelFile(file_path)
            analysis.sheet_names = xl_file.sheet_names
            
            if not analysis.sheet_names:
                analysis.add_message(ImportSeverity.ERROR, "NO_SHEETS",
                                   "The Excel file contains no sheets.", "")
                return
            
            analysis.recommended_sheet = analysis.sheet_names[0]
            
            if len(analysis.sheet_names) > 1:
                analysis.add_message(ImportSeverity.INFO, "MULTIPLE_SHEETS",
                                   f"File contains {len(analysis.sheet_names)} sheets. Using: '{analysis.sheet_names[0]}'.",
                                   "To import a different sheet, specify the sheet_name parameter.")
            
            # Analyze first sheet
            df_sample = pd.read_excel(file_path, sheet_name=analysis.recommended_sheet, nrows=10)
            analysis.num_columns_detected = len(df_sample.columns)
            analysis.column_names = [str(c) for c in df_sample.columns]
            
            # Detect dtypes
            for col in df_sample.columns:
                dtype = str(df_sample[col].dtype)
                if 'int' in dtype or 'float' in dtype:
                    analysis.dtypes_detected[str(col)] = 'numeric'
                elif 'datetime' in dtype:
                    analysis.dtypes_detected[str(col)] = 'date'
                else:
                    analysis.dtypes_detected[str(col)] = 'string'
                    
        except Exception as e:
            analysis.add_message(ImportSeverity.ERROR, "EXCEL_READ_ERROR",
                               f"Error reading Excel file: {str(e)}", "")

    def _import_csv(self, file_path: str, analysis: FileAnalysis) -> pd.DataFrame:
        """Import CSV file using detected or specified settings."""
        kwargs = {
            'filepath_or_buffer': file_path,
            'sep': analysis.delimiter or ',',
            'encoding': analysis.encoding or 'utf-8',
        }
        
        if analysis.has_header:
            kwargs['header'] = analysis.header_row_index
        else:
            kwargs['header'] = None
        
        # Add common NA values
        na_values = list(self.COMMON_NA_VALUES)
        if analysis.na_values_detected:
            na_values.extend(analysis.na_values_detected)
        kwargs['na_values'] = na_values
        
        df = pd.read_csv(**kwargs)
        
        # Set column names if generated
        if not analysis.has_header and analysis.column_names:
            df.columns = analysis.column_names
        
        return df

    def _import_excel(self, file_path: str, analysis: FileAnalysis) -> pd.DataFrame:
        """Import Excel file."""
        sheet = analysis.recommended_sheet or 0
        
        df = pd.read_excel(
            file_path,
            sheet_name=sheet,
            header=0 if analysis.has_header else None,
        )
        
        return df


# Convenience function
def smart_import(
    file_path: str,
    delimiter: Optional[str] = None,
    encoding: Optional[str] = None,
    has_header: Optional[bool] = None,
    sheet_name: Optional[str] = None,
    auto_detect: bool = True,
) -> pd.DataFrame:
    """
    Smart import function.
    
    Args:
        file_path: Path to the file
        delimiter: Delimiter override
        encoding: Encoding override  
        has_header: Header row override
        sheet_name: Excel sheet name
        auto_detect: If True, automatically detect all parameters
    
    Returns:
        pandas DataFrame
    """
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
        # Direct import without analysis
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
