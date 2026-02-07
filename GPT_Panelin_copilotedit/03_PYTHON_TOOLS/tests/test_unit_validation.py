"""
Unit Tests: Validation Functions
=================================

Tests for autoportancia validation and other validation functions.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from quotation_calculator_v3 import validate_autoportancia


class TestAutoportanciaValidation:
    """Tests for validate_autoportancia() function"""
    
    def test_valid_span_well_within_limit(self, mock_bom_rules):
        """Test with span well within safe limit"""
        result = validate_autoportancia("ISODEC_EPS", 100, 4.0)
        
        assert result['is_valid'] is True
        assert result['span_requested_m'] == 4.0
        assert result['span_max_m'] == 5.5
        assert abs(result['span_max_safe_m'] - 4.675) < 0.01
        assert result['excess_pct'] == 0.0
        assert len(result['alternative_thicknesses']) == 0
    
    def test_invalid_span_exceeds_limit(self, mock_bom_rules):
        """Test with span exceeding safe limit"""
        result = validate_autoportancia("ISODEC_EPS", 100, 8.0)
        
        assert result['is_valid'] is False
        assert result['span_requested_m'] == 8.0
        assert result['span_max_m'] == 5.5
        assert result['excess_pct'] > 0
        assert len(result['alternative_thicknesses']) > 0
        assert 250 in result['alternative_thicknesses']
    
    def test_span_at_safe_limit(self, mock_bom_rules):
        """Test with span exactly at safe limit"""
        safe_limit = 5.5 * 0.85  # 4.675m
        result = validate_autoportancia("ISODEC_EPS", 100, safe_limit)
        
        assert result['is_valid'] is True
        assert abs(result['span_max_safe_m'] - 4.675) < 0.01
    
    def test_span_just_above_safe_limit(self, mock_bom_rules):
        """Test with span just above safe limit"""
        result = validate_autoportancia("ISODEC_EPS", 100, 4.7)
        
        assert result['is_valid'] is False
        assert result['excess_pct'] > 0
    
    def test_unknown_thickness(self, mock_bom_rules):
        """Test with thickness not in table"""
        result = validate_autoportancia("ISODEC_EPS", 999, 5.0)
        
        assert result['is_valid'] is True  # Neutral validation
        assert "No autoportancia data" in result['recommendation']
        assert result['span_max_m'] == 0.0
    
    def test_alternative_suggestions(self, mock_bom_rules):
        """Test that alternative thicknesses are suggested correctly"""
        result = validate_autoportancia("ISODEC_EPS", 100, 8.0)
        
        # For 8.0m span, should suggest 250mm (max 10.4m)
        assert 250 in result['alternative_thicknesses']
        assert "Use 250mm thickness" in result['recommendation']
    
    def test_safety_margin_calculation(self, mock_bom_rules):
        """Test that safety margin is correctly applied"""
        result = validate_autoportancia("ISODEC_EPS", 100, 5.0, safety_margin=0.15)
        
        # Absolute max: 5.5m, Safe max with 15% margin: 4.675m
        assert abs(result['span_max_safe_m'] - 4.675) < 0.01
        assert result['span_max_m'] == 5.5
    
    def test_custom_safety_margin(self, mock_bom_rules):
        """Test with custom safety margin"""
        result = validate_autoportancia("ISODEC_EPS", 100, 4.5, safety_margin=0.20)
        
        # With 20% margin: 5.5 × 0.80 = 4.4m safe limit
        assert abs(result['span_max_safe_m'] - 4.4) < 0.01
        assert result['is_valid'] is False  # 4.5 > 4.4


@pytest.mark.parametrize("family,thickness,span,expected_valid", [
    # ISODEC_EPS tests
    ("ISODEC_EPS", 100, 4.0, True),
    ("ISODEC_EPS", 100, 4.675, True),
    ("ISODEC_EPS", 100, 5.0, False),
    ("ISODEC_EPS", 150, 6.0, True),
    ("ISODEC_EPS", 150, 8.0, False),
    ("ISODEC_EPS", 200, 7.5, True),
    ("ISODEC_EPS", 250, 9.0, True),
    
    # ISODEC_PIR tests
    ("ISODEC_PIR", 50, 2.5, True),
    ("ISODEC_PIR", 50, 3.5, False),
    ("ISODEC_PIR", 80, 4.5, True),
    ("ISODEC_PIR", 120, 6.0, True),
    
    # ISOROOF_3G tests
    ("ISOROOF_3G", 30, 2.0, True),
    ("ISOROOF_3G", 30, 3.0, False),
    ("ISOROOF_3G", 50, 2.8, True),
    ("ISOROOF_3G", 80, 3.5, True),
    
    # ISOPANEL_EPS tests
    ("ISOPANEL_EPS", 50, 2.5, True),
    ("ISOPANEL_EPS", 100, 4.5, True),
    ("ISOPANEL_EPS", 150, 6.5, True),
    ("ISOPANEL_EPS", 200, 7.5, True),
])
class TestAutoportanciaParameterized:
    """Parameterized tests for all product families"""
    
    def test_validation_result(self, family, thickness, span, expected_valid):
        """Test validation across all families and thicknesses"""
        result = validate_autoportancia(family, thickness, span)
        assert result['is_valid'] == expected_valid


class TestValidationRecommendations:
    """Tests for validation recommendations"""
    
    def test_recommendation_for_valid_span(self, mock_bom_rules):
        """Test that valid spans get positive recommendation"""
        result = validate_autoportancia("ISODEC_EPS", 100, 4.0)
        
        assert "✓" in result['recommendation'] or "PASSED" in result['recommendation']
    
    def test_recommendation_for_invalid_span(self, mock_bom_rules):
        """Test that invalid spans get warning recommendation"""
        result = validate_autoportancia("ISODEC_EPS", 100, 8.0)
        
        assert "⚠️" in result['recommendation'] or "EXCEEDS" in result['recommendation']
        assert "250mm" in result['recommendation']  # Should suggest alternative
    
    def test_recommendation_includes_metrics(self, mock_bom_rules):
        """Test that recommendations include specific metrics"""
        result = validate_autoportancia("ISODEC_EPS", 100, 4.0)
        
        assert "4.0m" in result['recommendation']
        assert "5.5m" in result['recommendation']  # Absolute max


class TestFamilyNameParsing:
    """Tests for product family name parsing"""
    
    def test_short_family_name(self, mock_bom_rules):
        """Test with short family name (ISODEC_EPS)"""
        result = validate_autoportancia("ISODEC_EPS", 100, 4.0)
        assert result['is_valid'] is True
    
    def test_long_family_name(self, mock_bom_rules):
        """Test with long family name (ISODEC_EPS_100mm)"""
        result = validate_autoportancia("ISODEC_EPS_100mm", 100, 4.0)
        assert result['is_valid'] is True
    
    def test_unknown_family(self, mock_bom_rules):
        """Test with unknown product family"""
        result = validate_autoportancia("UNKNOWN_FAMILY", 100, 4.0)
        
        assert result['is_valid'] is True  # Neutral validation
        assert "No autoportancia data" in result['recommendation']


class TestExcessCalculation:
    """Tests for excess percentage calculation"""
    
    def test_no_excess_when_valid(self, mock_bom_rules):
        """Test that excess is 0 when span is valid"""
        result = validate_autoportancia("ISODEC_EPS", 100, 4.0)
        assert result['excess_pct'] == 0.0
    
    def test_excess_calculation_when_invalid(self, mock_bom_rules):
        """Test excess percentage calculation"""
        result = validate_autoportancia("ISODEC_EPS", 100, 8.0)
        
        # Safe limit: 4.675m, Requested: 8.0m
        # Excess: (8.0 - 4.675) / 4.675 × 100 ≈ 71.1%
        assert result['excess_pct'] > 70
        assert result['excess_pct'] < 72


@pytest.mark.unit
class TestValidationEdgeCases:
    """Test edge cases for validation"""
    
    def test_zero_span(self, mock_bom_rules):
        """Test with zero span (should still validate)"""
        result = validate_autoportancia("ISODEC_EPS", 100, 0.0)
        assert result['is_valid'] is True  # Zero is within limit
    
    def test_negative_span(self, mock_bom_rules):
        """Test with negative span (should still validate)"""
        result = validate_autoportancia("ISODEC_EPS", 100, -1.0)
        assert result['is_valid'] is True  # Negative is within limit
    
    def test_very_large_span(self, mock_bom_rules):
        """Test with very large span"""
        result = validate_autoportancia("ISODEC_EPS", 100, 100.0)
        
        assert result['is_valid'] is False
        assert result['excess_pct'] > 1000  # Massive excess


class TestAlternativeThicknesses:
    """Tests for alternative thickness suggestions"""
    
    def test_suggests_next_thickness(self, mock_bom_rules):
        """Test that next working thickness is suggested"""
        result = validate_autoportancia("ISODEC_EPS", 100, 6.0)
        
        # For 6.0m span:
        # - 100mm: max 5.5m (safe 4.675m) ✗
        # - 150mm: max 7.5m (safe 6.375m) ✓
        assert 150 in result['alternative_thicknesses']
    
    def test_multiple_alternatives_sorted(self, mock_bom_rules):
        """Test that alternatives are sorted by thickness"""
        result = validate_autoportancia("ISODEC_EPS", 100, 8.0)
        
        alts = result['alternative_thicknesses']
        assert alts == sorted(alts)  # Should be sorted
    
    def test_no_alternatives_when_valid(self, mock_bom_rules):
        """Test that no alternatives suggested when span is valid"""
        result = validate_autoportancia("ISODEC_EPS", 100, 4.0)
        assert len(result['alternative_thicknesses']) == 0
