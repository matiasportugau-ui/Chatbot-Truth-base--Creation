#!/usr/bin/env python3
"""
Generate Opal Asset for GPT Simulation Agent

Creates a complete uploadable Opal document format asset that configures
GPT simulation agent functions and includes all workflow definitions.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from codex_generated_gems import codex_generated_gems
    CODEX_GEMS_AVAILABLE = True
except:
    CODEX_GEMS_AVAILABLE = False


def load_codex_gems() -> Dict:
    """Load Codex generated Gems"""
    gems_file = Path(__file__).parent.parent / "codex_generated_gems.json"
    if gems_file.exists():
        with open(gems_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def enhance_workflow_nodes(workflow: Dict) -> List[Dict]:
    """Enhance workflow nodes with proper input nodes and connections"""
    nodes = workflow.get("nodos", [])
    pasos = workflow.get("pasos", [])
    
    # Check if input node exists
    has_input = any(nodo.get("tipo") == "input" for nodo in nodes)
    
    enhanced_nodes = []
    
    # Add input node if missing
    if not has_input:
        # Determine input fields from description
        desc = workflow.get("descripcion", "")
        input_fields = []
        
        if "consulta" in desc.lower() or "query" in desc.lower():
            input_fields.append("query")
        if "especificaciones" in desc.lower() or "specifications" in desc.lower():
            input_fields.extend(["product_type", "dimensions", "specifications"])
        if "tema" in desc.lower() or "topic" in desc.lower():
            input_fields.append("topic")
        if "datos" in desc.lower() or "data" in desc.lower():
            input_fields.append("data")
        
        if not input_fields:
            input_fields = ["input"]
        
        input_node = {
            "id": "node_input",
            "type": "input",
            "name": f"Receive {', '.join(input_fields)}",
            "description": f"Receives as input: {', '.join(input_fields)}",
            "configuration": {
                "fields": input_fields,
                "input_type": "text" if len(input_fields) == 1 else "structured"
            },
            "connections": []
        }
        
        # Connect to first existing node
        if nodes:
            input_node["connections"].append({
                "target": nodes[0]["id"],
                "type": "sequential"
            })
        
        enhanced_nodes.append(input_node)
    
    # Enhance existing nodes
    for i, nodo in enumerate(nodes):
        enhanced_node = {
            "id": nodo.get("id", f"node_{i+1}"),
            "type": nodo.get("tipo", "process"),
            "name": nodo.get("nombre", f"Node {i+1}"),
            "description": nodo.get("descripcion", ""),
            "configuration": nodo.get("configuracion", {})
        }
        
        # Add connections
        connections = nodo.get("conexiones", [])
        if connections:
            enhanced_node["connections"] = [
                {
                    "target": conn.get("target", ""),
                    "type": conn.get("tipo", "sequential")
                }
                for conn in connections
            ]
        elif i < len(nodes) - 1:
            # Add sequential connection if missing
            next_node = nodes[i + 1]
            enhanced_node["connections"] = [{
                "target": next_node.get("id", f"node_{i+2}"),
                "type": "sequential"
            }]
        else:
            enhanced_node["connections"] = []
        
        enhanced_nodes.append(enhanced_node)
    
    return enhanced_nodes


def create_opal_asset() -> Dict:
    """Create complete Opal asset"""
    
    # Load existing Gems
    codex_data = load_codex_gems()
    
    # Base asset structure
    asset = {
        "opal_version": "1.0",
        "asset_type": "gpt_simulation_agent_configuration",
        "metadata": {
            "created": datetime.now().isoformat(),
            "source": "codex_analysis",
            "agent_type": "GPT Simulation Agent",
            "version": "1.0.0",
            "description": "Complete configuration for GPT Simulation Agent with all functions and workflows for Google Labs"
        },
        "system_instructions": {
            "main_agent": "You are a GPT Simulation Agent orchestrator that manages self-configuration, extraction, gap analysis, social media ingestion, training data processing, and Gem generation. You coordinate multiple specialized engines to analyze GPT configurations and generate Google Labs Gems automatically.",
            "capabilities": [
                "Self-diagnosis: Automatically scan workspace and identify configuration needs",
                "Intelligent extraction: Extract from JSON, Markdown, YAML files",
                "Gap analysis: Identify missing information and generate extraction guides",
                "Social media ingestion: Connect to Facebook & Instagram APIs",
                "Analytics: Process training data and generate insights",
                "Gem generation: Automatically generate Google Labs Gems from extracted configurations"
            ],
            "function_definitions": {
                "configure": {
                    "description": "Perform complete self-configuration. Scans workspace, extracts configuration, performs gap analysis, and generates user guides.",
                    "parameters": {
                        "workspace_path": {
                            "type": "string",
                            "description": "Path to workspace with GPT configuration files",
                            "required": True
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Directory for outputs (optional)",
                            "required": False
                        }
                    },
                    "returns": {
                        "diagnosis": "File scan results",
                        "extracted": "Extracted configuration",
                        "gap_analysis": "Missing information analysis",
                        "completion": "Percentage complete (0-100)"
                    }
                },
                "ingest_social_media": {
                    "description": "Ingest social media interactions from Facebook and Instagram APIs",
                    "parameters": {
                        "platforms": {
                            "type": "array",
                            "description": "Platforms to ingest from (facebook, instagram)",
                            "default": ["facebook", "instagram"]
                        },
                        "days_back": {
                            "type": "integer",
                            "description": "Days to look back",
                            "default": 30
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max interactions per platform",
                            "default": 1000
                        }
                    },
                    "returns": {
                        "facebook": "Facebook interaction data",
                        "instagram": "Instagram interaction data",
                        "total_count": "Total interactions ingested"
                    }
                },
                "process_training_data": {
                    "description": "Process all training data and generate analytics",
                    "parameters": {},
                    "returns": {
                        "total_interactions": "Total interactions processed",
                        "sources": "Data sources processed",
                        "analysis": "Analytics results"
                    }
                },
                "generate_gems": {
                    "description": "Generate Google Labs Gems from extracted configuration",
                    "parameters": {
                        "generate_multiple": {
                            "type": "boolean",
                            "description": "If true, generates multiple Gems for different use cases",
                            "default": False
                        }
                    },
                    "returns": {
                        "gems": "Generated Gems array",
                        "count": "Number of Gems generated",
                        "source": "Source of generation"
                    }
                },
                "generate_gem_from_training": {
                    "description": "Generate a Gem based on training data patterns",
                    "parameters": {},
                    "returns": {
                        "gem": "Generated Gem based on training data",
                        "common_queries": "Common queries identified",
                        "patterns": "Patterns detected"
                    }
                }
            }
        },
        "workflows": []
    }
    
    # Add main GPT Simulation Agent workflow
    main_workflow = {
        "workflow_id": "gpt_simulation_main",
        "name": "GPT Simulation Agent - Main Workflow",
        "description": "Complete GPT Simulation Agent workflow that orchestrates self-configuration, extraction, analysis, and Gem generation",
        "type": "automation",
        "nodes": [
            {
                "id": "node_1",
                "type": "input",
                "name": "Receive Workspace Path",
                "description": "Receives workspace path or configuration files as input",
                "configuration": {
                    "fields": ["workspace_path", "output_dir"],
                    "input_type": "text",
                    "required": ["workspace_path"]
                },
                "connections": [{"target": "node_2", "type": "sequential"}]
            },
            {
                "id": "node_2",
                "type": "process",
                "name": "Self-Diagnosis",
                "description": "Automatically scans workspace and identifies configuration needs",
                "configuration": {
                    "engine": "SelfDiagnosisEngine",
                    "action": "diagnose",
                    "output": "diagnosis.json"
                },
                "connections": [{"target": "node_3", "type": "sequential"}]
            },
            {
                "id": "node_3",
                "type": "process",
                "name": "Intelligent Extraction",
                "description": "Extracts configuration from JSON, Markdown, YAML files",
                "configuration": {
                    "engine": "ExtractionEngine",
                    "action": "extract_all",
                    "output": "extracted_configs/extracted_config.json"
                },
                "connections": [{"target": "node_4", "type": "sequential"}]
            },
            {
                "id": "node_4",
                "type": "analyze",
                "name": "Gap Analysis",
                "description": "Identifies missing information and generates extraction guides",
                "configuration": {
                    "engine": "GapAnalysisEngine",
                    "action": "analyze",
                    "output": "gap_analysis_report.json"
                },
                "connections": [{"target": "node_5", "type": "sequential"}]
            },
            {
                "id": "node_5",
                "type": "process",
                "name": "Generate Gems",
                "description": "Automatically generates Google Labs Gems from extracted configuration",
                "configuration": {
                    "engine": "GemGeneratorEngine",
                    "action": "generate_multiple_gems",
                    "output": "generated_gems/"
                },
                "connections": [{"target": "node_6", "type": "sequential"}]
            },
            {
                "id": "node_6",
                "type": "output",
                "name": "Present Results",
                "description": "Presents all generated Gems with descriptions ready for Google Labs",
                "configuration": {
                    "format": "structured",
                    "include": ["gems", "descriptions", "validation_status", "instructions"]
                },
                "connections": []
            }
        ],
        "validation": {
            "valid": True,
            "errors": [],
            "warnings": [],
            "total_nodes": 6
        }
    }
    
    asset["workflows"].append(main_workflow)
    
    # Add Gem workflows from Codex analysis
    if codex_data and codex_data.get("gems"):
        for gem_item in codex_data["gems"]:
            gem = gem_item.get("gem", {})
            workflow_data = gem.get("workflow", {})
            
            # Enhance nodes
            enhanced_nodes = enhance_workflow_nodes(workflow_data)
            
            gem_workflow = {
                "workflow_id": gem_item.get("type", "unknown").replace("_", "-"),
                "name": gem_item.get("name", "Unknown Gem"),
                "description": workflow_data.get("descripcion", ""),
                "type": workflow_data.get("tipo", "custom"),
                "nodes": enhanced_nodes,
                "validation": workflow_data.get("validacion", {}),
                "gem_description": gem.get("descripcion_gem", "")
            }
            
            asset["workflows"].append(gem_workflow)
    
    # Add knowledge base configuration
    asset["knowledge_base"] = {
        "hierarchy": {
            "level_1_master": ["BMC_Base_Conocimiento_GPT-2.json"],
            "level_2_validation": [],
            "level_3_dynamic": ["panelin_truth_bmcuruguay_web_only_v2.json"],
            "level_4_support": ["panelin_context_consolidacion_sin_backend.md"]
        },
        "source_of_truth": "level_1_master",
        "conflict_resolution": "hierarchical"
    }
    
    # Add tools configuration
    asset["tools"] = {
        "available_tools": [
            "google_search",
            "code_interpreter",
            "file_upload",
            "knowledge_base_access"
        ],
        "configurations": {
            "google_search": {"enabled": True, "max_results": 5},
            "code_interpreter": {"enabled": True, "languages": ["python", "javascript"]},
            "file_upload": {"enabled": True, "formats": ["json", "markdown", "yaml", "txt", "csv"]}
        }
    }
    
    # Add usage instructions
    asset["usage_instructions"] = {
        "upload_method": "Import this JSON file into Google Labs Gems editor or use workflow descriptions",
        "steps": [
            "1. Go to gemini.google.com",
            "2. Click 'Gems' in the left sidebar",
            "3. Click 'New Gem' in 'My Gems from Labs'",
            "4. Use the 'Import' or 'Upload' feature (if available) to upload this file",
            "5. Alternatively, copy the workflow definitions and paste into the editor",
            "6. Configure system instructions using the provided instructions",
            "7. Test each workflow",
            "8. Save and deploy"
        ]
    }
    
    return asset


def main():
    """Generate Opal asset"""
    print("=" * 70)
    print("Generating Opal Asset for GPT Simulation Agent")
    print("=" * 70)
    
    asset = create_opal_asset()
    
    # Save JSON
    output_file = Path(__file__).parent / "opal_gpt_simulation_agent_config.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(asset, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ Opal asset generated: {output_file}")
    print(f"📊 Total workflows: {len(asset['workflows'])}")
    print(f"🔧 Functions defined: {len(asset['system_instructions']['function_definitions'])}")
    
    print("\n📋 Workflows included:")
    for workflow in asset["workflows"]:
        print(f"  - {workflow['name']} ({workflow['workflow_id']})")
        print(f"    Nodes: {len(workflow['nodes'])}")
        print(f"    Valid: {workflow['validation'].get('valid', False)}")
    
    print("\n💡 Next steps:")
    print("  1. Upload opal_gpt_simulation_agent_config.json to Google Labs")
    print("  2. Or use the workflow descriptions to create Gems manually")
    print("  3. Configure system instructions using the provided definitions")


if __name__ == "__main__":
    main()
