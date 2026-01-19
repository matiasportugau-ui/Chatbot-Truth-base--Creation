"""
Tests for VersionManager
"""

from datetime import datetime

import pytest

from ai_files_organizer.core.version_manager import VersionManager


def test_generate_version_code():
    """Test version code generation"""
    manager = VersionManager()
    code = manager.generate_version_code()
    
    assert len(code) > 0
    assert "_v" in code


def test_extract_version_info():
    """Test version extraction from filename"""
    manager = VersionManager()
    
    # Test with version
    info = manager.extract_version_info("Document_1601_v2.md")
    assert info is not None
    date_part, version_num = info
    assert date_part == "1601"
    assert version_num == 2


def test_increment_version():
    """Test version increment"""
    manager = VersionManager()
    
    new_name = manager.increment_version("Document_1601_v1.md")
    assert "_v2" in new_name


def test_add_version_to_filename():
    """Test adding version to filename"""
    manager = VersionManager()
    
    new_name = manager.add_version_to_filename("Document.md")
    assert "_v" in new_name
    assert new_name.endswith(".md")
