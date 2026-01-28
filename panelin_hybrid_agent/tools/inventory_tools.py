"""
Inventory Tools for Panelin Hybrid Agent.

Provides real-time inventory checking via Shopify API.
DETERMINISTIC lookups - no LLM inference.
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path


def _get_shopify_config() -> Dict[str, Any]:
    """Get Shopify API configuration."""
    config_path = Path(__file__).parent.parent / "config" / "shopify_config.json"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    
    # Fall back to environment variables
    return {
        'store_url': os.environ.get('SHOPIFY_STORE_URL', 'bmcuruguay.myshopify.com'),
        'api_version': os.environ.get('SHOPIFY_API_VERSION', '2024-01'),
        'access_token': os.environ.get('SHOPIFY_ACCESS_TOKEN'),
    }


def _load_cached_inventory() -> Dict[str, Any]:
    """Load cached inventory data (for when API is unavailable)."""
    cache_path = Path(__file__).parent.parent / "knowledge_base" / "inventory_cache.json"
    
    if cache_path.exists():
        with open(cache_path, 'r') as f:
            return json.load(f)
    
    return {}


async def check_inventory_shopify(
    product_id: str,
    required_quantity: int = 1
) -> Dict[str, Any]:
    """
    Check product inventory from Shopify - DETERMINISTIC lookup.
    
    This function queries Shopify Admin API for real-time inventory.
    Falls back to cached data if API is unavailable.
    
    Args:
        product_id: Product SKU or Shopify ID
        required_quantity: Quantity needed
    
    Returns:
        Dictionary with availability status and details
    """
    config = _get_shopify_config()
    
    # For now, use cached/simulated data
    # In production, this would call Shopify Admin API
    
    result = {
        'product_id': product_id,
        'required_quantity': required_quantity,
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'source': 'cache',  # or 'shopify_api' in production
    }
    
    # Check if we have API credentials
    if not config.get('access_token'):
        # Use cached data
        cache = _load_cached_inventory()
        
        if product_id in cache:
            inventory_data = cache[product_id]
            available_qty = inventory_data.get('quantity', 0)
            
            result.update({
                'available': available_qty >= required_quantity,
                'quantity_available': available_qty,
                'quantity_needed': max(0, required_quantity - available_qty),
                'stock_status': 'in_stock' if available_qty > 0 else 'out_of_stock',
                'last_sync': inventory_data.get('last_sync', 'unknown'),
            })
        else:
            result.update({
                'available': None,  # Unknown
                'quantity_available': None,
                'stock_status': 'unknown',
                'note': 'Producto no encontrado en caché. Consultar disponibilidad con ventas.',
            })
    else:
        # In production: Call Shopify Admin API
        # Example implementation:
        # 
        # import httpx
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"https://{config['store_url']}/admin/api/{config['api_version']}/products/{product_id}.json",
        #         headers={'X-Shopify-Access-Token': config['access_token']}
        #     )
        #     data = response.json()
        #     ... process inventory levels ...
        
        result.update({
            'available': None,
            'note': 'API integration pending. Contact sales for availability.',
            'source': 'pending_api_integration'
        })
    
    return result


def get_product_availability(
    product_ids: List[str]
) -> Dict[str, Dict[str, Any]]:
    """
    Check availability for multiple products - DETERMINISTIC.
    
    Args:
        product_ids: List of product SKUs or Shopify IDs
    
    Returns:
        Dictionary mapping product_id to availability status
    """
    cache = _load_cached_inventory()
    
    results = {}
    
    for product_id in product_ids:
        if product_id in cache:
            inventory_data = cache[product_id]
            results[product_id] = {
                'available': inventory_data.get('quantity', 0) > 0,
                'quantity': inventory_data.get('quantity', 0),
                'stock_status': 'in_stock' if inventory_data.get('quantity', 0) > 0 else 'out_of_stock',
                'last_sync': inventory_data.get('last_sync', 'unknown'),
            }
        else:
            results[product_id] = {
                'available': None,
                'quantity': None,
                'stock_status': 'unknown',
            }
    
    return results


def sync_inventory_from_shopify() -> Dict[str, Any]:
    """
    Sync inventory from Shopify to local cache.
    
    This should be called periodically (e.g., daily) or via webhook.
    
    Returns:
        Sync result with counts and any errors
    """
    config = _get_shopify_config()
    
    if not config.get('access_token'):
        return {
            'success': False,
            'error': 'Shopify access token not configured',
            'synced_at': datetime.now(timezone.utc).isoformat()
        }
    
    # In production: Full sync from Shopify
    # This would:
    # 1. Call Shopify Admin API to get all products
    # 2. Get inventory levels for each
    # 3. Update local cache file
    # 4. Log any discrepancies
    
    return {
        'success': False,
        'error': 'Full sync not implemented - use webhook updates',
        'synced_at': datetime.now(timezone.utc).isoformat()
    }
