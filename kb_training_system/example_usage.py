#!/usr/bin/env python3
"""
Example Usage of Knowledge Base Training System
===============================================

Demonstrates how to use the multi-level training system for KB evolution.
"""

from pathlib import Path
import json
from kb_training_system import (
    TrainingOrchestrator,
    KnowledgeBaseEvaluator,
    KnowledgeBaseLeakDetector,
    Level1StaticGrounding,
    Level2InteractionEvolution
)


def example_level1_training():
    """Example: Level 1 - Train from quotes"""
    print("=" * 70)
    print("Example 1: Level 1 - Static Grounding from Quotes")
    print("=" * 70)
    
    # Sample quotes data
    quotes = [
        {
            "product_code": "ISODEC_EPS_100",
            "product_name": "ISODEC EPS 100mm",
            "price": 46.07,
            "currency": "USD",
            "thickness": "100mm",
            "quantity": 10
        },
        {
            "product_code": "ISOROOF_3G_150",
            "product_name": "ISOROOF 3G 150mm",
            "price": 52.30,
            "currency": "USD",
            "thickness": "150mm",
            "quantity": 5
        }
    ]
    
    trainer = Level1StaticGrounding(
        knowledge_base_path="Files/",
        quotes_path="quotes/"
    )
    
    result = trainer.train_from_quotes(quotes)
    
    print(f"\n✅ Level 1 Training Complete!")
    print(f"Items Processed: {result.items_processed}")
    print(f"Items Added: {result.items_added}")
    print(f"Items Updated: {result.items_updated}")
    print(f"Items Failed: {result.items_failed}")
    
    if result.recommendations:
        print(f"\n📋 Recommendations:")
        for rec in result.recommendations:
            print(f"  - {rec}")


def example_level2_training():
    """Example: Level 2 - Train from interactions"""
    print("\n" + "=" * 70)
    print("Example 2: Level 2 - Interaction-Driven Evolution")
    print("=" * 70)
    
    # Sample interactions
    interactions = [
        {
            "query": "¿Cuál es el precio de ISODEC 100mm?",
            "response": "El precio de ISODEC 100mm es $46.07 según BMC_Base_Conocimiento_GPT.json",
            "sources": ["BMC_Base_Conocimiento_GPT.json"],
            "timestamp": "2026-01-20T10:00:00",
            "metadata": {"is_question": True}
        },
        {
            "query": "¿Qué espesor necesito para 6 metros de luz?",
            "response": "No tengo esa información en mi base de conocimiento",
            "sources": [],
            "timestamp": "2026-01-20T11:00:00",
            "metadata": {"is_question": True}
        }
    ]
    
    trainer = Level2InteractionEvolution(
        knowledge_base_path="Files/",
        interactions_path="training_data/interactions/"
    )
    
    result = trainer.train_from_interactions(interactions)
    
    print(f"\n✅ Level 2 Training Complete!")
    print(f"Items Processed: {result.items_processed}")
    print(f"Patterns Identified: {result.metrics.get('patterns_identified', 0)}")
    print(f"Gaps Identified: {result.metrics.get('gaps_identified', 0)}")
    
    if result.recommendations:
        print(f"\n📋 Recommendations:")
        for rec in result.recommendations:
            print(f"  - {rec}")


def example_evaluation():
    """Example: Evaluate interactions"""
    print("\n" + "=" * 70)
    print("Example 3: Evaluation of Interactions")
    print("=" * 70)
    
    evaluator = KnowledgeBaseEvaluator(knowledge_base_path="Files/")
    
    # Evaluate single interaction
    result = evaluator.evaluate_interaction(
        query="¿Cuál es el precio de ISODEC 100mm?",
        response="El precio de ISODEC 100mm es $46.07 según BMC_Base_Conocimiento_GPT.json",
        sources_consulted=["BMC_Base_Conocimiento_GPT.json"],
        ground_truth="El precio de ISODEC 100mm es $46.07 USD"
    )
    
    print(f"\n✅ Evaluation Complete!")
    print(f"Relevance Score: {result.relevance_score:.3f}")
    print(f"Groundedness Score: {result.groundedness_score:.3f}")
    print(f"Coherence Score: {result.coherence_score:.3f}")
    print(f"Accuracy Score: {result.accuracy_score:.3f}")
    
    if result.leaks_detected:
        print(f"\n⚠️  Leaks Detected: {len(result.leaks_detected)}")
        for leak in result.leaks_detected:
            print(f"  - {leak}")
    
    if result.recommendations:
        print(f"\n📋 Recommendations:")
        for rec in result.recommendations:
            print(f"  - {rec}")


