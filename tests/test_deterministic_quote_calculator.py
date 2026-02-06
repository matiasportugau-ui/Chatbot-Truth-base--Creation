import pytest

from panelin.tools.quotation_calculator import calculate_panel_quote, validate_quotation


class TestDeterministicQuoteCalculator:
    def test_basic_isopanel_quote(self):
        """Test que paneles menores al mínimo se ajustan a longitud mínima."""
        result = calculate_panel_quote(
            panel_type="Isopanel",
            thickness_mm=50,
            length_m=2.0,  # Below minimum of 2.3m
            width_m=1.0,
            quantity=10,
        )
        
        # Should quote for 2.3m panels (minimum length), not 2.0m
        # area: 2.3m², unit: 2.3 * 41.88 = 96.324 -> 96.32
        # subtotal: 96.32 * 10 = 963.20
        line_item = result["line_items"][0]
        assert line_item["area_m2"] == 2.3
        assert line_item["unit_price_usd"] == 96.32
        assert result["subtotal_usd"] == 963.20
        assert result["discount_amount_usd"] == 0.0
        assert result["total_usd"] == 963.20
        assert result["calculation_verified"] is True
        validation = validate_quotation(result)
        assert validation["is_valid"] is True
        
        # Should include note about cutting
        assert "notes" in result
        assert len(result["notes"]) > 0
        assert any("cortar en obra" in note.lower() for note in result["notes"])

    def test_discount_application(self):
        result = calculate_panel_quote(
            panel_type="Isodec",
            thickness_mm=100,
            length_m=3.0,
            width_m=1.2,
            quantity=50,
            discount_percent=10,
        )
        # area: 3.6m², unit: 3.6 * 46.07 = 165.852 -> 165.85
        # subtotal: 165.85 * 50 = 8292.50
        # discount: 10% = 829.25
        # total: 7463.25
        line_item = result["line_items"][0]
        assert line_item["area_m2"] == pytest.approx(3.6)
        assert line_item["unit_price_usd"] == 165.85
        assert result["subtotal_usd"] == 8292.50
        assert result["discount_amount_usd"] == 829.25
        assert result["total_usd"] == 7463.25
        assert result["calculation_verified"] is True
        validation = validate_quotation(result)
        assert validation["is_valid"] is True

    def test_invalid_product_raises(self):
        with pytest.raises(ValueError):
            calculate_panel_quote(
                panel_type="Isopanel",
                thickness_mm=999,
                length_m=2.0,
                width_m=1.0,
                quantity=1,
            )

    def test_invalid_quantity_raises(self):
        with pytest.raises(ValueError):
            calculate_panel_quote(
                panel_type="Isopanel",
                thickness_mm=50,
                length_m=2.0,
                width_m=1.0,
                quantity=0,
            )

