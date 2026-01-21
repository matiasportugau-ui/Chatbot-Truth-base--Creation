#!/usr/bin/env python3
"""
Script para parsear el CSV de costos y ventas y generar una base de conocimiento JSON
"""

import csv
import json
import re
from typing import Dict, List, Optional, Any
from pathlib import Path

def clean_value(value: str) -> Optional[float]:
    """Limpia y convierte un valor a float, manejando casos especiales"""
    if not value or value.strip() == '':
        return None
    
    # Remover espacios y caracteres especiales
    value = value.strip()
    
    # Manejar valores como "#VALUE!", "x", etc.
    if value in ['#VALUE!', 'x', 'X', '-', '']:
        return None
    
    # Reemplazar comas por puntos para decimales
    value = value.replace(',', '.')
    
    # Remover caracteres no numéricos excepto punto y signo negativo
    value = re.sub(r'[^\d\.\-]', '', value)
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def extract_espesor(product_name: str) -> Optional[str]:
    """Extrae el espesor del nombre del producto"""
    # Buscar patrones como "30 mm", "50mm", "100 mm", etc.
    patterns = [
        r'(\d+)\s*mm',
        r'(\d+)\s*MM',
        r'espesor\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, product_name, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def categorize_product(sku: str, product_name: str) -> Dict[str, Any]:
    """Categoriza el producto según su SKU y nombre"""
    product_name_upper = product_name.upper()
    sku_upper = sku.upper()
    
    category = "accesorios"
    subcategory = "otros"
    
    # ISOROOF
    if "ISOROOF" in product_name_upper or "IROOF" in sku_upper or "IAGRO" in sku_upper:
        category = "isoroof"
        if "FOIL" in product_name_upper:
            subcategory = "foil"
        elif "PLUS" in product_name_upper or "PLS" in sku_upper:
            subcategory = "plus"
        elif "COLONIAL" in product_name_upper:
            subcategory = "colonial"
        else:
            subcategory = "standard"
    
    # ISODEC
    elif "ISODEC" in product_name_upper or "ISD" in sku_upper:
        category = "isodec"
        if "PIR" in product_name_upper or "PIR" in sku_upper:
            subcategory = "pir"
        else:
            subcategory = "eps"
    
    # ISOPANEL
    elif "ISOPANEL" in product_name_upper or "ISD" in sku_upper and "EPS" in product_name_upper:
        category = "isopanel"
        subcategory = "eps"
    
    # ISOWALL
    elif "ISOWALL" in product_name_upper or "IW" in sku_upper:
        category = "isowall"
        if "PIR" in product_name_upper:
            subcategory = "pir"
        else:
            subcategory = "standard"
    
    # ISOFRIG
    elif "ISOFRIG" in product_name_upper or "IF" in sku_upper:
        category = "isofrig"
        subcategory = "sala_limpia"
    
    # GOTEROS
    elif "GOTERO" in product_name_upper or "GF" in sku_upper or "GL" in sku_upper:
        category = "accesorios"
        if "FRONTAL" in product_name_upper:
            subcategory = "gotero_frontal"
        elif "LATERAL" in product_name_upper:
            subcategory = "gotero_lateral"
        else:
            subcategory = "gotero"
    
    # CANALONES
    elif "CANAL" in product_name_upper or "CD" in sku_upper or "CAN" in sku_upper:
        category = "accesorios"
        subcategory = "canalon"
    
    # CUMBRERAS
    elif "CUMBRERA" in product_name_upper or "CUM" in sku_upper:
        category = "accesorios"
        subcategory = "cumbrera"
    
    # BABETAS
    elif "BABETA" in product_name_upper or "BB" in sku_upper:
        category = "accesorios"
        subcategory = "babeta"
    
    # PERFILES
    elif "PERFIL" in product_name_upper or "PU" in sku_upper:
        category = "accesorios"
        subcategory = "perfil"
    
    # ANCLAJES
    elif any(x in product_name_upper for x in ["VARILLA", "TUERCA", "ARANDELA", "TACO"]):
        category = "accesorios"
        subcategory = "anclaje"
    
    # FLETE
    elif "FLETE" in product_name_upper:
        category = "servicios"
        subcategory = "flete"
    
    # OTROS
    elif any(x in product_name_upper for x in ["CINTA", "SILICONA", "BROMPLAST", "CABALLETE"]):
        category = "accesorios"
        subcategory = "sellado_fijacion"
    
    return {
        "category": category,
        "subcategory": subcategory
    }

def parse_csv_to_knowledge_base(csv_path: str) -> Dict[str, Any]:
    """Parsea el CSV y genera la estructura de conocimiento base"""
    
    products = {}
    accesorios = []
    servicios = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        # Saltar las primeras 2 filas de encabezados
        for i, row in enumerate(rows[2:], start=3):
            if len(row) < 20:  # Asegurar que hay suficientes columnas
                continue
            
            sku = row[3].strip() if len(row) > 3 else ""  # Columna D (índice 3)
            product_name = row[4].strip() if len(row) > 4 else ""  # Columna E (índice 4)
            costo = clean_value(row[6]) if len(row) > 6 else None  # Columna G (índice 6)
            precio_fabrica_iva = clean_value(row[11]) if len(row) > 11 else None  # Columna L (índice 11)
            precio_fabrica_iva_inc = clean_value(row[12]) if len(row) > 12 else None  # Columna M (índice 12)
            precio_web_iva = clean_value(row[18]) if len(row) > 18 else None  # Columna S (índice 18)
            precio_web_iva_inc = clean_value(row[19]) if len(row) > 19 else None  # Columna T (índice 19)
            
            # Saltar filas vacías o sin información relevante
            if not sku and not product_name:
                continue
            
            # Saltar filas que son solo encabezados de sección
            if product_name and any(x in product_name.upper() for x in [
                "PRODUCTO", "ISOROOF", "ISODEC", "ISOPANEL", "GOTERO", 
                "CANAL", "CUMBRERA", "BABETA", "PERFIL", "ANCLAJE"
            ]):
                # Verificar si es realmente un encabezado (sin números en nombre ni SKU)
                if not any(char.isdigit() for char in product_name) and not any(char.isdigit() for char in sku):
                    continue
            
            # Categorizar producto
            cat_info = categorize_product(sku, product_name)
            category = cat_info["category"]
            subcategory = cat_info["subcategory"]
            
            # Extraer espesor si existe
            espesor = extract_espesor(product_name)
            
            # Estructura del producto
            product_data = {
                "sku": sku,
                "nombre": product_name,
                "categoria": category,
                "subcategoria": subcategory,
                "costos": {
                    "costo_proveedor_actualizado": costo
                },
                "precios": {
                    "fabrica_directo": {
                        "precio_iva": precio_fabrica_iva,
                        "precio_iva_incluido": precio_fabrica_iva_inc
                    },
                    "web_stock": {
                        "precio_iva": precio_web_iva,
                        "precio_iva_incluido": precio_web_iva_inc
                    }
                }
            }
            
            # Agregar espesor si existe
            if espesor:
                product_data["espesor_mm"] = int(espesor)
            
            # Organizar por categoría
            if category in ["isoroof", "isodec", "isopanel", "isowall", "isofrig"]:
                # Productos principales - organizar por categoría y espesor
                key = f"{category}_{subcategory}"
                if key not in products:
                    products[key] = {
                        "categoria": category,
                        "subcategoria": subcategory,
                        "productos": []
                    }
                products[key]["productos"].append(product_data)
            elif category == "servicios":
                servicios.append(product_data)
            else:
                accesorios.append(product_data)
    
    # Estructura final de conocimiento base
    kb_structure = {
        "meta": {
            "nombre": "BMC Bromyros - Base de Conocimiento de Costos y Precios 2026",
            "version": "1.0",
            "fecha": "2026-01-21",
            "fuente": "MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv",
            "descripcion": "Base de conocimiento con costos de proveedor y precios de venta (fábrica directo y web/stock)"
        },
        "productos_principales": products,
        "accesorios": accesorios,
        "servicios": servicios,
        "estructura_precios": {
            "fabrica_directo": {
                "descripcion": "Precios para compras directas a fábrica o en local",
                "campos": {
                    "precio_iva": "Precio de venta + IVA (IVA se suma al precio)",
                    "precio_iva_incluido": "Precio de venta con IVA incluido (precio final al consumidor)"
                }
            },
            "web_stock": {
                "descripcion": "Precios para compras web o desde stock",
                "campos": {
                    "precio_iva": "Precio de venta + IVA (IVA se suma al precio)",
                    "precio_iva_incluido": "Precio de venta con IVA incluido (precio final al consumidor)"
                }
            }
        },
        "notas": {
            "moneda": "USD",
            "iva": "22%",
            "costo_proveedor": "Incluye IVA",
            "actualizacion": "Datos actualizados según matriz 2026"
        }
    }
    
    return kb_structure

def main():
    csv_path = "MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv"
    output_path = "BMC_Costos_Precios_2026.json"
    
    print(f"📊 Parseando CSV: {csv_path}")
    kb_data = parse_csv_to_knowledge_base(csv_path)
    
    print(f"✅ Productos principales encontrados: {len(kb_data['productos_principales'])} categorías")
    print(f"✅ Accesorios encontrados: {len(kb_data['accesorios'])}")
    print(f"✅ Servicios encontrados: {len(kb_data['servicios'])}")
    
    # Contar productos totales
    total_products = sum(len(cat["productos"]) for cat in kb_data['productos_principales'].values())
    total_products += len(kb_data['accesorios']) + len(kb_data['servicios'])
    print(f"📦 Total de productos: {total_products}")
    
    # Guardar JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(kb_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Base de conocimiento guardada en: {output_path}")
    
    # Mostrar resumen por categoría
    print("\n📋 Resumen por categoría:")
    for key, cat_data in kb_data['productos_principales'].items():
        print(f"  - {key}: {len(cat_data['productos'])} productos")

if __name__ == "__main__":
    main()