def example_leak_detection():
    """Example: Detect knowledge leaks"""
    print("\n" + "=" * 70)
    print("Example 4: Leak Detection")
    print("=" * 70)
    
    detector = KnowledgeBaseLeakDetector(knowledge_base_path="Files/")
    
    # Detect leaks in interaction
    leaks = detector.detect_leaks_in_interaction(
        query="¿Cuál es el precio de ISODEC 100mm?",
        response="No tengo esa información en mi base de conocimiento",
        sources_consulted=[],
        ground_truth="El precio de ISODEC 100mm es $46.07 USD"
    )
    
    print(f"\n✅ Leak Detection Complete!")
    print(f"Leaks Detected: {len(leaks)}")
    
    for leak in leaks:
        print(f"\n🔍 Leak: {leak.leak_id}")
        print(f"  Type: {leak.leak_type}")
        print(f"  Severity: {leak.severity}")
        print(f"  Category: {leak.category}")
        print(f"  Missing: {leak.missing_information}")
        if leak.recommendations:
            print(f"  Recommendations:")
            for rec in leak.recommendations:
                print(f"    - {rec}")


def example_complete_pipeline():
    """Example: Complete training pipeline"""
    print("\n" + "=" * 70)
    print("Example 5: Complete Training Pipeline")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = TrainingOrchestrator(
        knowledge_base_path="Files/",
        quotes_path="quotes/",
        interactions_path="training_data/interactions/",
        social_data_path="training_data/social_media/"
    )
    
    # Sample data
    quotes = [
        {
            "product_code": "ISODEC_EPS_100",
            "product_name": "ISODEC EPS 100mm",
            "price": 46.07,
            "currency": "USD"
        }
    ]
    
    interactions = [
        {
            "query": "¿Cuál es el precio de ISODEC 100mm?",
            "response": "El precio es $46.07",
            "sources": ["BMC_Base_Conocimiento_GPT.json"]
        }
    ]
    
    # Run pipeline
    result = orchestrator.run_complete_pipeline(
        quotes=quotes,
        interactions=interactions,
        run_levels=[1, 2]  # Run only levels 1 and 2 for demo
    )
    
    print(f"\n✅ Pipeline Complete!")
    print(f"Levels Completed: {result.overall_metrics.get('levels_completed', 0)}")
    print(f"Total Items Added: {result.overall_metrics.get('total_items_added', 0)}")
    print(f"Total Items Updated: {result.overall_metrics.get('total_items_updated', 0)}")
    
    if result.evaluation_benchmark:
        print(f"\n📊 Evaluation Benchmark:")
        print(f"  Average Relevance: {result.evaluation_benchmark.average_relevance:.3f}")
        print(f"  Average Groundedness: {result.evaluation_benchmark.average_groundedness:.3f}")
        print(f"  Source Compliance: {result.evaluation_benchmark.source_compliance_rate:.1%}")
    
    if result.leak_analysis:
        print(f"\n🔍 Leak Analysis:")
        print(f"  Total Leaks: {result.leak_analysis.total_leaks}")
        print(f"  Critical Leaks: {len(result.leak_analysis.critical_leaks)}")
    
    # Export report
    orchestrator.export_pipeline_report(result, "kb_training_system/pipeline_report_example.md")
    print(f"\n📄 Report exported to: kb_training_system/pipeline_report_example.md")


def example_benchmarking():
    """Example: Benchmark KB architecture"""
    print("\n" + "=" * 70)
    print("Example 6: Benchmark KB Architecture")
    print("=" * 70)
    
    evaluator = KnowledgeBaseEvaluator(knowledge_base_path="Files/")
    
    # Sample evaluation dataset
    evaluation_dataset = [
        {
            "query": "¿Cuál es el precio de ISODEC 100mm?",
            "response": "El precio de ISODEC 100mm es $46.07 según BMC_Base_Conocimiento_GPT.json",
            "sources": ["BMC_Base_Conocimiento_GPT.json"],
            "ground_truth": "El precio de ISODEC 100mm es $46.07 USD"
        },
        {
            "query": "¿Qué espesor necesito para 6 metros?",
            "response": "Para 6 metros de luz necesitas mínimo 150mm",
            "sources": ["BMC_Base_Conocimiento_GPT.json"],
            "ground_truth": "Para 6 metros necesitas panel de 150mm (autoportancia 7.5m)"
        }
    ]
    
    benchmark = evaluator.benchmark_architecture(evaluation_dataset)
    
    print(f"\n✅ Benchmark Complete!")
    print(f"Total Evaluations: {benchmark.total_evaluations}")
    print(f"Average Relevance: {benchmark.average_relevance:.3f}")
    print(f"Average Groundedness: {benchmark.average_groundedness:.3f}")
    print(f"Average Coherence: {benchmark.average_coherence:.3f}")
    print(f"Source Compliance Rate: {benchmark.source_compliance_rate:.1%}")
    print(f"Leak Rate: {benchmark.leak_rate:.2f} leaks/query")
    print(f"KB Coverage Score: {benchmark.kb_coverage_score:.1%}")
    print(f"Instruction Effectiveness: {benchmark.instruction_effectiveness:.3f}")
    
    # Export report
    evaluator.export_evaluation_report("kb_training_system/benchmark_report_example.md", benchmark)
    print(f"\n📄 Report exported to: kb_training_system/benchmark_report_example.md")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Knowledge Base Training System - Examples")
    print("=" * 70)
    
    # Run examples
    try:
        example_level1_training()
        example_level2_training()
        example_evaluation()
        example_leak_detection()
        example_complete_pipeline()
        example_benchmarking()
        
        print("\n" + "=" * 70)
        print("✅ All examples completed!")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
