#!/usr/bin/env python3
"""
Análisis de Cotizaciones 2025
=============================

Analiza inputs de clientes vs cotizaciones generadas, mes por mes desde hoy hacia atrás.
Genera presupuestos usando la base de conocimiento y compara diferencias.
"""

import csv
import json
import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import math

# Rutas
CSV_INPUTS = "/Volumes/My Passport for Mac/2.0 -  Administrador de Cotizaciones  - Admin..csv"
DROPBOX_COTIZACIONES = "/Users/matias/Library/CloudStorage/Dropbox/BMC - Uruguay/Cotizaciones"
BASE_CONOCIMIENTO = "BMC_Base_Conocimiento_GPT-2.json"


class AnalizadorCotizaciones:
    def __init__(self):
        self.base_conocimiento = self._cargar_base_conocimiento()
        self.inputs = []
        self.cotizaciones_reales = []
        self.resultados = []
        
    def _cargar_base_conocimiento(self) -> Dict:
        """Carga la base de conocimiento"""
        try:
            with open(BASE_CONOCIMIENTO, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error cargando base de conocimiento: {e}")
            return {}
    
    def _parsear_fecha(self, fecha_str: str) -> Optional[datetime]:
        """Parsea fecha del formato DD-MM o similar"""
        if not fecha_str or fecha_str.strip() == '':
            return None
        
        fecha_str = fecha_str.strip()
        
        # Formato: "19-01" (día-mes, año 2025)
        try:
            # Remover espacios y caracteres extra
            fecha_str = fecha_str.replace(' ', '')
            
            # Buscar patrón DD-MM
            match = re.match(r'(\d{1,2})-(\d{1,2})', fecha_str)
            if match:
                dia = int(match.group(1))
                mes = int(match.group(2))
                
                # Validar rango
                if 1 <= mes <= 12 and 1 <= dia <= 31:
                    año = 2025  # Asumimos 2025
                    try:
                        return datetime(año, mes, dia)
                    except ValueError:
                        # Fecha inválida (ej: 31 de febrero)
                        return None
        except Exception as e:
            pass
        
        return None
    
    def cargar_inputs_csv(self) -> List[Dict]:
        """Carga inputs del CSV"""
        inputs = []
        
        try:
            with open(CSV_INPUTS, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) < 3:
                    print("⚠️  CSV muy corto o vacío")
                    return []
                
                # Línea 1 (índice 0) tiene título, línea 2 (índice 1) tiene headers
                headers = [h.strip() for h in rows[1]]
                
                # Crear diccionario de índices
                header_map = {h: i for i, h in enumerate(headers)}
                
                # Procesar desde la línea 3 (índice 2) en adelante
                for idx, row in enumerate(rows[2:], start=3):
                    if len(row) < len(headers):
                        # Rellenar con valores vacíos si la fila es corta
                        row.extend([''] * (len(headers) - len(row)))
                    
                    # Extraer valores
                    def get_value(key, default=''):
                        col_idx = header_map.get(key, -1)
                        if col_idx >= 0 and col_idx < len(row):
                            return row[col_idx].strip()
                        return default
                    
                    # Intentar con y sin espacios
                    fecha_str = get_value('Fecha ') or get_value('Fecha')
                    cliente = get_value('Cliente ') or get_value('Cliente')
                    consulta = get_value('            Consulta ') or get_value('Consulta')
                    
                    # Parsear fecha
                    fecha = self._parsear_fecha(fecha_str)
                    
                    # Solo procesar si tiene fecha de 2025 y datos relevantes
                    if not fecha or fecha.year != 2025:
                        continue
                    
                    if not cliente and not consulta:
                        continue
                    
                    # Extraer todos los campos
                    input_data = {
                        'fecha': fecha,
                        'cliente': cliente,
                        'origen': get_value('Orig.'),
                        'telefono': get_value('Telefono-Contacto'),
                        'direccion': get_value('Direccion / Zona'),
                        'consulta': consulta,
                        'producto': get_value('Producto'),
                        'espesor': get_value('Espesor'),
                        'relleno': get_value('Relleno'),
                        'largo': get_value('Largo (M)'),
                        'ancho': get_value('Ancho (M)'),
                        'color': get_value('Color'),
                        'anclajes': get_value('Anclajes a'),
                        'traslado': get_value('Traslado'),
                        'direccion_envio': get_value('Dirección'),
                        'estado': get_value('Estado'),
                        'asignacion': get_value('Asig.'),
                        'row_index': idx
                    }
                    
                    inputs.append(input_data)
            
            print(f"✅ Cargados {len(inputs)} inputs de 2025")
            return inputs
            
        except Exception as e:
            print(f"❌ Error cargando CSV: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def buscar_cotizaciones_mes(self, año: int, mes: int) -> List[Dict]:
        """Busca cotizaciones generadas en un mes específico"""
        cotizaciones = []
        mes_str = f"{mes:02d}"
        
        # Buscar en estructura de carpetas
        base_path = Path(DROPBOX_COTIZACIONES)
        
        # Buscar en carpetas de 2025
        for carpeta in base_path.iterdir():
            if not carpeta.is_dir():
                continue
            
            # Buscar subcarpetas del mes
            mes_folders = [
                f"{mes_str} - {self._nombre_mes(mes)}",
                f"{mes_str}- {self._nombre_mes(mes)}",
                f"0{mes} - {self._nombre_mes(mes)}",
                f"{mes:02d} - {self._nombre_mes(mes)}",
                f"01-{self._nombre_mes(mes)}",
            ]
            
            for mes_folder in mes_folders:
                mes_path = carpeta / mes_folder
                if mes_path.exists():
                    for archivo in mes_path.rglob('*'):
                        if archivo.is_file() and self._es_cotizacion(archivo):
                            cotizaciones.append({
                                'archivo': str(archivo),
                                'nombre': archivo.name,
                                'fecha_modificacion': datetime.fromtimestamp(archivo.stat().st_mtime),
                                'tamaño': archivo.stat().st_size,
                                'carpeta': carpeta.name,
                                'path_completo': str(archivo)
                            })
        
        # También buscar en raíz de 2025
        for archivo in base_path.rglob('*'):
            if archivo.is_file() and self._es_cotizacion(archivo):
                fecha_mod = datetime.fromtimestamp(archivo.stat().st_mtime)
                if fecha_mod.year == año and fecha_mod.month == mes:
                    cotizaciones.append({
                        'archivo': str(archivo),
                        'nombre': archivo.name,
                        'fecha_modificacion': fecha_mod,
                        'tamaño': archivo.stat().st_size,
                        'carpeta': 'Raíz',
                        'path_completo': str(archivo)
                    })
        
        return cotizaciones
    
    def correlacionar_input_cotizacion(self, input_data: Dict, cotizaciones: List[Dict]) -> Optional[Dict]:
        """Intenta correlacionar un input con su cotización correspondiente"""
        cliente_input = input_data.get('cliente', '').lower().strip()
        fecha_input = input_data.get('fecha')
        consulta_input = input_data.get('consulta', '').lower()
        
        mejor_match = None
        mejor_score = 0
        
        for cotizacion in cotizaciones:
            nombre_archivo = cotizacion.get('nombre', '').lower()
            fecha_cotizacion = cotizacion.get('fecha_modificacion')
            
            score = 0
            
            # Coincidencia por nombre de cliente en archivo
            if cliente_input and cliente_input in nombre_archivo:
                score += 50
            
            # Coincidencia por palabras clave de la consulta
            palabras_clave = consulta_input.split()[:5]  # Primeras 5 palabras
            for palabra in palabras_clave:
                if len(palabra) > 3 and palabra in nombre_archivo:
                    score += 10
            
            # Coincidencia por fecha (mismo día o día cercano)
            if fecha_input and fecha_cotizacion:
                fecha_input_date = fecha_input.date() if isinstance(fecha_input, datetime) else fecha_input
                fecha_cotiz_date = fecha_cotizacion.date() if isinstance(fecha_cotizacion, datetime) else fecha_cotizacion
                diff_dias = abs((fecha_input_date - fecha_cotiz_date).days)
                if diff_dias == 0:
                    score += 30
                elif diff_dias <= 3:
                    score += 20
                elif diff_dias <= 7:
                    score += 10
            
            # Coincidencia por producto mencionado
            producto_input = input_data.get('producto', '').lower()
            if producto_input and any(p in nombre_archivo for p in ['isodec', 'isowall', 'isoroof', 'isopanel']):
                if producto_input in nombre_archivo:
                    score += 20
            
            if score > mejor_score:
                mejor_score = score
                mejor_match = cotizacion.copy()
                mejor_match['score_correlacion'] = score
        
        # Solo retornar si el score es significativo (>= 30)
        if mejor_match and mejor_score >= 30:
            return mejor_match
        
        return None
    
    def extraer_datos_cotizacion(self, archivo_path: str) -> Dict:
        """Intenta extraer datos de una cotización (PDF, Excel, etc.)"""
        datos = {
            'total': None,
            'subtotal': None,
            'iva': None,
            'productos': [],
            'cliente': None,
            'fecha': None,
            'error': None
        }
        
        try:
            path = Path(archivo_path)
            ext = path.suffix.lower()
            
            if ext == '.pdf':
                # Intentar extraer texto básico del PDF
                try:
                    try:
                        import PyPDF2
                    except ImportError:
                        try:
                            import pypdf as PyPDF2
                        except ImportError:
                            datos['error'] = 'PyPDF2 o pypdf no instalado'
                            return datos
                    
                    # Verificar que el archivo existe y es accesible
                    if not path.exists():
                        datos['error'] = f'Archivo no encontrado: {path}'
                        return datos
                    
                    # Intentar leer con timeout
                    import signal
                    
                    def timeout_handler(signum, frame):
                        raise TimeoutError("Timeout leyendo PDF")
                    
                    # Solo en sistemas Unix
                    try:
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(30)  # 30 segundos timeout (aumentado para archivos grandes)
                    except:
                        pass  # Windows no tiene SIGALRM
                    
                    texto = ''  # Inicializar antes del try
                    try:
                        with open(path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            # Leer máximo 5 páginas para evitar timeouts
                            max_pages = min(5, len(pdf_reader.pages))
                            for i in range(max_pages):
                                try:
                                    texto += pdf_reader.pages[i].extract_text()
                                except:
                                    continue
                    except TimeoutError:
                        datos['error'] = 'Timeout leyendo PDF (archivo muy grande o corrupto)'
                        return datos
                    except Exception as e:
                        datos['error'] = f'Error leyendo PDF: {str(e)}'
                        return datos
                    finally:
                        try:
                            signal.alarm(0)  # Cancelar alarm
                        except:
                            pass
                    
                    if not texto:
                        datos['error'] = 'No se pudo extraer texto del PDF'
                        return datos
                    
                    # Buscar totales
                    import re
                    # Buscar patrones de total (varios formatos)
                    patterns = [
                        r'total[:\s]*\$?\s*([\d.,]+)',
                        r'total[:\s]*usd\s*\$?\s*([\d.,]+)',
                        r'suma[:\s]*\$?\s*([\d.,]+)',
                        r'\$\s*([\d.,]+)\s*\(total\)',
                        r'total\s+general[:\s]*\$?\s*([\d.,]+)',
                        r'importe\s+total[:\s]*\$?\s*([\d.,]+)',
                        r'\$\s*([\d]{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:total|final)',
                    ]
                    
                    totales_encontrados = []
                    for pattern in patterns:
                        matches = re.finditer(pattern, texto, re.IGNORECASE)
                        for match in matches:
                            total_str = match.group(1)
                            # Limpiar y convertir
                            # Manejar formato uruguayo (punto como separador de miles, coma como decimal)
                            if '.' in total_str and ',' in total_str:
                                # Formato: 1.234,56
                                total_str = total_str.replace('.', '').replace(',', '.')
                            elif ',' in total_str:
                                # Puede ser decimal o separador de miles
                                if len(total_str.split(',')[-1]) <= 2:
                                    # Probablemente decimal
                                    total_str = total_str.replace(',', '.')
                                else:
                                    # Probablemente separador de miles
                                    total_str = total_str.replace(',', '')
                            else:
                                # Solo números, asumir que es el total
                                total_str = total_str.replace('.', '')
                            
                            try:
                                total_val = float(total_str)
                                if total_val > 0:  # Solo valores positivos
                                    totales_encontrados.append(total_val)
                            except:
                                pass
                    
                    # Usar el total más grande encontrado (probablemente el total final)
                    if totales_encontrados:
                        datos['total'] = max(totales_encontrados)
                        datos['totales_encontrados'] = totales_encontrados
                    
                    datos['texto_extraido'] = texto[:1000]  # Primeros 1000 caracteres para debug
                except Exception as e:
                    datos['error'] = f'Error leyendo PDF: {str(e)}'
            
            elif ext in ['.xlsx', '.xls', '.ods']:
                # Intentar leer Excel/ODS
                try:
                    try:
                        import pandas as pd
                    except ImportError:
                        datos['error'] = 'pandas no instalado. Ejecuta: pip install pandas openpyxl'
                        return datos
                    # Intentar leer todas las hojas
                    try:
                        excel_file = pd.ExcelFile(path)
                        sheet_names = excel_file.sheet_names
                    except:
                        sheet_names = [0]
                    
                    totales_encontrados = []
                    
                    for sheet in sheet_names[:5]:  # Máximo 5 hojas
                        try:
                            # Leer más filas para encontrar totales
                            df = pd.read_excel(path, sheet_name=sheet, nrows=200, header=None)
                            
                            # Buscar en todas las celdas valores que parezcan totales
                            for idx, row in df.iterrows():
                                for col_idx, val in row.items():
                                    try:
                                        # Buscar números grandes (probablemente totales)
                                        if isinstance(val, (int, float)) and val > 50:  # Total mínimo $50
                                            totales_encontrados.append(float(val))
                                        elif isinstance(val, str):
                                            # Buscar patrones de total en texto
                                            val_lower = val.lower()
                                            if any(word in val_lower for word in ['total', 'suma', 'importe']):
                                                # Extraer número del string
                                                num_match = re.search(r'[\d.,]+', val.replace(' ', ''))
                                                if num_match:
                                                    num_str = num_match.group(0)
                                                    # Limpiar formato uruguayo
                                                    if '.' in num_str and ',' in num_str:
                                                        # Formato: 1.234,56
                                                        num_str = num_str.replace('.', '').replace(',', '.')
                                                    elif ',' in num_str and len(num_str.split(',')[-1]) <= 2:
                                                        # Decimal con coma
                                                        num_str = num_str.replace(',', '.')
                                                    else:
                                                        # Separador de miles
                                                        num_str = num_str.replace(',', '').replace('.', '')
                                                    
                                                    try:
                                                        num_val = float(num_str)
                                                        if num_val > 50:
                                                            totales_encontrados.append(num_val)
                                                    except:
                                                        pass
                                    except:
                                        continue
                            
                            # También buscar en las últimas filas (donde suelen estar los totales)
                            if len(df) > 0:
                                for last_idx in range(max(0, len(df)-5), len(df)):
                                    last_row = df.iloc[last_idx]
                                    for val in last_row:
                                        try:
                                            if isinstance(val, (int, float)) and val > 50:
                                                totales_encontrados.append(float(val))
                                        except:
                                            pass
                        except Exception as e:
                            continue
                    
                    # Usar el total más grande encontrado
                    if totales_encontrados:
                        datos['total'] = max(totales_encontrados)
                        datos['totales_encontrados'] = totales_encontrados
                    
                except ImportError:
                    datos['error'] = 'pandas no instalado'
                except Exception as e:
                    datos['error'] = f'Error leyendo Excel: {str(e)}'
            
        except Exception as e:
            datos['error'] = f'Error general: {str(e)}'
        
        return datos
    
    def _nombre_mes(self, mes: int) -> str:
        """Nombre del mes en español"""
        meses = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        return meses.get(mes, '')
    
    def _es_cotizacion(self, archivo: Path) -> bool:
        """Verifica si un archivo es una cotización"""
        ext = archivo.suffix.lower()
        nombre = archivo.name.lower()
        
        # Extensiones de cotizaciones
        if ext in ['.pdf', '.xlsx', '.xls', '.ods', '.docx', '.doc']:
            # Buscar palabras clave
            if any(palabra in nombre for palabra in ['cotiz', 'presup', 'quote', 'budget']):
                return True
        
        return False
    
    def generar_presupuesto(self, input_data: Dict) -> Dict:
        """Genera presupuesto usando la base de conocimiento"""
        try:
            producto = input_data.get('producto', '').upper()
            espesor = input_data.get('espesor', '').replace('mm', '').replace(' ', '')
            largo_str = input_data.get('largo', '').replace(',', '.')
            ancho_str = input_data.get('ancho', '').replace(',', '.')
            
            # Intentar parsear dimensiones
            try:
                largo = float(largo_str) if largo_str else None
            except:
                largo = None
            
            try:
                ancho = float(ancho_str) if ancho_str else None
            except:
                ancho = None
            
            # Buscar producto en base de conocimiento
            producto_info = None
            if 'ISODEC' in producto or 'ISOWALL' in producto:
                if 'PIR' in input_data.get('relleno', '').upper():
                    producto_info = self.base_conocimiento.get('products', {}).get('ISODEC_PIR')
                else:
                    producto_info = self.base_conocimiento.get('products', {}).get('ISODEC_EPS')
            
            if not producto_info:
                return {
                    'error': 'Producto no encontrado en base de conocimiento',
                    'input': input_data
                }
            
            # Obtener precio del espesor
            espesor_key = espesor if espesor in producto_info.get('espesores', {}) else None
            if not espesor_key:
                # Buscar el más cercano
                espesores_disponibles = list(producto_info.get('espesores', {}).keys())
                if espesores_disponibles:
                    espesor_key = espesores_disponibles[0]  # Usar el primero disponible
            
            precio_info = producto_info.get('espesores', {}).get(espesor_key, {})
            precio_m2 = precio_info.get('precio', 0)
            autoportancia = precio_info.get('autoportancia', 0)
            ancho_util = producto_info.get('ancho_util', 1.12)
            
            # Calcular materiales
            if largo and ancho:
                area_total = largo * ancho
                cantidad_paneles = math.ceil(ancho / ancho_util)
                
                # Calcular apoyos
                apoyos = math.ceil((largo / autoportancia) + 1) if autoportancia > 0 else 1
                
                # Calcular puntos de fijación
                puntos_fijacion = math.ceil(((cantidad_paneles * apoyos) * 2) + (largo * 2 / 2.5))
                
                # Calcular accesorios
                varilla_cantidad = math.ceil(puntos_fijacion / 4)
                anclajes = input_data.get('anclajes', '').upper()
                
                if 'HORMIGON' in anclajes or 'HORMIGÓN' in anclajes:
                    tuercas = puntos_fijacion * 1
                    tacos = puntos_fijacion * 1
                else:
                    tuercas = puntos_fijacion * 2
                    tacos = 0
                
                # Calcular goteros
                gotero_frontal = math.ceil((cantidad_paneles * ancho_util) / 3)
                gotero_lateral = math.ceil((largo * 2) / 3)
                
                # Calcular costos
                costo_paneles = precio_m2 * largo * cantidad_paneles * ancho_util
                
                # Precios de accesorios (de base de conocimiento)
                precios = self.base_conocimiento.get('precios_accesorios_referencia', {})
                costo_varillas = varilla_cantidad * precios.get('varilla_3_8', 19.9)
                costo_tuercas = tuercas * precios.get('tuerca_3_8', 2.0)
                costo_tacos = tacos * precios.get('taco_3_8', 8.7) if tacos > 0 else 0
                costo_goteros = (gotero_frontal + gotero_lateral) * precios.get('gotero_frontal_isodec', 23.88)
                
                subtotal = costo_paneles + costo_varillas + costo_tuercas + costo_tacos + costo_goteros
                iva = subtotal * 0.22
                total = subtotal + iva
                
                return {
                    'producto': producto_info.get('nombre_comercial', ''),
                    'espesor': espesor_key,
                    'dimensiones': {
                        'largo': largo,
                        'ancho': ancho,
                        'area': area_total
                    },
                    'materiales': {
                        'paneles': cantidad_paneles,
                        'apoyos': apoyos,
                        'puntos_fijacion': puntos_fijacion,
                        'varillas': varilla_cantidad,
                        'tuercas': tuercas,
                        'tacos': tacos,
                        'goteros_frontal': gotero_frontal,
                        'goteros_lateral': gotero_lateral
                    },
                    'costos': {
                        'paneles': round(costo_paneles, 2),
                        'varillas': round(costo_varillas, 2),
                        'tuercas': round(costo_tuercas, 2),
                        'tacos': round(costo_tacos, 2),
                        'goteros': round(costo_goteros, 2),
                        'subtotal': round(subtotal, 2),
                        'iva': round(iva, 2),
                        'total': round(total, 2)
                    },
                    'validacion': {
                        'autoportancia': autoportancia,
                        'luz_cliente': largo,
                        'cumple_autoportancia': largo <= autoportancia if autoportancia > 0 else None
                    }
                }
            else:
                return {
                    'error': 'Faltan dimensiones (largo/ancho)',
                    'input': input_data
                }
        
        except Exception as e:
            return {
                'error': f'Error generando presupuesto: {str(e)}',
                'input': input_data
            }
    
    def analizar_mes(self, año: int, mes: int) -> Dict:
        """Analiza un mes completo"""
        print(f"\n📅 Analizando {self._nombre_mes(mes)} {año}...")
        
        # Filtrar inputs del mes
        inputs_mes = [
            inp for inp in self.inputs
            if inp['fecha'] and inp['fecha'].year == año and inp['fecha'].month == mes
        ]
        
        # Buscar cotizaciones del mes
        cotizaciones_mes = self.buscar_cotizaciones_mes(año, mes)
        
        # Generar presupuestos para cada input y correlacionar
        presupuestos_generados = []
        correlaciones = []
        
        for input_data in inputs_mes:
            presupuesto = self.generar_presupuesto(input_data)
            
            # Intentar correlacionar con cotización real
            cotizacion_correlacionada = self.correlacionar_input_cotizacion(input_data, cotizaciones_mes)
            
            item = {
                'input': input_data,
                'presupuesto': presupuesto,
                'cotizacion_real': cotizacion_correlacionada
            }
            
            # Si hay correlación, extraer datos de la cotización
            if cotizacion_correlacionada:
                print(f"  🔗 Correlacionado: {input_data.get('cliente', 'N/A')} -> {cotizacion_correlacionada.get('nombre', 'N/A')} (score: {cotizacion_correlacionada.get('score_correlacion', 0)})")
                print(f"     📄 Extrayendo datos de: {cotizacion_correlacionada.get('nombre', 'N/A')}")
                datos_cotizacion = self.extraer_datos_cotizacion(cotizacion_correlacionada['path_completo'])
                item['datos_cotizacion_real'] = datos_cotizacion
                
                # Mostrar resultado de extracción
                if datos_cotizacion.get('error'):
                    print(f"     ⚠️  Error extrayendo: {datos_cotizacion.get('error')}")
                    if datos_cotizacion.get('texto_extraido'):
                        print(f"     📝 Texto extraído (primeros 200 chars): {datos_cotizacion.get('texto_extraido')[:200]}")
                elif datos_cotizacion.get('total'):
                    print(f"     ✅ Total extraído: ${datos_cotizacion.get('total'):.2f}")
                    if datos_cotizacion.get('totales_encontrados'):
                        print(f"     📊 Totales encontrados: {datos_cotizacion.get('totales_encontrados')}")
                else:
                    print(f"     ⚠️  No se encontró total en el archivo")
                    if datos_cotizacion.get('texto_extraido'):
                        # Buscar cualquier número que parezca un total
                        import re
                        numeros = re.findall(r'\$?\s*[\d.,]+', datos_cotizacion.get('texto_extraido', ''))
                        if numeros:
                            print(f"     💡 Números encontrados en el texto: {numeros[:10]}")
                    if datos_cotizacion.get('totales_encontrados'):
                        print(f"     💡 Totales parciales encontrados: {datos_cotizacion.get('totales_encontrados')}")
                
                # Comparar totales
                if 'error' not in presupuesto:
                    total_generado = presupuesto.get('costos', {}).get('total', 0)
                    if datos_cotizacion.get('total'):
                        total_real = datos_cotizacion.get('total', 0)
                        if total_generado and total_real:
                            diferencia = abs(total_generado - total_real)
                            diferencia_porcentual = (diferencia / total_real * 100) if total_real > 0 else 0
                            item['comparacion'] = {
                                'total_generado': total_generado,
                                'total_real': total_real,
                                'diferencia': diferencia,
                                'diferencia_porcentual': diferencia_porcentual
                            }
                            print(f"     💰 Comparación: Generado=${total_generado:.2f} vs Real=${total_real:.2f} (Diff: ${diferencia:.2f} / {diferencia_porcentual:.1f}%)")
                    elif total_generado:
                        print(f"     💰 Presupuesto generado: ${total_generado:.2f} (sin total real para comparar)")
            
            presupuestos_generados.append(item)
            
            if cotizacion_correlacionada:
                correlaciones.append(item)
        
        print(f"  ✅ {len(correlaciones)} correlaciones encontradas de {len(presupuestos_generados)} inputs")
        
        return {
            'mes': mes,
            'año': año,
            'nombre_mes': self._nombre_mes(mes),
            'inputs': len(inputs_mes),
            'cotizaciones_reales': len(cotizaciones_mes),
            'presupuestos_generados': len(presupuestos_generados),
            'correlaciones': len(correlaciones),
            'detalle_inputs': inputs_mes,
            'detalle_cotizaciones': cotizaciones_mes,
            'detalle_presupuestos': presupuestos_generados
        }
    
    def procesar_todos_los_meses(self) -> List[Dict]:
        """Procesa todos los meses desde hoy hacia atrás"""
        hoy = datetime.now()
        resultados = []
        
        # Procesar desde el mes actual hacia atrás hasta enero 2025
        for mes in range(hoy.month, 0, -1):
            resultado = self.analizar_mes(2025, mes)
            resultados.append(resultado)
        
        return resultados
    
    def generar_reporte_html(self, resultados: List[Dict]) -> str:
        """Genera reporte HTML interactivo"""
        html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis de Cotizaciones 2025</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: #333; margin-bottom: 30px; }
        .mes-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .mes-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid #eee;
        }
        .mes-title { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .stats {
            display: flex;
            gap: 20px;
        }
        .stat {
            text-align: center;
            padding: 10px 15px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        .stat-value { font-size: 28px; font-weight: bold; color: #3498db; }
        .stat-label { font-size: 12px; color: #7f8c8d; margin-top: 5px; }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background: #ecf0f1;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
        }
        .tab.active {
            background: #3498db;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .input-item, .cotizacion-item, .presupuesto-item {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }
        .presupuesto-item { border-left-color: #27ae60; }
        .cotizacion-item { border-left-color: #e74c3c; }
        .comparacion {
            background: #fff3cd;
            padding: 15px;
            border-radius: 6px;
            margin: 10px 0;
            border-left: 4px solid #ffc107;
        }
        .diferencia {
            color: #e74c3c;
            font-weight: bold;
        }
        .coincidencia {
            color: #27ae60;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #34495e;
            color: white;
        }
        .error { color: #e74c3c; }
        .success { color: #27ae60; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Análisis de Cotizaciones 2025</h1>
"""
        
        for resultado in resultados:
            html += f"""
        <div class="mes-card">
            <div class="mes-header">
                <div class="mes-title">{resultado['nombre_mes']} {resultado['año']}</div>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{resultado['inputs']}</div>
                        <div class="stat-label">Inputs</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{resultado['cotizaciones_reales']}</div>
                        <div class="stat-label">Cotizaciones</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{resultado['presupuestos_generados']}</div>
                        <div class="stat-label">Presupuestos Gen.</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{resultado.get('correlaciones', 0)}</div>
                        <div class="stat-label">Correlaciones</div>
                    </div>
                </div>
            </div>
            
            <div class="tabs">
                <button class="tab active" onclick="showTab(this, 'comparaciones-{resultado['mes']}')">Comparaciones ({resultado.get('correlaciones', 0)})</button>
                <button class="tab" onclick="showTab(this, 'inputs-{resultado['mes']}')">Inputs ({resultado['inputs']})</button>
                <button class="tab" onclick="showTab(this, 'cotizaciones-{resultado['mes']}')">Cotizaciones ({resultado['cotizaciones_reales']})</button>
                <button class="tab" onclick="showTab(this, 'presupuestos-{resultado['mes']}')">Presupuestos ({resultado['presupuestos_generados']})</button>
            </div>
            
            <div id="comparaciones-{resultado['mes']}" class="tab-content active">
"""
            # Mostrar comparaciones
            for item in resultado['detalle_presupuestos']:
                if item.get('cotizacion_real') and item.get('comparacion'):
                    comparacion = item['comparacion']
                    input_data = item['input']
                    presupuesto = item['presupuesto']
                    cotizacion = item['cotizacion_real']
                    
                    diff_class = 'diferencia' if comparacion['diferencia_porcentual'] > 5 else 'coincidencia'
                    
                    html += f"""
                <div class="comparacion">
                    <h3>{input_data.get('cliente', 'N/A')} - {input_data.get('fecha').strftime('%d/%m/%Y') if input_data.get('fecha') else 'Sin fecha'}</h3>
                    <p><strong>Consulta:</strong> {input_data.get('consulta', 'N/A')[:100]}...</p>
                    <p><strong>Cotización Correlacionada:</strong> {cotizacion.get('nombre', 'N/A')}</p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                        <div>
                            <h4>💰 Presupuesto Generado (Base Conocimiento)</h4>
                            <table>
                                <tr><td>Subtotal:</td><td><strong>${comparacion['total_generado']:.2f}</strong></td></tr>
                                <tr><td>IVA (22%):</td><td>${comparacion['total_generado'] * 0.22 / 1.22:.2f}</td></tr>
                                <tr><td><strong>TOTAL:</strong></td><td><strong>${comparacion['total_generado']:.2f}</strong></td></tr>
                            </table>
                        </div>
                        <div>
                            <h4>📄 Cotización Real</h4>
                            <table>
                                <tr><td>Subtotal:</td><td><strong>${comparacion['total_real'] / 1.22:.2f}</strong></td></tr>
                                <tr><td>IVA (22%):</td><td>${comparacion['total_real'] - (comparacion['total_real'] / 1.22):.2f}</td></tr>
                                <tr><td><strong>TOTAL:</strong></td><td><strong>${comparacion['total_real']:.2f}</strong></td></tr>
                            </table>
                        </div>
                    </div>
                    <div style="margin-top: 15px; padding: 10px; background: {'#ffebee' if comparacion['diferencia_porcentual'] > 5 else '#e8f5e9'}; border-radius: 6px;">
                        <strong>Diferencia:</strong> 
                        <span class="{diff_class}">
                            ${comparacion['diferencia']:.2f} ({comparacion['diferencia_porcentual']:.1f}%)
                        </span>
                        {'⚠️ Diferencia significativa' if comparacion['diferencia_porcentual'] > 5 else '✅ Coincidencia aceptable'}
                    </div>
                </div>
"""
                elif item.get('cotizacion_real'):
                    # Hay correlación pero no se pudo extraer total
                    html += f"""
                <div class="comparacion">
                    <h3>{item['input'].get('cliente', 'N/A')}</h3>
                    <p><strong>Cotización encontrada:</strong> {item['cotizacion_real'].get('nombre', 'N/A')}</p>
                    <p><small>Score de correlación: {item['cotizacion_real'].get('score_correlacion', 0)}</small></p>
                    <p class="error">⚠️ No se pudo extraer el total de la cotización ({item.get('datos_cotizacion_real', {}).get('error', 'Error desconocido')})</p>
                </div>
"""
            
            html += """
            </div>
            
            <div id="inputs-{resultado['mes']}" class="tab-content">
"""
            for input_data in resultado['detalle_inputs']:
                html += f"""
                <div class="input-item">
                    <strong>{input_data['cliente']}</strong> - {input_data['fecha'].strftime('%d/%m/%Y') if input_data['fecha'] else 'Sin fecha'}<br>
                    <small>Origen: {input_data['origen']} | Tel: {input_data['telefono']}</small><br>
                    <p>{input_data['consulta']}</p>
                    <small>Producto: {input_data['producto']} | Espesor: {input_data['espesor']} | Largo: {input_data['largo']}m | Ancho: {input_data['ancho']}m</small>
                </div>
"""
            
            html += f"""
            </div>
            
            <div id="cotizaciones-{resultado['mes']}" class="tab-content">
"""
            for cotizacion in resultado['detalle_cotizaciones']:
                html += f"""
                <div class="cotizacion-item">
                    <strong>{cotizacion['nombre']}</strong><br>
                    <small>Carpeta: {cotizacion['carpeta']} | Modificado: {cotizacion['fecha_modificacion'].strftime('%d/%m/%Y %H:%M')}</small>
                </div>
"""
            
            html += f"""
            </div>
            
            <div id="presupuestos-{resultado['mes']}" class="tab-content">
"""
            for item in resultado['detalle_presupuestos']:
                presupuesto = item['presupuesto']
                input_data = item['input']
                
                if 'error' in presupuesto:
                    html += f"""
                <div class="presupuesto-item error">
                    <strong>Error:</strong> {presupuesto['error']}<br>
                    <small>Cliente: {input_data['cliente']} | Consulta: {input_data['consulta']}</small>
                </div>
"""
                else:
                    costos = presupuesto.get('costos', {})
                    html += f"""
                <div class="presupuesto-item">
                    <strong>{presupuesto.get('producto', 'N/A')} - {presupuesto.get('espesor', 'N/A')}</strong><br>
                    <small>Cliente: {input_data['cliente']}</small><br>
                    <table>
                        <tr><th>Concepto</th><th>Cantidad</th><th>Precio Unit.</th><th>Subtotal</th></tr>
                        <tr><td>Paneles</td><td>{presupuesto['materiales']['paneles']}</td><td>${presupuesto.get('costos', {}).get('paneles', 0) / presupuesto['materiales']['paneles'] if presupuesto['materiales']['paneles'] > 0 else 0:.2f}</td><td>${costos.get('paneles', 0):.2f}</td></tr>
                        <tr><td>Varillas</td><td>{presupuesto['materiales']['varillas']}</td><td>$19.90</td><td>${costos.get('varillas', 0):.2f}</td></tr>
                        <tr><td>Tuercas</td><td>{presupuesto['materiales']['tuercas']}</td><td>$2.00</td><td>${costos.get('tuercas', 0):.2f}</td></tr>
                        <tr><td>Goteros</td><td>{presupuesto['materiales']['goteros_frontal'] + presupuesto['materiales']['goteros_lateral']}</td><td>$23.88</td><td>${costos.get('goteros', 0):.2f}</td></tr>
                        <tr><td colspan="3"><strong>Subtotal</strong></td><td><strong>${costos.get('subtotal', 0):.2f}</strong></td></tr>
                        <tr><td colspan="3">IVA (22%)</td><td>${costos.get('iva', 0):.2f}</td></tr>
                        <tr><td colspan="3"><strong>TOTAL</strong></td><td><strong>${costos.get('total', 0):.2f}</strong></td></tr>
                    </table>
                </div>
"""
            
            html += """
            </div>
        </div>
"""
        
        html += """
    </div>
    
    <script>
        function showTab(button, tabId) {
            // Ocultar todos los tabs del mismo mes
            const mesCard = button.closest('.mes-card');
            mesCard.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            mesCard.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            
            // Mostrar el tab seleccionado
            button.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }
    </script>
</body>
</html>
"""
        return html


def main():
    print("=" * 60)
    print("🔍 Análisis de Cotizaciones 2025")
    print("=" * 60)
    
    analizador = AnalizadorCotizaciones()
    
    # Cargar inputs
    print("\n📥 Cargando inputs del CSV...")
    analizador.inputs = analizador.cargar_inputs_csv()
    
    # Procesar todos los meses
    print("\n📊 Procesando meses desde hoy hacia atrás...")
    resultados = analizador.procesar_todos_los_meses()
    
    # Generar reporte HTML
    print("\n📄 Generando reporte HTML interactivo...")
    html = analizador.generar_reporte_html(resultados)
    
    # Guardar reporte
    output_file = "analisis_cotizaciones_2025.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Reporte generado: {output_file}")
    print(f"   Abre el archivo en tu navegador para ver el análisis interactivo")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📈 RESUMEN")
    print("=" * 60)
    total_inputs = sum(r['inputs'] for r in resultados)
    total_cotizaciones = sum(r['cotizaciones_reales'] for r in resultados)
    total_presupuestos = sum(r['presupuestos_generados'] for r in resultados)
    
    print(f"Total Inputs: {total_inputs}")
    print(f"Total Cotizaciones Reales: {total_cotizaciones}")
    print(f"Total Presupuestos Generados: {total_presupuestos}")
    print(f"Ratio: {total_cotizaciones/total_inputs*100:.1f}%" if total_inputs > 0 else "N/A")


if __name__ == "__main__":
    main()
