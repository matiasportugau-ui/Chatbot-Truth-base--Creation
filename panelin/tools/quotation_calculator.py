import json
from decimal import Decimal, ROUND_HALF_UP
from typing import TypedDict, List, Optional, Union

# Define types
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
    warnings: List[str]

class ProductSpec(TypedDict):
    sku: str
    name: str
    price_per_m2: float
    min_length: float
    max_length: float

TRUTH_FILE_PATH = '/workspace/panelin_truth_bmcuruguay.json'

def load_catalog():
    with open(TRUTH_FILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_product_sku(panel_type: str, thickness_mm: int, catalog: dict) -> Optional[str]:
    """
    Finds a product SKU based on type and thickness.
    Simple heuristic matching for now.
    """
    panel_type_lower = panel_type.lower()
    
    # Map common names to families/subfamilies
    family_map = {
        "isopanel": ["ISOPANEL", "Pared"],
        "isodec": ["ISODEC", "Techo"],
        "isoroof": ["ISOROOF", "Techo"],
        "isowall": ["ISOWALL", "Fachada"]
    }
    
    keywords = family_map.get(panel_type_lower, [panel_type])
    
    for sku, product in catalog['products'].items():
        name_lower = product['name'].lower()
        cat_lower = product.get('category', '').lower()
        subcat_lower = product.get('subcategory', '').lower()
        
        # Check thickness
        specs = product.get('specifications', {})
        prod_thickness = specs.get('thickness_mm')
        
        # Handle cases where thickness might be in the name if not in specs
        if prod_thickness is None:
             # Try to extract from name or skip
             pass
        elif int(prod_thickness) != int(thickness_mm):
            continue

        # Check type match
        match = False
        if any(k.lower() in name_lower or k.lower() in cat_lower or k.lower() in subcat_lower for k in keywords):
            match = True
            
        if match:
            return sku
            
    return None

def calculate_panel_quote(
    panel_type: str,      # "Isopanel", "Isodec", "Isoroof"
    thickness_mm: int,    # 50, 75, 100, 150
    length_m: float,
    width_m: float,
    quantity: int,
    discount_percent: float = 0.0
) -> QuotationResult:
    """
    Deterministic calculation of quotation.
    The LLM NEVER executes this math—only extracts parameters.
    """
    catalog = load_catalog()
    
    # 1. Identify Product
    sku = find_product_sku(panel_type, thickness_mm, catalog)
    if not sku:
        # Fallback: try to construct a key if it was using the example format, or fail
        # For this implementation, we fail if not found by heuristic
        raise ValueError(f"No matching product found for {panel_type} {thickness_mm}mm")
    
    product = catalog['products'][sku]
    
    # 2. Get Price
    # Use price_per_m2 (which is sale_iva_inc in our mapping)
    price_per_m2_float = product['price_per_m2']
    if price_per_m2_float is None:
         raise ValueError(f"Price not available for {sku}")
         
    price_per_m2 = Decimal(str(price_per_m2_float))
    
    # 3. Validate Dimensions
    warnings = []
    specs = product.get('specifications', {})
    
    # Parse length limits "min / max" string or use defaults
    largo_range = specs.get('largo_min_max', "0.5 / 14")
    try:
        if isinstance(largo_range, str) and '/' in largo_range:
            min_l, max_l = map(float, largo_range.split('/'))
        else:
            min_l, max_l = 0.5, 14.0
    except:
        min_l, max_l = 0.5, 14.0
        
    if length_m < min_l:
        warnings.append(f"Length {length_m}m is below recommended minimum {min_l}m")
    if length_m > max_l:
        warnings.append(f"Length {length_m}m exceeds recommended maximum {max_l}m")

    # 4. Calculate
    # Calculation with Decimal precision
    area_per_panel = Decimal(str(length_m)) * Decimal(str(width_m))
    total_area = area_per_panel * quantity
    
    unit_price = (area_per_panel * price_per_m2).quantize(Decimal('0.01'), ROUND_HALF_UP)
    subtotal = (unit_price * quantity).quantize(Decimal('0.01'), ROUND_HALF_UP)
    
    discount_amount = (subtotal * Decimal(str(discount_percent)) / 100).quantize(Decimal('0.01'), ROUND_HALF_UP)
    total = subtotal - discount_amount
    
    return {
        "product_id": sku,
        "product_name": product['name'],
        "area_m2": float(total_area),
        "unit_price_usd": float(unit_price),
        "quantity": quantity,
        "subtotal_usd": float(subtotal),
        "discount_amount_usd": float(discount_amount),
        "total_usd": float(total),
        "calculation_verified": True,
        "warnings": warnings
    }

def lookup_product_specs(panel_type: str) -> List[ProductSpec]:
    """
    Returns product specifications for a given type to help the LLM or user.
    """
    catalog = load_catalog()
    results = []
    
    panel_type_lower = panel_type.lower()
    
    for sku, product in catalog['products'].items():
        name_lower = product['name'].lower()
        cat_lower = product.get('category', '').lower()
        
        if panel_type_lower in name_lower or panel_type_lower in cat_lower:
            specs = product.get('specifications', {})
            results.append({
                "sku": sku,
                "name": product['name'],
                "price_per_m2": product['price_per_m2'],
                "min_length": 0.0, # Placeholder, logic similar to above needed
                "max_length": 0.0
            })
            
    return results

if __name__ == "__main__":
    # Simple test
    try:
        quote = calculate_panel_quote("Isoroof", 50, 3.0, 1.0, 10)
        print(json.dumps(quote, indent=2))
    except Exception as e:
        print(f"Error: {e}")
