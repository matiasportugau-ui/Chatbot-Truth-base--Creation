#!/usr/bin/env python3
"""
Test completo del sistema con todos los modelos
"""

import os
import sys

# Configurar API keys
# Load API key from environment - set in .env file
if not os.getenv('ANTHROPIC_API_KEY'):
    print("⚠️  WARNING: ANTHROPIC_API_KEY not set")
if not os.getenv('GOOGLE_API_KEY'):
    print("⚠️  WARNING: GOOGLE_API_KEY not set")

from motor_cotizacion_panelin import MotorCotizacionPanelin
from agente_orquestador_multi_modelo import AgenteOrquestadorMultiModelo

print("=" * 70)
print("🧪 TEST COMPLETO DEL SISTEMA MULTI-MODELO")
print("=" * 70)

# Test 1: Motor de cotización
print("\n1️⃣  TEST: Motor de Cotización")
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

if 'error' in cotizacion:
    print(f"❌ Error: {cotizacion['error']}")
else:
    total = cotizacion.get('costos', {}).get('total', 0)
    print(f"✅ Presupuesto generado: ${total:.2f}")
    print(f"📊 Validación autoportancia: {cotizacion.get('validacion', {}).get('cumple_autoportancia', False)}")

# Test 2: Agente Orquestador
print("\n2️⃣  TEST: Agente Orquestador Multi-Modelo")
print("-" * 70)
agente = AgenteOrquestadorMultiModelo()

print("\n📊 Modelos disponibles:")
for modelo, disponible in agente.modelos_disponibles.items():
    status = "✅" if disponible else "❌"
    print(f"   {status} {modelo.value.upper()}")

# Test 3: Probar con input real
print("\n3️⃣  TEST: Proceso Completo con Input Real")
print("-" * 70)

input_test = {
    'fila': 999,
    'fecha': '19-01',
    'cliente': 'Agustín Arbiza',
    'consulta': 'ISODEC EPS 100mm',
    'producto': 'ISODEC EPS',
    'dimensiones': '10 x 5',
    'luz': '4.5',
    'fijacion': 'Hormigón',
    'notas': 'Flete a Montevideo'
}

# Probar generación de presupuesto
print("\n🔧 Generando presupuesto...")
presupuesto = agente.generar_presupuesto(input_test)

if 'error' in presupuesto:
    print(f"   ⚠️  {presupuesto['error']}")
    # Intentar con formato diferente
    input_test['dimensiones'] = '10m x 5m'
    presupuesto = agente.generar_presupuesto(input_test)
    if 'error' not in presupuesto:
        print(f"   ✅ Presupuesto generado (con formato alternativo): ${presupuesto.get('presupuesto', {}).get('costos', {}).get('total', 0):.2f}")
else:
    total = presupuesto.get('presupuesto', {}).get('costos', {}).get('total', 0)
    print(f"   ✅ Presupuesto generado: ${total:.2f}")

# Test 4: Probar análisis con Claude (si está disponible)
from agente_orquestador_multi_modelo import RolAgente
if agente.modelos_disponibles[agente.rol_modelo[RolAgente.DIFFERENCE_ANALYZER]]:
    print("\n4️⃣  TEST: Análisis con Claude")
    print("-" * 70)
    
    # Crear comparación de prueba
    comparacion_test = {
        'presupuesto_total': 4206.56,
        'pdf_total': 4200.00,
        'diferencia': 6.56,
        'diferencia_porcentaje': 0.16,
        'coincide': True
    }
    
    print("🧠 Analizando diferencias con Claude...")
    try:
        analisis = agente.analizar_diferencias(
            comparacion_test,
            {'presupuesto': cotizacion},
            {'total': 4200.00}
        )
        print(f"   ✅ Análisis completado")
        print(f"   📊 Magnitud: {analisis.get('magnitud', 'N/A')}")
        print(f"   📊 Tipo: {analisis.get('tipo', 'N/A')}")
        if 'claude_insights' in analisis:
            print(f"   💡 Claude generó insights adicionales")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETADO")
print("=" * 70)
