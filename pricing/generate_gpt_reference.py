#!/usr/bin/env python3
"""
GPT Pricing Reference Generator
Extracts simplified pricing data for the AI Assistant from the raw Cost Matrix.
Includes detailed metadata (thickness, length, type, etc.) as requested.
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configuration
SOURCE_FILE = "wiki/matriz de costos adaptacion /MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv"
OUTPUT_FILE = "pricing/out/bromyros_pricing_reference.json"
IVA_RATE = 0.22

# --- Extraction Logic (ported from price_base_parser.py to ensure consistency) ---

def clean_price(value: str) -> float:
    """Parse price string to float, handling commas and spaces."""
    if not value:
        return 0.0
    try:
        clean = value.replace(' ', '').replace(',', '.')
        return float(clean)
    except ValueError:
        return 0.0

def extract_thickness_mm(sku: str, name: str) -> Optional[int]:
    sku_upper = sku.upper() if sku else ""
    # Pattern for SKU like ISD100EPS, IW80PIR, IROOF30
    match = re.search(r'(?:ISD|IW|IROOF|IAGRO)(\d+)', sku_upper)
    if match:
        return int(match.group(1))
    
    # Try name (e.g., "100mm", "80 mm")
    name_lower = name.lower() if name else ""
    match = re.search(r'(\d+)\s*mm', name_lower, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def extract_length_m(name: str) -> Optional[float]:
    if not name:
        return None
    name_lower = name.lower()
    
    match = re.search(r'(\d+)\s*piezas?\s+de\s+(\d+[.,]?\d*)\s*m', name_lower)
    if match:
        pieces = int(match.group(1))
        length = float(match.group(2).replace(',', '.'))
        return pieces * length
    
    patterns = [
        r'largo\s+(\d+[.,]?\d*)\s*m',
        r'de\s+(\d+[.,]?\d*)\s*m',
        r'/\s*(\d+[.,]?\d*)\s*m',
        r'\((\d+[.,]?\d*)\s*m\)',
        r'(\d+[.,]?\d*)\s*m(?:\s|$)',
    ]
    for pattern in patterns:
        match = re.search(pattern, name_lower)
        if match:
            return float(match.group(1).replace(',', '.'))
    return None

def categorize_product(sku: str, name: str) -> Dict[str, Any]:
    sku_upper = sku.upper() if sku else ""
    name_lower = name.lower() if name else ""
    
    category = {
        "tipo": "otro",
        "familia": "accesorio",
        "unit_base": "unidad",
        "needs_length": False
    }
    
    if any(kw in sku_upper for kw in ["ISD", "IW", "IROOF", "IAGRO", "IF"]):
        if "PIR" in name_lower or "PIR" in sku_upper:
            if "IWALL" in sku_upper or "IW" in sku_upper:
                category.update({"tipo": "panel", "familia": "ISOWALL_PIR", "unit_base": "m2"})
            elif "ISODEC" in name_lower or "ISD" in sku_upper:
                category.update({"tipo": "panel", "familia": "ISODEC_PIR", "unit_base": "m2"})
            elif "ISOFRIG" in name_lower or "IF" in sku_upper:
                category.update({"tipo": "panel", "familia": "ISOFRIG_PIR", "unit_base": "m2"})
        else:
            if "ISOROOF" in name_lower or "IROOF" in sku_upper or "IAGRO" in sku_upper:
                category.update({"tipo": "panel", "familia": "ISOROOF_3G", "unit_base": "m2"})
            elif "PARED" in name_lower or "FACHADA" in name_lower or "WALL" in name_lower:
                category.update({"tipo": "panel", "familia": "ISOPANEL_EPS", "unit_base": "m2"})
            else:
                category.update({"tipo": "panel", "familia": "ISODEC_EPS", "unit_base": "m2"})
    
    elif any(kw in name_lower for kw in ["perfil", "canalon", "canal", "cumbrera", "babeta", "gotero"]):
        category.update({
            "tipo": "perfil",
            "unit_base": "metro_lineal",
            "needs_length": True
        })
        if "gotero" in name_lower: category["familia"] = "gotero"
        elif "canal" in name_lower: category["familia"] = "canalon"
        elif "cumbrera" in name_lower: category["familia"] = "cumbrera"
        elif "babeta" in name_lower: category["familia"] = "babeta"
        elif "perfil" in name_lower: category["familia"] = "perfil"
    
    elif any(kw in name_lower for kw in ["varilla", "tuerca", "arandela", "taco", "caballete", "tornillo"]):
        category.update({"tipo": "accesorio", "familia": "anclaje", "unit_base": "unidad"})
    elif any(kw in name_lower for kw in ["cinta", "silicona", "pistola", "remache"]):
        category.update({"tipo": "accesorio", "familia": "consumible", "unit_base": "unidad"})
    
    return category

def generate_reference():
    source_path = Path(SOURCE_FILE)
    if not source_path.exists():
        print(f"Error: Source file not found at {source_path}")
        return

    products: Dict[str, Any] = {}
    duplicates = []

    with open(source_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    for i, row in enumerate(rows):
        if len(row) < 13: 
            continue
            
        status = row[2].strip()
        sku = row[3].strip()
        name = row[4].strip()
        
        # Include if SKU exists and Status is not 'x' (exclude explicit deleted)
        if not sku or status == "x":
            continue
            
        # Extract Prices
        cost_ex_iva = clean_price(row[5]) if len(row) > 5 else 0.0
        price_ex_iva = clean_price(row[11])
        price_inc_iva = clean_price(row[12])
        web_price_inc_iva = clean_price(row[20]) if len(row) > 20 else 0.0
        
        if price_inc_iva == 0 and price_ex_iva > 0:
            price_inc_iva = round(price_ex_iva * (1 + IVA_RATE), 2)
        if web_price_inc_iva == 0:
            web_price_inc_iva = price_inc_iva

        # Extract Metadata
        thickness = extract_thickness_mm(sku, name)
        length = extract_length_m(name)
        cat = categorize_product(sku, name)

        # Handle Duplicates
        final_sku = sku
        if sku in products:
            existing = products[sku]
            if existing['name'] == name and abs(existing['price_usd'] - price_inc_iva) < 0.1:
                continue
            count = 1
            while f"{sku}_{count}" in products:
                count += 1
            final_sku = f"{sku}_{count}"
            duplicates.append(f"{sku} -> {final_sku} ({name})")

        product_entry = {
            "id": final_sku,
            "sku": sku,
            "name": name,
            "description": name,
            "stock_status": "In Stock" if status == "ACT." else "Check Availability",
            # Pricing
            "price_usd": price_inc_iva,     # Customer Price (Inc IVA)
            "sale_price_usd_ex_iva": price_ex_iva, # Sale Ex IVA
            "cost_usd_ex_iva": cost_ex_iva, # Internal Cost Ex IVA
            "web_price_usd": web_price_inc_iva,
            # Metadata
            "thickness_mm": thickness,
            "length_m": length,
            "type": cat["tipo"],
            "family": cat["familia"],
            "unit_base": cat["unit_base"]
        }
        
        products[final_sku] = product_entry

    product_list = list(products.values())
    
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"products": product_list, "meta": {"total": len(product_list)}}, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully generated pricing reference with {len(product_list)} products.")
    if duplicates:
        print(f"Handled {len(duplicates)} duplicates (suffixed):")
        for d in duplicates[:5]:
            print(f"- {d}")

if __name__ == "__main__":
    generate_reference()
