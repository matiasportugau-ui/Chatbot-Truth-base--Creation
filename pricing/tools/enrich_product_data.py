#!/usr/bin/env python3
"""
Product Data Enrichment Tool
Ingests logical rules and manual CSV data to complete missing product information.
Updated to handle min/max lengths and production types.
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List

# Paths
MASTER_JSON = "pricing/out/bromyros_pricing_reference.json"
RULES_JSON = "pricing/config/product_enrichment_rules.json"
MANUAL_CSV_1 = "pricing/config/manual_product_data.csv"
MANUAL_CSV_2 = "pricing/out/products_missing_data.csv"

def load_rules():
    path = Path(RULES_JSON)
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return {"rules": [], "families": {}}

def load_csv_data(path_str):
    data = {}
    path = Path(path_str)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row.get("sku")
                if sku:
                    cleaned_row = {k: v for k, v in row.items() if v and v.strip() != ""}
                    for field in ["length_m", "thickness_mm"]:
                        if field in cleaned_row:
                            try:
                                cleaned_row[field] = float(cleaned_row[field])
                            except ValueError:
                                pass 
                    data[sku] = cleaned_row
    return data

def apply_rules(product: Dict[str, Any], rules_config: Dict[str, Any]) -> List[str]:
    applied = []
    
    # 1. Family defaults
    family = product.get("family")
    if family and family in rules_config.get("families", {}):
        fam_defaults = rules_config["families"][family]
        for k, v in fam_defaults.items():
            if not product.get(k): 
                product[k] = v
                applied.append(f"Family default: {k}={v}")

    # 2. Logic Rules
    for rule in rules_config.get("rules", []):
        condition = rule.get("condition", {})
        match = True
        
        if "sku_contains" in condition:
            sku = product.get("sku", "").upper()
            if not any(sub in sku for sub in condition["sku_contains"]):
                match = False
                
        if match and "name_excludes" in condition:
             name = product.get("name", "").lower()
             if any(ex in name for ex in condition["name_excludes"]):
                 match = False

        if match and "type" in condition:
            if product.get("type") != condition["type"]:
                match = False
                
        if match and condition.get("length_m_is_missing"):
            if product.get("length_m"): 
                match = False

        if match:
            # Handle both single value (legacy) and multi-value dicts
            values = rule.get("values")
            if not values and "value" in rule:
                # Compatibility with old single-field rules
                target_field = rule["target_fields"][0]
                values = {target_field: rule["value"]}
            
            if values:
                for field, val in values.items():
                    # Only fill if missing OR if we are enriching new schema fields (min/max/production_type)
                    if not product.get(field):
                        product[field] = val
                        applied.append(f"Rule '{rule['name']}': {field}={val}")
                    
    return applied

def enrich():
    with open(MASTER_JSON, 'r', encoding='utf-8') as f:
        master = json.load(f)
    
    products = {p["id"]: p for p in master["products"]}
    rules = load_rules()
    
    manual_data = load_csv_data(MANUAL_CSV_2) 
    manual_data.update(load_csv_data(MANUAL_CSV_1))
    
    updates_count = 0
    
    for pid, p in products.items():
        original = p.copy()
        changes = []
        
        # A. Apply Rules
        rule_changes = apply_rules(p, rules)
        changes.extend(rule_changes)
        
        # B. Apply Manual Data
        sku = p.get("sku") 
        if sku in manual_data:
            override = manual_data[sku]
            for k, v in override.items():
                if k in ["sku", "name", "current_status"]: continue
                if str(p.get(k)) != str(v):
                    p[k] = v
                    changes.append(f"Manual Override: {k}={v}")

        if changes:
            updates_count += 1
            # print(f"Updated {pid}: {', '.join(changes)}")

    master["products"] = list(products.values())
    with open(MASTER_JSON, 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=2, ensure_ascii=False)
        
    print(f"Enrichment Complete. Updated {updates_count} products.")
    
    # Check
    on_demand = len([p for p in master["products"] if p.get("production_type") == "on_demand"])
    print(f"Products set to 'On Demand': {on_demand}")

if __name__ == "__main__":
    enrich()
