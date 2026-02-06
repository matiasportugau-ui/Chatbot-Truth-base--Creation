"""
Panelin Agent V2 - Deterministic Tools
=======================================

This module contains all deterministic calculation tools for the Panelin quotation system.
CRITICAL PRINCIPLE: LLM NEVER CALCULATES - All arithmetic is executed in Python with Decimal precision.
"""

from .quotation_calculator import (
    calculate_panel_quote,
    calculate_panels_needed,
    calculate_supports_needed,
    calculate_fixation_points,
    calculate_accessories,
    lookup_product_specs,
    validate_quotation,
    QuotationResult,
    ProductSpecs,
    AccessoriesResult,
)

from .product_lookup import (
    find_product_by_query,
    get_product_price,
    check_product_availability,
)

__all__ = [
    "calculate_panel_quote",
    "calculate_panels_needed",
    "calculate_supports_needed",
    "calculate_fixation_points",
    "calculate_accessories",
    "lookup_product_specs",
    "validate_quotation",
    "QuotationResult",
    "ProductSpecs",
    "AccessoriesResult",
    "find_product_by_query",
    "get_product_price",
    "check_product_availability",
]
