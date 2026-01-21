#!/usr/bin/env python3
"""
Probar extracción con PDFs pequeños
====================================
"""

import os
import json
from pathlib import Path
from datetime import datetime
import re

# Configurar API keys
os.environ['ANTHROPIC_API_KEY'] = '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'
os.environ['GOOGLE_API_KEY'] = 'AIzaSyAg_TTib1roBgzqoumJZ-SEWu8SyUwa-X0'

from agente_analisis_inteligente import AgenteAnalisisInteligente
from motor_cotizacion_panelin import MotorCotizacionPanelin

DROPBOX_COTIZACIONES = "/Users/matias/Library/CloudStorage/Dropbox/BMC - Uruguay/Cotizaciones"

motor = MotorCotizacionPanelin()
agente = AgenteAnalisisInteligente()

print("=" * 70)
print("🧪 PRUEBA DE EXTRACCIÓN CON PDFs PEQUEÑOS")
print("=" * 70)

# Cargar lista de PDFs pequeños
pdfs_pequenos = []
if Path('pdfs_pequenos_lista.txt').exists():
    with open('pdfs_pequenos_lista.txt', 'r', encoding='utf-8') as f:
        pdfs_pequenos = [line.strip() for line in f if line.strip()]
else:
    print("⚠️  Lista de PDFs pequeños no encontrada. Buscando...")
    dropbox_path = Path(DROPBOX_COTIZACIONES)
    pdfs_info = []
    for pdf_file in dropbox_path.rglob('*.pdf'):
        try:
            size = pdf_file.stat().st_size
            nombre = pdf_file.name.upper()
            if any(p in nombre for p in ['ISODEC', 'ISOROOF', 'ISOPANEL', 'ISOWALL']):
                pdfs_info.append({
                    'path': str(pdf_file),
                    'size_kb': size / 1024
                })
        except:
            continue
    pdfs_info.sort(key=lambda x: x['size_kb'])
    pdfs_pequenos = [p['path'] for p in pdfs_info[:20]]

print(f"\n📄 PDFs a probar: {len(pdfs_pequenos)}")

resultados = []
exitosos = 0
con_total = 0

for idx, pdf_path in enumerate(pdfs_pequenos[:10], 1):  # Probar primeros 10
    print(f"\n{'='*70}")
    print(f"📄 {idx}/10: {Path(pdf_path).name}")
    print(f"{'='*70}")
    
    try:
        # Extraer datos
        datos = agente.extraer_datos_pdf(pdf_path)
        
        total = datos.get('total')
        metodo = datos.get('metodo_extraccion', 'PyPDF2')
        
        print(f"   Método: {metodo}")
        print(f"   Total extraído: ${total:.2f}" if total else "   Total: No encontrado")
        print(f"   Subtotal: ${datos.get('subtotal', 0):.2f}" if datos.get('subtotal') else "   Subtotal: No encontrado")
        print(f"   IVA: ${datos.get('iva', 0):.2f}" if datos.get('iva') else "   IVA: No encontrado")
        
        if datos.get('error'):
            print(f"   ⚠️  Error: {datos['error']}")
        else:
            exitosos += 1
            if total:
                con_total += 1
        
        resultados.append({
            'pdf': Path(pdf_path).name,
            'path': pdf_path,
            'datos': datos,
            'exitoso': not datos.get('error'),
            'tiene_total': bool(total)
        })
        
    except Exception as e:
        print(f"   ❌ Error procesando: {str(e)}")
        resultados.append({
            'pdf': Path(pdf_path).name,
            'path': pdf_path,
            'error': str(e),
            'exitoso': False,
            'tiene_total': False
        })

print("\n" + "=" * 70)
print("📊 RESUMEN DE PRUEBA")
print("=" * 70)
print(f"   📄 PDFs procesados: {len(resultados)}")
print(f"   ✅ Exitosos: {exitosos}/{len(resultados)}")
print(f"   💰 Con total extraído: {con_total}/{len(resultados)}")
print(f"   📈 Tasa de éxito: {(exitosos/len(resultados)*100):.1f}%")
print(f"   📈 Tasa de extracción de total: {(con_total/len(resultados)*100):.1f}%")

# Guardar resultados
with open('prueba_pdfs_pequenos_resultados.json', 'w', encoding='utf-8') as f:
    json.dump({
        'fecha': datetime.now().isoformat(),
        'resumen': {
            'total': len(resultados),
            'exitosos': exitosos,
            'con_total': con_total
        },
        'resultados': resultados
    }, f, indent=2, ensure_ascii=False, default=str)

print(f"\n💾 Resultados guardados en: prueba_pdfs_pequenos_resultados.json")
print("=" * 70)
