"""
Webhook Handler for Shopify
===========================

Handles incoming webhooks from Shopify, validates HMAC signatures,
and routes to appropriate sync functions.
"""

import hashlib
import hmac
import base64
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, TypedDict
from dataclasses import dataclass
import logging

from .shopify_sync import (
    sync_product_from_webhook,
    sync_inventory_from_webhook,
    SyncResult,
)

logger = logging.getLogger(__name__)


class WebhookPayload(TypedDict):
    """Typed webhook payload structure"""
    topic: str
    shop_domain: str
    body: Dict[str, Any]
    timestamp: str


@dataclass
class WebhookConfig:
    """Configuration for webhook handling"""
    secret: str
    allowed_topics: tuple = (
        "products/update",
        "products/create",
        "products/delete",
        "inventory_levels/update",
    )
    shop_domain: str = "bmcuruguay.myshopify.com"


def validate_webhook_hmac(
    body: bytes,
    hmac_header: str,
    secret: str,
) -> bool:
    """
    Validate Shopify webhook HMAC signature.
    
    Args:
        body: Raw request body bytes
        hmac_header: X-Shopify-Hmac-SHA256 header value
        secret: Webhook secret from Shopify app settings
        
    Returns:
        True if valid, False otherwise
    """
    if not secret or not hmac_header:
        return False
    
    # Calculate expected HMAC
    digest = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()
    
    computed_hmac = base64.b64encode(digest).decode("utf-8")
    
    # Constant-time comparison
    return hmac.compare_digest(computed_hmac, hmac_header)


def process_webhook(
    topic: str,
    body: Dict[str, Any],
    shop_domain: str,
    config: Optional[WebhookConfig] = None,
) -> SyncResult:
    """
    Process a validated Shopify webhook.
    
    Args:
        topic: Webhook topic (e.g., "products/update")
        body: Parsed webhook payload
        shop_domain: Shop domain from header
        config: Webhook configuration
        
    Returns:
        SyncResult from the sync operation
    """
    if config is None:
        config = WebhookConfig(secret="")
    
    # Validate shop domain
    if shop_domain != config.shop_domain:
        return SyncResult(
            success=False,
            message=f"Invalid shop domain: {shop_domain}",
        )
    
    # Validate topic
    if topic not in config.allowed_topics:
        return SyncResult(
            success=False,
            message=f"Unhandled topic: {topic}",
        )
    
    logger.info(f"Processing webhook: {topic} from {shop_domain}")
    
    # Route to appropriate handler
    if topic in ("products/update", "products/create"):
        return sync_product_from_webhook(body)
    
    elif topic == "products/delete":
        # Handle product deletion
        product_id = body.get("id")
        logger.warning(f"Product deleted in Shopify: {product_id}")
        return SyncResult(
            success=True,
            message=f"Product deletion logged: {product_id}",
        )
    
    elif topic == "inventory_levels/update":
        return sync_inventory_from_webhook(body)
    
    return SyncResult(
        success=False,
        message=f"No handler for topic: {topic}",
    )


def create_webhook_endpoint_handler(config: WebhookConfig):
    """
    Create a webhook handler function for use with web frameworks.
    
    This returns a function that can be used as a route handler
    with FastAPI, Flask, etc.
    
    Args:
        config: Webhook configuration
        
    Returns:
        Async handler function
    """
    async def handle_webhook(
        body: bytes,
        hmac_header: str,
        topic: str,
        shop_domain: str,
    ) -> Dict[str, Any]:
        """
        Handle incoming Shopify webhook.
        
        Args:
            body: Raw request body
            hmac_header: X-Shopify-Hmac-SHA256 header
            topic: X-Shopify-Topic header
            shop_domain: X-Shopify-Shop-Domain header
            
        Returns:
            Response dict
        """
        # Validate HMAC
        if not validate_webhook_hmac(body, hmac_header, config.secret):
            logger.warning(f"Invalid HMAC for webhook from {shop_domain}")
            return {"status": "error", "message": "Invalid signature"}
        
        # Parse body
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON"}
        
        # Process webhook
        result = process_webhook(
            topic=topic,
            body=payload,
            shop_domain=shop_domain,
            config=config,
        )
        
        return {
            "status": "success" if result.success else "error",
            "message": result.message,
            "updated": result.updated_products,
            "timestamp": result.timestamp,
        }
    
    return handle_webhook


# Example FastAPI integration
"""
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()
webhook_config = WebhookConfig(secret=os.environ.get("SHOPIFY_WEBHOOK_SECRET", ""))
webhook_handler = create_webhook_endpoint_handler(webhook_config)

@app.post("/webhooks/shopify")
async def shopify_webhook(request: Request):
    body = await request.body()
    
    result = await webhook_handler(
        body=body,
        hmac_header=request.headers.get("X-Shopify-Hmac-SHA256", ""),
        topic=request.headers.get("X-Shopify-Topic", ""),
        shop_domain=request.headers.get("X-Shopify-Shop-Domain", ""),
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result
"""
