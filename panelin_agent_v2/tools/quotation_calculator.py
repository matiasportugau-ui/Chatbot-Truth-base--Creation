"""
Panelin Agent V2 - Deterministic Quotation Calculator
======================================================

CRITICAL ARCHITECTURE PRINCIPLE:
- The LLM NEVER performs arithmetic calculations
- All mathematical operations use Python's Decimal for financial precision
- Every calculation is deterministic and verifiable
- Results include 'calculation_verified: True' flag to ensure LLM didn't calculate

This module implements all quotation calculations for BMC Uruguay panel products.
"""

from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
from typing import TypedDict, Optional, List, Literal
from pathlib import Path
import json
import math

# Type definitions for structured outputs
class ProductSpecs(TypedDict):
    product_id: str
    name: str
    family: str
    sub_family: str
    thickness_mm: int
    price_per_m2: float
    currency: str
    ancho_util_m: float
    largo_min_m: float
    largo_max_m: float
    autoportancia_m: float
    stock_status: str


class AccessoriesResult(TypedDict):
    panels_needed: int
    supports_needed: int
    fixation_points: int
    rod_quantity: int
    front_drip_edge_units: int
    lateral_drip_edge_units: int
    rivets_needed: int
    silicone_tubes: int
    metal_nuts: int
    concrete_nuts: int
    concrete_anchors: int


class QuotationLineItem(TypedDict):
    product_id: str
    name: str
    quantity: int
    area_m2: float
    unit_price_usd: float
    line_total_usd: float


class QuotationResult(TypedDict):
    """Complete quotation result with deterministic calculations"""
    quotation_id: str
    product_id: str
    product_name: str
    
    # Dimensions
    length_m: float  # Requested length
    actual_length_m: float  # Actual panel length delivered
    width_m: float
    area_m2: float
    
    # Panel calculations
    panels_needed: int
    unit_price_per_m2: float
    
    # Pricing
    subtotal_usd: float
    discount_percent: float
    discount_amount_usd: float
    total_before_tax_usd: float
    tax_amount_usd: float
    total_usd: float
    
    # Accessories (optional)
    accessories: Optional[AccessoriesResult]
    accessories_total_usd: float
    
    # Grand total
    grand_total_usd: float
    
    # Verification flag - CRITICAL: must always be True
    calculation_verified: bool
    calculation_method: str
    currency: str
    notes: List[str]  # Notes including cutting instructions


