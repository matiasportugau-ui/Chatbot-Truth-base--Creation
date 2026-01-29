"""
Quotation Calculator - Cálculos Deterministas
==============================================

Este módulo implementa TODOS los cálculos de cotización de forma determinista.
El LLM NUNCA ejecuta esta matemática—solo extrae parámetros de lenguaje natural.

Principios:
1. Usar Decimal para toda aritmética financiera (no floats)
2. Cargar precios desde JSON KB, nunca hardcodear
3. Incluir 'calculation_verified: True' en todos los outputs
4. Validar rangos de entrada antes de calcular
"""

import json
import math
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
from pathlib import Path
from typing import TypedDict, Optional, List, Literal
from dataclasses import dataclass

# Ruta a la Knowledge Base
KB_PATH = Path(__file__).parent.parent / "kb" / "panelin_truth_bmcuruguay.json"


class QuotationResult(TypedDict):
    """Resultado de cotización de paneles"""
    product_id: str
    product_name: str
    panel_type: str
    thickness_mm: int
    length_m: float
    width_m: float
    area_m2: float
    unit_price_usd: float
    quantity: int
    subtotal_usd: float
    discount_percent: float
    discount_amount_usd: float
    total_usd: float
    price_type: str  # "empresa" o "particular"
    calculation_verified: bool
    notes: List[str]


class AccessoriesResult(TypedDict):
    """Resultado de cotización de accesorios"""
    items: List[dict]
    subtotal_usd: float
    total_usd: float
    calculation_verified: bool


class FixationResult(TypedDict):
    """Resultado de cálculo de puntos de fijación"""
    panel_count: int
    support_count: int
    fixation_points: int
    rods_needed: int
    metal_nuts: int
    concrete_nuts: int
    concrete_anchors: int
    calculation_verified: bool


class ProfilesResult(TypedDict):
    """Resultado de cotización de perfiles"""
    frontal_drip_count: int
    lateral_drip_count: int
    ridge_count: int
    profiles_total_meters: float
    rivets_needed: int
    silicone_tubes: int
    subtotal_usd: float
    calculation_verified: bool


def _load_kb() -> dict:
    """Carga la Knowledge Base desde JSON"""
    if not KB_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge Base no encontrada: {KB_PATH}. "
            "Ejecute el script de sincronización primero."
        )
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _to_decimal(value: float | int | str) -> Decimal:
    """Convierte un valor a Decimal de forma segura"""
    return Decimal(str(value))


def _round_currency(value: Decimal) -> Decimal:
    """Redondea a 2 decimales para moneda"""
    return value.quantize(Decimal("0.01"), ROUND_HALF_UP)


def _round_up(value: float) -> int:
    """Redondea hacia arriba (ROUNDUP de Excel)"""
    return math.ceil(value)


