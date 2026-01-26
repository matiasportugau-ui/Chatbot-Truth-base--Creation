#!/usr/bin/env python3
"""
Price Base Validation Module

Validates parsed price base for:
- Data quality issues (missing prices, negative values)
- IVA consistency checks
- Duplicate SKUs
- Length extraction hit rate for profiles
- Price sanity checks

Outputs validation reports in CSV and Markdown formats.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Union
from collections import Counter


def validate_price_base(price_base: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run comprehensive validation on parsed price base.
    
    Args:
        price_base: Parsed price base dict from parser
        
    Returns:
        Dict with validation results and issues
    """
    products = price_base["products"]
    
    validation = {
        "summary": {},
        "issues": [],
        "stats": {}
    }
    
    # Track statistics
    stats = {
        "total_products": len(products),
        "unique_skus": len(set(p["sku"] for p in products)),
        "duplicates": 0,
        "missing_cost": 0,
        "missing_sale_price": 0,
        "missing_web_price": 0,
        "negative_prices": 0,
        "iva_inconsistencies_sale": 0,
        "iva_inconsistencies_web": 0,
        "profiles_total": 0,
        "profiles_with_length": 0,
        "panels_total": 0,
        "consumables_total": 0,
    }
    
    issues = []
    
    # Check for duplicate SKUs
    sku_counts = Counter(p["sku"] for p in products)
    duplicates = {sku: count for sku, count in sku_counts.items() if count > 1}
    stats["duplicates"] = len(duplicates)
    
    for sku, count in duplicates.items():
        issues.append({
            "severity": "high",
            "type": "duplicate_sku",
            "sku": sku,
            "message": f"SKU appears {count} times",
            "products": [p["name"] for p in products if p["sku"] == sku]
        })
    
    # Validate each product
    for p in products:
        sku = p["sku"]
        name = p["name"]
        category = p.get("category", {})
        tipo = category.get("tipo")
        
        # Count by category
        if tipo == "panel":
            stats["panels_total"] += 1
        elif tipo == "perfil":
            stats["profiles_total"] += 1
            if p.get("length_m"):
                stats["profiles_with_length"] += 1
        elif tipo == "accesorio":
            stats["consumables_total"] += 1
        
        # Check for missing cost
        if p.get("cost_sin_iva") is None:
            stats["missing_cost"] += 1
            issues.append({
                "severity": "medium",
                "type": "missing_cost",
                "sku": sku,
                "name": name,
                "message": "Missing cost (col F)"
            })
        
        # Check for negative prices
        for field in ["cost_sin_iva", "sale_sin_iva", "sale_iva_inc", "web_sin_iva", "web_iva_inc"]:
            value = p.get(field)
            if value is not None and value < 0:
                stats["negative_prices"] += 1
                issues.append({
                    "severity": "high",
                    "type": "negative_price",
                    "sku": sku,
                    "name": name,
                    "field": field,
                    "value": value,
                    "message": f"Negative price in {field}: {value}"
                })
        
        # Check for missing sale price
        if p.get("sale_sin_iva") is None and p.get("sale_iva_inc") is None:
            stats["missing_sale_price"] += 1
            issues.append({
                "severity": "medium",
                "type": "missing_sale_price",
                "sku": sku,
                "name": name,
                "message": "Missing both sale_sin_iva (L) and sale_iva_inc (M)"
            })
        
        # Check for missing web price (info only, not critical)
        if p.get("web_sin_iva") is None and p.get("web_iva_inc") is None:
            stats["missing_web_price"] += 1
        
        # IVA consistency checks
        iva_checks = p.get("iva_checks", {})
        
        if iva_checks.get("sale_iva_consistent") is False:
            stats["iva_inconsistencies_sale"] += 1
            delta = iva_checks.get("sale_iva_delta_pct", 0)
            issues.append({
                "severity": "high",
                "type": "iva_inconsistency",
                "sku": sku,
                "name": name,
                "field": "sale_price",
                "delta_pct": delta,
                "sale_sin_iva": p.get("sale_sin_iva"),
                "sale_iva_inc": p.get("sale_iva_inc"),
                "message": f"IVA inconsistency in sale price: {delta:.2f}% delta"
            })
        
        if iva_checks.get("web_iva_consistent") is False:
            stats["iva_inconsistencies_web"] += 1
            delta = iva_checks.get("web_iva_delta_pct", 0)
            issues.append({
                "severity": "high",
                "type": "iva_inconsistency",
                "sku": sku,
                "name": name,
                "field": "web_price",
                "delta_pct": delta,
                "web_sin_iva": p.get("web_sin_iva"),
                "web_iva_inc": p.get("web_iva_inc"),
                "message": f"IVA inconsistency in web price: {delta:.2f}% delta"
            })
        
        # Check profiles without length extraction
        if tipo == "perfil" and category.get("needs_length") and not p.get("length_m"):
            issues.append({
                "severity": "low",
                "type": "missing_length",
                "sku": sku,
                "name": name,
                "message": "Profile without length extraction (col E) - cannot compute per_ml prices"
            })
    
    # Summary
    validation["stats"] = stats
    validation["issues"] = issues
    
    # Compute percentages
    validation["summary"] = {
        "total_products": stats["total_products"],
        "unique_skus": stats["unique_skus"],
        "duplicate_skus": stats["duplicates"],
        "data_quality": {
            "missing_cost": stats["missing_cost"],
            "missing_sale_price": stats["missing_sale_price"],
            "missing_web_price": stats["missing_web_price"],
            "negative_prices": stats["negative_prices"],
        },
        "iva_consistency": {
            "sale_inconsistencies": stats["iva_inconsistencies_sale"],
            "web_inconsistencies": stats["iva_inconsistencies_web"],
            "sale_pass_rate_pct": round((1 - stats["iva_inconsistencies_sale"] / stats["total_products"]) * 100, 2) if stats["total_products"] > 0 else 100,
            "web_pass_rate_pct": round((1 - stats["iva_inconsistencies_web"] / stats["total_products"]) * 100, 2) if stats["total_products"] > 0 else 100,
        },
        "length_extraction": {
            "profiles_total": stats["profiles_total"],
            "profiles_with_length": stats["profiles_with_length"],
            "hit_rate_pct": round((stats["profiles_with_length"] / stats["profiles_total"]) * 100, 2) if stats["profiles_total"] > 0 else 0,
        },
        "category_breakdown": {
            "panels": stats["panels_total"],
            "profiles": stats["profiles_total"],
            "consumables": stats["consumables_total"],
        }
    }
    
    return validation


