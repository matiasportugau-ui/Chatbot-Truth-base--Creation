#!/usr/bin/env python3
"""
Apply correction to SKU 6842: Change unit_base from 'metro_lineal' to 'unidad'

Usage:
    python3 pricing/tools/apply_sku_6842_correction.py
    
This script:
1. Reads bromyros_pricing_master.json
2. Finds SKU 6842
3. Changes unit_base to 'unidad'
4. Saves backup and updated file
5. Validates the change
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

# Paths
MASTER_FILE = Path("gpt_consolidation_agent/deployment/knowledge_base/bromyros_pricing_master.json")
BACKUP_DIR = Path("pricing/backups")

def main():
    print("=" * 60)
    print("SKU 6842 Correction Tool")
    print("=" * 60)
    
    # Ensure backup directory exists
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load master file
    print(f"\n📂 Loading: {MASTER_FILE}")
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find SKU 6842
    print("\n🔍 Searching for SKU 6842...")
    found = False
    original_unit_base = None
    
    for product in data.get('products', []):
        if product.get('sku') == '6842':
            found = True
            original_unit_base = product.get('unit_base')
            
            print(f"\n✅ Found SKU 6842:")
            print(f"   Name: {product.get('name')}")
            print(f"   Current unit_base: {original_unit_base}")
            print(f"   Length_m: {product.get('length_m')}")
            print(f"   Price s/IVA: ${product.get('sale_price_usd_ex_iva')}")
            
            # Apply correction
            if original_unit_base != 'unidad':
                print(f"\n🔧 Applying correction...")
                product['unit_base'] = 'unidad'
                print(f"   ✅ Changed unit_base: '{original_unit_base}' → 'unidad'")
            else:
                print(f"\n⚠️  No change needed - unit_base already 'unidad'")
                return
            
            break
    
    if not found:
        print("\n❌ ERROR: SKU 6842 not found in master file!")
        return
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"bromyros_pricing_master_backup_{timestamp}.json"
    
    print(f"\n💾 Creating backup: {backup_file}")
    shutil.copy2(MASTER_FILE, backup_file)
    
    # Save updated file
    print(f"\n💾 Saving corrected file: {MASTER_FILE}")
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Validate
    print("\n✅ Validation:")
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        validated_data = json.load(f)
    
    for product in validated_data.get('products', []):
        if product.get('sku') == '6842':
            validated_unit_base = product.get('unit_base')
            if validated_unit_base == 'unidad':
                print(f"   ✅ Correction verified: unit_base = '{validated_unit_base}'")
            else:
                print(f"   ❌ ERROR: unit_base = '{validated_unit_base}' (expected 'unidad')")
                return
            break
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ SUCCESS - Correction Applied")
    print("=" * 60)
    print(f"\nSKU: 6842")
    print(f"Product: Perf. Ch. Gotero Lateral 100mm")
    print(f"Change: unit_base '{original_unit_base}' → 'unidad'")
    print(f"\nBackup: {backup_file}")
    print(f"Updated: {MASTER_FILE}")
    print("\n📋 Next steps:")
    print("   1. Test quotation with SKU 6842")
    print("   2. Verify calculation: cantidad × price (no length multiplication)")
    print("   3. Regenerate GPT knowledge base if needed")
    print("   4. Update source CSV/database to prevent regression")

if __name__ == "__main__":
    main()
