#!/usr/bin/env python3
"""
Agente de Análisis Inteligente de Cotizaciones
===============================================

Agente que:
1. Revisa inputs de clientes
2. Genera presupuestos usando motor validado
3. Encuentra PDFs reales generados
4. Compara resultados
5. Analiza diferencias
6. Aprende e incorpora conocimiento
"""

import json
import csv
import re
import os
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import sys

# Importar motor
sys.path.insert(0, str(Path(__file__).parent))
from motor_cotizacion_panelin import MotorCotizacionPanelin

# Rutas
CSV_INPUTS = "/Volumes/My Passport for Mac/2.0 -  Administrador de Cotizaciones  - Admin..csv"
DROPBOX_COTIZACIONES = "/Users/matias/Library/CloudStorage/Dropbox/BMC - Uruguay/Cotizaciones"

motor = MotorCotizacionPanelin()


class AgenteAnalisisInteligente:
    """Agente que analiza, compara y aprende de cotizaciones"""
    
    def __init__(self):
        self.motor = motor
        self.inputs = []
        self.cotizaciones_reales = []
        self.comparaciones = []
        self.lecciones_aprendidas = []
        
    def revisar_inputs(self, cliente: str = None, fecha: str = None, producto: str = None) -> List[Dict]:
        """Revisa inputs del CSV con filtros opcionales"""
        inputs = []
        
        try:
            with open(CSV_INPUTS, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) < 3:
                    return []
                
                headers = [h.strip() for h in rows[1]]
                header_map = {h: i for i, h in enumerate(headers)}
                
                for idx, row in enumerate(rows[2:], start=3):
                    if len(row) < len(headers):
                        row.extend([''] * (len(headers) - len(row)))
                    
                    def get_value(key, default=''):
                        col_idx = header_map.get(key, -1)
                        return row[col_idx].strip() if col_idx >= 0 and col_idx < len(row) else default
                    
                    input_data = {
                        'fila': idx,
                        'fecha': get_value('Fecha'),
                        'cliente': get_value('Cliente'),
                        'consulta': get_value('Consulta'),
                        'producto': get_value('Producto'),
                        'dimensiones': get_value('Dimensiones'),
                        'luz': get_value('Luz'),
                        'fijacion': get_value('Fijación'),
                        'notas': get_value('Notas')
                    }
                    
                    # Aplicar filtros
                    if cliente and cliente.lower() not in input_data['cliente'].lower():
                        continue
                    if producto and producto.lower() not in input_data['consulta'].lower():
                        continue
                    
                    inputs.append(input_data)
        except Exception as e:
            print(f"⚠️  Error leyendo CSV: {e}")
        
        self.inputs = inputs
        return inputs
    
    def generar_presupuesto(self, input_data: Dict) -> Dict:
        """Genera presupuesto usando el motor validado"""
        try:
            # Extraer parámetros del input
            consulta = input_data.get('consulta', '').upper()
            dimensiones = input_data.get('dimensiones', '')
            luz_str = input_data.get('luz', '')
            
            # Identificar producto
            producto = None
            espesor = None
            
            if 'ISODEC' in consulta:
                if 'PIR' in consulta:
                    producto = "ISODEC PIR"
                else:
                    producto = "ISODEC EPS"
            elif 'ISOPANEL' in consulta:
                producto = "ISOPANEL EPS"
            elif 'ISOROOF' in consulta:
                producto = "ISOROOF 3G"
            elif 'ISOWALL' in consulta and 'PIR' in consulta:
                producto = "ISOWALL PIR"
            
            # Extraer espesor
            espesor_match = re.search(r'(\d+)\s*mm', consulta)
            if espesor_match:
                espesor = espesor_match.group(1)
            
            # Extraer dimensiones
            largo = None
            ancho = None
            if dimensiones:
                # Intentar múltiples formatos: "10 x 5", "10x5", "10m x 5m", "10metros x 5metros", etc.
                # Regex unificado que soporta unidades opcionales (m, metro, metros)
                # Patrón corregido: (?:m|metro|metros)? hace opcional el grupo completo
                dim_match = re.search(
                    r'(\d+(?:\.\d+)?)\s*(?:m|metro|metros)?\s*[xX×]\s*(\d+(?:\.\d+)?)\s*(?:m|metro|metros)?',
                    dimensiones,
                    re.IGNORECASE
                )
                if dim_match:
                    largo = float(dim_match.group(1))
                    ancho = float(dim_match.group(2))
            
            # Extraer luz
            luz = None
            if luz_str:
                luz_match = re.search(r'(\d+(?:\.\d+)?)', luz_str)
                if luz_match:
                    luz = float(luz_match.group(1))
            
            # Tipo de fijación
            tipo_fijacion = "hormigon"
            if 'metal' in consulta.lower() or 'metálic' in consulta.lower():
                tipo_fijacion = "metal"
            elif 'madera' in consulta.lower():
                tipo_fijacion = "madera"
            
            if not producto or not espesor or not largo or not ancho:
                return {
                    'error': 'Faltan parámetros para generar presupuesto',
                    'input': input_data
                }
            
            # Generar cotización
            cotizacion = self.motor.calcular_cotizacion(
                producto=producto,
                espesor=espesor,
                largo=largo,
                ancho=ancho,
                luz=luz if luz else largo,  # Si no hay luz, usar largo
                tipo_fijacion=tipo_fijacion
            )
            
            return {
                'input': input_data,
                'presupuesto': cotizacion,
                'parametros_usados': {
                    'producto': producto,
                    'espesor': espesor,
                    'largo': largo,
                    'ancho': ancho,
                    'luz': luz if luz else largo,
                    'tipo_fijacion': tipo_fijacion
                }
            }
        except Exception as e:
            return {
                'error': str(e),
                'input': input_data
            }
    
    def buscar_pdf_cotizacion(self, input_data: Dict) -> Optional[Dict]:
        """Busca PDF de cotización real relacionado con el input"""
        cliente = input_data.get('cliente', '').strip()
        fecha_str = input_data.get('fecha', '').strip()
        consulta = input_data.get('consulta', '').upper()
        
        if not cliente:
            return None
        
        # Parsear fecha
        fecha_input = self._parsear_fecha(fecha_str)
        if not fecha_input:
            return None
        
        # Buscar en Dropbox
        try:
            dropbox_path = Path(DROPBOX_COTIZACIONES)
            if not dropbox_path.exists():
                return None
            
            mejor_match = None
            mejor_score = 0
            
            # Buscar por año/mes
            año = fecha_input.year
            mes = fecha_input.month
            
            # Buscar en carpetas de año/mes
            año_path = dropbox_path / str(año)
            if año_path.exists():
                mes_path = año_path / f"{mes:02d}"
                if not mes_path.exists():
                    # Buscar carpetas que contengan el mes
                    for subdir in año_path.iterdir():
                        if subdir.is_dir() and str(mes) in subdir.name:
                            mes_path = subdir
                            break
                
                if mes_path.exists():
                    # Buscar PDFs
                    for pdf_file in mes_path.rglob("*.pdf"):
                        nombre = pdf_file.stem.upper()
                        
                        # Calcular score de correlación
                        score = 0
                        
                        # Coincidencia de cliente
                        palabras_cliente = cliente.upper().split()
                        for palabra in palabras_cliente:
                            if len(palabra) > 3 and palabra in nombre:
                                score += 10
                        
                        # Coincidencia de producto
                        if 'ISODEC' in consulta and 'ISODEC' in nombre:
                            score += 5
                        if 'ISOPANEL' in consulta and 'ISOPANEL' in nombre:
                            score += 5
                        if 'ISOROOF' in consulta and 'ISOROOF' in nombre:
                            score += 5
                        
                        # Coincidencia de fecha (buscar fecha en nombre)
                        fecha_nombre = self._extraer_fecha_nombre(nombre)
                        if fecha_nombre:
                            diff_dias = abs((fecha_nombre - fecha_input.date()).days)
                            if diff_dias <= 7:  # Dentro de 7 días
                                score += 20 - diff_dias
                        
                        if score > mejor_score:
                            mejor_score = score
                            mejor_match = {
                                'path': str(pdf_file),
                                'nombre': pdf_file.name,
                                'score': score,
                                'fecha_encontrada': fecha_nombre.isoformat() if fecha_nombre else None
                            }
            
            return mejor_match if mejor_score >= 10 else None
            
        except Exception as e:
            print(f"⚠️  Error buscando PDF: {e}")
            return None
    
    def extraer_datos_pdf(self, pdf_path: str) -> Dict:
        """Extrae datos de un PDF de cotización"""
        datos = {
            'total': None,
            'subtotal': None,
            'iva': None,
            'productos': [],
            'fecha': None,
            'cliente': None,
            'error': None
        }
        
        try:
            import PyPDF2
            import signal
            
            texto = ''
            usar_ocr = False
            
            # Intentar lectura normal con timeout corto
            try:
                def timeout_handler(signum, frame):
                    raise TimeoutError("Timeout leyendo PDF")
                
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(5)  # 5 segundos timeout (muy corto)
                
                try:
                    try:
                        with open(pdf_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            
                            # Intentar solo primera página primero (más rápido)
                            try:
                                if len(pdf_reader.pages) > 0:
                                    texto = pdf_reader.pages[0].extract_text() + '\n'
                            except:
                                pass
                            
                            # Si no hay texto suficiente, intentar última página
                            if len(texto.strip()) < 50 and len(pdf_reader.pages) > 1:
                                try:
                                    texto += pdf_reader.pages[-1].extract_text() + '\n'
                                except:
                                    pass
                        
                    except (TimeoutError, Exception):
                        # Si falla la lectura normal, usar OCR
                        usar_ocr = True
                        datos['error'] = "Timeout leyendo PDF, intentando OCR"
                    finally:
                        # Siempre cancelar el alarm, incluso si hay excepciones
                        signal.alarm(0)
                    
                except Exception as e:
                    # Si falla la configuración del signal o algo más, cancelar alarm y usar OCR
                    signal.alarm(0)  # Asegurar que el alarm se cancele
                    usar_ocr = True
                    datos['error'] = f"Error leyendo PDF: {str(e)}, intentando OCR"
            except Exception as e:
                # Si falla completamente (incluyendo signal.signal o signal.alarm), intentar OCR
                # Intentar cancelar alarm por si acaso fue configurado
                try:
                    signal.alarm(0)
                except:
                    pass  # Si falla, no hay nada que hacer
                usar_ocr = True
                datos['error'] = f"Error leyendo PDF: {str(e)}, intentando OCR"
            
            # Si el texto está vacío o es muy corto, o si hubo timeout, intentar OCR
            if usar_ocr or len(texto.strip()) < 50:
                try:
                    # Intentar OCR con pdf2image y pytesseract
                    from pdf2image import convert_from_path
                    import pytesseract
                    
                    # Convertir primera página a imagen (solo si no hay texto)
                    images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=200)
                    if images:
                        texto_ocr = pytesseract.image_to_string(images[0], lang='spa')
                        if len(texto_ocr.strip()) > len(texto.strip()):
                            texto = texto_ocr
                            datos['metodo_extraccion'] = 'OCR'
                            # Limpiar error si OCR funcionó
                            if datos.get('error') and 'OCR' in datos['error']:
                                datos['error'] = None
                except ImportError:
                    # OCR no disponible
                    if not texto:
                        datos['error'] = "OCR no disponible y texto no encontrado"
                except Exception as e:
                    # Error en OCR
                    if not texto:
                        datos['error'] = f"Error en OCR: {str(e)}"
                
                # Buscar totales
                # Patrones comunes: "TOTAL", "Total USD", "$ XXXX", etc.
                total_patterns = [
                    r'TOTAL[:\s]*USD[:\s]*\$?\s*([\d,]+\.?\d*)',
                    r'Total[:\s]*\$?\s*([\d,]+\.?\d*)',
                    r'\$\s*([\d,]+\.?\d*)\s*\(?TOTAL\)?',
                    r'IMPORTE[:\s]*TOTAL[:\s]*\$?\s*([\d,]+\.?\d*)',
                    r'TOTAL[:\s]*\$?\s*([\d,]+\.?\d*)',
                ]
                
                # Buscar todos los totales posibles y usar el más grande
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
                
                if totales_encontrados:
                    datos['total'] = max(totales_encontrados)  # Usar el más grande
                
                # Buscar subtotal
                subtotal_patterns = [
                    r'SUBTOTAL[:\s]*USD[:\s]*\$?\s*([\d,]+\.?\d*)',
                    r'Subtotal[:\s]*\$?\s*([\d,]+\.?\d*)',
                ]
                
                for pattern in subtotal_patterns:
                    match = re.search(pattern, texto, re.IGNORECASE)
                    if match:
                        subtotal_str = match.group(1).replace(',', '')
                        try:
                            datos['subtotal'] = float(subtotal_str)
                            break
                        except:
                            pass
                
                # Buscar IVA
                iva_patterns = [
                    r'IVA[:\s]*\(?22%?\)?[:\s]*\$?\s*([\d,]+\.?\d*)',
                    r'IVA[:\s]*\$?\s*([\d,]+\.?\d*)',
                ]
                
                for pattern in iva_patterns:
                    match = re.search(pattern, texto, re.IGNORECASE)
                    if match:
                        iva_str = match.group(1).replace(',', '')
                        try:
                            datos['iva'] = float(iva_str)
                            break
                        except:
                            pass
                
                # Buscar cliente
                cliente_patterns = [
                    r'Cliente[:\s]+([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ\s]+)',
                    r'COTIZACIÓN[:\s]+PARA[:\s]+([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ\s]+)',
                ]
                
                for pattern in cliente_patterns:
                    match = re.search(pattern, texto)
                    if match:
                        datos['cliente'] = match.group(1).strip()
                        break
                
                # Buscar fecha
                fecha_patterns = [
                    r'Fecha[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                ]
                
                for pattern in fecha_patterns:
                    match = re.search(pattern, texto)
                    if match:
                        fecha_str = match.group(1)
                        try:
                            datos['fecha'] = fecha_str
                            break
                        except:
                            pass
                
        except ImportError:
            datos['error'] = "PyPDF2 no instalado. Ejecuta: pip install PyPDF2"
        except Exception as e:
            datos['error'] = f"Error extrayendo: {str(e)}"
        
        return datos
    
    def comparar_resultados(self, presupuesto: Dict, pdf_real: Dict) -> Dict:
        """Compara presupuesto generado vs PDF real"""
        if 'error' in presupuesto or 'error' in pdf_real:
            return {
                'error': 'No se puede comparar: hay errores en los datos',
                'presupuesto_error': presupuesto.get('error'),
                'pdf_error': pdf_real.get('error')
            }
        
        presupuesto_total = presupuesto.get('presupuesto', {}).get('costos', {}).get('total', 0)
        pdf_total = pdf_real.get('total', 0)
        
        if not presupuesto_total or not pdf_total:
            return {
                'error': 'No se encontraron totales para comparar',
                'presupuesto_total': presupuesto_total,
                'pdf_total': pdf_total
            }
        
        diferencia = presupuesto_total - pdf_total
        diferencia_porcentaje = (diferencia / pdf_total * 100) if pdf_total > 0 else 0
        
        # Analizar diferencias
        analisis = self._analizar_diferencias(presupuesto, pdf_real, diferencia, diferencia_porcentaje)
        
        return {
            'presupuesto_total': presupuesto_total,
            'pdf_total': pdf_total,
            'diferencia': diferencia,
            'diferencia_porcentaje': diferencia_porcentaje,
            'analisis': analisis,
            'coincide': abs(diferencia_porcentaje) < 1.0  # Menos del 1% de diferencia
        }
    
    def _analizar_diferencias(self, presupuesto: Dict, pdf_real: Dict, diferencia: float, diferencia_pct: float) -> Dict:
        """Analiza las diferencias y trata de entenderlas"""
        analisis = {
            'magnitud': 'insignificante' if abs(diferencia_pct) < 1 else 'pequeña' if abs(diferencia_pct) < 5 else 'moderada' if abs(diferencia_pct) < 15 else 'grande',
            'tipo': 'sobreestimado' if diferencia > 0 else 'subestimado',
            'posibles_causas': [],
            'recomendaciones': []
        }
        
        # Analizar posibles causas
        input_data = presupuesto.get('input', {})
        parametros = presupuesto.get('parametros_usados', {})
        presupuesto_detalle = presupuesto.get('presupuesto', {})
        
        # Causa 1: Diferencia en materiales
        materiales_presupuesto = presupuesto_detalle.get('materiales', {})
        
        # Causa 2: Diferencia en precios
        if abs(diferencia_pct) > 5:
            analisis['posibles_causas'].append(
                f"Posible diferencia en precios unitarios (diferencia: {diferencia_pct:.1f}%)"
            )
        
        # Causa 3: Materiales adicionales no considerados
        if diferencia < 0:  # Subestimado
            analisis['posibles_causas'].append(
                "El presupuesto puede no incluir todos los materiales necesarios"
            )
            analisis['recomendaciones'].append(
                "Revisar si hay materiales adicionales en el PDF que no se consideraron"
            )
        
        # Causa 4: Flete o servicios adicionales
        consulta = input_data.get('consulta', '').upper()
        if 'FLETE' in consulta or 'ENVÍO' in consulta:
            analisis['posibles_causas'].append(
                "Flete o envío puede estar incluido en el PDF pero no en el presupuesto"
            )
        
        # Causa 5: Descuentos o ajustes
        if diferencia > 0:  # Sobreestimado
            analisis['posibles_causas'].append(
                "Puede haber descuentos aplicados en el PDF que no se consideraron"
            )
            analisis['recomendaciones'].append(
                "Revisar políticas de descuento para este tipo de cliente/proyecto"
            )
        
        return analisis
    
    def aprender_de_diferencias(self, comparacion: Dict) -> Dict:
        """Aprende de las diferencias y genera lecciones"""
        leccion = {
            'timestamp': datetime.now().isoformat(),
            'diferencia_porcentaje': comparacion.get('diferencia_porcentaje', 0),
            'analisis': comparacion.get('analisis', {}),
            'lecciones': [],
            'sugerencias_mejora': []
        }
        
        diferencia_pct = abs(comparacion.get('diferencia_porcentaje', 0))
        
        if diferencia_pct > 15:
            leccion['lecciones'].append(
                "Diferencia significativa detectada - requiere revisión de lógica de cotización"
            )
            leccion['sugerencias_mejora'].append(
                "Revisar fórmulas de cálculo y validar contra más casos reales"
            )
        elif diferencia_pct > 5:
            leccion['lecciones'].append(
                "Diferencia moderada - puede ser por materiales adicionales o ajustes comerciales"
            )
            leccion['sugerencias_mejora'].append(
                "Considerar agregar factores de ajuste para casos similares"
            )
        elif diferencia_pct > 1:
            leccion['lecciones'].append(
                "Diferencia pequeña - probablemente por redondeos o ajustes menores"
            )
        else:
            leccion['lecciones'].append(
                "Excelente coincidencia - la lógica de cotización es precisa"
            )
        
        # Agregar lecciones específicas del análisis
        analisis = comparacion.get('analisis', {})
        causas = analisis.get('posibles_causas', [])
        recomendaciones = analisis.get('recomendaciones', [])
        
        leccion['lecciones'].extend(causas)
        leccion['sugerencias_mejora'].extend(recomendaciones)
        
        self.lecciones_aprendidas.append(leccion)
        return leccion
    
    def proceso_completo(self, cliente: str = None, producto: str = None, limite: int = 10) -> Dict:
        """Proceso completo: revisar, generar, buscar, comparar, aprender"""
        print("=" * 70)
        print("🤖 AGENTE DE ANÁLISIS INTELIGENTE")
        print("=" * 70)
        
        # 1. Revisar inputs
        print("\n📋 Paso 1: Revisando inputs...")
        inputs = self.revisar_inputs(cliente=cliente, producto=producto)
        print(f"   ✅ Encontrados {len(inputs)} inputs")
        
        if limite:
            inputs = inputs[:limite]
        
        resultados = []
        
        for idx, input_data in enumerate(inputs, 1):
            print(f"\n{'='*70}")
            print(f"📊 Procesando input {idx}/{len(inputs)}: {input_data.get('cliente', 'N/A')}")
            print(f"{'='*70}")
            
            # 2. Generar presupuesto
            print("\n🔧 Paso 2: Generando presupuesto...")
            presupuesto = self.generar_presupuesto(input_data)
            
            if 'error' in presupuesto:
                print(f"   ⚠️  Error: {presupuesto['error']}")
                resultados.append({
                    'input': input_data,
                    'presupuesto': None,
                    'pdf_real': None,
                    'comparacion': None,
                    'leccion': None
                })
                continue
            
            print(f"   ✅ Presupuesto generado: ${presupuesto.get('presupuesto', {}).get('costos', {}).get('total', 0):.2f}")
            
            # 3. Buscar PDF real
            print("\n🔍 Paso 3: Buscando PDF real...")
            pdf_match = self.buscar_pdf_cotizacion(input_data)
            
            if not pdf_match:
                print("   ⚠️  No se encontró PDF relacionado")
                resultados.append({
                    'input': input_data,
                    'presupuesto': presupuesto,
                    'pdf_real': None,
                    'comparacion': None,
                    'leccion': None
                })
                continue
            
            print(f"   ✅ PDF encontrado: {pdf_match['nombre']} (score: {pdf_match['score']})")
            
            # 4. Extraer datos del PDF
            print("\n📄 Paso 4: Extrayendo datos del PDF...")
            pdf_datos = self.extraer_datos_pdf(pdf_match['path'])
            
            if pdf_datos.get('error'):
                print(f"   ⚠️  Error extrayendo: {pdf_datos['error']}")
                resultados.append({
                    'input': input_data,
                    'presupuesto': presupuesto,
                    'pdf_real': {'error': pdf_datos['error'], 'path': pdf_match['path']},
                    'comparacion': None,
                    'leccion': None
                })
                continue
            
            print(f"   ✅ Total extraído: ${pdf_datos.get('total', 0):.2f}")
            
            # 5. Comparar resultados
            print("\n⚖️  Paso 5: Comparando resultados...")
            comparacion = self.comparar_resultados(presupuesto, pdf_datos)
            
            if 'error' in comparacion:
                print(f"   ⚠️  Error comparando: {comparacion['error']}")
            else:
                diferencia_pct = comparacion.get('diferencia_porcentaje', 0)
                print(f"   📊 Diferencia: {diferencia_pct:+.2f}%")
                print(f"   {'✅ Coincide' if comparacion.get('coincide') else '⚠️  No coincide'}")
            
            # 6. Aprender
            print("\n🧠 Paso 6: Analizando y aprendiendo...")
            leccion = self.aprender_de_diferencias(comparacion) if 'error' not in comparacion else None
            
            if leccion:
                print(f"   ✅ Lecciones aprendidas: {len(leccion.get('lecciones', []))}")
            
            resultados.append({
                'input': input_data,
                'presupuesto': presupuesto,
                'pdf_real': {**pdf_datos, 'path': pdf_match['path'], 'nombre': pdf_match['nombre']},
                'comparacion': comparacion,
                'leccion': leccion
            })
        
        # Resumen final
        print(f"\n{'='*70}")
        print("📊 RESUMEN FINAL")
        print(f"{'='*70}")
        
        totales = len(resultados)
        con_pdf = sum(1 for r in resultados if r.get('pdf_real') and 'error' not in r.get('pdf_real', {}))
        comparados = sum(1 for r in resultados if r.get('comparacion') and 'error' not in r.get('comparacion', {}))
        coinciden = sum(1 for r in resultados if r.get('comparacion', {}).get('coincide', False))
        
        print(f"   📋 Inputs procesados: {totales}")
        print(f"   📄 PDFs encontrados: {con_pdf}")
        print(f"   ⚖️  Comparaciones realizadas: {comparados}")
        print(f"   ✅ Coincidencias: {coinciden}/{comparados}" if comparados > 0 else "   ✅ Coincidencias: N/A")
        
        return {
            'resultados': resultados,
            'resumen': {
                'totales': totales,
                'con_pdf': con_pdf,
                'comparados': comparados,
                'coinciden': coinciden
            },
            'lecciones_aprendidas': self.lecciones_aprendidas
        }
    
    def _parsear_fecha(self, fecha_str: str) -> Optional[datetime]:
        """Parsea fecha del formato DD-MM o similar"""
        if not fecha_str or fecha_str.strip() == '':
            return None
        
        fecha_str = fecha_str.strip()
        
        try:
            fecha_str = fecha_str.replace(' ', '')
            match = re.match(r'(\d{1,2})-(\d{1,2})', fecha_str)
            if match:
                dia = int(match.group(1))
                mes = int(match.group(2))
                
                if 1 <= mes <= 12 and 1 <= dia <= 31:
                    año = 2025
                    try:
                        return datetime(año, mes, dia)
                    except ValueError:
                        return None
        except Exception:
            pass
        
        return None
    
    def _extraer_fecha_nombre(self, nombre: str) -> Optional[date]:
        """Extrae fecha del nombre del archivo"""
        # Buscar patrones de fecha: DD-MM-YYYY, DD-MM-YY, etc.
        patterns = [
            r'(\d{1,2})[-_](\d{1,2})[-_](\d{2,4})',
            r'(\d{4})[-_](\d{1,2})[-_](\d{1,2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, nombre)
            if match:
                try:
                    if len(match.group(3)) == 4:  # YYYY-MM-DD
                        año = int(match.group(1))
                        mes = int(match.group(2))
                        dia = int(match.group(3))
                    else:  # DD-MM-YY
                        dia = int(match.group(1))
                        mes = int(match.group(2))
                        año = int(match.group(3))
                        if año < 100:
                            año += 2000
                    
                    return date(año, mes, dia)
                except:
                    pass
        
        return None


# ============================================================================
# FUNCIÓN PARA AGENTES DE IA (Function Calling)
# ============================================================================

def get_analisis_function_schema() -> Dict:
    """Schema de función para análisis inteligente"""
    return {
        "name": "analizar_cotizacion_completa",
        "description": "Analiza un input de cliente: genera presupuesto, busca PDF real, compara resultados y aprende de diferencias. Incluye revisión de inputs, generación de presupuesto usando motor validado, búsqueda de PDFs en Dropbox, extracción de datos, comparación y análisis de diferencias.",
        "parameters": {
            "type": "object",
            "properties": {
                "cliente": {
                    "type": "string",
                    "description": "Nombre del cliente (opcional, para filtrar)"
                },
                "producto": {
                    "type": "string",
                    "description": "Producto a buscar (opcional, ej: 'ISODEC', 'ISOROOF')"
                },
                "limite": {
                    "type": "integer",
                    "description": "Número máximo de inputs a procesar (default: 10)",
                    "default": 10
                }
            }
        }
    }


def analizar_cotizacion_completa(cliente: str = None, producto: str = None, limite: int = 10) -> Dict:
    """Función para agentes de IA"""
    agente = AgenteAnalisisInteligente()
    resultado = agente.proceso_completo(cliente=cliente, producto=producto, limite=limite)
    return resultado


if __name__ == "__main__":
    import sys
    
    cliente = sys.argv[1] if len(sys.argv) > 1 else None
    producto = sys.argv[2] if len(sys.argv) > 2 else None
    
    agente = AgenteAnalisisInteligente()
    resultado = agente.proceso_completo(cliente=cliente, producto=producto, limite=10)
    
    # Guardar resultado
    output_file = "analisis_inteligente_resultado.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Resultado guardado en: {output_file}")