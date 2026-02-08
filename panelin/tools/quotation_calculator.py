"""
Panelin Quotation Calculator - Cálculos deterministas con precisión Decimal.

PRINCIPIO FUNDAMENTAL: El LLM NUNCA calcula - solo extrae parámetros.
Toda la aritmética financiera ocurre aquí con tipo Decimal para precisión garantizada.

Este módulo implementa:
1. calculate_panel_quote() - Cotización de paneles individuales
2. calculate_multi_panel_quote() - Cotización de múltiples paneles
3. apply_pricing_rules() - Aplicación de descuentos y reglas de pricing
4. validate_quotation() - Verificación de integridad de cotización

Uso de Decimal:
- Todos los cálculos financieros usan Decimal, no float
- Redondeo ROUND_HALF_UP para consistencia
- Conversión a float solo al retornar para compatibilidad JSON
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib
import json
import uuid
from pathlib import Path

# Type imports
from panelin.models.schemas import (
    QuotationResult,
    QuotationLineItem,
    ProductSpec,
    ValidationResult,
    PricingRules,
)


# Constants
DECIMAL_PLACES = Decimal('0.01')
DEFAULT_KB_PATH = Path(__file__).parent.parent / "data" / "panelin_truth_bmcuruguay.json"


def _load_knowledge_base(kb_path: Optional[Path] = None) -> Dict[str, Any]:
    """Carga la base de conocimiento desde JSON."""
    path = kb_path or DEFAULT_KB_PATH
    
    # Try multiple possible paths
    possible_paths = [
        path,
        Path(__file__).parent.parent / "panelin_truth_bmcuruguay.json",
        Path(__file__).parent.parent.parent / "panelin_truth_bmcuruguay.json",
    ]
    
    for p in possible_paths:
        if p.exists():
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    raise FileNotFoundError(f"Knowledge base not found. Tried: {possible_paths}")


def _to_decimal(value: float | int | str | Decimal) -> Decimal:
    """Convierte un valor a Decimal de forma segura."""
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Cannot convert {value} to Decimal: {e}")


def _round_currency(value: Decimal) -> Decimal:
    """Redondea un valor monetario a 2 decimales."""
    return value.quantize(DECIMAL_PLACES, rounding=ROUND_HALF_UP)


def _generate_checksum(data: Dict[str, Any]) -> str:
    """Genera un checksum para verificar integridad de la cotización."""
    # Create a deterministic string representation
    checksum_data = {
        "line_items": [
            {
                "product_id": item["product_id"],
                "area_m2": item["area_m2"],
                "quantity": item["quantity"],
                "line_total_usd": item["line_total_usd"]
            }
            for item in data.get("line_items", [])
        ],
        "subtotal_usd": data.get("subtotal_usd"),
        "total_usd": data.get("total_usd"),
    }
    json_str = json.dumps(checksum_data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]


def calculate_panel_quote(
    panel_type: str,
    length_m: float,
    width_m: float,
    quantity: int,
    thickness_mm: Optional[int] = None,
    discount_percent: float = 0.0,
    include_delivery: bool = False,
    include_tax: bool = False,
    kb_path: Optional[Path] = None,
) -> QuotationResult:
    """
    Calcula cotización DETERMINISTA para paneles térmicos BMC.
    
    El LLM NUNCA ejecuta esta matemática—solo extrae parámetros.
    Toda la aritmética usa Decimal para precisión financiera garantizada.
    
    Args:
        panel_type: Tipo de panel (Isopanel EPS, Isodec EPS, etc.)
        length_m: Largo del panel en metros
        width_m: Ancho del panel en metros (normalmente ancho útil del producto)
        quantity: Cantidad de paneles
        thickness_mm: Espesor en mm (opcional, algunos productos tienen espesor fijo)
        discount_percent: Porcentaje de descuento (0-30)
        include_delivery: Incluir costo de entrega
        include_tax: Incluir IVA 22%
        kb_path: Path opcional a la KB (para testing)
    
    Returns:
        QuotationResult con calculation_verified=True
    
    Raises:
        ValueError: Si el producto no existe o parámetros inválidos
    """
    # Load knowledge base
    catalog = _load_knowledge_base(kb_path)
    
    # Normalize panel type for lookup
    panel_key = _normalize_panel_key(panel_type, thickness_mm)
    
    # Get product from catalog
    products = catalog.get("products", {})
    if panel_key not in products:
        # Try fuzzy match
        panel_key = _fuzzy_match_product(panel_type, thickness_mm, products)
        if not panel_key:
            available = list(products.keys())
            raise ValueError(
                f"Producto no encontrado: {panel_type} {thickness_mm}mm. "
                f"Productos disponibles: {available}"
            )
    
    product = products[panel_key]
    
    # Validate dimensions and get adjusted length for cut-to-length
    adjusted_length, cutting_notes = _validate_dimensions(length_m, width_m, product)
    _validate_quantity(quantity)
    _validate_discount(discount_percent)
    
    # Get pricing info
    price_per_m2 = _to_decimal(product["price_per_m2"])
    pricing_rules = catalog.get("pricing_rules", {})
    
    # Calculate with Decimal precision using adjusted length
    area = _to_decimal(adjusted_length) * _to_decimal(width_m)
    area = _round_currency(area)
    
    unit_price = area * price_per_m2
    unit_price = _round_currency(unit_price)
    
    line_total = unit_price * _to_decimal(quantity)
    line_total = _round_currency(line_total)
    
    # Create line item with both requested and actual dimensions
    line_item: QuotationLineItem = {
        "product_id": panel_key,
        "product_name": product.get("name", panel_key),
        "panel_type": panel_type,
        "thickness_mm": thickness_mm,
        "length_m": float(length_m),  # Requested length
        "actual_length_m": float(adjusted_length),  # Actual panel length delivered
        "width_m": float(width_m),
        "area_m2": float(area),  # Area based on actual panel
        "quantity": quantity,
        "unit_price_usd": float(unit_price),
        "line_total_usd": float(line_total),
    }
    
    # Calculate totals
    subtotal = line_total
    
    # Apply discount
    discount_pct = _to_decimal(discount_percent)
    discount_amount = _round_currency(subtotal * discount_pct / _to_decimal(100))
    
    # Check for bulk discount
    total_area = area * _to_decimal(quantity)
    calc_rules = product.get("calculation_rules", {})
    bulk_threshold = _to_decimal(calc_rules.get("bulk_discount_threshold_m2", 100))
    bulk_discount = _to_decimal(calc_rules.get("bulk_discount_percent", 0))
    
    if total_area >= bulk_threshold and discount_pct < bulk_discount:
        # Apply bulk discount instead if higher
        discount_pct = bulk_discount
        discount_amount = _round_currency(subtotal * discount_pct / _to_decimal(100))
    
    after_discount = subtotal - discount_amount
    
    # Calculate delivery
    delivery_cost = _to_decimal(0)
    if include_delivery:
        delivery_per_m2 = _to_decimal(pricing_rules.get("delivery_cost_per_m2", 1.50))
        min_delivery = _to_decimal(pricing_rules.get("minimum_delivery_charge", 50))
        free_threshold = _to_decimal(pricing_rules.get("free_delivery_threshold_usd", 1000))
        
        if after_discount < free_threshold:
            calculated_delivery = total_area * delivery_per_m2
            delivery_cost = max(calculated_delivery, min_delivery)
            delivery_cost = _round_currency(delivery_cost)
    
    # Calculate tax
    tax_rate = _to_decimal(0)
    tax_amount = _to_decimal(0)
    if include_tax:
        tax_rate = _to_decimal(pricing_rules.get("tax_rate_uy", 22)) / _to_decimal(100)
        taxable = after_discount + delivery_cost
        tax_amount = _round_currency(taxable * tax_rate)
    
    # Final total
    total = after_discount + delivery_cost + tax_amount
    total = _round_currency(total)
    
    # Generate quotation ID and timestamp
    quotation_id = f"BMC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Build notes
    notes = cutting_notes.copy()  # Start with cutting notes if any
    if discount_amount > 0:
        notes.append(f"Descuento aplicado: {float(discount_pct)}%")
    if total_area >= bulk_threshold:
        notes.append(f"Descuento por volumen ({float(bulk_threshold)}m² o más)")
    if include_delivery and delivery_cost == 0:
        notes.append(f"Envío gratis (compras mayores a USD {float(free_threshold)})")
    
    # Build result
    result: QuotationResult = {
        "quotation_id": quotation_id,
        "timestamp": timestamp,
        "line_items": [line_item],
        "subtotal_usd": float(subtotal),
        "discount_percent": float(discount_pct),
        "discount_amount_usd": float(discount_amount),
        "delivery_cost_usd": float(delivery_cost),
        "tax_rate": float(tax_rate * _to_decimal(100)),
        "tax_amount_usd": float(tax_amount),
        "total_usd": float(total),
        "total_uyu": None,  # Se puede agregar con exchange_rate
        "exchange_rate": None,
        "calculation_verified": True,  # CRÍTICO: Marca código determinista
        "verification_checksum": "",  # Will be set below
        "notes": notes,
    }
    
    # Generate checksum for verification
    result["verification_checksum"] = _generate_checksum(result)
    
    return result


def calculate_multi_panel_quote(
    items: List[Dict[str, Any]],
    global_discount_percent: float = 0.0,
    include_delivery: bool = False,
    include_tax: bool = False,
    kb_path: Optional[Path] = None,
) -> QuotationResult:
    """
    Calcula cotización para múltiples paneles/productos.
    
    Args:
        items: Lista de diccionarios con panel_type, thickness_mm, length_m, width_m, quantity
        global_discount_percent: Descuento aplicado al total
        include_delivery: Incluir entrega
        include_tax: Incluir IVA
        kb_path: Path a KB (testing)
    
    Returns:
        QuotationResult consolidado
    """
    catalog = _load_knowledge_base(kb_path)
    products = catalog.get("products", {})
    pricing_rules = catalog.get("pricing_rules", {})
    
    line_items: List[QuotationLineItem] = []
    subtotal = _to_decimal(0)
    total_area = _to_decimal(0)
    
    for item in items:
        panel_type = item["panel_type"]
        thickness_mm = item.get("thickness_mm")
        length_m = item["length_m"]
        width_m = item["width_m"]
        quantity = item["quantity"]
        
        # Normalize and find product
        panel_key = _normalize_panel_key(panel_type, thickness_mm)
        if panel_key not in products:
            panel_key = _fuzzy_match_product(panel_type, thickness_mm, products)
            if not panel_key:
                raise ValueError(f"Producto no encontrado: {panel_type} {thickness_mm}mm")
        
        product = products[panel_key]
        
        # Validate dimensions and get adjusted length
        adjusted_length, item_notes = _validate_dimensions(length_m, width_m, product)
        
        # Calculate line item using adjusted length
        price_per_m2 = _to_decimal(product["price_per_m2"])
        area = _round_currency(_to_decimal(adjusted_length) * _to_decimal(width_m))
        unit_price = _round_currency(area * price_per_m2)
        line_total = _round_currency(unit_price * _to_decimal(quantity))
        
        line_items.append({
            "product_id": panel_key,
            "product_name": product.get("name", panel_key),
            "panel_type": panel_type,
            "thickness_mm": thickness_mm,
            "length_m": float(length_m),
            "actual_length_m": float(adjusted_length),
            "width_m": float(width_m),
            "area_m2": float(area),
            "quantity": quantity,
            "unit_price_usd": float(unit_price),
            "line_total_usd": float(line_total),
        })
        
        subtotal += line_total
        total_area += area * _to_decimal(quantity)
    
    # Apply global discount
    discount_pct = _to_decimal(global_discount_percent)
    discount_amount = _round_currency(subtotal * discount_pct / _to_decimal(100))
    after_discount = subtotal - discount_amount
    
    # Delivery
    delivery_cost = _to_decimal(0)
    if include_delivery:
        delivery_per_m2 = _to_decimal(pricing_rules.get("delivery_cost_per_m2", 1.50))
        min_delivery = _to_decimal(pricing_rules.get("minimum_delivery_charge", 50))
        free_threshold = _to_decimal(pricing_rules.get("free_delivery_threshold_usd", 1000))
        
        if after_discount < free_threshold:
            calculated_delivery = total_area * delivery_per_m2
            delivery_cost = _round_currency(max(calculated_delivery, min_delivery))
    
    # Tax
    tax_rate = _to_decimal(0)
    tax_amount = _to_decimal(0)
    if include_tax:
        tax_rate = _to_decimal(pricing_rules.get("tax_rate_uy", 22)) / _to_decimal(100)
        taxable = after_discount + delivery_cost
        tax_amount = _round_currency(taxable * tax_rate)
    
    # Total
    total = _round_currency(after_discount + delivery_cost + tax_amount)
    
    quotation_id = f"BMC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    result: QuotationResult = {
        "quotation_id": quotation_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "line_items": line_items,
        "subtotal_usd": float(subtotal),
        "discount_percent": float(discount_pct),
        "discount_amount_usd": float(discount_amount),
        "delivery_cost_usd": float(delivery_cost),
        "tax_rate": float(tax_rate * _to_decimal(100)),
        "tax_amount_usd": float(tax_amount),
        "total_usd": float(total),
        "total_uyu": None,
        "exchange_rate": None,
        "calculation_verified": True,
        "verification_checksum": "",
        "notes": [],
    }
    
    result["verification_checksum"] = _generate_checksum(result)
    return result


def apply_pricing_rules(
    subtotal: float,
    total_area_m2: float,
    customer_type: str = "retail",
    kb_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Aplica reglas de pricing (descuentos, mínimos, etc.)
    
    Args:
        subtotal: Subtotal antes de descuentos
        total_area_m2: Área total en m²
        customer_type: retail, wholesale, contractor
        kb_path: Path a KB
    
    Returns:
        Diccionario con descuentos aplicables y reglas
    """
    catalog = _load_knowledge_base(kb_path)
    pricing_rules = catalog.get("pricing_rules", {})
    
    subtotal_dec = _to_decimal(subtotal)
    area_dec = _to_decimal(total_area_m2)
    
    # Determine applicable discounts
    applicable_discounts = []
    
    # Volume discount
    if area_dec >= _to_decimal(100):
        applicable_discounts.append({
            "type": "volume",
            "description": "Descuento por volumen (100m² o más)",
            "percent": 5.0,
        })
    if area_dec >= _to_decimal(200):
        applicable_discounts.append({
            "type": "volume",
            "description": "Descuento por volumen mayor (200m² o más)",
            "percent": 8.0,
        })
    
    # Customer type discount
    customer_discounts = {
        "retail": 0.0,
        "wholesale": 5.0,
        "contractor": 10.0,
    }
    if customer_type in customer_discounts and customer_discounts[customer_type] > 0:
        applicable_discounts.append({
            "type": "customer_type",
            "description": f"Descuento cliente {customer_type}",
            "percent": customer_discounts[customer_type],
        })
    
    # Calculate best discount (they don't stack)
    best_discount = max([d["percent"] for d in applicable_discounts], default=0.0)
    
    return {
        "applicable_discounts": applicable_discounts,
        "recommended_discount_percent": best_discount,
        "minimum_order_value": pricing_rules.get("minimum_order_value", 100),
        "free_delivery_threshold": pricing_rules.get("free_delivery_threshold_usd", 1000),
        "pricing_rules_version": catalog.get("version", "unknown"),
    }


