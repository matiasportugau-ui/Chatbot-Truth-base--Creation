import json
import os
import datetime
from decimal import Decimal

# Placeholder for Shopify API client
# import shopify 

def load_knowledge_base():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'panelin_truth_bmcuruguay.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_knowledge_base(data):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'panelin_truth_bmcuruguay.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def handle_product_update(webhook_data):
    """
    Procesa webhook de update de Shopify.
    Expected data structure matches Shopify Product Update Webhook.
    """
    kb = load_knowledge_base()
    
    # Extract data from webhook
    shopify_id = str(webhook_data.get('id', ''))
    title = webhook_data.get('title', '')
    variants = webhook_data.get('variants', [])
    
    # Find matching product in KB (by ID or Title)
    # This logic needs to be robust. For now, we assume title match or ID match.
    matched_key = None
    for key, product in kb['products'].items():
        if product.get('shopify_id') == shopify_id or product.get('name') == title:
            matched_key = key
            break
            
    if matched_key:
        print(f"Updating product {matched_key} from webhook")
        product = kb['products'][matched_key]
        product['shopify_id'] = shopify_id # Ensure ID is set
        product['last_updated'] = datetime.datetime.now(datetime.UTC).isoformat()
        product['_sync_source'] = 'shopify_webhook'
        
        # Update inventory if available
        # Sum inventory across variants?
        total_inventory = sum(v.get('inventory_quantity', 0) for v in variants)
        product['inventory_quantity'] = total_inventory
        
        # Update price? 
        # Price logic is complex because KB has price_per_m2 but Shopify might have unit price per panel.
        # This requires careful mapping.
        # For now, we log the price change but might not auto-update without safety checks.
        if variants:
            price = float(variants[0].get('price', 0))
            print(f"Shopify price: {price}. KB Price: {product['price_per_m2']}. Verification needed.")
            
        save_knowledge_base(kb)
    else:
        print(f"Product {title} not found in KB. Ignoring or creating new entry.")

if __name__ == "__main__":
    # Mock webhook data
    mock_data = {
        "id": 123456789,
        "title": "ISOPANEL EPS (Paredes y Fachadas) / 50 - 100 - 150 - 200 - 250 mm.",
        "variants": [
            {"id": 1, "price": "41.88", "inventory_quantity": 100}
        ]
    }
    handle_product_update(mock_data)
