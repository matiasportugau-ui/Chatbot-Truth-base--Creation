from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Literal, NotRequired, TypedDict, Any


DEFAULT_TRUTH_KB_PATH = Path("panelin_truth_bmcuruguay.json")


class QuotationResult(TypedDict):
    product_id: str
    panel_type: str
    thickness_mm: int
    area_m2: float
    unit_price_usd: float
    quantity: int
    subtotal_usd: float
    discount_usd: float
    total_usd: float
    currency: str
    calculation_verified: bool
    warnings: NotRequired[list[str]]


class ProductSpec(TypedDict):
    shopify_id: str | None
    name: str
    price_per_m2: float
    currency: str
    available_thicknesses: list[int]
    last_updated: str | None


class TruthKB(TypedDict):
    version: str
    last_sync: str
    shopify_store: str | None
    products: dict[str, ProductSpec]
    pricing_rules: dict[str, Any]


def _d(value: float | int | str | Decimal) -> Decimal:
    """
    Convert user-provided scalar to Decimal safely.

    Notes:
    - We prefer Decimal(str(x)) to avoid float binary artifacts.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, str)):
        return Decimal(str(value))
    return Decimal(str(value))


def _money(value: Decimal) -> Decimal:
    """Round to cents using banker-safe HALF_UP."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load_truth_kb(path: str | Path = DEFAULT_TRUTH_KB_PATH) -> TruthKB:
    kb_path = Path(path)
    with kb_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_product_id(panel_type: str, thickness_mm: int) -> str:
    return f"{panel_type}_{thickness_mm}mm"


def lookup_product_specs(
    panel_type: Literal["Isopanel", "Isodec", "Isoroof"],
    thickness_mm: int,
    *,
    kb_path: str | Path = DEFAULT_TRUTH_KB_PATH,
) -> ProductSpec:
    kb = load_truth_kb(kb_path)
    product_id = build_product_id(panel_type, thickness_mm)
    if product_id not in kb["products"]:
        raise ValueError(f"Producto no encontrado: {product_id}")
    return kb["products"][product_id]


def calculate_panel_quote(
    panel_type: Literal["Isopanel", "Isodec", "Isoroof"],
    thickness_mm: int,
    length_m: float,
    width_m: float,
    quantity: int,
    discount_percent: float = 0.0,
    *,
    kb_path: str | Path = DEFAULT_TRUTH_KB_PATH,
) -> QuotationResult:
    """
    Cálculo DETERMINISTA de cotización.

    Critical rule:
    - The LLM NEVER executes this math. It only extracts parameters.
    """
    if quantity < 1:
        raise ValueError("quantity debe ser >= 1")
    if length_m <= 0 or width_m <= 0:
        raise ValueError("length_m y width_m deben ser > 0")
    if discount_percent < 0 or discount_percent > 30:
        raise ValueError("discount_percent fuera de rango (0-30)")

    product_id = build_product_id(panel_type, thickness_mm)
    spec = lookup_product_specs(panel_type, thickness_mm, kb_path=kb_path)

    price_per_m2 = _d(spec["price_per_m2"])

    # Geometry (m²)
    area = _d(length_m) * _d(width_m)

    # Pricing
    unit_price = _money(area * price_per_m2)
    subtotal = _money(unit_price * _d(quantity))
    discount = _money(subtotal * _d(discount_percent) / Decimal("100"))
    total = _money(subtotal - discount)

    result: QuotationResult = {
        "product_id": product_id,
        "panel_type": panel_type,
        "thickness_mm": thickness_mm,
        "area_m2": float(area),
        "unit_price_usd": float(unit_price),
        "quantity": int(quantity),
        "subtotal_usd": float(subtotal),
        "discount_usd": float(discount),
        "total_usd": float(total),
        "currency": spec.get("currency", "USD"),
        "calculation_verified": True,
    }

    validate_quotation(result)
    return result


def validate_quotation(result: QuotationResult) -> bool:
    """
    Hard validation for deterministic outputs.

    If this fails, it indicates either:
    - input extraction produced invalid values, or
    - arithmetic was not executed deterministically.
    """
    if result.get("calculation_verified") is not True:
        raise AssertionError("calculation_verified debe ser True")

    for key in ("area_m2", "unit_price_usd", "subtotal_usd", "discount_usd", "total_usd"):
        if result[key] < 0:
            raise AssertionError(f"{key} no puede ser negativo")

    # Cross-check totals deterministically
    subtotal = _d(result["subtotal_usd"])
    discount = _d(result["discount_usd"])
    total = _d(result["total_usd"])
    if _money(subtotal - discount) != _money(total):
        raise AssertionError("total_usd no coincide con subtotal_usd - discount_usd")

    if result["quantity"] < 1:
        raise AssertionError("quantity inválida")
    if result["area_m2"] <= 0:
        raise AssertionError("area_m2 inválida")

    return True

