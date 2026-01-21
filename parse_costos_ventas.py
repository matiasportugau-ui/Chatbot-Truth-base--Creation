#!/usr/bin/env python3
"""
Script para parsear la matriz de costos y ventas y crear una knowledge base estructurada.
"""

import csv
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any

def clean_value(value: str) -> Optional[float]:
    """Limpia y convierte un valor a float."""
    if not value or value.strip() == '':
        return None
    # Remover espacios y convertir comas a puntos
    cleaned = value.strip().replace(',', '.')
    try:
        return float(cleaned)
    except (ValueError, AttributeError):
        return None

def extract_espesor(product_name: str) -> Optional[str]:
    """Extrae el espesor del nombre del producto."""
    # Buscar patrones como "30 mm", "100mm", "50mm", etc.
    match = re.search(r'(\d+)\s*mm', product_name, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def categorize_product(product_name: str, code: str) -> Dict[str, Any]:
    """Categoriza el producto según su nombre y código."""
    name_lower = product_name.lower()
    code_upper = code.upper() if code else ""
    
    category = {
        "tipo": "otro",
        "familia": "accesorio",
        "unidad": "m2"
    }
    
    # ISOROOF
    if "isoroof" in name_lower or code_upper.startswith("IROOF") or code_upper.startswith("IAGRO"):
        category["tipo"] = "cubierta_liviana"
        category["familia"] = "isoroof"
        if "foil" in name_lower:
            category["variante"] = "foil"
        elif "plus" in name_lower:
            category["variante"] = "plus"
        elif "colonial" in name_lower:
            category["variante"] = "colonial"
        else:
            category["variante"] = "standard"
    
    # ISODEC / ISOPANEL EPS
    elif "isodec" in name_lower or "isopanel" in name_lower or code_upper.startswith("ISD"):
        if "pir" in name_lower:
            category["tipo"] = "cubierta_pesada"
            category["familia"] = "isodec_pir"
        else:
            category["tipo"] = "cubierta_pesada"
            category["familia"] = "isodec_eps"
    
    # ISOWALL
    elif "isowall" in name_lower or code_upper.startswith("IW"):
        category["tipo"] = "fachada"
        category["familia"] = "isowall"
    
    # ISOFRIG
    elif "isofrig" in name_lower or code_upper.startswith("IF"):
        category["tipo"] = "sala_limpia"
        category["familia"] = "isofrig"
    
    # Goteros
    elif "gotero" in name_lower or code_upper.startswith("GF") or code_upper.startswith("GL"):
        category["tipo"] = "accesorio"
        category["familia"] = "gotero"
        category["unidad"] = "metro_lineal"
    
    # Canalones
    elif "canal" in name_lower or code_upper.startswith("CD") or code_upper.startswith("CAN"):
        category["tipo"] = "accesorio"
        category["familia"] = "canalon"
        category["unidad"] = "metro_lineal"
    
    # Cumbreras
    elif "cumbrera" in name_lower or code_upper.startswith("CUM"):
        category["tipo"] = "accesorio"
        category["familia"] = "cumbrera"
        category["unidad"] = "metro_lineal"
    
    # Babetas
    elif "babeta" in name_lower or code_upper.startswith("BB"):
        category["tipo"] = "accesorio"
        category["familia"] = "babeta"
        category["unidad"] = "metro_lineal"
    
    # Perfiles
    elif "perfil" in name_lower or code_upper.startswith("PU") or code_upper.startswith("PL"):
        category["tipo"] = "accesorio"
        category["familia"] = "perfil"
        category["unidad"] = "metro_lineal"
    
    # Anclajes
    elif any(word in name_lower for word in ["varilla", "tuerca", "arandela", "taco", "caballete"]):
        category["tipo"] = "accesorio"
        category["familia"] = "anclaje"
        category["unidad"] = "unidad"
    
    # Otros accesorios
    elif any(word in name_lower for word in ["cinta", "silicona", "flete", "pistola"]):
        category["tipo"] = "accesorio"
        category["familia"] = "otro"
        category["unidad"] = "unidad" if "pistola" in name_lower or "cinta" in name_lower else "metro_lineal"
    
    return category

def parse_csv_to_knowledge_base(csv_path: str) -> Dict[str, Any]:
    """Parsea el CSV y crea una knowledge base estructurada."""
    
    kb = {
        "meta": {
            "nombre": "BMC Uruguay - Matriz de Costos y Ventas 2026",
            "version": "1.0.0",
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d"),
            "fuente": "MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv",
            "descripcion": "Base de conocimiento de costos y precios de venta para compras directas a fábrica y compras web/stock"
        },
        "precios": {
            "fabrica_directo": {},
            "web_stock": {}
        },
        "productos": []
    }
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Saltar las primeras 3 filas de encabezados
    data_rows = rows[3:]
    
    productos_por_familia = {}
    
    for row in data_rows:
        # Verificar que la fila tenga datos suficientes
        if len(row) < 20:
            continue
        
        # Extraer datos de la fila
        notas = row[0].strip() if len(row) > 0 else ""
        descripcion_notas = row[1].strip() if len(row) > 1 else ""
        estado = row[2].strip() if len(row) > 2 else ""
        codigo = row[3].strip() if len(row) > 3 else ""
        producto_nombre = row[4].strip() if len(row) > 4 else ""
        
        # Saltar filas vacías o sin producto
        if not producto_nombre or producto_nombre == "":
            continue
        
        # Saltar productos marcados como "NO SUBIR" o "DESCONTINUADO"
        if "NO SUBIR" in notas.upper() or "DESCONTINUADO" in descripcion_notas.upper():
            continue
        
        # Extraer costos y precios
        costo_m2_iva = clean_value(row[5]) if len(row) > 5 else None  # Costo m2 U$S + IVA
        costo_con_aumento = clean_value(row[6]) if len(row) > 6 else None  # Con AUMENTO
        costo_proximo_aumento = clean_value(row[7]) if len(row) > 7 else None  # Proximo AUMENTO
        margen_pct = row[8].strip() if len(row) > 8 else None  # Margen %
        ganancia = clean_value(row[10]) if len(row) > 10 else None  # Ganancia
        venta_iva = clean_value(row[11]) if len(row) > 11 else None  # Venta + IVA
        consumidor_iva_inc = clean_value(row[12]) if len(row) > 12 else None  # CONSUMIDOR IVA INC.
        web_venta_iva = clean_value(row[18]) if len(row) > 18 else None  # WEB Venta + IVA
        web_venta_iva_inc = clean_value(row[19]) if len(row) > 19 else None  # WEB Venta IVA inc.
        
        # Precio metro lineal (si existe)
        precio_ml = clean_value(row[20]) if len(row) > 20 else None
        
        # Categorizar producto
        categoria = categorize_product(producto_nombre, codigo)
        espesor = extract_espesor(producto_nombre)
        
        # Crear estructura del producto
        producto = {
            "codigo": codigo if codigo else None,
            "nombre": producto_nombre,
            "estado": estado if estado else "ACT.",
            "notas": notas if notas else None,
            "descripcion_notas": descripcion_notas if descripcion_notas else None,
            "categoria": categoria,
            "espesor_mm": espesor,
            "costos": {
                "fabrica_directo": {
                    "costo_m2_usd_iva": costo_m2_iva,
                    "costo_con_aumento": costo_con_aumento,
                    "costo_proximo_aumento": costo_proximo_aumento
                },
                "margen_porcentaje": margen_pct,
                "ganancia_usd": ganancia
            },
            "precios": {
                "venta_iva": venta_iva,
                "consumidor_iva_inc": consumidor_iva_inc,
                "web_venta_iva": web_venta_iva,
                "web_venta_iva_inc": web_venta_iva_inc
            },
            "precio_metro_lineal": precio_ml
        }
        
        # Agregar a la lista de productos
        kb["productos"].append(producto)
        
        # Organizar por familia para búsqueda rápida
        familia = categoria["familia"]
        if familia not in productos_por_familia:
            productos_por_familia[familia] = []
        productos_por_familia[familia].append(producto)
    
    # Agregar índice por familia
    kb["indice_familias"] = {
        familia: [p["codigo"] for p in productos if p["codigo"]]
        for familia, productos in productos_por_familia.items()
    }
    
    # Estadísticas
    kb["meta"]["estadisticas"] = {
        "total_productos": len(kb["productos"]),
        "productos_activos": len([p for p in kb["productos"] if p["estado"] == "ACT."]),
        "familias": len(productos_por_familia),
        "productos_con_costo_fabrica": len([p for p in kb["productos"] if p["costos"]["fabrica_directo"]["costo_m2_usd_iva"]]),
        "productos_con_precio_web": len([p for p in kb["productos"] if p["precios"]["web_venta_iva"]])
    }
    
    return kb

def main():
    csv_path = "MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv"
    output_path = "BMC_Matriz_Costos_Ventas_2026.json"
    
    print(f"📊 Parseando CSV: {csv_path}")
    kb = parse_csv_to_knowledge_base(csv_path)
    
    print(f"✅ Productos procesados: {kb['meta']['estadisticas']['total_productos']}")
    print(f"✅ Productos activos: {kb['meta']['estadisticas']['productos_activos']}")
    print(f"✅ Familias de productos: {kb['meta']['estadisticas']['familias']}")
    
    # Guardar JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Knowledge base guardada en: {output_path}")
    
    # Mostrar muestra de productos
    print("\n📋 Muestra de productos (primeros 5):")
    for i, producto in enumerate(kb["productos"][:5]):
        print(f"\n{i+1}. {producto['nombre']}")
        print(f"   Código: {producto['codigo']}")
        print(f"   Familia: {producto['categoria']['familia']}")
        if producto['costos']['fabrica_directo']['costo_m2_usd_iva']:
            print(f"   Costo fábrica: ${producto['costos']['fabrica_directo']['costo_m2_usd_iva']:.2f} USD/m²")
        if producto['precios']['web_venta_iva']:
            print(f"   Precio web: ${producto['precios']['web_venta_iva']:.2f} USD/m²")

if __name__ == "__main__":
    main()
