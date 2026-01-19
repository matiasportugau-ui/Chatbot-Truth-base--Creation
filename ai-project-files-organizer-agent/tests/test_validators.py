"""
Tests for validators
"""

import tempfile
from pathlib import Path

import pytest

from ai_files_organizer.utils.validators import (
    validate_path,
    validate_write_permissions,
    sanitize_filename,
)


def test_validate_path():
    """Test path validation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("test")
        
        # Valid path
        is_valid, error = validate_path(str(test_file), must_exist=True)
        assert is_valid
        assert error == ""
        
        # Non-existent path
        is_valid, error = validate_path(str(Path(tmpdir) / "nonexistent.txt"), must_exist=True)
        assert not is_valid


def test_validate_path_traversal():
    """Test path traversal detection"""
    is_valid, error = validate_path("../etc/passwd")
    assert not is_valid
    assert "traversal" in error.lower()


def test_validate_path_workspace_boundary():
    """Test workspace boundary validation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir) / "workspace"
        workspace.mkdir()
        
        # Path within workspace
        test_path = workspace / "file.txt"
        is_valid, error = validate_path(
            str(test_path), workspace_root=workspace
        )
        assert is_valid
        
        # Path outside workspace
        outside_path = Path(tmpdir) / "outside" / "file.txt"
        is_valid, error = validate_path(
            str(outside_path), workspace_root=workspace
        )
        assert not is_valid
        assert "boundary" in error.lower()


def test_validate_write_permissions():
    """Test write permissions validation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "writable"
        test_dir.mkdir()
        
        is_valid, error = validate_write_permissions(test_dir)
        assert is_valid


def test_sanitize_filename():
    """Test filename sanitization"""
    # Test path separators
    assert sanitize_filename("path/to/file") == "path_to_file"
    
    # Test dangerous characters
    assert "<" not in sanitize_filename("file<name>")
    assert ":" not in sanitize_filename("file:name")
    
    # Test null bytes
    assert "\x00" not in sanitize_filename("file\x00name")
