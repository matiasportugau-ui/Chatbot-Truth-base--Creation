#!/usr/bin/env python3
"""
KB Comparison Module

Compares parsed price base with BMC_Base_Conocimiento_GPT-2.json:
- Maps SKUs to KB product keys
- Matches thickness to KB espesores
- Compares consumer prices (sheet col M vs KB precio)
- Reports matches, mismatches, and missing items

Outputs comparison reports in CSV and Markdown formats.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple


# Mapping rules: SKU patterns → KB product keys
SKU_TO_KB_MAPPING = {
    # ISODEC/ISOPANEL EPS (techo vs pared disambiguation via keywords)
    r"ISD\d+EPS": {
        "default": "ISODEC_EPS",
        "pared_keywords": ["pared", "fachada", "wall"],
        "pared_key": "ISOPANEL_EPS"
    },
    # ISODEC PIR
    r"ISD\d+PIR": "ISODEC_PIR",
    # ISOWALL PIR
    r"IW\d+": "ISOWALL_PIR",
    # ISOROOF
    r"IROOF\d+": "ISOROOF_3G",
    r"IAGRO\d+": "ISOROOF_3G",
    # ISOFRIG PIR
    r"IF\d+": "ISOFRIG_PIR",
}


def load_kb_gpt2(kb_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load BMC_Base_Conocimiento_GPT-2.json.
    
    Args:
        kb_path: Path to KB JSON file
        
    Returns:
        KB dict
    """
    with open(kb_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def map_sku_to_kb_key(sku: str, name: str) -> Optional[str]:
    """
    Map SKU and product name to KB product key.
    
    Uses SKU patterns and name keywords for disambiguation.
    
    Args:
        sku: Product SKU
        name: Product name
        
    Returns:
        KB product key or None if no match
    """
    import re
    
    sku_upper = sku.upper() if sku else ""
    name_lower = name.lower() if name else ""
    
    # Try each mapping pattern
    for pattern, mapping in SKU_TO_KB_MAPPING.items():
        if re.match(pattern, sku_upper):
            # Simple string mapping
            if isinstance(mapping, str):
                return mapping
            
            # Disambiguation mapping (e.g., ISODEC EPS techo vs pared)
            if isinstance(mapping, dict):
                default = mapping.get("default")
                pared_keywords = mapping.get("pared_keywords", [])
                pared_key = mapping.get("pared_key")
                
                # Check if name contains pared/fachada keywords
                if pared_key and any(kw in name_lower for kw in pared_keywords):
                    return pared_key
                
                return default
    
    return None


def get_kb_price(kb: Dict[str, Any], product_key: str, thickness_mm: Optional[int]) -> Optional[float]:
    """
    Get consumer price (IVA inc) from KB for a given product key and thickness.
    
    Args:
        kb: KB dict
        product_key: KB product key (e.g., "ISODEC_EPS")
        thickness_mm: Thickness in mm
        
    Returns:
        KB precio (consumer price IVA inc) or None if not found
    """
    if not thickness_mm:
        return None
    
    products = kb.get("products", {})
    product = products.get(product_key)
    
    if not product:
        return None
    
    espesores = product.get("espesores", {})
    espesor = espesores.get(str(thickness_mm))
    
    if not espesor:
        return None
    
    return espesor.get("precio")


def compare_with_kb(price_base: Dict[str, Any], kb_path: Union[str, Path], 
                    tolerance_pct: float = 1.0) -> Dict[str, Any]:
    """
    Compare price base with KB master.
    
    Args:
        price_base: Parsed price base dict
        kb_path: Path to BMC_Base_Conocimiento_GPT-2.json
        tolerance_pct: Tolerance for price match (default 1%)
        
    Returns:
        Dict with comparison results
    """
    kb = load_kb_gpt2(kb_path)
    products = price_base["products"]
    
    comparison = {
        "meta": {
            "kb_file": str(Path(kb_path).name),
            "kb_version": kb.get("meta", {}).get("version", "unknown"),
            "tolerance_pct": tolerance_pct,
        },
        "matches": [],
        "mismatches": [],
        "missing_in_kb": [],
        "stats": {
            "total_comparisons": 0,
            "matches": 0,
            "mismatches": 0,
            "missing_in_kb": 0,
            "no_mapping": 0,
            "no_thickness": 0,
        }
    }
    
    stats = comparison["stats"]
    
    for p in products:
        sku = p["sku"]
        name = p["name"]
        thickness_mm = p.get("thickness_mm")
        
        # Only compare panels (skip profiles/consumables)
        if p.get("category", {}).get("tipo") != "panel":
            continue
        
        # Get consumer price from sheet (col M: sale_iva_inc)
        sheet_price = p.get("sale_iva_inc")
        
        if not sheet_price:
            continue
        
        stats["total_comparisons"] += 1
        
        # Map SKU to KB key
        kb_key = map_sku_to_kb_key(sku, name)
        
        if not kb_key:
            stats["no_mapping"] += 1
            continue
        
        if not thickness_mm:
            stats["no_thickness"] += 1
            continue
        
        # Get KB price
        kb_price = get_kb_price(kb, kb_key, thickness_mm)
        
        if not kb_price:
            stats["missing_in_kb"] += 1
            comparison["missing_in_kb"].append({
                "sku": sku,
                "name": name,
                "kb_key": kb_key,
                "thickness_mm": thickness_mm,
                "sheet_price": sheet_price,
                "message": f"Not found in KB: {kb_key} @ {thickness_mm}mm"
            })
            continue
        
        # Compare prices
        delta = sheet_price - kb_price
        delta_pct = abs(delta / kb_price * 100) if kb_price > 0 else 0
        
        is_match = delta_pct <= tolerance_pct
        
        result = {
            "sku": sku,
            "name": name,
            "kb_key": kb_key,
            "thickness_mm": thickness_mm,
            "sheet_price": round(sheet_price, 2),
            "kb_price": round(kb_price, 2),
            "delta": round(delta, 2),
            "delta_pct": round(delta_pct, 2),
        }
        
        if is_match:
            stats["matches"] += 1
            comparison["matches"].append(result)
        else:
            stats["mismatches"] += 1
            result["severity"] = "high" if delta_pct > 5 else "medium"
            result["message"] = f"Price mismatch: {delta_pct:.2f}% delta (${delta:+.2f})"
            comparison["mismatches"].append(result)
    
    return comparison


def check_missing_in_sheet(kb: Dict[str, Any], price_base: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Reverse check: find KB items not present in sheet.
    
    Args:
        kb: KB dict
        price_base: Parsed price base
        
    Returns:
        List of KB items missing from sheet
    """
    missing = []
    
    # Build set of (kb_key, thickness_mm) from sheet
    sheet_items = set()
    for p in price_base["products"]:
        if p.get("category", {}).get("tipo") != "panel":
            continue
        
        kb_key = map_sku_to_kb_key(p["sku"], p["name"])
        thickness_mm = p.get("thickness_mm")
        
        if kb_key and thickness_mm:
            sheet_items.add((kb_key, thickness_mm))
    
    # Check all KB items
    products = kb.get("products", {})
    
    for kb_key, product in products.items():
        espesores = product.get("espesores", {})
        
        for thickness_str, espesor_data in espesores.items():
            thickness_mm = int(thickness_str)
            precio = espesor_data.get("precio")
            
            if precio and (kb_key, thickness_mm) not in sheet_items:
                missing.append({
                    "kb_key": kb_key,
                    "thickness_mm": thickness_mm,
                    "kb_price": precio,
                    "message": f"Present in KB but missing from sheet: {kb_key} @ {thickness_mm}mm"
                })
    
    return missing


def save_comparison_reports(comparison: Dict[str, Any], output_dir: Union[str, Path],
                             include_reverse_check: bool = False,
                             missing_in_sheet: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Path]:
    """
    Save comparison reports to CSV and Markdown.
    
    Args:
        comparison: Comparison results dict
        output_dir: Output directory
        include_reverse_check: Whether to include reverse check results
        missing_in_sheet: Optional list of KB items missing from sheet
        
    Returns:
        Dict with paths to saved files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    # Save CSV with all comparison results
    csv_path = output_dir / "compare_kb_gpt2.csv"
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            "status", "sku", "name", "kb_key", "thickness_mm",
            "sheet_price", "kb_price", "delta", "delta_pct", "severity", "message"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write matches
        for item in comparison["matches"]:
            row = {
                "status": "match",
                "severity": "ok",
                "message": "Price matches within tolerance",
                **item
            }
            writer.writerow(row)
        
        # Write mismatches
        for item in comparison["mismatches"]:
            row = {
                "status": "mismatch",
                **item
            }
            writer.writerow(row)
        
        # Write missing in KB
        for item in comparison["missing_in_kb"]:
            row = {
                "status": "missing_in_kb",
                "severity": "medium",
                "delta": None,
                "delta_pct": None,
                "kb_price": None,
                **item
            }
            writer.writerow(row)
        
        # Write reverse check if included
        if include_reverse_check and missing_in_sheet:
            for item in missing_in_sheet:
                row = {
                    "status": "missing_in_sheet",
                    "sku": None,
                    "name": None,
                    "sheet_price": None,
                    "delta": None,
                    "delta_pct": None,
                    "severity": "info",
                    **item
                }
                writer.writerow(row)
    
    saved_files["csv"] = csv_path
    
    # Save Markdown summary
    md_path = output_dir / "compare_kb_gpt2.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Bromyros Price Base vs KB GPT-2 Comparison\n\n")
        
        meta = comparison["meta"]
        f.write("## Comparison Settings\n\n")
        f.write(f"- **KB file**: {meta['kb_file']}\n")
        f.write(f"- **KB version**: {meta['kb_version']}\n")
        f.write(f"- **Tolerance**: ±{meta['tolerance_pct']}%\n\n")
        
        stats = comparison["stats"]
        f.write("## Summary Statistics\n\n")
        f.write(f"- **Total comparisons**: {stats['total_comparisons']}\n")
        f.write(f"- **Matches**: {stats['matches']} ({stats['matches'] / stats['total_comparisons'] * 100:.1f}%)\n" if stats['total_comparisons'] > 0 else "- **Matches**: 0\n")
        f.write(f"- **Mismatches**: {stats['mismatches']} ({stats['mismatches'] / stats['total_comparisons'] * 100:.1f}%)\n" if stats['total_comparisons'] > 0 else "- **Mismatches**: 0\n")
        f.write(f"- **Missing in KB**: {stats['missing_in_kb']}\n")
        f.write(f"- **No SKU mapping**: {stats['no_mapping']}\n")
        f.write(f"- **No thickness extracted**: {stats['no_thickness']}\n\n")
        
        # Matches
        f.write("## ✅ Matches\n\n")
        if comparison["matches"]:
            f.write("Sample matches (first 10):\n\n")
            f.write("| SKU | Name | KB Key | Thickness | Sheet Price | KB Price | Delta |\n")
            f.write("|-----|------|--------|-----------|-------------|----------|-------|\n")
            
            for item in comparison["matches"][:10]:
                f.write(f"| {item['sku']} | {item['name'][:30]} | {item['kb_key']} | {item['thickness_mm']}mm | ${item['sheet_price']} | ${item['kb_price']} | ${item['delta']:+.2f} ({item['delta_pct']:.2f}%) |\n")
            
            if len(comparison["matches"]) > 10:
                f.write(f"\n*... and {len(comparison['matches']) - 10} more matches.*\n")
        else:
            f.write("No matches found.\n")
        f.write("\n")
        
        # Mismatches
        f.write("## ⚠️ Mismatches\n\n")
        if comparison["mismatches"]:
            f.write("| SKU | Name | KB Key | Thickness | Sheet Price | KB Price | Delta | Severity |\n")
            f.write("|-----|------|--------|-----------|-------------|----------|-------|----------|\n")
            
            for item in comparison["mismatches"]:
                f.write(f"| {item['sku']} | {item['name'][:30]} | {item['kb_key']} | {item['thickness_mm']}mm | ${item['sheet_price']} | ${item['kb_price']} | ${item['delta']:+.2f} ({item['delta_pct']:.2f}%) | {item['severity']} |\n")
        else:
            f.write("No mismatches found.\n")
        f.write("\n")
        
        # Missing in KB
        f.write("## 🔍 Missing in KB\n\n")
        if comparison["missing_in_kb"]:
            f.write("Items present in sheet but not found in KB:\n\n")
            f.write("| SKU | Name | KB Key | Thickness | Sheet Price |\n")
            f.write("|-----|------|--------|-----------|-------------|\n")
            
            for item in comparison["missing_in_kb"]:
                f.write(f"| {item['sku']} | {item['name'][:30]} | {item['kb_key']} | {item['thickness_mm']}mm | ${item['sheet_price']} |\n")
        else:
            f.write("All sheet items found in KB.\n")
        f.write("\n")
        
        # Reverse check
        if include_reverse_check and missing_in_sheet:
            f.write("## 📋 Missing in Sheet (Reverse Check)\n\n")
            f.write("Items present in KB but not found in sheet export:\n\n")
            f.write("| KB Key | Thickness | KB Price |\n")
            f.write("|--------|-----------|----------|\n")
            
            for item in missing_in_sheet:
                f.write(f"| {item['kb_key']} | {item['thickness_mm']}mm | ${item['kb_price']} |\n")
            f.write("\n")
        
        f.write("---\n\n")
        f.write(f"*See `compare_kb_gpt2.csv` for full comparison results.*\n")
    
    saved_files["md"] = md_path
    
    return saved_files


def run_comparison(price_base: Dict[str, Any], kb_path: Union[str, Path],
                   output_dir: Union[str, Path], tolerance_pct: float = 1.0,
                   include_reverse_check: bool = True) -> Dict[str, Any]:
    """
    Run KB comparison and save reports.
    
    Args:
        price_base: Parsed price base
        kb_path: Path to BMC_Base_Conocimiento_GPT-2.json
        output_dir: Output directory for reports
        tolerance_pct: Tolerance for price match (default 1%)
        include_reverse_check: Whether to check for KB items missing from sheet
        
    Returns:
        Comparison results dict
    """
    from datetime import datetime
    
    print(f"🔍 Comparing with KB: {Path(kb_path).name}")
    comparison = compare_with_kb(price_base, kb_path, tolerance_pct)
    
    # Add timestamp
    comparison["meta"]["compared_at"] = datetime.now().isoformat()
    
    # Reverse check
    missing_in_sheet = []
    if include_reverse_check:
        print("🔄 Running reverse check (KB → sheet)...")
        kb = load_kb_gpt2(kb_path)
        missing_in_sheet = check_missing_in_sheet(kb, price_base)
        print(f"   - Found {len(missing_in_sheet)} KB items not in sheet")
    
    # Print summary
    stats = comparison["stats"]
    print(f"\n✅ Comparison complete:")
    print(f"   - Total comparisons: {stats['total_comparisons']}")
    print(f"   - Matches: {stats['matches']} ({stats['matches'] / stats['total_comparisons'] * 100:.1f}%)" if stats['total_comparisons'] > 0 else "   - Matches: 0")
    print(f"   - Mismatches: {stats['mismatches']}")
    print(f"   - Missing in KB: {stats['missing_in_kb']}")
    
    # Save reports
    print("\n💾 Saving comparison reports...")
    saved_files = save_comparison_reports(comparison, output_dir, include_reverse_check, missing_in_sheet)
    
    for key, path in saved_files.items():
        print(f"   - {key}: {path}")
    
    return comparison