def _load_knowledge_base() -> dict:
    """Load the single source of truth knowledge base"""
    kb_path = Path(__file__).parent.parent / "config" / "panelin_truth_bmcuruguay.json"
    if not kb_path.exists():
        raise FileNotFoundError(f"Knowledge base not found at {kb_path}")
    
    with open(kb_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _decimal_round(value: Decimal, places: int = 2) -> Decimal:
    """Round decimal to specified places using banker's rounding"""
    quantizer = Decimal(10) ** -places
    return value.quantize(quantizer, rounding=ROUND_HALF_UP)


def _decimal_ceil(value: Decimal) -> int:
    """Ceiling function for Decimal values"""
    return int(value.to_integral_value(rounding=ROUND_CEILING))


def lookup_product_specs(
    product_id: Optional[str] = None,
    family: Optional[str] = None,
    thickness_mm: Optional[int] = None,
    application: Optional[str] = None
) -> Optional[ProductSpecs]:
    """
    Look up product specifications from the knowledge base.
    
    This is a DETERMINISTIC lookup - no LLM inference involved.
    
    Args:
        product_id: Exact product ID (e.g., "ISOPANEL_EPS_50mm")
        family: Product family (e.g., "ISOPANEL", "ISODEC", "ISOROOF")
        thickness_mm: Panel thickness in millimeters
        application: Application type (e.g., "techos", "paredes", "fachadas")
    
    Returns:
        ProductSpecs dictionary or None if not found
    """
    kb = _load_knowledge_base()
    products = kb.get("products", {})
    
    # Direct lookup by product_id - if specified, must match exactly
    if product_id:
        if product_id in products:
            p = products[product_id]
            return ProductSpecs(
                product_id=product_id,
                name=p["name"],
                family=p["family"],
                sub_family=p["sub_family"],
                thickness_mm=p["thickness_mm"],
                price_per_m2=p["price_per_m2"],
                currency=p["currency"],
                ancho_util_m=p["ancho_util_m"],
                largo_min_m=p["largo_min_m"],
                largo_max_m=p["largo_max_m"],
                autoportancia_m=p["autoportancia_m"],
                stock_status=p["stock_status"]
            )
        else:
            # product_id was specified but not found - return None
            return None
    
    # Search by criteria (only when no product_id specified)
    for pid, p in products.items():
        match = True
        if family and p.get("family", "").upper() != family.upper():
            match = False
        if thickness_mm and p.get("thickness_mm") != thickness_mm:
            match = False
        if application and application.lower() not in [a.lower() for a in p.get("application", [])]:
            match = False
        
        if match:
            return ProductSpecs(
                product_id=pid,
                name=p["name"],
                family=p["family"],
                sub_family=p["sub_family"],
                thickness_mm=p["thickness_mm"],
                price_per_m2=p["price_per_m2"],
                currency=p["currency"],
                ancho_util_m=p["ancho_util_m"],
                largo_min_m=p["largo_min_m"],
                largo_max_m=p["largo_max_m"],
                autoportancia_m=p["autoportancia_m"],
                stock_status=p["stock_status"]
            )
    
    return None


def calculate_panels_needed(ancho_total: float, ancho_util: float) -> int:
    """
    Calculate number of panels needed.
    Formula: ROUNDUP(Ancho Total / Ancho Útil)
    
    Uses Decimal for precision.
    """
    if ancho_total <= 0:
        raise ValueError("ancho_total must be greater than 0")
    if ancho_util <= 0:
        raise ValueError("ancho_util must be greater than 0")
    
    ancho_total_d = Decimal(str(ancho_total))
    ancho_util_d = Decimal(str(ancho_util))
    
    return _decimal_ceil(ancho_total_d / ancho_util_d)


def calculate_supports_needed(largo: float, autoportancia: float) -> int:
    """
    Calculate number of supports (apoyos) needed.
    Formula: ROUNDUP((Largo / Autoportancia) + 1)
    
    Uses Decimal for precision.
    """
    if autoportancia <= 0:
        raise ValueError("autoportancia must be greater than 0")
    
    largo_d = Decimal(str(largo))
    autoportancia_d = Decimal(str(autoportancia))
    
    return _decimal_ceil((largo_d / autoportancia_d) + 1)


def calculate_fixation_points(
    cantidad_paneles: int,
    apoyos: int,
    largo: float,
    installation_type: Literal["techo", "pared"] = "techo"
) -> int:
    """
    Calculate fixation points needed.
    
    For roof (techo):
        ROUNDUP(((Cantidad * Apoyos) * 2) + (Largo * 2 / 2.5))
    
    For wall (pared):
        ROUNDUP((Cantidad * Apoyos) * 2)
    """
    largo_d = Decimal(str(largo))
    
    if installation_type == "techo":
        base = Decimal(cantidad_paneles * apoyos * 2)
        edge_fixations = largo_d * 2 / Decimal("2.5")
        return _decimal_ceil(base + edge_fixations)
    else:
        return _decimal_ceil(Decimal(cantidad_paneles * apoyos * 2))


def calculate_accessories(
    cantidad_paneles: int,
    apoyos: int,
    largo: float,
    ancho_util: float,
    installation_type: Literal["techo", "pared"] = "techo"
) -> AccessoriesResult:
    """
    Calculate all accessories needed for the installation.
    
    All calculations use deterministic formulas from the knowledge base.
    """
    puntos_fijacion = calculate_fixation_points(
        cantidad_paneles, apoyos, largo, installation_type
    )
    
    largo_d = Decimal(str(largo))
    ancho_util_d = Decimal(str(ancho_util))
    
    # Rod quantity: ROUNDUP(puntos / 4)
    rod_quantity = _decimal_ceil(Decimal(puntos_fijacion) / Decimal("4"))
    
    # Front drip edge: ROUNDUP((cantidad * ancho_util) / 3)
    front_drip = _decimal_ceil(
        (Decimal(cantidad_paneles) * ancho_util_d) / Decimal("3")
    )
    
    # Lateral drip edge: ROUNDUP((largo * 2) / 3)
    lateral_drip = _decimal_ceil((largo_d * 2) / Decimal("3"))
    
    # Total profiles for rivets
    total_perfiles = front_drip + lateral_drip
    
    # Rivets: ROUNDUP(total_perfiles * 20)
    rivets = _decimal_ceil(Decimal(total_perfiles) * Decimal("20"))
    
    # Silicone: estimate based on perimeter
    perimetro = (Decimal(cantidad_paneles) * ancho_util_d * 2) + (largo_d * 2)
    silicone_tubes = _decimal_ceil(perimetro / Decimal("8"))
    
    return AccessoriesResult(
        panels_needed=cantidad_paneles,
        supports_needed=apoyos,
        fixation_points=puntos_fijacion,
        rod_quantity=rod_quantity,
        front_drip_edge_units=front_drip,
        lateral_drip_edge_units=lateral_drip,
        rivets_needed=rivets,
        silicone_tubes=silicone_tubes,
        metal_nuts=puntos_fijacion * 2,
        concrete_nuts=puntos_fijacion,
        concrete_anchors=puntos_fijacion
    )


def calculate_panel_quote(
    product_id: str,
    length_m: float,
    width_m: float,
    quantity: int = 1,
    discount_percent: float = 0.0,
    include_accessories: bool = False,
    include_tax: bool = True,
    installation_type: Literal["techo", "pared"] = "techo"
) -> QuotationResult:
    """
    Calculate DETERMINISTIC quotation for panel products.
    
    CRITICAL: The LLM NEVER executes this arithmetic - it only extracts parameters.
    All calculations use Python's Decimal for financial precision.
    
    Args:
        product_id: Product identifier (e.g., "ISOPANEL_EPS_50mm")
        length_m: Panel length in meters (largo)
        width_m: Total width to cover in meters (ancho total)
        quantity: Number of identical panels/installations
        discount_percent: Discount percentage (0-30)
        include_accessories: Whether to calculate accessories
        include_tax: Whether to include IVA (22%)
        installation_type: "techo" or "pared"
    
    Returns:
        QuotationResult with all calculations verified
        
    Raises:
        ValueError: If product not found or parameters invalid
    """
    # Load KB and validate product
    kb = _load_knowledge_base()
    products = kb.get("products", {})
    
    if product_id not in products:
        raise ValueError(f"Product not found: {product_id}")
    
    product = products[product_id]
    pricing_rules = kb.get("pricing_rules", {})
    
    # Validate parameters
    if length_m <= 0 or width_m <= 0:
        raise ValueError("Dimensions must be greater than 0")
    
    # Validate dimensions and adjust for cut-to-length
    largo_min = product["largo_min_m"]
    largo_max = product["largo_max_m"]
    adjusted_length = length_m
    cutting_notes = []
    
    # If length is below minimum, calculate cut-to-length solution
    if length_m < largo_min:
        # Calculate how many minimum panels can be cut from one panel
        cutting_waste_per_cut = 0.01  # 1cm waste per cut
        usable_length_per_panel = largo_min - cutting_waste_per_cut
        panels_per_stock = int(usable_length_per_panel / length_m)
        
        if panels_per_stock > 0:
            adjusted_length = largo_min
            cutting_notes.append(
                f"Largo solicitado {length_m}m es menor al mínimo de producción ({largo_min}m). "
                f"Se entregarán paneles de {largo_min}m para cortar en obra. "
                f"De cada panel se pueden obtener {panels_per_stock} piezas de {length_m}m "
                f"(considerando 1cm de desperdicio por corte)."
            )
        else:
            raise ValueError(
                f"Largo {length_m}m demasiado corto. "
                f"Mínimo recomendado: {largo_min / 2}m para corte en obra."
            )
    
    if length_m > largo_max:
        raise ValueError(f"Length {length_m}m exceeds maximum {largo_max}m")
    
    if discount_percent < 0 or discount_percent > product["calculation_rules"]["max_discount_percent"]:
        raise ValueError(f"Discount must be between 0 and {product['calculation_rules']['max_discount_percent']}%")
    
    if quantity < 1:
        raise ValueError("Quantity must be at least 1")
    
    # === DETERMINISTIC CALCULATIONS WITH DECIMAL ===
    
    # Convert to Decimal for precision (use adjusted length for pricing)
    length_d = Decimal(str(adjusted_length))
    width_d = Decimal(str(width_m))
    price_per_m2_d = Decimal(str(product["price_per_m2"]))
    discount_d = Decimal(str(discount_percent))
    tax_rate_d = Decimal(str(pricing_rules.get("tax_rate_uy_iva", 0.22)))
    ancho_util_d = Decimal(str(product["ancho_util_m"]))
    
    # Calculate area per panel
    area_per_panel = _decimal_round(length_d * width_d)
    
    # Calculate panels needed (if width > ancho_util)
    panels_needed = calculate_panels_needed(float(width_d), product["ancho_util_m"])
    
    # Effective coverage area
    effective_area = _decimal_round(length_d * (ancho_util_d * panels_needed))
    
    # Unit price based on area
    unit_price = _decimal_round(area_per_panel * price_per_m2_d)
    
    # Subtotal for all quantities
    subtotal = _decimal_round(effective_area * price_per_m2_d * Decimal(quantity))
    
    # Apply bulk discount if applicable
    bulk_rules = product["calculation_rules"]
    total_m2 = float(effective_area) * quantity
    
    actual_discount = discount_d
    if total_m2 >= bulk_rules["bulk_discount_threshold_m2"]:
        bulk_discount = Decimal(str(bulk_rules["bulk_discount_percent"]))
        actual_discount = max(discount_d, bulk_discount)
    
    # Calculate discount amount
    discount_amount = _decimal_round(subtotal * actual_discount / Decimal("100"))
    
    # Total before tax
    total_before_tax = _decimal_round(subtotal - discount_amount)
    
    # Tax
    tax_amount = Decimal("0")
    if include_tax:
        tax_amount = _decimal_round(total_before_tax * tax_rate_d)
    
    # Total
    total = _decimal_round(total_before_tax + tax_amount)
    
    # Accessories calculation
    accessories = None
    accessories_total = Decimal("0")
    
    if include_accessories:
        apoyos = calculate_supports_needed(length_m, product["autoportancia_m"])
        accessories = calculate_accessories(
            panels_needed * quantity,
            apoyos,
            length_m,
            product["ancho_util_m"],
            installation_type
        )
        # Placeholder for accessories pricing (would need to sum from KB)
        accessories_total = Decimal("0")  # TODO: Calculate from accessories prices
    
    # Grand total
    grand_total = _decimal_round(total + accessories_total)
    
    # Generate quotation ID
    import uuid
    from datetime import datetime
    quotation_id = f"QT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    return QuotationResult(
        quotation_id=quotation_id,
        product_id=product_id,
        product_name=product["name"],
        
        length_m=float(length_m),  # Requested length
        actual_length_m=float(adjusted_length),  # Actual panel length
        width_m=float(width_d),
        area_m2=float(effective_area),
        
        panels_needed=panels_needed,
        unit_price_per_m2=float(price_per_m2_d),
        
        subtotal_usd=float(subtotal),
        discount_percent=float(actual_discount),
        discount_amount_usd=float(discount_amount),
        total_before_tax_usd=float(total_before_tax),
        tax_amount_usd=float(tax_amount),
        total_usd=float(total),
        
        accessories=accessories,
        accessories_total_usd=float(accessories_total),
        
        grand_total_usd=float(grand_total),
        
        # CRITICAL: This flag indicates calculation was done by Python, not LLM
        calculation_verified=True,
        calculation_method="python_decimal_deterministic",
        currency="USD",
        notes=cutting_notes  # Include cutting notes
    )


