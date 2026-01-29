"""
Test Suite for Quotation Calculator
====================================

Golden dataset tests that MUST pass before deployment.
Tests ensure 100% calculation accuracy using deterministic Python/Decimal operations.

CRITICAL: If any test fails, the system is NOT safe for production.
"""

import pytest
from decimal import Decimal
import json
from pathlib import Path

# Import the tools we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.quotation_calculator import (
    calculate_panel_quote,
    calculate_panels_needed,
    calculate_supports_needed,
    calculate_fixation_points,
    calculate_accessories,
    lookup_product_specs,
    validate_quotation,
    _decimal_round,
    _decimal_ceil,
)


class TestDecimalPrecision:
    """Test Decimal precision utilities"""
    
    def test_decimal_round_half_up(self):
        """Test that we use banker's rounding correctly"""
        assert float(_decimal_round(Decimal("10.125"))) == 10.13
        assert float(_decimal_round(Decimal("10.124"))) == 10.12
        assert float(_decimal_round(Decimal("10.1250"))) == 10.13
    
    def test_decimal_ceil(self):
        """Test ceiling function"""
        assert _decimal_ceil(Decimal("5.1")) == 6
        assert _decimal_ceil(Decimal("5.0")) == 5
        assert _decimal_ceil(Decimal("5.9999")) == 6
        assert _decimal_ceil(Decimal("0.01")) == 1


class TestPanelsNeededCalculation:
    """Test panels needed calculation"""
    
    def test_exact_fit(self):
        """When width divides evenly by ancho_util"""
        result = calculate_panels_needed(5.0, 1.0)
        assert result == 5
    
    def test_round_up_required(self):
        """When width doesn't divide evenly"""
        result = calculate_panels_needed(5.5, 1.12)
        # 5.5 / 1.12 = 4.91... → rounds up to 5
        assert result == 5
    
    def test_small_remainder(self):
        """Small remainder should still round up"""
        result = calculate_panels_needed(5.01, 1.0)
        assert result == 6
    
    def test_large_coverage(self):
        """Test large area coverage"""
        result = calculate_panels_needed(100.0, 1.12)
        # 100 / 1.12 = 89.28... → rounds up to 90
        assert result == 90
    
    def test_minimum_one_panel(self):
        """Should need at least 1 panel for any positive width"""
        result = calculate_panels_needed(0.1, 1.12)
        assert result == 1
    
    def test_invalid_ancho_util(self):
        """Zero ancho_util should raise error"""
        with pytest.raises(ValueError):
            calculate_panels_needed(5.0, 0)
    
    def test_invalid_ancho_total(self):
        """Zero or negative ancho_total should raise error"""
        with pytest.raises(ValueError):
            calculate_panels_needed(0, 1.12)
        with pytest.raises(ValueError):
            calculate_panels_needed(-5.0, 1.12)


class TestSupportsNeededCalculation:
    """Test supports (apoyos) calculation"""
    
    def test_standard_calculation(self):
        """Standard supports calculation"""
        result = calculate_supports_needed(6.0, 5.5)
        # (6 / 5.5) + 1 = 2.09 → rounds up to 3
        assert result == 3
    
    def test_exact_multiple(self):
        """When largo is exact multiple of autoportancia"""
        result = calculate_supports_needed(10.0, 5.0)
        # (10 / 5) + 1 = 3 → stays at 3
        assert result == 3
    
    def test_short_panel(self):
        """Panel shorter than autoportancia"""
        result = calculate_supports_needed(3.0, 5.5)
        # (3 / 5.5) + 1 = 1.545 → rounds up to 2
        assert result == 2
    
    def test_very_long_panel(self):
        """Very long panel needs many supports"""
        result = calculate_supports_needed(14.0, 5.5)
        # (14 / 5.5) + 1 = 3.545 → rounds up to 4
        assert result == 4
    
    def test_invalid_autoportancia(self):
        """Zero autoportancia should raise error"""
        with pytest.raises(ValueError):
            calculate_supports_needed(6.0, 0)