def calculate_panel_quote(
    panel_type: Literal["Isopanel", "Isodec", "Isoroof", "Isowall", "Isofrig"],
    thickness_mm: int,
    length_m: float,
    width_m: float,
    quantity: int,
    discount_percent: float = 0.0,
    price_type: Literal["empresa", "particular", "web"] = "empresa",
    insulation_type: Literal["EPS", "PIR"] = "EPS",
) -> QuotationResult:
    """
    Cálculo DETERMINISTA de cotización de paneles.
    El LLM NUNCA ejecuta esta matemática—solo extrae parámetros.
    
    Args:
        panel_type: Tipo de panel (Isopanel, Isodec, Isoroof, Isowall, Isofrig)
        thickness_mm: Espesor en milímetros
        length_m: Largo del panel en metros
        width_m: Ancho del panel en metros (típicamente el ancho útil)
        quantity: Cantidad de paneles
        discount_percent: Porcentaje de descuento (0-30)
        price_type: Tipo de precio (empresa, particular, web)
        insulation_type: Tipo de aislación (EPS o PIR)
    
    Returns:
        QuotationResult con todos los detalles del cálculo
    
    Raises:
        ValueError: Si los parámetros están fuera de rango
    """
    notes: List[str] = []
    
    # Validación de rangos
    if thickness_mm <= 0:
        raise ValueError(f"Espesor debe ser positivo: {thickness_mm}")
    if length_m < 0.5 or length_m > 14.0:
        raise ValueError(f"Largo debe estar entre 0.5 y 14.0 metros: {length_m}")
    if width_m <= 0 or width_m > 2.0:
        raise ValueError(f"Ancho debe estar entre 0 y 2.0 metros: {width_m}")
    if quantity < 1:
        raise ValueError(f"Cantidad debe ser al menos 1: {quantity}")
    if discount_percent < 0 or discount_percent > 30:
        raise ValueError(f"Descuento debe estar entre 0 y 30%: {discount_percent}")
    
    # Cargar KB y buscar producto
    kb = _load_kb()
    products = kb.get("products", {})
    
    # Construir clave de búsqueda
    product_key = f"{panel_type}_{thickness_mm}mm_{insulation_type}"
    product_key_alt = f"{panel_type}_{thickness_mm}mm"
    
    # Buscar producto en KB
    product = None
    matched_key = None
    
    for key, prod in products.items():
        if key == product_key or key == product_key_alt:
            product = prod
            matched_key = key
            break
        # Búsqueda flexible por familia y espesor
        if (prod.get("family", "").upper().startswith(panel_type.upper()) and 
            prod.get("thickness_mm") == thickness_mm):
            product = prod
            matched_key = key
            break
    
    if not product:
        raise ValueError(
            f"Producto no encontrado: {panel_type} {thickness_mm}mm {insulation_type}. "
            f"Verifique catálogo disponible."
        )
    
    # Obtener precio según tipo
    if price_type == "empresa":
        price_per_m2 = _to_decimal(product.get("sale_price_usd_ex_iva", product.get("price_usd", 0)))
    elif price_type == "particular":
        price_per_m2 = _to_decimal(product.get("price_usd", 0))
    else:  # web
        price_per_m2 = _to_decimal(product.get("web_price_usd", product.get("price_usd", 0)))
    
    if price_per_m2 <= 0:
        raise ValueError(f"Precio no válido para {matched_key}: {price_per_m2}")
    
    # Cálculos con precisión Decimal
    area = _to_decimal(length_m) * _to_decimal(width_m)
    unit_price = _round_currency(area * price_per_m2)
    subtotal = _round_currency(unit_price * quantity)
    discount_amount = _round_currency(subtotal * _to_decimal(discount_percent) / 100)
    total = subtotal - discount_amount
    
    # Notas adicionales
    min_order_m2 = product.get("min_order_m2", 10)
    total_area = float(area) * quantity
    if total_area < min_order_m2:
        notes.append(f"Pedido mínimo: {min_order_m2} m². Área solicitada: {total_area:.2f} m²")
    
    if product.get("production_type") == "on_demand":
        notes.append("Producción bajo pedido. Consultar plazos de entrega.")
    
    return QuotationResult(
        product_id=matched_key or product_key,
        product_name=product.get("name", panel_type),
        panel_type=panel_type,
        thickness_mm=thickness_mm,
        length_m=length_m,
        width_m=width_m,
        area_m2=float(area),
        unit_price_usd=float(unit_price),
        quantity=quantity,
        subtotal_usd=float(subtotal),
        discount_percent=discount_percent,
        discount_amount_usd=float(discount_amount),
        total_usd=float(total),
        price_type=price_type,
        calculation_verified=True,
        notes=notes,
    )


