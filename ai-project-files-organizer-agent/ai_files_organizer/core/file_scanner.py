"""
Enhanced File Scanner with categorization and metadata extraction
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import mimetypes


@dataclass
class FileMetadata:
    """Metadata for a scanned file"""

    path: Path
    name: str
    extension: str
    size: int
    modified_time: datetime
    category: str
    file_type: str
    content_hash: Optional[str] = None
    version_code: Optional[str] = None
    is_duplicate: bool = False
    duplicate_of: Optional[Path] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "path": str(self.path),
            "name": self.name,
            "extension": self.extension,
            "size": self.size,
            "modified_time": self.modified_time.isoformat(),
            "category": self.category,
            "file_type": self.file_type,
            "content_hash": self.content_hash,
            "version_code": self.version_code,
            "is_duplicate": self.is_duplicate,
            "duplicate_of": str(self.duplicate_of) if self.duplicate_of else None,
            "metadata": self.metadata,
        }


class FileScanner:
    """
    Enhanced file scanner with categorization and metadata extraction
    """

    # File type mappings
    DOCUMENTATION_EXTENSIONS = {".md", ".txt", ".rtf", ".rst", ".adoc"}
    CONFIG_EXTENSIONS = {".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".conf"}
    CODE_EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".go",
        ".rs",
        ".rb",
        ".php",
    }
    DATA_EXTENSIONS = {".json", ".csv", ".xml", ".parquet", ".xlsx", ".db"}
    OUTPUT_EXTENSIONS = {".log", ".out", ".report", ".pdf"}

    def __init__(self, workspace_path: str, exclude_patterns: Optional[List[str]] = None):
        """
        Initialize file scanner.

        Args:
            workspace_path: Root path to scan
            exclude_patterns: List of patterns to exclude (e.g., ['*.pyc', '__pycache__'])
        """
        self.workspace_path = Path(workspace_path).resolve()
        self.exclude_patterns = exclude_patterns or [
            "*.pyc",
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            "*.egg-info",
        ]
        self.scanned_files: List[FileMetadata] = []
        self.content_hashes: Dict[str, Path] = {}

    def scan(self, recursive: bool = True) -> List[FileMetadata]:
        """
        Scan workspace for files.

        Args:
            recursive: If True, scan recursively

        Returns:
            List of FileMetadata objects
        """
        self.scanned_files = []
        self.content_hashes = {}

        if not self.workspace_path.exists():
            return []

        if recursive:
            files = self._scan_recursive()
        else:
            files = [
                f
                for f in self.workspace_path.iterdir()
                if f.is_file() and not self._should_exclude(f)
            ]

        for file_path in files:
            metadata = self._extract_metadata(file_path)
            if metadata:
                self.scanned_files.append(metadata)
                self._check_duplicates(metadata)

        return self.scanned_files

    def _scan_recursive(self) -> List[Path]:
        """Recursively scan directory"""
        files = []
        for item in self.workspace_path.rglob("*"):
            if item.is_file() and not self._should_exclude(item):
                files.append(item)
        return files

    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded"""
        path_str = str(path)
        for pattern in self.exclude_patterns:
            if pattern in path_str or path.match(pattern):
                return True
        return False

    def _extract_metadata(self, file_path: Path) -> Optional[FileMetadata]:
        """Extract metadata from file"""
        try:
            stat = file_path.stat()
            extension = file_path.suffix.lower()
            category = self._categorize_file(file_path, extension)
            file_type = self._get_file_type(extension)

            # Calculate content hash
            content_hash = self._calculate_hash(file_path)

            # Extract version code from filename
            version_code = self._extract_version_code(file_path.name)

            metadata = FileMetadata(
                path=file_path,
                name=file_path.name,
                extension=extension,
                size=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                category=category,
                file_type=file_type,
                content_hash=content_hash,
                version_code=version_code,
            )

            return metadata

        except Exception:
            return None

    def _categorize_file(self, file_path: Path, extension: str) -> str:
        """Categorize file based on extension and name"""
        name_lower = file_path.name.lower()

        # Check patterns
        if extension in self.DOCUMENTATION_EXTENSIONS:
            return "documentation"
        elif extension in self.CONFIG_EXTENSIONS:
            if "config" in name_lower or "setup" in name_lower:
                return "configuration"
            elif "bundle" in name_lower or "training" in name_lower:
                return "training"
            else:
                return "data"
        elif extension in self.CODE_EXTENSIONS:
            return "code"
        elif extension in self.DATA_EXTENSIONS:
            if "training" in name_lower or "bundle" in name_lower:
                return "training"
            else:
                return "data"
        elif extension in self.OUTPUT_EXTENSIONS:
            return "output"
        else:
            return "other"

    def _get_file_type(self, extension: str) -> str:
        """Get MIME type for file"""
        mime_type, _ = mimetypes.guess_type(f"file{extension}")
        return mime_type or "application/octet-stream"

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file content"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""

    def _extract_version_code(self, filename: str) -> Optional[str]:
        """Extract version code from filename (format: ddmm_vN)"""
        import re

        # Pattern: _ddmm_vN or _ddmmvN
        pattern = r"_(\d{4})_?v(\d+)"
        match = re.search(pattern, filename)
        if match:
            date_part = match.group(1)
            version_part = match.group(2)
            return f"{date_part}_v{version_part}"

        # Also check for vN patterns
        pattern_v = r"[_v](\d+)(?:\.\d+)*"
        match_v = re.search(pattern_v, filename)
        if match_v:
            return f"v{match_v.group(1)}"

        return None

    def _check_duplicates(self, metadata: FileMetadata):
        """Check for duplicate files based on content hash"""
        if not metadata.content_hash:
            return

        if metadata.content_hash in self.content_hashes:
            metadata.is_duplicate = True
            metadata.duplicate_of = self.content_hashes[metadata.content_hash]
        else:
            self.content_hashes[metadata.content_hash] = metadata.path

    def get_files_by_category(self, category: str) -> List[FileMetadata]:
        """Get all files in a specific category"""
        return [f for f in self.scanned_files if f.category == category]

    def get_duplicates(self) -> List[FileMetadata]:
        """Get all duplicate files"""
        return [f for f in self.scanned_files if f.is_duplicate]

    def get_files_by_extension(self, extension: str) -> List[FileMetadata]:
        """Get all files with specific extension"""
        return [f for f in self.scanned_files if f.extension == extension]