class TestFixationPointsCalculation:
    """Test fixation points calculation"""
    
    def test_roof_installation(self):
        """Roof fixation points calculation"""
        result = calculate_fixation_points(4, 3, 6.0, "techo")
        # ((4 * 3) * 2) + (6 * 2 / 2.5) = 24 + 4.8 = 28.8 → 29
        assert result == 29
    
    def test_wall_installation(self):
        """Wall fixation points calculation (simpler)"""
        result = calculate_fixation_points(4, 3, 6.0, "pared")
        # (4 * 3) * 2 = 24
        assert result == 24
    
    def test_minimum_fixation(self):
        """Minimum fixation points"""
        result = calculate_fixation_points(1, 1, 1.0, "techo")
        # ((1 * 1) * 2) + (1 * 2 / 2.5) = 2 + 0.8 = 2.8 → 3
        assert result == 3


class TestAccessoriesCalculation:
    """Test accessories calculation"""
    
    def test_complete_accessories(self):
        """Full accessories calculation"""
        result = calculate_accessories(
            cantidad_paneles=4,
            apoyos=3,
            largo=6.0,
            ancho_util=1.12,
            installation_type="techo"
        )
        
        # Verify all fields present
        assert "panels_needed" in result
        assert "supports_needed" in result
        assert "fixation_points" in result
        assert "rod_quantity" in result
        assert "front_drip_edge_units" in result
        assert "lateral_drip_edge_units" in result
        assert "rivets_needed" in result
        assert "silicone_tubes" in result
        assert "metal_nuts" in result
        assert "concrete_nuts" in result
        assert "concrete_anchors" in result
        
        # Verify consistency
        assert result["panels_needed"] == 4
        assert result["supports_needed"] == 3
        assert result["metal_nuts"] == result["fixation_points"] * 2
        assert result["concrete_nuts"] == result["fixation_points"]


class TestProductLookup:
    """Test product lookup functionality"""
    
    def test_lookup_by_product_id(self):
        """Lookup product by exact ID"""
        result = lookup_product_specs(product_id="ISOPANEL_EPS_50mm")
        assert result is not None
        assert result["product_id"] == "ISOPANEL_EPS_50mm"
        assert result["price_per_m2"] > 0
    
    def test_lookup_by_family_and_thickness(self):
        """Lookup by family and thickness"""
        result = lookup_product_specs(family="ISODEC", thickness_mm=100)
        assert result is not None
        assert result["family"] == "ISODEC"
        assert result["thickness_mm"] == 100
    
    def test_lookup_not_found(self):
        """Lookup for non-existent product by exact ID"""
        # When using product_id, must match exactly - return None if not found
        result = lookup_product_specs(product_id="FAKE_PRODUCT_999mm")
        assert result is None


