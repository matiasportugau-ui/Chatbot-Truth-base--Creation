#!/usr/bin/env python3
"""
Setup para Agente Build AI Apps
================================

Configura el agente especialista en Build AI Apps para diferentes plataformas:
- OpenAI Assistants API
- Claude (Anthropic)
- Gemini (Google)
"""

import os
import json
from pathlib import Path
from typing import Optional

# Importar funciones del agente
from agente_build_ai_apps import (
    get_build_ai_apps_function_schema,
    get_listar_plantillas_function_schema,
    get_usar_plantilla_function_schema
)


def setup_openai_agent():
    """Configura el agente para OpenAI Assistants API"""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY no encontrada en variables de entorno")
            return None
        
        client = OpenAI(api_key=api_key)
        
        # Crear asistente
        assistant = client.beta.assistants.create(
            name="Build AI Apps Specialist",
            instructions="""Eres un especialista en crear AI apps y workflows personalizados usando Google Labs Gems (Opal).

Tu función es ayudar a los usuarios a:
1. Diseñar workflows multi-paso para AI apps
2. Generar descripciones optimizadas para Google Labs
3. Crear estructuras de nodos y pasos
4. Validar y optimizar workflows
5. Proporcionar instrucciones paso a paso

Siempre usa la función diseñar_ai_app() para crear workflows completos.
Usa listar_plantillas_ai_apps() para mostrar opciones disponibles.
Usa usar_plantilla_ai_app() para empezar desde una plantilla.

Sé claro, detallado y proporciona ejemplos prácticos.""",
            model="gpt-4",
            tools=[{
                "type": "function",
                "function": get_build_ai_apps_function_schema()
            }, {
                "type": "function",
                "function": get_listar_plantillas_function_schema()
            }, {
                "type": "function",
                "function": get_usar_plantilla_function_schema()
            }]
        )
        
        print("✅ Asistente OpenAI creado exitosamente")
        print(f"   ID: {assistant.id}")
        print(f"   Nombre: {assistant.name}")
        
        # Guardar ID
        id_file = Path(__file__).parent / ".build_ai_apps_assistant_id"
        with open(id_file, 'w') as f:
            f.write(assistant.id)
        
        print(f"\n💾 ID guardado en: {id_file}")
        print("\n📝 Para usar el agente:")
        print("   from agente_build_ai_apps import AgenteBuildAIAppsOpenAI")
        print(f"   agente = AgenteBuildAIAppsOpenAI('{api_key[:10]}...', '{assistant.id}')")
        
        return assistant
        
    except ImportError:
        print("❌ openai no instalado. Ejecuta: pip install openai")
        return None
    except Exception as e:
        print(f"❌ Error configurando OpenAI: {e}")
        return None


def setup_claude_agent():
    """Configura el agente para Claude (Anthropic)"""
    try:
        import anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("❌ ANTHROPIC_API_KEY no encontrada en variables de entorno")
            return None
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Definir herramientas
        tools = [
            {
                "name": "diseñar_ai_app",
                "description": get_build_ai_apps_function_schema()["description"],
                "input_schema": get_build_ai_apps_function_schema()["parameters"]
            },
            {
                "name": "listar_plantillas_ai_apps",
                "description": get_listar_plantillas_function_schema()["description"],
                "input_schema": get_listar_plantillas_function_schema()["parameters"]
            },
            {
                "name": "usar_plantilla_ai_app",
                "description": get_usar_plantilla_function_schema()["description"],
                "input_schema": get_usar_plantilla_function_schema()["parameters"]
            }
        ]
        
        print("✅ Configuración Claude lista")
        print("\n📝 Para usar el agente con Claude:")
        print("   import anthropic")
        print("   from agente_build_ai_apps import diseñar_ai_app, listar_plantillas_ai_apps, usar_plantilla_ai_app")
        print("   ")
        print("   client = anthropic.Anthropic(api_key='tu-key')")
        print("   # Usa las funciones directamente en tus mensajes")
        
        # Guardar configuración
        config = {
            "platform": "claude",
            "tools": [tool["name"] for tool in tools],
            "model": "claude-3-5-sonnet-20241022"
        }
        
        config_file = Path(__file__).parent / ".build_ai_apps_claude_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 Configuración guardada en: {config_file}")
        
        return config
        
    except ImportError:
        print("❌ anthropic no instalado. Ejecuta: pip install anthropic")
        return None
    except Exception as e:
        print(f"❌ Error configurando Claude: {e}")
        return None


def setup_gemini_agent():
    """Configura el agente para Gemini (Google)"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY no encontrada en variables de entorno")
            return None
        
        genai.configure(api_key=api_key)
        
        # Definir herramientas (Gemini usa function calling)
        tools = [
            {
                "function_declarations": [{
                    "name": "diseñar_ai_app",
                    "description": get_build_ai_apps_function_schema()["description"],
                    "parameters": {
                        "type": "object",
                        "properties": {
                            prop: {
                                "type": param.get("type", "string"),
                                "description": param.get("description", "")
                            }
                            for prop, param in get_build_ai_apps_function_schema()["parameters"]["properties"].items()
                        },
                        "required": get_build_ai_apps_function_schema()["parameters"].get("required", [])
                    }
                }]
            }
        ]
        
        print("✅ Configuración Gemini lista")
        print("\n📝 Para usar el agente con Gemini:")
        print("   import google.generativeai as genai")
        print("   from agente_build_ai_apps import diseñar_ai_app")
        print("   ")
        print("   genai.configure(api_key='tu-key')")
        print("   model = genai.GenerativeModel('gemini-pro', tools=tools)")
        
        # Guardar configuración
        config = {
            "platform": "gemini",
            "tools": ["diseñar_ai_app", "listar_plantillas_ai_apps", "usar_plantilla_ai_app"],
            "model": "gemini-pro"
        }
        
        config_file = Path(__file__).parent / ".build_ai_apps_gemini_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 Configuración guardada en: {config_file}")
        
        return config
        
    except ImportError:
        print("❌ google-generativeai no instalado. Ejecuta: pip install google-generativeai")
        return None
    except Exception as e:
        print(f"❌ Error configurando Gemini: {e}")
        return None


def main():
    """Función principal de setup"""
    print("=" * 70)
    print("🚀 SETUP: Agente Build AI Apps")
    print("=" * 70)
    print("\nSelecciona la plataforma:")
    print("1. OpenAI Assistants API")
    print("2. Claude (Anthropic)")
    print("3. Gemini (Google)")
    print("4. Todas las anteriores")
    
    opcion = input("\nOpción (1-4): ").strip()
    
    resultados = {}
    
    if opcion == "1" or opcion == "4":
        print("\n" + "=" * 70)
        print("🔧 Configurando OpenAI...")
        print("=" * 70)
        resultados["openai"] = setup_openai_agent()
    
    if opcion == "2" or opcion == "4":
        print("\n" + "=" * 70)
        print("🔧 Configurando Claude...")
        print("=" * 70)
        resultados["claude"] = setup_claude_agent()
    
    if opcion == "3" or opcion == "4":
        print("\n" + "=" * 70)
        print("🔧 Configurando Gemini...")
        print("=" * 70)
        resultados["gemini"] = setup_gemini_agent()
    
    print("\n" + "=" * 70)
    print("✅ SETUP COMPLETADO")
    print("=" * 70)
    
    print("\n📚 Próximos pasos:")
    print("1. Revisa GUIA_BUILD_AI_APPS.md para instrucciones detalladas")
    print("2. Prueba el agente con ejemplos en agente_build_ai_apps.py")
    print("3. Usa las funciones directamente en tu código")


if __name__ == "__main__":
    main()
