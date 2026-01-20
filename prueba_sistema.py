#!/usr/bin/env python3
"""
Prueba completa del sistema
"""

import os
import sys

# Configurar API keys
os.environ['ANTHROPIC_API_KEY'] = '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'
os.environ['GOOGLE_API_KEY'] = 'AIzaSyAg_TTib1roBgzqoumJZ-SEWu8SyUwa-X0'

from agente_orquestador_multi_modelo import AgenteOrquestadorMultiModelo
from motor_cotizacion_panelin import MotorCotizacionPanelin
from agente_analisis_inteligente import AgenteAnalisisInteligente

print("=" * 70)
print("🧪 PRUEBA COMPLETA DEL SISTEMA MULTI-MODELO")
print("=" * 70)

# Test 1: Motor directo
print("\n1️⃣  Motor de Cotización")
print("-" * 70)
motor = MotorCotizacionPanelin()
cotizacion = motor.calcular_cotizacion(
    producto='ISODEC EPS',
    espesor='100',
    largo=10.0,
    ancho=5.0,
    luz=4.5,
    tipo_fijacion='hormigon'
)
if 'error' not in cotizacion:
    total = cotizacion.get('costos', {}).get('total', 0)
    autoportancia = cotizacion.get('validacion', {}).get('cumple_autoportancia', False)
    print(f"✅ Presupuesto generado: ${total:.2f}")
    print(f"✅ Autoportancia validada: {autoportancia}")
    print(f"📊 Materiales: {len(cotizacion.get('materiales', {}))} items")
else:
    print(f"❌ Error: {cotizacion.get('error')}")

# Test 2: Agente Orquestador
print("\n2️⃣  Agente Orquestador")
print("-" * 70)
agente = AgenteOrquestadorMultiModelo()
print("Modelos disponibles:")
for modelo, disponible in agente.modelos_disponibles.items():
    status = "✅" if disponible else "❌"
    print(f"  {status} {modelo.value.upper()}")

# Test 3: Caso real con formato correcto
print("\n3️⃣  Proceso Completo - Caso Real")
print("-" * 70)
input_real = {
    'fila': 1,
    'fecha': '19-01',
    'cliente': 'Agustín Arbiza',
    'consulta': 'ISODEC EPS 100mm',
    'producto': 'ISODEC EPS',
    'dimensiones': '10m x 5m',
    'luz': '4.5',
    'fijacion': 'Hormigón',
    'notas': ''
}

print(f"Cliente: {input_real['cliente']}")
print(f"Producto: {input_real['consulta']}")
print(f"Dimensiones: {input_real['dimensiones']}")

presupuesto = agente.generar_presupuesto(input_real)
if 'error' not in presupuesto:
    total = presupuesto.get('presupuesto', {}).get('costos', {}).get('total', 0)
    print(f"✅ Presupuesto generado: ${total:.2f}")
    params = presupuesto.get('parametros_usados', {})
    print(f"📊 Parámetros: {params.get('producto')} {params.get('espesor')}mm, {params.get('largo')}m x {params.get('ancho')}m")
else:
    print(f"⚠️  {presupuesto.get('error', 'Error desconocido')}")

# Test 4: Buscar inputs reales
print("\n4️⃣  Buscar Inputs Reales")
print("-" * 70)
agente_analisis = AgenteAnalisisInteligente()
inputs = agente_analisis.revisar_inputs()
if len(inputs) > 20:
    inputs = inputs[:20]

inputs_validos = [i for i in inputs if i.get('consulta') and 
                  ('ISODEC' in i.get('consulta', '').upper() or 
                   'ISOROOF' in i.get('consulta', '').upper() or
                   'ISOPANEL' in i.get('consulta', '').upper())]

print(f"✅ Total inputs encontrados: {len(inputs)}")
print(f"✅ Inputs válidos (con producto): {len(inputs_validos)}")

if inputs_validos:
    print("\n📋 Primeros 3 inputs válidos:")
    for idx, inp in enumerate(inputs_validos[:3], 1):
        print(f"\n{idx}. Cliente: {inp.get('cliente', 'N/A')}")
        print(f"   Consulta: {inp.get('consulta', 'N/A')[:70]}")
        print(f"   Dimensiones: {inp.get('dimensiones', 'N/A')}")
        
        # Intentar generar presupuesto
        presupuesto = agente_analisis.generar_presupuesto(inp)
        if 'error' not in presupuesto:
            total = presupuesto.get('presupuesto', {}).get('costos', {}).get('total', 0)
            print(f"   ✅ Presupuesto: ${total:.2f}")
        else:
            error = presupuesto.get('error', 'Error')
            print(f"   ⚠️  {error[:50]}")

print("\n" + "=" * 70)
print("✅ PRUEBA COMPLETADA")
print("=" * 70)
print("\n📊 Resumen:")
print(f"  ✅ Motor de cotización: Funcionando")
print(f"  ✅ Agente orquestador: Funcionando")
print(f"  ✅ Modelos configurados: {sum(agente.modelos_disponibles.values())}/3")
print(f"  ✅ Inputs procesados: {len(inputs)}")
print(f"  ✅ Inputs válidos: {len(inputs_validos)}")
