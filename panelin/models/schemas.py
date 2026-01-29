"""
Panelin Schemas - TypedDict definitions for strict typing.

Todos los modelos usan TypedDict para garantizar tipado estricto
y compatibilidad con Structured Outputs de OpenAI/LangChain.
"""

from typing import TypedDict, Literal, Optional, List
from datetime import datetime


class CalculationRules(TypedDict):
    """Reglas de cálculo para un producto específico."""
    minimum_order_m2: float
    bulk_discount_threshold_m2: float
    bulk_discount_percent: float
    max_discount_percent: float


class ProductSpec(TypedDict):
    """Especificaciones de un producto en la KB."""
    shopify_id: Optional[str]
    sku: str
    name: str
    familia: str
    sub_familia: str
    tipo: Literal["Panel", "Accesorio", "Perfileria / Terminaciones", "Anclajes / Fijaciones"]
    price_per_m2: float
    price_per_unit: Optional[float]
    currency: Literal["USD", "UYU"]
    available_thicknesses: Optional[List[int]]
    ancho_util_m: float
    largo_min_m: float
    largo_max_m: float
    calculation_rules: CalculationRules
    inventory_quantity: Optional[int]
    stock_status: Literal["in_stock", "low_stock", "out_of_stock", "unknown"]
    last_updated: str
    sync_source: Literal["shopify_webhook", "shopify_api", "manual", "html_scrape"]


class QuotationLineItem(TypedDict):
    """Un item de línea en una cotización."""
    product_id: str
    product_name: str
    panel_type: str
    thickness_mm: Optional[int]
    length_m: float
    width_m: float
    area_m2: float
    quantity: int
    unit_price_usd: float
    line_total_usd: float


class QuotationResult(TypedDict):
    """Resultado de una cotización calculada deterministicamente."""
    quotation_id: str
    timestamp: str
    line_items: List[QuotationLineItem]
    subtotal_usd: float
    discount_percent: float
    discount_amount_usd: float
    delivery_cost_usd: float
    tax_rate: float
    tax_amount_usd: float
    total_usd: float
    total_uyu: Optional[float]
    exchange_rate: Optional[float]
    calculation_verified: bool  # CRÍTICO: Marca que pasó por código determinista
    verification_checksum: str
    notes: List[str]


class PricingRules(TypedDict):
    """Reglas generales de pricing."""
    tax_rate_uy: float
    delivery_cost_per_m2: float
    minimum_delivery_charge: float
    free_delivery_threshold_usd: float
    default_currency: Literal["USD", "UYU"]


class QuotationRequest(TypedDict):
    """Request de cotización extraído por el LLM."""
    panel_type: str
    thickness_mm: Optional[int]
    length_m: float
    width_m: float
    quantity: int
    discount_percent: Optional[float]
    include_delivery: bool
    include_tax: bool
    customer_type: Literal["retail", "wholesale", "contractor"]


class ValidationResult(TypedDict):
    """Resultado de validación de una cotización."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    checks_performed: List[str]


class ShopifySyncEvent(TypedDict):
    """Evento de sincronización de Shopify."""
    event_type: Literal["product_update", "product_create", "product_delete", "inventory_update"]
    shopify_id: str
    sku: str
    timestamp: str
    old_values: dict
    new_values: dict
    sync_status: Literal["success", "failed", "pending"]
    error_message: Optional[str]


# Tool definitions for LLM (OpenAI Function Calling / LangChain Tools)
CALCULATE_PANEL_QUOTE_TOOL_SCHEMA = {
    "name": "calculate_panel_quote",
    "description": "Calcula cotización exacta para paneles térmicos BMC. USAR SIEMPRE para cualquier cálculo de precio. El LLM NO debe calcular precios directamente.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "panel_type": {
                "type": "string",
                "enum": [
                    "Isopanel EPS", "Isodec EPS", "Isodec PIR", 
                    "Isowall PIR", "Isoroof 3G", "Isoroof Plus 3G",
                    "Isoroof Foil 3G", "Hiansa Panel 5G"
                ],
                "description": "Tipo de panel solicitado"
            },
            "thickness_mm": {
                "type": "integer",
                "enum": [30, 40, 50, 75, 80, 100, 120, 150, 200, 250],
                "description": "Espesor en milímetros (no todos disponibles para todos los paneles)"
            },
            "length_m": {
                "type": "number",
                "minimum": 0.5,
                "maximum": 14.0,
                "description": "Largo del panel en metros"
            },
            "width_m": {
                "type": "number", 
                "minimum": 0.5,
                "maximum": 1.5,
                "description": "Ancho del panel en metros (usar ancho útil del producto)"
            },
            "quantity": {
                "type": "integer",
                "minimum": 1,
                "description": "Cantidad de paneles"
            },
            "discount_percent": {
                "type": "number",
                "minimum": 0,
                "maximum": 30,
                "default": 0,
                "description": "Porcentaje de descuento aplicable (máximo 30%)"
            },
            "include_delivery": {
                "type": "boolean",
                "default": False,
                "description": "Incluir costo de entrega en cotización"
            },
            "include_tax": {
                "type": "boolean",
                "default": False,
                "description": "Incluir IVA (22%) en cotización"
            }
        },
        "required": ["panel_type", "length_m", "width_m", "quantity"]
    }
}

LOOKUP_PRODUCT_SPECS_TOOL_SCHEMA = {
    "name": "lookup_product_specs",
    "description": "Busca especificaciones exactas de un producto en la base de conocimiento. Usar para obtener precios, dimensiones y disponibilidad.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "product_identifier": {
                "type": "string",
                "description": "SKU, nombre de producto, o tipo de panel a buscar"
            },
            "thickness_mm": {
                "type": "integer",
                "description": "Espesor específico a buscar (opcional)"
            }
        },
        "required": ["product_identifier"]
    }
}

SEARCH_PRODUCTS_TOOL_SCHEMA = {
    "name": "search_products",
    "description": "Búsqueda semántica de productos por descripción o uso. Ejemplo: 'paneles económicos para techos planos'",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Descripción del producto o uso buscado"
            },
            "filters": {
                "type": "object",
                "properties": {
                    "familia": {"type": "string"},
                    "min_price": {"type": "number"},
                    "max_price": {"type": "number"},
                    "in_stock_only": {"type": "boolean"}
                }
            },
            "limit": {
                "type": "integer",
                "default": 5,
                "description": "Número máximo de resultados"
            }
        },
        "required": ["query"]
    }
}

VALIDATE_QUOTATION_TOOL_SCHEMA = {
    "name": "validate_quotation",
    "description": "Valida una cotización calculada para verificar integridad y consistencia. SIEMPRE usar después de calculate_panel_quote.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "quotation": {
                "type": "object",
                "description": "Objeto QuotationResult a validar"
            }
        },
        "required": ["quotation"]
    }
}
