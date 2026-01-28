import json
import datetime
from decimal import Decimal

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def consolidate_kb():
    pricing_source_path = '/workspace/pricing/out/bromyros_pricing_gpt_optimized.json'
    web_source_path = '/workspace/gpt_consolidation_agent/deployment/knowledge_base/panelin_truth_bmcuruguay_web_only_v2.json'
    output_path = '/workspace/panelin_truth_bmcuruguay.json'

    pricing_data = load_json(pricing_source_path)
    web_data = load_json(web_source_path)
    
    products = {}
    
    # Process products from pricing source
    for product in pricing_data.get('products', []):
        sku = product.get('sku')
        if not sku:
            continue
            
        # Create a clean key for the product
        product_key = sku
        
        # Base product structure
        clean_product = {
            "name": product.get('name'),
            "sku": sku,
            "category": product.get('familia'),
            "subcategory": product.get('sub_familia'),
            "type": product.get('tipo'),
            "price_per_m2": product.get('pricing', {}).get('sale_iva_inc'), # Using IVA included price for now as default reference
            "price_details": {
                "cost_sin_iva": product.get('pricing', {}).get('cost_sin_iva'),
                "sale_sin_iva": product.get('pricing', {}).get('sale_sin_iva'),
                "sale_iva_inc": product.get('pricing', {}).get('sale_iva_inc'),
            },
            "currency": pricing_data.get('metadata', {}).get('currency', 'USD'),
            "specifications": product.get('specifications', {}),
            "calculation_rules": {
                "minimum_order_m2": 10, # Default
                "bulk_discount_threshold_m2": 100, # Default
                "bulk_discount_percent": 5 # Default
            },
            "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        
        products[product_key] = clean_product

    # Enrich with web data if possible (mapping might be tricky without shared ID, checking SKUs or names)
    # The web data uses keys like "isopanel_eps_paredes_fachadas".
    # I will try to match loosely or just leave it for now as the pricing data seems more complete for calculation.
    
    # Construct final JSON
    final_kb = {
        "version": "2.0.0",
        "last_sync": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "shopify_store": "bmcuruguay.myshopify.com",
        "products": products,
        "pricing_rules": {
            "tax_rate_uy": pricing_data.get('metadata', {}).get('iva_rate', 0.22) * 100,
            "delivery_cost_per_m2": 1.50, # Default from prompt
            "minimum_delivery_charge": 50 # Default from prompt
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_kb, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully created {output_path} with {len(products)} products.")

if __name__ == "__main__":
    consolidate_kb()
