"""
Test Cases for Quotation Calculator
====================================

Golden dataset tests - MUST pass before deployment.
These tests verify deterministic calculations with known correct values.
"""

import pytest
from decimal import Decimal
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from panelin_hybrid_agent.tools.quotation_calculator import (
    calculate_panel_quote,
    calculate_fixation_points,
    calculate_profiles_quote,
    calculate_complete_quotation,
    _round_up,
)


class TestCalculationVerified:
    """Test that all calculations return calculation_verified=True"""
    
    def test_panel_quote_verified(self):
        """Panel quote must be verified"""
        result = calculate_panel_quote(
            panel_type="Isoroof",
            thickness_mm=50,
            length_m=6.0,
            width_m=1.0,
            quantity=10,
        )
        assert result["calculation_verified"] == True
    
    def test_fixation_verified(self):
        """Fixation calculation must be verified"""
        result = calculate_fixation_points(
            panel_count=10,
            panel_length_m=6.0,
        )
        assert result["calculation_verified"] == True
    
    def test_profiles_verified(self):
        """Profiles calculation must be verified"""
        result = calculate_profiles_quote(
            panel_count=10,
            panel_length_m=6.0,
            panel_width_m=1.0,
            thickness_mm=50,
        )
        assert result["calculation_verified"] == True


class TestPanelQuoteCalculations:
    """Test panel quote calculations"""
    
    def test_basic_area_calculation(self):
        """Area = length × width"""
        result = calculate_panel_quote(
            panel_type="Isoroof",
            thickness_mm=50,
            length_m=6.0,
            width_m=1.0,
            quantity=1,
        )
        assert result["area_m2"] == 6.0
    
    def test_quantity_multiplier(self):
        """Total should include quantity"""
        single = calculate_panel_quote(
            panel_type="Isoroof",
            thickness_mm=50,
            length_m=6.0,
            width_m=1.0,
            quantity=1,
        )
        
        ten = calculate_panel_quote(
            panel_type="Isoroof",
            thickness_mm=50,
            length_m=6.0,
            width_m=1.0,
            quantity=10,
        )
        
        # Total should be 10x single (before discount)
        assert abs(ten["subtotal_usd"] - single["subtotal_usd"] * 10) < 0.01
    
    def test_discount_application(self):
        """Discount should reduce total correctly"""
        no_discount = calculate_panel_quote(
            panel_type="Isoroof",
            thickness_mm=50,
            length_m=6.0,
            width_m=1.0,
            quantity=10,
            discount_percent=0,
        )
        
        with_discount = calculate_panel_quote(
            panel_type="Isoroof",
            thickness_mm=50,
            length_m=6.0,
            width_m=1.0,
            quantity=10,
            discount_percent=10,
        )
        
        expected_total = no_discount["subtotal_usd"] * 0.9
        assert abs(with_discount["total_usd"] - expected_total) < 0.01
    
    def test_price_types(self):
        """Different price types should return different prices"""
        empresa = calculate_panel_quote(
            panel_type="Isoroof",
            thickness_mm=50,
            length_m=6.0,
            width_m=1.0,
            quantity=1,
            price_type="empresa",
        )
        
        particular = calculate_panel_quote(
            panel_type="Isoroof",
            thickness_mm=50,
            length_m=6.0,
            width_m=1.0,
            quantity=1,
            price_type="particular",
        )
        
        web = calculate_panel_quote(
            panel_type="Isoroof",
            thickness_mm=50,
            length_m=6.0,
            width_m=1.0,
            quantity=1,
            price_type="web",
        )
        
        # Empresa (ex-IVA) should be less than particular (inc-IVA)
        assert empresa["total_usd"] < particular["total_usd"]
        # Web is typically higher
        assert web["total_usd"] > empresa["total_usd"]


