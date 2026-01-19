"""
Outdated File Detector with date and content analysis
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from .file_scanner import FileMetadata, FileScanner


class OutdatedDetector:
    """
    Detects outdated files based on multiple criteria
    """

    def __init__(
        self,
        days_threshold: int = 90,
        check_content: bool = True,
        check_references: bool = True,
    ):
        """
        Initialize outdated detector.

        Args:
            days_threshold: Days since modification to consider outdated
            check_content: If True, check content for duplicates
            check_references: If True, check if files are referenced
        """
        self.days_threshold = days_threshold
        self.check_content = check_content
        self.check_references = check_references

    def detect_outdated(
        self, files: List[FileMetadata], workspace_path: Path
    ) -> List[Dict]:
        """
        Detect outdated files.

        Args:
            files: List of file metadata
            workspace_path: Workspace root path

        Returns:
            List of outdated file reports with reasons
        """
        outdated_files = []
        threshold_date = datetime.now() - timedelta(days=self.days_threshold)

        for file_meta in files:
            reasons = []

            # Check by date
            if file_meta.modified_time < threshold_date:
                days_old = (datetime.now() - file_meta.modified_time).days
                reasons.append(
                    {
                        "type": "date",
                        "reason": f"Not modified in {days_old} days (threshold: {self.days_threshold})",
                        "severity": "medium",
                    }
                )

            # Check for duplicates
            if self.check_content and file_meta.is_duplicate:
                reasons.append(
                    {
                        "type": "duplicate",
                        "reason": f"Duplicate of {file_meta.duplicate_of}",
                        "severity": "high",
                    }
                )

            # Check version age
            if file_meta.version_code:
                version_info = self._parse_version_code(file_meta.version_code)
                if version_info:
                    date_part, version_num = version_info
                    # Check if version is very old
                    try:
                        day = int(date_part[:2])
                        month = int(date_part[2:])
                        version_date = datetime(
                            datetime.now().year, month, day
                        )
                        if version_date < threshold_date:
                            reasons.append(
                                {
                                    "type": "version_age",
                                    "reason": f"Version code indicates old date: {date_part}",
                                    "severity": "low",
                                }
                            )
                    except (ValueError, IndexError):
                        pass

            # Check references (if enabled)
            if self.check_references:
                is_referenced = self._check_file_references(
                    file_meta.path, workspace_path
                )
                if not is_referenced:
                    reasons.append(
                        {
                            "type": "unreferenced",
                            "reason": "File not referenced in code or documentation",
                            "severity": "low",
                        }
                    )

            if reasons:
                outdated_files.append(
                    {
                        "file": file_meta.path,
                        "metadata": file_meta.to_dict(),
                        "reasons": reasons,
                        "suggested_action": self._suggest_action(reasons),
                    }
                )

        return outdated_files

    def _parse_version_code(self, version_code: str) -> Optional[tuple]:
        """Parse version code to extract date and version"""
        import re

        pattern = r"(\d{4})_v(\d+)"
        match = re.match(pattern, version_code)
        if match:
            date_part = match.group(1)
            version_num = int(match.group(2))
            return (date_part, version_num)
        return None

    def _check_file_references(
        self, file_path: Path, workspace_path: Path
    ) -> bool:
        """
        Check if file is referenced in other files.

        Args:
            file_path: File to check
            workspace_path: Workspace root

        Returns:
            True if file is referenced
        """
        file_name = file_path.name
        file_stem = file_path.stem

        # Search in code files
        code_extensions = {".py", ".js", ".ts", ".md", ".txt", ".yaml", ".yml"}

        for code_file in workspace_path.rglob("*"):
            if (
                code_file.is_file()
                and code_file.suffix in code_extensions
                and code_file != file_path
            ):
                try:
                    content = code_file.read_text(encoding="utf-8", errors="ignore")
                    if file_name in content or file_stem in content:
                        return True
                except Exception:
                    continue

        return False

    def _suggest_action(self, reasons: List[Dict]) -> str:
        """
        Suggest action based on reasons.

        Args:
            reasons: List of reason dictionaries

        Returns:
            Suggested action string
        """
        has_duplicate = any(r["type"] == "duplicate" for r in reasons)
        has_date = any(r["type"] == "date" for r in reasons)
        has_unreferenced = any(r["type"] == "unreferenced" for r in reasons)

        if has_duplicate:
            return "archive_or_delete"
        elif has_date and has_unreferenced:
            return "archive"
        elif has_date:
            return "review_and_update"
        else:
            return "review"
