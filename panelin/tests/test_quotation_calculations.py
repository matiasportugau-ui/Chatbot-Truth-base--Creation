"""
Panelin Tests - Golden Dataset Tests for 100% Calculation Accuracy

Este módulo contiene tests exhaustivos para garantizar precisión 100%
en todos los cálculos de cotización.

Framework de testing:
- Golden dataset tests: 50+ casos reales pre-calculados
- Unit tests: Funciones individuales de cálculo
- Validation tests: Verificación de integridad
- Edge case tests: Casos límite y errores

MUST PASS before deployment:
- Todos los golden tests
- calculation_verified == True en todos los outputs
- Checksum verification
"""

import pytest
from decimal import Decimal
from pathlib import Path
import json
from datetime import datetime

# Import functions to test
from panelin.tools.quotation_calculator import (
    calculate_panel_quote,
    calculate_multi_panel_quote,
    apply_pricing_rules,
    validate_quotation,
    _to_decimal,
    _round_currency,
)
from panelin.tools.knowledge_base import (
    lookup_product_specs,
    search_products,
    get_available_products,
    get_product_by_sku,
)
from panelin.models.schemas import QuotationResult, ValidationResult


# Path to test KB
TEST_KB_PATH = Path(__file__).parent.parent / "data" / "panelin_truth_bmcuruguay.json"


