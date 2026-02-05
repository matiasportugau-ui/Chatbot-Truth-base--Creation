#!/usr/bin/env python3
"""
Cotización Completa con Panelin
=================================

Combina el motor de cotización validado con Panelin para generar
cotizaciones completas y precisas.
"""

import os
from openai import OpenAI
from pathlib import Path
import sys

from config.settings import settings

API_KEY = settings.OPENAI_API_KEY
ASSISTANT_ID = settings.OPENAI_ASSISTANT_ID


def generar_cotizacion_completa(
    cliente: str,
    producto: str,
    espesor: str,
    largo: float,
    ancho: float,
    luz: float = None,
    tipo_fijacion: str = "hormigon",
    incluir_flete: bool = False,
    destino: str = None
):
    """Genera cotización completa usando motor + Panelin"""
    
    print("=" * 70)
    print("🏗️  COTIZACIÓN COMPLETA - PANELIN")
    print("=" * 70)
    print(f"\n👤 Cliente: {cliente}")
    print(f"📋 Producto: {producto} {espesor}mm")
    print(f"📐 Dimensiones: {largo}m x {ancho}m")
    if luz:
        print(f"🔧 Luz entre apoyos: {luz}m")
    print(f"🔩 Fijación: {tipo_fijacion}")
    if incluir_flete:
        print(f"🚚 Flete: Incluido a {destino or 'Montevideo'}")
    
    # 1. Calcular con motor validado
    print("\n" + "-" * 70)
    print("📊 PASO 1: Cálculo con Motor Validado")
    print("-" * 70 + "\n")
    
    motor = MotorCotizacionPanelin()
    cotizacion = motor.calcular_cotizacion(
        producto=producto,
        espesor=espesor,
        largo=largo,
        ancho=ancho,
        tipo_fijacion=tipo_fijacion,
        luz=luz
    )
    
    if 'error' in cotizacion:
        print(f"❌ Error en motor: {cotizacion['error']}")
        return None
    
    # Mostrar cotización del motor
    print(motor.formatear_cotizacion(cotizacion))
    
    # 2. Generar presentación con Panelin
    print("\n" + "-" * 70)
    print("🤖 PASO 2: Presentación con Panelin")
    print("-" * 70 + "\n")
    
    # Preparar datos para Panelin
    datos_cotizacion = f"""
COTIZACIÓN CALCULADA:

Producto: {cotizacion['producto']} {cotizacion['espesor']}
Dimensiones: {cotizacion['dimensiones']['largo']}m x {cotizacion['dimensiones']['ancho']}m
Área: {cotizacion['dimensiones']['area']:.2f} m²

MATERIALES:
- Paneles: {cotizacion['materiales']['paneles']} unidades
- Apoyos: {cotizacion['materiales']['apoyos']}
- Varillas 3/8": {cotizacion['materiales']['varillas']} unidades
- Tuercas: {cotizacion['materiales']['tuercas']} unidades
- Tacos: {cotizacion['materiales']['tacos']} unidades
- Goteros frontal: {cotizacion['materiales']['goteros_frontal']} unidades
- Goteros lateral: {cotizacion['materiales']['goteros_lateral']} unidades
- Silicona: {cotizacion['materiales']['silicona']} pomos

COSTOS:
- Paneles: ${cotizacion['costos']['paneles']:.2f}
- Varillas: ${cotizacion['costos']['varillas']:.2f}
- Tuercas: ${cotizacion['costos']['tuercas']:.2f}
- Tacos: ${cotizacion['costos']['tacos']:.2f}
- Goteros: ${cotizacion['costos']['goteros']:.2f}
- Silicona: ${cotizacion['costos']['silicona']:.2f}
- Subtotal: ${cotizacion['costos']['subtotal']:.2f}
- IVA (22%): ${cotizacion['costos']['iva']:.2f}
- TOTAL: ${cotizacion['costos']['total']:.2f}

VALIDACIÓN:
- Autoportancia: {cotizacion['validacion']['autoportancia']}m
- Luz efectiva: {cotizacion['validacion']['luz_efectiva']}m
- {'✅ CUMPLE' if cotizacion['validacion']['cumple_autoportancia'] else '⚠️ NO CUMPLE'}
"""
    
    # Consulta para Panelin (simplificada)
    consulta_panelin = f"""Hola, soy {cliente}. 

Necesito que presentes esta cotización de forma profesional:

Producto: {cotizacion['producto']} {cotizacion['espesor']}
Dimensiones: {largo}m x {ancho}m
Luz entre apoyos: {luz or cotizacion['validacion']['luz_efectiva']}m
Fijación: {tipo_fijacion}

MATERIALES Y COSTOS:
- {cotizacion['materiales']['paneles']} paneles: ${cotizacion['costos']['paneles']:.2f}
- {cotizacion['materiales']['varillas']} varillas: ${cotizacion['costos']['varillas']:.2f}
- {cotizacion['materiales']['tuercas']} tuercas: ${cotizacion['costos']['tuercas']:.2f}
- {cotizacion['materiales']['tacos']} tacos: ${cotizacion['costos']['tacos']:.2f}
- {cotizacion['materiales']['goteros_total']} goteros: ${cotizacion['costos']['goteros']:.2f}
- {cotizacion['materiales']['silicona']} silicona: ${cotizacion['costos']['silicona']:.2f}
Subtotal: ${cotizacion['costos']['subtotal']:.2f}
IVA 22%: ${cotizacion['costos']['iva']:.2f}
TOTAL: ${cotizacion['costos']['total']:.2f}

Validación: Autoportancia {cotizacion['validacion']['autoportancia']}m {'✅ CUMPLE' if cotizacion['validacion']['cumple_autoportancia'] else '⚠️ REVISAR'}

Presenta esto como Panelin, de forma profesional y consultiva."""
    
    # Enviar a Panelin
    client = OpenAI(api_key=API_KEY)
    thread = client.beta.threads.create()
    
    print("🤖 Enviando a Panelin para presentación profesional...\n")
    
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=consulta_panelin
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )
    
    import time
    while run.status in ["queued", "in_progress"]:
        time.sleep(2)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "in_progress":
            print("   💭 Panelin está preparando la presentación...")
    
    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        respuesta = messages.data[0].content[0].text.value
        
        print("\n" + "=" * 70)
        print("📄 COTIZACIÓN PRESENTADA POR PANELIN:")
        print("=" * 70)
        print(f"\n{respuesta}\n")
        print("=" * 70)
        
        return {
            'cotizacion_motor': cotizacion,
            'presentacion_panelin': respuesta
        }
    else:
        print(f"\n❌ Error: {run.status}")
        return None


def main():
    """Ejecuta cotización completa"""
    
    # Input real: Agustín Arbiza
    resultado = generar_cotizacion_completa(
        cliente="Agustín Arbiza",
        producto="ISODEC EPS",
        espesor="100",
        largo=10.0,
        ancho=5.0,
        luz=4.5,
        tipo_fijacion="hormigon",
        incluir_flete=True,
        destino="Montevideo"
    )
    
    if resultado:
        print("\n✅ Cotización completa generada")
        print("\n📊 Resumen:")
        print(f"   Total calculado: ${resultado['cotizacion_motor']['costos']['total']:.2f}")
        print(f"   Validación técnica: {'✅ CUMPLE' if resultado['cotizacion_motor']['validacion']['cumple_autoportancia'] else '⚠️ REVISAR'}")


if __name__ == "__main__":
    main()
