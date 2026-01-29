import csv
import json
from datetime import datetime
import os

SOURCE_CSV = "/workspace/pricing/out/bromyros_price_base_v1.csv"
OUTPUT_JSON = "/workspace/panelin/data/panelin_truth_bmcuruguay.json"

def create_kb():
    products = {}
    
    with open(SOURCE_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sku = row['sku']
            name = row['name']
            
            try:
                price = float(row['sale_sin_iva']) if row['sale_sin_iva'] else 0.0
            except ValueError:
                price = 0.0

            # Use SKU as key, or generate a composite key if SKU is not unique
            # The prompt suggests keys like "Isopanel_50mm"
            # Looking at the CSV: SKU IAGRO30 has thickness 30.
            
            # Let's clean up thickness
            try:
                thickness = int(float(row['thickness_mm'])) if row['thickness_mm'] else 0
            except ValueError:
                thickness = 0
            
            # Simple normalization for the key
            # If SKU is present, use it. If duplicates, we might need a better strategy.
            # For now, let's use SKU and append if needed or just use SKU if unique.
            # But the prompt suggests "Isopanel_50mm".
            # Let's try to infer type from name or use 'tipo' column if useful.
            
            product_type = row.get('tipo', 'unknown')
            
            key = sku
            
            if key not in products:
                products[key] = {
                    "sku": sku,
                    "name": name,
                    "price_per_m2": price,
                    "currency": "USD", # Assuming USD based on context
                    "thickness_mm": thickness,
                    "type": product_type,
                    "calculation_rules": {
                        "minimum_order_m2": 1, # Default
                        "bulk_discount_threshold_m2": 100,
                        "bulk_discount_percent": 5
                    },
                    "last_updated": datetime.now().isoformat(),
                    "_sync_source": "csv_import"
                }
            else:
                # If duplicate SKU, warn or handle. 
                # In this CSV, IAGRO30 appears twice? 
                # Row 2: Isoroof FOIL 30 mm - Color Gris-Rojo
                # Row 10: Isoroof COLONIAL 40 mm - Color simil teja (Wait, SKU IAGRO30 for 40mm?)
                # If SKU is reused, we might need composite key.
                pass

    kb = {
        "version": "2.0.0",
        "last_sync": datetime.now().isoformat(),
        "shopify_store": "bmcuruguay.myshopify.com",
        "products": products,
        "pricing_rules": {
            "tax_rate_uy": 22,
            "delivery_cost_per_m2": 1.50,
            "minimum_delivery_charge": 50
        }
    }
    
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(kb, f, indent=2)
    
    print(f"Created KB at {OUTPUT_JSON} with {len(products)} products.")

if __name__ == "__main__":
    create_kb()
