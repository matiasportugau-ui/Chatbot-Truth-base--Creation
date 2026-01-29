"""
Type definitions for Panelin Hybrid Agent.

These TypedDicts and Enums ensure type safety and enable
structured outputs from LLM parameter extraction.
"""

from enum import Enum
from typing import TypedDict, Optional, List, Literal
from decimal import Decimal


# === Enums for constrained values ===

class PanelType(str, Enum):
    """Available panel types from BMC Uruguay catalog."""
    ISOPANEL_EPS = "Isopanel_EPS"       # Paredes y fachadas EPS
    ISODEC_EPS = "Isodec_EPS"           # Techos EPS
    ISODEC_PIR = "Isodec_PIR"           # Techos PIR (ignífugo)
    ISOROOF_3G = "Isoroof_3G"           # Cubierta liviana
    ISOROOF_PLUS = "Isoroof_Plus"       # Cubierta liviana Plus
    ISOROOF_FOIL = "Isoroof_Foil"       # Cubierta con foil
    ISOWALL_PIR = "Isowall_PIR"         # Paredes PIR
    ISOFRIG_PIR = "Isofrig_PIR"         # Frigoríficos PIR
    HIANSA_5G = "Hiansa_5G"             # Panel trapezoidal


class ThicknessType(int, Enum):
    """Available thickness options in millimeters."""
    T30 = 30
    T50 = 50
    T75 = 75
    T80 = 80
    T100 = 100
    T120 = 120
    T150 = 150
    T200 = 200
    T250 = 250


class MaterialType(str, Enum):
    """Core material types."""
    EPS = "EPS"   # Poliestireno expandido
    PIR = "PIR"   # Poliisocianurato (ignífugo)
    PUR = "PUR"   # Poliuretano


class ApplicationType(str, Enum):
    """Application types for panels."""
    TECHO = "techo"
    PARED = "pared"
    CUBIERTA_LIVIANA = "cubierta_liviana"
    FRIGORIFICO = "frigorifico"


class FixationType(str, Enum):
    """Fixing system types."""
    VARILLA_TUERCA = "varilla_tuerca"       # Para metal/hormigón
    CABALLETE_TORNILLO = "caballete_tornillo"  # Para madera (Isoroof)
    TORNILLO_DIRECTO = "tornillo_directo"    # Fijación directa


class BaseType(str, Enum):
    """Base/structure types for installation."""
    METAL = "metal"
    HORMIGON = "hormigon"
    MADERA = "madera"


# === TypedDicts for structured data ===

class ProductSpec(TypedDict):
    """Product specification from knowledge base."""
    product_id: str
    name: str
    panel_type: str
    material: str
    thickness_mm: int
    ancho_util_m: float
    price_per_m2: float
    currency: str
    autoportancia_m: Optional[float]
    coeficiente_termico: Optional[float]
    resistencia_termica: Optional[float]
    ignifugo: str
    sistema_fijacion: str
    shopify_id: Optional[str]
    last_updated: str


class QuotationLineItem(TypedDict):
    """Individual line item in a quotation."""
    item_type: str  # "panel", "fijacion", "accesorio", "perfileria"
    product_id: str
    description: str
    quantity: int
    unit: str
    unit_price_usd: float
    subtotal_usd: float
    notes: Optional[str]


class QuotationRequest(TypedDict):
    """Request parameters for quotation calculation."""
    panel_type: str
    thickness_mm: int
    length_m: float
    width_m: float
    quantity: int
    base_type: str  # metal, hormigon, madera
    discount_percent: float
    include_fijaciones: bool
    include_perfileria: bool
    project_notes: Optional[str]


class QuotationResult(TypedDict):
    """Result of deterministic quotation calculation."""
    product_id: str
    panel_type: str
    thickness_mm: int
    area_m2: float
    unit_price_usd: float
    quantity: int
    panels_subtotal_usd: float
    fijaciones_subtotal_usd: float
    perfileria_subtotal_usd: float
    subtotal_usd: float
    discount_usd: float
    total_usd: float
    total_with_iva_usd: float
    calculation_verified: bool  # CRITICAL: Must be True
    calculation_method: str     # e.g., "deterministic_python_decimal"
    timestamp: str


