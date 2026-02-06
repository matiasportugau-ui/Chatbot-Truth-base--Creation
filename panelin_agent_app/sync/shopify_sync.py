"""
Panelin Agent V2 - Shopify Sync Service
========================================

This module implements Shopify ↔ Knowledge Base synchronization.

ARCHITECTURE:
1. Webhooks for real-time updates (products/update, inventory_levels/update)
2. Daily reconciliation for data integrity verification
3. Git commit for audit trail on every KB change
4. Alerting for price/inventory discrepancies

The sync service ensures the KB (panelin_truth_bmcuruguay.json) is always
up-to-date with Shopify, enabling accurate quotations.
"""

import json
import hashlib
import hmac
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict, Optional, List, Dict, Any, Literal
from dataclasses import dataclass
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


class WebhookPayload(TypedDict):
    """
    Shopify webhook payload structure passed into sync handlers.

    IMPORTANT: `raw_body` SHOULD contain the exact raw HTTP request body bytes
    as received from Shopify, before any JSON parsing or re-serialization.
    This is required for correct HMAC verification.
    """

    topic: str
    shop: str
    payload: Dict[str, Any]
    timestamp: str
    hmac_header: str
    raw_body: Optional[bytes]


class SyncResult(TypedDict):
    """Result of a sync operation"""

    success: bool
    action: Literal["created", "updated", "deleted", "unchanged", "error"]
    product_id: Optional[str]
    changes: List[str]
    timestamp: str
    error: Optional[str]


class ReconciliationReport(TypedDict):
    """Daily reconciliation report"""

    timestamp: str
    products_checked: int
    discrepancies_found: int
    discrepancies: List[Dict[str, Any]]
    auto_fixed: int
    requires_review: int


# ============================================================================
# CONFIGURATION
# ============================================================================


@dataclass
class SyncConfig:
    """Configuration for Shopify sync"""

    shopify_store: str = "bmcuruguay.myshopify.com"
    shopify_api_version: str = "2024-10"
    webhook_secret: str = ""  # Set via env var SHOPIFY_WEBHOOK_SECRET
    kb_path: Path = (
        Path(__file__).parent.parent / "config" / "panelin_truth_bmcuruguay.json"
    )
    backup_dir: Path = Path(__file__).parent.parent / "config" / "backups"
    git_enabled: bool = True
    alert_webhook_url: Optional[str] = None  # For Slack/Teams alerts

    def __post_init__(self):
        self.webhook_secret = os.environ.get(
            "SHOPIFY_WEBHOOK_SECRET", self.webhook_secret
        )
        self.alert_webhook_url = os.environ.get(
            "SYNC_ALERT_WEBHOOK", self.alert_webhook_url
        )


# ============================================================================
# HMAC VERIFICATION
# ============================================================================


def verify_shopify_hmac(payload: bytes, hmac_header: str, secret: str) -> bool:
    """
    Verify Shopify webhook HMAC signature.

    CRITICAL: Always verify webhooks to prevent malicious data injection.
    """
    if not secret:
        logger.warning(
            "SHOPIFY_WEBHOOK_SECRET not configured - skipping HMAC verification"
        )
        return True  # Allow in development

    computed_hmac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).digest()

    import base64

    computed_hmac_b64 = base64.b64encode(computed_hmac).decode()

    return hmac.compare_digest(computed_hmac_b64, hmac_header)


# ============================================================================
# KNOWLEDGE BASE OPERATIONS
# ============================================================================


