"""
Analytics Engine

Processes interaction data and generates analytics reports.
"""

from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter
from datetime import datetime
import json
import pandas as pd
from loguru import logger


class AnalyticsEngine:
    """Engine for analyzing interaction data"""

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize analytics engine

        Args:
            data_dir: Directory containing interaction data
        """
        self.data_dir = Path(data_dir) if data_dir else Path("training_data")

    def analyze_interactions(self, interactions: List[Dict]) -> Dict:
        """Analyze interaction patterns"""
        if not interactions:
            return {}

        df = pd.DataFrame(interactions)

        analysis = {
            "total_interactions": len(interactions),
            "by_platform": self._analyze_by_platform(df),
            "by_type": self._analyze_by_type(df),
            "common_queries": self._find_common_queries(df),
            "question_rate": self._calculate_question_rate(df),
            "engagement_metrics": self._calculate_engagement(df),
            "temporal_patterns": self._analyze_temporal(df),
        }

        return analysis

    def _analyze_by_platform(self, df: pd.DataFrame) -> Dict:
        """Analyze interactions by platform"""
        if "platform" not in df.columns:
            return {}
        return df["platform"].value_counts().to_dict()

    def _analyze_by_type(self, df: pd.DataFrame) -> Dict:
        """Analyze interactions by type"""
        if "type" not in df.columns:
            return {}
        return df["type"].value_counts().to_dict()

    def _find_common_queries(self, df: pd.DataFrame, top_n: int = 10) -> List[Dict]:
        """Find most common queries"""
        if "content" not in df.columns:
            return []

        # Extract questions
        questions = df[df["metadata"].apply(lambda x: x.get("is_question", False) if isinstance(x, dict) else False)]["content"].tolist()

        # Simple keyword extraction
        keywords = []
        for q in questions:
            words = q.lower().split()[:5]  # First 5 words
            keywords.extend(words)

        counter = Counter(keywords)
        return [{"query": k, "count": v} for k, v in counter.most_common(top_n)]

    def _calculate_question_rate(self, df: pd.DataFrame) -> float:
        """Calculate percentage of questions"""
        if "metadata" not in df.columns:
            return 0.0

        total = len(df)
        questions = df["metadata"].apply(
            lambda x: x.get("is_question", False) if isinstance(x, dict) else False
        ).sum()

        return (questions / total * 100) if total > 0 else 0.0

    def _calculate_engagement(self, df: pd.DataFrame) -> Dict:
        """Calculate engagement metrics"""
        if "engagement" not in df.columns:
            return {}

        total_likes = df["engagement"].apply(
            lambda x: x.get("likes", 0) if isinstance(x, dict) else 0
        ).sum()

        total_replies = df["engagement"].apply(
            lambda x: x.get("replies", 0) if isinstance(x, dict) else 0
        ).sum()

        return {
            "total_likes": int(total_likes),
            "total_replies": int(total_replies),
            "avg_likes_per_interaction": float(total_likes / len(df)) if len(df) > 0 else 0.0,
        }

    def _analyze_temporal(self, df: pd.DataFrame) -> Dict:
        """Analyze temporal patterns"""
        if "timestamp" not in df.columns:
            return {}

        try:
            df["datetime"] = pd.to_datetime(df["timestamp"])
            df["hour"] = df["datetime"].dt.hour
            df["day_of_week"] = df["datetime"].dt.day_name()

            return {
                "peak_hours": df["hour"].mode().tolist(),
                "peak_days": df["day_of_week"].mode().tolist(),
            }
        except:
            return {}

    def generate_report(self, analysis: Dict, output_path: Optional[str] = None) -> str:
        """Generate analytics report"""
        report = f"""
# Interaction Analytics Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Interactions: {analysis.get('total_interactions', 0)}
- Question Rate: {analysis.get('question_rate', 0):.1f}%

## By Platform
{self._format_dict(analysis.get('by_platform', {}))}

## By Type
{self._format_dict(analysis.get('by_type', {}))}

## Common Queries
{self._format_list(analysis.get('common_queries', []))}

## Engagement
{self._format_dict(analysis.get('engagement_metrics', {}))}
"""

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)

        return report

    def _format_dict(self, d: Dict) -> str:
        """Format dictionary for report"""
        return "\n".join(f"- {k}: {v}" for k, v in d.items())

    def _format_list(self, l: List) -> str:
        """Format list for report"""
        return "\n".join(f"- {item.get('query', '')}: {item.get('count', 0)}" for item in l)
