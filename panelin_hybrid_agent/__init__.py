"""
Panelin Hybrid Agent v2.0

Arquitectura híbrida para cotización de paneles aislantes BMC Uruguay.

Principio fundamental: LLM orquesta, código calcula.
- El LLM NUNCA ejecuta aritmética
- Solo interpreta intención, extrae parámetros, y formatea respuestas
- Toda operación matemática ocurre en funciones Python deterministas

Stack tecnológico:
- Framework: LangGraph 1.0
- LLM: GPT-4o-mini / Gemini 2.5 Flash / Claude 3.5 Haiku
- KB: JSON estructurado (single source of truth)
- Sync: Webhooks Shopify con reconciliación diaria
"""

__version__ = "2.0.0"
__author__ = "BMC Uruguay AI Team"

from .tools.quotation_calculator import (
    QuotationResult,
    calculate_panel_quote,
    lookup_product_specs,
    apply_pricing_rules,
    validate_quotation,
)
from .tools.inventory_tools import check_inventory_shopify
from .models.types import (
    PanelType,
    ThicknessType,
    QuotationRequest,
    QuotationResponse,
)

__all__ = [
    "QuotationResult",
    "calculate_panel_quote",
    "lookup_product_specs",
    "apply_pricing_rules",
    "validate_quotation",
    "check_inventory_shopify",
    "PanelType",
    "ThicknessType",
    "QuotationRequest",
    "QuotationResponse",
]
