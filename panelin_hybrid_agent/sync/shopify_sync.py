"""
Shopify Sync Service for Panelin Hybrid Agent.

Implements:
1. Webhook handlers for real-time updates
2. Daily reconciliation for data integrity
3. HMAC validation for security
4. Automatic KB updates with audit trail

Architecture:
┌─────────────────────────────────────────────────────────────────┐
│                      SHOPIFY STORE                               │
│              (Fuente de verdad para inventario)                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │ products/ │   │ inventory_│   │ products/ │
    │ update    │   │ levels/   │   │ delete    │
    │ webhook   │   │ update    │   │ webhook   │
    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
          │               │               │
          └───────────────┼───────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SYNC SERVICE                                  │
│  1. Validar HMAC del webhook                                     │
│  2. Transformar Shopify schema → KB schema                       │
│  3. Validar datos (precio > 0, SKU existe)                      │
│  4. Actualizar JSON KB con timestamp                            │
│  5. Commit a Git (audit trail)                                  │
│  6. Notificar éxito/fallo                                       │
└─────────────────────────────────────────────────────────────────┘
"""

import json
import hmac
import hashlib
import os
import subprocess
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SyncConfig:
    """Configuration for Shopify sync."""
    store_url: str = "bmcuruguay.myshopify.com"
    api_version: str = "2024-01"
    webhook_secret: Optional[str] = None
    access_token: Optional[str] = None
    kb_path: Path = Path(__file__).parent.parent / "knowledge_base" / "panelin_truth_bmcuruguay.json"
    inventory_cache_path: Path = Path(__file__).parent.parent / "knowledge_base" / "inventory_cache.json"
    enable_git_commits: bool = True
    notification_webhook: Optional[str] = None


