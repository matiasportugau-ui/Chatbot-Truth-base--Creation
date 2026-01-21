"""
Training Orchestrator
=====================

Orchestrates multi-level training system for knowledge base evolution.
Coordinates all four training levels and manages training pipeline.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
from loguru import logger

from .training_levels import (
    Level1StaticGrounding,
    Level2InteractionEvolution,
    Level3SocialIngestion,
    Level4AutonomousFeedback,
    TrainingResult
)
from .kb_evaluator import KnowledgeBaseEvaluator, BenchmarkResult
from .kb_leak_detector import KnowledgeBaseLeakDetector, LeakAnalysisReport


@dataclass
class TrainingPipelineResult:
    """Result of complete training pipeline"""
    timestamp: str
    pipeline_version: str = "1.0.0"
    level1_result: Optional[TrainingResult] = None
    level2_result: Optional[TrainingResult] = None
    level3_result: Optional[TrainingResult] = None
    level4_result: Optional[TrainingResult] = None
    evaluation_benchmark: Optional[BenchmarkResult] = None
    leak_analysis: Optional[LeakAnalysisReport] = None
    overall_metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class TrainingOrchestrator:
    """
    Orchestrates multi-level training system.
    
    Manages:
    - Training pipeline execution
    - Data flow between levels
    - Evaluation and benchmarking
    - Leak detection and resolution
    """
    
    def __init__(
        self,
        knowledge_base_path: str,
        quotes_path: Optional[str] = None,
        interactions_path: Optional[str] = None,
        social_data_path: Optional[str] = None,
        evaluation_dataset_path: Optional[str] = None
    ):
        """
        Initialize training orchestrator
        
        Args:
            knowledge_base_path: Path to knowledge base directory
            quotes_path: Path to quotes directory
            interactions_path: Path to interactions directory
            social_data_path: Path to social media data
            evaluation_dataset_path: Path to evaluation dataset
        """
        self.kb_path = Path(knowledge_base_path)
        
        # Initialize training levels
        self.level1 = Level1StaticGrounding(
            knowledge_base_path=knowledge_base_path,
            quotes_path=quotes_path
        )
        self.level2 = Level2InteractionEvolution(
            knowledge_base_path=knowledge_base_path,
            interactions_path=interactions_path
        )
        self.level3 = Level3SocialIngestion(
            knowledge_base_path=knowledge_base_path,
            social_data_path=social_data_path
        )
        self.level4 = Level4AutonomousFeedback(
            knowledge_base_path=knowledge_base_path
        )
        
        # Initialize evaluators
        self.evaluator = KnowledgeBaseEvaluator(knowledge_base_path=knowledge_base_path)
        self.leak_detector = KnowledgeBaseLeakDetector(knowledge_base_path=knowledge_base_path)
        
        self.evaluation_dataset_path = Path(evaluation_dataset_path) if evaluation_dataset_path else None
    
    def run_complete_pipeline(
        self,
        quotes: Optional[List[Dict]] = None,
        interactions: Optional[List[Dict]] = None,
        social_interactions: Optional[List[Dict]] = None,
        evaluation_dataset: Optional[List[Dict]] = None,
        run_levels: List[int] = [1, 2, 3, 4]
    ) -> TrainingPipelineResult:
        """
        Run complete training pipeline
        
        Args:
            quotes: List of quotes for Level 1
            interactions: List of interactions for Level 2
            social_interactions: List of social interactions for Level 3
            evaluation_dataset: Dataset for evaluation
            run_levels: Which levels to run (default: all)
            
        Returns:
            TrainingPipelineResult with all results
        """
        logger.info("Starting complete training pipeline")
        
        result = TrainingPipelineResult(
            timestamp=datetime.now().isoformat()
        )
        
        # Level 1: Static Grounding
        if 1 in run_levels and quotes:
            logger.info("Running Level 1: Static Grounding")
            try:
                result.level1_result = self.level1.train_from_quotes(quotes)
                logger.info(f"Level 1 complete: {result.level1_result.items_added} added, "
                          f"{result.level1_result.items_updated} updated")
            except Exception as e:
                logger.error(f"Level 1 error: {e}")
        
        # Level 2: Interaction Evolution
        if 2 in run_levels and interactions:
            logger.info("Running Level 2: Interaction-Driven Evolution")
            try:
                result.level2_result = self.level2.train_from_interactions(interactions)
                logger.info(f"Level 2 complete: {result.level2_result.items_added} added, "
                          f"{result.level2_result.items_updated} updated")
            except Exception as e:
                logger.error(f"Level 2 error: {e}")
        
        # Level 3: Social Ingestion
        if 3 in run_levels and social_interactions:
            logger.info("Running Level 3: Proactive Social & Synthetic Ingestion")
            try:
                result.level3_result = self.level3.train_from_social_media(social_interactions)
                logger.info(f"Level 3 complete: {result.level3_result.items_added} added, "
                          f"{result.level3_result.items_updated} updated")
            except Exception as e:
                logger.error(f"Level 3 error: {e}")
        
        # Level 4: Autonomous Feedback
        if 4 in run_levels:
            logger.info("Running Level 4: Autonomous Agent Feedback Loop")
            try:
                # Use evaluation results if available
                eval_results = self._prepare_evaluation_results(
                    evaluation_dataset, interactions
                )
                if eval_results:
                    result.level4_result = self.level4.train_from_evaluation(eval_results)
                    logger.info(f"Level 4 complete: {result.level4_result.items_added} added, "
                              f"{result.level4_result.items_updated} updated")
            except Exception as e:
                logger.error(f"Level 4 error: {e}")
        
        # Run evaluation benchmark
        if evaluation_dataset:
            logger.info("Running evaluation benchmark")
            try:
                result.evaluation_benchmark = self.evaluator.benchmark_architecture(
                    evaluation_dataset
                )
                logger.info(f"Benchmark complete: "
                          f"Relevance={result.evaluation_benchmark.average_relevance:.3f}, "
                          f"Groundedness={result.evaluation_benchmark.average_groundedness:.3f}")
            except Exception as e:
                logger.error(f"Evaluation error: {e}")
        
        # Run leak analysis
        if interactions:
            logger.info("Running leak analysis")
            try:
                result.leak_analysis = self.leak_detector.analyze_leak_patterns(interactions)
                logger.info(f"Leak analysis complete: {result.leak_analysis.total_leaks} leaks detected")
            except Exception as e:
                logger.error(f"Leak analysis error: {e}")
        
        # Calculate overall metrics
        result.overall_metrics = self._calculate_overall_metrics(result)
        
        # Generate recommendations
        result.recommendations = self._generate_overall_recommendations(result)
        
        logger.info("Training pipeline complete")
        return result
    
    def _prepare_evaluation_results(
        self,
        evaluation_dataset: Optional[List[Dict]],
        interactions: Optional[List[Dict]]
    ) -> List[Dict]:
        """Prepare evaluation results from dataset or interactions"""
        results = []
        
        if evaluation_dataset:
            # Convert evaluation dataset to evaluation results format
            for sample in evaluation_dataset:
                eval_result = self.evaluator.evaluate_interaction(
                    query=sample.get("query", ""),
                    response=sample.get("response", ""),
                    sources_consulted=sample.get("sources", []),
                    ground_truth=sample.get("ground_truth")
                )
                results.append({
                    "relevance_score": eval_result.relevance_score,
                    "groundedness_score": eval_result.groundedness_score,
                    "coherence_score": eval_result.coherence_score,
                    "accuracy_score": eval_result.accuracy_score,
                    "leaks_detected": len(eval_result.leaks_detected)
                })
        
        elif interactions:
            # Evaluate interactions
            for interaction in interactions[:50]:  # Limit for performance
                eval_result = self.evaluator.evaluate_interaction(
                    query=interaction.get("query", ""),
                    response=interaction.get("response", ""),
                    sources_consulted=interaction.get("sources", [])
                )
                results.append({
                    "relevance_score": eval_result.relevance_score,
                    "groundedness_score": eval_result.groundedness_score,
                    "coherence_score": eval_result.coherence_score,
                    "accuracy_score": eval_result.accuracy_score,
                    "leaks_detected": len(eval_result.leaks_detected)
                })
        
        return results
    
    def _calculate_overall_metrics(
        self,
        result: TrainingPipelineResult
    ) -> Dict[str, Any]:
        """Calculate overall training metrics"""
        metrics = {
            "total_items_added": 0,
            "total_items_updated": 0,
            "total_items_processed": 0,
            "levels_completed": 0,
            "training_success_rate": 0.0
        }
        
        # Aggregate from all levels
        for level_result in [
            result.level1_result,
            result.level2_result,
            result.level3_result,
            result.level4_result
        ]:
            if level_result:
                metrics["total_items_added"] += level_result.items_added
                metrics["total_items_updated"] += level_result.items_updated
                metrics["total_items_processed"] += level_result.items_processed
                metrics["levels_completed"] += 1
        
        # Calculate success rate
        if metrics["total_items_processed"] > 0:
            successful = metrics["total_items_added"] + metrics["total_items_updated"]
            metrics["training_success_rate"] = successful / metrics["total_items_processed"]
        
        # Add evaluation metrics
        if result.evaluation_benchmark:
            metrics["evaluation"] = {
                "average_relevance": result.evaluation_benchmark.average_relevance,
                "average_groundedness": result.evaluation_benchmark.average_groundedness,
                "average_coherence": result.evaluation_benchmark.average_coherence,
                "source_compliance_rate": result.evaluation_benchmark.source_compliance_rate,
                "leak_rate": result.evaluation_benchmark.leak_rate
            }
        
        # Add leak metrics
        if result.leak_analysis:
            metrics["leaks"] = {
                "total_leaks": result.leak_analysis.total_leaks,
                "critical_leaks": len(result.leak_analysis.critical_leaks),
                "coverage_gaps": len(result.leak_analysis.kb_coverage_gaps)
            }
        
        return metrics
    
    def _generate_overall_recommendations(
        self,
        result: TrainingPipelineResult
    ) -> List[str]:
        """Generate overall recommendations from pipeline results"""
        recommendations = []
        
        # Level-specific recommendations
        for level_result in [
            result.level1_result,
            result.level2_result,
            result.level3_result,
            result.level4_result
        ]:
            if level_result and level_result.recommendations:
                recommendations.extend(level_result.recommendations)
        
        # Evaluation recommendations
        if result.evaluation_benchmark:
            if result.evaluation_benchmark.average_relevance < 0.7:
                recommendations.append(
                    "Improve query-response relevance. Consider expanding KB with synonyms."
                )
            if result.evaluation_benchmark.average_groundedness < 0.6:
                recommendations.append(
                    "Strengthen KB grounding. Ensure responses cite specific sources."
                )
            if result.evaluation_benchmark.source_compliance_rate < 0.8:
                recommendations.append(
                    "Improve source compliance. Enforce Level 1 (Master) source usage."
                )
        
        # Leak recommendations
        if result.leak_analysis:
            if result.leak_analysis.total_leaks > 10:
                recommendations.append(
                    f"Address {result.leak_analysis.total_leaks} knowledge leaks. "
                    "Review critical leaks first."
                )
            if result.leak_analysis.critical_leaks:
                recommendations.append(
                    f"URGENT: Address {len(result.leak_analysis.critical_leaks)} critical leaks."
                )
        
        return recommendations
    
    def export_pipeline_report(
        self,
        result: TrainingPipelineResult,
        output_path: str
    ) -> str:
        """Export complete pipeline report"""
        report = f"""
