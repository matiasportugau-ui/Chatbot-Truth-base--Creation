#!/usr/bin/env python3
"""
Product Data Validator
Reports on data completeness and consistency after enrichment.
"""

import json
from pathlib import Path

MASTER_JSON = "pricing/out/bromyros_pricing_reference.json"

def validate():
    with open(MASTER_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get("products", [])
    total = len(products)
    
    missing_fields = {
        "length_m": [],
        "thickness_mm": [],
        "type": [],
        "family": [],
        "unit_base": []
    }
    
    for p in products:
        pid = p.get("id")
        name = p.get("name")
        
        for field in missing_fields:
            val = p.get(field)
            if val is None or val == "" or (isinstance(val, (int, float)) and val == 0):
                missing_fields[field].append(f"{pid} ({name})")
                
    print(f"=== Validation Report (Total Products: {total}) ===")
    
    for field, items in missing_fields.items():
        completeness = ((total - len(items)) / total) * 100
        print(f"\nField '{field}': {completeness:.1f}% Complete ({len(items)} missing)")
        if items:
            print(f"Sample missing: {items[:3]}...")

if __name__ == "__main__":
    validate()
