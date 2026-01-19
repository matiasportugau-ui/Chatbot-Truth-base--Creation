"""
Tests for OutdatedDetector
"""

import tempfile
from pathlib import Path
from datetime import datetime, timedelta

import pytest

from ai_files_organizer.core.outdated_detector import OutdatedDetector
from ai_files_organizer.core.file_scanner import FileMetadata


@pytest.fixture
def temp_workspace():
    """Create temporary workspace"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        yield workspace


def test_detect_outdated_by_date(temp_workspace):
    """Test outdated detection by date"""
    detector = OutdatedDetector(days_threshold=90)
    
    # Create old file
    old_file = temp_workspace / "old_file.md"
    old_file.write_text("# Old")
    
    # Set old modification time
    old_time = datetime.now() - timedelta(days=100)
    old_timestamp = old_time.timestamp()
    old_file.touch()
    import os
    os.utime(old_file, (old_timestamp, old_timestamp))
    
    # Create metadata
    from ai_files_organizer.core.file_scanner import FileScanner
    scanner = FileScanner(str(temp_workspace))
    files = scanner.scan()
    
    outdated = detector.detect_outdated(files, temp_workspace)
    
    assert len(outdated) >= 1
    assert any("old_file.md" in str(o["file"]) for o in outdated)
