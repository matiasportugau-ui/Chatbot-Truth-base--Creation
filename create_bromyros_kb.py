#!/usr/bin/env python3
"""
Script to parse BROMYROS cost matrix CSV and create knowledge base JSON
"""

import csv
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

def clean_value(value: str) -> Optional[float]:
    """Clean and convert value to float"""
    if not value or value.strip() == '':
        return None
    # Remove commas and convert
    try:
        return float(value.replace(',', '').strip())
    except (ValueError, AttributeError):
        return None

def clean_string(value: str) -> Optional[str]:
    """Clean string value"""
    if not value or value.strip() == '':
        return None
    return value.strip()

def extract_espesor(product_name: str) -> Optional[str]:
    """Extract espesor (thickness) from product name"""
    # Look for patterns like "30 mm", "50mm", "100 mm", etc.
    match = re.search(r'(\d+)\s*mm', product_name, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def categorize_product(product_name: str, code: str) -> str:
    """Categorize product based on name and code"""
    name_lower = product_name.lower()
    code_upper = code.upper()
    
    # ISOROOF
    if 'isoroof' in name_lower or code_upper.startswith('IROOF') or code_upper.startswith('IAGRO'):
        if 'colonial' in name_lower:
            return 'ISOROOF_COLONIAL'
        elif 'plus' in name_lower or 'PLS' in code_upper:
            return 'ISOROOF_PLUS'
        elif 'foil' in name_lower:
            return 'ISOROOF_FOIL'
        else:
            return 'ISOROOF'
    
    # ISODEC
    if 'isodec' in name_lower or code_upper.startswith('ISD'):
        if 'pir' in name_lower or 'PIR' in code_upper:
            return 'ISODEC_PIR'
        else:
            return 'ISODEC_EPS'
    
    # ISOPANEL
    if 'isopanel' in name_lower or code_upper.startswith('ISD') and 'EPS' in code_upper:
        return 'ISOPANEL_EPS'
    
    # ISOWALL
    if 'isowall' in name_lower or code_upper.startswith('IW'):
        if 'pir' in name_lower:
            return 'ISOWALL_PIR'
        else:
            return 'ISOWALL'
    
    # ISOFRIG
    if 'isofrig' in name_lower or code_upper.startswith('IF'):
        return 'ISOFRIG'
    
    # Accessories
    if 'gotero' in name_lower or code_upper.startswith('GF') or code_upper.startswith('GL') or code_upper.startswith('GSDECAM') or code_upper.startswith('GLDCAM'):
        if 'frontal' in name_lower:
            return 'GOTERO_FRONTAL'
        elif 'lateral' in name_lower:
            return 'GOTERO_LATERAL'
        else:
            return 'GOTERO'
    
    if 'babeta' in name_lower or code_upper.startswith('BB'):
        return 'BABETAS'
    
    if 'canalón' in name_lower or 'canalon' in name_lower or code_upper.startswith('CD') or code_upper.startswith('CAN'):
        return 'CANALON'
    
    if 'cumbrera' in name_lower or code_upper.startswith('CUM'):
        return 'CUMBRERAS'
    
    if 'perfil' in name_lower or code_upper.startswith('PU') or code_upper.startswith('PERFIL'):
        return 'PERFILES'
    
    if 'varilla' in name_lower or 'tuerca' in name_lower or 'arandela' in name_lower or 'taco' in name_lower:
        return 'ANCLAJES'
    
    if 'flete' in name_lower or code_upper.startswith('FLETE'):
        return 'FLETE'
    
    if 'cinta' in name_lower or 'butilo' in name_lower:
        return 'ACCESORIOS'
    
    if 'caballete' in name_lower or code_upper.startswith('CAB'):
        return 'ACCESORIOS'
    
    if 'silicona' in name_lower or 'bromplast' in name_lower:
        return 'ACCESORIOS'
    
    if 'eps' in name_lower and 'cat' in name_lower:
        return 'EPS_PAQUETES'
    
    return 'OTROS'

def parse_csv_to_kb(csv_path: str) -> Dict[str, Any]:
    """Parse CSV and create knowledge base structure"""
    
    products_by_category: Dict[str, List[Dict[str, Any]]] = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Skip header rows (first 3 rows)
    for i, row in enumerate(rows[3:], start=4):
        if len(row) < 5:
            continue
        
        # Extract data
        shopify_note = clean_string(row[0]) if len(row) > 0 else None
        notes = clean_string(row[1]) if len(row) > 1 else None
        status = clean_string(row[2]) if len(row) > 2 else None
        code = clean_string(row[3]) if len(row) > 3 else None
        product_name = clean_string(row[4]) if len(row) > 4 else None
        
        # Skip if no product name
        if not product_name or product_name == '':
            continue
        
        # Skip header rows and empty rows
        if 'Producto' in product_name or 'Precio' in product_name or product_name.startswith('ISOROOF') or product_name.startswith('ISODEC') or product_name.startswith('ISOPANEL'):
            continue
        
        # Extract pricing data
        costo_fabrica = clean_value(row[5]) if len(row) > 5 else None  # Costo m2 U$S + IVA (column 5)
        costo_con_aumento = clean_value(row[6]) if len(row) > 6 else None  # Con AUMENTO (column 6)
        costo_proximo_aumento = clean_value(row[7]) if len(row) > 7 else None  # Proximo AUMENTO (column 7)
        margen = clean_string(row[8]) if len(row) > 8 else None  # Margen % (column 8)
        ganancia = clean_value(row[10]) if len(row) > 10 else None  # Ganancia (column 10)
        venta_iva = clean_value(row[11]) if len(row) > 11 else None  # Venta + IVA (column 11) - for companies
        consumidor_iva_inc = clean_value(row[12]) if len(row) > 12 else None  # CONSUMIDOR IVA INC. (column 12) - for individuals
        web_venta_iva = clean_value(row[14]) if len(row) > 14 else None  # WEB Venta + IVA (column 14)
        web_venta_iva_inc = clean_value(row[15]) if len(row) > 15 else None  # WEB Venta IVA inc. (column 15)
        
        # Extract espesor
        espesor = extract_espesor(product_name)
        
        # Categorize
        category = categorize_product(product_name, code or '')
        
        # Create product entry
        product = {
            "codigo": code,
            "nombre": product_name,
            "espesor": espesor,
            "status": status,
            "costos": {
                "fabrica_directo": {
                    "costo_m2_usd_iva": costo_fabrica,
                    "costo_con_aumento": costo_con_aumento,
                    "costo_proximo_aumento": costo_proximo_aumento
                }
            },
            "precios": {
                "empresa": {
                    "venta_iva": venta_iva,  # Precio + IVA (companies discount IVA)
                    "nota": "Empresas descuentan IVA, usar precio + IVA"
                },
                "particular": {
                    "consumidor_iva_inc": consumidor_iva_inc,  # Precio IVA incluido (individuals)
                    "nota": "Particulares no descuentan IVA, usar precio IVA incluido"
                },
                "web_stock": {
                    "web_venta_iva": web_venta_iva,
                    "web_venta_iva_inc": web_venta_iva_inc
                }
            },
            "margen": margen,
            "ganancia": ganancia,
            "notas": {
                "shopify": shopify_note,
                "generales": notes,
                "cotizacion": "SIEMPRE usar 'venta_iva' para cotizar y agregar IVA al final"
            }
        }
        
        # Add to category
        if category not in products_by_category:
            products_by_category[category] = []
        
        products_by_category[category].append(product)
    
    # Create knowledge base structure
    kb = {
        "meta": {
            "nombre": "BROMYROS - Matriz de Costos y Ventas 2026",
            "version": "1.0",
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "fuente": "MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv",
            "descripcion": "Base de conocimiento de costos y precios BROMYROS para agentes internos"
        },
        "reglas_precios": {
            "empresa": {
                "descripcion": "Empresas descuentan IVA",
                "precio_a_usar": "venta_iva",
                "campo": "precios.empresa.venta_iva"
            },
            "particular": {
                "descripcion": "Particulares no descuentan IVA",
                "precio_a_usar": "consumidor_iva_inc",
                "campo": "precios.particular.consumidor_iva_inc"
            },
            "cotizacion": {
                "descripcion": "SIEMPRE usar precio + IVA y agregar IVA al final",
                "precio_base": "precios.empresa.venta_iva",
                "iva": 0.22,
                "nota": "En cotizaciones, siempre usar venta_iva y calcular IVA por separado al final"
            },
            "web_stock": {
                "descripcion": "Precios para compras web o stock",
                "campos": ["precios.web_stock.web_venta_iva", "precios.web_stock.web_venta_iva_inc"]
            }
        },
        "costos": {
            "fabrica_directo": {
                "descripcion": "Costos de compra directa a fábrica",
                "campo": "costos.fabrica_directo.costo_m2_usd_iva",
                "nota": "Costo por m² en USD con IVA incluido"
            }
        },
        "productos": products_by_category
    }
    
    return kb

def main():
    csv_path = "MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv"
    output_path = "BROMYROS_Base_Costos_Precios_2026.json"
    
    print(f"Parsing CSV: {csv_path}")
    kb = parse_csv_to_kb(csv_path)
    
    print(f"Creating knowledge base: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)
    
    # Print summary
    total_products = sum(len(products) for products in kb["productos"].values())
    print(f"\n✅ Knowledge base created successfully!")
    print(f"   Total products: {total_products}")
    print(f"   Categories: {len(kb['productos'])}")
    print(f"\nCategories:")
    for category, products in kb["productos"].items():
        print(f"   - {category}: {len(products)} products")

if __name__ == "__main__":
    main()
