#!/usr/bin/env python3
"""
Codex to Gem Generator
======================

Generates Google Labs Gems based on Codex analysis results.
Uses comprehensive chatbot analysis to create highly informed Gems.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from codex_chatbot_analysis import ChatbotCodexAnalyzer
    CODEX_AVAILABLE = True
except ImportError:
    print("Warning: Codex analyzer not found")
    CODEX_AVAILABLE = False

try:
    from agente_build_ai_apps import diseñar_ai_app, AgenteBuildAIApps
    BUILD_AI_APPS_AVAILABLE = True
except ImportError:
    print("Warning: Build AI Apps agent not found")
    BUILD_AI_APPS_AVAILABLE = False


class CodexToGemGenerator:
    """Generate Gems from Codex analysis results"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.codex_analyzer = ChatbotCodexAnalyzer(str(workspace_path)) if CODEX_AVAILABLE else None
        self.build_ai_apps_agent = AgenteBuildAIApps() if BUILD_AI_APPS_AVAILABLE else None
        
    def generate_gems_from_codex(self, codex_results: Optional[Dict] = None) -> Dict:
        """
        Generate Google Labs Gems based on Codex analysis
        
        Args:
            codex_results: Optional pre-computed Codex analysis results
        
        Returns:
            Dictionary with generated Gems based on Codex insights
        """
        if not CODEX_AVAILABLE or not BUILD_AI_APPS_AVAILABLE:
            return {
                "error": "Missing dependencies",
                "codex_available": CODEX_AVAILABLE,
                "build_ai_apps_available": BUILD_AI_APPS_AVAILABLE
            }
        
        # Run Codex analysis if not provided
        if not codex_results:
            print("Running Codex analysis...")
            codex_results = self.codex_analyzer.run_full_analysis()
        
        analysis = codex_results.get("analysis", {})
        gems = []
        
        # Gem 1: Main Assistant Gem (based on intelligence capabilities)
        print("\n📊 Generating Main Assistant Gem from intelligence analysis...")
        intelligence_gem = self._generate_intelligence_gem(analysis.get("intelligence", {}))
        if intelligence_gem:
            gems.append({
                "name": "Main Assistant Gem",
                "type": "intelligence_based",
                "gem": intelligence_gem
            })
        
        # Gem 2: Quotation System Gem (based on functionalities)
        print("\n⚙️  Generating Quotation System Gem from functionalities...")
        quotation_gem = self._generate_quotation_gem(analysis.get("functionalities", {}))
        if quotation_gem:
            gems.append({
                "name": "Quotation System Gem",
                "type": "functionality_based",
                "gem": quotation_gem
            })
        
        # Gem 3: Training & Analytics Gem (based on training system)
        print("\n🎓 Generating Training & Analytics Gem...")
        training_gem = self._generate_training_gem(analysis.get("training_system", {}))
        if training_gem:
            gems.append({
                "name": "Training & Analytics Gem",
                "type": "training_based",
                "gem": training_gem
            })
        
        # Gem 4: Architecture Analysis Gem
        print("\n🏗️  Generating Architecture Analysis Gem...")
        architecture_gem = self._generate_architecture_gem(analysis.get("architecture", {}))
        if architecture_gem:
            gems.append({
                "name": "Architecture Analysis Gem",
                "type": "architecture_based",
                "gem": architecture_gem
            })
        
        # Gem 5: Capacity Assessment Gem
        print("\n💪 Generating Capacity Assessment Gem...")
        capacity_gem = self._generate_capacity_gem(analysis.get("capacities", {}))
        if capacity_gem:
            gems.append({
                "name": "Capacity Assessment Gem",
                "type": "capacity_based",
                "gem": capacity_gem
            })
        
        return {
            "source": "codex_analysis",
            "codex_timestamp": codex_results.get("timestamp"),
            "gems": gems,
            "total_gems": len(gems),
            "codex_insights_used": {
                "intelligence": bool(analysis.get("intelligence")),
                "functionalities": bool(analysis.get("functionalities")),
                "training_system": bool(analysis.get("training_system")),
                "architecture": bool(analysis.get("architecture")),
                "capacities": bool(analysis.get("capacities"))
            }
        }
    
    def _generate_intelligence_gem(self, intelligence: Dict) -> Optional[Dict]:
        """Generate Gem based on intelligence capabilities"""
        nlu = intelligence.get("natural_language_understanding", {})
        reasoning = intelligence.get("reasoning_capabilities", {})
        knowledge = intelligence.get("knowledge_retrieval", {})
        
        # Build description
        description = "Un app que actúa como asistente inteligente especializado en "
        description += f"{nlu.get('domain', 'dominio técnico-comercial')}, "
        description += f"con capacidades de razonamiento multi-paso, "
        description += f"validación técnica, y acceso a base de conocimiento jerárquica. "
        
        if reasoning.get("multi_step_reasoning"):
            description += "El app puede realizar razonamiento complejo en múltiples pasos, "
        
        if knowledge.get("files_count", 0) > 0:
            description += f"accediendo a {knowledge.get('files_count')} archivos de conocimiento, "
            description += "resolviendo conflictos jerárquicamente, "
        
        description += "y generando respuestas personalizadas con validación técnica."
        
        try:
            resultado = diseñar_ai_app(
                descripcion=description,
                tipo="research",
                optimizar=True
            )
            return resultado
        except Exception as e:
            print(f"Error generating intelligence Gem: {e}")
            return None
    
    def _generate_quotation_gem(self, functionalities: Dict) -> Optional[Dict]:
        """Generate Gem based on quotation system functionalities"""
        quotation = functionalities.get("quotation_system", {})
        phases = quotation.get("phases", 0)
        
        description = f"Un app que genera cotizaciones completas en {phases} fases: "
        description += "identificación de productos, validación técnica (autoportancia), "
        description += "búsqueda de datos en base de conocimiento, cálculos con fórmulas validadas, "
        description += "y presentación detallada con desglose de materiales, costos e IVA. "
        description += "Incluye validación de parámetros técnicos y recomendaciones de optimización."
        
        try:
            resultado = diseñar_ai_app(
                descripcion=description,
                tipo="data_processing",
                optimizar=True
            )
            return resultado
        except Exception as e:
            print(f"Error generating quotation Gem: {e}")
            return None
    
    def _generate_training_gem(self, training_system: Dict) -> Optional[Dict]:
        """Generate Gem based on training system capabilities"""
        data_sources = training_system.get("data_sources", {})
        analytics = training_system.get("analytics", {})
        
        description = "Un app que procesa datos de entrenamiento de múltiples fuentes "
        
        platforms = []
        if data_sources.get("social_media", {}).get("available"):
            social = data_sources.get("social_media", {})
            platforms.extend(social.get("platforms", []))
        
        if platforms:
            description += f"({', '.join(platforms)}), "
        
        description += "normaliza interacciones, identifica patrones comunes, "
        description += "analiza métricas de engagement, y genera reportes de analytics "
        description += "con insights sobre consultas frecuentes y comportamiento de usuarios."
        
        try:
            resultado = diseñar_ai_app(
                descripcion=description,
                tipo="analysis",
                optimizar=True
            )
            return resultado
        except Exception as e:
            print(f"Error generating training Gem: {e}")
            return None
    
    def _generate_architecture_gem(self, architecture: Dict) -> Optional[Dict]:
        """Generate Gem based on architecture analysis"""
        components = architecture.get("components", [])
        workflow = architecture.get("workflow", {})
        
        description = "Un app que analiza arquitectura de sistemas de IA, "
        description += f"identificando {len(components)} componentes principales, "
        description += "mapeando flujos de trabajo, analizando integraciones, "
        description += "y generando documentación técnica con recomendaciones de mejora."
        
        try:
            resultado = diseñar_ai_app(
                descripcion=description,
                tipo="analysis",
                optimizar=True
            )
            return resultado
        except Exception as e:
            print(f"Error generating architecture Gem: {e}")
            return None
    
    def _generate_capacity_gem(self, capacities: Dict) -> Optional[Dict]:
        """Generate Gem based on capacity assessment"""
        current = capacities.get("current_capacity", {})
        potential = capacities.get("potential_capacity", {})
        
        description = "Un app que evalúa capacidades de sistemas de IA, "
        description += "analizando capacidad actual vs potencial, identificando cuellos de botella, "
        description += "sugiriendo optimizaciones, y generando reportes de capacidad "
        description += "con métricas de rendimiento y recomendaciones de escalamiento."
        
        try:
            resultado = diseñar_ai_app(
                descripcion=description,
                tipo="analysis",
                optimizar=True
            )
            return resultado
        except Exception as e:
            print(f"Error generating capacity Gem: {e}")
            return None
    
    def save_gems(self, gems_result: Dict, output_file: str = "codex_generated_gems.json"):
        """Save generated Gems to file"""
        output_path = self.workspace_path / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(gems_result, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Gems saved to: {output_path}")
        return str(output_path)


def main():
    """Main function"""
    workspace_path = Path(__file__).parent
    
    print("=" * 70)
    print("🚀 Codex to Gem Generator")
    print("=" * 70)
    print(f"\nWorkspace: {workspace_path}")
    
    generator = CodexToGemGenerator(str(workspace_path))
    
    # Generate Gems from Codex analysis
    print("\n📊 Starting Codex-based Gem generation...")
    gems_result = generator.generate_gems_from_codex()
    
    if "error" in gems_result:
        print(f"\n❌ Error: {gems_result['error']}")
        return
    
    print(f"\n✅ Generated {gems_result['total_gems']} Gems from Codex analysis")
    
    # Display results
    print("\n📋 Generated Gems:")
    for i, gem_item in enumerate(gems_result["gems"], 1):
        print(f"\n{i}. {gem_item['name']} ({gem_item['type']})")
        if gem_item.get("gem") and gem_item["gem"].get("gem_description"):
            desc = gem_item["gem"]["gem_description"]
            print(f"   Description: {desc[:100]}...")
    
    # Save results
    output_path = generator.save_gems(gems_result)
    
    print("\n" + "=" * 70)
    print("✅ Codex to Gem Generation Complete!")
    print("=" * 70)
    print(f"\n📁 Results saved to: {output_path}")
    print("\n💡 Next steps:")
    print("   1. Review generated Gems in the JSON file")
    print("   2. Copy 'gem_description' from each Gem")
    print("   3. Paste into Google Labs (gemini.google.com)")
    print("   4. Test and refine your Gems!")


if __name__ == "__main__":
    main()
