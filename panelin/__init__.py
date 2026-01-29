"""
Panelin Quotation Agent v2 - Hybrid Architecture

Este paquete implementa la arquitectura híbrida recomendada para el sistema de 
cotización de paneles aislantes de BMC Uruguay:
- LLM orquesta (comprensión de lenguaje natural)
- Código Python calcula (aritmética determinista con Decimal)

Principios fundamentales:
1. LLM_NEVER_CALCULATES: Todo cálculo matemático en funciones Python con Decimal
2. SINGLE_SOURCE_OF_TRUTH: panelin_truth_bmcuruguay.json es la única fuente de precios
3. DETERMINISTIC_FIRST: Preferir herramientas deterministas sobre razonamiento LLM
4. VALIDATE_EVERYTHING: Cada output de cálculo pasa por verificación

Arquitectura:
┌──────────────────────────────────────────────────────────────────┐
│                    PANELIN QUOTATION AGENT v2                     │
├──────────────────────────────────────────────────────────────────┤
│  Input Usuario → LLM Extracción → Validación → CÁLCULO           │
│  (Lenguaje       (Structured Out)  Schema+Rango  DETERMINISTA    │
│   Natural)                         (Python)      (Python/Decimal)│
│                                                                  │
│  HERRAMIENTAS DETERMINISTAS:                                     │
│  ├── calculate_panel_quote()      - Cotización Isopanel/Isodec  │
│  ├── lookup_product_specs()       - Query JSON KB exacto        │
│  ├── check_inventory_shopify()    - API tiempo real             │
│  ├── apply_pricing_rules()        - Descuentos, mínimos         │
│  └── validate_quotation()         - Verificación cruzada        │
└──────────────────────────────────────────────────────────────────┘
"""

__version__ = "2.0.0"
__author__ = "BMC Uruguay / Panelin Team"

from panelin.tools.quotation_calculator import (
    calculate_panel_quote,
    apply_pricing_rules,
    validate_quotation,
)
from panelin.tools.knowledge_base import (
    lookup_product_specs,
    search_products,
    get_available_products,
)
from panelin.models.schemas import (
    QuotationResult,
    ProductSpec,
    PricingRules,
    QuotationRequest,
)

__all__ = [
    # Tools
    "calculate_panel_quote",
    "apply_pricing_rules",
    "validate_quotation",
    "lookup_product_specs",
    "search_products",
    "get_available_products",
    # Schemas
    "QuotationResult",
    "ProductSpec",
    "PricingRules",
    "QuotationRequest",
]
Panelin core package.

This package hosts deterministic tools and utilities that can be called by an LLM
agent. Critical rule: the LLM orchestrates; Python computes.
"""

