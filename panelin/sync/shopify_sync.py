import json
import os
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

# Mock Shopify Client for architecture demonstration
class ShopifyClient:
    async def get_all_products(self):
        return {}

# Configuration
KB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'panelin_truth_bmcuruguay.json')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_knowledge_base():
    if not os.path.exists(KB_PATH):
        return {"products": {}}
    with open(KB_PATH, 'r') as f:
        return json.load(f)

def save_knowledge_base(kb_data):
    with open(KB_PATH, 'w') as f:
        json.dump(kb_data, f, indent=2)

def transform_shopify_to_kb(shopify_product: Dict[str, Any]) -> Dict[str, Any]:
    """Transform Shopify product schema to Panelin KB schema"""
    # This is a placeholder for the actual transformation logic
    # In a real implementation, we would map fields from shopify_product
    return {
        "name": shopify_product.get("title"),
        "price_per_m2": float(shopify_product.get("variants", [{}])[0].get("price", 0)),
        "shopify_id": shopify_product.get("id"),
        "last_updated": datetime.now().isoformat(),
        "_sync_source": "shopify_webhook"
    }

async def handle_product_update(webhook_payload: Dict[str, Any]):
    """
    Handle Shopify product update webhook
    1. Validate HMAC (assumed done by middleware)
    2. Transform data
    3. Update KB
    """
    try:
        sku = webhook_payload.get("variants", [{}])[0].get("sku")
        if not sku:
            logger.warning("Product update without SKU")
            return
            
        kb_data = load_knowledge_base()
        
        # Update or add product
        transformed_product = transform_shopify_to_kb(webhook_payload)
        
        # Merge with existing data to preserve manual fields like calculation_rules if needed
        if sku in kb_data["products"]:
             # Update only fields that come from Shopify
             kb_data["products"][sku].update(transformed_product)
        else:
            kb_data["products"][sku] = transformed_product
            
        kb_data["last_sync"] = datetime.now().isoformat()
        
        save_knowledge_base(kb_data)
        logger.info(f"Updated product {sku} in KB")
        
        # Here we would trigger a Git commit or Qdrant re-indexing
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")

async def daily_shopify_reconciliation():
    """Verifica integridad KB vs Shopify API"""
    shopify_client = ShopifyClient()
    shopify_products = await shopify_client.get_all_products()
    kb_products = load_knowledge_base().get("products", {})
    
    discrepancies = []
    for sku, shopify_data in shopify_products.items():
        if sku not in kb_products:
            discrepancies.append(f"MISSING: {sku} not in KB")
        elif abs(kb_products[sku]['price_per_m2'] - float(shopify_data.get('price', 0))) > 0.01:
            discrepancies.append(f"PRICE_MISMATCH: {sku}")
    
    if discrepancies:
        logger.warning(f"Found discrepancies: {discrepancies}")
        # alert_operations_team(discrepancies)
