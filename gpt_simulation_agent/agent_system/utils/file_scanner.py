"""
File Scanner Utility

Scans workspace for GPT configuration files and categorizes them.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class FileType(Enum):
    """File type categories for GPT configuration"""
    JSON_KNOWLEDGE_BASE = "json_kb"
    JSON_CONFIG = "json_config"
    MARKDOWN_INSTRUCTIONS = "md_instructions"
    MARKDOWN_DOCS = "md_docs"
    YAML_ACTIONS = "yaml_actions"
    TEXT_INSTRUCTIONS = "text_instructions"
    CSV_DATA = "csv_data"
    RTF_DOCS = "rtf_docs"
    UNKNOWN = "unknown"


@dataclass
class ScannedFile:
    """Represents a scanned file with metadata"""
    path: Path
    file_type: FileType
    size: int
    category: str
    confidence: float = 1.0
    metadata: Optional[Dict] = None


class FileScanner:
    """Scans and categorizes GPT configuration files"""

    KNOWLEDGE_BASE_PATTERNS = [
        "base_conocimiento",
        "catalogo",
        "truth",
        "knowledge",
        "catalog",
    ]

    INSTRUCTION_PATTERNS = [
        "instrucciones",
        "instructions",
        "system",
        "prompt",
        "config",
    ]

    ACTION_PATTERNS = [
        "action",
        "api",
        "schema",
        "openapi",
    ]

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        if not self.workspace_path.exists():
            raise ValueError(f"Workspace path does not exist: {workspace_path}")

    def scan(self, recursive: bool = True) -> List[ScannedFile]:
        """Scan workspace for configuration files"""
        scanned_files = []
        pattern = "**/*" if recursive else "*"

        for file_path in self.workspace_path.glob(pattern):
            if file_path.is_file() and not self._is_ignored(file_path):
                file_type = self._identify_file_type(file_path)
                category = self._categorize_file(file_path, file_type)
                confidence = self._calculate_confidence(file_path, file_type)

                scanned_files.append(
                    ScannedFile(
                        path=file_path,
                        file_type=file_type,
                        size=file_path.stat().st_size,
                        category=category,
                        confidence=confidence,
                        metadata=self._extract_metadata(file_path),
                    )
                )

        return sorted(scanned_files, key=lambda x: x.confidence, reverse=True)

    def _is_ignored(self, file_path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = [
            ".git",
            "__pycache__",
            ".DS_Store",
            "node_modules",
            ".venv",
            "venv",
            ".env",
        ]
        return any(pattern in str(file_path) for pattern in ignore_patterns)

    def _identify_file_type(self, file_path: Path) -> FileType:
        """Identify file type based on extension and name"""
        suffix = file_path.suffix.lower()
        name_lower = file_path.name.lower()

        if suffix == ".json":
            if any(pattern in name_lower for pattern in self.KNOWLEDGE_BASE_PATTERNS):
                return FileType.JSON_KNOWLEDGE_BASE
            return FileType.JSON_CONFIG

        elif suffix == ".md":
            if any(pattern in name_lower for pattern in self.INSTRUCTION_PATTERNS):
                return FileType.MARKDOWN_INSTRUCTIONS
            return FileType.MARKDOWN_DOCS

        elif suffix in [".yaml", ".yml"]:
            return FileType.YAML_ACTIONS

        elif suffix == ".txt":
            if any(pattern in name_lower for pattern in self.INSTRUCTION_PATTERNS):
                return FileType.TEXT_INSTRUCTIONS
            return FileType.TEXT_INSTRUCTIONS

        elif suffix == ".csv":
            return FileType.CSV_DATA

        elif suffix == ".rtf":
            return FileType.RTF_DOCS

        return FileType.UNKNOWN

    def _categorize_file(self, file_path: Path, file_type: FileType) -> str:
        """Categorize file into hierarchy levels"""
        name_lower = file_path.name.lower()

        if "base_conocimiento" in name_lower or "master" in name_lower:
            return "nivel_1_master"

        if "unificada" in name_lower or "backup" in name_lower:
            return "nivel_2_validation"

        if "web_only" in name_lower or "truth" in name_lower:
            return "nivel_3_dynamic"

        if file_type in [FileType.MARKDOWN_INSTRUCTIONS, FileType.TEXT_INSTRUCTIONS]:
            if "consolidacion" in name_lower or "sop" in name_lower:
                return "nivel_4_workflow"
            return "nivel_4_instructions"

        if file_type == FileType.RTF_DOCS:
            return "nivel_4_technical_rules"

        if file_type == FileType.CSV_DATA:
            return "nivel_4_index"

        return "nivel_4_support"

    def _calculate_confidence(self, file_path: Path, file_type: FileType) -> float:
        """Calculate confidence score for file identification"""
        confidence = 0.5

        if file_type != FileType.UNKNOWN:
            confidence += 0.3

        name_lower = file_path.name.lower()
        if any(pattern in name_lower for pattern in self.KNOWLEDGE_BASE_PATTERNS):
            confidence += 0.2

        return min(confidence, 1.0)

    def _extract_metadata(self, file_path: Path) -> Dict:
        """Extract additional metadata from file"""
        stat = file_path.stat()
        return {
            "modified_time": stat.st_mtime,
            "created_time": stat.st_ctime,
            "extension": file_path.suffix,
            "stem": file_path.stem,
        }

    def get_files_by_type(self, file_type: FileType) -> List[ScannedFile]:
        """Get all files of a specific type"""
        all_files = self.scan()
        return [f for f in all_files if f.file_type == file_type]

    def get_files_by_category(self, category: str) -> List[ScannedFile]:
        """Get all files in a specific category"""
        all_files = self.scan()
        return [f for f in all_files if f.category == category]

    def get_knowledge_base_hierarchy(self) -> Dict[str, List[ScannedFile]]:
        """Get knowledge base files organized by hierarchy level"""
        all_files = self.scan()
        hierarchy = {
            "nivel_1_master": [],
            "nivel_2_validation": [],
            "nivel_3_dynamic": [],
            "nivel_4_support": [],
        }

        for file in all_files:
            if file.category in hierarchy:
                hierarchy[file.category].append(file)

        return hierarchy
