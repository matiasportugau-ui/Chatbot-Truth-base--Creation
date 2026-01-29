"""
Herramientas Deterministas para Panelin Hybrid Agent
====================================================

Todas las herramientas en este módulo ejecutan cálculos de forma DETERMINISTA
usando el tipo Decimal para precisión financiera. El LLM solo extrae parámetros
y llama a estas funciones—NUNCA realiza cálculos directamente.
"""

from .quotation_calculator import (
    calculate_panel_quote,
    calculate_accessories_quote,
    calculate_fixation_points,
    calculate_profiles_quote,
    QuotationResult,
    AccessoriesResult,
    FixationResult,
    ProfilesResult,
)
from .product_lookup import (
    lookup_product_specs,
    search_products_by_criteria,
    get_available_thicknesses,
    get_price_for_product,
)
from .pricing_rules import (
    apply_discount,
    apply_bulk_pricing,
    calculate_delivery_cost,
    get_minimum_order_value,
)

__all__ = [
    # Quotation Calculator
    "calculate_panel_quote",
    "calculate_accessories_quote",
    "calculate_fixation_points",
    "calculate_profiles_quote",
    "QuotationResult",
    "AccessoriesResult",
    "FixationResult",
    "ProfilesResult",
    # Product Lookup
    "lookup_product_specs",
    "search_products_by_criteria",
    "get_available_thicknesses",
    "get_price_for_product",
    # Pricing Rules
    "apply_discount",
    "apply_bulk_pricing",
    "calculate_delivery_cost",
    "get_minimum_order_value",
]
