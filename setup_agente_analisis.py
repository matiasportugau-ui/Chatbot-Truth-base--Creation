#!/usr/bin/env python3
"""
Setup Agente de Análisis Inteligente
=====================================

Configura el agente de análisis inteligente para OpenAI/Claude/Gemini
"""

import os
import sys
from pathlib import Path

# Importar funciones
sys.path.insert(0, str(Path(__file__).parent))
from agente_analisis_inteligente import AgenteAnalisisInteligente, analizar_cotizacion_completa
from agente_cotizacion_panelin import AgentePanelinOpenAI, crear_config_openai_assistant

def ejemplo_uso_directo():
    """Ejemplo de uso directo del agente"""
    print("=" * 70)
    print("🤖 AGENTE DE ANÁLISIS INTELIGENTE - USO DIRECTO")
    print("=" * 70)
    
    agente = AgenteAnalisisInteligente()
    
    # Analizar cotizaciones de un cliente específico
    resultado = agente.proceso_completo(
        cliente="Agustín",  # Opcional: filtrar por cliente
        producto="ISODEC",  # Opcional: filtrar por producto
        limite=5  # Procesar máximo 5 inputs
    )
    
    print("\n" + "=" * 70)
    print("📊 RESULTADOS")
    print("=" * 70)
    
    for idx, item in enumerate(resultado['resultados'], 1):
        print(f"\n{item['input'].get('cliente', 'N/A')} - {item['input'].get('fecha', 'N/A')}")
        
        if item.get('presupuesto') and 'error' not in item['presupuesto']:
            presupuesto_total = item['presupuesto'].get('presupuesto', {}).get('costos', {}).get('total', 0)
            print(f"  💰 Presupuesto generado: ${presupuesto_total:.2f}")
        
        if item.get('pdf_real') and 'error' not in item['pdf_real']:
            pdf_total = item['pdf_real'].get('total', 0)
            print(f"  📄 PDF real: ${pdf_total:.2f}")
        
        if item.get('comparacion') and 'error' not in item['comparacion']:
            diff_pct = item['comparacion'].get('diferencia_porcentaje', 0)
            coincide = item['comparacion'].get('coincide', False)
            print(f"  ⚖️  Diferencia: {diff_pct:+.2f}% {'✅' if coincide else '⚠️'}")
        
        if item.get('leccion'):
            lecciones = item['leccion'].get('lecciones', [])
            if lecciones:
                print(f"  🧠 Lecciones: {len(lecciones)} aprendidas")


def ejemplo_con_openai():
    """Ejemplo integrando con OpenAI Assistant"""
    print("=" * 70)
    print("🤖 AGENTE DE ANÁLISIS INTELIGENTE - CON OPENAI")
    print("=" * 70)
    
    from config.settings import settings
    # Crear asistente con función de análisis
    agente = AgentePanelinOpenAI(settings.OPENAI_API_KEY)
    
    # Usar asistente configurado
    assistant_id = settings.OPENAI_ASSISTANT_ID
    agente.assistant_id = assistant_id
    
    # Crear thread
    thread = agente.client.beta.threads.create()
    
    # Mensaje para analizar
    mensaje = """Por favor, analiza las cotizaciones de los últimos inputs.
    Usa la función analizar_cotizacion_completa() para:
    1. Revisar los inputs
    2. Generar presupuestos
    3. Buscar PDFs reales
    4. Comparar resultados
    5. Analizar diferencias y aprender"""
    
    respuesta = agente.procesar_mensaje(thread.id, mensaje)
    print(respuesta)


if __name__ == "__main__":
    import sys
    
    modo = sys.argv[1] if len(sys.argv) > 1 else "directo"
    
    if modo == "openai":
        ejemplo_con_openai()
    else:
        ejemplo_uso_directo()