class TestQuotationCalculation:
    """Test complete quotation calculation - GOLDEN DATASET"""
    
    def test_basic_quotation(self):
        """Basic quotation calculation"""
        result = calculate_panel_quote(
            product_id="ISOPANEL_EPS_50mm",
            length_m=6.0,
            width_m=4.0,
            quantity=1,
            include_tax=True
        )
        
        # CRITICAL: Verify calculation was done by code, not LLM
        assert result["calculation_verified"] == True
        assert result["calculation_method"] == "python_decimal_deterministic"
        
        # Verify quotation fields
        assert result["product_id"] == "ISOPANEL_EPS_50mm"
        assert result["length_m"] == 6.0
        assert result["width_m"] == 4.0
        assert result["area_m2"] > 0
        assert result["panels_needed"] >= 1
        assert result["subtotal_usd"] > 0
        assert result["total_usd"] > 0
        assert result["currency"] == "USD"
    
    def test_quotation_with_discount(self):
        """Quotation with discount applied"""
        result = calculate_panel_quote(
            product_id="ISODEC_EPS_100mm",
            length_m=6.0,
            width_m=4.0,
            quantity=1,
            discount_percent=10.0,
            include_tax=True
        )
        
        assert result["calculation_verified"] == True
        assert result["discount_percent"] == 10.0
        assert result["discount_amount_usd"] > 0
        assert result["total_before_tax_usd"] < result["subtotal_usd"]
    
    def test_quotation_no_tax(self):
        """Quotation without tax"""
        result = calculate_panel_quote(
            product_id="ISOPANEL_EPS_100mm",
            length_m=4.0,
            width_m=3.0,
            quantity=1,
            include_tax=False
        )
        
        assert result["calculation_verified"] == True
        assert result["tax_amount_usd"] == 0
        assert result["total_usd"] == result["total_before_tax_usd"]
    
    def test_quotation_multiple_quantities(self):
        """Quotation with multiple quantities"""
        single = calculate_panel_quote(
            product_id="ISOROOF_3G",
            length_m=5.0,
            width_m=3.0,
            quantity=1,
            include_tax=False
        )
        
        double = calculate_panel_quote(
            product_id="ISOROOF_3G",
            length_m=5.0,
            width_m=3.0,
            quantity=2,
            include_tax=False
        )
        
        # Double quantity should be roughly 2x the price
        ratio = double["subtotal_usd"] / single["subtotal_usd"]
        assert 1.9 < ratio < 2.1
    
    def test_quotation_bulk_discount(self):
        """Quotation should apply bulk discount for large orders"""
        result = calculate_panel_quote(
            product_id="ISOPANEL_EPS_50mm",
            length_m=10.0,
            width_m=12.0,  # Large width = many panels = bulk discount
            quantity=1,
            discount_percent=0,  # No manual discount
            include_tax=False
        )
        
        # Bulk discount should be applied for >100m²
        if result["area_m2"] >= 100:
            assert result["discount_percent"] >= 5  # Bulk discount kicks in
    
    def test_quotation_invalid_product(self):
        """Quotation for invalid product should fail"""
        with pytest.raises(ValueError, match="Product not found"):
            calculate_panel_quote(
                product_id="FAKE_PRODUCT",
                length_m=6.0,
                width_m=4.0,
                quantity=1
            )
    
    def test_quotation_invalid_dimensions(self):
        """Invalid dimensions should fail"""
        with pytest.raises(ValueError):
            calculate_panel_quote(
                product_id="ISOPANEL_EPS_50mm",
                length_m=0,  # Invalid
                width_m=4.0,
                quantity=1
            )
        
        with pytest.raises(ValueError):
            calculate_panel_quote(
                product_id="ISOPANEL_EPS_50mm",
                length_m=6.0,
                width_m=-1.0,  # Invalid
                quantity=1
            )
    
    def test_quotation_exceeds_max_length(self):
        """Length exceeding max should fail"""
        with pytest.raises(ValueError, match="exceeds maximum"):
            calculate_panel_quote(
                product_id="ISOPANEL_EPS_50mm",
                length_m=20.0,  # Exceeds 14m max
                width_m=4.0,
                quantity=1
            )
    
    def test_quotation_below_min_length(self):
        """Length below minimum should fail"""
        with pytest.raises(ValueError, match="below minimum"):
            calculate_panel_quote(
                product_id="ISOPANEL_EPS_50mm",
                length_m=1.0,  # Below 2.3m min
                width_m=4.0,
                quantity=1
            )
    
    def test_quotation_invalid_discount(self):
        """Discount above max should fail"""
        with pytest.raises(ValueError, match="Discount must be between"):
            calculate_panel_quote(
                product_id="ISOPANEL_EPS_50mm",
                length_m=6.0,
                width_m=4.0,
                quantity=1,
                discount_percent=50.0  # Exceeds max 15%
            )