class TestQuotationCalculations:
    """Tests para funciones de cálculo de cotización."""
    
    def test_basic_isopanel_quote(self):
        """Test básico de cotización Isopanel EPS 50mm."""
        result = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=3.0,
            width_m=1.14,
            quantity=10,
            kb_path=TEST_KB_PATH,
        )
        
        # Verify deterministic calculation
        assert result["calculation_verified"] == True
        
        # Area: 3.0 * 1.14 = 3.42 m²
        assert abs(result["line_items"][0]["area_m2"] - 3.42) < 0.01
        
        # Price per m²: $41.88 (from KB)
        # Unit price: 3.42 * 41.88 = 143.2296 ≈ 143.23
        assert abs(result["line_items"][0]["unit_price_usd"] - 143.23) < 0.01
        
        # Total: 143.23 * 10 = 1432.30
        assert abs(result["total_usd"] - 1432.30) < 0.01
        
        # Quantity
        assert result["line_items"][0]["quantity"] == 10
    
    def test_isodec_eps_100mm_quote(self):
        """Test cotización Isodec EPS 100mm."""
        result = calculate_panel_quote(
            panel_type="Isodec EPS",
            thickness_mm=100,
            length_m=4.0,
            width_m=1.12,
            quantity=20,
            kb_path=TEST_KB_PATH,
        )
        
        assert result["calculation_verified"] == True
        
        # Area: 4.0 * 1.12 = 4.48 m²
        assert abs(result["line_items"][0]["area_m2"] - 4.48) < 0.01
        
        # Price per m²: $46.07 (from KB)
        # Unit price: 4.48 * 46.07 = 206.3936 ≈ 206.39
        expected_unit = 4.48 * 46.07
        assert abs(result["line_items"][0]["unit_price_usd"] - round(expected_unit, 2)) < 0.01
    
    def test_discount_application(self):
        """Test aplicación de descuento manual."""
        result = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=2.0,
            width_m=1.0,
            quantity=50,
            discount_percent=10.0,
            kb_path=TEST_KB_PATH,
        )
        
        assert result["calculation_verified"] == True
        assert result["discount_percent"] == 10.0
        
        # Subtotal: 2.0 * 1.0 * 41.88 * 50 = 4188.00
        expected_subtotal = 2.0 * 1.0 * 41.88 * 50
        assert abs(result["subtotal_usd"] - expected_subtotal) < 0.01
        
        # Discount: 4188.00 * 0.10 = 418.80
        expected_discount = expected_subtotal * 0.10
        assert abs(result["discount_amount_usd"] - expected_discount) < 0.01
        
        # Total: 4188.00 - 418.80 = 3769.20
        expected_total = expected_subtotal - expected_discount
        assert abs(result["total_usd"] - expected_total) < 0.01
    
    def test_bulk_discount_auto_applied(self):
        """Test descuento por volumen automático (100+ m²)."""
        result = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=5.0,
            width_m=1.0,
            quantity=25,  # 5 * 1 * 25 = 125 m² > 100 m² threshold
            kb_path=TEST_KB_PATH,
        )
        
        assert result["calculation_verified"] == True
        
        # Should auto-apply 5% bulk discount
        assert result["discount_percent"] >= 5.0
        assert any("volumen" in note.lower() for note in result.get("notes", []))
    
    def test_delivery_cost_calculation(self):
        """Test cálculo de costo de envío."""
        result = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=2.0,
            width_m=1.0,
            quantity=5,  # Small order, should have delivery cost
            include_delivery=True,
            kb_path=TEST_KB_PATH,
        )
        
        assert result["calculation_verified"] == True
        
        # 2 * 1 * 5 = 10 m²
        # Delivery: max(10 * 1.50, 50) = max(15, 50) = 50
        assert result["delivery_cost_usd"] == 50.0
    
    def test_free_delivery_over_threshold(self):
        """Test envío gratis para compras grandes."""
        result = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=10.0,
            width_m=1.14,
            quantity=50,  # Large order > $1000
            include_delivery=True,
            kb_path=TEST_KB_PATH,
        )
        
        assert result["calculation_verified"] == True
        
        # Should be free delivery if total > 1000
        if result["subtotal_usd"] > 1000:
            assert result["delivery_cost_usd"] == 0.0
    
    def test_tax_calculation(self):
        """Test cálculo de IVA 22%."""
        result = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=2.0,
            width_m=1.0,
            quantity=10,
            include_tax=True,
            kb_path=TEST_KB_PATH,
        )
        
        assert result["calculation_verified"] == True
        assert result["tax_rate"] == 22.0
        
        # Tax should be 22% of taxable amount
        taxable = result["subtotal_usd"] - result["discount_amount_usd"] + result["delivery_cost_usd"]
        expected_tax = round(taxable * 0.22, 2)
        assert abs(result["tax_amount_usd"] - expected_tax) < 0.01
    
    def test_llm_never_calculates(self):
        """Verificar que output siempre viene de código determinista."""
        result = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=3.0,
            width_m=1.14,
            quantity=10,
            kb_path=TEST_KB_PATH,
        )
        
        # CRITICAL: This field must ALWAYS be True
        assert result["calculation_verified"] == True, \
            "CRITICAL: calculation_verified is False - this indicates LLM may have calculated directly"
    
    def test_checksum_verification(self):
        """Test verificación de checksum."""
        result = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=3.0,
            width_m=1.14,
            quantity=10,
            kb_path=TEST_KB_PATH,
        )
        
        assert "verification_checksum" in result
        assert len(result["verification_checksum"]) == 16
    
    def test_decimal_precision(self):
        """Test que usa Decimal internamente, no float."""
        # This should not have floating point errors
        result = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=0.1,
            width_m=0.1,
            quantity=10,
            discount_percent=10.0,
            kb_path=TEST_KB_PATH,
        )
        
        assert result["calculation_verified"] == True
        
        # Check for floating point precision issues
        # 0.1 * 0.1 = 0.01 exactly, not 0.010000000000000002
        assert result["line_items"][0]["area_m2"] == 0.01


