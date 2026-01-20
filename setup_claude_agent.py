#!/usr/bin/env python3
"""
Setup Panelin Agent para Claude
================================
"""

import os
import sys
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("Instalando anthropic...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic"])
    import anthropic

from agente_cotizacion_panelin import calcular_cotizacion_agente, crear_config_claude

API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    print("❌ ANTHROPIC_API_KEY no configurada")
    print("   Obtén tu key en: https://console.anthropic.com/")
    sys.exit(1)

client = anthropic.Anthropic(api_key=API_KEY)

def chat_con_panelin(mensaje: str):
    """Chat con Panelin usando Claude"""
    
    config = crear_config_claude()
    
    print(f"\n👤 Tú: {mensaje}\n")
    print("🤖 Panelin está pensando...\n")
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        system=config["system"],
        tools=config["tools"],
        messages=[{"role": "user", "content": mensaje}]
    )
    
    # Manejar function calls
    if response.stop_reason == "tool_use":
        tool_use = response.content[0]
        
        if tool_use.name == "calcular_cotizacion":
            print(f"🔧 Panelin está calculando la cotización...\n")
            result = calcular_cotizacion_agente(**tool_use.input)
            
            # Continuar con resultado
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=config["system"],
                tools=config["tools"],
                messages=[
                    {"role": "user", "content": mensaje},
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": f"""Resultado de la cotización:

{result.get('presentacion_texto', '')}

Datos estructurados:
{json.dumps(result.get('cotizacion', {}), indent=2, ensure_ascii=False)}"""
                            }
                        ]
                    }
                ]
            )
    
    print(f"🤖 Panelin: {response.content[0].text}\n")
    return response.content[0].text


def main():
    import json
    
    print("=" * 70)
    print("🤖 PANELIN CON CLAUDE")
    print("=" * 70)
    
    # Ejemplo
    mensaje = """Hola, mi nombre es Agustín Arbiza. 
    Necesito cotizar ISODEC EPS 100mm para un techo.
    El techo mide 10 metros de largo por 5 metros de ancho.
    La distancia entre apoyos es de 4.5 metros.
    La fijación será en hormigón.
    Necesito el sistema completo con babetas y flete a Montevideo."""
    
    chat_con_panelin(mensaje)


if __name__ == "__main__":
    import json
    main()
