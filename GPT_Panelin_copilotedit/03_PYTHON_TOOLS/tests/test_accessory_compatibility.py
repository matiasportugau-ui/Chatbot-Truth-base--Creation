"""
Unit Tests: Accessory System Compatibility Selection
=====================================================

Tests for find_accessory() system-compatible selection logic
in calculate_accessories_pricing(). Validates that the sistema
parameter is used to select the correct accessory SKU based on
the compatibilidad field in the catalog.

Addresses issue #165: Use system/compatibility when selecting accessory SKUs.
"""

import pytest
from decimal import Decimal
from unittest.mock import patch
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from quotation_calculator_v3 import (
    calculate_accessories_pricing,
    _SISTEMA_TO_COMPAT,
)


@pytest.fixture
def mock_catalog():
    """Mock accessories catalog with items having different compatibilidad."""
    return {
        "accesorios": [
            {
                "sku": "UNI-001",
                "name": "Gotero Frontal Universal",
                "tipo": "gotero_frontal",
                "precio_unit_iva_inc": 5.00,
                "compatibilidad": ["UNIVERSAL"],
            },
            {
                "sku": "ISO-001",
                "name": "Gotero Frontal ISODEC",
                "tipo": "gotero_frontal",
                "precio_unit_iva_inc": 7.50,
                "compatibilidad": ["ISODEC"],
            },
            {
                "sku": "IRF-001",
                "name": "Gotero Frontal ISOROOF",
                "tipo": "gotero_frontal",
                "precio_unit_iva_inc": 8.00,
                "compatibilidad": ["ISOROOF"],
            },
            {
                "sku": "UNI-002",
                "name": "Gotero Lateral Universal",
                "tipo": "gotero_lateral",
                "precio_unit_iva_inc": 4.00,
                "compatibilidad": ["UNIVERSAL"],
            },
            {
                "sku": "SIL-001",
                "name": "Silicona General",
                "tipo": "silicona",
                "precio_unit_iva_inc": 3.00,
                "compatibilidad": ["UNIVERSAL"],
            },
            {
                "sku": "VAR-001",
                "name": "Varilla General",
                "tipo": "varilla",
                "precio_unit_iva_inc": 2.00,
                "compatibilidad": ["UNIVERSAL"],
            },
        ],
        "indices": {
            "by_tipo": {
                "gotero_frontal": [0, 1, 2],
                "gotero_lateral": [3],
                "silicona": [4],
                "varilla": [5],
            }
        },
    }


@pytest.fixture
def sample_accessories_quantities():
    """Minimal accessories quantities for testing."""
    return {
        "front_drip_edge_units": 2,
        "lateral_drip_edge_units": 0,
        "silicone_tubes": 0,
        "rod_quantity": 0,
    }


class TestSistemaToCompat:
    """Tests for the _SISTEMA_TO_COMPAT mapping."""

    def test_isodec_eps_maps_to_isodec(self):
        assert _SISTEMA_TO_COMPAT["techo_isodec_eps"] == "ISODEC"

    def test_isodec_pir_maps_to_isodec(self):
        assert _SISTEMA_TO_COMPAT["techo_isodec_pir"] == "ISODEC"

    def test_isoroof_maps_to_isoroof(self):
        assert _SISTEMA_TO_COMPAT["techo_isoroof_3g"] == "ISOROOF"

    def test_isopanel_maps_to_isopanel(self):
        assert _SISTEMA_TO_COMPAT["pared_isopanel_eps"] == "ISOPANEL"

    def test_isowall_maps_to_isowall(self):
        assert _SISTEMA_TO_COMPAT["pared_isowall_pir"] == "ISOWALL"

    def test_isofrig_maps_to_isofrig(self):
        assert _SISTEMA_TO_COMPAT["pared_isofrig_pir"] == "ISOFRIG"

    def test_unknown_sistema_returns_empty(self):
        assert _SISTEMA_TO_COMPAT.get("unknown_system", "") == ""


class TestFindAccessoryCompatibility:
    """Tests that find_accessory selects the correct SKU based on sistema."""

    def test_selects_isodec_specific_accessory(self, mock_catalog, sample_accessories_quantities):
        """When sistema=techo_isodec_eps, should pick ISODEC-specific gotero."""
        with patch(
            "quotation_calculator_v3._load_accessories_catalog",
            return_value=mock_catalog,
        ):
            items, total = calculate_accessories_pricing(
                sample_accessories_quantities,
                sistema="techo_isodec_eps",
            )
        assert len(items) == 1
        assert items[0]["product_id"] == "ISO-001"
        assert items[0]["unit_price_usd"] == 7.50

    def test_selects_isoroof_specific_accessory(self, mock_catalog, sample_accessories_quantities):
        """When sistema=techo_isoroof_3g, should pick ISOROOF-specific gotero."""
        with patch(
            "quotation_calculator_v3._load_accessories_catalog",
            return_value=mock_catalog,
        ):
            items, total = calculate_accessories_pricing(
                sample_accessories_quantities,
                sistema="techo_isoroof_3g",
            )
        assert len(items) == 1
        assert items[0]["product_id"] == "IRF-001"
        assert items[0]["unit_price_usd"] == 8.00

    def test_falls_back_to_universal(self, mock_catalog, sample_accessories_quantities):
        """When no system-specific match exists, should pick UNIVERSAL."""
        with patch(
            "quotation_calculator_v3._load_accessories_catalog",
            return_value=mock_catalog,
        ):
            items, total = calculate_accessories_pricing(
                sample_accessories_quantities,
                sistema="pared_isopanel_eps",
            )
        # No ISOPANEL gotero_frontal exists, should fall back to UNIVERSAL
        assert len(items) == 1
        assert items[0]["product_id"] == "UNI-001"
        assert items[0]["unit_price_usd"] == 5.00

    def test_unknown_sistema_falls_back_to_universal(self, mock_catalog, sample_accessories_quantities):
        """Unknown sistema should still get UNIVERSAL accessory."""
        with patch(
            "quotation_calculator_v3._load_accessories_catalog",
            return_value=mock_catalog,
        ):
            items, total = calculate_accessories_pricing(
                sample_accessories_quantities,
                sistema="unknown_system",
            )
        assert len(items) == 1
        assert items[0]["product_id"] == "UNI-001"

    def test_total_reflects_correct_price(self, mock_catalog, sample_accessories_quantities):
        """Total should use the system-specific price, not the first item."""
        with patch(
            "quotation_calculator_v3._load_accessories_catalog",
            return_value=mock_catalog,
        ):
            items, total = calculate_accessories_pricing(
                sample_accessories_quantities,
                sistema="techo_isodec_eps",
            )
        # 2 units * 7.50 = 15.00
        assert total == Decimal("15.00")

    def test_fallback_to_first_item_when_no_compat(self, sample_accessories_quantities):
        """When no compatibilidad field exists at all, falls back to first item."""
        catalog_no_compat = {
            "accesorios": [
                {
                    "sku": "PLAIN-001",
                    "name": "Gotero sin compat",
                    "tipo": "gotero_frontal",
                    "precio_unit_iva_inc": 6.00,
                },
            ],
            "indices": {"by_tipo": {"gotero_frontal": [0]}},
        }
        with patch(
            "quotation_calculator_v3._load_accessories_catalog",
            return_value=catalog_no_compat,
        ):
            items, total = calculate_accessories_pricing(
                sample_accessories_quantities,
                sistema="techo_isodec_eps",
            )
        assert len(items) == 1
        assert items[0]["product_id"] == "PLAIN-001"