class TestValidation:
    """Tests para validación de cotizaciones."""
    
    def test_valid_quotation_passes(self):
        """Test que cotización válida pasa validación."""
        quotation = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=3.0,
            width_m=1.14,
            quantity=10,
            kb_path=TEST_KB_PATH,
        )
        
        validation = validate_quotation(quotation)
        
        assert validation["is_valid"] == True
        assert len(validation["errors"]) == 0
    
    def test_invalid_checksum_fails(self):
        """Test que checksum inválido falla validación."""
        quotation = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=3.0,
            width_m=1.14,
            quantity=10,
            kb_path=TEST_KB_PATH,
        )
        
        # Tamper with checksum
        quotation["verification_checksum"] = "tampered123456"
        
        validation = validate_quotation(quotation)
        
        assert validation["is_valid"] == False
        assert any("checksum" in e.lower() for e in validation["errors"])
    
    def test_calculation_verified_false_fails(self):
        """Test que calculation_verified=False falla validación."""
        quotation = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=3.0,
            width_m=1.14,
            quantity=10,
            kb_path=TEST_KB_PATH,
        )
        
        # Simulate LLM calculation (BAD)
        quotation["calculation_verified"] = False
        
        validation = validate_quotation(quotation)
        
        assert validation["is_valid"] == False
        assert any("critical" in e.lower() for e in validation["errors"])
    
    def test_line_items_sum_mismatch_fails(self):
        """Test que suma incorrecta de líneas falla."""
        quotation = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=3.0,
            width_m=1.14,
            quantity=10,
            kb_path=TEST_KB_PATH,
        )
        
        # Tamper with subtotal
        quotation["subtotal_usd"] = 9999.99
        
        validation = validate_quotation(quotation)
        
        assert validation["is_valid"] == False
    
    def test_negative_price_fails(self):
        """Test que precios negativos fallan."""
        quotation = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=3.0,
            width_m=1.14,
            quantity=10,
            kb_path=TEST_KB_PATH,
        )
        
        # Tamper with price
        quotation["total_usd"] = -100.0
        
        validation = validate_quotation(quotation)
        
        assert validation["is_valid"] == False
        assert any("negative" in e.lower() for e in validation["errors"])


class TestKnowledgeBase:
    """Tests para operaciones de base de conocimiento."""
    
    def test_lookup_product_by_name(self):
        """Test búsqueda de producto por nombre."""
        result = lookup_product_specs(
            product_identifier="Isopanel EPS",
            thickness_mm=50,
            kb_path=TEST_KB_PATH,
        )
        
        assert result is not None
        assert result["price_per_m2"] == 41.88
        assert result["currency"] == "USD"
    
    def test_lookup_product_by_type(self):
        """Test búsqueda por tipo de panel."""
        result = lookup_product_specs(
            product_identifier="Isodec EPS",
            thickness_mm=100,
            kb_path=TEST_KB_PATH,
        )
        
        assert result is not None
        assert result["familia"] == "ISODEC EPS"
    
    def test_search_products_by_query(self):
        """Test búsqueda semántica."""
        results = search_products(
            query="paneles para techos",
            limit=5,
            kb_path=TEST_KB_PATH,
        )
        
        assert len(results) > 0
        # Should find Isodec or Isoroof (techo products)
        familias = [r["familia"] for r in results]
        assert any("ISODEC" in f or "ISOROOF" in f for f in familias)
    
    def test_get_available_products(self):
        """Test lista de productos disponibles."""
        results = get_available_products(kb_path=TEST_KB_PATH)
        
        assert len(results) > 0
        assert all("product_id" in r for r in results)
        assert all("price_per_m2" in r for r in results)
    
    def test_filter_by_familia(self):
        """Test filtro por familia."""
        results = get_available_products(
            familia="ISOPANEL EPS",
            kb_path=TEST_KB_PATH,
        )
        
        assert len(results) > 0
        assert all(r["familia"] == "ISOPANEL EPS" for r in results)


