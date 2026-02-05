#!/usr/bin/env python3
"""
Probar extracción con OCR en PDFs específicos
=============================================
"""

import os
import json
from pathlib import Path
from datetime import datetime
import re

from dotenv import load_dotenv
load_dotenv()
if not os.environ.get('ANTHROPIC_API_KEY') or not os.environ.get('GOOGLE_API_KEY'):
    print("⚠️  Configure ANTHROPIC_API_KEY y GOOGLE_API_KEY en .env")

from agente_analisis_inteligente import AgenteAnalisisInteligente

DROPBOX_COTIZACIONES = "/Users/matias/Library/CloudStorage/Dropbox/BMC - Uruguay/Cotizaciones"

agente = AgenteAnalisisInteligente()

print("=" * 70)
print("🔍 PRUEBA DE EXTRACCIÓN CON OCR")
print("=" * 70)

# Buscar PDFs de tamaño medio (más probables de tener texto extraíble)
dropbox_path = Path(DROPBOX_COTIZACIONES)
pdfs_para_probar = []

print("\n1️⃣  Buscando PDFs de tamaño medio (100KB - 500KB)...")
for pdf_file in dropbox_path.rglob('*.pdf'):
    try:
        size = pdf_file.stat().st_size
        nombre = pdf_file.name.upper()
        
        if any(p in nombre for p in ['ISODEC', 'ISOROOF', 'ISOPANEL', 'ISOWALL']):
            if 100000 <= size <= 500000:  # 100KB - 500KB
                pdfs_para_probar.append({
                    'path': str(pdf_file),
                    'nombre': pdf_file.name,
                    'size_kb': size / 1024
                })
                if len(pdfs_para_probar) >= 10:
                    break
    except:
        continue

if not pdfs_para_probar:
    print("   ⚠️  No se encontraron PDFs en ese rango, buscando cualquier tamaño...")
    for pdf_file in dropbox_path.rglob('*.pdf'):
        try:
            nombre = pdf_file.name.upper()
            if any(p in nombre for p in ['ISODEC', 'ISOROOF', 'ISOPANEL']):
                pdfs_para_probar.append({
                    'path': str(pdf_file),
                    'nombre': pdf_file.name,
                    'size_kb': pdf_file.stat().st_size / 1024
                })
                if len(pdfs_para_probar) >= 10:
                    break
        except:
            continue

print(f"   ✅ PDFs encontrados: {len(pdfs_para_probar)}")

resultados = []
exitosos = 0
con_total = 0
con_ocr = 0

print("\n2️⃣  Procesando PDFs con OCR...")
for idx, pdf_info in enumerate(pdfs_para_probar, 1):
    print(f"\n{'='*70}")
    print(f"📄 {idx}/{len(pdfs_para_probar)}: {pdf_info['nombre']}")
    print(f"   Tamaño: {pdf_info['size_kb']:.1f} KB")
    print(f"{'='*70}")
    
    try:
        # Extraer datos
        datos = agente.extraer_datos_pdf(pdf_info['path'])
        
        total = datos.get('total')
        metodo = datos.get('metodo_extraccion', 'PyPDF2')
        
        print(f"   ✅ Método: {metodo}")
        
        if metodo == 'OCR':
            con_ocr += 1
            print(f"   🔍 OCR utilizado (texto no encontrado con PyPDF2)")
        
        if total:
            con_total += 1
            print(f"   💰 Total extraído: ${total:.2f}")
        else:
            print(f"   ⚠️  Total: No encontrado")
        
        if datos.get('subtotal'):
            print(f"   📊 Subtotal: ${datos['subtotal']:.2f}")
        if datos.get('iva'):
            print(f"   📊 IVA: ${datos['iva']:.2f}")
        if datos.get('cliente'):
            print(f"   👤 Cliente: {datos['cliente']}")
        if datos.get('fecha'):
            print(f"   📅 Fecha: {datos['fecha']}")
        
        if datos.get('error'):
            print(f"   ⚠️  Error: {datos['error']}")
        else:
            exitosos += 1
        
        resultados.append({
            'pdf': pdf_info['nombre'],
            'path': pdf_info['path'],
            'size_kb': pdf_info['size_kb'],
            'datos': datos,
            'exitoso': not datos.get('error'),
            'tiene_total': bool(total),
            'metodo': metodo
        })
        
    except Exception as e:
        print(f"   ❌ Error procesando: {str(e)}")
        resultados.append({
            'pdf': pdf_info['nombre'],
            'path': pdf_info['path'],
            'error': str(e),
            'exitoso': False,
            'tiene_total': False
        })

print("\n" + "=" * 70)
print("📊 RESUMEN DE PRUEBA CON OCR")
print("=" * 70)
print(f"   📄 PDFs procesados: {len(resultados)}")
print(f"   ✅ Exitosos: {exitosos}/{len(resultados)}")
print(f"   💰 Con total extraído: {con_total}/{len(resultados)}")
print(f"   🔍 OCR utilizado: {con_ocr}/{len(resultados)}")
print(f"   📈 Tasa de éxito: {(exitosos/len(resultados)*100):.1f}%")
print(f"   📈 Tasa de extracción de total: {(con_total/len(resultados)*100):.1f}%")

# Guardar resultados
with open('prueba_ocr_resultados.json', 'w', encoding='utf-8') as f:
    json.dump({
        'fecha': datetime.now().isoformat(),
        'resumen': {
            'total': len(resultados),
            'exitosos': exitosos,
            'con_total': con_total,
            'con_ocr': con_ocr
        },
        'resultados': resultados
    }, f, indent=2, ensure_ascii=False, default=str)

print(f"\n💾 Resultados guardados en: prueba_ocr_resultados.json")
print("=" * 70)
