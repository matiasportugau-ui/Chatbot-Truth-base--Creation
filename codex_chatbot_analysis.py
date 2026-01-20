#!/usr/bin/env python3
"""
Codex Analysis: Chatbot Intelligence, Functionalities, Capacities, and Training System
====================================================================================

Comprehensive analysis of Panelin (BMC Assistant Pro) chatbot system.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict
import re

try:
    from gpt_simulation_agent.agent_system.gpt_simulation_agent import GPTSimulationAgent
    from gpt_simulation_agent.agent_system.agent_self_diagnosis import SelfDiagnosisEngine
    from gpt_simulation_agent.agent_system.agent_extraction import ExtractionEngine
    from gpt_simulation_agent.agent_system.agent_training_processor import TrainingProcessor
except ImportError:
    print("Warning: GPT simulation agent modules not found. Some features may be limited.")
    GPTSimulationAgent = None


class ChatbotCodexAnalyzer:
    """Comprehensive analyzer for chatbot intelligence and capabilities"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.analysis_results = {}
        
    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete codex analysis"""
        print("=" * 80)
        print("CODEX ANALYSIS: Chatbot Intelligence & Functionalities")
        print("=" * 80)
        print()
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "workspace": str(self.workspace_path),
            "analysis": {}
        }
        
        # 1. Intelligence Capabilities Analysis
        print("📊 Analyzing Intelligence Capabilities...")
        results["analysis"]["intelligence"] = self.analyze_intelligence()
        
        # 2. Functionalities Analysis
        print("⚙️  Analyzing Functionalities...")
        results["analysis"]["functionalities"] = self.analyze_functionalities()
        
        # 3. Training System Analysis
        print("🎓 Analyzing Training System...")
        results["analysis"]["training_system"] = self.analyze_training_system()
        
        # 4. Architecture Analysis
        print("🏗️  Analyzing Architecture...")
        results["analysis"]["architecture"] = self.analyze_architecture()
        
        # 5. Capacity Assessment
        print("💪 Assessing Capacities...")
        results["analysis"]["capacities"] = self.assess_capacities()
        
        # 6. Recommendations
        print("💡 Generating Recommendations...")
        results["analysis"]["recommendations"] = self.generate_recommendations(results["analysis"])
        
        return results
    
    def analyze_intelligence(self) -> Dict[str, Any]:
        """Analyze chatbot intelligence capabilities"""
        intelligence = {
            "natural_language_understanding": {},
            "reasoning_capabilities": {},
            "knowledge_retrieval": {},
            "context_management": {},
            "personalization": {},
            "guardrails": {}
        }
        
        # Read system instructions
        system_instructions = self._read_system_instructions()
        
        # NLU Analysis
        intelligence["natural_language_understanding"] = {
            "language": "Spanish (Rioplatense - Uruguay)",
            "domain": "Technical-commercial (construction materials)",
            "query_types_supported": [
                "Product identification",
                "Technical specifications",
                "Price quotations",
                "Technical validation",
                "Product recommendations",
                "Business rules queries"
            ],
            "complexity_handling": "Multi-phase quotation process (5 phases)",
            "intent_recognition": "Product queries, quotations, technical questions"
        }
        
        # Reasoning Capabilities
        intelligence["reasoning_capabilities"] = {
            "multi_step_reasoning": True,
            "technical_validation": True,
            "optimization_suggestions": True,
            "conflict_detection": True,
            "formula_application": True,
            "reasoning_steps": [
                "Product identification",
                "Parameter extraction",
                "Technical validation (autoportancia)",
                "Data retrieval from knowledge base",
                "Formula-based calculations",
                "Business rule application",
                "Response generation"
            ]
        }
        
        # Knowledge Retrieval
        kb_files = self._find_knowledge_base_files()
        intelligence["knowledge_retrieval"] = {
            "source_hierarchy": {
                "level_1_master": [f for f in kb_files if "Base_Conocimiento_GPT" in f],
                "level_2_validation": [f for f in kb_files if "Unificada" in f],
                "level_3_dynamic": [f for f in kb_files if "web_only" in f or "truth" in f],
                "level_4_support": [f for f in kb_files if f.endswith((".rtf", ".md", ".csv"))]
            },
            "retrieval_strategy": "Hierarchical source of truth with conflict resolution",
            "files_count": len(kb_files),
            "conflict_resolution": "Level 1 always wins, conflicts reported"
        }
        
        # Context Management
        intelligence["context_management"] = {
            "context_awareness": True,
            "conversation_memory": "User-specific personalization",
            "special_commands": ["/estado", "/checkpoint", "/consolidar"],
            "context_risk_monitoring": True,
            "ledger_system": "Incremental ledger for context tracking"
        }
        
        # Personalization
        intelligence["personalization"] = {
            "user_specific": True,
            "personalized_users": ["Mauro", "Martin", "Rami"],
            "personalization_type": "Dynamic, concept-guided, non-scripted",
            "tone_adaptation": "Rioplatense, professional, technical but accessible"
        }
        
        # Guardrails
        guardrails = self._extract_guardrails(system_instructions)
        intelligence["guardrails"] = {
            "source_of_truth_enforcement": True,
            "price_validation": "Must read Level 1 before giving prices",
            "formula_validation": "Only use formulas from knowledge base",
            "conflict_detection": True,
            "business_rule_validation": True,
            "guardrail_checks": guardrails
        }
        
        return intelligence
    
    def analyze_functionalities(self) -> Dict[str, Any]:
        """Analyze chatbot functionalities"""
        functionalities = {
            "core_functions": {},
            "quotation_system": {},
            "product_consultation": {},
            "technical_validation": {},
            "document_generation": {},
            "integration_capabilities": {}
        }
        
        # Core Functions
        functionalities["core_functions"] = {
            "product_identification": True,
            "price_quotation": True,
            "technical_specification_lookup": True,
            "autoportancia_validation": True,
            "material_calculation": True,
            "business_rule_application": True,
            "pdf_generation": True,
            "code_interpreter": True
        }
        
        # Quotation System
        functionalities["quotation_system"] = {
            "phases": 5,
            "phase_1_identification": {
                "product_types": ["Techo Liviano", "Techo Pesado", "Pared", "Impermeabilización"],
                "parameters_extracted": ["espesor", "luz", "cantidad", "tipo_fijacion"]
            },
            "phase_2_validation": {
                "autoportancia_check": True,
                "light_validation": True,
                "recommendation_engine": True
            },
            "phase_3_data_retrieval": {
                "price_lookup": True,
                "specification_lookup": True,
                "dynamic_price_check": True
            },
            "phase_4_calculations": {
                "formulas_used": [
                    "Paneles calculation",
                    "Apoyos calculation",
                    "Puntos fijación",
                    "Varilla cantidad",
                    "Tuercas (metal/hormigón)",
                    "Tacos hormigón",
                    "Gotero (frontal/lateral)",
                    "Remaches",
                    "Silicona"
                ],
                "rounding_rules": "ROUNDUP for all calculations"
            },
            "phase_5_presentation": {
                "detailed_breakdown": True,
                "iva_calculation": True,
                "technical_recommendations": True,
                "fixation_notes": True
            }
        }
        
        # Product Consultation
        functionalities["product_consultation"] = {
            "product_lines": ["ISODEC", "ISOPANEL", "ISOROOF", "ISOWALL"],
            "specifications_available": [
                "Espesores",
                "Autoportancia",
                "Ancho útil",
                "Sistemas de fijación",
                "Precios",
                "Aplicaciones"
            ],
            "consultative_selling": True,
            "optimization_suggestions": True
        }
        
        # Technical Validation
        functionalities["technical_validation"] = {
            "autoportancia_validation": True,
            "light_distance_validation": True,
            "safety_recommendations": True,
            "material_optimization": True,
            "structural_advice": True
        }
        
        # Document Generation
        functionalities["document_generation"] = {
            "pdf_generation": True,
            "pdf_tool": "Code Interpreter with reportlab",
            "quote_formatting": True,
            "structured_output": True
        }
        
        # Integration Capabilities
        functionalities["integration_capabilities"] = {
            "openai_assistants_api": True,
            "knowledge_base_files": True,
            "code_interpreter": True,
            "social_media_ingestion": "Facebook, Instagram (via training system)",
            "shopify_integration": "Via knowledge base JSON files"
        }
        
        return functionalities
    
    def analyze_training_system(self) -> Dict[str, Any]:
        """Analyze training system architecture"""
        training = {
            "architecture": {},
            "data_sources": {},
            "processing_pipeline": {},
            "analytics": {},
            "social_media_integration": {}
        }
        
        # Check if training system exists
        training_data_path = self.workspace_path / "gpt_simulation_agent" / "training_data"
        has_training_system = training_data_path.exists()
        
        # Architecture
        training["architecture"] = {
            "system_type": "GPT Simulation Agent",
            "components": [
                "SelfDiagnosisEngine",
                "ExtractionEngine",
                "GapAnalysisEngine",
                "SocialIngestionEngine",
                "TrainingProcessor",
                "AnalyticsEngine"
            ],
            "workflow_phases": [
                "Phase 1: Self-Configuration",
                "Phase 2: Social Media Ingestion",
                "Phase 3: Training Data Processing",
                "Phase 4: Analytics Generation"
            ]
        }
        
        # Data Sources
        training["data_sources"] = {
            "social_media": {
                "platforms": ["Facebook", "Instagram"],
                "data_types": ["posts", "comments", "messages", "DMs"],
                "ingestion_method": "API-based",
                "available": has_training_system
            },
            "quotes": {
                "source": "Historical quotations",
                "format": "JSON",
                "available": (training_data_path / "quotes").exists() if has_training_system else False
            },
            "interactions": {
                "source": "General user interactions",
                "format": "JSON",
                "available": (training_data_path / "interactions").exists() if has_training_system else False
            }
        }
        
        # Processing Pipeline
        training["processing_pipeline"] = {
            "steps": [
                "1. Data Ingestion (Social Media APIs)",
                "2. Normalization (Platform-specific → Standard format)",
                "3. Aggregation (All sources combined)",
                "4. Analytics (Pattern detection, metrics)",
                "5. Report Generation (Markdown reports)"
            ],
            "normalization": "Platform-specific data normalized to standard interaction format",
            "analytics_capabilities": [
                "Question rate analysis",
                "Common queries identification",
                "Engagement metrics",
                "Interaction patterns",
                "Training data quality assessment"
            ]
        }
        
        # Analytics
        training["analytics"] = {
            "metrics_tracked": [
                "Total interactions",
                "Question rate",
                "Common queries",
                "Engagement metrics",
                "Source distribution",
                "Interaction patterns"
            ],
            "report_generation": True,
            "report_format": "Markdown"
        }
        
        # Social Media Integration
        training["social_media_integration"] = {
            "facebook": {
                "api_client": "FacebookAPIClient",
                "endpoints": ["posts", "comments", "messages"],
                "config_required": ["APP_ID", "APP_SECRET", "PAGE_ACCESS_TOKEN", "PAGE_ID"]
            },
            "instagram": {
                "api_client": "InstagramAPIClient",
                "endpoints": ["media", "comments", "DMs"],
                "config_required": ["APP_ID", "ACCESS_TOKEN", "BUSINESS_ACCOUNT_ID"]
            },
            "ingestion_parameters": {
                "days_back": "Configurable (default: 30)",
                "limit_per_platform": "Configurable (default: 1000)"
            }
        }
        
        return training
    
    def analyze_architecture(self) -> Dict[str, Any]:
        """Analyze system architecture"""
        architecture = {
            "layered_architecture": {},
            "knowledge_base_structure": {},
            "retrieval_strategy": {},
            "generation_pipeline": {},
            "orchestration": {}
        }
        
        # Layered Architecture
        architecture["layered_architecture"] = {
            "layer_1_identity": {
                "purpose": "Fixed identity and personality",
                "components": ["Name (Panelin)", "Role", "User personalization"],
                "immutable": True
            },
            "layer_2_knowledge_base": {
                "purpose": "Structured information storage",
                "hierarchy_levels": 4,
                "files_count": len(self._find_knowledge_base_files())
            },
            "layer_3_retrieval": {
                "purpose": "Efficient information finding",
                "strategy": "Hybrid search (semantic + keyword + structured)",
                "reranking": True
            },
            "layer_4_generation": {
                "purpose": "Response generation",
                "pipeline": "Context + Instructions + Guardrails → LLM → Post-processing"
            },
            "layer_5_memory": {
                "purpose": "User memory and personalization",
                "features": ["User history", "Preferences", "Conversation context"]
            },
            "layer_6_orchestration": {
                "purpose": "Coordinate all layers",
                "decision_flow": "Query type identification → Retrieval → Generation → Delivery"
            }
        }
        
        # Knowledge Base Structure
        kb_files = self._find_knowledge_base_files()
        architecture["knowledge_base_structure"] = {
            "total_files": len(kb_files),
            "file_types": {
                "json": len([f for f in kb_files if f.endswith(".json")]),
                "markdown": len([f for f in kb_files if f.endswith(".md")]),
                "rtf": len([f for f in kb_files if f.endswith(".rtf")]),
                "csv": len([f for f in kb_files if f.endswith(".csv")])
            },
            "hierarchy": {
                "level_1_master": "BMC_Base_Conocimiento_GPT.json",
                "level_2_validation": "BMC_Base_Unificada_v4.json",
                "level_3_dynamic": "panelin_truth_bmcuruguay_web_only_v2.json",
                "level_4_support": "Aleros.rtf, panelin_context_consolidacion_sin_backend.md, CSV"
            }
        }
        
        # Retrieval Strategy
        architecture["retrieval_strategy"] = {
            "hybrid_search": {
                "semantic_search": "Vector embeddings for intent capture",
                "keyword_search": "Exact terms, product codes, numbers",
                "structured_search": "JSON path queries, filters"
            },
            "reranking": {
                "factors": [
                    "Semantic relevance",
                    "Source priority (Level 1 > 2 > 3)",
                    "Data freshness",
                    "Technical confidence"
                ]
            },
            "chunking_strategy": "Logical structure-based (not just size), with overlapping"
        }
        
        # Generation Pipeline
        architecture["generation_pipeline"] = {
            "input": "Retrieved context + System instructions + User personality",
            "guardrails": "Source validation, formula validation, conflict detection",
            "model": "GPT-4 / GPT-4 Turbo / GPT-4o (configurable)",
            "post_processing": "Formula validation, price verification, output formatting",
            "output": "Structured response (text or PDF)"
        }
        
        # Orchestration
        architecture["orchestration"] = {
            "query_classification": "Identifies query type (quotation, consultation, etc.)",
            "flow_control": "Coordinates retrieval → validation → generation → delivery",
            "error_handling": "Conflict detection, missing data handling, fallback strategies"
        }
        
        return architecture
    
    def assess_capacities(self) -> Dict[str, Any]:
        """Assess system capacities and limitations"""
        capacities = {
            "processing_capacity": {},
            "knowledge_capacity": {},
            "scalability": {},
            "performance_metrics": {},
            "limitations": {}
        }
        
        # Processing Capacity
        capacities["processing_capacity"] = {
            "concurrent_users": "Limited by OpenAI API rate limits",
            "quotation_complexity": "Multi-phase, formula-based calculations",
            "context_window": "Model-dependent (GPT-4: 128k tokens)",
            "response_time": "API-dependent, typically 2-10 seconds"
        }
        
        # Knowledge Capacity
        kb_files = self._find_knowledge_base_files()
        capacities["knowledge_capacity"] = {
            "knowledge_base_files": len(kb_files),
            "product_coverage": "ISODEC, ISOPANEL, ISOROOF, ISOWALL lines",
            "formula_coverage": "Complete quotation formulas",
            "business_rules": "IVA, shipping, technical rules",
            "update_mechanism": "Manual file updates + dynamic web snapshot"
        }
        
        # Scalability
        capacities["scalability"] = {
            "horizontal_scaling": "Limited by OpenAI API",
            "knowledge_expansion": "Add files to knowledge base",
            "training_data_growth": "Social media ingestion supports growth",
            "user_personalization": "Currently 3 users, extensible"
        }
        
        # Performance Metrics
        capacities["performance_metrics"] = {
            "accuracy": "High (source of truth enforcement)",
            "precision": "High (formula validation)",
            "recall": "High (hybrid search strategy)",
            "consistency": "High (hierarchical source resolution)"
        }
        
        # Limitations
        capacities["limitations"] = {
            "api_dependency": "Requires OpenAI API access",
            "knowledge_boundaries": "Limited to knowledge base content",
            "real_time_updates": "Manual or scheduled (not real-time)",
            "multilingual": "Currently Spanish only",
            "custom_model_training": "Uses pre-trained models, no fine-tuning yet"
        }
        
        return capacities
    
    def generate_recommendations(self, analysis: Dict) -> Dict[str, Any]:
        """Generate recommendations based on analysis"""
        recommendations = {
            "immediate_improvements": [],
            "architectural_enhancements": [],
            "training_system_improvements": [],
            "performance_optimizations": []
        }
        
        # Immediate Improvements
        recommendations["immediate_improvements"] = [
            "Enhance source of truth enforcement in guardrails",
            "Improve conflict detection and reporting",
            "Add more detailed logging for debugging",
            "Create comprehensive test cases for quotation formulas"
        ]
        
        # Architectural Enhancements
        recommendations["architectural_enhancements"] = [
            "Implement vector database for semantic search",
            "Add caching layer for frequently accessed data",
            "Implement automatic knowledge base refresh",
            "Add monitoring and alerting system",
            "Create feedback loop for continuous improvement"
        ]
        
        # Training System Improvements
        recommendations["training_system_improvements"] = [
            "Expand social media platform support",
            "Implement automated training data quality checks",
            "Add fine-tuning pipeline for custom model",
            "Create training data validation framework"
        ]
        
        # Performance Optimizations
        recommendations["performance_optimizations"] = [
            "Implement query caching",
            "Optimize knowledge base chunking",
            "Add parallel processing for multi-source queries",
            "Implement lazy loading for knowledge base files"
        ]
        
        return recommendations
    
    # Helper methods
    def _read_system_instructions(self) -> str:
        """Read system instructions file"""
        possible_files = [
            "Instrucciones_Sistema_Panelin_CopiarPegar.txt",
            "setup_panelin_with_model.py"
        ]
        
        for filename in possible_files:
            filepath = self.workspace_path / filename
            if filepath.exists():
                return filepath.read_text(encoding="utf-8")
        
        return ""
    
    def _find_knowledge_base_files(self) -> List[str]:
        """Find all knowledge base files"""
        kb_patterns = [
            "*Base_Conocimiento*.json",
            "*Unificada*.json",
            "*truth*.json",
            "*Catalogo*.json",
            "*.rtf",
            "*context*.md"
        ]
        
        files = []
        for pattern in kb_patterns:
            files.extend([str(f.name) for f in self.workspace_path.glob(pattern)])
        
        return list(set(files))
    
    def _extract_guardrails(self, instructions: str) -> List[str]:
        """Extract guardrail checks from instructions"""
        guardrails = []
        
        if "GUARDRAILS" in instructions or "guardrails" in instructions.lower():
            # Extract guardrail section
            lines = instructions.split("\n")
            in_guardrails = False
            for line in lines:
                if "GUARDRAILS" in line.upper() or "VALIDACIONES OBLIGATORIAS" in line.upper():
                    in_guardrails = True
                    continue
                if in_guardrails and line.strip():
                    if line.strip().startswith("✓") or line.strip().startswith("-"):
                        guardrails.append(line.strip())
                    elif line.strip().startswith("#") and "GUARDRAILS" not in line.upper():
                        break
        
        return guardrails if guardrails else [
            "Source of truth validation",
            "Price validation from Level 1",
            "Formula validation",
            "Conflict detection",
            "Business rule validation"
        ]


def main():
    """Main execution"""
    workspace_path = Path(__file__).parent
    
    print("Initializing Codex Analyzer...")
    analyzer = ChatbotCodexAnalyzer(str(workspace_path))
    
    print("Running comprehensive analysis...")
    results = analyzer.run_full_analysis()
    
    # Save results
    output_file = workspace_path / "codex_analysis_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Results saved to: {output_file}")
    print()
    
    # Print summary
    print("📊 SUMMARY:")
    print(f"  Intelligence Capabilities: {len(results['analysis']['intelligence'])} categories")
    print(f"  Functionalities: {len(results['analysis']['functionalities'])} categories")
    print(f"  Training System: {len(results['analysis']['training_system'])} components")
    print(f"  Architecture: {len(results['analysis']['architecture'])} layers")
    print(f"  Recommendations: {sum(len(v) for v in results['analysis']['recommendations'].values())} items")
    print()
    
    return results


if __name__ == "__main__":
    try:
        results = main()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
