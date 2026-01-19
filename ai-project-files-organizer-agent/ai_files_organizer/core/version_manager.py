"""
Version Manager for generating and managing file version codes
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


class VersionManager:
    """
    Manages file versioning with ddmm_vN format
    """

    def __init__(self, format_string: str = "ddmm_vN", auto_increment: bool = True):
        """
        Initialize version manager.

        Args:
            format_string: Version format (default: "ddmm_vN")
            auto_increment: If True, auto-increment versions
        """
        self.format_string = format_string
        self.auto_increment = auto_increment

    def generate_version_code(self, date: Optional[datetime] = None) -> str:
        """
        Generate version code in format ddmm_vN.

        Args:
            date: Date to use (default: today)

        Returns:
            Version code string (e.g., "1601_v1")
        """
        if date is None:
            date = datetime.now()

        day = date.day
        month = date.month
        date_part = f"{day:02d}{month:02d}"

        return f"{date_part}_v1"

    def extract_version_info(self, filename: str) -> Optional[Tuple[str, int]]:
        """
        Extract version information from filename.

        Args:
            filename: Filename to parse

        Returns:
            Tuple of (date_part, version_number) or None
        """
        # Pattern: _ddmm_vN
        pattern = r"_(\d{4})_v(\d+)"
        match = re.search(pattern, filename)
        if match:
            date_part = match.group(1)
            version_num = int(match.group(2))
            return (date_part, version_num)

        return None

    def increment_version(self, filename: str) -> str:
        """
        Increment version in filename.

        Args:
            filename: Current filename

        Returns:
            New filename with incremented version
        """
        version_info = self.extract_version_info(filename)
        if version_info:
            date_part, version_num = version_info
            new_version = version_num + 1
            # Replace old version with new one
            pattern = r"_(\d{4})_v(\d+)"
            new_filename = re.sub(
                pattern, f"_{date_part}_v{new_version}", filename
            )
            return new_filename
        else:
            # No version found, add new version
            path_obj = Path(filename)
            stem = path_obj.stem
            extension = path_obj.suffix
            version_code = self.generate_version_code()
            return f"{stem}_{version_code}{extension}"

    def add_version_to_filename(
        self, filename: str, date: Optional[datetime] = None
    ) -> str:
        """
        Add version code to filename if it doesn't have one.

        Args:
            filename: Original filename
            date: Date to use (default: today)

        Returns:
            Filename with version code
        """
        if self.extract_version_info(filename):
            # Already has version
            return filename

        path_obj = Path(filename)
        stem = path_obj.stem
        extension = path_obj.suffix
        version_code = self.generate_version_code(date)

        return f"{stem}_{version_code}{extension}"

    def update_version_on_modification(
        self, filename: str, was_modified: bool
    ) -> str:
        """
        Update version if file was modified.

        Args:
            filename: Current filename
            was_modified: Whether file was modified

        Returns:
            Updated filename
        """
        if not was_modified:
            return filename

        if self.auto_increment:
            return self.increment_version(filename)
        else:
            return filename

    def get_latest_version(self, base_name: str, directory: Path) -> int:
        """
        Get the latest version number for a base filename in a directory.

        Args:
            base_name: Base filename without version
            directory: Directory to search

        Returns:
            Latest version number (0 if none found)
        """
        max_version = 0
        base_lower = base_name.lower()

        for file_path in directory.iterdir():
            if not file_path.is_file():
                continue

            if base_lower in file_path.name.lower():
                version_info = self.extract_version_info(file_path.name)
                if version_info:
                    _, version_num = version_info
                    max_version = max(max_version, version_num)

        return max_version

    def generate_next_version_filename(
        self, base_name: str, directory: Path, date: Optional[datetime] = None
    ) -> str:
        """
        Generate next version filename for a base name.

        Args:
            base_name: Base filename
            directory: Directory to check for existing versions
            date: Date to use (default: today)

        Returns:
            Next version filename
        """
        latest_version = self.get_latest_version(base_name, directory)
        path_obj = Path(base_name)

        if date is None:
            date = datetime.now()

        day = date.day
        month = date.month
        date_part = f"{day:02d}{month:02d}"

        if latest_version > 0:
            new_version = latest_version + 1
        else:
            new_version = 1

        version_code = f"{date_part}_v{new_version}"
        stem = path_obj.stem
        extension = path_obj.suffix

        return f"{stem}_{version_code}{extension}"
