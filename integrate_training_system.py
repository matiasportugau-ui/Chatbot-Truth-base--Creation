#!/usr/bin/env python3
"""
Integration Script for KB Training System
==========================================

Integrates the KB training system with existing quote and interaction systems.
"""

from pathlib import Path
import json
from loguru import logger
from kb_training_system import TrainingOrchestrator

# Import existing systems
try:
    from comparar_cotizaciones_vendedoras import comparar_cotizaciones
    HAS_QUOTE_SYSTEM = True
except ImportError:
    HAS_QUOTE_SYSTEM = False
    logger.warning("Quote comparison system not found")

try:
    from gpt_simulation_agent.agent_system.agent_training_processor import TrainingProcessor
    HAS_TRAINING_PROCESSOR = True
except ImportError:
    HAS_TRAINING_PROCESSOR = False
    logger.warning("Training processor not found")


def load_quotes_from_system():
    """Load quotes from existing comparison system"""
    if not HAS_QUOTE_SYSTEM:
        logger.info("Quote system not available, skipping...")
        return []
    
    try:
        # Try to load from comparison results
        comparison_file = Path("comparacion_vendedoras_sistema.json")
        if comparison_file.exists():
            with open(comparison_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract quotes from comparison results
            quotes = []
            for presupuesto in data.get('presupuestos', []):
                if isinstance(presupuesto, dict) and 'error' not in presupuesto:
                    quote = {
                        "product_code": presupuesto.get('producto', ''),
                        "product_name": presupuesto.get('producto', ''),
                        "price": presupuesto.get('precio_unitario', 0),
                        "currency": "USD",
                        "thickness": presupuesto.get('espesor', ''),
                        "quantity": presupuesto.get('cantidad', 0)
                    }
                    quotes.append(quote)
            
            logger.info(f"Loaded {len(quotes)} quotes from comparison system")
            return quotes
    except Exception as e:
        logger.error(f"Error loading quotes: {e}")
    
    return []


def load_interactions_from_training_data():
    """Load interactions from training data directory"""
    interactions = []
    
    # Check training data directory
    training_dir = Path("training_data")
    if not training_dir.exists():
        logger.info("Training data directory not found")
        return interactions
    
    # Load from interactions subdirectory
    interactions_dir = training_dir / "interactions"
    if interactions_dir.exists():
        for json_file in interactions_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        interactions.extend(data)
                    else:
                        interactions.append(data)
            except Exception as e:
                logger.warning(f"Error loading {json_file}: {e}")
    
    # Also check social media data
    social_dir = training_dir / "social_media"
    if social_dir.exists():
        for platform_dir in social_dir.iterdir():
            if platform_dir.is_dir():
                for json_file in platform_dir.rglob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                interactions.extend(data)
                            else:
                                interactions.append(data)
                    except Exception as e:
                        logger.warning(f"Error loading {json_file}: {e}")
    
    logger.info(f"Loaded {len(interactions)} interactions from training data")
    return interactions


def run_integrated_training():
    """Run integrated training pipeline"""
    print("=" * 70)
    print("🚀 KB Training System - Integrated Pipeline")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = TrainingOrchestrator(
        knowledge_base_path="Files/",
        quotes_path="quotes/",
        interactions_path="training_data/interactions/",
        social_data_path="training_data/social_media/"
    )
    
    # Load data from existing systems
    print("\n📊 Loading data from existing systems...")
    
    quotes = load_quotes_from_system()
    print(f"   ✅ Loaded {len(quotes)} quotes")
    
    interactions = load_interactions_from_training_data()
    print(f"   ✅ Loaded {len(interactions)} interactions")
    
    # Separate social interactions if available
    social_interactions = []
    regular_interactions = []
    
    for interaction in interactions:
        if interaction.get("platform") in ["facebook", "instagram"]:
            social_interactions.append(interaction)
        else:
            regular_interactions.append(interaction)
    
    print(f"   ✅ {len(social_interactions)} social interactions")
    print(f"   ✅ {len(regular_interactions)} regular interactions")
    
    # Determine which levels to run
    run_levels = []
    
    if quotes:
        run_levels.append(1)
        print("\n✅ Level 1: Will train from quotes")
    
    if regular_interactions:
        run_levels.append(2)
        print("✅ Level 2: Will train from interactions")
    
    if social_interactions:
        run_levels.append(3)
        print("✅ Level 3: Will train from social media")
    
    # Always run Level 4 if we have any evaluation data
    if interactions:
        run_levels.append(4)
        print("✅ Level 4: Will run autonomous feedback")
    
    if not run_levels:
        print("\n⚠️  No data found. Please ensure:")
        print("   - Quote comparison system has run")
        print("   - Training data directory exists")
        print("   - Social media data is available")
        return
    
    # Run pipeline
    print(f"\n🔄 Running training pipeline (Levels: {run_levels})...")
    
    result = orchestrator.run_complete_pipeline(
        quotes=quotes if 1 in run_levels else None,
        interactions=regular_interactions if 2 in run_levels else None,
        social_interactions=social_interactions if 3 in run_levels else None,
        run_levels=run_levels
    )
    
    # Display results
    print("\n" + "=" * 70)
    print("📊 Training Results")
    print("=" * 70)
    
    print(f"\n✅ Levels Completed: {result.overall_metrics.get('levels_completed', 0)}/4")
    print(f"📈 Total Items Added: {result.overall_metrics.get('total_items_added', 0)}")
    print(f"📝 Total Items Updated: {result.overall_metrics.get('total_items_updated', 0)}")
    print(f"📊 Training Success Rate: {result.overall_metrics.get('training_success_rate', 0):.1%}")
    
    if result.evaluation_benchmark:
        print(f"\n📊 Evaluation Benchmark:")
        print(f"   Relevance: {result.evaluation_benchmark.average_relevance:.3f}")
        print(f"   Groundedness: {result.evaluation_benchmark.average_groundedness:.3f}")
        print(f"   Source Compliance: {result.evaluation_benchmark.source_compliance_rate:.1%}")
    
    if result.leak_analysis:
        print(f"\n🔍 Leak Analysis:")
        print(f"   Total Leaks: {result.leak_analysis.total_leaks}")
        print(f"   Critical Leaks: {len(result.leak_analysis.critical_leaks)}")
    
    # Export report
    report_path = "kb_training_system/integrated_training_report.md"
    orchestrator.export_pipeline_report(result, report_path)
    print(f"\n📄 Report exported to: {report_path}")
    
    # Show recommendations
    if result.recommendations:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(result.recommendations[:5], 1):  # Top 5
            print(f"   {i}. {rec}")
        if len(result.recommendations) > 5:
            print(f"   ... and {len(result.recommendations) - 5} more")
    
    print("\n" + "=" * 70)
    print("✅ Integration Complete!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        run_integrated_training()
    except Exception as e:
        logger.error(f"Error running integrated training: {e}")
        import traceback
        traceback.print_exc()
