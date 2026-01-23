#!/usr/bin/env python3
"""
Wrapper script to run KB evaluator comprehensive diagnostic
"""
import sys
import os
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from kb_training_system.kb_evaluator import KnowledgeBaseEvaluator

def main():
    """Run KB evaluator comprehensive diagnostic"""
    print("=" * 70)
    print("KNOWLEDGE BASE EVALUATOR - COMPREHENSIVE DIAGNOSTIC")
    print("=" * 70)
    
    kb_path = str(project_root / "training_data")
    print(f"\nKB Path: {kb_path}\n")
    
    try:
        evaluator = KnowledgeBaseEvaluator(knowledge_base_path=str(project_root))
        
        print("Running comprehensive evaluation...")
        print("Note: This uses sample test data for demonstration.\n")
        
        # Sample evaluation dataset
        evaluation_dataset = [
            {
                "query": "¿Cuál es el precio del panel de 50mm?",
                "response": "Según la base de conocimiento BMC_Base_Costos.json, el precio del panel de 50mm es $XX por m².",
                "sources": ["BMC_Base_Costos.json"],
                "ground_truth": "El precio del panel de 50mm depende del tipo y espesor específico."
            },
            {
                "query": "¿Qué autoportancia tiene el panel de 100mm?",
                "response": "El panel de 100mm tiene una autoportancia de X metros según las especificaciones técnicas.",
                "sources": ["BMC_Base_Costos.json"],
                "ground_truth": "La autoportancia varía según el tipo de panel."
            },
            {
                "query": "¿Cómo se calcula el costo total de una cotización?",
                "response": "No tengo esa información disponible en la base de conocimiento actual.",
                "sources": [],
                "ground_truth": "Se calcula sumando materiales, mano de obra y gastos generales."
            },
        ]
        
        # Run benchmark
        benchmark = evaluator.benchmark_architecture(
            evaluation_dataset=evaluation_dataset,
            kb_structure={
                "total_files": 15,
                "levels": ["nivel_1_master", "nivel_2_derivado", "nivel_3_docs"]
            }
        )
        
        # Export report
        report_path = project_root / "diagnostico_kb_evaluation.md"
        report = evaluator.export_evaluation_report(
            output_path=str(report_path),
            benchmark=benchmark
        )
        
        print(f"\n✅ KB Evaluation completed!")
        print(f"Report saved to: {report_path}")
        
        # Save JSON results
        json_path = project_root / "diagnostico_kb_evaluation.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": benchmark.timestamp,
                "total_evaluations": benchmark.total_evaluations,
                "metrics": {
                    "average_relevance": benchmark.average_relevance,
                    "average_groundedness": benchmark.average_groundedness,
                    "average_coherence": benchmark.average_coherence,
                    "average_accuracy": benchmark.average_accuracy,
                    "source_compliance_rate": benchmark.source_compliance_rate,
                    "leak_rate": benchmark.leak_rate,
                    "kb_coverage_score": benchmark.kb_coverage_score,
                    "instruction_effectiveness": benchmark.instruction_effectiveness
                },
                "detailed_metrics": benchmark.detailed_metrics
            }, f, indent=2, ensure_ascii=False)
        
        print(f"JSON results saved to: {json_path}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("KB EVALUATION SUMMARY")
        print("=" * 70)
        
        print(f"\n📊 Total Evaluations: {benchmark.total_evaluations}")
        
        print("\n📈 Metrics:")
        metrics = [
            ("Relevance", benchmark.average_relevance),
            ("Groundedness", benchmark.average_groundedness),
            ("Coherence", benchmark.average_coherence),
            ("Accuracy", benchmark.average_accuracy),
        ]
        
        for name, score in metrics:
            bar = "█" * int(score * 20)
            print(f"  {name:15s}: {bar:20s} {score:.3f}")
        
        print("\n🎯 Source Compliance:")
        bar = "█" * int(benchmark.source_compliance_rate * 20)
        print(f"  Compliance Rate: {bar:20s} {benchmark.source_compliance_rate:.1%}")
        
        print("\n💧 Knowledge Leaks:")
        print(f"  Leak Rate: {benchmark.leak_rate:.2f} leaks per query")
        leak_types = benchmark.detailed_metrics.get("leak_types", {})
        for leak_type, count in leak_types.items():
            print(f"    - {leak_type}: {count}")
        
        print("\n📚 KB Coverage:")
        bar = "█" * int(benchmark.kb_coverage_score * 20)
        print(f"  Coverage Score: {bar:20s} {benchmark.kb_coverage_score:.1%}")
        
        print("\n🎓 Instruction Effectiveness:")
        bar = "█" * int(benchmark.instruction_effectiveness * 20)
        print(f"  Effectiveness:  {bar:20s} {benchmark.instruction_effectiveness:.3f}")
        
        print("\n📁 Source Usage:")
        source_usage = benchmark.detailed_metrics.get("source_usage", {})
        for source, count in sorted(source_usage.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {source}: {count} times")
        
        print("\n" + "=" * 70)
        print("\n💡 Tip: Review the detailed report in diagnostico_kb_evaluation.md")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during KB evaluation: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
