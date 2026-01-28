from decimal import Decimal, ROUND_HALF_UP
from typing import TypedDict, Literal, Optional
import json
import os

# Path to the Single Source of Truth
KB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'panelin_truth_bmcuruguay.json')

class QuotationResult(TypedDict):
    product_id: str
    product_name: str
    area_m2: float
    unit_price_usd: float
    quantity: int
    subtotal_usd: float
    discount_amount_usd: float
    total_usd: float
    calculation_verified: bool
    error: Optional[str]

def load_catalog():
    if not os.path.exists(KB_PATH):
        raise FileNotFoundError(f"Knowledge Base not found at {KB_PATH}")
    with open(KB_PATH, 'r') as f:
        return json.load(f)

def calculate_panel_quote(
    product_sku: str,
    length_m: float,
    width_m: float,
    quantity: int,
    discount_percent: float = 0.0
) -> QuotationResult:
    """
    Cálculo DETERMINISTA de cotización.
    El LLM NUNCA ejecuta esta matemática—solo extrae parámetros.
    """
    try:
        catalog = load_catalog()
        
        if product_sku not in catalog['products']:
            # Fallback: try to find by similarity or return error
            # For strict deterministic, we return error if not exact match.
            return QuotationResult(
                product_id=product_sku,
                product_name="Unknown",
                area_m2=0.0,
                unit_price_usd=0.0,
                quantity=quantity,
                subtotal_usd=0.0,
                discount_amount_usd=0.0,
                total_usd=0.0,
                calculation_verified=False,
                error=f"Producto no encontrado: {product_sku}"
            )
        
        product_data = catalog['products'][product_sku]
        price_per_m2 = Decimal(str(product_data['price_per_m2']))
        
        # Cálculo con precisión Decimal (no floats)
        l_dec = Decimal(str(length_m))
        w_dec = Decimal(str(width_m))
        area = l_dec * w_dec
        
        # Unit price for one item (area * price_per_m2)
        # Note: Usually price is per m2. So item price = area * price_per_m2
        unit_price = (area * price_per_m2).quantize(Decimal('0.01'), ROUND_HALF_UP)
        
        q_dec = Decimal(str(quantity))
        subtotal = (unit_price * q_dec).quantize(Decimal('0.01'), ROUND_HALF_UP)
        
        d_pct = Decimal(str(discount_percent))
        discount = (subtotal * d_pct / Decimal('100')).quantize(Decimal('0.01'), ROUND_HALF_UP)
        
        total = subtotal - discount
        
        return QuotationResult(
            product_id=product_sku,
            product_name=product_data['name'],
            area_m2=float(area),
            unit_price_usd=float(unit_price),
            quantity=quantity,
            subtotal_usd=float(subtotal),
            discount_amount_usd=float(discount),
            total_usd=float(total),
            calculation_verified=True,
            error=None
        )
    except Exception as e:
        return QuotationResult(
            product_id=product_sku,
            product_name="Error",
            area_m2=0.0,
            unit_price_usd=0.0,
            quantity=quantity,
            subtotal_usd=0.0,
            discount_amount_usd=0.0,
            total_usd=0.0,
            calculation_verified=False,
            error=str(e)
        )

def validate_quotation(result: QuotationResult) -> bool:
    """
    Verifica que el resultado tenga la flag de verificado y valores consistentes.
    """
    if not result['calculation_verified']:
        return False
    if result['total_usd'] < 0:
        return False
    if result['quantity'] <= 0:
        return False
    return True