def validate_quotation(quotation: QuotationResult) -> ValidationResult:
    """
    Valida una cotización para verificar integridad y consistencia.
    
    Verifica:
    1. calculation_verified == True
    2. Checksum matches
    3. Line items sum to subtotal
    4. Total = subtotal - discount + delivery + tax
    5. All prices are positive
    
    Args:
        quotation: QuotationResult a validar
    
    Returns:
        ValidationResult con errores/warnings
    """
    errors: List[str] = []
    warnings: List[str] = []
    checks_performed: List[str] = []
    
    # Check 1: calculation_verified flag
    checks_performed.append("calculation_verified_flag")
    if not quotation.get("calculation_verified"):
        errors.append("CRITICAL: calculation_verified is False - quotation may have been calculated by LLM")
    
    # Check 2: Checksum verification
    checks_performed.append("checksum_verification")
    expected_checksum = _generate_checksum(quotation)
    if quotation.get("verification_checksum") != expected_checksum:
        errors.append(f"Checksum mismatch: expected {expected_checksum}, got {quotation.get('verification_checksum')}")
    
    # Check 3: Line items sum
    checks_performed.append("line_items_sum")
    line_items = quotation.get("line_items", [])
    calculated_subtotal = sum(item["line_total_usd"] for item in line_items)
    if abs(calculated_subtotal - quotation.get("subtotal_usd", 0)) > 0.01:
        errors.append(f"Line items sum ({calculated_subtotal}) != subtotal ({quotation.get('subtotal_usd')})")
    
    # Check 4: Total calculation
    checks_performed.append("total_calculation")
    subtotal = _to_decimal(quotation.get("subtotal_usd", 0))
    discount = _to_decimal(quotation.get("discount_amount_usd", 0))
    delivery = _to_decimal(quotation.get("delivery_cost_usd", 0))
    tax = _to_decimal(quotation.get("tax_amount_usd", 0))
    expected_total = float(_round_currency(subtotal - discount + delivery + tax))
    
    if abs(expected_total - quotation.get("total_usd", 0)) > 0.01:
        errors.append(f"Total calculation error: expected {expected_total}, got {quotation.get('total_usd')}")
    
    # Check 5: Positive prices
    checks_performed.append("positive_prices")
    if quotation.get("subtotal_usd", 0) < 0:
        errors.append("Subtotal is negative")
    if quotation.get("total_usd", 0) < 0:
        errors.append("Total is negative")
    for item in line_items:
        if item.get("unit_price_usd", 0) < 0:
            errors.append(f"Negative unit price for {item.get('product_id')}")
    
    # Check 6: Discount within limits
    checks_performed.append("discount_limits")
    if quotation.get("discount_percent", 0) > 30:
        errors.append(f"Discount exceeds maximum (30%): {quotation.get('discount_percent')}%")
    
    # Warnings
    if quotation.get("total_usd", 0) < 100:
        warnings.append("Total is below minimum order value (USD 100)")
    
    if len(line_items) == 0:
        warnings.append("Quotation has no line items")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        checks_performed=checks_performed,
    )


