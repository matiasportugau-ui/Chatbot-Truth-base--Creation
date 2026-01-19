"""
Validation utilities for AI Files Organizer Agent
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple


def validate_path(
    path: str,
    must_exist: bool = False,
    workspace_root: Optional[Path] = None,
) -> Tuple[bool, str]:
    """
    Validate a file or directory path with workspace boundary check.

    Args:
        path: Path to validate
        must_exist: If True, path must exist
        workspace_root: Optional workspace root to enforce boundary

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check for path traversal attempts BEFORE resolving
        # resolve() normalizes paths and removes .. components, so we need to check first
        path_parts = Path(path).parts
        if ".." in path_parts:
            return False, "Path traversal detected"

        # Now resolve to get the absolute path
        path_obj = Path(path).resolve()

        # Ensure path is within workspace (if workspace_root provided)
        if workspace_root:
            workspace_root = workspace_root.resolve()
            try:
                path_obj.relative_to(workspace_root)
            except ValueError:
                return False, "Path outside workspace boundary"

        # Additional safety check: ensure resolved path doesn't contain .. (shouldn't happen)
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


def validate_write_permissions(directory_path: Path) -> Tuple[bool, str]:
    """
    Validate write permissions for a directory.

    Args:
        directory_path: Path to directory

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not directory_path.exists():
        # Try to create parent directory to check permissions
        try:
            directory_path.parent.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            return False, f"Cannot create directory: {str(e)}"

    if not directory_path.is_dir():
        return False, "Path is not a directory"

    if not os.access(directory_path, os.W_OK):
        return False, f"Directory is not writable: {directory_path}"

    # Test write permission by attempting to create a test file
    try:
        test_file = directory_path / ".write_test"
        test_file.touch()
        test_file.unlink()
    except (OSError, PermissionError) as e:
        return False, f"Cannot write to directory: {str(e)}"

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
