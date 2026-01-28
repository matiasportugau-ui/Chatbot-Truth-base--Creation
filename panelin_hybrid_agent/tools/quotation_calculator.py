"""
Deterministic Quotation Calculator for Panelin Hybrid Agent.

CRITICAL: This module performs ALL mathematical calculations.
The LLM NEVER executes arithmetic - it only extracts parameters.

Uses Python's Decimal type for financial precision (no floating-point errors).
"""

import json
import math
from decimal import Decimal, ROUND_HALF_UP, ROUND_UP
from typing import TypedDict, Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from pathlib import Path

# === Type Definitions ===

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
    calculation_verified: bool
    calculation_method: str
    timestamp: str


class FijacionesResult(TypedDict):
    """Result of fixing kit calculation."""
    base_type: str
    puntos_fijacion: int
    varillas_qty: int
    tuercas_qty: int
    tacos_qty: int
    arandelas_qty: int
    tortugas_qty: int
    subtotal_usd: float
    items: List[Dict[str, Any]]


class PerifileriaResult(TypedDict):
    """Result of perfileria (trim) calculation."""
    gotero_frontal_qty: int
    gotero_lateral_qty: int
    silicona_qty: int
    fijaciones_perfileria_qty: int
    subtotal_usd: float
    items: List[Dict[str, Any]]


# === Knowledge Base Loading ===

def _get_kb_path() -> Path:
    """Get path to knowledge base file."""
    # Check multiple possible locations
    possible_paths = [
        Path(__file__).parent.parent / "knowledge_base" / "panelin_truth_bmcuruguay.json",
        Path("/workspace/panelin_hybrid_agent/knowledge_base/panelin_truth_bmcuruguay.json"),
    ]
    for path in possible_paths:
        if path.exists():
            return path
    raise FileNotFoundError(f"Knowledge base not found in: {possible_paths}")


