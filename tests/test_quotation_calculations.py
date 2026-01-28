import pytest
import sys
import os
from decimal import Decimal

# Add workspace root to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from panelin.tools.quotation_calculator import calculate_panel_quote

class TestQuotationCalculations:
    """Golden dataset tests - MUST pass before deployment"""
    
    def test_basic_isopanel_quote(self):
        # Using a key that exists in my consolidated KB
        # "isopanel_eps_paredes_fachadas" has price 41.88
        result = calculate_panel_quote.invoke({
            "panel_type": "isopanel_eps_paredes_fachadas",
            "thickness_mm": 50,
            "length_m": 2.0,
            "width_m": 1.0, # Note: Actual width in KB is 1.14 but logic uses input width
            "quantity": 10
        })
        
        # Area = 2.0 * 1.0 = 2.0 m2
        # Price = 41.88
        # Unit Price = 2.0 * 41.88 = 83.76
        # Subtotal = 83.76 * 10 = 837.60
        
        assert result['area_m2'] == 2.0
        assert result['total_usd'] == 837.60
        assert result['calculation_verified'] == True
    
    def test_discount_application(self):
        # "isodec_eps_techo" price 46.07
        result = calculate_panel_quote.invoke({
            "panel_type": "isodec_eps_techo",
            "thickness_mm": 100,
            "length_m": 3.0,
            "width_m": 1.0,
            "quantity": 50,
            "discount_percent": 10
        })
        # Area = 3.0 * 1.0 = 3.0
        # Unit Price = 3.0 * 46.07 = 138.21
        # Subtotal = 138.21 * 50 = 6910.50
        # Discount = 6910.50 * 0.10 = 691.05
        # Total = 6910.50 - 691.05 = 6219.45
        
        expected_subtotal = Decimal('6910.50')
        expected_total = Decimal('6219.45')
        
        assert abs(result['subtotal_usd'] - float(expected_subtotal)) < 0.01
        assert abs(result['total_usd'] - float(expected_total)) < 0.01
        assert result['calculation_verified'] == True

    def test_product_lookup_fuzzy(self):
        # "isopanel" should match "isopanel_eps_paredes_fachadas"
        result = calculate_panel_quote.invoke({
            "panel_type": "Isopanel",
            "thickness_mm": 50,
            "length_m": 1.0,
            "width_m": 1.0,
            "quantity": 1
        })
        assert "isopanel" in result['product_id'].lower()
