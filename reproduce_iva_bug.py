import sys
from typing import Dict, List, Optional


# Mock QuotationConstants from pdf_styles.py
class QuotationConstants:
    IVA_RATE = 0.22
    DEFAULT_SHIPPING_USD = 280.0


# Extract logic from Panelin_GPT/01_UPLOAD_FILES/pdf_generator.py
class QuotationDataFormatter:
    @staticmethod
    def calculate_item_total(item: Dict) -> float:
        unit_base = item.get("unit_base", "unidad").lower()
        price = item.get("sale_sin_iva", item.get("unit_price_usd", 0))

        if unit_base == "unidad":
            return item.get("quantity", 0) * price
        elif unit_base == "ml":
            quantity = item.get("quantity", 0)
            length_m = item.get("Length_m", item.get("length_m", 0))
            return quantity * length_m * price
        elif unit_base == "m²" or unit_base == "m2":
            total_m2 = item.get("total_m2", 0)
            return total_m2 * price
        else:
            return item.get("quantity", 0) * price

    @staticmethod
    def calculate_totals(
        products: List[Dict],
        accessories: List[Dict],
        fixings: List[Dict],
        shipping_usd: Optional[float] = None,
    ) -> Dict:
        products_total = 0
        for item in products:
            if item.get("total_usd") is None:
                item["total_usd"] = QuotationDataFormatter.calculate_item_total(item)
            products_total += item["total_usd"]

        accessories_total = 0
        for item in accessories:
            if item.get("total_usd") is None:
                item["total_usd"] = QuotationDataFormatter.calculate_item_total(item)
            accessories_total += item["total_usd"]

        fixings_total = 0
        for item in fixings:
            if item.get("total_usd") is None:
                item["total_usd"] = QuotationDataFormatter.calculate_item_total(item)
            fixings_total += item["total_usd"]

        # Total from all items (which already includes IVA) <- THIS IS THE BUGGY ASSUMPTION
        grand_total_items = products_total + accessories_total + fixings_total

        # Calculate subtotal (net) and IVA from the total that already includes it
        subtotal = grand_total_items / (1 + QuotationConstants.IVA_RATE)
        iva = grand_total_items - subtotal

        # Materials total is the original sum (IVA included)
        materials_total = grand_total_items

        shipping = (
            shipping_usd
            if shipping_usd is not None
            else QuotationConstants.DEFAULT_SHIPPING_USD
        )
        grand_total = materials_total + shipping

        return {
            "subtotal": subtotal,
            "iva": iva,
            "materials_total": materials_total,
            "grand_total": grand_total,
        }


# Test case
test_item = {
    "name": "Test Product",
    "sale_sin_iva": 100.0,
    "quantity": 1,
    "unit_base": "unidad",
}

print("--- Running Reproduction ---")
result = QuotationDataFormatter.calculate_totals([test_item], [], [])

print(f"Item Price (Sin IVA): 100.0")
print(f"Calculated Subtotal: {result['subtotal']:.2f} (Expected: 100.0)")
print(f"Calculated IVA: {result['iva']:.2f} (Expected: 22.0)")
print(f"Calculated Materials Total: {result['materials_total']:.2f} (Expected: 122.0)")

if abs(result["subtotal"] - 100.0) > 0.01:
    print("\nBUG CONFIRMED: Subtotal is underreported.")
else:
    print("\nNo bug found.")