def save_validation_reports(validation: Dict[str, Any], output_dir: Union[str, Path]) -> Dict[str, Path]:
    """
    Save validation reports to CSV and Markdown.
    
    Args:
        validation: Validation results dict
        output_dir: Output directory
        
    Returns:
        Dict with paths to saved files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    # Save issues CSV
    csv_path = output_dir / "validation_issues.csv"
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        if validation["issues"]:
            # Collect all unique field names from all issues
            all_fieldnames = set()
            for issue in validation["issues"]:
                all_fieldnames.update(issue.keys())
            
            # Sort for consistent column order
            fieldnames = sorted(all_fieldnames)
            
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for issue in validation["issues"]:
                # Flatten any list fields for CSV
                row = issue.copy()
                for key, value in row.items():
                    if isinstance(value, list):
                        row[key] = "; ".join(str(v) for v in value)
                writer.writerow(row)
    
    saved_files["issues_csv"] = csv_path
    
    # Save summary Markdown
    md_path = output_dir / "validation_summary.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Bromyros Price Base - Validation Summary\n\n")
        
        summary = validation["summary"]
        
        f.write("## Overview\n\n")
        f.write(f"- **Total products**: {summary['total_products']}\n")
        f.write(f"- **Unique SKUs**: {summary['unique_skus']}\n")
        f.write(f"- **Duplicate SKUs**: {summary['duplicate_skus']}\n\n")
        
        f.write("## Data Quality\n\n")
        dq = summary["data_quality"]
        f.write(f"- Missing cost (col F): {dq['missing_cost']}\n")
        f.write(f"- Missing sale price (cols L/M): {dq['missing_sale_price']}\n")
        f.write(f"- Missing web price (cols T/U): {dq['missing_web_price']}\n")
        f.write(f"- Negative prices: {dq['negative_prices']}\n\n")
        
        f.write("## IVA Consistency\n\n")
        iva = summary["iva_consistency"]
        f.write(f"- Sale price IVA inconsistencies: {iva['sale_inconsistencies']} ({iva['sale_pass_rate_pct']:.2f}% pass rate)\n")
        f.write(f"- Web price IVA inconsistencies: {iva['web_inconsistencies']} ({iva['web_pass_rate_pct']:.2f}% pass rate)\n\n")
        
        f.write("## Length Extraction (Profiles)\n\n")
        length = summary["length_extraction"]
        f.write(f"- Total profiles: {length['profiles_total']}\n")
        f.write(f"- Profiles with length extracted: {length['profiles_with_length']}\n")
        f.write(f"- Hit rate: {length['hit_rate_pct']:.2f}%\n\n")
        
        f.write("## Category Breakdown\n\n")
        cat = summary["category_breakdown"]
        f.write(f"- Panels: {cat['panels']}\n")
        f.write(f"- Profiles: {cat['profiles']}\n")
        f.write(f"- Consumables: {cat['consumables']}\n\n")
        
        f.write("## Issues by Severity\n\n")
        issues_by_severity = {"high": [], "medium": [], "low": []}
        for issue in validation["issues"]:
            severity = issue.get("severity", "low")
            issues_by_severity[severity].append(issue)
        
        for severity in ["high", "medium", "low"]:
            count = len(issues_by_severity[severity])
            f.write(f"### {severity.upper()} ({count})\n\n")
            
            if count == 0:
                f.write("No issues.\n\n")
            else:
                for issue in issues_by_severity[severity][:20]:  # Limit to 20 per severity
                    f.write(f"- **{issue.get('sku')}**: {issue.get('message')}\n")
                
                if count > 20:
                    f.write(f"\n*... and {count - 20} more. See `validation_issues.csv` for full list.*\n")
                f.write("\n")
        
        f.write("---\n\n")
        f.write(f"*Generated: {validation.get('meta', {}).get('validated_at', 'N/A')}*\n")
    
    saved_files["summary_md"] = md_path
    
    return saved_files


def run_validation(price_base: Dict[str, Any], output_dir: Union[str, Path]) -> Dict[str, Any]:
    """
    Run validation and save reports.
    
    Args:
        price_base: Parsed price base
        output_dir: Output directory for reports
        
    Returns:
        Validation results dict
    """
    from datetime import datetime
    
    print("🔍 Running validation checks...")
    validation = validate_price_base(price_base)
    
    # Add metadata
    validation["meta"] = {
        "validated_at": datetime.now().isoformat(),
        "source_file": price_base.get("meta", {}).get("source_file", "unknown")
    }
    
    # Print summary
    summary = validation["summary"]
    print(f"\n✅ Validation complete:")
    print(f"   - Total products: {summary['total_products']}")
    print(f"   - Unique SKUs: {summary['unique_skus']}")
    print(f"   - Duplicate SKUs: {summary['duplicate_skus']}")
    print(f"   - IVA pass rate (sale): {summary['iva_consistency']['sale_pass_rate_pct']:.2f}%")
    print(f"   - IVA pass rate (web): {summary['iva_consistency']['web_pass_rate_pct']:.2f}%")
    print(f"   - Length extraction hit rate: {summary['length_extraction']['hit_rate_pct']:.2f}%")
    print(f"   - Total issues: {len(validation['issues'])}")
    
    # Save reports
    print("\n💾 Saving validation reports...")
    saved_files = save_validation_reports(validation, output_dir)
    
    for key, path in saved_files.items():
        print(f"   - {key}: {path}")
    
    return validation
