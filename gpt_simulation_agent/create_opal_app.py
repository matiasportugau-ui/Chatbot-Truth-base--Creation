#!/usr/bin/env python3
"""
Create Opal App Format for Google Labs

Converts GPT Simulation Agent configuration to the exact Opal app format
that Google Labs uses for importing apps.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_codex_gems() -> Dict:
    """Load Codex generated Gems"""
    gems_file = Path(__file__).parent.parent / "codex_generated_gems.json"
    if gems_file.exists():
        with open(gems_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def create_main_workflow_nodes() -> tuple[List[Dict], List[Dict]]:
    """Create main GPT Simulation Agent workflow nodes and edges"""
    nodes = [
        {
            "id": "node_1",
            "type": "input",
            "label": "Receive Workspace Path",
            "config": {
                "fields": ["workspace_path", "output_dir"],
                "input_type": "text",
                "required": ["workspace_path"],
                "description": "Receives workspace path or configuration files as input"
            },
            "position": {"x": 100, "y": 100}
        },
        {
            "id": "node_2",
            "type": "process",
            "label": "Self-Diagnosis",
            "config": {
                "engine": "SelfDiagnosisEngine",
                "action": "diagnose",
                "output": "diagnosis.json",
                "description": "Automatically scans workspace and identifies configuration needs"
            },
            "position": {"x": 300, "y": 100}
        },
        {
            "id": "node_3",
            "type": "process",
            "label": "Intelligent Extraction",
            "config": {
                "engine": "ExtractionEngine",
                "action": "extract_all",
                "output": "extracted_configs/extracted_config.json",
                "description": "Extracts configuration from JSON, Markdown, YAML files"
            },
            "position": {"x": 500, "y": 100}
        },
        {
            "id": "node_4",
            "type": "analyze",
            "label": "Gap Analysis",
            "config": {
                "engine": "GapAnalysisEngine",
                "action": "analyze",
                "output": "gap_analysis_report.json",
                "description": "Identifies missing information and generates extraction guides"
            },
            "position": {"x": 700, "y": 100}
        },
        {
            "id": "node_5",
            "type": "process",
            "label": "Generate Gems",
            "config": {
                "engine": "GemGeneratorEngine",
                "action": "generate_multiple_gems",
                "output": "generated_gems/",
                "description": "Automatically generates Google Labs Gems from extracted configuration"
            },
            "position": {"x": 900, "y": 100}
        },
        {
            "id": "node_6",
            "type": "output",
            "label": "Present Results",
            "config": {
                "format": "structured",
                "include": ["gems", "descriptions", "validation_status", "instructions"],
                "description": "Presents all generated Gems with descriptions ready for Google Labs"
            },
            "position": {"x": 1100, "y": 100}
        }
    ]
    
    edges = [
        {"from": "node_1", "to": "node_2"},
        {"from": "node_2", "to": "node_3"},
        {"from": "node_3", "to": "node_4"},
        {"from": "node_4", "to": "node_5"},
        {"from": "node_5", "to": "node_6"}
    ]
    
    return nodes, edges


def create_gem_workflow_nodes(gem_name: str, gem_type: str, description: str) -> tuple[List[Dict], List[Dict]]:
    """Create nodes and edges for a Gem workflow"""
    
    # Base structure for all Gems
    nodes = [
        {
            "id": f"{gem_type}_input",
            "type": "input",
            "label": f"Receive Input - {gem_name}",
            "config": {
                "fields": ["input"],
                "description": f"Receives input for {gem_name}"
            },
            "position": {"x": 100, "y": 100}
        },
        {
            "id": f"{gem_type}_process",
            "type": "process",
            "label": f"Process - {gem_name}",
            "config": {
                "workflow_type": gem_type,
                "description": description
            },
            "position": {"x": 300, "y": 100}
        },
        {
            "id": f"{gem_type}_output",
            "type": "output",
            "label": f"Present Result - {gem_name}",
            "config": {
                "format": "structured",
                "description": f"Presents result for {gem_name}"
            },
            "position": {"x": 500, "y": 100}
        }
    ]
    
    edges = [
        {"from": f"{gem_type}_input", "to": f"{gem_type}_process"},
        {"from": f"{gem_type}_process", "to": f"{gem_type}_output"}
    ]
    
    return nodes, edges


def create_opal_app() -> Dict:
    """Create complete Opal app in Google Labs format"""
    
    # Load Codex Gems for descriptions
    codex_data = load_codex_gems()
    
    # Create main workflow
    main_nodes, main_edges = create_main_workflow_nodes()
    
    # Start with main workflow nodes
    all_nodes = main_nodes.copy()
    all_edges = main_edges.copy()
    
    # Add Gem workflows as sub-workflows
    gem_workflows = [
        {
            "name": "Main Assistant Gem",
            "type": "intelligence_based",
            "description": "Intelligent assistant specialized in technical-commercial construction materials with multi-step reasoning and hierarchical knowledge base access"
        },
        {
            "name": "Quotation System Gem",
            "type": "functionality_based",
            "description": "5-phase quotation system with product identification, technical validation (autoportancia), knowledge base retrieval, formula-based calculations, and detailed cost breakdown"
        },
        {
            "name": "Training & Analytics Gem",
            "type": "training_based",
            "description": "Processes training data from multiple sources (Facebook, Instagram), normalizes interactions, identifies patterns, analyzes engagement metrics, and generates analytics reports"
        },
        {
            "name": "Architecture Analysis Gem",
            "type": "architecture_based",
            "description": "Analyzes AI system architectures, identifies components, maps workflows, analyzes integrations, and generates technical documentation"
        },
        {
            "name": "Capacity Assessment Gem",
            "type": "capacity_based",
            "description": "Evaluates AI system capabilities, analyzes current vs potential capacity, identifies bottlenecks, suggests optimizations, and generates capacity reports"
        }
    ]
    
    # Add Gem workflow nodes
    y_offset = 300
    for gem in gem_workflows:
        gem_nodes, gem_edges = create_gem_workflow_nodes(
            gem["name"],
            gem["type"],
            gem["description"]
        )
        
        # Adjust positions
        for node in gem_nodes:
            node["position"]["y"] = y_offset
        
        all_nodes.extend(gem_nodes)
        all_edges.extend(gem_edges)
        y_offset += 200
    
    # Create Opal app structure
    opal_app = {
        "title": "GPT Simulation Agent - Complete System",
        "description": "Complete GPT Simulation Agent orchestrator with self-configuration, extraction, gap analysis, social media ingestion, training data processing, and automatic Gem generation. Includes 5 specialized Gems: Main Assistant, Quotation System, Training & Analytics, Architecture Analysis, and Capacity Assessment.",
        "version": "1.0.0",
        "nodes": all_nodes,
        "edges": all_edges,
        "url": "",
        "metadata": {
            "source": "codex_analysis",
            "agent_type": "GPT Simulation Agent",
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "functions": [
                "configure",
                "ingest_social_media",
                "process_training_data",
                "generate_gems",
                "generate_gem_from_training"
            ],
            "workflows": [
                "gpt_simulation_main",
                "main_assistant_gem",
                "quotation_system_gem",
                "training_analytics_gem",
                "architecture_analysis_gem",
                "capacity_assessment_gem"
            ],
            "system_instructions": "You are a GPT Simulation Agent orchestrator that manages self-configuration, extraction, gap analysis, social media ingestion, training data processing, and Gem generation. You coordinate multiple specialized engines to analyze GPT configurations and generate Google Labs Gems automatically."
        }
    }
    
    return opal_app


def main():
    """Generate Opal app file"""
    print("=" * 70)
    print("Creating Opal App for Google Labs")
    print("=" * 70)
    
    opal_app = create_opal_app()
    
    # Save JSON
    output_file = Path(__file__).parent / "opal_app_gpt_simulation_agent.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(opal_app, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ Opal app created: {output_file}")
    print(f"📊 Total nodes: {len(opal_app['nodes'])}")
    print(f"🔗 Total edges: {len(opal_app['edges'])}")
    print(f"📋 Workflows: {len(opal_app['metadata']['workflows'])}")
    
    print("\n💡 Next steps:")
    print("  1. Open Google Labs (gemini.google.com)")
    print("  2. Go to Gems → New Gem")
    print("  3. Look for 'Import' or 'Load from file'")
    print("  4. Upload opal_app_gpt_simulation_agent.json")
    print("  5. The app will be automatically configured!")


if __name__ == "__main__":
    main()
