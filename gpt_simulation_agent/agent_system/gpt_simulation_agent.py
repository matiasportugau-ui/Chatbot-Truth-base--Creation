"""
Main GPT Simulation Agent Orchestrator

Orchestrates all phases of the self-configuring agent.
"""

from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
import json
from datetime import datetime

from .agent_self_diagnosis import SelfDiagnosisEngine
from .agent_extraction import ExtractionEngine
from .agent_gap_analysis import GapAnalysisEngine
from .agent_social_ingestion import SocialIngestionEngine
from .agent_training_processor import TrainingProcessor
from .agent_gem_generator import GemGeneratorEngine


class GPTSimulationAgent:
    """Main orchestrator for GPT simulation agent"""

    def __init__(
        self,
        workspace_path: str,
        output_dir: Optional[str] = None,
    ):
        """
        Initialize GPT simulation agent

        Args:
            workspace_path: Path to workspace with GPT configuration files
            output_dir: Directory for outputs
        """
        self.workspace_path = Path(workspace_path)
        self.output_dir = Path(output_dir) if output_dir else Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize engines
        self.diagnosis_engine = SelfDiagnosisEngine(str(self.workspace_path))
        self.extraction_engine = ExtractionEngine(str(self.workspace_path))
        self.gap_analysis_engine = GapAnalysisEngine(str(self.workspace_path))
        self.social_ingestion_engine = SocialIngestionEngine(
            output_dir=str(self.output_dir.parent / "training_data" / "social_media")
        )
        self.training_processor = TrainingProcessor(
            data_dir=str(self.output_dir.parent / "training_data")
        )
        self.gem_generator = GemGeneratorEngine(
            workspace_path=str(self.workspace_path),
            output_dir=str(self.output_dir)
        )

    def configure(self) -> Dict:
        """
        Perform complete self-configuration

        Returns:
            Configuration results
        """
        logger.info("Starting self-configuration...")

        # Phase 1: Self-diagnosis
        diagnosis = self.diagnosis_engine.diagnose()
        self._save_output("diagnosis.json", diagnosis)

        # Phase 2: Extraction
        extracted = self.extraction_engine.extract_all()
        self._save_output("extracted_configs/extracted_config.json", extracted)
        self._last_extracted_config = extracted  # Store for Gem generation

        # Phase 3: Gap analysis
        gap_analysis = self.gap_analysis_engine.analyze()
        self._save_output("gap_analysis_report.json", gap_analysis)

        # Generate user guides
        self._generate_user_guides(gap_analysis)

        return {
            "diagnosis": diagnosis,
            "extracted": extracted,
            "gap_analysis": gap_analysis,
            "completion": gap_analysis.get("completion_percentage", 0.0),
        }

    def ingest_social_media(
        self,
        platforms: List[str] = ["facebook", "instagram"],
        days_back: int = 30,
        limit: int = 1000,
    ) -> Dict:
        """
        Ingest social media interactions

        Args:
            platforms: Platforms to ingest from
            days_back: Days to look back
            limit: Max interactions per platform

        Returns:
            Ingestion results
        """
        logger.info(f"Ingesting from {platforms}...")
        results = self.social_ingestion_engine.ingest(
            platforms=platforms,
            days_back=days_back,
            limit_per_platform=limit,
        )
        self._save_output("social_ingestion_results.json", results)
        return results

    def process_training_data(self) -> Dict:
        """
        Process all training data

        Returns:
            Processing results
        """
        logger.info("Processing training data...")
        results = self.training_processor.process_all()

        # Generate analytics report
        if results.get("analysis"):
            report = self.training_processor.analytics_engine.generate_report(
                results["analysis"],
                output_path=str(self.output_dir / "analytics_reports" / "analytics_report.md"),
            )

        self._save_output("training_processing_results.json", results)
        return results

    def generate_analytics(self) -> Dict:
        """Generate analytics from processed data"""
        results = self.process_training_data()
        return results.get("analysis", {})

    def generate_gems(self, generate_multiple: bool = False) -> Dict:
        """
        Generate Google Labs Gems from extracted configuration

        Args:
            generate_multiple: If True, generates multiple Gems for different use cases

        Returns:
            Generated Gems data
        """
        logger.info("Generating Google Labs Gems...")

        # First, ensure we have extracted configuration
        if not hasattr(self, '_last_extracted_config'):
            logger.info("Running configuration extraction first...")
            config_result = self.configure()
            extracted = config_result.get("extracted", {})
        else:
            extracted = self._last_extracted_config

        if not extracted:
            logger.warning("No extracted configuration available. Run configure() first.")
            return {"error": "No extracted configuration available"}

        # Generate Gem(s)
        if generate_multiple:
            gems = self.gem_generator.generate_multiple_gems(extracted)
            result = {
                "gems": gems,
                "count": len(gems),
                "source": "extracted_config"
            }
        else:
            gem = self.gem_generator.generate_gem_from_config(extracted)
            result = {
                "gem": gem,
                "source": "extracted_config"
            }

        self._save_output("generated_gems_summary.json", result)
        return result

    def generate_gem_from_training(self) -> Dict:
        """
        Generate a Gem based on training data patterns

        Returns:
            Generated Gem based on training data
        """
        logger.info("Generating Gem from training data...")

        # Process training data if not already done
        training_results = self.process_training_data()

        # Generate Gem from training patterns
        gem = self.gem_generator.generate_gem_from_training_data(training_results)

        self._save_output("training_based_gem_summary.json", gem)
        return gem

    def _save_output(self, filename: str, data: Dict):
        """Save output to file"""
        filepath = self.output_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Saved output to {filepath}")

    def _generate_user_guides(self, gap_analysis: Dict):
        """Generate user-friendly extraction guides"""
        guides = gap_analysis.get("manual_guides", [])

        for guide in guides:
            guide_content = f"""
# {guide.get('title', 'Extraction Guide')}

## Field: {guide.get('field', 'Unknown')}

### Steps:
{chr(10).join(guide.get('steps', []))}

### Template:
```json
{json.dumps(guide.get('template', {}), indent=2)}
```
"""

            filename = f"manual_guides/{guide.get('field', 'guide').replace('.', '_')}.md"
            filepath = self.output_dir / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(guide_content)

            logger.info(f"Generated guide: {filepath}")
