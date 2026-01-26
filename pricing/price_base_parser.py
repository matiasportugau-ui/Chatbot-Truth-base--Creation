#!/usr/bin/env python3
"""
Price Base Parser for Bromyros Sheet Export

Parses CSV/XLSX export with column layout:
- D: SKU
- E: product name + notes
- F: cost sin IVA
- L: sale price sin IVA
- M: sale price IVA inc.
- T: web sale price sin IVA (optional)
- U: web sale price IVA inc. (optional)

Normalizes units, extracts thickness/length, and computes derived fields.
"""

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import openpyxl


def clean_number(value: Union[str, float, int, None]) -> Optional[float]:
    """
    Clean and parse a number that may have comma decimals and whitespace.
    
    Args:
        value: Raw value from spreadsheet
        
    Returns:
        Parsed float or None if invalid/empty
    """
    if value is None:
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if not isinstance(value, str):
        return None
        
    # Remove whitespace and replace comma with dot
    cleaned = str(value).strip().replace(',', '.').replace(' ', '')
    
    if not cleaned or cleaned == '':
        return None
    
    try:
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def extract_thickness_mm(sku: str, name: str) -> Optional[int]:
    """
    Extract thickness in mm from SKU and/or product name.
    
    Patterns:
    - SKU: ISD100EPS, IW80PIR, IROOF30 → extract numeric part
    - Name: "100mm", "80 mm", etc.
    
    Args:
        sku: Product SKU
        name: Product name
        
    Returns:
        Thickness in mm as integer, or None
    """
    # Try SKU first (e.g., ISD100EPS → 100)
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
    """
    Extract piece length in meters from product name.
    
    Patterns:
    - "/ 3 m" → 3.0
    - "(3,03m)" → 3.03
    - "de 6,8 m" → 6.8
    - "largo 2,2 m" → 2.2
    - "2 piezas de 1,1m" → 2.2 (total)
    - "3m" → 3.0
    
    Args:
        name: Product name
        
    Returns:
        Length in meters, or None if can't confidently extract
    """
    if not name:
        return None
    
    name_lower = name.lower()
    
    # Pattern: "2 piezas de 1,1m" → multiply pieces × length
    match = re.search(r'(\d+)\s*piezas?\s+de\s+(\d+[.,]?\d*)\s*m', name_lower)
    if match:
        pieces = int(match.group(1))
        length = float(match.group(2).replace(',', '.'))
        return pieces * length
    
    # Pattern: "largo X m", "de X m", "/ X m", "(X m)", "Xm"
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
    """
    Categorize product and determine base unit.
    
    Categories:
    - Panels (EPS/PIR): m2
    - Profiles/gutters/cumbreras/babetas: piece + metro lineal
    - Hardware/consumables: unidad
    
    Args:
        sku: Product SKU
        name: Product name
        
    Returns:
        Dict with tipo, familia, unit_base, needs_length
    """
    sku_upper = sku.upper() if sku else ""
    name_lower = name.lower() if name else ""
    
    # Default
    category = {
        "tipo": "otro",
        "familia": "accesorio",
        "unit_base": "unidad",
        "needs_length": False
    }
    
    # PANELS - unit_base = m2
    if any(kw in sku_upper for kw in ["ISD", "IW", "IROOF", "IAGRO", "IF"]):
        if "PIR" in name_lower or "PIR" in sku_upper:
            if "IWALL" in sku_upper or "IW" in sku_upper:
                category.update({"tipo": "panel", "familia": "ISOWALL_PIR", "unit_base": "m2"})
            elif "ISODEC" in name_lower or "ISD" in sku_upper:
                category.update({"tipo": "panel", "familia": "ISODEC_PIR", "unit_base": "m2"})
            elif "ISOFRIG" in name_lower or "IF" in sku_upper:
                category.update({"tipo": "panel", "familia": "ISOFRIG_PIR", "unit_base": "m2"})
        else:
            # EPS
            if "ISOROOF" in name_lower or "IROOF" in sku_upper or "IAGRO" in sku_upper:
                category.update({"tipo": "panel", "familia": "ISOROOF_3G", "unit_base": "m2"})
            elif "PARED" in name_lower or "FACHADA" in name_lower or "WALL" in name_lower:
                category.update({"tipo": "panel", "familia": "ISOPANEL_EPS", "unit_base": "m2"})
            else:
                # Default EPS techo
                category.update({"tipo": "panel", "familia": "ISODEC_EPS", "unit_base": "m2"})
    
    # PROFILES/GUTTERS/etc. - needs_length for per_ml conversion
    elif any(kw in name_lower for kw in ["perfil", "canalon", "canal", "cumbrera", "babeta", "gotero"]):
        category.update({
            "tipo": "perfil",
            "unit_base": "metro_lineal",
            "needs_length": True
        })
        
        if "gotero" in name_lower:
            category["familia"] = "gotero"
        elif "canal" in name_lower:
            category["familia"] = "canalon"
        elif "cumbrera" in name_lower:
            category["familia"] = "cumbrera"
        elif "babeta" in name_lower:
            category["familia"] = "babeta"
        elif "perfil" in name_lower:
            category["familia"] = "perfil"
    
    # HARDWARE - unit_base = unidad
    elif any(kw in name_lower for kw in ["varilla", "tuerca", "arandela", "taco", "caballete", "tornillo"]):
        category.update({
            "tipo": "accesorio",
            "familia": "anclaje",
            "unit_base": "unidad",
            "needs_length": False
        })
    
    # OTHER CONSUMABLES
    elif any(kw in name_lower for kw in ["cinta", "silicona", "pistola", "remache"]):
        category.update({
            "tipo": "accesorio",
            "familia": "consumible",
            "unit_base": "unidad",
            "needs_length": False
        })
    
    return category


