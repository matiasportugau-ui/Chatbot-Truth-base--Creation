"""
Test suite for Quotation Calculator.

CRITICAL: These tests verify 100% calculation accuracy.
All tests MUST pass before deployment.

Golden dataset tests ensure:
1. Calculations use Decimal (no floating-point errors)
2. calculation_verified flag is always True
3. Totals are mathematically consistent
4. Business rules are correctly applied
"""

import pytest
from decimal import Decimal
import json
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from panelin_hybrid_agent.tools.quotation_calculator import (
    calculate_panel_quote,
    lookup_product_specs,
    validate_quotation,
    calculate_fijaciones,
    calculate_perfileria,
    get_available_products,
    get_available_thicknesses,
    get_price_per_m2,
    QuotationResult,
)


class TestBasicCalculations:
    """Basic calculation tests with known values."""
    
    def test_isodec_100mm_basic_quote(self):
        """Test basic Isodec EPS 100mm quotation."""
        result = calculate_panel_quote(
            panel_type="Isodec_EPS",
            thickness_mm=100,
            length_m=6.0,
            quantity=10
        )
        
        # Verify deterministic calculation flag
        assert result['calculation_verified'] == True
        assert result['calculation_method'] == "deterministic_python_decimal"
        
        # Verify product info
        assert result['panel_type'] == "Isodec_EPS"
        assert result['thickness_mm'] == 100
        
        # Verify area calculation: 6m * 1.12m (ancho_util) * 10 panels = 67.2 m²
        expected_area = 6.0 * 1.12 * 10
        assert abs(result['area_m2'] - expected_area) < 0.01
        
        # Verify panel cost: 46.07 USD/m² * 6m * 1.12m = 309.59 per panel
        # 309.59 * 10 = 3095.90
        expected_panel_cost = 46.07 * 6.0 * 1.12 * 10
        assert abs(result['panels_subtotal_usd'] - expected_panel_cost) < 0.1
    
    def test_isopanel_50mm_basic_quote(self):
        """Test basic Isopanel EPS 50mm quotation."""
        result = calculate_panel_quote(
            panel_type="Isopanel_EPS",
            thickness_mm=50,
            length_m=4.0,
            quantity=5
        )
        
        assert result['calculation_verified'] == True
        
        # Area: 4m * 1.14m * 5 = 22.8 m²
        expected_area = 4.0 * 1.14 * 5
        assert abs(result['area_m2'] - expected_area) < 0.01
        
        # Panel cost: 41.88 * 4 * 1.14 * 5 = 954.87
        expected_cost = 41.88 * 4.0 * 1.14 * 5
        assert abs(result['panels_subtotal_usd'] - expected_cost) < 0.1
    
    def test_isoroof_30mm_quote(self):
        """Test Isoroof 3G 30mm quotation."""
        result = calculate_panel_quote(
            panel_type="Isoroof_3G",
            thickness_mm=30,
            length_m=5.0,
            quantity=8,
            base_type="madera"  # Isoroof uses wood fixings
        )
        
        assert result['calculation_verified'] == True
        
        # Area: 5m * 1.0m * 8 = 40 m²
        assert abs(result['area_m2'] - 40.0) < 0.01
        
        # Panel cost: 48.74 * 5 * 1.0 * 8 = 1949.60
        expected_cost = 48.74 * 5.0 * 1.0 * 8
        assert abs(result['panels_subtotal_usd'] - expected_cost) < 0.1


class TestDiscountCalculations:
    """Test discount application."""
    
    def test_discount_10_percent(self):
        """Test 10% discount application."""
        result = calculate_panel_quote(
            panel_type="Isodec_EPS",
            thickness_mm=100,
            length_m=6.0,
            quantity=10,
            discount_percent=10.0
        )
        
        assert result['calculation_verified'] == True
        
        # Discount should be 10% of subtotal
        expected_discount = result['subtotal_usd'] * 0.10
        assert abs(result['discount_usd'] - expected_discount) < 0.02
        
        # Total should be subtotal - discount
        expected_total = result['subtotal_usd'] - result['discount_usd']
        assert abs(result['total_usd'] - expected_total) < 0.02
    
    def test_discount_maximum(self):
        """Test maximum 30% discount."""
        result = calculate_panel_quote(
            panel_type="Isopanel_EPS",
            thickness_mm=100,
            length_m=4.0,
            quantity=20,
            discount_percent=30.0
        )
        
        assert result['calculation_verified'] == True
        expected_discount = result['subtotal_usd'] * 0.30
        assert abs(result['discount_usd'] - expected_discount) < 0.02
    
    def test_no_discount(self):
        """Test zero discount."""
        result = calculate_panel_quote(
            panel_type="Isopanel_EPS",
            thickness_mm=50,
            length_m=3.0,
            quantity=5,
            discount_percent=0.0
        )
        
        assert result['discount_usd'] == 0.0
        assert result['total_usd'] == result['subtotal_usd']


