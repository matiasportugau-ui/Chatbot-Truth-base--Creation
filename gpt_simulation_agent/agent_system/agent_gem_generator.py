"""
Gem Generator Module

Integrates with Build AI Apps agent to generate Google Labs Gems
from extracted GPT configurations.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import sys

# Try to import loguru, fallback to basic logging
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)

# Add parent directory to path to import Build AI Apps agent
# Path structure: gpt_simulation_agent/agent_system/agent_gem_generator.py
# Need to go up to root: gpt_simulation_agent -> parent directory
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

try:
    from agente_build_ai_apps import AgenteBuildAIApps, diseñar_ai_app
    BUILD_AI_APPS_AVAILABLE = True
    logger.info("Build AI Apps agent loaded successfully")
except ImportError as e:
    logger.warning(f"Build AI Apps agent not available: {e}")
    logger.warning(f"Looking in: {root_path}")
    BUILD_AI_APPS_AVAILABLE = False


class GemGeneratorEngine:
    """Engine for generating Google Labs Gems from GPT configurations"""

    def __init__(self, workspace_path: str, output_dir: Optional[str] = None):
        """
        Initialize Gem generator engine

        Args:
            workspace_path: Path to workspace directory
            output_dir: Directory for outputs
        """
        self.workspace_path = Path(workspace_path)
        self.output_dir = Path(output_dir) if output_dir else Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if BUILD_AI_APPS_AVAILABLE:
            self.build_ai_apps_agent = AgenteBuildAIApps()
        else:
            self.build_ai_apps_agent = None
            logger.warning("Build AI Apps agent not available. Gem generation will be limited.")

    def generate_gem_from_config(self, extracted_config: Dict) -> Dict:
        """
        Generate a Google Labs Gem from extracted GPT configuration

        Args:
            extracted_config: Extracted configuration from GPT Simulation Agent

        Returns:
            Dictionary with generated Gem workflow and description
        """
        logger.info("Generating Gem from extracted configuration...")

        if not BUILD_AI_APPS_AVAILABLE:
            return {
                "error": "Build AI Apps agent not available",
                "suggestion": "Install agente_build_ai_apps.py in the parent directory"
            }

        # Analyze configuration to determine Gem type
        gem_type = self._determine_gem_type(extracted_config)
        
        # Generate description for the Gem
        description = self._generate_gem_description(extracted_config, gem_type)
        
        # Design workflow using Build AI Apps agent
        try:
            resultado = diseñar_ai_app(
                descripcion=description,
                tipo=gem_type,
                optimizar=True,
                exportar_formato="json"
            )
            
            gem_data = {
                "source": "gpt_simulation_agent",
                "extracted_config": extracted_config,
                "gem_type": gem_type,
                "description": description,
                "workflow": resultado.get("workflow", {}),
                "gem_description": resultado.get("descripcion_gem", ""),
                "instrucciones": resultado.get("instrucciones", []),
                "valido": resultado.get("valido", False)
            }
            
            # Save Gem data
            self._save_gem_output("generated_gem.json", gem_data)
            
            logger.info("Gem generated successfully")
            return gem_data
            
        except Exception as e:
            logger.error(f"Error generating Gem: {e}")
            return {
                "error": str(e),
                "description": description,
                "gem_type": gem_type
            }

    def _determine_gem_type(self, config: Dict) -> str:
        """Determine the type of Gem based on configuration"""
        # Check capabilities and features
        capabilities = config.get("capabilities", {})
        knowledge_base = config.get("knowledge_base", {})
        actions = config.get("actions", {})
        
        # If has actions, it's likely an automation
        if actions.get("enabled", False) and actions.get("schemas"):
            return "automation"
        
        # If has extensive knowledge base, it's research/analysis
        if knowledge_base.get("files") and len(knowledge_base.get("files", [])) > 3:
            return "research"
        
        # If has products and formulas, it's data processing
        if config.get("products") or config.get("formulas"):
            return "data_processing"
        
        # Default to custom
        return "custom"

    def _generate_gem_description(self, config: Dict, gem_type: str) -> str:
        """Generate a natural language description for the Gem"""
        identity = config.get("identity", {})
        name = identity.get("name", "AI Assistant")
        role = identity.get("role", "assistant")
        objective = identity.get("objective", "")
        
        # Build description based on configuration
        description_parts = []
        
        # Base description
        if objective:
            description_parts.append(f"Un app que {objective.lower()}")
        else:
            description_parts.append(f"Un app que actúa como {name}, un {role}")
        
        # Add knowledge base capabilities
        knowledge_base = config.get("knowledge_base", {})
        if knowledge_base.get("files"):
            num_files = len(knowledge_base.get("files", []))
            description_parts.append(f"con acceso a {num_files} archivos de conocimiento")
        
        # Add product capabilities
        products = config.get("products", {})
        if products.get("specifications"):
            description_parts.append("que puede cotizar productos")
        
        # Add action capabilities
        actions = config.get("actions", {})
        if actions.get("enabled"):
            description_parts.append("y puede ejecutar acciones personalizadas")
        
        # Add specific workflows based on type
        if gem_type == "automation":
            description_parts.append("automatizando procesos multi-paso")
        elif gem_type == "research":
            description_parts.append("investigando y analizando información")
        elif gem_type == "data_processing":
            description_parts.append("procesando datos y generando reportes")
        
        description = ", ".join(description_parts) + "."
        
        return description

    def generate_multiple_gems(self, extracted_config: Dict) -> List[Dict]:
        """
        Generate multiple Gems for different use cases from the same configuration

        Args:
            extracted_config: Extracted configuration

        Returns:
            List of generated Gems
        """
        logger.info("Generating multiple Gems from configuration...")
        
        gems = []
        
        # Gem 1: Main assistant Gem
        main_gem = self.generate_gem_from_config(extracted_config)
        if "error" not in main_gem:
            gems.append({
                "name": "Main Assistant Gem",
                "gem": main_gem
            })
        
        # Gem 2: Research/Knowledge Gem (if has knowledge base)
        knowledge_base = extracted_config.get("knowledge_base", {})
        if knowledge_base.get("files"):
            research_description = self._generate_research_gem_description(extracted_config)
            try:
                research_result = diseñar_ai_app(
                    descripcion=research_description,
                    tipo="research",
                    optimizar=True
                )
                gems.append({
                    "name": "Research & Knowledge Gem",
                    "gem": research_result
                })
            except Exception as e:
                logger.warning(f"Could not generate research Gem: {e}")
        
        # Gem 3: Quotation/Calculation Gem (if has products/formulas)
        products = extracted_config.get("products", {})
        formulas = extracted_config.get("formulas", {})
        if products or formulas:
            calculation_description = self._generate_calculation_gem_description(extracted_config)
            try:
                calc_result = diseñar_ai_app(
                    descripcion=calculation_description,
                    tipo="data_processing",
                    optimizar=True
                )
                gems.append({
                    "name": "Quotation & Calculation Gem",
                    "gem": calc_result
                })
            except Exception as e:
                logger.warning(f"Could not generate calculation Gem: {e}")
        
        # Save all Gems
        self._save_gem_output("all_generated_gems.json", gems)
        
        return gems

    def _generate_research_gem_description(self, config: Dict) -> str:
        """Generate description for research Gem"""
        knowledge_base = config.get("knowledge_base", {})
        files = knowledge_base.get("files", [])
        
        description = f"Un app que investiga temas usando una base de conocimiento con {len(files)} archivos, "
        description += "busca información relevante, sintetiza los hallazgos, y genera reportes completos con insights."
        
        return description

    def _generate_calculation_gem_description(self, config: Dict) -> str:
        """Generate description for calculation Gem"""
        products = config.get("products", {})
        formulas = config.get("formulas", {})
        
        description = "Un app que recibe especificaciones de productos, "
        description += "aplica fórmulas de cálculo validadas, genera cotizaciones detalladas, "
        description += "y presenta los resultados con desglose de costos."
        
        return description

    def _save_gem_output(self, filename: str, data: Dict):
        """Save Gem output to file"""
        filepath = self.output_dir / "generated_gems" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Saved Gem output to {filepath}")

    def generate_gem_from_training_data(self, training_results: Dict) -> Dict:
        """
        Generate a Gem based on training data patterns

        Args:
            training_results: Results from training data processing

        Returns:
            Generated Gem based on common patterns
        """
        logger.info("Generating Gem from training data patterns...")
        
        if not BUILD_AI_APPS_AVAILABLE:
            return {"error": "Build AI Apps agent not available"}
        
        analysis = training_results.get("analysis", {})
        common_queries = analysis.get("common_queries", [])
        
        if not common_queries:
            return {"error": "No common queries found in training data"}
        
        # Analyze most common query type
        top_query = common_queries[0] if common_queries else "general inquiry"
        
        description = f"Un app que responde a consultas comunes como '{top_query}', "
        description += "procesa la información relevante, y genera respuestas personalizadas basadas en patrones aprendidos."
        
        try:
            resultado = diseñar_ai_app(
                descripcion=description,
                tipo="content",
                optimizar=True
            )
            
            gem_data = {
                "source": "training_data",
                "training_results": training_results,
                "common_queries": common_queries,
                "workflow": resultado.get("workflow", {}),
                "gem_description": resultado.get("descripcion_gem", ""),
                "instrucciones": resultado.get("instrucciones", [])
            }
            
            self._save_gem_output("training_based_gem.json", gem_data)
            
            return gem_data
            
        except Exception as e:
            logger.error(f"Error generating Gem from training data: {e}")
            return {"error": str(e)}
