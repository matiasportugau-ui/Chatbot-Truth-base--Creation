import sys
import os
import pytest
from decimal import Decimal

# Add workspace root to python path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from panelin_core.quotation_calculator import calculate_panel_quote

class TestQuotationCalculations:
    """Golden dataset tests - MUST pass before deployment"""
    
    def test_basic_isopanel_quote(self):
        # Isopanel_EPS_50mm price is 41.88
        # Area = 2.0 * 1.10 = 2.2 m2 (using standard width 1.10 for Isopanel if we pass it, or whatever we pass)
        # Using 1.10 as width to match catalog width for Isopanel
        
        result = calculate_panel_quote(
            panel_type="Isopanel",
            thickness_mm=50,
            length_m=2.0,
            width_m=1.10, 
            quantity=10
        )
        
        # Calculation:
        # Area per panel = 2.0 * 1.10 = 2.2 m2
        # Price per m2 = 41.88
        # Unit price = 2.2 * 41.88 = 92.136 -> 92.14
        # Total = 92.14 * 10 = 921.40
        
        assert result['product_id'] == "Isopanel_EPS_50mm"
        assert result['area_m2'] == 22.0
        assert result['unit_price_usd'] == 92.14
        assert result['total_usd'] == 921.40
        assert result['calculation_verified'] == True
    
    def test_discount_application(self):
        # Isodec_EPS_100mm price is 46.07
        result = calculate_panel_quote(
            panel_type="Isodec",
            thickness_mm=100,
            length_m=3.0,
            width_m=1.12, # Standard Isodec width
            quantity=50,
            discount_percent=10
        )
        
        # Calc:
        # Area = 3.0 * 1.12 = 3.36 m2
        # Unit Price = 3.36 * 46.07 = 154.7952 -> 154.80
        # Subtotal = 154.80 * 50 = 7740.00
        # Discount = 7740.00 * 0.10 = 774.00
        # Total = 6966.00
        
        assert result['subtotal_usd'] == 7740.00
        assert result['discount_amount_usd'] == 774.00
        assert result['total_usd'] == 6966.00
        assert result['calculation_verified'] == True

    def test_min_order_warning(self):
        # Minimum order is 10m2
        # Isopanel minimum length is 2.3m. Use 2.5m to avoid length warning.
        result = calculate_panel_quote(
            panel_type="Isopanel",
            thickness_mm=50,
            length_m=2.5,
            width_m=1.10,
            quantity=1 # 2.5 * 1.1 = 2.75 m2 total < 10m2
        )
        
        assert len(result['warnings']) > 0
        # Check if any warning contains the expected text
        assert any("mínimo de compra" in w for w in result['warnings'])

    def test_product_not_found(self):
        with pytest.raises(ValueError):
            calculate_panel_quote(
                panel_type="NonExistentPanel",
                thickness_mm=999,
                length_m=1.0,
                width_m=1.0,
                quantity=1
            )