def _normalize_panel_key(panel_type: str, thickness_mm: Optional[int]) -> str:
    """Normaliza el identificador de producto para lookup en KB."""
    # Clean up panel type
    normalized = panel_type.lower().strip()
    
    # Map common names to KB keys
    type_mapping = {
        "isopanel eps": "isopanel_eps",
        "isopanel": "isopanel_eps",
        "isodec eps": "isodec_eps",
        "isodec pir": "isodec_pir",
        "isodec": "isodec_eps",
        "isowall pir": "isowall_pir",
        "isowall": "isowall_pir",
        "isoroof 3g": "isoroof_3g",
        "isoroof": "isoroof_3g",
        "isoroof plus 3g": "isoroof_plus_3g",
        "isoroof plus": "isoroof_plus_3g",
        "isoroof foil 3g": "isoroof_foil_3g",
        "isoroof foil": "isoroof_foil_3g",
        "hiansa panel 5g": "hiansa_panel_5g",
        "hiansa panel": "hiansa_panel_5g",
        "hiansa": "hiansa_panel_5g",
    }
    
    base_key = type_mapping.get(normalized, normalized.replace(" ", "_"))
    
    if thickness_mm:
        return f"{base_key}_{thickness_mm}mm"
    return base_key


def _fuzzy_match_product(
    panel_type: str,
    thickness_mm: Optional[int],
    products: Dict[str, Any]
) -> Optional[str]:
    """Intenta hacer match fuzzy de producto."""
    normalized = panel_type.lower().strip()
    
    # Try exact match first
    for key in products:
        if normalized in key.lower():
            if thickness_mm is None or f"{thickness_mm}mm" in key:
                return key
    
    # Try without thickness only if thickness was not specified
    if thickness_mm is None:
        for key in products:
            if normalized.replace(" ", "_") in key.lower():
                return key
    
    return None


