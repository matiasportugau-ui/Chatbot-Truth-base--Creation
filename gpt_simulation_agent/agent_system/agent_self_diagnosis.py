"""
Self-Diagnosis Engine

Analyzes workspace to identify GPT configuration needs and components.
"""

from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

from .utils.file_scanner import FileScanner, FileType
from .utils.json_parser import JSONParser
from .utils.markdown_parser import MarkdownParser


class SelfDiagnosisEngine:
    """Engine for self-diagnosing configuration needs"""

    def __init__(self, workspace_path: str):
        """
        Initialize self-diagnosis engine

        Args:
            workspace_path: Path to workspace directory
        """
        self.workspace_path = Path(workspace_path)
        self.scanner = FileScanner(str(self.workspace_path))
        self.json_parser = JSONParser()
        self.md_parser = MarkdownParser()

    def diagnose(self) -> Dict:
        """
        Perform complete self-diagnosis

        Returns:
            Dictionary with diagnosis results
        """
        logger.info("Starting self-diagnosis...")

        # Scan files
        scanned_files = self.scanner.scan()
        logger.info(f"Found {len(scanned_files)} files")

        # Get knowledge base hierarchy
        kb_hierarchy = self.scanner.get_knowledge_base_hierarchy()

        # Identify configuration components
        components = self._identify_components(scanned_files)

        # Map knowledge base structure
        kb_structure = self._map_knowledge_base_structure(kb_hierarchy)

        # Extract system instruction patterns
        instruction_patterns = self._extract_instruction_patterns(scanned_files)

        # Identify capabilities
        capabilities = self._identify_capabilities(scanned_files)

        diagnosis = {
            "workspace_path": str(self.workspace_path),
            "total_files": len(scanned_files),
            "scanned_files": [
                {
                    "path": str(f.path),
                    "type": f.file_type.value,
                    "category": f.category,
                    "confidence": f.confidence,
                }
                for f in scanned_files
            ],
            "knowledge_base_hierarchy": kb_structure,
            "components": components,
            "instruction_patterns": instruction_patterns,
            "capabilities": capabilities,
            "auto_extractable": self._identify_auto_extractable(scanned_files),
        }

        logger.info("Self-diagnosis completed")
        return diagnosis

    def _identify_components(self, scanned_files: List) -> Dict:
        """Identify configuration components from files"""
        components = {
            "knowledge_base_files": [],
            "instruction_files": [],
            "action_files": [],
            "support_files": [],
        }

        for file in scanned_files:
            if file.file_type == FileType.JSON_KNOWLEDGE_BASE:
                components["knowledge_base_files"].append(str(file.path))
            elif file.file_type in [
                FileType.MARKDOWN_INSTRUCTIONS,
                FileType.TEXT_INSTRUCTIONS,
            ]:
                components["instruction_files"].append(str(file.path))
            elif file.file_type == FileType.YAML_ACTIONS:
                components["action_files"].append(str(file.path))
            else:
                components["support_files"].append(str(file.path))

        return components

    def _map_knowledge_base_structure(self, kb_hierarchy: Dict) -> Dict:
        """Map knowledge base structure by hierarchy levels"""
        structure = {}
        for level, files in kb_hierarchy.items():
            structure[level] = [
                {
                    "path": str(f.path),
                    "name": f.path.name,
                    "size": f.size,
                    "confidence": f.confidence,
                }
                for f in files
            ]
        return structure

    def _extract_instruction_patterns(self, scanned_files: List) -> Dict:
        """Extract patterns from instruction files"""
        patterns = {
            "personalization": False,
            "source_of_truth": False,
            "quotation_process": False,
            "special_commands": False,
            "guardrails": False,
        }

        instruction_files = [
            f
            for f in scanned_files
            if f.file_type
            in [FileType.MARKDOWN_INSTRUCTIONS, FileType.TEXT_INSTRUCTIONS]
        ]

        for file in instruction_files:
            try:
                if file.path.suffix == ".md":
                    content = self.md_parser.parse(file.path)
                    text = content.get("full_text", "").lower()
                else:
                    with open(file.path, "r", encoding="utf-8") as f:
                        text = f.read().lower()

                # Check for patterns
                if "personalizaci" in text or "personalization" in text:
                    patterns["personalization"] = True
                if "fuente de verdad" in text or "source of truth" in text:
                    patterns["source_of_truth"] = True
                if "cotizaci" in text or "quotation" in text:
                    patterns["quotation_process"] = True
                if "/estado" in text or "/checkpoint" in text or "command" in text:
                    patterns["special_commands"] = True
                if "guardrail" in text or "validaci" in text:
                    patterns["guardrails"] = True

            except Exception as e:
                logger.warning(f"Error reading {file.path}: {e}")

        return patterns

    def _identify_capabilities(self, scanned_files: List) -> Dict:
        """Identify enabled capabilities from files"""
        capabilities = {
            "web_browsing": False,
            "code_interpreter": False,
            "image_generation": False,
            "canvas": False,
        }

        # Check instruction files for capability mentions
        instruction_files = [
            f
            for f in scanned_files
            if f.file_type
            in [FileType.MARKDOWN_INSTRUCTIONS, FileType.TEXT_INSTRUCTIONS]
        ]

        for file in instruction_files:
            try:
                if file.path.suffix == ".md":
                    content = self.md_parser.parse(file.path)
                    text = content.get("full_text", "").lower()
                else:
                    with open(file.path, "r", encoding="utf-8") as f:
                        text = f.read().lower()

                if "web browsing" in text or "web search" in text:
                    capabilities["web_browsing"] = True
                if "code interpreter" in text or "code interpreter" in text:
                    capabilities["code_interpreter"] = True
                if "image generation" in text or "dall-e" in text:
                    capabilities["image_generation"] = True
                if "canvas" in text:
                    capabilities["canvas"] = True

            except Exception as e:
                logger.warning(f"Error reading {file.path}: {e}")

        return capabilities

    def _identify_auto_extractable(self, scanned_files: List) -> Dict:
        """Identify what can be automatically extracted"""
        extractable = {
            "knowledge_base": [],
            "system_instructions": [],
            "products": [],
            "formulas": [],
            "business_rules": [],
            "actions": [],
        }

        for file in scanned_files:
            if file.file_type == FileType.JSON_KNOWLEDGE_BASE:
                extractable["knowledge_base"].append(str(file.path))
                extractable["products"].append(str(file.path))
                extractable["formulas"].append(str(file.path))
                extractable["business_rules"].append(str(file.path))
            elif file.file_type in [
                FileType.MARKDOWN_INSTRUCTIONS,
                FileType.TEXT_INSTRUCTIONS,
            ]:
                extractable["system_instructions"].append(str(file.path))
            elif file.file_type == FileType.YAML_ACTIONS:
                extractable["actions"].append(str(file.path))

        return extractable