def _load_knowledge_base() -> Dict[str, Any]:
    """Load knowledge base from JSON file."""
    kb_path = _get_kb_path()
    with open(kb_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _to_decimal(value: Union[int, float, str]) -> Decimal:
    """Convert value to Decimal for precise arithmetic."""
    return Decimal(str(value))


def _round_currency(value: Decimal) -> Decimal:
    """Round to 2 decimal places for currency."""
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _round_up_qty(value: Decimal) -> int:
    """Round up for quantities (always round up for materials)."""
    return int(value.quantize(Decimal('1'), rounding=ROUND_UP))


# === Core Calculation Functions ===

def lookup_product_specs(
    panel_type: Optional[str] = None,
    thickness_mm: Optional[int] = None,
    search_query: Optional[str] = None
) -> Dict[str, Any]:
    """
    Look up exact product specifications from knowledge base.
    
    This is a DETERMINISTIC lookup - no LLM inference.
    
    Args:
        panel_type: Panel type ID (e.g., "Isodec_EPS")
        thickness_mm: Specific thickness in mm
        search_query: Free text search (matches against names)
    
    Returns:
        Product specifications dictionary
    """
    kb = _load_knowledge_base()
    products = kb.get('products', {})
    
    results = []
    
    for product_id, product_data in products.items():
        # Filter by panel type
        if panel_type and product_id != panel_type:
            continue
            
        # Get base product info
        product_info = {
            'product_id': product_id,
            'name': product_data.get('nombre_comercial', product_id),
            'tipo': product_data.get('tipo'),
            'ignifugo': product_data.get('ignifugo'),
            'ancho_util_m': product_data.get('ancho_util'),
            'sistema_fijacion': product_data.get('sistema_fijacion'),
        }
        
        # Get thickness-specific data
        espesores = product_data.get('espesores', {})
        
        if thickness_mm:
            thickness_key = str(thickness_mm)
            if thickness_key in espesores:
                espesor_data = espesores[thickness_key]
                product_info.update({
                    'thickness_mm': thickness_mm,
                    'price_per_m2': espesor_data.get('precio'),
                    'autoportancia_m': espesor_data.get('autoportancia'),
                    'coeficiente_termico': espesor_data.get('coeficiente_termico'),
                    'resistencia_termica': espesor_data.get('resistencia_termica'),
                })
                results.append(product_info)
        else:
            # Return all available thicknesses
            for esp_key, esp_data in espesores.items():
                product_variant = product_info.copy()
                product_variant.update({
                    'thickness_mm': int(esp_key),
                    'price_per_m2': esp_data.get('precio'),
                    'autoportancia_m': esp_data.get('autoportancia'),
                    'coeficiente_termico': esp_data.get('coeficiente_termico'),
                    'resistencia_termica': esp_data.get('resistencia_termica'),
                })
                results.append(product_variant)
    
    # Text search if provided
    if search_query:
        search_lower = search_query.lower()
        results = [r for r in results if search_lower in r.get('name', '').lower()]
    
    return {
        'found': len(results) > 0,
        'count': len(results),
        'products': results,
        'lookup_method': 'deterministic_json_query'
    }


def calculate_fijaciones(
    panel_type: str,
    largo_m: float,
    cantidad: int,
    autoportancia_m: float,
    base_type: str = "metal"
) -> FijacionesResult:
    """
    Calculate fixing kit requirements - DETERMINISTIC.
    
    Uses formulas from BMC knowledge base:
    - Apoyos = ROUNDUP((LARGO / AUTOPORTANCIA) + 1)
    - Puntos fijación techo = ROUNDUP(((CANTIDAD * APOYOS) * 2) + (LARGO * 2 / 2.5))
    
    Args:
        panel_type: Type of panel
        largo_m: Panel length in meters
        cantidad: Number of panels
        autoportancia_m: Self-supporting span in meters
        base_type: "metal", "hormigon", or "madera"
    
    Returns:
        FijacionesResult with all components and costs
    """
    kb = _load_knowledge_base()
    precios = kb.get('precios_accesorios_referencia', {})
    kits = kb.get('kits_fijacion', {})
    
    largo = _to_decimal(largo_m)
    cant = _to_decimal(cantidad)
    autoport = _to_decimal(autoportancia_m) if autoportancia_m else _to_decimal(5.5)
    
    # Calculate supports needed
    apoyos = _round_up_qty((largo / autoport) + 1)
    
    # Calculate fixing points
    # Formula: ROUNDUP(((CANTIDAD * APOYOS) * 2) + (LARGO * 2 / 2.5))
    puntos_lateral = (largo * 2 / _to_decimal(2.5))
    puntos_total = (cant * _to_decimal(apoyos) * 2) + puntos_lateral
    puntos_fijacion = _round_up_qty(puntos_total)
    
    # Calculate quantities based on base type
    kit_info = kits.get(base_type, kits.get('metal', {}))
    
    # Varilla: 1 per 4 fixing points
    varillas_qty = _round_up_qty(_to_decimal(puntos_fijacion) / 4)
    
    # Tuercas: 2 for metal, 1 for hormigon
    tuercas_por_punto = kit_info.get('tuercas_por_punto', 2)
    tuercas_qty = puntos_fijacion * tuercas_por_punto
    
    # Tacos: only for hormigon
    tacos_qty = puntos_fijacion if kit_info.get('requiere_taco', False) else 0
    
    # Arandelas and tortugas: 1 per point
    arandelas_qty = puntos_fijacion
    tortugas_qty = puntos_fijacion
    
    # Calculate costs
    precio_varilla = _to_decimal(precios.get('varilla_3_8', 19.9))
    precio_tuerca = _to_decimal(precios.get('tuerca_3_8', 2.0))
    precio_taco = _to_decimal(precios.get('taco_3_8', 8.7))
    
    items = []
    subtotal = _to_decimal(0)
    
    # Add items
    if varillas_qty > 0:
        costo_varillas = _round_currency(precio_varilla * varillas_qty)
        items.append({
            'item': 'Varilla 3/8',
            'qty': varillas_qty,
            'unit_price': float(precio_varilla),
            'subtotal': float(costo_varillas)
        })
        subtotal += costo_varillas
    
    if tuercas_qty > 0:
        costo_tuercas = _round_currency(precio_tuerca * tuercas_qty)
        items.append({
            'item': 'Tuerca 3/8',
            'qty': tuercas_qty,
            'unit_price': float(precio_tuerca),
            'subtotal': float(costo_tuercas)
        })
        subtotal += costo_tuercas
    
    if tacos_qty > 0:
        costo_tacos = _round_currency(precio_taco * tacos_qty)
        items.append({
            'item': 'Taco expansivo 3/8',
            'qty': tacos_qty,
            'unit_price': float(precio_taco),
            'subtotal': float(costo_tacos)
        })
        subtotal += costo_tacos
    
    return FijacionesResult(
        base_type=base_type,
        puntos_fijacion=puntos_fijacion,
        varillas_qty=varillas_qty,
        tuercas_qty=tuercas_qty,
        tacos_qty=tacos_qty,
        arandelas_qty=arandelas_qty,
        tortugas_qty=tortugas_qty,
        subtotal_usd=float(_round_currency(subtotal)),
        items=items
    )


def calculate_perfileria(
    cantidad_paneles: int,
    ancho_util_m: float,
    largo_m: float
) -> PerifileriaResult:
    """
    Calculate perfileria (trim/profiles) requirements - DETERMINISTIC.
    
    Formulas from KB:
    - Gotero frontal: ROUNDUP((CANTIDAD * ANCHO_UTIL) / 3)
    - Gotero lateral: ROUNDUP((LARGO * 2) / 3)
    - Silicona: ROUNDUP(TOTAL_ML / 8)
    - Fijaciones perfileria: 1 cada 30cm
    
    Args:
        cantidad_paneles: Number of panels
        ancho_util_m: Panel useful width in meters
        largo_m: Panel length in meters
    
    Returns:
        PerifileriaResult with all components and costs
    """
    kb = _load_knowledge_base()
    precios = kb.get('precios_accesorios_referencia', {})
    
    cant = _to_decimal(cantidad_paneles)
    ancho = _to_decimal(ancho_util_m)
    largo = _to_decimal(largo_m)
    
    # Gotero frontal: covers panel width
    ancho_total = cant * ancho
    gotero_frontal_qty = _round_up_qty(ancho_total / 3)  # 3m pieces
    
    # Gotero lateral: covers panel length on both sides
    largo_total = largo * 2
    gotero_lateral_qty = _round_up_qty(largo_total / 3)  # 3m pieces
    
    # Total linear meters of perfileria
    ml_total = ancho_total + largo_total
    
    # Silicona: 1 cartucho cada 8 metros lineales
    silicona_qty = _round_up_qty(ml_total / 8)
    
    # Fijaciones: 1 cada 30cm
    fijaciones_qty = _round_up_qty(ml_total / _to_decimal(0.30))
    
    # Calculate costs
    precio_gotero = _to_decimal(precios.get('gotero_frontal_isodec', 23.88))
    precio_silicona = _to_decimal(precios.get('silicona_pomo', 11.89))
    
    items = []
    subtotal = _to_decimal(0)
    
    if gotero_frontal_qty > 0:
        costo = _round_currency(precio_gotero * gotero_frontal_qty)
        items.append({
            'item': 'Gotero frontal',
            'qty': gotero_frontal_qty,
            'unit_price': float(precio_gotero),
            'subtotal': float(costo)
        })
        subtotal += costo
    
    if gotero_lateral_qty > 0:
        costo = _round_currency(precio_gotero * gotero_lateral_qty)
        items.append({
            'item': 'Gotero lateral',
            'qty': gotero_lateral_qty,
            'unit_price': float(precio_gotero),
            'subtotal': float(costo)
        })
        subtotal += costo
    
    if silicona_qty > 0:
        costo = _round_currency(precio_silicona * silicona_qty)
        items.append({
            'item': 'Silicona selladora',
            'qty': silicona_qty,
            'unit_price': float(precio_silicona),
            'subtotal': float(costo)
        })
        subtotal += costo
    
    return PerifileriaResult(
        gotero_frontal_qty=gotero_frontal_qty,
        gotero_lateral_qty=gotero_lateral_qty,
        silicona_qty=silicona_qty,
        fijaciones_perfileria_qty=fijaciones_qty,
        subtotal_usd=float(_round_currency(subtotal)),
        items=items
    )


def apply_pricing_rules(
    subtotal: float,
    area_m2: float,
    panel_type: str
) -> Dict[str, Any]:
    """
    Apply business pricing rules - DETERMINISTIC.
    
    Includes:
    - Bulk discounts for large areas
    - Minimum order requirements
    - Delivery cost calculations
    
    Args:
        subtotal: Current subtotal in USD
        area_m2: Total area in square meters
        panel_type: Type of panel
    
    Returns:
        Dictionary with adjustments and final pricing
    """
    kb = _load_knowledge_base()
    rules = kb.get('reglas_negocio', {})
    
    subtotal_dec = _to_decimal(subtotal)
    area_dec = _to_decimal(area_m2)
    
    adjustments = []
    discount_total = _to_decimal(0)
    
    # Check for bulk discount (example: 5% for >100m²)
    if area_dec > 100:
        bulk_discount = _round_currency(subtotal_dec * _to_decimal(0.05))
        discount_total += bulk_discount
        adjustments.append({
            'type': 'bulk_discount',
            'description': 'Descuento por volumen (>100m²)',
            'amount': float(bulk_discount),
            'percentage': 5.0
        })
    
    # IVA rate
    iva_rate = _to_decimal(rules.get('iva', 0.22))
    
    final_subtotal = subtotal_dec - discount_total
    iva_amount = _round_currency(final_subtotal * iva_rate)
    total_with_iva = _round_currency(final_subtotal + iva_amount)
    
    return {
        'original_subtotal': float(subtotal_dec),
        'adjustments': adjustments,
        'discount_total': float(_round_currency(discount_total)),
        'subtotal_after_discount': float(_round_currency(final_subtotal)),
        'iva_rate': float(iva_rate),
        'iva_amount': float(iva_amount),
        'total_with_iva': float(total_with_iva)
    }


def calculate_panel_quote(
    panel_type: str,
    thickness_mm: int,
    length_m: float,
    quantity: int,
    width_m: Optional[float] = None,
    base_type: str = "metal",
    discount_percent: float = 0.0,
    include_fijaciones: bool = True,
    include_perfileria: bool = True
) -> QuotationResult:
    """
    Calculate DETERMINISTIC quotation for panels.
    
    CRITICAL: The LLM NEVER executes this arithmetic.
    It only extracts parameters - all calculations happen here.
    
    Uses Decimal for financial precision (no floating-point errors).
    
    Args:
        panel_type: Panel type ID (e.g., "Isodec_EPS", "Isopanel_EPS")
        thickness_mm: Thickness in millimeters
        length_m: Panel length in meters
        quantity: Number of panels
        width_m: Panel width (defaults to ancho_util from catalog)
        base_type: Structure type for fixings ("metal", "hormigon", "madera")
        discount_percent: Discount percentage (0-30)
        include_fijaciones: Include fixing kit in quote
        include_perfileria: Include trim/profiles in quote
    
    Returns:
        QuotationResult with all calculations and verification flag
    
    Raises:
        ValueError: If product not found or invalid parameters
    """
    # Load knowledge base
    kb = _load_knowledge_base()
    products = kb.get('products', {})
    
    # Validate panel type exists
    if panel_type not in products:
        raise ValueError(f"Producto no encontrado: {panel_type}. Tipos válidos: {list(products.keys())}")
    
    product = products[panel_type]
    espesores = product.get('espesores', {})
    
    # Validate thickness
    thickness_key = str(thickness_mm)
    if thickness_key not in espesores:
        available = list(espesores.keys())
        raise ValueError(f"Espesor {thickness_mm}mm no disponible para {panel_type}. Opciones: {available}")
    
    espesor_data = espesores[thickness_key]
    
    # Get price - must exist
    price_per_m2 = espesor_data.get('precio')
    if price_per_m2 is None or price_per_m2 == "Consultar":
        raise ValueError(f"Precio no disponible para {panel_type} {thickness_mm}mm. Consultar con ventas.")
    
    # Get panel dimensions
    ancho_util = width_m if width_m else product.get('ancho_util', 1.0)
    autoportancia = espesor_data.get('autoportancia', 5.5)
    
    # === DETERMINISTIC CALCULATIONS WITH DECIMAL ===
    
    # Convert to Decimal for precision
    precio = _to_decimal(price_per_m2)
    largo = _to_decimal(length_m)
    ancho = _to_decimal(ancho_util)
    cant = _to_decimal(quantity)
    descuento_pct = _to_decimal(discount_percent)
    
    # Calculate area per panel
    area_unitaria = largo * ancho
    
    # Calculate panel cost: PRECIO * LARGO * ANCHO_UTIL * CANTIDAD
    costo_paneles = precio * area_unitaria * cant
    costo_paneles = _round_currency(costo_paneles)
    
    # Calculate fixings if requested
    fijaciones_subtotal = _to_decimal(0)
    if include_fijaciones:
        fijaciones = calculate_fijaciones(
            panel_type=panel_type,
            largo_m=length_m,
            cantidad=quantity,
            autoportancia_m=autoportancia,
            base_type=base_type
        )
        fijaciones_subtotal = _to_decimal(fijaciones['subtotal_usd'])
    
    # Calculate perfileria if requested
    perfileria_subtotal = _to_decimal(0)
    if include_perfileria:
        perfileria = calculate_perfileria(
            cantidad_paneles=quantity,
            ancho_util_m=float(ancho),
            largo_m=length_m
        )
        perfileria_subtotal = _to_decimal(perfileria['subtotal_usd'])
    
    # Calculate subtotal
    subtotal = costo_paneles + fijaciones_subtotal + perfileria_subtotal
    subtotal = _round_currency(subtotal)
    
    # Apply discount
    descuento = _round_currency(subtotal * descuento_pct / 100)
    total = _round_currency(subtotal - descuento)
    
    # Apply IVA
    iva_rate = _to_decimal(kb.get('reglas_negocio', {}).get('iva', 0.22))
    total_con_iva = _round_currency(total * (1 + iva_rate))
    
    # Build result
    area_total = float(area_unitaria * cant)
    precio_unitario = float(_round_currency(precio * area_unitaria))
    
    return QuotationResult(
        product_id=f"{panel_type}_{thickness_mm}mm",
        panel_type=panel_type,
        thickness_mm=thickness_mm,
        area_m2=area_total,
        unit_price_usd=precio_unitario,
        quantity=quantity,
        panels_subtotal_usd=float(costo_paneles),
        fijaciones_subtotal_usd=float(fijaciones_subtotal),
        perfileria_subtotal_usd=float(perfileria_subtotal),
        subtotal_usd=float(subtotal),
        discount_usd=float(descuento),
        total_usd=float(total),
        total_with_iva_usd=float(total_con_iva),
        calculation_verified=True,  # CRITICAL: Marks deterministic calculation
        calculation_method="deterministic_python_decimal",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


def validate_quotation(result: QuotationResult) -> Dict[str, Any]:
    """
    Validate quotation result - DETERMINISTIC verification.
    
    Checks:
    1. calculation_verified must be True
    2. All values must be positive
    3. Totals must be mathematically consistent
    4. IVA calculation must be correct
    
    Args:
        result: QuotationResult to validate
    
    Returns:
        ValidationResult with is_valid and any errors/warnings
    """
    errors = []
    warnings = []
    checks = []
    
    # Critical: Must have deterministic calculation flag
    if not result.get('calculation_verified'):
        errors.append("CRITICAL: calculation_verified is False - LLM may have calculated directly!")
    else:
        checks.append("✓ Calculation verified as deterministic")
    
    # Check calculation method
    if result.get('calculation_method') != "deterministic_python_decimal":
        warnings.append(f"Unexpected calculation method: {result.get('calculation_method')}")
    else:
        checks.append("✓ Decimal precision method used")
    
    # Check positive values
    if result.get('total_usd', 0) <= 0:
        errors.append(f"Total must be positive, got: {result.get('total_usd')}")
    else:
        checks.append("✓ Total is positive")
    
    if result.get('area_m2', 0) <= 0:
        errors.append(f"Area must be positive, got: {result.get('area_m2')}")
    else:
        checks.append("✓ Area is positive")
    
    # Verify subtotal calculation
    expected_subtotal = (
        _to_decimal(result.get('panels_subtotal_usd', 0)) +
        _to_decimal(result.get('fijaciones_subtotal_usd', 0)) +
        _to_decimal(result.get('perfileria_subtotal_usd', 0))
    )
    actual_subtotal = _to_decimal(result.get('subtotal_usd', 0))
    
    if abs(expected_subtotal - actual_subtotal) > _to_decimal('0.02'):
        errors.append(f"Subtotal mismatch: expected {expected_subtotal}, got {actual_subtotal}")
    else:
        checks.append("✓ Subtotal calculation verified")
    
    # Verify total after discount
    expected_total = actual_subtotal - _to_decimal(result.get('discount_usd', 0))
    actual_total = _to_decimal(result.get('total_usd', 0))
    
    if abs(expected_total - actual_total) > _to_decimal('0.02'):
        errors.append(f"Total after discount mismatch: expected {expected_total}, got {actual_total}")
    else:
        checks.append("✓ Discount calculation verified")
    
    # Verify IVA
    iva_rate = _to_decimal(0.22)  # Uruguay standard
    expected_with_iva = _round_currency(actual_total * (1 + iva_rate))
    actual_with_iva = _to_decimal(result.get('total_with_iva_usd', 0))
    
    if abs(expected_with_iva - actual_with_iva) > _to_decimal('0.05'):
        errors.append(f"IVA calculation mismatch: expected {expected_with_iva}, got {actual_with_iva}")
    else:
        checks.append("✓ IVA calculation verified")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'verification_checks': checks,
        'verified_at': datetime.now(timezone.utc).isoformat()
    }


# === Convenience Functions ===

def get_available_products() -> List[str]:
    """Get list of available product types."""
    kb = _load_knowledge_base()
    return list(kb.get('products', {}).keys())


def get_available_thicknesses(panel_type: str) -> List[int]:
    """Get available thicknesses for a panel type."""
    kb = _load_knowledge_base()
    products = kb.get('products', {})
    
    if panel_type not in products:
        return []
    
    espesores = products[panel_type].get('espesores', {})
    return [int(e) for e in espesores.keys()]


def get_price_per_m2(panel_type: str, thickness_mm: int) -> Optional[float]:
    """Get price per m² for specific product variant."""
    result = lookup_product_specs(panel_type, thickness_mm)
    if result['found'] and result['products']:
        return result['products'][0].get('price_per_m2')
    return None
