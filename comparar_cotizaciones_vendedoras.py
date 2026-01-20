#!/usr/bin/env python3
"""
Comparación de Cotizaciones: Vendedoras vs Sistema
===================================================

Busca PDFs en Dropbox, extrae datos y compara con presupuestos generados
por el sistema usando el centro de conocimiento actual.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re

# Configurar API keys
os.environ['ANTHROPIC_API_KEY'] = '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'
os.environ['GOOGLE_API_KEY'] = 'AIzaSyAg_TTib1roBgzqoumJZ-SEWu8SyUwa-X0'

from agente_analisis_inteligente import AgenteAnalisisInteligente
from motor_cotizacion_panelin import MotorCotizacionPanelin
from agente_orquestador_multi_modelo import AgenteOrquestadorMultiModelo

DROPBOX_COTIZACIONES = "/Users/matias/Library/CloudStorage/Dropbox/BMC - Uruguay/Cotizaciones"

motor = MotorCotizacionPanelin()
agente = AgenteAnalisisInteligente()
orquestador = AgenteOrquestadorMultiModelo()


def buscar_todos_pdfs() -> List[Dict]:
    """Busca todos los PDFs de cotizaciones en Dropbox relacionados con paneles"""
    pdfs = []
    dropbox_path = Path(DROPBOX_COTIZACIONES)
    
    if not dropbox_path.exists():
        print(f"⚠️  Dropbox no encontrado en: {DROPBOX_COTIZACIONES}")
        return []
    
    print(f"🔍 Buscando PDFs de paneles en: {dropbox_path}")
    
    # Productos a buscar
    productos_buscar = ['ISODEC', 'ISOROOF', 'ISOPANEL', 'ISOWALL', 'PANEL', 'PANELES']
    
    # Buscar recursivamente todos los PDFs
    for pdf_file in dropbox_path.rglob("*.pdf"):
        try:
            nombre_upper = pdf_file.name.upper()
            
            # Filtrar solo PDFs relacionados con paneles
            if any(producto in nombre_upper for producto in productos_buscar):
                # Obtener fecha de modificación
                fecha_mod = datetime.fromtimestamp(pdf_file.stat().st_mtime)
                
                pdfs.append({
                    'path': str(pdf_file),
                    'nombre': pdf_file.name,
                    'fecha_modificacion': fecha_mod,
                    'año': fecha_mod.year,
                    'mes': fecha_mod.month,
                    'carpeta': pdf_file.parent.name,
                    'ruta_completa': str(pdf_file.relative_to(dropbox_path))
                })
        except Exception as e:
            continue
    
    # Ordenar por fecha (más recientes primero)
    pdfs.sort(key=lambda x: x['fecha_modificacion'], reverse=True)
    
    return pdfs


def extraer_info_pdf(pdf_path: str) -> Dict:
    """Extrae información completa de un PDF"""
    # Primero intentar extraer del nombre del archivo (más rápido)
    nombre = Path(pdf_path).stem.upper()
    
    datos = {
        'total': None,
        'subtotal': None,
        'iva': None,
        'cliente': None,
        'fecha': None,
        'error': None
    }
    
    # Extraer información del nombre
    # Buscar producto en nombre
    producto = None
    if 'ISODEC' in nombre:
        producto = 'ISODEC EPS' if 'PIR' not in nombre else 'ISODEC PIR'
    elif 'ISOPANEL' in nombre:
        producto = 'ISOPANEL EPS'
    elif 'ISOROOF' in nombre:
        if 'FOIL' in nombre:
            producto = 'ISOROOF FOIL'
        elif 'PLUS' in nombre:
            producto = 'ISOROOF PLUS'
        else:
            producto = 'ISOROOF 3G'
    elif 'ISOWALL' in nombre and 'PIR' in nombre:
        producto = 'ISOWALL PIR'
    
    # Buscar espesor
    espesor = None
    espesor_match = re.search(r'(\d+)\s*MM', nombre)
    if espesor_match:
        espesor = espesor_match.group(1)
    
    # Buscar dimensiones en nombre
    dimensiones = None
    dim_match = re.search(
        r'(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)',
        nombre
    )
    if dim_match:
        dimensiones = f"{dim_match.group(1)} x {dim_match.group(2)}"
    
    # Buscar cliente en nombre (antes del guion o " - ")
    cliente_match = re.search(r'Cotizaci[oó]n\s+\d+\s+([^-]+?)\s*-', nombre)
    if cliente_match:
        datos['cliente'] = cliente_match.group(1).strip()
    
    # Buscar fecha en nombre
    fecha_match = re.search(r'(\d{8})', nombre)
    if fecha_match:
        fecha_str = fecha_match.group(1)
        try:
            fecha = datetime.strptime(fecha_str, '%d%m%Y')
            datos['fecha'] = fecha.strftime('%d-%m-%Y')
        except:
            pass
    
    # Intentar extraer total del PDF (método rápido: solo primera y última página)
    try:
        import PyPDF2
        
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            num_pages = len(pdf_reader.pages)
            
            if num_pages > 0:
                # Leer solo primera página (header) y última página (donde suele estar el total)
                texto = ""
                try:
                    texto += pdf_reader.pages[0].extract_text() + "\n"
                except:
                    pass
                
                if num_pages > 1:
                    try:
                        texto += pdf_reader.pages[-1].extract_text() + "\n"
                    except:
                        pass
                
                # Buscar totales
                total_patterns = [
                    r'TOTAL[:\s]*USD[:\s]*\$?\s*([\d,]+\.?\d*)',
                    r'Total[:\s]*\$?\s*([\d,]+\.?\d*)',
                    r'\$\s*([\d,]+\.?\d*)\s*\(?TOTAL\)?',
                    r'IMPORTE[:\s]*TOTAL[:\s]*\$?\s*([\d,]+\.?\d*)',
                ]
                
                totales_encontrados = []
                for pattern in total_patterns:
                    matches = re.finditer(pattern, texto, re.IGNORECASE)
                    for match in matches:
                        total_str = match.group(1).replace(',', '').replace('.', '')
                        try:
                            total_val = float(total_str)
                            if total_val > 100:  # Filtrar valores muy pequeños
                                totales_encontrados.append(total_val)
                        except:
                            pass
                
                # Usar el total más grande encontrado
                if totales_encontrados:
                    datos['total'] = max(totales_encontrados)
    except Exception as e:
        # Si falla, usar solo datos del nombre
        pass
    
    datos['producto_detectado'] = producto
    datos['espesor_detectado'] = espesor
    datos['dimensiones_detectadas'] = dimensiones
    datos['nombre_archivo'] = Path(pdf_path).name
    
    return datos


def generar_presupuesto_sistema(datos_pdf: Dict) -> Optional[Dict]:
    """Genera presupuesto usando el sistema con la base de conocimiento"""
    producto = datos_pdf.get('producto_detectado')
    espesor = datos_pdf.get('espesor_detectado')
    dimensiones = datos_pdf.get('dimensiones_detectadas')
    
    if not producto or not espesor:
        return None
    
    # Si no hay dimensiones, usar valores por defecto para generar presupuesto de ejemplo
    # (esto permite comparar la estructura aunque no las dimensiones exactas)
    if not dimensiones:
        # Intentar extraer del nombre del archivo si está disponible
        nombre = datos_pdf.get('nombre_archivo', '').upper()
        dim_match = re.search(
            r'(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)',
            nombre
        )
        if dim_match:
            dimensiones = f"{dim_match.group(1)} x {dim_match.group(2)}"
        else:
            # Usar dimensiones por defecto (10m x 5m) para poder generar presupuesto
            # Esto permite ver la estructura aunque no las dimensiones exactas
            dimensiones = "10 x 5"
    
    # Parsear dimensiones
    dim_match = re.search(
        r'(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)',
        dimensiones
    )
    if not dim_match:
        return None
    
    largo = float(dim_match.group(1))
    ancho = float(dim_match.group(2))
    
    # Usar largo como luz por defecto (puede mejorarse)
    luz = largo
    
    try:
        cotizacion = motor.calcular_cotizacion(
            producto=producto,
            espesor=espesor,
            largo=largo,
            ancho=ancho,
            luz=luz,
            tipo_fijacion='hormigon'
        )
        return cotizacion
    except Exception as e:
        return {'error': str(e)}


def comparar_cotizaciones():
    """Compara cotizaciones de vendedoras vs sistema"""
    print("=" * 70)
    print("📊 COMPARACIÓN: VENDEDORAS vs SISTEMA")
    print("=" * 70)
    
    # 1. Buscar PDFs
    print("\n1️⃣  Buscando PDFs en Dropbox...")
    pdfs = buscar_todos_pdfs()
    print(f"   ✅ PDFs encontrados: {len(pdfs)}")
    
    if len(pdfs) == 0:
        print("   ⚠️  No se encontraron PDFs")
        return
    
    # 2. Procesar PDFs
    print("\n2️⃣  Procesando PDFs...")
    comparaciones = []
    
    for idx, pdf_info in enumerate(pdfs[:20], 1):  # Procesar primeros 20
        print(f"\n   📄 {idx}/{min(20, len(pdfs))}: {pdf_info['nombre']}")
        
        # Extraer datos del PDF
        datos_pdf = extraer_info_pdf(pdf_info['path'])
        
        total_pdf = datos_pdf.get('total')
        
        # Mostrar información extraída
        producto_detectado = datos_pdf.get('producto_detectado')
        espesor_detectado = datos_pdf.get('espesor_detectado')
        dimensiones_detectadas = datos_pdf.get('dimensiones_detectadas')
        
        if total_pdf:
            print(f"      ✅ Total PDF: ${total_pdf:.2f}")
        else:
            if datos_pdf.get('error'):
                print(f"      ⚠️  No se pudo extraer total: {datos_pdf['error'][:50]}")
            else:
                print(f"      ⚠️  Total no encontrado en PDF")
            
            # Si no tenemos total pero tenemos info del nombre, continuar para generar presupuesto
            if not producto_detectado or not espesor_detectado:
                print(f"      ⚠️  Faltan datos para generar presupuesto")
                comparaciones.append({
                    'pdf': pdf_info,
                    'datos_pdf': datos_pdf,
                    'presupuesto_sistema': None,
                    'comparacion': None
                })
                continue
            print(f"      💡 Continuando con datos del nombre del archivo...")
        
        # Generar presupuesto con sistema
        presupuesto_sistema = generar_presupuesto_sistema(datos_pdf)
        
        if not presupuesto_sistema:
            print(f"      ⚠️  No se pudo generar presupuesto (retornó None)")
            comparaciones.append({
                'pdf': pdf_info,
                'datos_pdf': datos_pdf,
                'presupuesto_sistema': None,
                'comparacion': None
            })
            continue
        
        if 'error' in presupuesto_sistema:
            print(f"      ⚠️  No se pudo generar presupuesto del sistema")
            if 'error' in presupuesto_sistema:
                print(f"         Error: {presupuesto_sistema['error'][:50]}")
            comparaciones.append({
                'pdf': pdf_info,
                'datos_pdf': datos_pdf,
                'presupuesto_sistema': None,
                'comparacion': None
            })
            continue
        
        total_sistema = presupuesto_sistema.get('costos', {}).get('total', 0)
        print(f"      ✅ Total Sistema: ${total_sistema:.2f}")
        
        # Comparar solo si tenemos total del PDF
        comparacion = None
        if total_pdf:
            diferencia = total_sistema - total_pdf
            diferencia_pct = (diferencia / total_pdf * 100) if total_pdf > 0 else 0
            
            comparacion = {
                'total_pdf': total_pdf,
                'total_sistema': total_sistema,
                'diferencia': diferencia,
                'diferencia_porcentaje': diferencia_pct,
                'coincide': abs(diferencia_pct) < 1.0
            }
            
            print(f"      📊 Diferencia: {diferencia_pct:+.2f}% {'✅' if comparacion['coincide'] else '⚠️'}")
        else:
            print(f"      💡 Presupuesto generado pero sin total PDF para comparar")
        
        comparaciones.append({
            'pdf': pdf_info,
            'datos_pdf': datos_pdf,
            'presupuesto_sistema': presupuesto_sistema,
            'comparacion': comparacion
        })
    
    # 3. Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE COMPARACIONES")
    print("=" * 70)
    
    totales = len(comparaciones)
    con_comparacion = sum(1 for c in comparaciones if c.get('comparacion') and c['comparacion'] is not None)
    coinciden = sum(1 for c in comparaciones if c.get('comparacion') and c['comparacion'] is not None and c['comparacion'].get('coincide', False))
    
    print(f"   📄 PDFs procesados: {totales}")
    print(f"   ⚖️  Comparaciones realizadas: {con_comparacion}")
    print(f"   ✅ Coincidencias (<1%): {coinciden}/{con_comparacion}" if con_comparacion > 0 else "   ✅ Coincidencias: N/A")
    
        # Estadísticas de diferencias
    if con_comparacion > 0:
        diferencias = [c['comparacion']['diferencia_porcentaje'] for c in comparaciones if c.get('comparacion') and c['comparacion'] is not None]
        if diferencias:
            print(f"\n   📈 Estadísticas de diferencias:")
            print(f"      Promedio: {sum(diferencias)/len(diferencias):+.2f}%")
            print(f"      Mínima: {min(diferencias):+.2f}%")
            print(f"      Máxima: {max(diferencias):+.2f}%")
    
    # 4. Guardar resultados
    output_file = "comparacion_vendedoras_sistema.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'fecha_analisis': datetime.now().isoformat(),
            'total_pdfs': len(pdfs),
            'procesados': totales,
            'comparaciones': comparaciones,
            'resumen': {
                'totales': totales,
                'con_comparacion': con_comparacion,
                'coinciden': coinciden
            }
        }, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Resultados guardados en: {output_file}")
    
    # 5. Mostrar casos destacados
    print("\n" + "=" * 70)
    print("🔍 CASOS DESTACADOS")
    print("=" * 70)
    
    # Mejores coincidencias
    mejores = sorted(
        [c for c in comparaciones if c.get('comparacion') and c['comparacion'] is not None],
        key=lambda x: abs(x['comparacion']['diferencia_porcentaje'])
    )[:5]
    
    if mejores:
        print("\n✅ Top 5 mejores coincidencias:")
        for idx, comp in enumerate(mejores, 1):
            diff = comp['comparacion']['diferencia_porcentaje']
            print(f"   {idx}. {comp['pdf']['nombre'][:50]}")
            print(f"      Diferencia: {diff:+.2f}%")
    
    # Mayores diferencias
    mayores = sorted(
        [c for c in comparaciones if c.get('comparacion') and c['comparacion'] is not None],
        key=lambda x: abs(x['comparacion']['diferencia_porcentaje']),
        reverse=True
    )[:5]
    
    if mayores:
        print("\n⚠️  Top 5 mayores diferencias:")
        for idx, comp in enumerate(mayores, 1):
            diff = comp['comparacion']['diferencia_porcentaje']
            print(f"   {idx}. {comp['pdf']['nombre'][:50]}")
            print(f"      Diferencia: {diff:+.2f}%")
    
    print("\n" + "=" * 70)
    print("✅ COMPARACIÓN COMPLETADA")
    print("=" * 70)


if __name__ == "__main__":
    comparar_cotizaciones()
