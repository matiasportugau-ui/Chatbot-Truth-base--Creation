"""
Unit Tests: Calculation Functions
==================================

Tests for core calculation functions in quotation_calculator_v3.
Tests use Decimal precision and validate mathematical accuracy.
"""

import pytest
from decimal import Decimal
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from quotation_calculator_v3 import (
    calculate_panels_needed,
    calculate_supports_needed,
    calculate_fixation_points,
    _decimal_round,
    _decimal_ceil
)


class TestPanelsCalculation:
    """Tests for calculate_panels_needed()"""
    
    def test_exact_division(self):
        """Test when width divides exactly by ancho_util"""
        result = calculate_panels_needed(ancho_total=11.2, ancho_util=1.12)
        assert result == 10
    
    def test_needs_rounding_up(self):
        """Test when division requires rounding up"""
        result = calculate_panels_needed(ancho_total=10.0, ancho_util=1.12)
        assert result == 9  # 10 / 1.12 = 8.93 → rounds up to 9
    
    def test_single_panel(self):
        """Test when only one panel is needed"""
        result = calculate_panels_needed(ancho_total=1.0, ancho_util=1.12)
        assert result == 1
    
    @pytest.mark.parametrize("ancho_total,ancho_util,expected", [
        (5.0, 1.0, 5),
        (5.5, 1.0, 6),
        (10.0, 1.12, 9),
        (11.2, 1.12, 10),
        (15.0, 1.12, 14),
        (0.5, 1.12, 1),
    ])
    def test_various_widths(self, ancho_total, ancho_util, expected):
        """Parameterized test for various width combinations"""
        result = calculate_panels_needed(ancho_total, ancho_util)
        assert result == expected
    
    def test_invalid_zero_width(self):
        """Test that zero width raises error"""
        with pytest.raises(ValueError, match="ancho_total must be greater than 0"):
            calculate_panels_needed(ancho_total=0, ancho_util=1.12)
    
    def test_invalid_zero_util(self):
        """Test that zero ancho_util raises error"""
        with pytest.raises(ValueError, match="ancho_util must be greater than 0"):
            calculate_panels_needed(ancho_total=10.0, ancho_util=0)


class TestSupportsCalculation:
    """Tests for calculate_supports_needed()"""
    
    def test_exact_division(self):
        """Test when length divides exactly by autoportancia"""
        result = calculate_supports_needed(largo=10.0, autoportancia=5.0)
        assert result == 3  # (10/5) + 1 = 3
    
    def test_needs_rounding_up(self):
        """Test when division requires rounding up"""
        result = calculate_supports_needed(largo=11.0, autoportancia=5.5)
        assert result == 3  # (11/5.5) + 1 = 3
    
    @pytest.mark.parametrize("largo,autoportancia,expected", [
        (5.0, 5.5, 2),   # (5/5.5) + 1 = 1.91 → 2
        (10.0, 5.5, 3),  # (10/5.5) + 1 = 2.82 → 3
        (11.0, 5.5, 3),  # (11/5.5) + 1 = 3.0 → 3
        (15.0, 5.5, 4),  # (15/5.5) + 1 = 3.73 → 4
    ])
    def test_various_lengths(self, largo, autoportancia, expected):
        """Parameterized test for various length combinations"""
        result = calculate_supports_needed(largo, autoportancia)
        assert result == expected


class TestFixationPointsCalculation:
    """Tests for calculate_fixation_points()"""
    
    def test_basic_fixation_points(self):
        """Test basic fixation points calculation"""
        result = calculate_fixation_points(
            panels_needed=10,
            supports_needed=3,
            largo=10.0
        )
        # Formula: ceil((panels × supports × 2) + (largo × 2 / 2.5))
        # = ceil((10 × 3 × 2) + (10 × 2 / 2.5))
        # = ceil(60 + 8) = 68
        assert result == 68
    
    @pytest.mark.parametrize("panels,supports,largo,expected", [
        (5, 2, 5.0, 24),   # (5×2×2) + (5×2/2.5) = 20 + 4 = 24
        (10, 3, 10.0, 68), # (10×3×2) + (10×2/2.5) = 60 + 8 = 68
        (8, 4, 12.0, 74),  # (8×4×2) + (12×2/2.5) = 64 + 9.6 → 74
    ])
    def test_various_scenarios(self, panels, supports, largo, expected):
        """Parameterized test for various fixation scenarios"""
        result = calculate_fixation_points(panels, supports, largo)
        assert result == expected


