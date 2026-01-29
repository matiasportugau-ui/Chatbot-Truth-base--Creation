"""
Panelin Hybrid Agent v2.0
========================

Arquitectura óptima para cotización de paneles aislantes BMC Uruguay.

Principio fundamental: LLM orquesta, código calcula.
El LLM NUNCA ejecuta aritmética—solo interpreta intención, extrae parámetros,
y formatea respuestas. Toda operación matemática ocurre en funciones Python
deterministas usando el tipo Decimal.

Componentes principales:
- tools/: Herramientas deterministas de cálculo y búsqueda
- agent/: Agente LangGraph con single-agent pattern
- kb/: Knowledge Base JSON como fuente de verdad
- sync/: Sincronización automática con Shopify
- validation/: Sistema de validación y testing
"""

__version__ = "2.0.0"
__author__ = "BMC Uruguay AI Team"

from .tools.quotation_calculator import (
    calculate_panel_quote,
    calculate_accessories_quote,
    QuotationResult,
    AccessoriesResult,
)
from .tools.product_lookup import (
    lookup_product_specs,
    search_products_by_criteria,
)
from .validation.validators import (
    validate_quotation,
    validate_kb_integrity,
)

__all__ = [
    "calculate_panel_quote",
    "calculate_accessories_quote",
    "QuotationResult",
    "AccessoriesResult",
    "lookup_product_specs",
    "search_products_by_criteria",
    "validate_quotation",
    "validate_kb_integrity",
]
