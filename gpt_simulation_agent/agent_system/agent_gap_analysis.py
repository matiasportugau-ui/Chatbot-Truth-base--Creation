"""
Gap Analysis Module

Identifies missing information and generates guided extraction requests.
"""

from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
import json

from .agent_extraction import ExtractionEngine


class GapAnalysisEngine:
    """Engine for analyzing gaps and generating extraction requests"""

    def __init__(self, workspace_path: str, config_template_path: Optional[str] = None):
        """
        Initialize gap analysis engine

        Args:
            workspace_path: Path to workspace directory
            config_template_path: Path to configuration template JSON
        """
        self.workspace_path = Path(workspace_path)
        self.extraction_engine = ExtractionEngine(str(self.workspace_path))

        if config_template_path:
            self.template_path = Path(config_template_path)
        else:
            self.template_path = (
                Path(__file__).parent / "config" / "config_template.json"
            )

        self.template = self._load_template()

    def _load_template(self) -> Dict:
        """Load configuration template"""
        try:
            with open(self.template_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load template: {e}")
            return {}

    def analyze(self) -> Dict:
        """
        Perform gap analysis

        Returns:
            Dictionary with gap analysis results
        """
        logger.info("Starting gap analysis...")

        # Extract what we have
        extracted = self.extraction_engine.extract_all()

        # Compare against template
        gaps = self._identify_gaps(extracted, self.template)

        # Generate extraction requests
        requests = self._generate_extraction_requests(gaps, extracted)

        # Create manual extraction guides
        guides = self._create_extraction_guides(gaps)

        analysis = {
            "extracted_fields": self._get_extracted_fields(extracted),
            "missing_fields": gaps,
            "extraction_requests": requests,
            "manual_guides": guides,
            "completion_percentage": self._calculate_completion(extracted, self.template),
        }

        logger.info(f"Gap analysis completed. Completion: {analysis['completion_percentage']:.1f}%")
        return analysis

    def _identify_gaps(self, extracted: Dict, template: Dict) -> List[Dict]:
        """Identify missing fields by comparing extracted data with template"""
        gaps = []

        def check_nested(extracted_data: Any, template_data: Any, path: str = ""):
            if isinstance(template_data, dict):
                for key, value in template_data.items():
                    current_path = f"{path}.{key}" if path else key

                    if key not in extracted_data or not extracted_data[key]:
                        gaps.append({
                            "path": current_path,
                            "type": "missing",
                            "expected_type": type(value).__name__,
                            "description": f"Missing field: {current_path}",
                        })
                    elif isinstance(value, dict):
                        check_nested(
                            extracted_data.get(key, {}),
                            value,
                            current_path,
                        )
                    elif isinstance(value, list) and value:
                        # Check if list should have items
                        if not extracted_data.get(key):
                            gaps.append({
                                "path": current_path,
                                "type": "empty_list",
                                "description": f"Empty list expected at: {current_path}",
                            })

        # Check main sections
        for section in ["identity", "knowledge_base", "system_instructions", "capabilities"]:
            if section in template:
                check_nested(
                    extracted.get(section, {}),
                    template[section],
                    section,
                )

        return gaps

    def _generate_extraction_requests(self, gaps: List[Dict], extracted: Dict) -> Dict:
        """Generate extraction requests categorized by type"""
        requests = {
            "auto_extractable": [],
            "semi_automatic": [],
            "manual_required": [],
        }

        for gap in gaps:
            path = gap["path"]
            gap_type = gap["type"]

            # Determine extraction method
            if self._can_auto_extract(path, extracted):
                requests["auto_extractable"].append({
                    "field": path,
                    "method": "auto",
                    "source": self._suggest_source(path),
                    "description": gap["description"],
                })
            elif self._can_semi_auto_extract(path, extracted):
                requests["semi_automatic"].append({
                    "field": path,
                    "method": "semi_auto",
                    "source": self._suggest_source(path),
                    "description": gap["description"],
                    "guidance": self._generate_guidance(path),
                })
            else:
                requests["manual_required"].append({
                    "field": path,
                    "method": "manual",
                    "description": gap["description"],
                    "template": self._generate_template(path),
                })

        return requests

    def _can_auto_extract(self, path: str, extracted: Dict) -> bool:
        """Check if field can be auto-extracted"""
        # Fields that can typically be auto-extracted
        auto_extractable = [
            "identity.name",
            "identity.role",
            "knowledge_base.files",
            "products",
            "formulas",
            "business_rules",
        ]

        return any(path.startswith(prefix) for prefix in auto_extractable)

    def _can_semi_auto_extract(self, path: str, extracted: Dict) -> bool:
        """Check if field can be semi-automatically extracted"""
        # Fields that need user confirmation
        semi_auto = [
            "identity.personality",
            "system_instructions.sections",
            "capabilities",
        ]

        return any(path.startswith(prefix) for prefix in semi_auto)

    def _suggest_source(self, path: str) -> str:
        """Suggest source file for extraction"""
        if "identity" in path:
            return "Knowledge base JSON files"
        elif "knowledge_base" in path:
            return "Scanned workspace files"
        elif "system_instructions" in path:
            return "Markdown or text instruction files"
        elif "products" in path or "formulas" in path:
            return "Knowledge base JSON files"
        return "Unknown source"

    def _generate_guidance(self, path: str) -> str:
        """Generate guidance for semi-automatic extraction"""
        guidance = {
            "identity.personality": "Review personality settings in knowledge base files and confirm tone/style preferences.",
            "system_instructions.sections": "Review instruction files and confirm section organization.",
            "capabilities": "Check instruction files for capability mentions (Web Browsing, Code Interpreter, etc.).",
        }

        return guidance.get(path, "Please review and confirm this information.")

    def _generate_template(self, path: str) -> Dict:
        """Generate template for manual extraction"""
        templates = {
            "identity.personality.tone": {
                "type": "string",
                "options": ["professional", "casual", "technical", "friendly"],
                "example": "professional",
            },
            "identity.personality.style": {
                "type": "string",
                "options": ["consultative", "direct", "educational"],
                "example": "consultative",
            },
        }

        return templates.get(path, {"type": "string", "description": f"Provide value for {path}"})

    def _create_extraction_guides(self, gaps: List[Dict]) -> List[Dict]:
        """Create user-friendly extraction guides"""
        guides = []

        for gap in gaps:
            if gap["type"] == "manual_required" or "personality" in gap["path"]:
                guides.append({
                    "field": gap["path"],
                    "title": f"Guide: {gap['path']}",
                    "steps": self._generate_steps(gap),
                    "template": self._generate_template(gap["path"]),
                })

        return guides

    def _generate_steps(self, gap: Dict) -> List[str]:
        """Generate step-by-step extraction guide"""
        path = gap["path"]

        if "personality" in path:
            return [
                "1. Review existing instruction files for personality mentions",
                "2. Identify tone and style preferences",
                "3. Document personalization rules if any",
                "4. Confirm with user if needed",
            ]
        elif "capabilities" in path:
            return [
                "1. Check instruction files for capability mentions",
                "2. Look for: Web Browsing, Code Interpreter, Image Generation, Canvas",
                "3. Mark as enabled if mentioned",
            ]

        return [
            f"1. Locate information for {path}",
            "2. Extract relevant data",
            "3. Format according to template",
            "4. Validate and confirm",
        ]

    def _get_extracted_fields(self, extracted: Dict) -> List[str]:
        """Get list of successfully extracted fields"""
        fields = []

        def collect_fields(data: Any, prefix: str = ""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{prefix}.{key}" if prefix else key
                    if value:
                        if isinstance(value, (dict, list)):
                            collect_fields(value, current_path)
                        else:
                            fields.append(current_path)

        collect_fields(extracted)
        return fields

    def _calculate_completion(self, extracted: Dict, template: Dict) -> float:
        """Calculate completion percentage"""
        total_fields = self._count_template_fields(template)
        extracted_fields = len(self._get_extracted_fields(extracted))

        if total_fields == 0:
            return 0.0

        return (extracted_fields / total_fields) * 100.0

    def _count_template_fields(self, template: Dict) -> int:
        """Count total fields in template"""
        count = 0

        def count_nested(data: Any):
            nonlocal count
            if isinstance(data, dict):
                for value in data.values():
                    if isinstance(value, (dict, list)):
                        count_nested(value)
                    else:
                        count += 1
            elif isinstance(data, list):
                for item in data:
                    count_nested(item)

        count_nested(template)
        return count