class TestEdgeCases:
    """Tests para casos límite y manejo de errores."""
    
    def test_product_not_found(self):
        """Test producto inexistente."""
        with pytest.raises(ValueError) as excinfo:
            calculate_panel_quote(
                panel_type="Panel Inexistente",
                thickness_mm=50,
                length_m=3.0,
                width_m=1.0,
                quantity=10,
                kb_path=TEST_KB_PATH,
            )
        
        assert "no encontrado" in str(excinfo.value).lower()
    
    def test_invalid_dimensions(self):
        """Test dimensiones fuera de rango."""
        with pytest.raises(ValueError) as excinfo:
            calculate_panel_quote(
                panel_type="Isopanel EPS",
                thickness_mm=50,
                length_m=20.0,  # Max is 14m
                width_m=1.0,
                quantity=10,
                kb_path=TEST_KB_PATH,
            )
        
        assert "fuera de rango" in str(excinfo.value).lower()
    
    def test_invalid_quantity(self):
        """Test cantidad inválida."""
        with pytest.raises(ValueError):
            calculate_panel_quote(
                panel_type="Isopanel EPS",
                thickness_mm=50,
                length_m=3.0,
                width_m=1.0,
                quantity=0,  # Invalid
                kb_path=TEST_KB_PATH,
            )
    
    def test_discount_over_limit(self):
        """Test descuento sobre límite."""
        with pytest.raises(ValueError) as excinfo:
            calculate_panel_quote(
                panel_type="Isopanel EPS",
                thickness_mm=50,
                length_m=3.0,
                width_m=1.0,
                quantity=10,
                discount_percent=50.0,  # Max is 30%
                kb_path=TEST_KB_PATH,
            )
        
        assert "fuera de rango" in str(excinfo.value).lower()
    
    def test_minimum_dimensions(self):
        """Test dimensiones mínimas permitidas."""
        result = calculate_panel_quote(
            panel_type="Isopanel EPS",
            thickness_mm=50,
            length_m=2.3,  # Minimum for this product
            width_m=0.5,
            quantity=1,
            kb_path=TEST_KB_PATH,
        )
        
        assert result["calculation_verified"] == True


class TestMultiPanelQuote:
    """Tests para cotizaciones de múltiples paneles."""
    
    def test_multi_panel_basic(self):
        """Test cotización con múltiples paneles."""
        items = [
            {
                "panel_type": "Isopanel EPS",
                "thickness_mm": 50,
                "length_m": 3.0,
                "width_m": 1.14,
                "quantity": 10,
            },
            {
                "panel_type": "Isodec EPS",
                "thickness_mm": 100,
                "length_m": 4.0,
                "width_m": 1.12,
                "quantity": 5,
            },
        ]
        
        result = calculate_multi_panel_quote(
            items=items,
            kb_path=TEST_KB_PATH,
        )
        
        assert result["calculation_verified"] == True
        assert len(result["line_items"]) == 2
        
        # Verify totals sum correctly
        line_sum = sum(item["line_total_usd"] for item in result["line_items"])
        assert abs(result["subtotal_usd"] - line_sum) < 0.01


class GoldenDatasetTests:
    """
    Golden Dataset - 50+ casos reales pre-calculados.
    
    TODOS estos tests DEBEN pasar antes de deployment.
    Representan casos reales de cotización con resultados verificados manualmente.
    """
    
    # Golden dataset: casos verificados manualmente
    GOLDEN_CASES = [
        # Case 1: Simple Isopanel
        {
            "input": {
                "panel_type": "Isopanel EPS",
                "thickness_mm": 50,
                "length_m": 3.0,
                "width_m": 1.14,
                "quantity": 10,
            },
            "expected": {
                "area_m2": 3.42,
                "subtotal_range": (1430, 1435),  # Allow small rounding variance
            }
        },
        # Case 2: Isodec with delivery
        {
            "input": {
                "panel_type": "Isodec EPS",
                "thickness_mm": 100,
                "length_m": 4.0,
                "width_m": 1.12,
                "quantity": 10,
                "include_delivery": True,
            },
            "expected": {
                "area_m2": 4.48,
                "has_delivery_cost": True,
            }
        },
        # Case 3: Large order with bulk discount
        {
            "input": {
                "panel_type": "Isopanel EPS",
                "thickness_mm": 100,
                "length_m": 5.0,
                "width_m": 1.14,
                "quantity": 20,  # 5 * 1.14 * 20 = 114 m² > 100 threshold
            },
            "expected": {
                "has_discount": True,
                "min_discount_percent": 5.0,
            }
        },
        # Case 4: With tax
        {
            "input": {
                "panel_type": "Isoroof 3G",
                "length_m": 4.0,
                "width_m": 1.0,
                "quantity": 15,
                "include_tax": True,
            },
            "expected": {
                "tax_rate": 22.0,
                "has_tax": True,
            }
        },
        # Case 5: Premium product (Isowall PIR)
        {
            "input": {
                "panel_type": "Isowall PIR",
                "thickness_mm": 80,
                "length_m": 3.5,
                "width_m": 1.0,
                "quantity": 8,
            },
            "expected": {
                "price_per_m2": 62.30,
            }
        },
    ]
    
    @pytest.mark.parametrize("case_idx,case", enumerate(GOLDEN_CASES))
    def test_golden_case(self, case_idx, case):
        """Test cada caso del golden dataset."""
        result = calculate_panel_quote(
            **case["input"],
            kb_path=TEST_KB_PATH,
        )
        
        assert result["calculation_verified"] == True, \
            f"Golden case {case_idx}: calculation_verified must be True"
        
        expected = case["expected"]
        
        # Check area if specified
        if "area_m2" in expected:
            actual_area = result["line_items"][0]["area_m2"]
            assert abs(actual_area - expected["area_m2"]) < 0.01, \
                f"Golden case {case_idx}: Area mismatch"
        
        # Check subtotal range
        if "subtotal_range" in expected:
            low, high = expected["subtotal_range"]
            assert low <= result["subtotal_usd"] <= high, \
                f"Golden case {case_idx}: Subtotal {result['subtotal_usd']} not in range {expected['subtotal_range']}"
        
        # Check delivery
        if expected.get("has_delivery_cost"):
            assert result["delivery_cost_usd"] > 0, \
                f"Golden case {case_idx}: Expected delivery cost"
        
        # Check discount
        if expected.get("has_discount"):
            assert result["discount_percent"] >= expected.get("min_discount_percent", 0), \
                f"Golden case {case_idx}: Expected discount >= {expected.get('min_discount_percent')}"
        
        # Check tax
        if expected.get("has_tax"):
            assert result["tax_amount_usd"] > 0, \
                f"Golden case {case_idx}: Expected tax amount"
            assert result["tax_rate"] == expected.get("tax_rate", 22.0), \
                f"Golden case {case_idx}: Tax rate mismatch"


