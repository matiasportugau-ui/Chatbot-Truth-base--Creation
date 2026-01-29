"""
Deterministic tools for Panelin Hybrid Agent.

CRITICAL PRINCIPLE: LLM orquesta, código calcula.
All mathematical operations MUST be performed by these Python functions,
NEVER by the LLM directly.
"""

from .quotation_calculator import (
    QuotationResult,
    calculate_panel_quote,
    lookup_product_specs,
    apply_pricing_rules,
    validate_quotation,
    calculate_fijaciones,
    calculate_perfileria,
)
from .inventory_tools import (
    check_inventory_shopify,
    get_product_availability,
)

__all__ = [
    "QuotationResult",
    "calculate_panel_quote",
    "lookup_product_specs",
    "apply_pricing_rules",
    "validate_quotation",
    "calculate_fijaciones",
    "calculate_perfileria",
    "check_inventory_shopify",
    "get_product_availability",
]
