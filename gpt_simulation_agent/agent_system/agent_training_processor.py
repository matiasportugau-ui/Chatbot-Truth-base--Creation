"""
Training Data Processor

Processes training data from multiple sources and performs analytics.
"""

from pathlib import Path
from typing import Dict, List, Optional
import json
from loguru import logger

from .utils.analytics_engine import AnalyticsEngine
from .agent_social_ingestion import SocialIngestionEngine


class TrainingProcessor:
    """Processor for training data"""

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize training processor

        Args:
            data_dir: Directory containing training data
        """
        self.data_dir = Path(data_dir) if data_dir else Path("training_data")
        self.analytics_engine = AnalyticsEngine(str(self.data_dir))

    def process_all(self) -> Dict:
        """Process all training data sources"""
        logger.info("Processing all training data...")

        # Load interactions from all sources
        all_interactions = []

        # Load social media interactions
        social_interactions = self._load_social_media_interactions()
        all_interactions.extend(social_interactions)

        # Load quotes
        quotes = self._load_quotes()
        all_interactions.extend(quotes)

        # Load general interactions
        general = self._load_general_interactions()
        all_interactions.extend(general)

        # Analyze
        analysis = self.analytics_engine.analyze_interactions(all_interactions)

        return {
            "total_interactions": len(all_interactions),
            "sources": {
                "social_media": len(social_interactions),
                "quotes": len(quotes),
                "general": len(general),
            },
            "analysis": analysis,
        }

    def _load_social_media_interactions(self) -> List[Dict]:
        """Load social media interactions"""
        interactions = []
        social_dir = self.data_dir / "social_media"

        if not social_dir.exists():
            return interactions

        for platform_dir in social_dir.iterdir():
            if platform_dir.is_dir():
                for type_dir in platform_dir.iterdir():
                    if type_dir.is_dir():
                        for json_file in type_dir.glob("*.json"):
                            try:
                                with open(json_file, "r", encoding="utf-8") as f:
                                    data = json.load(f)
                                    if isinstance(data, list):
                                        interactions.extend(data)
                                    else:
                                        interactions.append(data)
                            except Exception as e:
                                logger.warning(f"Error loading {json_file}: {e}")

        return interactions

    def _load_quotes(self) -> List[Dict]:
        """Load quote examples"""
        quotes = []
        quotes_dir = self.data_dir / "quotes"

        if quotes_dir.exists():
            for json_file in quotes_dir.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            quotes.extend(data)
                        else:
                            quotes.append(data)
                except Exception as e:
                    logger.warning(f"Error loading {json_file}: {e}")

        return quotes

    def _load_general_interactions(self) -> List[Dict]:
        """Load general interactions"""
        interactions = []
        interactions_dir = self.data_dir / "interactions"

        if interactions_dir.exists():
            for json_file in interactions_dir.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            interactions.extend(data)
                        else:
                            interactions.append(data)
                except Exception as e:
                    logger.warning(f"Error loading {json_file}: {e}")

        return interactions