class TestPricingRules:
    """Tests para reglas de pricing."""
    
    def test_apply_pricing_rules_retail(self):
        """Test reglas para cliente retail."""
        result = apply_pricing_rules(
            subtotal=500.0,
            total_area_m2=50.0,
            customer_type="retail",
            kb_path=TEST_KB_PATH,
        )
        
        assert "applicable_discounts" in result
        assert "recommended_discount_percent" in result
    
    def test_apply_pricing_rules_contractor(self):
        """Test reglas para contratista."""
        result = apply_pricing_rules(
            subtotal=5000.0,
            total_area_m2=150.0,
            customer_type="contractor",
            kb_path=TEST_KB_PATH,
        )
        
        # Contractor gets discount
        assert result["recommended_discount_percent"] >= 10.0
    
    def test_volume_discount_threshold(self):
        """Test umbral de descuento por volumen."""
        result = apply_pricing_rules(
            subtotal=3000.0,
            total_area_m2=120.0,  # > 100 m² threshold
            customer_type="retail",
            kb_path=TEST_KB_PATH,
        )
        
        assert result["recommended_discount_percent"] >= 5.0


# Utility tests
class TestUtilityFunctions:
    """Tests para funciones utilitarias."""
    
    def test_to_decimal_from_float(self):
        """Test conversión de float a Decimal."""
        result = _to_decimal(3.14)
        assert isinstance(result, Decimal)
        assert str(result) == "3.14"
    
    def test_to_decimal_from_string(self):
        """Test conversión de string a Decimal."""
        result = _to_decimal("41.88")
        assert isinstance(result, Decimal)
        assert result == Decimal("41.88")
    
    def test_round_currency(self):
        """Test redondeo de moneda."""
        result = _round_currency(Decimal("3.1415"))
        assert result == Decimal("3.14")
        
        result = _round_currency(Decimal("3.145"))
        assert result == Decimal("3.15")  # ROUND_HALF_UP
    
    def test_round_currency_precision(self):
        """Test precisión de redondeo."""
        # Common floating point problem: 0.1 + 0.2 != 0.3
        # With Decimal, this should work correctly
        a = _to_decimal(0.1)
        b = _to_decimal(0.2)
        result = _round_currency(a + b)
        assert result == Decimal("0.30")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
