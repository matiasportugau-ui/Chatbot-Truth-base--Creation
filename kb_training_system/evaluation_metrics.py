"""
Evaluation Metrics
==================

Standard evaluation metrics for chatbot knowledge base interactions.
Based on industry standards: Azure AI Evaluation, RAG evaluation frameworks.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import re
from collections import Counter


@dataclass
class MetricScore:
    """Individual metric score"""
    name: str
    value: float
    max_value: float = 1.0
    weight: float = 1.0
    description: str = ""


class EvaluationMetrics:
    """
    Standard evaluation metrics for KB interactions.
    
    Metrics:
    - Relevance: Query-response matching
    - Groundedness: KB data reliance
    - Coherence: Logical consistency
    - Accuracy: BLEU, Precision, Recall, F1
    - Source Compliance: Source of truth adherence
    """
    
    @staticmethod
    def calculate_relevance(query: str, response: str) -> float:
        """Calculate relevance score (0-1)"""
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Extract key terms
        query_terms = set(re.findall(r'\b\w{4,}\b', query_lower))
        
        if not query_terms:
            return 0.5
        
        # Check term overlap
        matches = sum(1 for term in query_terms if term in response_lower)
        relevance = matches / len(query_terms)
        
        return min(1.0, relevance)
    
    @staticmethod
    def calculate_groundedness(response: str, sources: List[str]) -> float:
        """Calculate groundedness score (0-1)"""
        if not sources:
            return 0.0
        
        response_lower = response.lower()
        
        # Data indicators
        indicators = [
            "según", "en la base", "según el archivo",
            "precio", "costo", "espesor", "autoportancia"
        ]
        
        indicators_found = sum(1 for ind in indicators if ind in response_lower)
        base_score = 0.5 if sources else 0.0
        indicator_score = min(0.5, indicators_found * 0.1)
        
        # Penalize vague responses
        vague_phrases = ["no estoy seguro", "creo que", "probablemente"]
        vague_penalty = sum(0.1 for phrase in vague_phrases if phrase in response_lower)
        
        return max(0.0, min(1.0, base_score + indicator_score - vague_penalty))
    
    @staticmethod
    def calculate_coherence(response: str) -> float:
        """Calculate coherence score (0-1)"""
        response_lower = response.lower()
        
        # Check for contradictions
        contradictions = [
            ("precio", "gratis"),
            ("incluye", "no incluye")
        ]
        
        for term1, term2 in contradictions:
            if term1 in response_lower and term2 in response_lower:
                return 0.3
        
        # Structure score
        has_structure = any(marker in response for marker in [":", "-", "•"])
        structure_score = 0.3 if has_structure else 0.0
        
        # Length score
        word_count = len(response.split())
        length_score = 0.4 if 20 <= word_count <= 500 else 0.2
        
        return min(1.0, structure_score + length_score + 0.3)
    
    @staticmethod
    def calculate_accuracy(response: str, ground_truth: str) -> Dict[str, float]:
        """Calculate accuracy metrics (BLEU-like)"""
        response_words = set(response.lower().split())
        truth_words = set(ground_truth.lower().split())
        
        if not truth_words:
            return {
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0
            }
        
        overlap = len(response_words & truth_words)
        precision = overlap / len(response_words) if response_words else 0.0
        recall = overlap / len(truth_words) if truth_words else 0.0
        
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }
    
    @staticmethod
    def calculate_source_compliance(
        sources_consulted: List[str],
        expected_level: int = 1
    ) -> float:
        """Calculate source compliance score (0-1)"""
        if not sources_consulted:
            return 0.0
        
        level_1_files = [
            "BMC_Base_Conocimiento_GPT.json",
            "BMC_Base_Conocimiento_GPT-2.json"
        ]
        
        if expected_level == 1:
            has_level_1 = any(
                any(level_1 in source for level_1 in level_1_files)
                for source in sources_consulted
            )
            return 1.0 if has_level_1 else 0.0
        
        return 0.5  # Default for other levels
    
    @staticmethod
    def aggregate_metrics(metrics_list: List[Dict[str, float]]) -> Dict[str, float]:
        """Aggregate multiple metric scores"""
        if not metrics_list:
            return {}
        
        aggregated = {}
        for key in metrics_list[0].keys():
            values = [m.get(key, 0.0) for m in metrics_list if key in m]
            if values:
                aggregated[key] = sum(values) / len(values)
        
        return aggregated
    
    @staticmethod
    def calculate_overall_score(metrics: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate weighted overall score"""
        if not metrics:
            return 0.0
        
        default_weights = {
            "relevance": 0.3,
            "groundedness": 0.3,
            "coherence": 0.2,
            "f1": 0.2
        }
        
        weights = weights or default_weights
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric, value in metrics.items():
            weight = weights.get(metric, 0.0)
            weighted_sum += value * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
