"""
Panelin Agent V2 - Single Agent Architecture for BMC Uruguay Quotations
========================================================================

Este módulo implementa la arquitectura óptima para agentes GPT de cotización
en e-commerce, siguiendo los principios de 2025:

1. LLM NUNCA CALCULA - Solo extrae parámetros de lenguaje natural
2. Python/Decimal ejecuta toda la aritmética financiera
3. Single-agent con herramientas deterministas (no multi-agent)
4. KB sincronizada con Shopify en tiempo real

Arquitectura:
    ┌─────────────┐    ┌──────────────────┐    ┌────────────────┐
    │ Input       │───→│ LLM: Extracción  │───→│ Validación     │
    │ Usuario     │    │ de Parámetros    │    │ Schema + Rango │
    └─────────────┘    └──────────────────┘    └───────┬────────┘
                                                       │
    ┌─────────────┐    ┌──────────────────┐    ┌───────▼────────┐
    │ LLM:        │←───│ Verificación     │←───│ CÁLCULO        │
    │ Formato     │    │ Dual-Path        │    │ DETERMINISTA   │
    │ Respuesta   │    │                  │    │ (Python/       │
    │             │    │                  │    │  Decimal)      │
    └─────────────┘    └──────────────────┘    └────────────────┘

Uso básico:
    from panelin_agent_v2 import calculate_panel_quote, find_product_by_query
    
    # Buscar producto
    products = find_product_by_query("isopanel 100mm para techo")
    
    # Calcular cotización (determinista)
    quote = calculate_panel_quote(
        product_id=products[0]["product_id"],
        length_m=6.0,
        width_m=4.0,
        quantity=1
    )
    
    # Verificar que el cálculo fue por Python, no LLM
    assert quote["calculation_verified"] == True

Costos estimados:
    - GPT-4o-mini: ~$0.002 por cotización
    - Gemini 2.5 Flash: ~$0.002 por cotización
    - Precisión: 100% (código determinista)

Referencias:
    - LangGraph 1.0: https://langchain-ai.github.io/langgraph/
    - Anthropic Building Effective Agents (2025)
    - OpenAI Responses API (reemplaza Assistants API)
"""

__version__ = "2.0.0"
__author__ = "Panelin Team"
__architecture__ = "single_agent_deterministic_tools"

# Core tools - Always available
from .tools.quotation_calculator import (
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

from .tools.product_lookup import (
    find_product_by_query,
    get_product_price,
    check_product_availability,
    list_all_products,
    get_pricing_rules,
)

# Sync service
from .sync.shopify_sync import (
    ShopifySyncService,
    process_product_webhook,
    process_inventory_webhook,
    daily_reconciliation,
)

# Agent (requires LangGraph)
try:
    from .agent.panelin_agent import (
        PanelinQuotationAgent,
        create_agent,
        run_quotation_query,
    )
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    PanelinQuotationAgent = None
    create_agent = None
    run_quotation_query = None

__all__ = [
    # Version info
    "__version__",
    "__architecture__",
    
    # Quotation calculator
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
    
    # Product lookup
    "find_product_by_query",
    "get_product_price",
    "check_product_availability",
    "list_all_products",
    "get_pricing_rules",
    
    # Sync service
    "ShopifySyncService",
    "process_product_webhook",
    "process_inventory_webhook",
    "daily_reconciliation",
    
    # Agent (conditional)
    "PanelinQuotationAgent",
    "create_agent",
    "run_quotation_query",
    "AGENT_AVAILABLE",
]
