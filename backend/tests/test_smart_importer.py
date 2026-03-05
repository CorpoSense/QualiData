"""Tests for smart importer service."""

import pytest
import os
import tempfile


class TestSmartImporterBasics:
    """Basic tests for SmartImporter."""

    def test_smart_importer_import(self):
        """Test basic import works."""
        from app.services.smart_importer import SmartImporter
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,age\n")
            f.write("John,25\n")
            tmp = f.name
        
        try:
            imp = SmartImporter()
            df = imp.import_file(tmp, has_header=True)
            assert len(df) >= 1
        finally:
            os.unlink(tmp)

    def test_analyze_returns_file_info(self):
        """Test analyze returns metadata."""
        from app.services.smart_importer import SmartImporter
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("a,b\n1,2\n")
            tmp = f.name
        
        try:
            imp = SmartImporter()
            result = imp.analyze(tmp)
            assert result.is_importable is True
            assert result.delimiter is not None
        finally:
            os.unlink(tmp)

    def test_nonexistent_file_raises(self):
        """Test nonexistent file raises error."""
        from app.services.smart_importer import SmartImporter
        
        imp = SmartImporter()
        with pytest.raises(Exception):
            imp.import_file("/nonexistent/file.csv")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