def compute_derived_fields(row_data: Dict[str, Any], iva_rate: float = 0.22) -> Dict[str, Any]:
    """
    Compute derived fields: margins, per_ml prices, IVA consistency flags.
    
    Args:
        row_data: Parsed row with cost/prices
        iva_rate: IVA rate (default 0.22)
        
    Returns:
        Dict with computed fields
    """
    derived = {
        "margins": {},
        "per_ml": {},
        "iva_checks": {}
    }
    
    cost_sin_iva = row_data.get("cost_sin_iva")
    sale_sin_iva = row_data.get("sale_sin_iva")
    sale_iva_inc = row_data.get("sale_iva_inc")
    web_sin_iva = row_data.get("web_sin_iva")
    web_iva_inc = row_data.get("web_iva_inc")
    length_m = row_data.get("length_m")
    
    # Business margin (net prices)
    if sale_sin_iva and cost_sin_iva and sale_sin_iva > 0:
        derived["margins"]["business_margin_pct"] = round(((sale_sin_iva - cost_sin_iva) / sale_sin_iva) * 100, 2)
    
    if web_sin_iva and cost_sin_iva and web_sin_iva > 0:
        derived["margins"]["web_margin_pct"] = round(((web_sin_iva - cost_sin_iva) / web_sin_iva) * 100, 2)
    
    # Gross margin (with IVA, sanity check only)
    if sale_iva_inc and cost_sin_iva and sale_iva_inc > 0:
        derived["margins"]["gross_margin_pct"] = round(((sale_iva_inc - cost_sin_iva) / sale_iva_inc) * 100, 2)
    
    # IVA consistency checks (tolerance ±1%)
    tolerance = 0.01
    
    if sale_sin_iva and sale_iva_inc:
        expected_iva_inc = sale_sin_iva * (1 + iva_rate)
        delta_pct = abs(sale_iva_inc - expected_iva_inc) / expected_iva_inc if expected_iva_inc > 0 else 0
        derived["iva_checks"]["sale_iva_consistent"] = delta_pct <= tolerance
        derived["iva_checks"]["sale_iva_delta_pct"] = round(delta_pct * 100, 2)
    
    if web_sin_iva and web_iva_inc:
        expected_iva_inc = web_sin_iva * (1 + iva_rate)
        delta_pct = abs(web_iva_inc - expected_iva_inc) / expected_iva_inc if expected_iva_inc > 0 else 0
        derived["iva_checks"]["web_iva_consistent"] = delta_pct <= tolerance
        derived["iva_checks"]["web_iva_delta_pct"] = round(delta_pct * 100, 2)
    
    # Per metro lineal prices (for profiles/pieces with known length)
    if length_m and length_m > 0:
        if sale_sin_iva:
            derived["per_ml"]["sale_sin_iva_per_ml"] = round(sale_sin_iva / length_m, 2)
        if sale_iva_inc:
            derived["per_ml"]["sale_iva_inc_per_ml"] = round(sale_iva_inc / length_m, 2)
        if web_sin_iva:
            derived["per_ml"]["web_sin_iva_per_ml"] = round(web_sin_iva / length_m, 2)
        if web_iva_inc:
            derived["per_ml"]["web_iva_inc_per_ml"] = round(web_iva_inc / length_m, 2)
    
    return derived