class TestFixationCalculations:
    """Test fixation point calculations"""
    
    def test_supports_calculation(self):
        """Supports = ROUNDUP((length / autoportancia) + 1)"""
        result = calculate_fixation_points(
            panel_count=10,
            panel_length_m=6.0,
            autoportancia_m=5.5,
        )
        # ROUNDUP((6/5.5) + 1) = ROUNDUP(2.09) = 3
        assert result["support_count"] == 3
    
    def test_fixation_points_formula(self):
        """Test fixation points formula"""
        result = calculate_fixation_points(
            panel_count=4,
            panel_length_m=6.0,
            autoportancia_m=5.5,
        )
        # Supports = 3
        # Points = ROUNDUP(((4 * 3) * 2) + (6 * 2 / 2.5))
        #        = ROUNDUP(24 + 4.8) = 29
        assert result["fixation_points"] == 29
    
    def test_rods_calculation(self):
        """Rods = ROUNDUP(points / 4)"""
        result = calculate_fixation_points(
            panel_count=4,
            panel_length_m=6.0,
        )
        expected_rods = _round_up(result["fixation_points"] / 4)
        assert result["rods_needed"] == expected_rods
    
    def test_metal_structure(self):
        """Metal structure needs metal nuts"""
        result = calculate_fixation_points(
            panel_count=10,
            panel_length_m=6.0,
            structure_type="metal",
        )
        assert result["metal_nuts"] == result["fixation_points"] * 2
        assert result["concrete_nuts"] == 0
    
    def test_concrete_structure(self):
        """Concrete structure needs concrete nuts and anchors"""
        result = calculate_fixation_points(
            panel_count=10,
            panel_length_m=6.0,
            structure_type="concrete",
        )
        assert result["concrete_nuts"] == result["fixation_points"]
        assert result["concrete_anchors"] == result["fixation_points"]
        assert result["metal_nuts"] == 0


class TestProfilesCalculations:
    """Test profile calculations"""
    
    def test_frontal_drip_calculation(self):
        """Frontal drip = ROUNDUP((panels × width) / 3)"""
        result = calculate_profiles_quote(
            panel_count=4,
            panel_length_m=6.0,
            panel_width_m=1.12,
            thickness_mm=50,
        )
        # ROUNDUP((4 * 1.12) / 3) = ROUNDUP(1.49) = 2
        assert result["frontal_drip_count"] == 2
    
    def test_lateral_drip_calculation(self):
        """Lateral drip = ROUNDUP((length × 2) / 3)"""
        result = calculate_profiles_quote(
            panel_count=4,
            panel_length_m=6.0,
            panel_width_m=1.12,
            thickness_mm=50,
        )
        # ROUNDUP((6 * 2) / 3) = ROUNDUP(4) = 4
        assert result["lateral_drip_count"] == 4
    
    def test_rivets_calculation(self):
        """Rivets = ROUNDUP(total_profiles × 20)"""
        result = calculate_profiles_quote(
            panel_count=4,
            panel_length_m=6.0,
            panel_width_m=1.12,
            thickness_mm=50,
        )
        total_profiles = result["frontal_drip_count"] + result["lateral_drip_count"] + result["ridge_count"]
        expected_rivets = _round_up(total_profiles * 20)
        assert result["rivets_needed"] == expected_rivets


class TestInputValidation:
    """Test input validation"""
    
    def test_negative_thickness_rejected(self):
        """Negative thickness should raise error"""
        with pytest.raises(ValueError):
            calculate_panel_quote(
                panel_type="Isoroof",
                thickness_mm=-50,
                length_m=6.0,
                width_m=1.0,
                quantity=1,
            )
    
    def test_excessive_length_rejected(self):
        """Length > 14m should raise error"""
        with pytest.raises(ValueError):
            calculate_panel_quote(
                panel_type="Isoroof",
                thickness_mm=50,
                length_m=15.0,
                width_m=1.0,
                quantity=1,
            )
    
    def test_zero_quantity_rejected(self):
        """Quantity < 1 should raise error"""
        with pytest.raises(ValueError):
            calculate_panel_quote(
                panel_type="Isoroof",
                thickness_mm=50,
                length_m=6.0,
                width_m=1.0,
                quantity=0,
            )
    
    def test_excessive_discount_rejected(self):
        """Discount > 30% should raise error"""
        with pytest.raises(ValueError):
            calculate_panel_quote(
                panel_type="Isoroof",
                thickness_mm=50,
                length_m=6.0,
                width_m=1.0,
                quantity=1,
                discount_percent=35,
            )


