import sys
from typing import Dict, List, Optional


# Mock QuotationConstants from pdf_styles.py
class QuotationConstants:
    IVA_RATE = 0.22
    DEFAULT_SHIPPING_USD = 280.0


# Extract logic from Panelin_GPT/01_UPLOAD_FILES/pdf_generator.py (AFTER FIX)
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

        # FIXED LOGIC
        # Total from all items (calculated without IVA)
        subtotal = products_total + accessories_total + fixings_total

        # Calculate IVA from the subtotal
        iva = subtotal * QuotationConstants.IVA_RATE

        # Materials total is subtotal + IVA
        materials_total = subtotal + iva

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

print("--- Running Verification After Fix ---")
result = QuotationDataFormatter.calculate_totals([test_item], [], [])

print(f"Item Price (Sin IVA): 100.0")
print(f"Calculated Subtotal: {result['subtotal']:.2f} (Expected: 100.0)")
print(f"Calculated IVA: {result['iva']:.2f} (Expected: 22.0)")
print(f"Calculated Materials Total: {result['materials_total']:.2f} (Expected: 122.0)")

if abs(result["subtotal"] - 100.0) < 0.01 and abs(result["iva"] - 22.0) < 0.01:
    print("\nFIX VERIFIED: Totals are calculated correctly.")
else:
    print("\nBug still exists or new issue found.")
