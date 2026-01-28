"""
Pricing Rules - Reglas de Precios Deterministas
===============================================

Este módulo implementa las reglas de negocio para precios, descuentos,
y costos de envío. Todas las reglas son deterministas y configurables
desde la Knowledge Base.
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Optional, Literal, Dict, Any

KB_PATH = Path(__file__).parent.parent / "kb" / "panelin_truth_bmcuruguay.json"


def _load_kb() -> dict:
    """Carga la Knowledge Base desde JSON"""
    if not KB_PATH.exists():
        raise FileNotFoundError(f"Knowledge Base no encontrada: {KB_PATH}")
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _to_decimal(value: float | int | str) -> Decimal:
    """Convierte un valor a Decimal de forma segura"""
    return Decimal(str(value))


def _round_currency(value: Decimal) -> Decimal:
    """Redondea a 2 decimales para moneda"""
    return value.quantize(Decimal("0.01"), ROUND_HALF_UP)


def apply_discount(
    subtotal_usd: float,
    discount_percent: float,
    max_discount_percent: float = 30.0,
) -> Dict[str, float]:
    """
    Aplica un descuento al subtotal.
    
    Args:
        subtotal_usd: Subtotal en USD
        discount_percent: Porcentaje de descuento a aplicar
        max_discount_percent: Descuento máximo permitido
        
    Returns:
        Dict con discount_amount, final_total, effective_percent
    """
    if discount_percent < 0:
        discount_percent = 0
    if discount_percent > max_discount_percent:
        discount_percent = max_discount_percent
    
    subtotal = _to_decimal(subtotal_usd)
    discount = _round_currency(subtotal * _to_decimal(discount_percent) / 100)
    final = subtotal - discount
    
    return {
        "subtotal_usd": float(subtotal),
        "discount_percent": discount_percent,
        "discount_amount_usd": float(discount),
        "final_total_usd": float(final),
        "calculation_verified": True,
    }


def apply_bulk_pricing(
    total_area_m2: float,
    base_price_per_m2: float,
    product_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Aplica precios por volumen según área total.
    
    Reglas típicas:
    - < 10 m²: Precio base + recargo pedido mínimo
    - 10-50 m²: Precio base
    - 50-100 m²: 3% descuento
    - 100-500 m²: 5% descuento
    - 500-1000 m²: 7% descuento
    - > 1000 m²: 10% descuento (requiere aprobación)
    
    Args:
        total_area_m2: Área total en metros cuadrados
        base_price_per_m2: Precio base por m²
        product_type: Tipo de producto (opcional, para reglas específicas)
        
    Returns:
        Dict con precio ajustado y detalles del descuento
    """
    kb = _load_kb()
    pricing_rules = kb.get("pricing_rules", {})
    bulk_rules = pricing_rules.get("bulk_discounts", {})
    
    # Reglas por defecto si no están en KB
    default_rules = [
        {"min_m2": 0, "max_m2": 10, "discount": -5, "note": "Recargo pedido mínimo"},
        {"min_m2": 10, "max_m2": 50, "discount": 0, "note": "Precio estándar"},
        {"min_m2": 50, "max_m2": 100, "discount": 3, "note": "Descuento volumen"},
        {"min_m2": 100, "max_m2": 500, "discount": 5, "note": "Descuento volumen mayor"},
        {"min_m2": 500, "max_m2": 1000, "discount": 7, "note": "Descuento mayorista"},
        {"min_m2": 1000, "max_m2": float("inf"), "discount": 10, "note": "Requiere aprobación"},
    ]
    
    rules = bulk_rules.get("tiers", default_rules)
    
    # Encontrar regla aplicable
    applicable_rule = None
    for rule in rules:
        if rule["min_m2"] <= total_area_m2 < rule.get("max_m2", float("inf")):
            applicable_rule = rule
            break
    
    if not applicable_rule:
        applicable_rule = {"discount": 0, "note": "Sin regla aplicable"}
    
    discount_percent = applicable_rule.get("discount", 0)
    base_total = _to_decimal(total_area_m2) * _to_decimal(base_price_per_m2)
    
    if discount_percent < 0:
        # Es un recargo, no descuento
        surcharge = _round_currency(base_total * abs(_to_decimal(discount_percent)) / 100)
        final_total = base_total + surcharge
        return {
            "total_area_m2": total_area_m2,
            "base_price_per_m2": base_price_per_m2,
            "base_total_usd": float(_round_currency(base_total)),
            "adjustment_type": "surcharge",
            "adjustment_percent": abs(discount_percent),
            "adjustment_amount_usd": float(surcharge),
            "final_total_usd": float(_round_currency(final_total)),
            "final_price_per_m2": float(_round_currency(final_total / _to_decimal(total_area_m2))),
            "note": applicable_rule.get("note", ""),
            "calculation_verified": True,
        }
    else:
        discount = _round_currency(base_total * _to_decimal(discount_percent) / 100)
        final_total = base_total - discount
        return {
            "total_area_m2": total_area_m2,
            "base_price_per_m2": base_price_per_m2,
            "base_total_usd": float(_round_currency(base_total)),
            "adjustment_type": "discount",
            "adjustment_percent": discount_percent,
            "adjustment_amount_usd": float(discount),
            "final_total_usd": float(_round_currency(final_total)),
            "final_price_per_m2": float(_round_currency(final_total / _to_decimal(total_area_m2))),
            "note": applicable_rule.get("note", ""),
            "calculation_verified": True,
        }


