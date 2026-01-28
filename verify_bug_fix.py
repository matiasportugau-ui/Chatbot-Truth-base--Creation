import sys
from typing import Dict, List, Optional
from datetime import datetime


# Mocking the classes needed for the test
class QuotationConstants:
    IVA_RATE = 0.22
    DEFAULT_SHIPPING_USD = 280.0


class QuotationDataFormatter:
    @staticmethod
    def calculate_item_total(item: Dict) -> float:
        return 100.0  # Mocked value

    @staticmethod
    def calculate_totals(
        products: List[Dict],
        accessories: List[Dict],
        fixings: List[Dict],
        shipping_usd: Optional[float] = None,
    ) -> Dict:
        # This is the method we want to test
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

        grand_total_items = products_total + accessories_total + fixings_total
        subtotal = grand_total_items / (1 + QuotationConstants.IVA_RATE)
        iva = grand_total_items - subtotal
        materials_total = grand_total_items
        shipping = (
            shipping_usd
            if shipping_usd is not None
            else QuotationConstants.DEFAULT_SHIPPING_USD
        )
        grand_total = materials_total + shipping

        return {"products_total": products_total, "grand_total": grand_total}


# Test case: total_usd is None
products = [{"name": "P1", "total_usd": None}]
accessories = []
fixings = []

try:
    result = QuotationDataFormatter.calculate_totals(products, accessories, fixings)
    print(f"Success! Result: {result}")
    if products[0]["total_usd"] == 100.0:
        print("Calculation verified correctly.")
    else:
        print(f"Unexpected total_usd: {products[0]['total_usd']}")
except TypeError as e:
    print(f"Failed with TypeError: {e}")
except Exception as e:
    print(f"Failed with error: {e}")