# Knowledge Base Training Pipeline Report
Generated: {result.timestamp}
Pipeline Version: {result.pipeline_version}

## Executive Summary
- Levels Completed: {result.overall_metrics.get('levels_completed', 0)}/4
- Total Items Added: {result.overall_metrics.get('total_items_added', 0)}
- Total Items Updated: {result.overall_metrics.get('total_items_updated', 0)}
- Training Success Rate: {result.overall_metrics.get('training_success_rate', 0):.1%}

## Level Results

### Level 1: Static Grounding
"""
        if result.level1_result:
            report += f"""
- Items Processed: {result.level1_result.items_processed}
- Items Added: {result.level1_result.items_added}
- Items Updated: {result.level1_result.items_updated}
- Items Failed: {result.level1_result.items_failed}
"""
        else:
            report += "- Not executed\n"
        
        report += """
### Level 2: Interaction-Driven Evolution
"""
        if result.level2_result:
            report += f"""
- Items Processed: {result.level2_result.items_processed}
- Items Added: {result.level2_result.items_added}
- Items Updated: {result.level2_result.items_updated}
- Patterns Identified: {result.level2_result.metrics.get('patterns_identified', 0)}
- Gaps Identified: {result.level2_result.metrics.get('gaps_identified', 0)}
"""
        else:
            report += "- Not executed\n"
        
        report += """
