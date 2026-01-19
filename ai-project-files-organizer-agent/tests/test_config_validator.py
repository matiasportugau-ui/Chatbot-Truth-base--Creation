"""
Tests for ConfigValidator
"""

import tempfile
import json
from pathlib import Path

import pytest

from ai_files_organizer.utils.config_validator import ConfigValidator


def test_validate_config_valid():
    """Test validation of valid config"""
    config = {
        "monitoring": {
            "realtime": True,
            "periodic_interval_hours": 24,
            "scan_on_startup": True,
        },
        "versioning": {
            "format": "ddmm_vN",
            "auto_increment": True,
            "add_to_existing": True,
        },
        "outdated_detection": {
            "days_threshold": 90,
            "check_content": True,
            "check_references": True,
        },
        "folder_structure": {
            "rules_file": "folder_rules.json",
            "auto_create_folders": True,
        },
        "approval": {
            "require_approval": True,
            "batch_mode": True,
            "timeout_seconds": 3600,
        },
    }
    
    is_valid, errors = ConfigValidator.validate(config)
    assert is_valid
    assert len(errors) == 0


def test_validate_config_missing_section():
    """Test validation with missing required section"""
    config = {
        "monitoring": {"realtime": True},
        # Missing other required sections
    }
    
    is_valid, errors = ConfigValidator.validate(config)
    assert not is_valid
    assert len(errors) > 0


def test_validate_config_wrong_type():
    """Test validation with wrong type"""
    config = {
        "monitoring": {
            "realtime": "not a boolean",  # Should be bool
            "periodic_interval_hours": 24,
            "scan_on_startup": True,
        },
        "versioning": {
            "format": "ddmm_vN",
            "auto_increment": True,
            "add_to_existing": True,
        },
        "outdated_detection": {
            "days_threshold": 90,
            "check_content": True,
            "check_references": True,
        },
        "folder_structure": {
            "rules_file": "folder_rules.json",
            "auto_create_folders": True,
        },
        "approval": {
            "require_approval": True,
            "batch_mode": True,
            "timeout_seconds": 3600,
        },
    }
    
    is_valid, errors = ConfigValidator.validate(config)
    assert not is_valid
    assert any("realtime" in error.lower() for error in errors)


def test_validate_file():
    """Test validation of config file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        
        # Valid config
        valid_config = {
            "monitoring": {
                "realtime": True,
                "periodic_interval_hours": 24,
                "scan_on_startup": True,
            },
            "versioning": {
                "format": "ddmm_vN",
                "auto_increment": True,
                "add_to_existing": True,
            },
            "outdated_detection": {
                "days_threshold": 90,
                "check_content": True,
                "check_references": True,
            },
            "folder_structure": {
                "rules_file": "folder_rules.json",
                "auto_create_folders": True,
            },
            "approval": {
                "require_approval": True,
                "batch_mode": True,
                "timeout_seconds": 3600,
            },
        }
        
        with open(config_file, "w") as f:
            json.dump(valid_config, f)
        
        is_valid, errors, config = ConfigValidator.validate_file(config_file)
        assert is_valid
        assert len(errors) == 0
        assert config == valid_config