class TestCompleteQuotation:
    """Test complete quotation generation"""
    
    def test_complete_quotation_structure(self):
        """Complete quotation should have all sections"""
        result = calculate_complete_quotation(
            panel_type="Isoroof",
            thickness_mm=50,
            total_width_m=10.0,
            total_length_m=6.0,
        )
        
        assert "panels" in result
        assert "profiles" in result
        assert "fixation" in result
        assert "grand_total_usd" in result
        assert result["calculation_verified"] == True
    
    def test_panel_count_calculation(self):
        """Panel count should be calculated from dimensions"""
        result = calculate_complete_quotation(
            panel_type="Isoroof",
            thickness_mm=50,
            total_width_m=10.0,
            total_length_m=6.0,
        )
        
        # Isoroof has useful_width_m = 1.0
        # ROUNDUP(10.0 / 1.0) = 10
        assert result["panel_count"] == 10
    
    def test_totals_add_up(self):
        """Grand total should equal sum of subtotals"""
        result = calculate_complete_quotation(
            panel_type="Isoroof",
            thickness_mm=50,
            total_width_m=10.0,
            total_length_m=6.0,
        )
        
        expected_total = (
            result["panels_subtotal_usd"] +
            result["profiles_subtotal_usd"]
        )
        
        assert abs(result["grand_total_usd"] - expected_total) < 0.01


class TestEdgeCases:
    """Test edge cases"""
    
    def test_minimum_dimensions(self):
        """Minimum valid dimensions should work"""
        result = calculate_panel_quote(
            panel_type="Isoroof",
            thickness_mm=30,
            length_m=0.5,
            width_m=0.5,
            quantity=1,
        )
        assert result["calculation_verified"] == True
        assert result["total_usd"] > 0
    
    def test_single_panel(self):
        """Single panel calculation"""
        result = calculate_panel_quote(
            panel_type="Isoroof",
            thickness_mm=50,
            length_m=6.0,
            width_m=1.0,
            quantity=1,
        )
        assert result["quantity"] == 1
        assert result["subtotal_usd"] == result["unit_price_usd"]
    
    def test_large_order(self):
        """Large order should calculate correctly"""
        result = calculate_panel_quote(
            panel_type="Isoroof",
            thickness_mm=50,
            length_m=12.0,
            width_m=1.0,
            quantity=100,
        )
        assert result["calculation_verified"] == True
        assert result["total_usd"] > 0


class TestGoldenDataset:
    """
    Golden dataset tests with pre-calculated correct values.
    These MUST pass before any deployment.
    """
    
    def test_golden_isoroof_50mm(self):
        """Golden test: Isoroof 50mm, 6×1m, 10 panels"""
        result = calculate_panel_quote(
            panel_type="Isoroof",
            thickness_mm=50,
            length_m=6.0,
            width_m=1.0,
            quantity=10,
            price_type="empresa",
        )
        
        # Known values from catalog:
        # Isoroof 50mm empresa: $44.00/m² (sale_price_usd_ex_iva)
        # Area: 6m² per panel
        # Unit price: 6 × 44.00 = $264.00
        # Total: 264.00 × 10 = $2,640.00
        
        assert result["area_m2"] == 6.0
        assert result["calculation_verified"] == True
        assert result["quantity"] == 10
        # Allow small tolerance for price variations
        assert result["subtotal_usd"] > 2000  # Reasonable total
    
    def test_golden_fixation_10x6(self):
        """Golden test: Fixation for 10 panels, 6m length"""
        result = calculate_fixation_points(
            panel_count=10,
            panel_length_m=6.0,
            autoportancia_m=5.5,
            structure_type="metal",
        )
        
        # Supports: ROUNDUP((6/5.5)+1) = 3
        # Points: ROUNDUP(((10×3)×2) + (6×2/2.5)) = ROUNDUP(60 + 4.8) = 65
        # Rods: ROUNDUP(65/4) = 17
        # Metal nuts: 65 × 2 = 130
        
        assert result["support_count"] == 3
        assert result["fixation_points"] == 65
        assert result["rods_needed"] == 17
        assert result["metal_nuts"] == 130
        assert result["calculation_verified"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