def _validate_dimensions(
    length_m: float, 
    width_m: float, 
    product: Dict[str, Any]
) -> tuple[float, List[str]]:
    """
    Valida dimensiones y ajusta para paneles que requieren corte.
    
    Returns:
        Tuple of (adjusted_length, notes)
    """
    min_length = product.get("largo_min_m", 2.3)
    max_length = product.get("largo_max_m", 14.0)
    notes = []
    adjusted_length = length_m
    
    # If length is below minimum, calculate cut-to-length solution
    if length_m < min_length:
        # Calculate how many minimum panels can be cut from one panel
        cutting_waste_per_cut = 0.01  # 1cm waste per cut
        usable_length_per_panel = min_length - cutting_waste_per_cut
        panels_per_stock = int(usable_length_per_panel / length_m)
        
        if panels_per_stock > 0:
            adjusted_length = min_length
            notes.append(
                f"Largo solicitado {length_m}m es menor al mínimo de producción ({min_length}m). "
                f"Se entregarán paneles de {min_length}m para cortar en obra. "
                f"De cada panel se pueden obtener {panels_per_stock} piezas de {length_m}m "
                f"(considerando 1cm de desperdicio por corte)."
            )
        else:
            raise ValueError(
                f"Largo {length_m}m demasiado corto. "
                f"Mínimo recomendado: {min_length / 2}m para corte en obra."
            )
    
    if length_m > max_length:
        raise ValueError(f"Largo {length_m}m excede máximo de {max_length}m")
    
    if width_m <= 0 or width_m > 2.0:
        raise ValueError(f"Ancho {width_m}m inválido (debe ser entre 0 y 2m)")
    
    return adjusted_length, notes


def _validate_quantity(quantity: int) -> None:
    """Valida cantidad."""
    if quantity < 1:
        raise ValueError(f"Cantidad debe ser al menos 1, recibido: {quantity}")


def _validate_discount(discount_percent: float) -> None:
    """Valida porcentaje de descuento."""
    if discount_percent < 0 or discount_percent > 30:
        raise ValueError(f"Descuento {discount_percent}% fuera de rango (0-30%)")