def parse_csv_export(csv_path: Path, iva_rate: float = 0.22) -> List[Dict[str, Any]]:
    """
    Parse CSV export with Bromyros column layout.
    
    Column mapping (1-indexed Excel):
    - D (3): SKU
    - E (4): product name
    - F (5): cost sin IVA
    - L (11): sale price sin IVA
    - M (12): sale price IVA inc.
    - T (19): web sale price sin IVA
    - U (20): web sale price IVA inc.
    
    Args:
        csv_path: Path to CSV file
        iva_rate: IVA rate for validation (default 0.22)
        
    Returns:
        List of parsed product dicts
    """
    products = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    for i, row in enumerate(rows):
        # Skip header rows or rows with insufficient columns
        if len(row) < 20:
            continue
        
        # Extract core fields (0-indexed in Python)
        sku = row[3].strip() if len(row) > 3 else ""
        name = row[4].strip() if len(row) > 4 else ""
        
        # Only process rows with both SKU and name
        if not sku or not name:
            continue
        
        # Extract prices
        cost_sin_iva = clean_number(row[5]) if len(row) > 5 else None
        sale_sin_iva = clean_number(row[11]) if len(row) > 11 else None
        sale_iva_inc = clean_number(row[12]) if len(row) > 12 else None
        web_sin_iva = clean_number(row[19]) if len(row) > 19 else None
        web_iva_inc = clean_number(row[20]) if len(row) > 20 else None
        
        # Extract metadata
        thickness_mm = extract_thickness_mm(sku, name)
        length_m = extract_length_m(name)
        category = categorize_product(sku, name)
        
        # Build row data
        row_data = {
            "row_index": i + 1,
            "sku": sku,
            "name": name,
            "thickness_mm": thickness_mm,
            "length_m": length_m,
            "category": category,
            "cost_sin_iva": cost_sin_iva,
            "sale_sin_iva": sale_sin_iva,
            "sale_iva_inc": sale_iva_inc,
            "web_sin_iva": web_sin_iva,
            "web_iva_inc": web_iva_inc,
        }
        
        # Compute derived fields
        derived = compute_derived_fields(row_data, iva_rate)
        row_data.update(derived)
        
        products.append(row_data)
    
    return products


def parse_xlsx_export(xlsx_path: Path, iva_rate: float = 0.22) -> List[Dict[str, Any]]:
    """
    Parse XLSX export with Bromyros column layout.
    
    Uses openpyxl to read .xlsx directly.
    
    Args:
        xlsx_path: Path to XLSX file
        iva_rate: IVA rate for validation
        
    Returns:
        List of parsed product dicts
    """
    products = []
    
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb.active
    
    for i, row in enumerate(ws.iter_rows(min_row=1, values_only=True), start=1):
        # Skip rows with insufficient columns
        if len(row) < 20:
            continue
        
        # Extract core fields (0-indexed)
        sku = str(row[3]).strip() if row[3] else ""
        name = str(row[4]).strip() if row[4] else ""
        
        # Only process rows with both SKU and name
        if not sku or not name or sku == "None" or name == "None":
            continue
        
        # Extract prices
        cost_sin_iva = clean_number(row[5]) if len(row) > 5 else None
        sale_sin_iva = clean_number(row[11]) if len(row) > 11 else None
        sale_iva_inc = clean_number(row[12]) if len(row) > 12 else None
        web_sin_iva = clean_number(row[19]) if len(row) > 19 else None
        web_iva_inc = clean_number(row[20]) if len(row) > 20 else None
        
        # Extract metadata
        thickness_mm = extract_thickness_mm(sku, name)
        length_m = extract_length_m(name)
        category = categorize_product(sku, name)
        
        # Build row data
        row_data = {
            "row_index": i,
            "sku": sku,
            "name": name,
            "thickness_mm": thickness_mm,
            "length_m": length_m,
            "category": category,
            "cost_sin_iva": cost_sin_iva,
            "sale_sin_iva": sale_sin_iva,
            "sale_iva_inc": sale_iva_inc,
            "web_sin_iva": web_sin_iva,
            "web_iva_inc": web_iva_inc,
        }
        
        # Compute derived fields
        derived = compute_derived_fields(row_data, iva_rate)
        row_data.update(derived)
        
        products.append(row_data)
    
    return products