def validate_quotation(result: QuotationResult) -> tuple[bool, List[str]]:
    """
    Validate a quotation result for consistency.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # CRITICAL: Verify calculation was done by code, not LLM
    if not result.get("calculation_verified"):
        errors.append("CRITICAL: calculation_verified is False - LLM may have calculated")
    
    if result.get("calculation_method") != "python_decimal_deterministic":
        errors.append(f"Unexpected calculation method: {result.get('calculation_method')}")
    
    # Validate numeric consistency
    if result["total_usd"] <= 0:
        errors.append("Total USD must be greater than 0")
    
    if result["area_m2"] <= 0:
        errors.append("Area must be greater than 0")
    
    if result["panels_needed"] < 1:
        errors.append("Must need at least 1 panel")
    
    # Validate discount application
    expected_discount = Decimal(str(result["subtotal_usd"])) * Decimal(str(result["discount_percent"])) / Decimal("100")
    expected_discount = float(_decimal_round(expected_discount))
    
    if abs(result["discount_amount_usd"] - expected_discount) > 0.01:
        errors.append(f"Discount calculation mismatch: {result['discount_amount_usd']} vs expected {expected_discount}")
    
    # Validate total calculation
    expected_total_before_tax = result["subtotal_usd"] - result["discount_amount_usd"]
    if abs(result["total_before_tax_usd"] - expected_total_before_tax) > 0.01:
        errors.append("Total before tax calculation mismatch")
    
    return (len(errors) == 0, errors)


# Tool definitions for LLM integration
TOOL_DEFINITIONS = [
    {
        "name": "calculate_panel_quote",
        "description": "Calcula cotización exacta para paneles térmicos BMC. USAR SIEMPRE para cualquier cálculo de precio. El LLM NUNCA debe calcular precios directamente.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "ID del producto (ej: ISOPANEL_EPS_50mm, ISODEC_EPS_100mm, ISOROOF_3G)"
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
                    "maximum": 50.0,
                    "description": "Ancho total a cubrir en metros"
                },
                "quantity": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 1,
                    "description": "Cantidad de instalaciones/paneles"
                },
                "discount_percent": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 30,
                    "default": 0,
                    "description": "Porcentaje de descuento aplicable"
                },
                "include_accessories": {
                    "type": "boolean",
                    "default": False,
                    "description": "Incluir cálculo de accesorios"
                },
                "include_tax": {
                    "type": "boolean",
                    "default": True,
                    "description": "Incluir IVA (22%)"
                },
                "installation_type": {
                    "type": "string",
                    "enum": ["techo", "pared"],
                    "default": "techo",
                    "description": "Tipo de instalación"
                }
            },
            "required": ["product_id", "length_m", "width_m"]
        }
    },
    {
        "name": "lookup_product_specs",
        "description": "Busca especificaciones de un producto en la base de conocimiento. Usar para consultar precios, dimensiones y disponibilidad.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "ID exacto del producto"
                },
                "family": {
                    "type": "string",
                    "enum": ["ISOPANEL", "ISODEC", "ISOWALL", "ISOROOF", "HIANSA"],
                    "description": "Familia de producto"
                },
                "thickness_mm": {
                    "type": "integer",
                    "description": "Espesor en milímetros"
                },
                "application": {
                    "type": "string",
                    "enum": ["techos", "paredes", "fachadas", "cubiertas", "agro"],
                    "description": "Tipo de aplicación"
                }
            }
        }
    },
    {
        "name": "calculate_accessories",
        "description": "Calcula accesorios necesarios para la instalación de paneles.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "cantidad_paneles": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Cantidad de paneles"
                },
                "apoyos": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Cantidad de apoyos"
                },
                "largo": {
                    "type": "number",
                    "description": "Largo en metros"
                },
                "ancho_util": {
                    "type": "number",
                    "description": "Ancho útil del panel en metros"
                },
                "installation_type": {
                    "type": "string",
                    "enum": ["techo", "pared"],
                    "default": "techo"
                }
            },
            "required": ["cantidad_paneles", "apoyos", "largo", "ancho_util"]
        }
    }
]