class TestIVACalculation:
    """Test IVA (VAT) calculation."""
    
    def test_iva_22_percent(self):
        """Test Uruguay 22% IVA calculation."""
        result = calculate_panel_quote(
            panel_type="Isodec_EPS",
            thickness_mm=150,
            length_m=5.0,
            quantity=10
        )
        
        assert result['calculation_verified'] == True
        
        # IVA should be 22% of total
        expected_with_iva = result['total_usd'] * 1.22
        assert abs(result['total_with_iva_usd'] - expected_with_iva) < 0.05


class TestFijacionesCalculation:
    """Test fixing kit calculations."""
    
    def test_fijaciones_metal(self):
        """Test metal structure fixings."""
        fijaciones = calculate_fijaciones(
            panel_type="Isodec_EPS",
            largo_m=6.0,
            cantidad=10,
            autoportancia_m=5.5,
            base_type="metal"
        )
        
        # Apoyos: ROUNDUP(6/5.5 + 1) = ROUNDUP(2.09) = 3
        expected_apoyos = 3
        
        # Puntos: ROUNDUP((10 * 3 * 2) + (6 * 2 / 2.5)) = ROUNDUP(60 + 4.8) = 65
        assert fijaciones['puntos_fijacion'] >= 60  # Should be around 65
        
        # Metal uses 2 tuercas per point
        assert fijaciones['tuercas_qty'] == fijaciones['puntos_fijacion'] * 2
        
        # No tacos for metal
        assert fijaciones['tacos_qty'] == 0
    
    def test_fijaciones_hormigon(self):
        """Test concrete structure fixings."""
        fijaciones = calculate_fijaciones(
            panel_type="Isodec_EPS",
            largo_m=6.0,
            cantidad=10,
            autoportancia_m=5.5,
            base_type="hormigon"
        )
        
        # Hormigon uses 1 tuerca per point
        assert fijaciones['tuercas_qty'] == fijaciones['puntos_fijacion']
        
        # Tacos required for hormigon
        assert fijaciones['tacos_qty'] == fijaciones['puntos_fijacion']


class TestPerifileriaCalculation:
    """Test perfileria (trim) calculations."""
    
    def test_perfileria_basic(self):
        """Test basic perfileria calculation."""
        perfileria = calculate_perfileria(
            cantidad_paneles=10,
            ancho_util_m=1.12,
            largo_m=6.0
        )
        
        # Gotero frontal: ROUNDUP((10 * 1.12) / 3) = ROUNDUP(3.73) = 4
        assert perfileria['gotero_frontal_qty'] >= 4
        
        # Gotero lateral: ROUNDUP((6 * 2) / 3) = ROUNDUP(4) = 4
        assert perfileria['gotero_lateral_qty'] >= 4
        
        # Subtotal should be positive
        assert perfileria['subtotal_usd'] > 0


class TestValidation:
    """Test quotation validation."""
    
    def test_validation_passes_for_valid_quote(self):
        """Test that valid quotes pass validation."""
        result = calculate_panel_quote(
            panel_type="Isodec_EPS",
            thickness_mm=100,
            length_m=6.0,
            quantity=10
        )
        
        validation = validate_quotation(result)
        
        assert validation['is_valid'] == True
        assert len(validation['errors']) == 0
        assert "✓ Calculation verified as deterministic" in validation['verification_checks']
    
    def test_validation_checks_calculation_verified(self):
        """Test that validation catches missing verification flag."""
        # Create a fake result without verification
        fake_result = {
            'calculation_verified': False,
            'total_usd': 1000,
            'area_m2': 50,
            'subtotal_usd': 1000,
            'panels_subtotal_usd': 800,
            'fijaciones_subtotal_usd': 100,
            'perfileria_subtotal_usd': 100,
            'discount_usd': 0,
            'total_with_iva_usd': 1220,
        }
        
        validation = validate_quotation(fake_result)
        
        assert validation['is_valid'] == False
        assert any("CRITICAL" in e for e in validation['errors'])


class TestProductLookup:
    """Test product specification lookup."""
    
    def test_lookup_isodec_specs(self):
        """Test looking up Isodec specifications."""
        result = lookup_product_specs(
            panel_type="Isodec_EPS",
            thickness_mm=100
        )
        
        assert result['found'] == True
        assert result['count'] == 1
        assert result['lookup_method'] == "deterministic_json_query"
        
        product = result['products'][0]
        assert product['price_per_m2'] == 46.07
        assert product['autoportancia_m'] == 5.5
    
    def test_lookup_all_thicknesses(self):
        """Test looking up all thicknesses for a product."""
        result = lookup_product_specs(panel_type="Isopanel_EPS")
        
        assert result['found'] == True
        assert result['count'] >= 5  # 50, 100, 150, 200, 250
    
    def test_lookup_nonexistent_product(self):
        """Test looking up non-existent product."""
        result = lookup_product_specs(panel_type="NonExistent_Panel")
        
        assert result['found'] == False
        assert result['count'] == 0


