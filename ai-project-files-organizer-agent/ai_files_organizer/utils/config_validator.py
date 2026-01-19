"""
Configuration validation utilities
"""

from typing import Dict, List, Tuple, Any
import json
from pathlib import Path


class ConfigValidator:
    """Validates configuration structure and values"""

    REQUIRED_SECTIONS = [
        "monitoring",
        "versioning",
        "outdated_detection",
        "folder_structure",
        "approval",
    ]

    SECTION_SCHEMAS = {
        "monitoring": {
            "realtime": bool,
            "periodic_interval_hours": (int, float),
            "scan_on_startup": bool,
        },
        "versioning": {
            "format": str,
            "auto_increment": bool,
            "add_to_existing": bool,
        },
        "outdated_detection": {
            "days_threshold": (int, float),
            "check_content": bool,
            "check_references": bool,
        },
        "folder_structure": {
            "rules_file": str,
            "auto_create_folders": bool,
        },
        "approval": {
            "require_approval": bool,
            "batch_mode": bool,
            "timeout_seconds": (int, float),
        },
        "git": {
            "enabled": bool,
            "require_approval": bool,
            "conventional_commits": bool,
            "auto_stage": bool,
            "auto_commit": bool,
            "auto_push": bool,
        },
        "backup": {
            "enabled": bool,
            "location": str,
            "keep_days": (int, float),
        },
    }

    @classmethod
    def validate(cls, config: Dict) -> Tuple[bool, List[str]]:
        """
        Validate configuration structure and values.

        Args:
            config: Configuration dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required sections
        for section in cls.REQUIRED_SECTIONS:
            if section not in config:
                errors.append(f"Missing required section: {section}")

        # Validate section schemas
        for section, schema in cls.SECTION_SCHEMAS.items():
            if section in config:
                section_errors = cls._validate_section(
                    config[section], schema, section
                )
                errors.extend(section_errors)

        return len(errors) == 0, errors

    @classmethod
    def _validate_section(
        cls, section_data: Dict, schema: Dict, section_name: str
    ) -> List[str]:
        """Validate a configuration section"""
        errors = []

        if not isinstance(section_data, dict):
            errors.append(f"Section '{section_name}' must be a dictionary")
            return errors

        for key, expected_type in schema.items():
            if key not in section_data:
                # Optional fields are allowed to be missing
                continue

            value = section_data[key]
            if isinstance(expected_type, tuple):
                if not isinstance(value, expected_type):
                    errors.append(
                        f"Section '{section_name}.{key}' must be one of {expected_type}, got {type(value).__name__}"
                    )
            elif not isinstance(value, expected_type):
                errors.append(
                    f"Section '{section_name}.{key}' must be {expected_type.__name__}, got {type(value).__name__}"
                )

        return errors

    @classmethod
    def validate_file(cls, config_path: Path) -> Tuple[bool, List[str], Dict]:
        """
        Validate configuration file.

        Args:
            config_path: Path to configuration file

        Returns:
            Tuple of (is_valid, list_of_errors, config_dict)
        """
        errors = []
        config = {}

        if not config_path.exists():
            return False, [f"Configuration file does not exist: {config_path}"], {}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON in config file: {e}"], {}
        except Exception as e:
            return False, [f"Error reading config file: {e}"], {}

        is_valid, validation_errors = cls.validate(config)
        errors.extend(validation_errors)

        return is_valid, errors, config