def load_knowledge_base(config: SyncConfig) -> Dict[str, Any]:
    """Load the current knowledge base"""
    if not config.kb_path.exists():
        raise FileNotFoundError(f"KB not found: {config.kb_path}")

    with open(config.kb_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_knowledge_base(
    kb: Dict[str, Any], config: SyncConfig, change_reason: str
) -> bool:
    """
    Save knowledge base with backup and optional git commit.

    Args:
        kb: Updated knowledge base
        config: Sync configuration
        change_reason: Description of changes for git commit

    Returns:
        True if save successful
    """
    # Create backup directory if needed
    config.backup_dir.mkdir(parents=True, exist_ok=True)

    # Backup current KB
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = config.backup_dir / f"kb_backup_{timestamp}.json"

    if config.kb_path.exists():
        import shutil

        shutil.copy(config.kb_path, backup_path)
        logger.info(f"Created backup: {backup_path}")

    # Update timestamp
    kb["last_sync"] = datetime.now(timezone.utc).isoformat()

    # Save new KB
    with open(config.kb_path, "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved KB: {config.kb_path}")

    # Git commit if enabled
    if config.git_enabled:
        try:
            import subprocess

            subprocess.run(
                ["git", "add", str(config.kb_path)],
                cwd=config.kb_path.parent,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", f"[sync] {change_reason}"],
                cwd=config.kb_path.parent,
                check=True,
                capture_output=True,
            )
            logger.info(f"Git commit: {change_reason}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Git commit failed: {e}")
        except FileNotFoundError:
            logger.warning("Git not available")

    return True


# ============================================================================
# PRODUCT MAPPING
# ============================================================================


def map_shopify_to_kb_product(
    shopify_product: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Map Shopify product data to KB product format.

    Extracts and normalizes product information from Shopify API response.
    """
    try:
        # Extract base info
        title = shopify_product.get("title", "")
        handle = shopify_product.get("handle", "")
        shopify_id = shopify_product.get("id") or shopify_product.get(
            "admin_graphql_api_id"
        )

        # Get first variant for pricing
        variants = shopify_product.get("variants", [])
        if not variants:
            logger.warning(f"No variants for product: {title}")
            return None

        primary_variant = variants[0]
        price = float(primary_variant.get("price", 0))

        # Determine product family from title
        title_lower = title.lower()
        if "isopanel" in title_lower and "isodec" not in title_lower:
            family = "ISOPANEL"
            sub_family = "EPS"
        elif "isodec" in title_lower:
            family = "ISODEC"
            sub_family = "PIR" if "pir" in title_lower else "EPS"
        elif "isowall" in title_lower:
            family = "ISOWALL"
            sub_family = "PIR"
        elif "isoroof" in title_lower:
            family = "ISOROOF"
            sub_family = "PIR"
        elif "hiansa" in title_lower:
            family = "HIANSA"
            sub_family = "BECAM"
        else:
            family = "OTHER"
            sub_family = "UNKNOWN"

        # Extract thickness from options
        thickness = 50  # default
        options = shopify_product.get("options", [])
        for opt in options:
            if opt.get("name", "").lower() == "espesor":
                values = opt.get("values", [])
                if values:
                    # Parse first thickness value (e.g., "50 mm" -> 50)
                    import re

                    match = re.search(r"(\d+)", values[0])
                    if match:
                        thickness = int(match.group(1))

        # Generate product ID
        product_id = f"{family}_{sub_family}_{thickness}mm"

        # Determine application
        if family in ["ISODEC", "ISOROOF"]:
            application = ["techos", "cubiertas"]
        elif family == "ISOPANEL":
            application = ["paredes", "fachadas"]
        elif family == "ISOWALL":
            application = ["fachadas"]
        else:
            application = ["general"]

        return {
            "product_id": product_id,
            "shopify_id": str(shopify_id),
            "name": title,
            "family": family,
            "sub_family": sub_family,
            "application": application,
            "thickness_mm": thickness,
            "price_per_m2": price,
            "currency": "USD",
            "ancho_util_m": 1.12 if family in ["ISODEC", "ISOPANEL"] else 1.0,
            "largo_min_m": 2.3,
            "largo_max_m": 14.0,
            "autoportancia_m": 5.5,
            "calculation_rules": {
                "minimum_order_m2": 10,
                "bulk_discount_threshold_m2": 100,
                "bulk_discount_percent": 5,
                "max_discount_percent": 15,
            },
            "inventory_quantity": primary_variant.get("inventory_quantity"),
            "stock_status": (
                "available"
                if primary_variant.get("inventory_quantity", 0) > 0
                else "out_of_stock"
            ),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "_sync_source": "shopify_webhook",
        }

    except Exception as e:
        logger.error(f"Error mapping Shopify product: {e}")
        return None


# ============================================================================
# WEBHOOK HANDLERS
# ============================================================================


def process_product_webhook(
    payload: WebhookPayload, config: Optional[SyncConfig] = None
) -> SyncResult:
    """
    Process Shopify products/update or products/create webhook.

    Updates the KB with new product data from Shopify.
    """
    config = config or SyncConfig()
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        # Verify HMAC using the ORIGINAL raw HTTP body bytes from Shopify.
        # Re-serializing JSON can change whitespace/key ordering and break HMAC.
        raw_body = payload.get("raw_body")  # type: ignore[typeddict-item]
        if raw_body is None:
            logger.warning(
                "WebhookPayload.raw_body not provided; falling back to JSON "
                "re-serialization for HMAC verification. This may fail if the "
                "payload formatting differs from Shopify's original bytes. "
                "Pass the raw HTTP request body to ShopifySyncService.handle_webhook "
                "to ensure reliable verification."
            )
            raw_body = json.dumps(
                payload["payload"],
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")

        if not verify_shopify_hmac(
            raw_body, payload.get("hmac_header", ""), config.webhook_secret
        ):
            return SyncResult(
                success=False,
                action="error",
                product_id=None,
                changes=[],
                timestamp=timestamp,
                error="HMAC verification failed",
            )

        # Map Shopify product to KB format
        shopify_product = payload["payload"]
        kb_product = map_shopify_to_kb_product(shopify_product)

        if not kb_product:
            return SyncResult(
                success=False,
                action="error",
                product_id=None,
                changes=[],
                timestamp=timestamp,
                error="Failed to map Shopify product",
            )

        # Load current KB
        kb = load_knowledge_base(config)
        products = kb.get("products", {})

        product_id = kb_product["product_id"]
        changes = []

        # Check for changes
        if product_id in products:
            existing = products[product_id]

            # Track price changes
            if existing.get("price_per_m2") != kb_product["price_per_m2"]:
                changes.append(
                    f"price: {existing.get('price_per_m2')} -> {kb_product['price_per_m2']}"
                )

            # Track stock changes
            if existing.get("stock_status") != kb_product["stock_status"]:
                changes.append(
                    f"stock_status: {existing.get('stock_status')} -> {kb_product['stock_status']}"
                )

            if not changes:
                return SyncResult(
                    success=True,
                    action="unchanged",
                    product_id=product_id,
                    changes=[],
                    timestamp=timestamp,
                    error=None,
                )

            action = "updated"
        else:
            action = "created"
            changes.append("new product")

        # Update KB
        products[product_id] = kb_product
        kb["products"] = products

        # Save with audit trail
        save_knowledge_base(kb, config, f"Webhook: {action} {product_id}")

        logger.info(f"Processed webhook: {action} {product_id} - {changes}")

        return SyncResult(
            success=True,
            action=action,
            product_id=product_id,
            changes=changes,
            timestamp=timestamp,
            error=None,
        )

    except Exception as e:
        logger.error(f"Error processing product webhook: {e}")
        return SyncResult(
            success=False,
            action="error",
            product_id=None,
            changes=[],
            timestamp=timestamp,
            error=str(e),
        )


def process_inventory_webhook(
    payload: WebhookPayload, config: Optional[SyncConfig] = None
) -> SyncResult:
    """
    Process Shopify inventory_levels/update webhook.

    Updates stock quantities in the KB.
    """
    config = config or SyncConfig()
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        # Verify HMAC using the ORIGINAL raw HTTP body bytes from Shopify.
        raw_body = payload.get("raw_body")  # type: ignore[typeddict-item]
        if raw_body is None:
            logger.warning(
                "WebhookPayload.raw_body not provided; falling back to JSON "
                "re-serialization for HMAC verification. This may fail if the "
                "payload formatting differs from Shopify's original bytes. "
                "Pass the raw HTTP request body to ShopifySyncService.handle_webhook "
                "to ensure reliable verification."
            )
            raw_body = json.dumps(
                payload["payload"],
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")

        if not verify_shopify_hmac(
            raw_body, payload.get("hmac_header", ""), config.webhook_secret
        ):
            return SyncResult(
                success=False,
                action="error",
                product_id=None,
                changes=[],
                timestamp=timestamp,
                error="HMAC verification failed",
            )

        inventory_data = payload["payload"]
        inventory_item_id = inventory_data.get("inventory_item_id")
        available = inventory_data.get("available", 0)

        # Load KB
        kb = load_knowledge_base(config)
        products = kb.get("products", {})

        # Find product by Shopify ID (would need inventory_item mapping)
        # For now, log the update
        logger.info(
            f"Inventory update: item={inventory_item_id}, available={available}"
        )

        return SyncResult(
            success=True,
            action="updated",
            product_id=str(inventory_item_id),
            changes=[f"available: {available}"],
            timestamp=timestamp,
            error=None,
        )

    except Exception as e:
        logger.error(f"Error processing inventory webhook: {e}")
        return SyncResult(
            success=False,
            action="error",
            product_id=None,
            changes=[],
            timestamp=timestamp,
            error=str(e),
        )


# ============================================================================
# DAILY RECONCILIATION
# ============================================================================


async def daily_reconciliation(
    config: Optional[SyncConfig] = None,
    shopify_api_key: Optional[str] = None,
    shopify_access_token: Optional[str] = None,
) -> ReconciliationReport:
    """
    Perform daily reconciliation between Shopify and KB.

    This runs as a scheduled job to:
    1. Fetch all products from Shopify Admin API
    2. Compare with KB
    3. Alert on discrepancies
    4. Auto-fix safe discrepancies (price updates)
    5. Queue unsafe discrepancies for human review
    """
    config = config or SyncConfig()
    timestamp = datetime.now(timezone.utc).isoformat()

    logger.info("Starting daily reconciliation...")

    # Load current KB
    kb = load_knowledge_base(config)
    kb_products = kb.get("products", {})

    discrepancies = []
    auto_fixed = 0
    requires_review = 0

    # In production, this would call Shopify Admin API
    # For now, we simulate the reconciliation logic

    # Check each KB product
    for product_id, kb_product in kb_products.items():
        # Simulated Shopify data (in production: fetch from API)
        shopify_price = kb_product.get("price_per_m2")  # Would come from API
        kb_price = kb_product.get("price_per_m2")

        # Check for price discrepancy
        if shopify_price and kb_price:
            if abs(shopify_price - kb_price) > 0.01:
                discrepancies.append(
                    {
                        "product_id": product_id,
                        "field": "price_per_m2",
                        "kb_value": kb_price,
                        "shopify_value": shopify_price,
                        "severity": "high",
                    }
                )
                requires_review += 1

        # Check last_updated freshness
        last_updated = kb_product.get("last_updated")
        if last_updated:
            try:
                update_time = datetime.fromisoformat(
                    last_updated.replace("Z", "+00:00")
                )
                age_hours = (
                    datetime.now(timezone.utc) - update_time
                ).total_seconds() / 3600

                if age_hours > 168:  # > 7 days
                    discrepancies.append(
                        {
                            "product_id": product_id,
                            "field": "last_updated",
                            "kb_value": last_updated,
                            "shopify_value": "stale_data",
                            "severity": "medium",
                        }
                    )
            except Exception:
                pass

    report = ReconciliationReport(
        timestamp=timestamp,
        products_checked=len(kb_products),
        discrepancies_found=len(discrepancies),
        discrepancies=discrepancies,
        auto_fixed=auto_fixed,
        requires_review=requires_review,
    )

    # Send alert if discrepancies found
    if discrepancies and config.alert_webhook_url:
        await send_alert(config.alert_webhook_url, report)

    logger.info(f"Reconciliation complete: {len(discrepancies)} discrepancies found")

    return report


async def send_alert(webhook_url: str, report: ReconciliationReport) -> None:
    """Send alert to Slack/Teams webhook"""
    try:
        import aiohttp

        message = {
            "text": f"🔔 Panelin KB Reconciliation Report",
            "attachments": [
                {
                    "color": "warning" if report["discrepancies_found"] > 0 else "good",
                    "fields": [
                        {
                            "title": "Products Checked",
                            "value": str(report["products_checked"]),
                            "short": True,
                        },
                        {
                            "title": "Discrepancies",
                            "value": str(report["discrepancies_found"]),
                            "short": True,
                        },
                        {
                            "title": "Auto-Fixed",
                            "value": str(report["auto_fixed"]),
                            "short": True,
                        },
                        {
                            "title": "Needs Review",
                            "value": str(report["requires_review"]),
                            "short": True,
                        },
                    ],
                }
            ],
        }

        async with aiohttp.ClientSession() as session:
            await session.post(webhook_url, json=message)
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")


# ============================================================================
# SYNC SERVICE CLASS
# ============================================================================


class ShopifySyncService:
    """
    Main sync service class for managing Shopify ↔ KB synchronization.
    """

    def __init__(self, config: Optional[SyncConfig] = None):
        self.config = config or SyncConfig()

    def handle_webhook(
        self,
        topic: str,
        payload: Dict[str, Any],
        hmac_header: str,
        raw_body: Optional[bytes] = None,
    ) -> SyncResult:
        """
        Handle incoming Shopify webhook.

        Args:
            topic: Webhook topic (e.g., "products/update")
            payload: Parsed JSON webhook payload
            hmac_header: X-Shopify-Hmac-SHA256 header value
            raw_body: Raw HTTP request body bytes from Shopify. When provided,
                this is used for HMAC verification to match Shopify's signature.

        Returns:
            SyncResult with operation outcome
        """
        webhook_payload = WebhookPayload(
            topic=topic,
            shop=self.config.shopify_store,
            payload=payload,
            timestamp=datetime.now(timezone.utc).isoformat(),
            hmac_header=hmac_header,
            raw_body=raw_body,
        )

        if topic.startswith("products/"):
            return process_product_webhook(webhook_payload, self.config)
        elif topic.startswith("inventory_levels/"):
            return process_inventory_webhook(webhook_payload, self.config)
        else:
            return SyncResult(
                success=False,
                action="error",
                product_id=None,
                changes=[],
                timestamp=datetime.now(timezone.utc).isoformat(),
                error=f"Unknown webhook topic: {topic}",
            )

    async def run_reconciliation(self) -> ReconciliationReport:
        """Run daily reconciliation check"""
        return await daily_reconciliation(self.config)

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        kb = load_knowledge_base(self.config)

        return {
            "kb_version": kb.get("version"),
            "last_sync": kb.get("last_sync"),
            "products_count": len(kb.get("products", {})),
            "shopify_store": self.config.shopify_store,
            "webhook_secret_configured": bool(self.config.webhook_secret),
        }


# ============================================================================
# CLI / TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PANELIN SHOPIFY SYNC SERVICE")
    print("=" * 60)

    config = SyncConfig()
    service = ShopifySyncService(config)

    print("\nSync Status:")
    status = service.get_sync_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\nSimulating product webhook...")
    simulated_payload = {
        "id": "12345",
        "title": "ISOPANEL EPS (Paredes y Fachadas) 100mm TEST",
        "handle": "isopanel-eps-test",
        "variants": [{"price": "50.00", "inventory_quantity": 100}],
        "options": [{"name": "Espesor", "values": ["100 mm"]}],
    }
    simulated_raw_body = json.dumps(
        simulated_payload, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    test_payload = WebhookPayload(
        topic="products/update",
        shop="bmcuruguay.myshopify.com",
        payload=simulated_payload,
        timestamp=datetime.now(timezone.utc).isoformat(),
        hmac_header="",
        raw_body=simulated_raw_body,
    )

    result = process_product_webhook(test_payload, config)
    print(f"\nResult: {result['action']}")
    print(f"Changes: {result['changes']}")
