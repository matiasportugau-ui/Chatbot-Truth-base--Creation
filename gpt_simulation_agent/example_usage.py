#!/usr/bin/env python3
"""
Example usage of GPT Simulation Agent

This script demonstrates how to use the self-configuring GPT simulation agent.
"""

import sys
from pathlib import Path

# Add agent_system to path
sys.path.insert(0, str(Path(__file__).parent))

from agent_system.gpt_simulation_agent import GPTSimulationAgent


def main():
    """Main example function"""
    # Get workspace path (parent directory)
    workspace_path = Path(__file__).parent.parent
    
    print("=" * 60)
    print("GPT Simulation Agent - Example Usage")
    print("=" * 60)
    print(f"\nWorkspace: {workspace_path}")
    
    # Initialize agent
    print("\n[1/4] Initializing agent...")
    agent = GPTSimulationAgent(workspace_path=str(workspace_path))
    print("✓ Agent initialized")
    
    # Self-configure
    print("\n[2/4] Running self-configuration...")
    try:
        config = agent.configure()
        print(f"✓ Configuration complete")
        print(f"  - Completion: {config.get('completion', 0):.1f}%")
        print(f"  - Files scanned: {len(config.get('diagnosis', {}).get('scanned_files', []))}")
    except Exception as e:
        print(f"⚠ Configuration error: {e}")
    
    # Social media ingestion (optional - requires API credentials)
    print("\n[3/4] Social media ingestion (optional)...")
    print("  Note: Requires Facebook/Instagram API credentials in .env")
    try:
        # Uncomment to enable:
        # social_data = agent.ingest_social_media(
        #     platforms=['facebook', 'instagram'],
        #     days_back=30,
        #     limit=100
        # )
        # print(f"✓ Ingested {social_data.get('facebook', {}).get('count', 0)} Facebook interactions")
        # print(f"✓ Ingested {social_data.get('instagram', {}).get('count', 0)} Instagram interactions")
        print("  (Skipped - uncomment in script to enable)")
    except Exception as e:
        print(f"⚠ Ingestion error: {e}")
    
    # Process training data
    print("\n[4/4] Processing training data...")
    try:
        training_results = agent.process_training_data()
        print(f"✓ Processing complete")
        print(f"  - Total interactions: {training_results.get('total_interactions', 0)}")
        print(f"  - Sources: {training_results.get('sources', {})}")
    except Exception as e:
        print(f"⚠ Processing error: {e}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    print("\nCheck the 'output' directory for generated files:")
    print("  - diagnosis.json")
    print("  - extracted_configs/extracted_config.json")
    print("  - gap_analysis_report.json")
    print("  - analytics_reports/analytics_report.md")


if __name__ == "__main__":
    main()