### Level 3: Proactive Social & Synthetic Ingestion
"""
        if result.level3_result:
            report += f"""
- Items Processed: {result.level3_result.items_processed}
- Items Added: {result.level3_result.items_added}
- Trends Identified: {result.level3_result.metrics.get('trends_identified', 0)}
- Synthetic Cases Generated: {result.level3_result.metrics.get('synthetic_cases_generated', 0)}
"""
        else:
            report += "- Not executed\n"
        
        report += """
### Level 4: Autonomous Agent Feedback Loop
"""
        if result.level4_result:
            report += f"""
- Items Processed: {result.level4_result.items_processed}
- Items Added: {result.level4_result.items_added}
- Performance Metrics Analyzed: {result.level4_result.metrics.get('total_evaluations', 0)}
"""
        else:
            report += "- Not executed\n"
        
        # Evaluation Benchmark
        if result.evaluation_benchmark:
            report += f"""
## Evaluation Benchmark
- Average Relevance: {result.evaluation_benchmark.average_relevance:.3f}
- Average Groundedness: {result.evaluation_benchmark.average_groundedness:.3f}
- Average Coherence: {result.evaluation_benchmark.average_coherence:.3f}
- Source Compliance Rate: {result.evaluation_benchmark.source_compliance_rate:.1%}
- Leak Rate: {result.evaluation_benchmark.leak_rate:.2f} leaks/query
- KB Coverage Score: {result.evaluation_benchmark.kb_coverage_score:.1%}
"""
        
        # Leak Analysis
        if result.leak_analysis:
            report += f"""
## Leak Analysis
- Total Leaks: {result.leak_analysis.total_leaks}
- Critical Leaks: {len(result.leak_analysis.critical_leaks)}
- Coverage Gaps: {len(result.leak_analysis.kb_coverage_gaps)}
"""
        
        # Recommendations
        report += """
## Recommendations
"""
        for rec in result.recommendations:
            report += f"- {rec}\n"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report, encoding="utf-8")
        
        logger.info(f"Pipeline report exported to {output_path}")
        return report
