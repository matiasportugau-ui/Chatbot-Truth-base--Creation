import pytest

from panelin.tools.quotation_calculator import calculate_panel_quote, validate_quotation


class TestDeterministicQuoteCalculator:
    def test_basic_isopanel_quote(self):
        result = calculate_panel_quote(
            panel_type="Isopanel",
            thickness_mm=50,
            length_m=2.5,
            width_m=1.0,
            quantity=10,
        )
        # area: 2.5m², unit: 2.5 * 41.88 = 104.70, subtotal: 1047.00
        assert result["line_items"][0]["area_m2"] == 2.5
        assert result["line_items"][0]["unit_price_usd"] == 104.70
        assert result["subtotal_usd"] == 1047.00
        assert result["discount_amount_usd"] == 0.0
        assert result["total_usd"] == 1047.00
        assert result["calculation_verified"] is True
        assert validate_quotation(result)["is_valid"] is True

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
        assert result["line_items"][0]["area_m2"] == pytest.approx(3.6)
        assert result["line_items"][0]["unit_price_usd"] == 165.85
        assert result["subtotal_usd"] == 8292.50
        assert result["discount_amount_usd"] == 829.25
        assert result["total_usd"] == 7463.25
        assert result["calculation_verified"] is True
        assert validate_quotation(result)["is_valid"] is True

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

