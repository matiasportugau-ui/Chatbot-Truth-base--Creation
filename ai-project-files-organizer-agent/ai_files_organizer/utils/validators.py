"""
Validation utilities for AI Files Organizer Agent
"""

import os
from pathlib import Path
from typing import List, Tuple


def validate_path(path: str, must_exist: bool = False) -> Tuple[bool, str]:
    """
    Validate a file or directory path.

    Args:
        path: Path to validate
        must_exist: If True, path must exist

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        path_obj = Path(path).resolve()

        # Check for path traversal attempts
        if ".." in str(path_obj):
            return False, "Path traversal detected"

        if must_exist and not path_obj.exists():
            return False, f"Path does not exist: {path}"

        return True, ""

    except Exception as e:
        return False, f"Invalid path: {str(e)}"


def validate_file_permissions(file_path: Path) -> Tuple[bool, str]:
    """
    Validate file permissions.

    Args:
        file_path: Path to file

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path.exists():
        return False, "File does not exist"

    if not os.access(file_path, os.R_OK):
        return False, "File is not readable"

    return True, ""


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path separators
    filename = filename.replace("/", "_").replace("\\", "_")

    # Remove null bytes
    filename = filename.replace("\x00", "")

    # Remove other dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, "_")

    return filename


def validate_file_list(files: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate a list of file paths.

    Args:
        files: List of file paths

    Returns:
        Tuple of (all_valid, list_of_errors)
    """
    errors = []
    for file_path in files:
        is_valid, error = validate_path(file_path, must_exist=True)
        if not is_valid:
            errors.append(f"{file_path}: {error}")

    return len(errors) == 0, errors
