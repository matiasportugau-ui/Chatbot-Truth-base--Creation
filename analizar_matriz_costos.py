#!/usr/bin/env python3
"""
Analizador de Matriz de Costos y Ventas 2026
Extrae costos y precios para diferentes tipos de compra por proveedor
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class AnalizadorMatrizCostos:
    """Analiza matrices de costos y genera base de conocimiento estructurada"""
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.proveedores: Dict[str, List[Dict]] = {}
        self.secciones: List[str] = []
        
    def limpiar_valor(self, valor: str) -> Optional[float]:
        """Limpia y convierte valores numéricos del CSV"""
        if not valor or valor.strip() == '':
            return None
        
        # Remover espacios y caracteres especiales
        valor = valor.strip().replace(',', '.')
        
        # Remover porcentajes
        if '%' in valor:
            valor = valor.replace('%', '')
        
        # Intentar convertir a float
        try:
            return float(valor)
        except (ValueError, TypeError):
            return None
    
    def identificar_seccion(self, fila: List[str]) -> Optional[str]:
        """Identifica la sección/categoría del producto"""
        # Buscar en diferentes columnas
        for col in fila:
            if col and isinstance(col, str):
                col_upper = col.upper().strip()
                
                # Categorías principales
                if 'ISOROOF' in col_upper and 'FOIL' in col_upper:
                    return 'ISOROOF_FOIL'
                elif 'ISOROOF' in col_upper and 'PLUS' in col_upper:
                    return 'ISOROOF_PLUS'
                elif 'ISOROOF' in col_upper and 'COLONIAL' in col_upper:
                    return 'ISOROOF_COLONIAL'
                elif 'ISOROOF' in col_upper:
                    return 'ISOROOF'
                elif 'ISOPANEL' in col_upper and 'EPS' in col_upper:
                    return 'ISOPANEL_EPS'
                elif 'ISODEC' in col_upper and 'EPS' in col_upper:
                    return 'ISODEC_EPS'
                elif 'ISODEC' in col_upper and 'PIR' in col_upper:
                    return 'ISODEC_PIR'
                elif 'ISOWALL' in col_upper:
                    return 'ISOWALL'
                elif 'ISOFRIG' in col_upper:
                    return 'ISOFRIG'
                elif 'GOTERO' in col_upper:
                    if 'FRONTAL' in col_upper:
                        return 'GOTERO_FRONTAL'
                    elif 'LATERAL' in col_upper:
                        return 'GOTERO_LATERAL'
                    elif 'SUPERIOR' in col_upper:
                        return 'GOTERO_SUPERIOR'
                elif 'BABETA' in col_upper:
                    return 'BABETAS'
                elif 'CANALÓN' in col_upper or 'CANALON' in col_upper:
                    return 'CANALONES'
                elif 'CUMBRERA' in col_upper:
                    return 'CUMBRERAS'
                elif 'PERFIL' in col_upper:
                    return 'PERFILES'
                elif 'ANCLAJE' in col_upper:
                    return 'ANCLAJES'
                elif 'FLETE' in col_upper:
                    return 'FLETES'
                elif 'ACCESORIO' in col_upper:
                    return 'ACCESORIOS'
        
        return None
    
    def extraer_producto(self, fila: List[str], headers: List[str]) -> Optional[Dict[str, Any]]:
        """Extrae información de un producto de una fila"""
        producto = {}
        
        # Estructura del CSV:
        # Col 0: Notas (Fata foto, NO SUBIR, etc.)
        # Col 1: Notas adicionales
        # Col 2: Estado (ACT.)
        # Col 3: Código (IAGRO30, IROOF30, etc.)
        # Col 4: Nombre del producto
        # Col 5: Costo m2 U$S + IVA
        # Col 6: Con AUMENTO
        # Col 7: Proximo AUMENTO
        # Col 8: Margen %
        # Col 9: (vacía)
        # Col 10: Ganancia
        # Col 11: Venta + IVA
        # Col 12: CONSUMIDOR IVA INC.
        # Col 15: WEB Venta + IVA
        # Col 16: WEB Venta IVA inc.
        
        # Buscar código del producto (columna 3)
        codigo = fila[3] if len(fila) > 3 else None
        nombre = fila[4] if len(fila) > 4 else None
        
        # Validar que tenga código y nombre
        if not codigo or not nombre or codigo.strip() == '' or nombre.strip() == '':
            return None
        
        # Si tiene "NO SUBIR" o está descontinuado, marcarlo
        estado_notas = fila[0] if len(fila) > 0 else ''
        if 'NO SUBIR' in str(estado_notas).upper():
            producto['subir_web'] = False
        else:
            producto['subir_web'] = True
        
        producto['codigo'] = codigo.strip()
        producto['nombre'] = nombre.strip()
        producto['notas'] = estado_notas.strip() if estado_notas else ''
        producto['estado'] = fila[2].strip() if len(fila) > 2 and fila[2] else ''
        
        # Extraer costos (Compras a fábrica directo)
        # Columna 5: "Costo m2 U$S + IVA" (costo base)
        costo_base = self.limpiar_valor(fila[5] if len(fila) > 5 else '')
        # Columna 6: "Con AUMENTO"
        costo_con_aumento = self.limpiar_valor(fila[6] if len(fila) > 6 else '')
        # Columna 7: "Proximo AUMENTO"
        costo_proximo_aumento = self.limpiar_valor(fila[7] if len(fila) > 7 else '')
        
        producto['costos_fabrica_directo'] = {
            'costo_base_usd_iva': costo_base,
            'costo_con_aumento_usd_iva': costo_con_aumento,
            'costo_proximo_aumento_usd_iva': costo_proximo_aumento
        }
        
        # Extraer precios (Compras web o stock)
        # Columna 11: "Venta + IVA"
        venta_iva = self.limpiar_valor(fila[11] if len(fila) > 11 else '')
        # Columna 12: "CONSUMIDOR IVA INC."
        consumidor_iva_inc = self.limpiar_valor(fila[12] if len(fila) > 12 else '')
        # Columna 15: "WEB Venta + IVA"
        web_venta_iva = self.limpiar_valor(fila[15] if len(fila) > 15 else '')
        # Columna 16: "WEB Venta IVA inc."
        web_venta_iva_inc = self.limpiar_valor(fila[16] if len(fila) > 16 else '')
        
        producto['precios_web_stock'] = {
            'venta_iva_usd': venta_iva,
            'consumidor_iva_inc_usd': consumidor_iva_inc,
            'web_venta_iva_usd': web_venta_iva,
            'web_venta_iva_inc_usd': web_venta_iva_inc
        }
        
        # Margen y ganancia
        margen_str = fila[8] if len(fila) > 8 else ''
        margen = self.limpiar_valor(margen_str)
        ganancia = self.limpiar_valor(fila[10] if len(fila) > 10 else '')
        
        producto['margen_porcentaje'] = margen
        producto['ganancia_usd'] = ganancia
        
        # Precio por metro lineal (columna 14)
        precio_ml = self.limpiar_valor(fila[14] if len(fila) > 14 else '')
        if precio_ml:
            producto['precio_metro_lineal_usd'] = precio_ml
        
        # Precios por metro lineal según largo (columnas 21-41)
        # Las columnas empiezan en 21 con largos de 1.0m, 1.5m, 2.0m, etc.
        precios_ml_largos = {}
        for i in range(21, min(42, len(fila))):
            largo = 1.0 + (i - 21) * 0.5  # 1.0, 1.5, 2.0, ..., 13.0
            precio = self.limpiar_valor(fila[i])
            if precio:
                precios_ml_largos[f"{largo:.1f}m"] = precio
        
        if precios_ml_largos:
            producto['precios_metro_lineal_por_largo'] = precios_ml_largos
        
        return producto
    
    def analizar_csv(self, proveedor_nombre: str = "BROMYROS"):
        """Analiza el CSV y extrae todos los productos organizados por sección"""
        productos_por_seccion: Dict[str, List[Dict]] = {}
        seccion_actual = None
        
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            # Leer headers (primeras 2-3 líneas)
            headers = []
            for i, fila in enumerate(reader):
                if i < 3:
                    headers.append(fila)
                else:
                    break
        
        # Reiniciar lectura para procesar datos
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            # Saltar headers
            for i in range(3):
                next(reader, None)
            
            # Procesar filas
            for fila in reader:
                # Identificar sección
                nueva_seccion = self.identificar_seccion(fila)
                if nueva_seccion:
                    seccion_actual = nueva_seccion
                    if seccion_actual not in productos_por_seccion:
                        productos_por_seccion[seccion_actual] = []
                
                # Extraer producto
                producto = self.extraer_producto(fila, headers)
                if producto and seccion_actual:
                    producto['seccion'] = seccion_actual
                    productos_por_seccion[seccion_actual].append(producto)
        
        self.proveedores[proveedor_nombre] = productos_por_seccion
        return productos_por_seccion
    
    def generar_base_conocimiento(self, output_path: str):
        """Genera archivo JSON con base de conocimiento estructurada"""
        kb = {
            "meta": {
                "nombre": "Base de Conocimiento - Costos y Precios por Proveedor",
                "version": "1.0",
                "fecha_creacion": datetime.now().isoformat(),
                "fuente": "MATRIZ de COSTOS y VENTAS 2026.xlsx",
                "descripcion": "Costos y precios organizados por proveedor y tipo de compra"
            },
            "estructura_precios": {
                "compras_fabrica_directo": {
                    "descripcion": "Precios para compras directas a fábrica",
                    "campos": [
                        "costo_base_usd_iva",
                        "costo_con_aumento_usd_iva",
                        "costo_proximo_aumento_usd_iva"
                    ]
                },
                "compras_web_stock": {
                    "descripcion": "Precios para compras web o desde stock",
                    "campos": [
                        "venta_iva_usd",
                        "consumidor_iva_inc_usd",
                        "web_venta_iva_usd",
                        "web_venta_iva_inc_usd"
                    ]
                }
            },
            "proveedores": {}
        }
        
        for proveedor, secciones in self.proveedores.items():
            kb["proveedores"][proveedor] = {
                "nombre": proveedor,
                "secciones": {}
            }
            
            for seccion, productos in secciones.items():
                kb["proveedores"][proveedor]["secciones"][seccion] = {
                    "nombre": seccion,
                    "total_productos": len(productos),
                    "productos": productos
                }
        
        # Guardar JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(kb, f, ensure_ascii=False, indent=2)
        
        return kb
    
    def generar_resumen(self) -> Dict[str, Any]:
        """Genera un resumen estadístico del análisis"""
        resumen = {
            "total_proveedores": len(self.proveedores),
            "proveedores": {}
        }
        
        for proveedor, secciones in self.proveedores.items():
            total_productos = 0
            secciones_info = {}
            
            for seccion, productos in secciones.items():
                total_productos += len(productos)
                secciones_info[seccion] = {
                    "total_productos": len(productos),
                    "productos_con_costo": sum(1 for p in productos if p.get('costos_fabrica_directo', {}).get('costo_base_usd_iva')),
                    "productos_con_precio_web": sum(1 for p in productos if p.get('precios_web_stock', {}).get('web_venta_iva_inc_usd'))
                }
            
            resumen["proveedores"][proveedor] = {
                "total_productos": total_productos,
                "total_secciones": len(secciones),
                "secciones": secciones_info
            }
        
        return resumen


def main():
    """Función principal"""
    csv_path = "MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv"
    
    if not Path(csv_path).exists():
        print(f"❌ Error: No se encuentra el archivo {csv_path}")
        return
    
    print(f"📊 Analizando {csv_path}...")
    
    analizador = AnalizadorMatrizCostos(csv_path)
    productos = analizador.analizar_csv("BROMYROS")
    
    print(f"✅ Análisis completado")
    print(f"   - Secciones encontradas: {len(productos)}")
    
    # Generar resumen
    resumen = analizador.generar_resumen()
    print("\n📈 RESUMEN:")
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    
    # Generar base de conocimiento
    output_path = "BMC_Base_Costos_Precios_BROMYROS.json"
    kb = analizador.generar_base_conocimiento(output_path)
    
    print(f"\n💾 Base de conocimiento guardada en: {output_path}")
    print(f"   - Total productos: {sum(len(seccion) for seccion in productos.values())}")
    
    # Guardar resumen también
    resumen_path = "resumen_analisis_costos_BROMYROS.json"
    with open(resumen_path, 'w', encoding='utf-8') as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Resumen guardado en: {resumen_path}")


if __name__ == "__main__":
    main()
