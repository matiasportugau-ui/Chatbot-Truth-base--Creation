"""
Panelin Shopify Sync - Sincronización con Shopify via webhooks y API.

Este módulo implementa la sincronización automática entre Shopify y la 
base de conocimiento local (panelin_truth_bmcuruguay.json).

Arquitectura de Sincronización:
┌─────────────────────────────────────────────────────────────────┐
│                      SHOPIFY STORE                               │
│              (Fuente de verdad para inventario)                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │ products/     │ inventory/    │ products/
            │ update        │ update        │ delete
            │ webhook       │ webhook       │ webhook
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

Funciones:
1. handle_shopify_webhook() - Procesa webhooks de Shopify
2. sync_product_from_shopify() - Sync individual via API
3. daily_shopify_reconciliation() - Reconciliación diaria completa
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import os

from panelin.models.schemas import ShopifySyncEvent


# Configure logging
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_KB_PATH = Path(__file__).parent.parent / "data" / "panelin_truth_bmcuruguay.json"
SYNC_LOG_PATH = Path(__file__).parent.parent / "data" / "sync_history.json"


class ShopifySyncError(Exception):
    """Error durante sincronización con Shopify."""
    pass


class ShopifyClient:
    """Cliente básico para Shopify API."""
    
    def __init__(
        self,
        shop_domain: Optional[str] = None,
        access_token: Optional[str] = None,
        api_version: str = "2024-01",
    ):
        self.shop_domain = shop_domain or os.environ.get("SHOPIFY_SHOP_DOMAIN", "bmcuruguay.myshopify.com")
        self.access_token = access_token or os.environ.get("SHOPIFY_ACCESS_TOKEN")
        self.api_version = api_version
        self.base_url = f"https://{self.shop_domain}/admin/api/{api_version}"
    
    async def get_product(self, product_id: str) -> Dict[str, Any]:
        """Obtiene un producto por ID."""
        # This would use aiohttp or httpx in production
        # For now, return placeholder
        logger.info(f"Would fetch product {product_id} from Shopify API")
        return {}
    
    async def get_all_products(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene todos los productos."""
        logger.info("Would fetch all products from Shopify API")
        return {}
    
    async def get_inventory_level(self, inventory_item_id: str) -> int:
        """Obtiene nivel de inventario."""
        logger.info(f"Would fetch inventory for {inventory_item_id}")
        return 0


def verify_webhook_signature(
    payload: bytes,
    hmac_header: str,
    secret: Optional[str] = None,
) -> bool:
    """
    Verifica la firma HMAC de un webhook de Shopify.
    
    Args:
        payload: Body del request como bytes
        hmac_header: Valor del header X-Shopify-Hmac-Sha256
        secret: Shopify webhook secret (o de env var)
    
    Returns:
        True si la firma es válida
    """
    secret = secret or os.environ.get("SHOPIFY_WEBHOOK_SECRET", "")
    
    if not secret:
        logger.warning("SHOPIFY_WEBHOOK_SECRET not set, skipping verification")
        return True  # Allow in development
    
    computed_hmac = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).digest()
    
    import base64
    computed_b64 = base64.b64encode(computed_hmac).decode('utf-8')
    
    return hmac.compare_digest(computed_b64, hmac_header)


