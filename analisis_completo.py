#!/usr/bin/env python3
"""
Análisis Completo del Sistema
"""

import os
import sys

# Configurar API keys
os.environ['ANTHROPIC_API_KEY'] = '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'
os.environ['GOOGLE_API_KEY'] = 'AIzaSyAg_TTib1roBgzqoumJZ-SEWu8SyUwa-X0'

from agente_analisis_inteligente import AgenteAnalisisInteligente
from agente_orquestador_multi_modelo import AgenteOrquestadorMultiModelo
import json

print("=" * 70)
print("📊 ANÁLISIS COMPLETO DEL SISTEMA")
print("=" * 70)

# 1. Verificar modelos
print("\n1️⃣  Verificación de Modelos")
print("-" * 70)
agente_orquestador = AgenteOrquestadorMultiModelo()
for modelo, disponible in agente_orquestador.modelos_disponibles.items():
    status = "✅" if disponible else "❌"
    print(f"   {status} {modelo.value.upper()}")

# 2. Buscar inputs
print("\n2️⃣  Búsqueda de Inputs")
print("-" * 70)
agente = AgenteAnalisisInteligente()
inputs = agente.revisar_inputs()
print(f"   ✅ Total inputs encontrados: {len(inputs)}")

# Filtrar inputs válidos
inputs_validos = []
for inp in inputs:
    consulta = inp.get('consulta', '').upper()
    if any(p in consulta for p in ['ISODEC', 'ISOROOF', 'ISOPANEL', 'ISOWALL']):
        inputs_validos.append(inp)

print(f"   ✅ Inputs válidos (con producto): {len(inputs_validos)}")

# 3. Procesar inputs válidos
print("\n3️⃣  Procesamiento de Inputs Válidos")
print("-" * 70)
resultados = []

for idx, inp in enumerate(inputs_validos[:10], 1):
    cliente = inp.get('cliente', 'N/A')
    consulta = inp.get('consulta', 'N/A')[:60]
    print(f"\n{idx}. {cliente}")
    print(f"   Consulta: {consulta}")
    
    # Generar presupuesto
    presupuesto = agente.generar_presupuesto(inp)
    if 'error' not in presupuesto:
        total = presupuesto.get('presupuesto', {}).get('costos', {}).get('total', 0)
        print(f"   ✅ Presupuesto: ${total:.2f}")
        resultados.append({
            'cliente': cliente,
            'consulta': consulta,
            'presupuesto': total,
            'error': None
        })
    else:
        error = presupuesto.get('error', 'Error desconocido')
        print(f"   ⚠️  {error[:60]}")
        resultados.append({
            'cliente': cliente,
            'consulta': consulta,
            'presupuesto': None,
            'error': str(error)
        })

# 4. Resumen final
print("\n" + "=" * 70)
print("📊 RESUMEN FINAL")
print("=" * 70)
exitosos = sum(1 for r in resultados if r['presupuesto'] is not None)
print(f"   📋 Total inputs: {len(inputs)}")
print(f"   ✅ Inputs válidos: {len(inputs_validos)}")
print(f"   🔧 Procesados: {len(resultados)}")
print(f"   ✅ Exitosos: {exitosos}/{len(resultados)}")
print(f"   ⚠️  Errores: {len(resultados) - exitosos}/{len(resultados)}")

# Guardar resultados
try:
    with open('analisis_completo_resultados.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_inputs': len(inputs),
            'inputs_validos': len(inputs_validos),
            'procesados': len(resultados),
            'exitosos': exitosos,
            'resultados': resultados
        }, f, indent=2, ensure_ascii=False, default=str)
    print("\n💾 Resultados guardados en: analisis_completo_resultados.json")
except Exception as e:
    print(f"\n⚠️  Error guardando resultados: {e}")

print("\n" + "=" * 70)
print("✅ ANÁLISIS COMPLETADO")
print("=" * 70)