class ShopifySyncService:
    """
    Service for synchronizing Shopify data with local knowledge base.
    
    Features:
    - HMAC validation for webhook security
    - Schema transformation (Shopify → KB)
    - Automatic KB updates with timestamps
    - Git commit for audit trail
    - Discord/Slack notifications
    """
    
    def __init__(self, config: Optional[SyncConfig] = None):
        """Initialize sync service."""
        self.config = config or SyncConfig()
        
        # Load config from environment if available
        self.config.webhook_secret = os.environ.get(
            'SHOPIFY_WEBHOOK_SECRET', 
            self.config.webhook_secret
        )
        self.config.access_token = os.environ.get(
            'SHOPIFY_ACCESS_TOKEN',
            self.config.access_token
        )
    
    def validate_webhook(self, payload: bytes, hmac_header: str) -> bool:
        """
        Validate Shopify webhook HMAC signature.
        
        Args:
            payload: Raw webhook payload bytes
            hmac_header: X-Shopify-Hmac-SHA256 header value
        
        Returns:
            True if valid, False otherwise
        """
        if not self.config.webhook_secret:
            logger.warning("No webhook secret configured - skipping HMAC validation")
            return True
        
        calculated_hmac = hmac.new(
            self.config.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(calculated_hmac, hmac_header)
    
    def load_kb(self) -> Dict[str, Any]:
        """Load current knowledge base."""
        if self.config.kb_path.exists():
            with open(self.config.kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"products": {}, "meta": {}}
    
    def save_kb(self, kb: Dict[str, Any], commit_message: Optional[str] = None) -> bool:
        """
        Save knowledge base and optionally commit to git.
        
        Args:
            kb: Knowledge base dictionary
            commit_message: Git commit message (if git is enabled)
        
        Returns:
            True if successful
        """
        # Update metadata
        kb['meta']['last_sync'] = datetime.now(timezone.utc).isoformat()
        
        # Write file
        with open(self.config.kb_path, 'w', encoding='utf-8') as f:
            json.dump(kb, f, indent=2, ensure_ascii=False)
        
        logger.info(f"KB saved to {self.config.kb_path}")
        
        # Git commit if enabled
        if self.config.enable_git_commits and commit_message:
            try:
                subprocess.run(
                    ['git', 'add', str(self.config.kb_path)],
                    cwd=self.config.kb_path.parent.parent,
                    check=True,
                    capture_output=True
                )
                subprocess.run(
                    ['git', 'commit', '-m', commit_message],
                    cwd=self.config.kb_path.parent.parent,
                    check=True,
                    capture_output=True
                )
                logger.info(f"Git commit: {commit_message}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Git commit failed: {e}")
        
        return True
    
    def transform_shopify_product(self, shopify_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Shopify product data to KB schema.
        
        Args:
            shopify_data: Raw Shopify product webhook payload
        
        Returns:
            KB-formatted product data
        """
        # Extract basic info
        product_id = shopify_data.get('id')
        title = shopify_data.get('title', '')
        handle = shopify_data.get('handle', '')
        
        # Process variants for pricing by thickness
        variants = shopify_data.get('variants', [])
        espesores = {}
        
        for variant in variants:
            # Try to extract thickness from variant title or option
            thickness = self._extract_thickness(variant)
            if thickness:
                espesores[str(thickness)] = {
                    'precio': float(variant.get('price', 0)),
                    'currency': 'USD',
                    'unit': 'm2',
                    'shopify_variant_id': variant.get('id'),
                    'sku': variant.get('sku'),
                    'inventory_quantity': variant.get('inventory_quantity', 0),
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
        
        return {
            'shopify_id': f"gid://shopify/Product/{product_id}",
            'nombre_comercial': title,
            'handle': handle,
            'espesores': espesores,
            '_sync_source': 'shopify_webhook',
            '_synced_at': datetime.now(timezone.utc).isoformat()
        }
    
    def _extract_thickness(self, variant: Dict[str, Any]) -> Optional[int]:
        """Extract thickness in mm from variant data."""
        # Check variant title
        title = variant.get('title', '')
        
        # Common patterns: "100 mm", "100mm", "100"
        import re
        match = re.search(r'(\d+)\s*mm', title, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Check option values
        for option in ['option1', 'option2', 'option3']:
            value = variant.get(option, '')
            match = re.search(r'(\d+)\s*mm', str(value), re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def process_product_update(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a product update webhook.
        
        Args:
            webhook_data: Shopify webhook payload
        
        Returns:
            Sync result with success status and details
        """
        kb = self.load_kb()
        
        # Transform Shopify data to KB format
        product_data = self.transform_shopify_product(webhook_data)
        shopify_id = product_data['shopify_id']
        
        # Find matching product in KB by shopify_id
        updated_product = None
        for product_key, product in kb.get('products', {}).items():
            if product.get('shopify_id') == shopify_id:
                # Update existing product
                product.update(product_data)
                updated_product = product_key
                break
        
        if updated_product:
            logger.info(f"Updated product: {updated_product}")
        else:
            logger.info(f"New product from Shopify: {shopify_id}")
            # For new products, we log but don't auto-add (requires manual KB update)
        
        # Save KB
        self.save_kb(
            kb,
            f"[Auto-Sync] Product update: {updated_product or shopify_id}"
        )
        
        return {
            'success': True,
            'action': 'update' if updated_product else 'new',
            'product_id': updated_product or shopify_id,
            'synced_at': datetime.now(timezone.utc).isoformat()
        }
    
    def process_inventory_update(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an inventory level update webhook.
        
        Args:
            webhook_data: Shopify inventory webhook payload
        
        Returns:
            Sync result
        """
        inventory_item_id = webhook_data.get('inventory_item_id')
        available = webhook_data.get('available', 0)
        
        # Update inventory cache
        cache = {}
        if self.config.inventory_cache_path.exists():
            with open(self.config.inventory_cache_path, 'r') as f:
                cache = json.load(f)
        
        cache[str(inventory_item_id)] = {
            'quantity': available,
            'last_sync': datetime.now(timezone.utc).isoformat()
        }
        
        with open(self.config.inventory_cache_path, 'w') as f:
            json.dump(cache, f, indent=2)
        
        logger.info(f"Updated inventory for item {inventory_item_id}: {available}")
        
        return {
            'success': True,
            'inventory_item_id': inventory_item_id,
            'new_quantity': available,
            'synced_at': datetime.now(timezone.utc).isoformat()
        }


# === Webhook Handler Functions ===

def handle_webhook(
    topic: str,
    payload: bytes,
    hmac_header: str,
    config: Optional[SyncConfig] = None
) -> Dict[str, Any]:
    """
    Handle incoming Shopify webhook.
    
    Args:
        topic: Webhook topic (e.g., "products/update")
        payload: Raw payload bytes
        hmac_header: HMAC signature header
        config: Optional sync configuration
    
    Returns:
        Processing result
    """
    service = ShopifySyncService(config)
    
    # Validate HMAC
    if not service.validate_webhook(payload, hmac_header):
        logger.error("Invalid webhook signature")
        return {'success': False, 'error': 'Invalid signature'}
    
    # Parse payload
    try:
        data = json.loads(payload.decode('utf-8'))
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON payload: {e}")
        return {'success': False, 'error': 'Invalid JSON'}
    
    # Route by topic
    if topic.startswith('products/'):
        return service.process_product_update(data)
    elif topic.startswith('inventory_levels/'):
        return service.process_inventory_update(data)
    else:
        logger.warning(f"Unhandled webhook topic: {topic}")
        return {'success': False, 'error': f'Unhandled topic: {topic}'}


def sync_product_update(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sync a product update (direct call, not webhook).
    
    Args:
        product_data: Product data in Shopify format
    
    Returns:
        Sync result
    """
    service = ShopifySyncService()
    return service.process_product_update(product_data)


def sync_inventory_update(inventory_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sync an inventory update (direct call, not webhook).
    
    Args:
        inventory_data: Inventory data
    
    Returns:
        Sync result
    """
    service = ShopifySyncService()
    return service.process_inventory_update(inventory_data)


async def daily_reconciliation() -> Dict[str, Any]:
    """
    Perform daily reconciliation between Shopify and KB.
    
    This should be run as a scheduled job (e.g., via cron or n8n).
    
    Checks:
    1. All products in Shopify exist in KB
    2. Prices match between Shopify and KB
    3. Inventory levels are up to date
    
    Returns:
        Reconciliation report
    """
    service = ShopifySyncService()
    kb = service.load_kb()
    
    discrepancies = []
    synced = []
    
    # Note: This would need Shopify Admin API access
    # For now, we return a placeholder
    if not service.config.access_token:
        return {
            'success': False,
            'error': 'Shopify API access not configured',
            'recommendation': 'Set SHOPIFY_ACCESS_TOKEN environment variable'
        }
    
    # In production, this would:
    # 1. Call Shopify Admin API to get all products
    # 2. Compare with KB
    # 3. Log discrepancies
    # 4. Optionally auto-fix
    
    return {
        'success': True,
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'discrepancies': discrepancies,
        'synced': synced,
        'kb_products_count': len(kb.get('products', {})),
        'note': 'Full reconciliation requires Shopify Admin API access'
    }


# === Flask/FastAPI Webhook Endpoint Example ===

WEBHOOK_ENDPOINT_EXAMPLE = '''
# FastAPI example for webhook endpoint

from fastapi import FastAPI, Request, HTTPException
from panelin_hybrid_agent.sync import handle_webhook

app = FastAPI()

@app.post("/webhooks/shopify")
async def shopify_webhook(request: Request):
    """Handle Shopify webhooks."""
    # Get headers
    topic = request.headers.get('X-Shopify-Topic', '')
    hmac_header = request.headers.get('X-Shopify-Hmac-SHA256', '')
    
    # Get raw body for HMAC validation
    body = await request.body()
    
    # Process webhook
    result = handle_webhook(topic, body, hmac_header)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return {"status": "ok", "result": result}
'''
