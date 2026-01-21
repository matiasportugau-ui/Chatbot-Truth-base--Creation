"""
Knowledge Base Evaluator
========================

Evaluates chatbot interactions with knowledge base using industry-standard metrics:
- Relevance (how well answer matches query)
- Groundedness (how much answer relies on KB data)
- Coherence (logical consistency)
- Accuracy (BLEU, Precision, Recall, F1)
- Source of Truth compliance
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
from collections import Counter
import re
from loguru import logger

from panelin_improvements.source_of_truth_validator import SourceOfTruthValidator


@dataclass
class EvaluationResult:
    """Result of KB evaluation"""
    query: str
    response: str
    sources_consulted: List[str]
    timestamp: str
    metrics: Dict[str, float] = field(default_factory=dict)
    relevance_score: float = 0.0
    groundedness_score: float = 0.0
    coherence_score: float = 0.0
    accuracy_score: float = 0.0
    source_validation: Optional[Dict] = None
    leaks_detected: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class BenchmarkResult:
    """Benchmark result for KB architecture"""
    timestamp: str
    total_evaluations: int
    average_relevance: float
    average_groundedness: float
    average_coherence: float
    average_accuracy: float
    source_compliance_rate: float
    leak_rate: float
    kb_coverage_score: float
    instruction_effectiveness: float
    detailed_metrics: Dict[str, Any] = field(default_factory=dict)


class KnowledgeBaseEvaluator:
    """
    Evaluates chatbot knowledge base interactions using industry standards.
    
    Based on:
    - Azure AI Evaluation SDK patterns
    - RAG evaluation frameworks
    - GPT-assisted metrics
    """
    
    def __init__(
        self,
        knowledge_base_path: Optional[str] = None,
        ground_truth_path: Optional[str] = None
    ):
        """
        Initialize evaluator
        
        Args:
            knowledge_base_path: Path to knowledge base directory
            ground_truth_path: Path to ground truth dataset (optional)
        """
        self.kb_path = Path(knowledge_base_path) if knowledge_base_path else None
        self.ground_truth_path = Path(ground_truth_path) if ground_truth_path else None
        self.source_validator = SourceOfTruthValidator(knowledge_base_path)
        self.evaluation_history: List[EvaluationResult] = []
        
    def evaluate_interaction(
        self,
        query: str,
        response: str,
        sources_consulted: List[str],
        ground_truth: Optional[str] = None,
        expected_sources: Optional[List[str]] = None
    ) -> EvaluationResult:
        """
        Evaluate a single interaction
        
        Args:
            query: User query
            response: Chatbot response
            sources_consulted: KB sources used
            ground_truth: Expected answer (optional)
            expected_sources: Expected sources (optional)
            
        Returns:
            EvaluationResult with metrics
        """
        result = EvaluationResult(
            query=query,
            response=response,
            sources_consulted=sources_consulted,
            timestamp=datetime.now().isoformat()
        )
        
        # 1. Relevance Score (0-1): How well answer matches query
        result.relevance_score = self._calculate_relevance(query, response)
        
        # 2. Groundedness Score (0-1): How much answer relies on KB
        result.groundedness_score = self._calculate_groundedness(
            response, sources_consulted
        )
        
        # 3. Coherence Score (0-1): Logical consistency
        result.coherence_score = self._calculate_coherence(response)
        
        # 4. Accuracy Score (0-1): If ground truth available
        if ground_truth:
            result.accuracy_score = self._calculate_accuracy(response, ground_truth)
        
        # 5. Source of Truth Validation
        response_data = {"content": response, "sources": sources_consulted}
        validation = self.source_validator.validate_response(
            response_data, sources_consulted
        )
        result.source_validation = {
            "valid": validation.valid,
            "source_level": validation.source_level,
            "warnings": validation.warnings,
            "errors": validation.errors
        }
        
        # 6. Detect leaks (missing information)
        result.leaks_detected = self._detect_leaks(query, response, sources_consulted)
        
        # 7. Generate recommendations
        result.recommendations = self._generate_recommendations(result)
        
        # Compile metrics
        result.metrics = {
            "relevance": result.relevance_score,
            "groundedness": result.groundedness_score,
            "coherence": result.coherence_score,
            "accuracy": result.accuracy_score,
            "source_compliance": 1.0 if validation.valid else 0.0,
            "leak_count": len(result.leaks_detected)
        }
        
        self.evaluation_history.append(result)
        return result
    
    def _calculate_relevance(self, query: str, response: str) -> float:
        """
        Calculate relevance: how well answer matches query intent
        
        Uses keyword overlap and semantic similarity heuristics
        """
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Extract key terms from query
        query_terms = set(re.findall(r'\b\w{4,}\b', query_lower))
        
        # Check if response addresses query terms
        matches = sum(1 for term in query_terms if term in response_lower)
        
        if not query_terms:
            return 0.5  # Neutral if no clear terms
        
        relevance = matches / len(query_terms)
        
        # Boost if response contains question keywords
        question_indicators = ["precio", "costo", "espesor", "autoportancia", 
                               "cotización", "producto", "características"]
        if any(indicator in query_lower for indicator in question_indicators):
            if any(indicator in response_lower for indicator in question_indicators):
                relevance = min(1.0, relevance + 0.2)
        
        return min(1.0, relevance)
    
    def _calculate_groundedness(self, response: str, sources: List[str]) -> float:
        """
        Calculate groundedness: how much answer relies on KB data
        
        Higher score = more grounded in KB, less hallucination
        """
        if not sources:
            return 0.0  # No sources = not grounded
        
        # Check for specific data indicators
        data_indicators = [
            "según", "en la base", "según el archivo", "de acuerdo a",
            "precio", "costo", "espesor", "autoportancia", "fórmula",
            "BMC_Base", "json", "archivo"
        ]
        
        response_lower = response.lower()
        indicators_found = sum(1 for indicator in data_indicators 
                              if indicator in response_lower)
        
        # Base score from having sources
        base_score = 0.5 if sources else 0.0
        
        # Boost for data indicators
        indicator_score = min(0.5, indicators_found * 0.1)
        
        # Penalize vague responses
        vague_phrases = ["no estoy seguro", "creo que", "probablemente", 
                        "no tengo información"]
        vague_penalty = sum(0.1 for phrase in vague_phrases 
                           if phrase in response_lower)
        
        groundedness = base_score + indicator_score - vague_penalty
        return max(0.0, min(1.0, groundedness))
    
    def _calculate_coherence(self, response: str) -> float:
        """
        Calculate coherence: logical consistency of response
        """
        # Check for contradictions
        contradictions = [
            ("precio", "gratis"),
            ("incluye", "no incluye"),
            ("siempre", "nunca"),
        ]
        
        response_lower = response.lower()
        contradiction_count = sum(
            1 for (term1, term2) in contradictions
            if term1 in response_lower and term2 in response_lower
        )
        
        if contradiction_count > 0:
            return 0.3  # Low coherence if contradictions
        
        # Check structure
        has_structure = any(marker in response for marker in [":", "-", "•", "1.", "2."])
        structure_score = 0.3 if has_structure else 0.0
        
        # Check completeness (not too short, not too long)
        word_count = len(response.split())
        length_score = 0.4 if 20 <= word_count <= 500 else 0.2
        
        return min(1.0, structure_score + length_score + 0.3)
    
    def _calculate_accuracy(self, response: str, ground_truth: str) -> float:
        """
        Calculate accuracy using BLEU-like metrics
        """
        # Simple word overlap
        response_words = set(response.lower().split())
        truth_words = set(ground_truth.lower().split())
        
        if not truth_words:
            return 0.0
        
        overlap = len(response_words & truth_words)
        precision = overlap / len(response_words) if response_words else 0.0
        recall = overlap / len(truth_words) if truth_words else 0.0
        
        if precision + recall == 0:
            return 0.0
        
        f1 = 2 * (precision * recall) / (precision + recall)
        return f1
    
    def _detect_leaks(
        self, 
        query: str, 
        response: str, 
        sources: List[str]
    ) -> List[str]:
        """
        Detect knowledge leaks: information gaps in KB
        """
        leaks = []
        
        # Check for "I don't know" patterns
        unknown_patterns = [
            "no tengo", "no sé", "no está disponible", "no encuentro",
            "no tengo esa información", "no disponible en base"
        ]
        
        response_lower = response.lower()
        if any(pattern in response_lower for pattern in unknown_patterns):
            leaks.append(f"Missing information for query: {query[:100]}")
        
        # Check if query asks for specific data but response is vague
        specific_indicators = ["precio de", "costo de", "espesor", "autoportancia"]
        if any(indicator in query.lower() for indicator in specific_indicators):
            if not any(indicator in response_lower for indicator in specific_indicators):
                leaks.append(f"Specific data requested but not provided: {query[:100]}")
        
        # Check source coverage
        if not sources:
            leaks.append("No sources consulted for query")
        
        return leaks
    
    def _generate_recommendations(self, result: EvaluationResult) -> List[str]:
        """Generate recommendations based on evaluation"""
        recommendations = []
        
        if result.relevance_score < 0.6:
            recommendations.append(
                "Improve query-response matching. Consider expanding KB with "
                "synonyms and alternative phrasings."
            )
        
        if result.groundedness_score < 0.5:
            recommendations.append(
                "Response not well-grounded in KB. Ensure responses cite specific "
                "sources and data from knowledge base."
            )
        
        if result.coherence_score < 0.6:
            recommendations.append(
                "Response coherence could be improved. Check for contradictions "
                "and ensure logical flow."
            )
        
        if result.source_validation and not result.source_validation["valid"]:
            recommendations.append(
                "Use Level 1 (Master) source for prices and formulas. "
                "Current sources may not be authoritative."
            )
        
        if result.leaks_detected:
            recommendations.append(
                f"Knowledge leak detected: {len(result.leaks_detected)} gaps found. "
                "Consider adding missing information to KB."
            )
        
        return recommendations
    
    def benchmark_architecture(
        self,
        evaluation_dataset: List[Dict[str, Any]],
        kb_structure: Optional[Dict] = None
    ) -> BenchmarkResult:
        """
        Benchmark entire KB architecture
        
        Args:
            evaluation_dataset: List of {query, response, sources, ground_truth}
            kb_structure: KB structure metadata
            
        Returns:
            BenchmarkResult with comprehensive metrics
        """
        logger.info(f"Benchmarking KB architecture with {len(evaluation_dataset)} samples")
        
        results = []
        for sample in evaluation_dataset:
            result = self.evaluate_interaction(
                query=sample.get("query", ""),
                response=sample.get("response", ""),
                sources_consulted=sample.get("sources", []),
                ground_truth=sample.get("ground_truth"),
                expected_sources=sample.get("expected_sources")
            )
            results.append(result)
        
        # Calculate aggregate metrics
        avg_relevance = sum(r.relevance_score for r in results) / len(results)
        avg_groundedness = sum(r.groundedness_score for r in results) / len(results)
        avg_coherence = sum(r.coherence_score for r in results) / len(results)
        avg_accuracy = sum(r.accuracy_score for r in results) / len(results)
        
        # Source compliance
        compliant = sum(
            1 for r in results 
            if r.source_validation and r.source_validation["valid"]
        )
        compliance_rate = compliant / len(results) if results else 0.0
        
        # Leak rate
        total_leaks = sum(len(r.leaks_detected) for r in results)
        leak_rate = total_leaks / len(results) if results else 0.0
        
        # KB coverage (estimated)
        kb_coverage = self._estimate_kb_coverage(results, kb_structure)
        
        # Instruction effectiveness (based on source compliance and coherence)
        instruction_effectiveness = (compliance_rate + avg_coherence) / 2
        
        benchmark = BenchmarkResult(
            timestamp=datetime.now().isoformat(),
            total_evaluations=len(results),
            average_relevance=avg_relevance,
            average_groundedness=avg_groundedness,
            average_coherence=avg_coherence,
            average_accuracy=avg_accuracy,
            source_compliance_rate=compliance_rate,
            leak_rate=leak_rate,
            kb_coverage_score=kb_coverage,
            instruction_effectiveness=instruction_effectiveness,
            detailed_metrics={
                "relevance_distribution": self._calculate_distribution(
                    [r.relevance_score for r in results]
                ),
                "groundedness_distribution": self._calculate_distribution(
                    [r.groundedness_score for r in results]
                ),
                "leak_types": self._categorize_leaks(results),
                "source_usage": self._analyze_source_usage(results)
            }
        )
        
        return benchmark
    
    def _estimate_kb_coverage(
        self, 
        results: List[EvaluationResult],
        kb_structure: Optional[Dict]
    ) -> float:
        """Estimate KB coverage based on leaks and successful queries"""
        if not results:
            return 0.0
        
        successful = sum(
            1 for r in results 
            if not r.leaks_detected and r.relevance_score > 0.6
        )
        
        return successful / len(results)
    
    def _calculate_distribution(self, scores: List[float]) -> Dict[str, float]:
        """Calculate score distribution"""
        if not scores:
            return {}
        
        return {
            "min": min(scores),
            "max": max(scores),
            "mean": sum(scores) / len(scores),
            "median": sorted(scores)[len(scores) // 2]
        }
    
    def _categorize_leaks(self, results: List[EvaluationResult]) -> Dict[str, int]:
        """Categorize types of leaks detected"""
        categories = Counter()
        
        for result in results:
            for leak in result.leaks_detected:
                if "precio" in leak.lower() or "costo" in leak.lower():
                    categories["pricing"] += 1
                elif "espesor" in leak.lower() or "autoportancia" in leak.lower():
                    categories["specifications"] += 1
                elif "no sources" in leak.lower():
                    categories["source_missing"] += 1
                else:
                    categories["general"] += 1
        
        return dict(categories)
    
    def _analyze_source_usage(self, results: List[EvaluationResult]) -> Dict[str, int]:
        """Analyze which sources are used most"""
        source_counter = Counter()
        
        for result in results:
            for source in result.sources_consulted:
                source_counter[source] += 1
        
        return dict(source_counter)
    
    def export_evaluation_report(
        self,
        output_path: str,
        benchmark: Optional[BenchmarkResult] = None
    ) -> str:
        """Export evaluation report"""
        if benchmark is None and self.evaluation_history:
            # Create benchmark from history
            dataset = [
                {
                    "query": r.query,
                    "response": r.response,
                    "sources": r.sources_consulted
                }
                for r in self.evaluation_history
            ]
            benchmark = self.benchmark_architecture(dataset)
        
        if not benchmark:
            return "No evaluation data available"
        
        report = f"""
