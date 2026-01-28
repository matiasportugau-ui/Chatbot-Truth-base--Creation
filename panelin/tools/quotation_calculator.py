from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Literal, Optional, TypedDict

try:
    # Optional at runtime, but present in repo requirements.
    import jsonschema  # type: ignore
except Exception:  # pragma: no cover
    jsonschema = None  # type: ignore


PanelType = Literal["Isopanel", "Isodec", "Isoroof"]


class QuotationResult(TypedDict):
    product_id: str
    area_m2: float
    unit_price_usd: float
    quantity: int
    subtotal_usd: float
    discount_usd: float
    total_usd: float
    currency: str
    calculation_verified: bool
    kb_version: str


@dataclass(frozen=True)
class TruthConfig:
    kb_path: Path
    schema_path: Optional[Path] = None


DEFAULT_TRUTH_CONFIG = TruthConfig(
    kb_path=Path("panelin_truth_bmcuruguay.json"),
    schema_path=Path("schemas/panelin_truth_bmcuruguay.schema.json"),
)


def _to_decimal(value: Any) -> Decimal:
    """
    Convert numeric-like values to Decimal safely.

    - Floats are stringified to avoid binary float artifacts.
    - Ints/Decimals/strings are supported.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    if isinstance(value, str):
        return Decimal(value.strip())
    raise TypeError(f"Unsupported numeric type: {type(value).__name__}")


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load_panelin_truth(config: TruthConfig = DEFAULT_TRUTH_CONFIG) -> Dict[str, Any]:
    """
    Load Panelin SSOT knowledge base (JSON).

    If the JSON Schema exists (and jsonschema is installed), validate on load.
    """
    data = json.loads(config.kb_path.read_text(encoding="utf-8"))
    if config.schema_path and config.schema_path.exists() and jsonschema is not None:
        schema = json.loads(config.schema_path.read_text(encoding="utf-8"))
        jsonschema.validate(instance=data, schema=schema)
    return data


def calculate_panel_quote(
    *,
    panel_type: PanelType,
    thickness_mm: int,
    length_m: float,
    width_m: float,
    quantity: int,
    discount_percent: float = 0.0,
    config: TruthConfig = DEFAULT_TRUTH_CONFIG,
) -> QuotationResult:
    """
    Deterministic quotation calculator.

    CRITICAL: The LLM must NEVER compute prices; it must call this function.
    """
    if quantity < 1:
        raise ValueError("quantity must be >= 1")
    if thickness_mm <= 0:
        raise ValueError("thickness_mm must be > 0")
    if length_m <= 0 or width_m <= 0:
        raise ValueError("length_m and width_m must be > 0")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("discount_percent must be between 0 and 100")

    kb = load_panelin_truth(config=config)
    kb_version = str(kb.get("version", "unknown"))
    products: Dict[str, Any] = kb.get("products", {})

    product_id = f"{panel_type}_{thickness_mm}mm"
    product = products.get(product_id)
    if not product:
        raise ValueError(f"Producto no encontrado en KB: {product_id}")

    price_per_m2 = _to_decimal(product["price_per_m2"])
    currency = str(product.get("currency", kb.get("currency", "USD")))

    # All arithmetic in Decimal
    area = _to_decimal(length_m) * _to_decimal(width_m)
    unit_price = _money(area * price_per_m2)
    subtotal = _money(unit_price * _to_decimal(quantity))
    discount_usd = _money(subtotal * _to_decimal(discount_percent) / Decimal("100"))
    total = _money(subtotal - discount_usd)

    result: QuotationResult = {
        "product_id": product_id,
        "area_m2": float(area),
        "unit_price_usd": float(unit_price),
        "quantity": int(quantity),
        "subtotal_usd": float(subtotal),
        "discount_usd": float(discount_usd),
        "total_usd": float(total),
        "currency": currency,
        "calculation_verified": True,
        "kb_version": kb_version,
    }

    # Dual-path verification (recompute independently)
    if not validate_quotation(result):
        raise RuntimeError("Quotation validation failed (dual-path check).")

    return result


def validate_quotation(result: QuotationResult) -> bool:
    """
    Post-calculation validation guardrail.

    Ensures the output is:
    - Marked as deterministic
    - Internally consistent within cents
    """
    if result.get("calculation_verified") is not True:
        return False

    unit_price = _to_decimal(result["unit_price_usd"])
    quantity = _to_decimal(result["quantity"])
    subtotal = _to_decimal(result["subtotal_usd"])
    discount = _to_decimal(result["discount_usd"])
    total = _to_decimal(result["total_usd"])

    if _money(unit_price * quantity) != _money(subtotal):
        return False
    if _money(subtotal - discount) != _money(total):
        return False
    if total <= 0:
        return False
    return True

