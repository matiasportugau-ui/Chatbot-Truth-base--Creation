import pytest

from panelin.tools.quotation_calculator import calculate_panel_quote


def test_basic_isopanel_quote():
    result = calculate_panel_quote(
        panel_type="Isopanel",
        thickness_mm=50,
        length_m=2.0,
        width_m=1.0,
        quantity=10,
    )
    assert result["area_m2"] == 2.0
    assert result["unit_price_usd"] == 45.0
    assert result["subtotal_usd"] == 450.0
    assert result["total_usd"] == 450.0  # 2m² × $22.50 × 10
    assert result["calculation_verified"] is True


def test_discount_application():
    result = calculate_panel_quote(
        panel_type="Isodec",
        thickness_mm=75,
        length_m=3.0,
        width_m=1.2,
        quantity=50,
        discount_percent=10.0,
    )
    assert abs(result["subtotal_usd"] - 5040.0) < 0.01
    assert abs(result["discount_usd"] - 504.0) < 0.01
    assert abs(result["total_usd"] - 4536.0) < 0.01
    assert result["calculation_verified"] is True


def test_llm_never_calculates_flag_is_enforced():
    result = calculate_panel_quote(
        panel_type="Isoroof",
        thickness_mm=50,
        length_m=3.5,
        width_m=1.0,
        quantity=1,
    )
    assert result["calculation_verified"] is True


def test_invalid_discount_rejected():
    with pytest.raises(ValueError):
        calculate_panel_quote(
            panel_type="Isopanel",
            thickness_mm=50,
            length_m=2.0,
            width_m=1.0,
            quantity=1,
            discount_percent=99,
        )