# Knowledge Base Evaluation Report
Generated: {benchmark.timestamp}

## Executive Summary
- Total Evaluations: {benchmark.total_evaluations}
- Overall Score: {(benchmark.average_relevance + benchmark.average_groundedness + benchmark.average_coherence) / 3:.2f}/1.0

## Metrics

### Relevance
- Average: {benchmark.average_relevance:.3f}
- Distribution: {benchmark.detailed_metrics.get('relevance_distribution', {})}

### Groundedness
- Average: {benchmark.average_groundedness:.3f}
- Distribution: {benchmark.detailed_metrics.get('groundedness_distribution', {})}

### Coherence
- Average: {benchmark.average_coherence:.3f}

### Accuracy
- Average: {benchmark.average_accuracy:.3f}

## Source of Truth Compliance
- Compliance Rate: {benchmark.source_compliance_rate:.1%}
- Source Usage: {benchmark.detailed_metrics.get('source_usage', {})}

## Knowledge Leaks
- Leak Rate: {benchmark.leak_rate:.2f} leaks per query
- Leak Types: {benchmark.detailed_metrics.get('leak_types', {})}

## KB Coverage
- Coverage Score: {benchmark.kb_coverage_score:.1%}

## Instruction Effectiveness
- Effectiveness Score: {benchmark.instruction_effectiveness:.3f}

## Recommendations
1. Improve source compliance to Level 1 (Master) sources
2. Address knowledge leaks in identified categories
3. Enhance query-response matching for better relevance
4. Strengthen KB grounding to reduce hallucination
"""
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report, encoding="utf-8")
        
        logger.info(f"Evaluation report exported to {output_path}")
        return report