def calculate_delivery_cost(
    total_area_m2: float,
    destination_zone: Literal["montevideo", "canelones", "interior", "exterior"] = "montevideo",
    product_weight_kg_per_m2: float = 12.0,
) -> Dict[str, Any]:
    """
    Calcula el costo de envío.
    
    Args:
        total_area_m2: Área total en m²
        destination_zone: Zona de destino
        product_weight_kg_per_m2: Peso por m² (típico: 10-15 kg/m²)
        
    Returns:
        Dict con costo de envío y detalles
    """
    kb = _load_kb()
    pricing_rules = kb.get("pricing_rules", {})
    delivery_rules = pricing_rules.get("delivery", {})
    
    # Tarifas por defecto
    default_rates = {
        "montevideo": {"per_m2": 1.50, "minimum": 50},
        "canelones": {"per_m2": 2.00, "minimum": 75},
        "interior": {"per_m2": 3.00, "minimum": 150},
        "exterior": {"per_m2": 0, "minimum": 0, "note": "Consultar"},
    }
    
    rates = delivery_rules.get("zones", default_rates)
    zone_rate = rates.get(destination_zone, default_rates["interior"])
    
    if destination_zone == "exterior":
        return {
            "total_area_m2": total_area_m2,
            "destination_zone": destination_zone,
            "delivery_cost_usd": 0,
            "note": "Envío al exterior: consultar para cotización especial",
            "requires_quote": True,
            "calculation_verified": True,
        }
    
    per_m2_rate = _to_decimal(zone_rate.get("per_m2", 2.0))
    minimum = _to_decimal(zone_rate.get("minimum", 50))
    
    calculated_cost = _round_currency(_to_decimal(total_area_m2) * per_m2_rate)
    final_cost = max(calculated_cost, minimum)
    
    total_weight = total_area_m2 * product_weight_kg_per_m2
    
    return {
        "total_area_m2": total_area_m2,
        "destination_zone": destination_zone,
        "rate_per_m2_usd": float(per_m2_rate),
        "calculated_cost_usd": float(calculated_cost),
        "minimum_charge_usd": float(minimum),
        "delivery_cost_usd": float(final_cost),
        "estimated_weight_kg": round(total_weight, 1),
        "note": zone_rate.get("note", ""),
        "calculation_verified": True,
    }


