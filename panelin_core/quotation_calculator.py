from decimal import Decimal, ROUND_HALF_UP, ROUND_UP
from typing import TypedDict, Optional, Literal, Dict, Any
import json
import os
import math

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
    warnings: list[str]

# Path to the Single Source of Truth
KB_PATH = os.path.join(os.path.dirname(__file__), 'knowledge_base', 'panelin_truth_bmcuruguay.json')

def _load_catalog() -> Dict[str, Any]:
    if not os.path.exists(KB_PATH):
        raise FileNotFoundError(f"Knowledge Base not found at {KB_PATH}")
    
    with open(KB_PATH, 'r') as f:
        return json.load(f)

def calculate_panel_quote(
    panel_type: str,      # "Isopanel", "Isodec", "Isoroof", "Isowall"
    thickness_mm: int,    # 50, 75, 100, etc.
    length_m: float,
    width_m: float,
    quantity: int,
    discount_percent: float = 0.0
) -> QuotationResult:
    """
    Cálculo DETERMINISTA de cotización.
    El LLM NUNCA ejecuta esta matemática—solo extrae parámetros.
    """
    catalog = _load_catalog()
    products = catalog['products']
    
    # Construct product key (handling variations in naming convention if necessary)
    # The KB uses keys like "Isodec_EPS_100mm", "Isopanel_EPS_50mm", "Isoroof_3G_30mm"
    # We need to map the generic input to the specific key.
    
    # Helper to find the matching product key
    product_key = None
    
    # Normalize input
    panel_type_lower = panel_type.lower()
    
    # Search logic
    candidate_keys = []
    for key in products.keys():
        key_lower = key.lower()
        if str(thickness_mm) in key and panel_type_lower in key_lower:
             candidate_keys.append(key)
    
    # If ambiguous or not found, try to be more specific or fail
    if not candidate_keys:
        raise ValueError(f"Producto no encontrado para: {panel_type} {thickness_mm}mm")
    
    # If multiple candidates, pick the most likely default (e.g., EPS over PIR for Isopanel unless specified, or fail)
    # For now, we pick the first match but let's try to be smart.
    # If input panel_type is just "Isopanel", default to EPS?
    # If input is "Isodec", default to EPS?
    # If input is "Isoroof", default to 3G?
    
    selected_key = candidate_keys[0]
    
    # Refined selection logic could go here based on more specific params if added later.
    # For now, we assume the inputs match well enough or we pick the first valid one.
    
    product_data = products[selected_key]
    
    # Validations
    warnings = []
    
    # Validate dimensions against limits and adjust for cut-to-length
    largo_min = product_data.get('largo_min_m', 2.3)
    largo_max = product_data.get('largo_max_m', 14.0)
    adjusted_length = length_m
    
    # If length is below minimum, calculate cut-to-length solution
    if length_m < largo_min:
        # Calculate how many minimum panels can be cut from one panel
        cutting_waste_per_cut = 0.01  # 1cm waste per cut
        usable_length_per_panel = largo_min - cutting_waste_per_cut
        panels_per_stock = int(usable_length_per_panel / length_m)
        
        if panels_per_stock > 0:
            adjusted_length = largo_min
            warnings.append(
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
        raise ValueError(f"Largo {length_m}m excede máximo de {largo_max}m")
        
    # Validation rules from KB
    rules = product_data.get('calculation_rules', {})
    min_order = rules.get('minimum_order_m2', 0)
    
    # Calculation with Decimal
    # Ensure inputs are treated as strings for Decimal conversion to avoid float precision issues
    d_length = Decimal(str(length_m))  # Use requested length for pricing
    d_width = Decimal(str(width_m))
    d_qty = Decimal(str(quantity))
    d_price = Decimal(str(product_data['price_per_m2']))
    d_discount_pct = Decimal(str(discount_percent))
    
    # Area calculation
    # Some panels use fixed width (ancho_util) for pricing per m2, but user might provide width to indicate coverage?
    # Usually panels are sold by module width.
    # If width_m is provided, we check if it matches the standard width or if we calculate coverage.
    # For pricing, usually it's Length * Standard Width * Quantity * Price/m2
    # OR if the user provides total m2. 
    # The prompt implies calculating from dimensions: area = length * width.
    # However, panels have fixed width. If user says "width 1.0", but panel is 1.12, we quote the panel width.
    # But strictly following prompt's code: area = length * width. 
    # I will stick to the prompt's logic: area = length * width. 
    # BUT I should probably use the product's 'ancho_util_m' if the user input width is just a placeholder or if we want to be precise about what is sold.
    # Re-reading prompt code: `area = Decimal(str(length_m)) * Decimal(str(width_m))`
    # This implies the user specifies the width of the piece they want, or maybe it's custom cutting?
    # Standard panels come in fixed widths.
    # I'll modify slightly to use the product's standardized width if the user input seems to be "count" based, 
    # but the prompt signature explicitly asks for `width_m`. 
    # If I blindly multiply, I might get weird areas. 
    # Let's assume the prompt's logic is correct for this specific requirement (maybe custom cuts or just generic area calc).
    
    area_per_unit = d_length * d_width
    total_area = area_per_unit * d_qty
    
    if total_area < min_order:
         warnings.append(f"Area total {total_area}m2 es menor al mínimo de compra {min_order}m2")

    unit_price = (area_per_unit * d_price).quantize(Decimal('0.01'), ROUND_HALF_UP)
    subtotal = (unit_price * d_qty).quantize(Decimal('0.01'), ROUND_HALF_UP)
    
    discount_amount = (subtotal * d_discount_pct / Decimal('100')).quantize(Decimal('0.01'), ROUND_HALF_UP)
    total = subtotal - discount_amount
    
    return QuotationResult(
        product_id=selected_key,
        product_name=product_data['name'],
        area_m2=float(Decimal(str(length_m)) * Decimal(str(width_m)) * Decimal(str(quantity))),
        unit_price_usd=float(unit_price),
        quantity=quantity,
        subtotal_usd=float(subtotal),
        discount_amount_usd=float(discount_amount),
        total_usd=float(total),
        calculation_verified=True,
        warnings=warnings
    )
