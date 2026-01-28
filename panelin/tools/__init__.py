"""
Panelin Tools - Herramientas deterministas para el agente híbrido.

Estas herramientas son llamadas por el LLM pero ejecutan código Python determinista.
El LLM NUNCA debe calcular directamente - solo extrae parámetros y llama estas funciones.
"""

from panelin.tools.quotation_calculator import (
    calculate_panel_quote,
    calculate_multi_panel_quote,
    apply_pricing_rules,
    validate_quotation,
)
from panelin.tools.knowledge_base import (
    lookup_product_specs,
    search_products,
    get_available_products,
    get_product_by_sku,
)
from panelin.tools.shopify_sync import (
    handle_shopify_webhook,
    sync_product_from_shopify,
    daily_shopify_reconciliation,
)

__all__ = [
    # Quotation Calculator
    "calculate_panel_quote",
    "calculate_multi_panel_quote",
    "apply_pricing_rules",
    "validate_quotation",
    # Knowledge Base
    "lookup_product_specs",
    "search_products",
    "get_available_products",
    "get_product_by_sku",
    # Shopify Sync
    "handle_shopify_webhook",
    "sync_product_from_shopify",
    "daily_shopify_reconciliation",
]
