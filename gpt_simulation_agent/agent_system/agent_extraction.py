"""
Intelligent Extraction Module

Automatically extracts information from available sources.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger

from .utils.json_parser import JSONParser
from .utils.markdown_parser import MarkdownParser
from .agent_self_diagnosis import SelfDiagnosisEngine


class ExtractionEngine:
    """Engine for intelligent information extraction"""

    def __init__(self, workspace_path: str):
        """
        Initialize extraction engine

        Args:
            workspace_path: Path to workspace directory
        """
        self.workspace_path = Path(workspace_path)
        self.json_parser = JSONParser()
        self.md_parser = MarkdownParser()
        self.diagnosis_engine = SelfDiagnosisEngine(str(self.workspace_path))

    def extract_all(self) -> Dict[str, Any]:
        """
        Extract all available information

        Returns:
            Dictionary with extracted configuration
        """
        logger.info("Starting extraction...")

        diagnosis = self.diagnosis_engine.diagnose()
        extractable = diagnosis.get("auto_extractable", {})

        extracted = {
            "identity": self._extract_identity(extractable),
            "knowledge_base": self._extract_knowledge_base(extractable),
            "system_instructions": self._extract_system_instructions(extractable),
            "products": self._extract_products(extractable),
            "formulas": self._extract_formulas(extractable),
            "business_rules": self._extract_business_rules(extractable),
            "actions": self._extract_actions(extractable),
            "capabilities": diagnosis.get("capabilities", {}),
            "confidence_scores": {},
        }

        # Calculate confidence scores
        extracted["confidence_scores"] = self._calculate_confidence_scores(extracted)

        logger.info("Extraction completed")
        return extracted

    def _extract_identity(self, extractable: Dict) -> Dict:
        """Extract identity/role information"""
        identity = {}
        kb_files = extractable.get("knowledge_base", [])

        for file_path in kb_files:
            try:
                data = self.json_parser.parse(Path(file_path))
                identity_data = self.json_parser.extract_identity(data)
                if identity_data:
                    identity.update(identity_data)
                    break  # Use first found
            except Exception as e:
                logger.warning(f"Error extracting identity from {file_path}: {e}")

        return identity

    def _extract_knowledge_base(self, extractable: Dict) -> Dict:
        """Extract knowledge base structure"""
        kb_structure = {
            "files": [],
            "hierarchy": {},
        }

        diagnosis = self.diagnosis_engine.diagnose()
        kb_hierarchy = diagnosis.get("knowledge_base_hierarchy", {})

        for level, files in kb_hierarchy.items():
            kb_structure["hierarchy"][level] = [f["name"] for f in files]
            kb_structure["files"].extend([f["path"] for f in files])

        # Determine source of truth
        if kb_structure["hierarchy"].get("nivel_1_master"):
            kb_structure["source_of_truth"] = kb_structure["hierarchy"]["nivel_1_master"][
                0
            ]

        return kb_structure

    def _extract_system_instructions(self, extractable: Dict) -> Dict:
        """Extract system instructions"""
        instructions = {"full_text": "", "sections": {}}

        instruction_files = extractable.get("system_instructions", [])

        for file_path in instruction_files:
            try:
                path = Path(file_path)
                if path.suffix == ".md":
                    parsed = self.md_parser.parse(path)
                    instructions["sections"].update(parsed.get("sections", {}))
                    if not instructions["full_text"]:
                        instructions["full_text"] = parsed.get("full_text", "")
                else:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    if not instructions["full_text"]:
                        instructions["full_text"] = content
                    instructions["sections"]["full"] = content

            except Exception as e:
                logger.warning(f"Error extracting instructions from {file_path}: {e}")

        return instructions

    def _extract_products(self, extractable: Dict) -> Dict:
        """Extract product specifications"""
        all_products = {}

        kb_files = extractable.get("products", [])

        for file_path in kb_files:
            try:
                data = self.json_parser.parse(Path(file_path))
                products = self.json_parser.extract_products(data)
                if products:
                    all_products.update(products)
            except Exception as e:
                logger.warning(f"Error extracting products from {file_path}: {e}")

        return all_products

    def _extract_formulas(self, extractable: Dict) -> Dict:
        """Extract formulas"""
        all_formulas = {}

        formula_files = extractable.get("formulas", [])

        for file_path in formula_files:
            try:
                data = self.json_parser.parse(Path(file_path))
                formulas = self.json_parser.extract_formulas(data)
                if formulas:
                    all_formulas.update(formulas)
            except Exception as e:
                logger.warning(f"Error extracting formulas from {file_path}: {e}")

        return all_formulas

    def _extract_business_rules(self, extractable: Dict) -> Dict:
        """Extract business rules"""
        all_rules = {}

        rule_files = extractable.get("business_rules", [])

        for file_path in rule_files:
            try:
                data = self.json_parser.parse(Path(file_path))
                rules = self.json_parser.extract_business_rules(data)
                if rules:
                    all_rules.update(rules)
            except Exception as e:
                logger.warning(f"Error extracting rules from {file_path}: {e}")

        return all_rules

    def _extract_actions(self, extractable: Dict) -> List[Dict]:
        """Extract action schemas"""
        actions = []

        action_files = extractable.get("actions", [])

        for file_path in action_files:
            try:
                import yaml
                with open(file_path, "r", encoding="utf-8") as f:
                    action_schema = yaml.safe_load(f)
                if action_schema:
                    actions.append({"file": file_path, "schema": action_schema})
            except Exception as e:
                logger.warning(f"Error extracting actions from {file_path}: {e}")

        return actions

    def _calculate_confidence_scores(self, extracted: Dict) -> Dict[str, float]:
        """Calculate confidence scores for extracted data"""
        scores = {}

        # Identity confidence
        scores["identity"] = 1.0 if extracted.get("identity") else 0.0

        # Knowledge base confidence
        kb_files = extracted.get("knowledge_base", {}).get("files", [])
        scores["knowledge_base"] = min(len(kb_files) / 4.0, 1.0) if kb_files else 0.0

        # Instructions confidence
        instructions = extracted.get("system_instructions", {})
        scores["instructions"] = (
            1.0 if instructions.get("full_text") else 0.0
        )

        # Products confidence
        products = extracted.get("products", {})
        scores["products"] = min(len(products) / 10.0, 1.0) if products else 0.0

        # Formulas confidence
        formulas = extracted.get("formulas", {})
        scores["formulas"] = 1.0 if formulas else 0.0

        # Overall confidence
        scores["overall"] = sum(scores.values()) / len(scores) if scores else 0.0

        return scores