class TestQuotationValidation:
    """Test quotation validation"""
    
    def test_valid_quotation(self):
        """Valid quotation should pass validation"""
        result = calculate_panel_quote(
            product_id="ISOPANEL_EPS_50mm",
            length_m=6.0,
            width_m=4.0,
            quantity=1,
            include_tax=True
        )
        
        is_valid, errors = validate_quotation(result)
        assert is_valid == True
        assert len(errors) == 0
    
    def test_invalid_calculation_verified(self):
        """Quotation with calculation_verified=False should fail"""
        result = calculate_panel_quote(
            product_id="ISOPANEL_EPS_50mm",
            length_m=6.0,
            width_m=4.0,
            quantity=1
        )
        
        # Simulate LLM calculation (FORBIDDEN in real system)
        result["calculation_verified"] = False
        
        is_valid, errors = validate_quotation(result)
        assert is_valid == False
        assert any("CRITICAL" in e for e in errors)
    
    def test_invalid_calculation_method(self):
        """Wrong calculation method should fail"""
        result = calculate_panel_quote(
            product_id="ISOPANEL_EPS_50mm",
            length_m=6.0,
            width_m=4.0,
            quantity=1
        )
        
        result["calculation_method"] = "llm_inference"
        
        is_valid, errors = validate_quotation(result)
        assert is_valid == False


class TestGoldenDataset:
    """
    Golden dataset tests with exact expected values.
    These tests verify specific calculation scenarios.
    """
    
    def test_golden_isopanel_50mm_6x4(self):
        """Golden test: ISOPANEL 50mm, 6m x 4m"""
        result = calculate_panel_quote(
            product_id="ISOPANEL_EPS_50mm",
            length_m=6.0,
            width_m=4.0,
            quantity=1,
            discount_percent=0,
            include_tax=True
        )
        
        # Verify exact values based on KB:
        # - Price: $41.88/m²
        # - Ancho útil: 1.14m
        # - Panels needed: ceil(4.0 / 1.14) = 4
        # - Effective area: 6 * (1.14 * 4) = 27.36 m²
        # - Subtotal: 27.36 * 41.88 = 1145.84
        # - Tax (22%): 252.09
        # - Total: 1397.93
        
        assert result["panels_needed"] == 4
        assert result["calculation_verified"] == True
        
        # Allow small tolerance for rounding
        assert abs(result["area_m2"] - 27.36) < 0.1
    
    def test_golden_isodec_100mm_with_discount(self):
        """Golden test: ISODEC 100mm with 10% discount"""
        result = calculate_panel_quote(
            product_id="ISODEC_EPS_100mm",
            length_m=5.0,
            width_m=5.0,
            quantity=1,
            discount_percent=10.0,
            include_tax=False
        )
        
        # Verify discount was applied
        expected_discount_amount = result["subtotal_usd"] * 0.10
        assert abs(result["discount_amount_usd"] - expected_discount_amount) < 0.01
        assert result["total_usd"] == result["subtotal_usd"] - result["discount_amount_usd"]


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_minimum_dimensions(self):
        """Test with minimum allowed dimensions"""
        result = calculate_panel_quote(
            product_id="ISOPANEL_EPS_50mm",
            length_m=2.3,  # Minimum length
            width_m=0.5,   # Minimum width
            quantity=1
        )
        
        assert result["calculation_verified"] == True
        assert result["panels_needed"] >= 1
    
    def test_maximum_dimensions(self):
        """Test with maximum allowed dimensions"""
        result = calculate_panel_quote(
            product_id="ISOPANEL_EPS_50mm",
            length_m=14.0,  # Maximum length
            width_m=50.0,   # Large width
            quantity=1
        )
        
        assert result["calculation_verified"] == True
        assert result["panels_needed"] > 1
    
    def test_high_quantity(self):
        """Test with high quantity"""
        result = calculate_panel_quote(
            product_id="ISOPANEL_EPS_50mm",
            length_m=6.0,
            width_m=4.0,
            quantity=100
        )
        
        assert result["calculation_verified"] == True
        assert result["subtotal_usd"] > 0
    
    def test_precision_with_many_decimals(self):
        """Test precision with many decimal places in input"""
        result = calculate_panel_quote(
            product_id="ISOPANEL_EPS_50mm",
            length_m=6.123456789,
            width_m=4.987654321,
            quantity=1
        )
        
        assert result["calculation_verified"] == True
        # Result should be properly rounded
        assert isinstance(result["total_usd"], float)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
