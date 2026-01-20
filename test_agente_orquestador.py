#!/usr/bin/env python3
"""
Test del Agente Orquestador con caso real
"""

from agente_orquestador_multi_modelo import AgenteOrquestadorMultiModelo
import json

# Caso de prueba real: Agustín Arbiza - ISODEC EPS 100mm
input_test = {
    'fila': 999,
    'fecha': '19-01',
    'cliente': 'Agustín Arbiza',
    'consulta': 'ISODEC EPS 100mm / Ver plano / Completo (babetas) + Flete',
    'producto': 'ISODEC EPS',
    'dimensiones': '10 x 5',
    'luz': '4.5',
    'fijacion': 'Hormigón',
    'notas': 'Flete a Montevideo'
}

print("=" * 70)
print("🧪 TEST DEL AGENTE ORQUESTADOR")
print("=" * 70)
print(f"\n📋 Caso de prueba:")
print(f"   Cliente: {input_test['cliente']}")
print(f"   Producto: {input_test['consulta']}")
print(f"   Dimensiones: {input_test['dimensiones']}")
print(f"   Luz: {input_test['luz']}m")
print()

agente = AgenteOrquestadorMultiModelo()

# Probar cada paso individualmente
print("=" * 70)
print("1️⃣  GENERAR PRESUPUESTO")
print("=" * 70)
presupuesto = agente.generar_presupuesto(input_test)
if 'error' in presupuesto:
    print(f"   ❌ Error: {presupuesto['error']}")
else:
    total = presupuesto.get('presupuesto', {}).get('costos', {}).get('total', 0)
    print(f"   ✅ Presupuesto generado: ${total:.2f}")
    print(f"   📊 Producto: {presupuesto.get('parametros_usados', {}).get('producto', 'N/A')}")
    print(f"   📏 Dimensiones: {presupuesto.get('parametros_usados', {}).get('largo', 0)}m x {presupuesto.get('parametros_usados', {}).get('ancho', 0)}m")

print("\n" + "=" * 70)
print("2️⃣  BUSCAR PDF")
print("=" * 70)
pdf_match = agente.buscar_pdf(input_test)
if pdf_match:
    print(f"   ✅ PDF encontrado: {pdf_match['nombre']}")
    print(f"   📊 Score: {pdf_match['score']}")
else:
    print("   ⚠️  No se encontró PDF relacionado")

if pdf_match:
    print("\n" + "=" * 70)
    print("3️⃣  EXTRAER DATOS DEL PDF")
    print("=" * 70)
    pdf_datos = agente.extraer_datos_pdf(pdf_match['path'])
    if pdf_datos.get('error'):
        print(f"   ⚠️  Error: {pdf_datos['error']}")
    else:
        print(f"   ✅ Total extraído: ${pdf_datos.get('total', 0):.2f}")
        print(f"   📊 Subtotal: ${pdf_datos.get('subtotal', 0):.2f}")
        print(f"   📊 IVA: ${pdf_datos.get('iva', 0):.2f}")
    
    if not pdf_datos.get('error') and 'error' not in presupuesto:
        print("\n" + "=" * 70)
        print("4️⃣  COMPARAR RESULTADOS")
        print("=" * 70)
        comparacion = agente.comparar_resultados(presupuesto, pdf_datos)
        if 'error' in comparacion:
            print(f"   ⚠️  Error: {comparacion['error']}")
        else:
            diff_pct = comparacion.get('diferencia_porcentaje', 0)
            coincide = comparacion.get('coincide', False)
            print(f"   📊 Presupuesto: ${comparacion.get('presupuesto_total', 0):.2f}")
            print(f"   📄 PDF Real: ${comparacion.get('pdf_total', 0):.2f}")
            print(f"   📈 Diferencia: {diff_pct:+.2f}%")
            print(f"   {'✅ Coincide' if coincide else '⚠️  No coincide'}")
        
        if 'error' not in comparacion:
            print("\n" + "=" * 70)
            print("5️⃣  ANALIZAR DIFERENCIAS")
            print("=" * 70)
            analisis = agente.analizar_diferencias(comparacion, presupuesto, pdf_datos)
            print(f"   📊 Magnitud: {analisis.get('magnitud', 'N/A')}")
            print(f"   📊 Tipo: {analisis.get('tipo', 'N/A')}")
            print(f"   📋 Causas identificadas: {len(analisis.get('posibles_causas', []))}")
            print(f"   💡 Recomendaciones: {len(analisis.get('recomendaciones', []))}")
            
            print("\n" + "=" * 70)
            print("6️⃣  APRENDER")
            print("=" * 70)
            leccion = agente.aprender_de_diferencias(comparacion)
            print(f"   📚 Lecciones: {len(leccion.get('lecciones', []))}")
            print(f"   💡 Sugerencias: {len(leccion.get('sugerencias_mejora', []))}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETADO")
print("=" * 70)
