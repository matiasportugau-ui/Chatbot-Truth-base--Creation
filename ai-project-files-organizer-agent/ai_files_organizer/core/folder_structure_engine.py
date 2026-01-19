"""
Folder Structure Engine for generating organization proposals
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from .file_scanner import FileMetadata


class FolderStructureEngine:
    """
    Generates folder structure proposals based on best practices
    """

    def __init__(self, rules_file: Optional[Path] = None):
        """
        Initialize folder structure engine.

        Args:
            rules_file: Path to folder rules JSON file
        """
        self.rules_file = rules_file
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict:
        """Load folder organization rules"""
        if self.rules_file and self.rules_file.exists():
            try:
                with open(self.rules_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # Default rules
        return {
            "rules": [
                {
                    "category": "documentation",
                    "extensions": [".md", ".txt", ".rtf"],
                    "target_folder": "docs",
                },
                {
                    "category": "configuration",
                    "extensions": [".yaml", ".yml", ".json"],
                    "target_folder": "config",
                },
                {
                    "category": "code",
                    "extensions": [".py", ".js", ".ts"],
                    "target_folder": "src",
                },
            ],
            "default_folder": "misc",
        }

    def generate_proposal(
        self, file_meta: FileMetadata, workspace_path: Path
    ) -> Dict:
        """
        Generate folder structure proposal for a file.

        Args:
            file_meta: File metadata
            workspace_path: Workspace root path

        Returns:
            Proposal dictionary with location and justification
        """
        # Find matching rule
        rule = self._find_matching_rule(file_meta)

        if rule:
            target_folder = rule.get("target_folder", "misc")
            subfolder = self._determine_subfolder(file_meta, rule)

            if subfolder:
                proposed_path = workspace_path / target_folder / subfolder
            else:
                proposed_path = workspace_path / target_folder

            confidence = self._calculate_confidence(file_meta, rule)
            justification = self._generate_justification(file_meta, rule, subfolder)

        else:
            # Use default folder
            proposed_path = workspace_path / self.rules.get("default_folder", "misc")
            confidence = 0.5
            justification = "No specific rule matched, using default location"

        return {
            "file": file_meta.path,
            "current_location": str(file_meta.path.parent),
            "proposed_location": str(proposed_path),
            "proposed_name": file_meta.path.name,
            "justification": justification,
            "confidence": confidence,
            "actions": self._determine_actions(file_meta.path, proposed_path),
        }

    def _find_matching_rule(self, file_meta: FileMetadata) -> Optional[Dict]:
        """Find matching rule for file"""
        for rule in self.rules.get("rules", []):
            # Check extension
            if file_meta.extension in rule.get("extensions", []):
                return rule

            # Check category
            if file_meta.category == rule.get("category"):
                return rule

            # Check patterns
            patterns = rule.get("patterns", [])
            for pattern in patterns:
                if pattern.lower() in file_meta.name.lower():
                    return rule

        return None

    def _determine_subfolder(
        self, file_meta: FileMetadata, rule: Dict
    ) -> Optional[str]:
        """Determine subfolder based on file name patterns"""
        subfolders = rule.get("subfolders", {})
        name_lower = file_meta.name.lower()

        for subfolder_name, patterns in subfolders.items():
            for pattern in patterns:
                if pattern.lower() in name_lower:
                    return subfolder_name

        return None

    def _calculate_confidence(
        self, file_meta: FileMetadata, rule: Dict
    ) -> float:
        """Calculate confidence score for proposal"""
        confidence = 0.7  # Base confidence

        # Extension match increases confidence
        if file_meta.extension in rule.get("extensions", []):
            confidence += 0.2

        # Category match increases confidence
        if file_meta.category == rule.get("category"):
            confidence += 0.1

        return min(confidence, 1.0)

    def _generate_justification(
        self, file_meta: FileMetadata, rule: Dict, subfolder: Optional[str]
    ) -> str:
        """Generate justification for proposal"""
        category = rule.get("category", "unknown")
        target_folder = rule.get("target_folder", "misc")

        justification = f"File is categorized as '{category}' and should be in '{target_folder}'"

        if subfolder:
            justification += f"/{subfolder}"

        justification += " based on best practices for project organization."

        return justification

    def _determine_actions(
        self, current_path: Path, proposed_path: Path
    ) -> List[str]:
        """Determine actions needed to organize file"""
        actions = []

        if current_path.parent != proposed_path:
            actions.append("move")

        # Check if renaming is needed (version codes, etc.)
        # This would be handled by version_manager separately

        return actions

    def generate_batch_proposals(
        self, files: List[FileMetadata], workspace_path: Path
    ) -> List[Dict]:
        """
        Generate proposals for multiple files.

        Args:
            files: List of file metadata
            workspace_path: Workspace root path

        Returns:
            List of proposal dictionaries
        """
        proposals = []
        for file_meta in files:
            proposal = self.generate_proposal(file_meta, workspace_path)
            proposals.append(proposal)

        return proposals