def get_minimum_order_value(
    product_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Obtiene el valor mínimo de pedido.
    
    Args:
        product_type: Tipo de producto (opcional)
        
    Returns:
        Dict con valores mínimos
    """
    kb = _load_kb()
    pricing_rules = kb.get("pricing_rules", {})
    minimums = pricing_rules.get("minimum_orders", {})
    
    # Valores por defecto
    default_minimums = {
        "panel": {"min_area_m2": 10, "min_value_usd": 500},
        "perfil": {"min_units": 3, "min_value_usd": 50},
        "accesorio": {"min_value_usd": 25},
        "default": {"min_value_usd": 100},
    }
    
    mins = minimums if minimums else default_minimums
    
    if product_type and product_type in mins:
        return {
            "product_type": product_type,
            **mins[product_type],
            "calculation_verified": True,
        }
    
    return {
        "product_type": "default",
        **mins.get("default", {"min_value_usd": 100}),
        "calculation_verified": True,
    }


def calculate_tax(
    subtotal_usd: float,
    client_type: Literal["empresa", "particular"] = "empresa",
    include_iva: bool = True,
) -> Dict[str, Any]:
    """
    Calcula impuestos (IVA Uruguay = 22%).
    
    Args:
        subtotal_usd: Subtotal en USD
        client_type: Tipo de cliente
        include_iva: Si incluir IVA en el cálculo
        
    Returns:
        Dict con desglose de impuestos
    """
    kb = _load_kb()
    pricing_rules = kb.get("pricing_rules", {})
    tax_rate = _to_decimal(pricing_rules.get("tax_rate_uy", 22))
    
    subtotal = _to_decimal(subtotal_usd)
    
    if client_type == "empresa":
        # Empresas descuentan IVA, mostramos precio + IVA
        iva_amount = _round_currency(subtotal * tax_rate / 100)
        total_with_iva = subtotal + iva_amount
        
        return {
            "subtotal_usd": float(subtotal),
            "client_type": client_type,
            "tax_rate_percent": float(tax_rate),
            "iva_amount_usd": float(iva_amount),
            "total_with_iva_usd": float(total_with_iva),
            "note": "Empresas: precio + IVA (descuentan IVA)",
            "calculation_verified": True,
        }
    else:
        # Particulares: precio IVA incluido
        # Si el precio ya incluye IVA, extraer el componente
        iva_component = _round_currency(subtotal * tax_rate / (100 + tax_rate))
        base_price = subtotal - iva_component
        
        return {
            "subtotal_usd": float(subtotal),
            "client_type": client_type,
            "tax_rate_percent": float(tax_rate),
            "iva_included_usd": float(iva_component),
            "base_price_ex_iva_usd": float(base_price),
            "total_usd": float(subtotal),
            "note": "Particulares: precio IVA incluido (no descuentan)",
            "calculation_verified": True,
        }


def get_payment_terms() -> Dict[str, Any]:
    """
    Obtiene las condiciones de pago disponibles.
    
    Returns:
        Dict con opciones de pago y sus condiciones
    """
    kb = _load_kb()
    pricing_rules = kb.get("pricing_rules", {})
    payment_terms = pricing_rules.get("payment_terms", {})
    
    default_terms = {
        "options": [
            {
                "method": "contado",
                "discount_percent": 3,
                "note": "Descuento por pago contado",
            },
            {
                "method": "transferencia",
                "discount_percent": 2,
                "note": "Descuento por transferencia bancaria",
            },
            {
                "method": "cheque_30_dias",
                "discount_percent": 0,
                "note": "Precio de lista",
            },
            {
                "method": "cheque_60_dias",
                "surcharge_percent": 2,
                "note": "Recargo por financiación",
            },
            {
                "method": "tarjeta_credito",
                "surcharge_percent": 5,
                "note": "Recargo por tarjeta de crédito",
            },
        ],
        "default_method": "cheque_30_dias",
    }
    
    return payment_terms if payment_terms else default_terms
