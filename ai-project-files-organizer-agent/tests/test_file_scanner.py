"""
Tests for FileScanner
"""

import tempfile
from pathlib import Path
from datetime import datetime

import pytest

from ai_files_organizer.core.file_scanner import FileScanner, FileMetadata


@pytest.fixture
def temp_workspace():
    """Create temporary workspace"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        # Create test files
        (workspace / "test.md").write_text("# Test")
        (workspace / "config.json").write_text('{"key": "value"}')
        (workspace / "script.py").write_text("print('hello')")
        
        yield workspace


def test_file_scanner_scan(temp_workspace):
    """Test file scanning"""
    scanner = FileScanner(str(temp_workspace))
    files = scanner.scan()
    
    assert len(files) >= 3
    assert any(f.name == "test.md" for f in files)
    assert any(f.name == "config.json" for f in files)
    assert any(f.name == "script.py" for f in files)


def test_file_scanner_categorization(temp_workspace):
    """Test file categorization"""
    scanner = FileScanner(str(temp_workspace))
    files = scanner.scan()
    
    md_files = [f for f in files if f.extension == ".md"]
    assert len(md_files) > 0
    assert md_files[0].category == "documentation"


def test_file_scanner_duplicates(temp_workspace):
    """Test duplicate detection"""
    scanner = FileScanner(str(temp_workspace))
    
    # Create duplicate file
    (temp_workspace / "duplicate.md").write_text("# Test")
    
    files = scanner.scan()
    duplicates = scanner.get_duplicates()
    
    # Should detect duplicate
    assert len(duplicates) >= 1