class PricingRule(TypedDict):
    """Pricing rule from knowledge base."""
    rule_id: str
    rule_type: str  # "bulk_discount", "minimum_order", "delivery"
    threshold: float
    value: float
    unit: str
    description: str


class ValidationResult(TypedDict):
    """Result of quotation validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    verification_checks: List[str]


class QuotationResponse(TypedDict):
    """Complete quotation response."""
    success: bool
    quotation: Optional[QuotationResult]
    line_items: List[QuotationLineItem]
    validation: ValidationResult
    recommendations: List[str]
    error_message: Optional[str]


# === Tool parameter schemas for LLM ===

CALCULATE_PANEL_QUOTE_SCHEMA = {
    "name": "calculate_panel_quote",
    "description": "Calcula cotización exacta para paneles térmicos BMC Uruguay. USAR SIEMPRE para cualquier cálculo de precio. El LLM NUNCA debe calcular precios directamente.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "panel_type": {
                "type": "string",
                "enum": [
                    "Isopanel_EPS", "Isodec_EPS", "Isodec_PIR",
                    "Isoroof_3G", "Isoroof_Plus", "Isoroof_Foil",
                    "Isowall_PIR", "Isofrig_PIR", "Hiansa_5G"
                ],
                "description": "Tipo de panel según catálogo BMC"
            },
            "thickness_mm": {
                "type": "integer",
                "enum": [30, 50, 75, 80, 100, 120, 150, 200, 250],
                "description": "Espesor del panel en milímetros"
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
                "description": "Ancho útil del panel en metros (verificar catálogo)"
            },
            "quantity": {
                "type": "integer",
                "minimum": 1,
                "description": "Cantidad de paneles"
            },
            "base_type": {
                "type": "string",
                "enum": ["metal", "hormigon", "madera"],
                "default": "metal",
                "description": "Tipo de estructura base para calcular fijaciones"
            },
            "discount_percent": {
                "type": "number",
                "minimum": 0,
                "maximum": 30,
                "default": 0,
                "description": "Porcentaje de descuento aplicable"
            },
            "include_fijaciones": {
                "type": "boolean",
                "default": True,
                "description": "Incluir kit de fijación en cotización"
            },
            "include_perfileria": {
                "type": "boolean",
                "default": True,
                "description": "Incluir perfilería (goteros, etc.) en cotización"
            }
        },
        "required": ["panel_type", "thickness_mm", "length_m", "quantity"],
        "additionalProperties": False
    }
}

LOOKUP_PRODUCT_SPECS_SCHEMA = {
    "name": "lookup_product_specs",
    "description": "Busca especificaciones exactas de un producto en la base de conocimiento. Usar para consultar precios, autoportancia, propiedades térmicas.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "panel_type": {
                "type": "string",
                "description": "Tipo de panel a buscar"
            },
            "thickness_mm": {
                "type": "integer",
                "description": "Espesor específico (opcional)"
            },
            "search_query": {
                "type": "string",
                "description": "Búsqueda por texto libre (opcional)"
            }
        },
        "required": [],
        "additionalProperties": False
    }
}

CHECK_INVENTORY_SCHEMA = {
    "name": "check_inventory_shopify",
    "description": "Verifica disponibilidad de inventario en tiempo real desde Shopify.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "product_id": {
                "type": "string",
                "description": "ID del producto (SKU o Shopify ID)"
            },
            "required_quantity": {
                "type": "integer",
                "minimum": 1,
                "description": "Cantidad requerida"
            }
        },
        "required": ["product_id"],
        "additionalProperties": False
    }
}

# Export all schemas for tool registration
TOOL_SCHEMAS = {
    "calculate_panel_quote": CALCULATE_PANEL_QUOTE_SCHEMA,
    "lookup_product_specs": LOOKUP_PRODUCT_SPECS_SCHEMA,
    "check_inventory_shopify": CHECK_INVENTORY_SCHEMA,
}
