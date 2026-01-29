import pytest
from decimal import Decimal
import sys
import os

# Add workspace to path
sys.path.append('/workspace')

from panelin.tools.quotation_calculator import calculate_panel_quote

class TestQuotationCalculations:
    """Golden dataset tests - MUST pass before deployment"""
    
    def test_basic_quote_sanity(self):
        # We need to find a valid SKU from our generated KB to test.
        # SKU: IROOF50
        
        result = calculate_panel_quote(
            product_sku="IROOF50",
            length_m=3.0,
            width_m=1.0,
            quantity=10
        )
        
        assert result['calculation_verified'] == True
        assert result['quantity'] == 10
        assert result['area_m2'] == 3.0 * 1.0
        
        assert result['subtotal_usd'] > 0
        assert abs(result['total_usd'] - result['subtotal_usd']) < 0.01 # No discount
        
    def test_discount_application(self):
        # SKU: IROOF50
        result = calculate_panel_quote(
            product_sku="IROOF50",
            length_m=2.0,
            width_m=1.0,
            quantity=5,
            discount_percent=10
        )
        
        assert result['calculation_verified'] == True
        assert result['discount_amount_usd'] > 0
        
        # subtotal - discount = total
        assert abs(result['subtotal_usd'] - result['discount_amount_usd'] - result['total_usd']) < 0.01

    def test_invalid_product(self):
        result = calculate_panel_quote(
            product_sku="NONEXISTENT_SKU_123",
            length_m=1.0,
            width_m=1.0,
            quantity=1
        )
        
        assert result['calculation_verified'] == False
        assert result['error'] is not None