def calculate_fixation_points(
    panel_count: int,
    panel_length_m: float,
    autoportancia_m: float = 5.5,
    structure_type: Literal["metal", "concrete"] = "metal",
) -> FixationResult:
    """
    Calcula puntos de fijación y materiales necesarios.
    
    Fórmulas:
    - Apoyos: ROUNDUP((LARGO / AUTOPORTANCIA) + 1)
    - Puntos: ROUNDUP(((CANTIDAD * APOYOS) * 2) + (LARGO * 2 / 2.5))
    - Varillas: ROUNDUP(PUNTOS / 4)
    - Tuercas metal: PUNTOS * 2
    - Tuercas hormigón: PUNTOS * 1
    - Tacos hormigón: PUNTOS * 1
    """
    if panel_count < 1:
        raise ValueError("Cantidad de paneles debe ser al menos 1")
    if panel_length_m <= 0:
        raise ValueError("Largo de panel debe ser positivo")
    if autoportancia_m <= 0:
        raise ValueError("Autoportancia debe ser positiva")
    
    # Cálculo de apoyos
    support_count = _round_up((panel_length_m / autoportancia_m) + 1)
    
    # Cálculo de puntos de fijación
    fixation_points = _round_up(
        ((panel_count * support_count) * 2) + (panel_length_m * 2 / 2.5)
    )
    
    # Materiales derivados
    rods_needed = _round_up(fixation_points / 4)
    
    if structure_type == "metal":
        metal_nuts = fixation_points * 2
        concrete_nuts = 0
        concrete_anchors = 0
    else:  # concrete
        metal_nuts = 0
        concrete_nuts = fixation_points
        concrete_anchors = fixation_points
    
    return FixationResult(
        panel_count=panel_count,
        support_count=support_count,
        fixation_points=fixation_points,
        rods_needed=rods_needed,
        metal_nuts=metal_nuts,
        concrete_nuts=concrete_nuts,
        concrete_anchors=concrete_anchors,
        calculation_verified=True,
    )


def calculate_profiles_quote(
    panel_count: int,
    panel_length_m: float,
    panel_width_m: float,
    thickness_mm: int,
    include_ridge: bool = True,
    price_type: Literal["empresa", "particular", "web"] = "empresa",
) -> ProfilesResult:
    """
    Calcula perfiles necesarios y su cotización.
    
    Fórmulas:
    - Gotero frontal: ROUNDUP((CANTIDAD * ANCHO_UTIL) / 3)
    - Gotero lateral: ROUNDUP((LARGO * 2) / 3)
    - Remaches: ROUNDUP(TOTAL_PERFILES * 20)
    - Silicona: ROUNDUP(TOTAL_ML / 8)
    """
    if panel_count < 1:
        raise ValueError("Cantidad de paneles debe ser al menos 1")
    
    kb = _load_kb()
    products = kb.get("products", {})
    
    # Cálculo de cantidades
    frontal_drip_count = _round_up((panel_count * panel_width_m) / 3)
    lateral_drip_count = _round_up((panel_length_m * 2) / 3)
    ridge_count = frontal_drip_count if include_ridge else 0
    
    total_profiles = frontal_drip_count + lateral_drip_count + ridge_count
    profiles_total_meters = total_profiles * 3.0  # Perfiles de 3m
    
    rivets_needed = _round_up(total_profiles * 20)
    silicone_tubes = _round_up(profiles_total_meters / 8)
    
    # Buscar precios de perfiles
    subtotal = Decimal("0")
    
    # Gotero frontal
    gf_key = f"GFS{thickness_mm}"
    if gf_key in products:
        gf_price = _to_decimal(products[gf_key].get("sale_price_usd_ex_iva", 20))
        subtotal += gf_price * frontal_drip_count
    
    # Gotero lateral
    gl_key = f"GL{thickness_mm}"
    if gl_key in products:
        gl_price = _to_decimal(products[gl_key].get("sale_price_usd_ex_iva", 25))
        subtotal += gl_price * lateral_drip_count
    
    # Cumbrera
    if include_ridge:
        ridge_price = _to_decimal(products.get("CUMROOF3M", {}).get("sale_price_usd_ex_iva", 35))
        subtotal += ridge_price * ridge_count
    
    return ProfilesResult(
        frontal_drip_count=frontal_drip_count,
        lateral_drip_count=lateral_drip_count,
        ridge_count=ridge_count,
        profiles_total_meters=profiles_total_meters,
        rivets_needed=rivets_needed,
        silicone_tubes=silicone_tubes,
        subtotal_usd=float(_round_currency(subtotal)),
        calculation_verified=True,
    )


