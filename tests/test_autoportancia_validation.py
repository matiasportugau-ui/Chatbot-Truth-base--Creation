"""
Tests for validate_autoportancia function with safety_margin parameter.

Tests the V3.1 feature where safety_margin defaults to 0.0 for exact
technical specification validation.
"""
import pytest
from panelin.tools.bom_calculator import validate_autoportancia


class TestAutoportanciaValidation:
    """Test suite for autoportancia validation with safety margin."""

    def test_default_safety_margin_is_zero(self):
        """Test that default safety_margin is 0.0 (exact specs)."""
        result = validate_autoportancia(
            espesor_mm=100,
            luz_m=5.5,
            producto_base='ISODEC_EPS',
        )
        assert result['cumple'] is True
        assert result['autoportancia_m'] == 5.5
        assert '100.0% of rated capacity' in result['recomendacion']

    def test_span_at_exact_technical_limit_passes(self):
        """Test that a span equal to technical spec passes with default margin."""
        result = validate_autoportancia(
            espesor_mm=100,
            luz_m=5.5,
            producto_base='ISODEC_EPS',
            safety_margin=0.0,
        )
        assert result['cumple'] is True
        assert result['luz_m'] == 5.5
        assert result['autoportancia_m'] == 5.5

    def test_span_exceeding_technical_limit_fails(self):
        """Test that a span exceeding technical spec fails."""
        result = validate_autoportancia(
            espesor_mm=100,
            luz_m=5.6,
            producto_base='ISODEC_EPS',
            safety_margin=0.0,
        )
        assert result['cumple'] is False
        assert 'NO cubre' in result['recomendacion']
        assert 'technical specifications' in result['recomendacion']

    def test_with_15_percent_safety_margin(self):
        """Test that 15% safety margin reduces allowable span."""
        # With 15% margin, 5.5m becomes 4.675m max safe span
        result = validate_autoportancia(
            espesor_mm=100,
            luz_m=5.0,
            producto_base='ISODEC_EPS',
            safety_margin=0.15,
        )
        # 5.0m exceeds 4.675m safe limit
        assert result['cumple'] is False
        assert result['autoportancia_m'] == 5.5  # Technical spec unchanged

    def test_with_15_percent_safety_margin_passes_smaller_span(self):
        """Test that smaller spans still pass with 15% safety margin."""
        result = validate_autoportancia(
            espesor_mm=100,
            luz_m=4.5,
            producto_base='ISODEC_EPS',
            safety_margin=0.15,
        )
        # 4.5m is within 4.675m safe limit (5.5 * 0.85)
        assert result['cumple'] is True

    def test_recommendation_message_format_on_success(self):
        """Test that success message includes technical limit and capacity usage."""
        result = validate_autoportancia(
            espesor_mm=100,
            luz_m=5.0,
            producto_base='ISODEC_EPS',
            safety_margin=0.0,
        )
        assert result['cumple'] is True
        assert '✓ Span validation PASSED' in result['recomendacion']
        assert 'technical limit' in result['recomendacion']
        assert 'rated capacity' in result['recomendacion']

    def test_recommendation_message_format_on_failure(self):
        """Test that failure message references technical specifications."""
        result = validate_autoportancia(
            espesor_mm=100,
            luz_m=6.0,
            producto_base='ISODEC_EPS',
            safety_margin=0.0,
        )
        assert result['cumple'] is False
        assert 'technical specifications' in result['recomendacion']
        assert 'maximum' in result['recomendacion']

    def test_multiple_thicknesses_isodec_eps(self):
        """Test validation across multiple thicknesses for ISODEC_EPS."""
        test_cases = [
            (100, 5.5, True),   # At limit
            (100, 5.4, True),   # Below limit
            (100, 5.6, False),  # Above limit
            (150, 7.5, True),   # 150mm at limit
            (150, 7.6, False),  # 150mm above limit
        ]
        
        for espesor, luz, expected_cumple in test_cases:
            result = validate_autoportancia(
                espesor_mm=espesor,
                luz_m=luz,
                producto_base='ISODEC_EPS',
                safety_margin=0.0,
            )
            assert result['cumple'] == expected_cumple, \
                f"Failed for espesor={espesor}, luz={luz}: expected cumple={expected_cumple}"

    def test_product_not_found_returns_appropriate_message(self):
        """Test that unknown product returns appropriate error message."""
        result = validate_autoportancia(
            espesor_mm=100,
            luz_m=5.0,
            producto_base='NONEXISTENT_PRODUCT',
            safety_margin=0.0,
        )
        assert result['cumple'] is False
        assert result['autoportancia_m'] == 0
        assert 'No se encontró' in result['recomendacion']

    def test_safety_margin_parameter_is_optional(self):
        """Test that safety_margin parameter is optional."""
        # Should work without safety_margin parameter
        result = validate_autoportancia(
            espesor_mm=100,
            luz_m=5.0,
            producto_base='ISODEC_EPS',
        )
        assert 'cumple' in result
        assert 'autoportancia_m' in result
        assert 'recomendacion' in result