class TestDecimalPrecision:
    """Tests for Decimal precision functions"""
    
    def test_decimal_round_two_places(self):
        """Test rounding to 2 decimal places"""
        value = Decimal("123.456")
        result = _decimal_round(value, places=2)
        assert result == Decimal("123.46")
    
    def test_decimal_round_zero_places(self):
        """Test rounding to whole number"""
        value = Decimal("123.6")
        result = _decimal_round(value, places=0)
        assert result == Decimal("124")
    
    def test_decimal_ceil_rounds_up(self):
        """Test ceiling function rounds up"""
        value = Decimal("10.1")
        result = _decimal_ceil(value)
        assert result == 11
    
    def test_decimal_ceil_exact_value(self):
        """Test ceiling with exact integer"""
        value = Decimal("10.0")
        result = _decimal_ceil(value)
        assert result == 10
    
    @pytest.mark.parametrize("value,places,expected", [
        ("100.123", 2, "100.12"),
        ("100.126", 2, "100.13"),
        ("100.125", 2, "100.13"),  # Banker's rounding
        ("99.999", 2, "100.00"),
        ("0.001", 2, "0.00"),
    ])
    def test_decimal_rounding_scenarios(self, value, places, expected):
        """Parameterized decimal rounding tests"""
        result = _decimal_round(Decimal(value), places=places)
        assert result == Decimal(expected)


class TestPricingCalculations:
    """Tests for pricing calculations with Decimal precision"""
    
    def test_subtotal_calculation(self, decimal_test_values):
        """Test subtotal = price × area"""
        price = decimal_test_values["price_per_m2"]
        area = decimal_test_values["area"]
        expected = decimal_test_values["expected_subtotal"]
        
        subtotal = _decimal_round(price * area)
        assert subtotal == expected
    
    def test_discount_10_percent(self, decimal_test_values):
        """Test 10% discount calculation"""
        subtotal = decimal_test_values["expected_subtotal"]
        discount_pct = decimal_test_values["discount_10pct"]
        expected_discount = decimal_test_values["expected_discount_10"]
        
        discount = _decimal_round(subtotal * discount_pct / Decimal("100"))
        assert discount == expected_discount
    
    @pytest.mark.parametrize("discount_percent,expected_multiplier", [
        (0, Decimal("1.00")),
        (10, Decimal("0.90")),
        (20, Decimal("0.80")),
        (30, Decimal("0.70")),
    ])
    def test_discount_multipliers(self, discount_percent, expected_multiplier):
        """Test discount multiplier calculations"""
        multiplier = Decimal("1.00") - (Decimal(str(discount_percent)) / Decimal("100"))
        assert multiplier == expected_multiplier
    
    def test_iva_calculation(self, decimal_test_values):
        """Test IVA (22%) calculation"""
        total_before_tax = decimal_test_values["expected_total_after_discount"]
        tax_rate = decimal_test_values["tax_rate"]
        expected_tax = decimal_test_values["expected_tax"]
        
        tax = _decimal_round(total_before_tax * tax_rate)
        assert tax == expected_tax


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_small_width(self):
        """Test with very small width"""
        result = calculate_panels_needed(ancho_total=0.1, ancho_util=1.12)
        assert result == 1  # Always need at least 1 panel
    
    def test_very_large_width(self):
        """Test with very large width"""
        result = calculate_panels_needed(ancho_total=100.0, ancho_util=1.12)
        assert result == 90  # 100 / 1.12 = 89.29 → 90
    
    def test_minimum_span(self):
        """Test with minimum span"""
        result = calculate_supports_needed(largo=0.5, autoportancia=5.5)
        assert result == 2  # (0.5/5.5) + 1 = 1.09 → 2
    
    def test_maximum_span(self):
        """Test with maximum span (14m)"""
        result = calculate_supports_needed(largo=14.0, autoportancia=5.5)
        assert result == 4  # (14/5.5) + 1 = 3.55 → 4