def parse_price_base(input_path: Union[str, Path], iva_rate: float = 0.22) -> Dict[str, Any]:
    """
    Main entry point: parse CSV or XLSX export into canonical price base.
    
    Args:
        input_path: Path to CSV or XLSX file
        iva_rate: IVA rate (default 0.22, read from KB if available)
        
    Returns:
        Dict with metadata and products list
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Parse based on extension
    if input_path.suffix.lower() == '.csv':
        products = parse_csv_export(input_path, iva_rate)
    elif input_path.suffix.lower() in ['.xlsx', '.xls']:
        products = parse_xlsx_export(input_path, iva_rate)
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")
    
    # Build canonical structure
    price_base = {
        "meta": {
            "source_file": str(input_path.name),
            "parsed_at": datetime.now().isoformat(),
            "iva_rate": iva_rate,
            "total_products": len(products),
            "unique_skus": len(set(p["sku"] for p in products)),
        },
        "products": products
    }
    
    return price_base


def save_price_base(price_base: Dict[str, Any], output_dir: Union[str, Path], 
                    save_csv: bool = True, save_json: bool = True) -> Dict[str, Path]:
    """
    Save price base to JSON and optionally CSV.
    
    Args:
        price_base: Parsed price base dict
        output_dir: Output directory
        save_csv: Whether to save CSV version
        save_json: Whether to save JSON version
        
    Returns:
        Dict with paths to saved files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    # Save JSON
    if save_json:
        json_path = output_dir / "bromyros_price_base_v1.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(price_base, f, indent=2, ensure_ascii=False)
        saved_files["json"] = json_path
    
    # Save CSV (flattened)
    if save_csv:
        csv_path = output_dir / "bromyros_price_base_v1.csv"
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            if not price_base["products"]:
                return saved_files
            
            # Define CSV columns
            fieldnames = [
                "sku", "name", "thickness_mm", "length_m",
                "tipo", "familia", "unit_base",
                "cost_sin_iva", "sale_sin_iva", "sale_iva_inc",
                "web_sin_iva", "web_iva_inc",
                "business_margin_pct", "web_margin_pct",
                "sale_iva_consistent", "web_iva_consistent",
                "sale_sin_iva_per_ml", "sale_iva_inc_per_ml"
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for p in price_base["products"]:
                row = {
                    "sku": p["sku"],
                    "name": p["name"],
                    "thickness_mm": p.get("thickness_mm"),
                    "length_m": p.get("length_m"),
                    "tipo": p["category"]["tipo"],
                    "familia": p["category"]["familia"],
                    "unit_base": p["category"]["unit_base"],
                    "cost_sin_iva": p.get("cost_sin_iva"),
                    "sale_sin_iva": p.get("sale_sin_iva"),
                    "sale_iva_inc": p.get("sale_iva_inc"),
                    "web_sin_iva": p.get("web_sin_iva"),
                    "web_iva_inc": p.get("web_iva_inc"),
                    "business_margin_pct": p.get("margins", {}).get("business_margin_pct"),
                    "web_margin_pct": p.get("margins", {}).get("web_margin_pct"),
                    "sale_iva_consistent": p.get("iva_checks", {}).get("sale_iva_consistent"),
                    "web_iva_consistent": p.get("iva_checks", {}).get("web_iva_consistent"),
                    "sale_sin_iva_per_ml": p.get("per_ml", {}).get("sale_sin_iva_per_ml"),
                    "sale_iva_inc_per_ml": p.get("per_ml", {}).get("sale_iva_inc_per_ml"),
                }
                writer.writerow(row)
        
        saved_files["csv"] = csv_path
    
    return saved_files