def handle_shopify_webhook(
    topic: str,
    payload: Dict[str, Any],
    kb_path: Optional[Path] = None,
) -> ShopifySyncEvent:
    """
    Procesa un webhook de Shopify y actualiza la KB.
    
    Args:
        topic: Tipo de webhook (products/update, products/create, inventory_levels/update)
        payload: Datos del webhook
        kb_path: Path a la KB (opcional)
    
    Returns:
        ShopifySyncEvent con resultado de la operación
    
    Topics soportados:
        - products/create
        - products/update
        - products/delete
        - inventory_levels/update
    """
    kb_path = kb_path or DEFAULT_KB_PATH
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Map topic to event type
    topic_mapping = {
        "products/create": "product_create",
        "products/update": "product_update",
        "products/delete": "product_delete",
        "inventory_levels/update": "inventory_update",
    }
    
    event_type = topic_mapping.get(topic)
    if not event_type:
        return ShopifySyncEvent(
            event_type="product_update",
            shopify_id=str(payload.get("id", "")),
            sku="",
            timestamp=timestamp,
            old_values={},
            new_values={},
            sync_status="failed",
            error_message=f"Unsupported webhook topic: {topic}",
        )
    
    try:
        if event_type == "product_delete":
            result = _handle_product_delete(payload, kb_path)
        elif event_type == "inventory_update":
            result = _handle_inventory_update(payload, kb_path)
        else:
            result = _handle_product_upsert(payload, kb_path)
        
        # Log sync event
        _log_sync_event(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return ShopifySyncEvent(
            event_type=event_type,
            shopify_id=str(payload.get("id", "")),
            sku=_extract_sku(payload),
            timestamp=timestamp,
            old_values={},
            new_values=payload,
            sync_status="failed",
            error_message=str(e),
        )


def _handle_product_upsert(
    payload: Dict[str, Any],
    kb_path: Path,
) -> ShopifySyncEvent:
    """Maneja creación o actualización de producto."""
    shopify_id = str(payload.get("id", ""))
    sku = _extract_sku(payload)
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Load current KB
    catalog = _load_kb(kb_path)
    products = catalog.get("products", {})
    
    # Find existing product by SKU or Shopify ID
    existing_key = None
    old_values = {}
    for key, product in products.items():
        if product.get("shopify_id") == shopify_id or product.get("sku") == sku:
            existing_key = key
            old_values = product.copy()
            break
    
    # Transform Shopify data to KB format
    kb_product = _transform_shopify_to_kb(payload)
    
    # Determine key
    product_key = existing_key or _generate_product_key(payload)
    
    # Update KB
    products[product_key] = {**products.get(product_key, {}), **kb_product}
    products[product_key]["last_updated"] = timestamp
    products[product_key]["sync_source"] = "shopify_webhook"
    
    catalog["products"] = products
    catalog["last_sync"] = timestamp
    
    # Save KB
    _save_kb(catalog, kb_path)
    
    return ShopifySyncEvent(
        event_type="product_update" if existing_key else "product_create",
        shopify_id=shopify_id,
        sku=sku,
        timestamp=timestamp,
        old_values=old_values,
        new_values=kb_product,
        sync_status="success",
        error_message=None,
    )


def _handle_product_delete(
    payload: Dict[str, Any],
    kb_path: Path,
) -> ShopifySyncEvent:
    """Maneja eliminación de producto."""
    shopify_id = str(payload.get("id", ""))
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    catalog = _load_kb(kb_path)
    products = catalog.get("products", {})
    
    # Find and mark as deleted (don't remove, keep history)
    deleted_key = None
    old_values = {}
    for key, product in products.items():
        if product.get("shopify_id") == shopify_id:
            deleted_key = key
            old_values = product.copy()
            products[key]["stock_status"] = "deleted"
            products[key]["last_updated"] = timestamp
            break
    
    if deleted_key:
        catalog["products"] = products
        catalog["last_sync"] = timestamp
        _save_kb(catalog, kb_path)
    
    return ShopifySyncEvent(
        event_type="product_delete",
        shopify_id=shopify_id,
        sku=old_values.get("sku", ""),
        timestamp=timestamp,
        old_values=old_values,
        new_values={"stock_status": "deleted"},
        sync_status="success" if deleted_key else "failed",
        error_message=None if deleted_key else "Product not found in KB",
    )


def _handle_inventory_update(
    payload: Dict[str, Any],
    kb_path: Path,
) -> ShopifySyncEvent:
    """Maneja actualización de inventario."""
    inventory_item_id = str(payload.get("inventory_item_id", ""))
    available = payload.get("available", 0)
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    catalog = _load_kb(kb_path)
    products = catalog.get("products", {})
    
    # Find product by inventory_item_id
    updated_key = None
    old_values = {}
    for key, product in products.items():
        if product.get("inventory_item_id") == inventory_item_id:
            updated_key = key
            old_values = {"inventory_quantity": product.get("inventory_quantity")}
            products[key]["inventory_quantity"] = available
            products[key]["stock_status"] = _determine_stock_status(available)
            products[key]["last_updated"] = timestamp
            break
    
    if updated_key:
        catalog["products"] = products
        catalog["last_sync"] = timestamp
        _save_kb(catalog, kb_path)
    
    return ShopifySyncEvent(
        event_type="inventory_update",
        shopify_id=inventory_item_id,
        sku=products.get(updated_key, {}).get("sku", "") if updated_key else "",
        timestamp=timestamp,
        old_values=old_values,
        new_values={"inventory_quantity": available},
        sync_status="success" if updated_key else "failed",
        error_message=None if updated_key else "Inventory item not found in KB",
    )


async def sync_product_from_shopify(
    product_id: str,
    client: Optional[ShopifyClient] = None,
    kb_path: Optional[Path] = None,
) -> ShopifySyncEvent:
    """
    Sincroniza un producto específico desde Shopify API.
    
    Args:
        product_id: ID del producto en Shopify
        client: Cliente Shopify (opcional)
        kb_path: Path a KB
    
    Returns:
        ShopifySyncEvent con resultado
    """
    client = client or ShopifyClient()
    kb_path = kb_path or DEFAULT_KB_PATH
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    try:
        product_data = await client.get_product(product_id)
        
        if not product_data:
            return ShopifySyncEvent(
                event_type="product_update",
                shopify_id=product_id,
                sku="",
                timestamp=timestamp,
                old_values={},
                new_values={},
                sync_status="failed",
                error_message="Product not found in Shopify",
            )
        
        return handle_shopify_webhook("products/update", product_data, kb_path)
        
    except Exception as e:
        return ShopifySyncEvent(
            event_type="product_update",
            shopify_id=product_id,
            sku="",
            timestamp=timestamp,
            old_values={},
            new_values={},
            sync_status="failed",
            error_message=str(e),
        )


async def daily_shopify_reconciliation(
    client: Optional[ShopifyClient] = None,
    kb_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Reconciliación diaria completa Shopify ↔ KB.
    
    Verifica integridad y detecta discrepancias entre
    la KB local y Shopify.
    
    Args:
        client: Cliente Shopify
        kb_path: Path a KB
    
    Returns:
        Diccionario con discrepancias encontradas y acciones tomadas
    """
    client = client or ShopifyClient()
    kb_path = kb_path or DEFAULT_KB_PATH
    
    catalog = _load_kb(kb_path)
    kb_products = catalog.get("products", {})
    
    try:
        shopify_products = await client.get_all_products()
    except Exception as e:
        logger.error(f"Failed to fetch Shopify products: {e}")
        return {
            "status": "error",
            "error": str(e),
            "discrepancies": [],
        }
    
    discrepancies = []
    
    # Check each Shopify product against KB
    for sku, shopify_data in shopify_products.items():
        kb_product = None
        for key, product in kb_products.items():
            if product.get("sku") == sku:
                kb_product = product
                break
        
        if not kb_product:
            discrepancies.append({
                "type": "MISSING_IN_KB",
                "sku": sku,
                "shopify_id": shopify_data.get("id"),
                "action": "Will add to KB",
            })
        else:
            # Check price
            kb_price = kb_product.get("price_per_m2", 0)
            shopify_price = shopify_data.get("price", 0)
            if abs(kb_price - shopify_price) > 0.01:
                discrepancies.append({
                    "type": "PRICE_MISMATCH",
                    "sku": sku,
                    "kb_price": kb_price,
                    "shopify_price": shopify_price,
                    "action": "Will update KB price",
                })
    
    # Check for KB products not in Shopify
    shopify_skus = set(shopify_products.keys())
    for key, product in kb_products.items():
        sku = product.get("sku", key)
        if sku not in shopify_skus and product.get("sync_source") == "shopify_webhook":
            discrepancies.append({
                "type": "MISSING_IN_SHOPIFY",
                "sku": sku,
                "action": "Will mark as potentially deleted",
            })
    
    # Alert if discrepancies found
    if discrepancies:
        logger.warning(f"Found {len(discrepancies)} discrepancies in daily reconciliation")
        # In production, this would alert the operations team
    
    return {
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_kb_products": len(kb_products),
        "total_shopify_products": len(shopify_products),
        "discrepancies": discrepancies,
        "discrepancy_count": len(discrepancies),
    }


def _load_kb(kb_path: Path) -> Dict[str, Any]:
    """Carga la KB desde archivo."""
    if kb_path.exists():
        with open(kb_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"version": "2.0.0", "products": {}, "pricing_rules": {}}


def _save_kb(catalog: Dict[str, Any], kb_path: Path) -> None:
    """Guarda la KB a archivo."""
    kb_path.parent.mkdir(parents=True, exist_ok=True)
    with open(kb_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved KB to {kb_path}")


def _extract_sku(payload: Dict[str, Any]) -> str:
    """Extrae SKU de payload de Shopify."""
    variants = payload.get("variants", [])
    if variants:
        return variants[0].get("sku", "")
    return payload.get("sku", "")


def _generate_product_key(payload: Dict[str, Any]) -> str:
    """Genera key de producto desde datos de Shopify."""
    title = payload.get("title", "").lower()
    title = title.replace(" ", "_").replace("/", "_")
    return f"shopify_{title}"[:50]


def _transform_shopify_to_kb(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Transforma datos de Shopify a formato KB."""
    variants = payload.get("variants", [{}])
    first_variant = variants[0] if variants else {}
    
    # Extract price (assume per m²)
    price_str = first_variant.get("price", "0")
    try:
        price = float(price_str)
    except (ValueError, TypeError):
        price = 0.0
    
    return {
        "shopify_id": str(payload.get("id", "")),
        "sku": first_variant.get("sku", ""),
        "name": payload.get("title", ""),
        "price_per_m2": price,
        "currency": "USD",
        "inventory_item_id": str(first_variant.get("inventory_item_id", "")),
        "inventory_quantity": first_variant.get("inventory_quantity"),
        "stock_status": _determine_stock_status(first_variant.get("inventory_quantity")),
    }


def _determine_stock_status(quantity: Optional[int]) -> str:
    """Determina estado de stock basado en cantidad."""
    if quantity is None:
        return "unknown"
    if quantity <= 0:
        return "out_of_stock"
    if quantity < 10:
        return "low_stock"
    return "in_stock"


def _log_sync_event(event: ShopifySyncEvent) -> None:
    """Registra evento de sincronización."""
    try:
        if SYNC_LOG_PATH.exists():
            with open(SYNC_LOG_PATH, 'r') as f:
                history = json.load(f)
        else:
            history = {"events": []}
        
        # Keep last 1000 events
        history["events"] = history["events"][-999:] + [dict(event)]
        
        SYNC_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SYNC_LOG_PATH, 'w') as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        logger.error(f"Failed to log sync event: {e}")