def calculate_accessories_quote(
    accessories: List[dict],
    price_type: Literal["empresa", "particular", "web"] = "empresa",
) -> AccessoriesResult:
    """
    Calcula cotización de accesorios.
    
    Args:
        accessories: Lista de dicts con {sku, quantity}
        price_type: Tipo de precio
    
    Returns:
        AccessoriesResult con desglose y total
    """
    kb = _load_kb()
    products = kb.get("products", {})
    
    items = []
    subtotal = Decimal("0")
    
    for acc in accessories:
        sku = acc.get("sku", "")
        qty = acc.get("quantity", 1)
        
        if sku not in products:
            items.append({
                "sku": sku,
                "name": "Producto no encontrado",
                "quantity": qty,
                "unit_price_usd": 0,
                "line_total_usd": 0,
                "error": f"SKU {sku} no encontrado en catálogo",
            })
            continue
        
        product = products[sku]
        
        if price_type == "empresa":
            price = _to_decimal(product.get("sale_price_usd_ex_iva", product.get("price_usd", 0)))
        elif price_type == "particular":
            price = _to_decimal(product.get("price_usd", 0))
        else:
            price = _to_decimal(product.get("web_price_usd", product.get("price_usd", 0)))
        
        line_total = _round_currency(price * qty)
        subtotal += line_total
        
        items.append({
            "sku": sku,
            "name": product.get("name", sku),
            "quantity": qty,
            "unit_price_usd": float(price),
            "line_total_usd": float(line_total),
        })
    
    return AccessoriesResult(
        items=items,
        subtotal_usd=float(_round_currency(subtotal)),
        total_usd=float(_round_currency(subtotal)),
        calculation_verified=True,
    )


def calculate_complete_quotation(
    panel_type: str,
    thickness_mm: int,
    total_width_m: float,
    total_length_m: float,
    include_accessories: bool = True,
    include_fixation: bool = True,
    structure_type: Literal["metal", "concrete"] = "metal",
    discount_percent: float = 0.0,
    price_type: Literal["empresa", "particular", "web"] = "empresa",
    insulation_type: Literal["EPS", "PIR"] = "EPS",
) -> dict:
    """
    Genera cotización completa incluyendo paneles, perfiles y fijaciones.
    
    Esta es la función principal que combina todos los cálculos.
    """
    kb = _load_kb()
    products = kb.get("products", {})
    
    # Determinar ancho útil del panel
    product_info = None
    for key, prod in products.items():
        if (prod.get("family", "").upper().startswith(panel_type.upper()) and 
            prod.get("thickness_mm") == thickness_mm):
            product_info = prod
            break
    
    useful_width = product_info.get("useful_width_m", 1.12) if product_info else 1.12
    
    # Calcular cantidad de paneles
    panel_count = _round_up(total_width_m / useful_width)
    
    # Cotización de paneles
    panel_quote = calculate_panel_quote(
        panel_type=panel_type,
        thickness_mm=thickness_mm,
        length_m=total_length_m,
        width_m=useful_width,
        quantity=panel_count,
        discount_percent=discount_percent,
        price_type=price_type,
        insulation_type=insulation_type,
    )
    
    result = {
        "panels": panel_quote,
        "panel_count": panel_count,
        "total_area_m2": panel_quote["area_m2"] * panel_count,
        "panels_subtotal_usd": panel_quote["total_usd"],
    }
    
    # Perfiles y accesorios
    if include_accessories:
        profiles = calculate_profiles_quote(
            panel_count=panel_count,
            panel_length_m=total_length_m,
            panel_width_m=useful_width,
            thickness_mm=thickness_mm,
            include_ridge=True,
            price_type=price_type,
        )
        result["profiles"] = profiles
        result["profiles_subtotal_usd"] = profiles["subtotal_usd"]
    
    # Fijaciones
    if include_fixation:
        fixation = calculate_fixation_points(
            panel_count=panel_count,
            panel_length_m=total_length_m,
            structure_type=structure_type,
        )
        result["fixation"] = fixation
    
    # Totales
    grand_total = Decimal(str(panel_quote["total_usd"]))
    if include_accessories:
        grand_total += Decimal(str(profiles["subtotal_usd"]))
    
    result["grand_total_usd"] = float(_round_currency(grand_total))
    result["calculation_verified"] = True
    result["price_type"] = price_type
    
    return result
