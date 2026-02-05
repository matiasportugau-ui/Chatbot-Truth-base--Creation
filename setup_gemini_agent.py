#!/usr/bin/env python3
"""
Setup Panelin Agent para Gemini
================================
"""

import os
import sys
import json
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    print("Instalando google-generativeai...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai

from agente_cotizacion_panelin import calcular_cotizacion_agente

from config.settings import settings
API_KEY = settings.GOOGLE_API_KEY
if not API_KEY:
    print("❌ GOOGLE_API_KEY no configurada")
    print("   Obtén tu key en: https://makersuite.google.com/app/apikey")
    sys.exit(1)

genai.configure(api_key=API_KEY)

# Definir función para Gemini
cotizacion_tool = {
    "function_declarations": [
        {
            "name": "calcular_cotizacion",
            "description": "Calcula una cotización completa para paneles ISODEC, ISOPANEL, ISOROOF o ISOWALL usando la base de conocimiento validada. Incluye validación técnica, cálculo de materiales y costos con IVA.",
            "parameters": {
                "type": "object",
                "properties": {
                    "producto": {
                        "type": "string",
                        "enum": ["ISODEC EPS", "ISODEC PIR", "ISOPANEL EPS", "ISOROOF 3G", "ISOROOF PLUS", "ISOROOF FOIL", "ISOWALL PIR"],
                        "description": "Tipo de producto a cotizar"
                    },
                    "espesor": {
                        "type": "string",
                        "description": "Espesor del panel en mm"
                    },
                    "largo": {
                        "type": "number",
                        "description": "Largo en metros"
                    },
                    "ancho": {
                        "type": "number",
                        "description": "Ancho en metros"
                    },
                    "luz": {
                        "type": "number",
                        "description": "Distancia entre apoyos (luz) en metros"
                    },
                    "tipo_fijacion": {
                        "type": "string",
                        "enum": ["hormigon", "metal", "madera"],
                        "description": "Tipo de fijación"
                    }
                },
                "required": ["producto", "espesor", "largo", "ancho", "luz", "tipo_fijacion"]
            }
        }
    ]
}

def chat_con_panelin(mensaje: str):
    """Chat con Panelin usando Gemini"""
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        tools=[cotizacion_tool],
        system_instruction="""Eres Panelin, BMC Assistant Pro - experto técnico en cotizaciones.

INSTRUCCIONES:
- SIEMPRE usa calcular_cotizacion() para generar cotizaciones
- NUNCA inventes precios
- Valida autoportancia siempre
- Indaga dimensiones, luz, tipo de fijación antes de cotizar
- Presenta resultados profesionales"""
    )
    
    print(f"\n👤 Tú: {mensaje}\n")
    print("🤖 Panelin está pensando...\n")
    
    response = model.generate_content(mensaje)
    
    # Manejar function calls
    if hasattr(response, 'candidates') and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
            for part in candidate.content.parts:
                if hasattr(part, 'function_call'):
                    func_name = part.function_call.name
                    func_args = {}
                    for key, value in part.function_call.args.items():
                        func_args[key] = value
                    
                    if func_name == "calcular_cotizacion":
                        print(f"🔧 Panelin está calculando la cotización...\n")
                        result = calcular_cotizacion_agente(**func_args)
                        
                        # Continuar con resultado
                        follow_up = f"""Resultado de la cotización:

{result.get('presentacion_texto', '')}

Por favor, presenta esta cotización de forma profesional como Panelin, explicando:
1. La validación técnica de autoportancia
2. Los materiales necesarios
3. El desglose de costos
4. Recomendaciones técnicas si aplica"""
                        
                        response = model.generate_content(follow_up)
    
    print(f"🤖 Panelin: {response.text}\n")
    return response.text


def main():
    print("=" * 70)
    print("🤖 PANELIN CON GEMINI")
    print("=" * 70)
    
    # Ejemplo
    mensaje = """Hola, mi nombre es Agustín Arbiza. 
    Necesito cotizar ISODEC EPS 100mm para un techo.
    El techo mide 10 metros de largo por 5 metros de ancho.
    La distancia entre apoyos es de 4.5 metros.
    La fijación será en hormigón."""
    
    chat_con_panelin(mensaje)


if __name__ == "__main__":
    main()