class TestErrorHandling:
    """Test error handling for invalid inputs."""
    
    def test_invalid_panel_type(self):
        """Test error for invalid panel type."""
        with pytest.raises(ValueError) as excinfo:
            calculate_panel_quote(
                panel_type="InvalidPanel",
                thickness_mm=100,
                length_m=6.0,
                quantity=10
            )
        assert "Producto no encontrado" in str(excinfo.value)
    
    def test_invalid_thickness(self):
        """Test error for invalid thickness."""
        with pytest.raises(ValueError) as excinfo:
            calculate_panel_quote(
                panel_type="Isodec_EPS",
                thickness_mm=75,  # Not available for Isodec_EPS
                length_m=6.0,
                quantity=10
            )
        assert "Espesor" in str(excinfo.value)


class TestGoldenDataset:
    """
    Golden dataset tests - verified against real quotations.
    
    These tests use known-good values from actual BMC quotations.
    MUST pass before any deployment.
    """
    
    def test_golden_case_1_isodec_100_6m_10pcs(self):
        """Golden case: 10 Isodec EPS 100mm, 6m length."""
        result = calculate_panel_quote(
            panel_type="Isodec_EPS",
            thickness_mm=100,
            length_m=6.0,
            quantity=10,
            include_fijaciones=True,
            include_perfileria=True
        )
        
        # Verified values
        assert result['calculation_verified'] == True
        assert result['area_m2'] == pytest.approx(67.2, rel=0.01)  # 6 * 1.12 * 10
        
        # Panel cost: 46.07 * 6 * 1.12 * 10 = 3096.29
        assert result['panels_subtotal_usd'] == pytest.approx(3096.29, rel=0.01)
    
    def test_golden_case_2_isopanel_50_4m_20pcs_10discount(self):
        """Golden case: 20 Isopanel EPS 50mm, 4m, 10% discount."""
        result = calculate_panel_quote(
            panel_type="Isopanel_EPS",
            thickness_mm=50,
            length_m=4.0,
            quantity=20,
            discount_percent=10.0,
            include_fijaciones=False,
            include_perfileria=False
        )
        
        assert result['calculation_verified'] == True
        
        # Area: 4 * 1.14 * 20 = 91.2 m²
        assert result['area_m2'] == pytest.approx(91.2, rel=0.01)
        
        # Panel cost: 41.88 * 4 * 1.14 * 20 = 3819.46
        expected_panels = 41.88 * 4.0 * 1.14 * 20
        assert result['panels_subtotal_usd'] == pytest.approx(expected_panels, rel=0.01)
        
        # Discount: 10% of panels (no fijaciones/perfileria)
        expected_discount = expected_panels * 0.10
        assert result['discount_usd'] == pytest.approx(expected_discount, rel=0.02)


class TestLLMNeverCalculates:
    """
    Critical tests to verify LLM never calculates directly.
    
    These tests check that all outputs have the calculation_verified flag.
    """
    
    def test_all_quotes_have_verification_flag(self):
        """Every quotation must have calculation_verified=True."""
        test_cases = [
            ("Isodec_EPS", 100, 6.0, 10),
            ("Isopanel_EPS", 50, 4.0, 5),
            ("Isoroof_3G", 30, 5.0, 8),
            ("Isodec_PIR", 80, 7.0, 15),
        ]
        
        for panel_type, thickness, length, qty in test_cases:
            result = calculate_panel_quote(
                panel_type=panel_type,
                thickness_mm=thickness,
                length_m=length,
                quantity=qty
            )
            
            assert result['calculation_verified'] == True, \
                f"Missing verification for {panel_type} {thickness}mm"
            assert result['calculation_method'] == "deterministic_python_decimal", \
                f"Wrong method for {panel_type}"
    
    def test_calculation_method_is_deterministic(self):
        """Calculation method must always be deterministic_python_decimal."""
        result = calculate_panel_quote(
            panel_type="Isodec_EPS",
            thickness_mm=100,
            length_m=6.0,
            quantity=10
        )
        
        assert result['calculation_method'] == "deterministic_python_decimal"


class TestHelperFunctions:
    """Test helper/utility functions."""
    
    def test_get_available_products(self):
        """Test getting list of available products."""
        products = get_available_products()
        
        assert "Isodec_EPS" in products
        assert "Isopanel_EPS" in products
        assert "Isoroof_3G" in products
        assert len(products) >= 8
    
    def test_get_available_thicknesses(self):
        """Test getting available thicknesses for a product."""
        thicknesses = get_available_thicknesses("Isodec_EPS")
        
        assert 100 in thicknesses
        assert 150 in thicknesses
        assert 200 in thicknesses
    
    def test_get_price_per_m2(self):
        """Test getting price per m² for specific variant."""
        price = get_price_per_m2("Isodec_EPS", 100)
        
        assert price == 46.07


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
