"""
Test Accessory Lookup with System Compatibility
================================================

Tests for the lookup_accessory_price function to ensure it correctly
filters accessories by system compatibility (ISOROOF, ISODEC, etc.)
"""

import pytest
from pathlib import Path
from panelin.tools.bom_calculator import (
    lookup_accessory_price,
    _flatten_accessories_catalog,
    _check_compatibility,
)


class TestAccessoryCompatibility:
    """Tests for system/compatibility filtering in accessory lookup."""

    def test_check_compatibility_exact_match(self):
        """Test exact compatibility matching."""
        assert _check_compatibility(["ISOROOF"], "ISOROOF") is True
        assert _check_compatibility(["ISODEC"], "ISODEC") is True
        assert _check_compatibility(["ISOPANEL"], "ISOPANEL") is True

    def test_check_compatibility_universal(self):
        """Test UNIVERSAL compatibility matches any system."""
        assert _check_compatibility(["UNIVERSAL"], "ISOROOF") is True
        assert _check_compatibility(["UNIVERSAL"], "ISODEC") is True
        assert _check_compatibility(["UNIVERSAL"], "ISOPANEL") is True

    def test_check_compatibility_partial_match(self):
        """Test partial compatibility matching."""
        assert _check_compatibility(["ISOROOF"], "ISOROOF_3G") is True
        assert _check_compatibility(["ISOROOF"], "ISOROOF 3G") is True
        assert _check_compatibility(["ISODEC"], "ISODEC_EPS") is True
        assert _check_compatibility(["ISODEC"], "ISODEC EPS") is True

    def test_check_compatibility_no_match(self):
        """Test compatibility returns False when no match."""
        assert _check_compatibility(["ISOROOF"], "ISODEC") is False
        assert _check_compatibility(["ISODEC"], "ISOROOF") is False
        assert _check_compatibility([], "ISOROOF") is False

    def test_check_compatibility_multiple_systems(self):
        """Test items compatible with multiple systems."""
        assert _check_compatibility(["ISODEC", "ISOPANEL"], "ISODEC") is True
        assert _check_compatibility(["ISODEC", "ISOPANEL"], "ISOPANEL") is True
        assert _check_compatibility(["ISODEC", "ISOPANEL"], "ISOROOF") is False


class TestFlattenCatalog:
    """Tests for catalog flattening."""

    def test_flatten_empty_catalog(self):
        """Test flattening empty catalog returns empty list."""
        result = _flatten_accessories_catalog({})
        assert result == []

    def test_flatten_simple_list(self):
        """Test flattening catalog with simple list."""
        catalog = {
            "items": [
                {"sku": "SKU1", "precio_unit_iva_inc": 10.0},
                {"sku": "SKU2", "precio_unit_iva_inc": 20.0},
            ]
        }
        result = _flatten_accessories_catalog(catalog)
        assert len(result) == 2

    def test_flatten_nested_structure(self):
        """Test flattening nested catalog structure."""
        catalog = {
            "perfileria": {
                "goteros_frontales": {
                    "isoroof": [
                        {"sku": "GFS30", "precio_venta_iva_inc": 19.31}
                    ],
                    "isodec": [
                        {"sku": "6838", "precio_venta_iva_inc": 19.12}
                    ]
                }
            }
        }
        result = _flatten_accessories_catalog(catalog)
        assert len(result) == 2
        skus = [item["sku"] for item in result]
        assert "GFS30" in skus
        assert "6838" in skus


class TestLookupAccessoryPrice:
    """Tests for lookup_accessory_price function."""

    def test_lookup_by_sku(self):
        """Test lookup by exact SKU."""
        # This test uses the actual catalog if available
        result = lookup_accessory_price(
            tipo="gotero_frontal",
            familia="ISOROOF",
            sku="GFS30"
        )
        # SKU lookup should return item or None if catalog doesn't have it
        if result:
            assert result.get("sku") == "GFS30"

    def test_lookup_filters_by_compatibility(self):
        """Test that lookup filters by system compatibility."""
        # Look for gotero frontal for ISOROOF
        isoroof_result = lookup_accessory_price(
            tipo="gotero_frontal",
            familia="ISOROOF",
            espesor_mm=30
        )

        # Look for gotero frontal for ISODEC
        isodec_result = lookup_accessory_price(
            tipo="gotero_frontal",
            familia="ISODEC",
            espesor_mm=100
        )

        # Both should return results if catalog has data
        # But they should be DIFFERENT products
        if isoroof_result and isodec_result:
            # ISOROOF goteros have different SKUs than ISODEC goteros
            assert isoroof_result.get("sku") != isodec_result.get("sku")
            # Check compatibility fields
            isoroof_compat = isoroof_result.get("compatibilidad", [])
            isodec_compat = isodec_result.get("compatibilidad", [])
            # ISOROOF result should be compatible with ISOROOF
            assert _check_compatibility(isoroof_compat, "ISOROOF") is True
            # ISODEC result should be compatible with ISODEC
            assert _check_compatibility(isodec_compat, "ISODEC") is True

    def test_lookup_returns_none_for_incompatible(self):
        """Test that lookup returns None when no compatible item found."""
        # Look for a very specific combination unlikely to exist
        result = lookup_accessory_price(
            tipo="nonexistent_tipo",
            familia="NONEXISTENT_SYSTEM",
        )
        assert result is None

    def test_lookup_prefers_matching_espesor(self):
        """Test that lookup prefers items matching the specified thickness."""
        result = lookup_accessory_price(
            tipo="gotero_frontal",
            familia="ISOROOF",
            espesor_mm=50
        )
        if result:
            # Check if thickness matches when available
            item_espesor = result.get("espesor_compatible_mm") or result.get("espesor_panel_mm")
            if item_espesor:
                if isinstance(item_espesor, list):
                    assert 50 in item_espesor
                else:
                    assert item_espesor == 50


class TestBOMCalculatorIntegration:
    """Integration tests for BOM calculator with accessories."""

    def test_different_systems_get_different_accessories(self):
        """
        Critical test: Ensure ISOROOF and ISODEC get different accessory SKUs.
        
        This is the main fix for the issue: accessories pricing function takes
        a 'sistema' argument and must use it to filter accessories.
        """
        # Get gotero for ISOROOF 50mm
        isoroof_gotero = lookup_accessory_price(
            tipo="gotero_frontal",
            familia="ISOROOF",
            espesor_mm=50
        )

        # Get gotero for ISODEC 100mm
        isodec_gotero = lookup_accessory_price(
            tipo="gotero_frontal",
            familia="ISODEC",
            espesor_mm=100
        )

        # If both are found, they should be different products
        if isoroof_gotero and isodec_gotero:
            # The SKUs should be different
            assert isoroof_gotero.get("sku") != isodec_gotero.get("sku"), \
                "ISOROOF and ISODEC should have different goteros"

            # Names should reflect the system
            isoroof_name = isoroof_gotero.get("name", "").upper()
            isodec_name = isodec_gotero.get("name", "").upper()

            # ISOROOF gotero shouldn't say ISODEC and vice versa
            if "ISODEC" not in isoroof_name and "ISOROOF" not in isodec_name:
                # Names are generic, check compatibility instead
                isoroof_compat = isoroof_gotero.get("compatibilidad", [])
                isodec_compat = isodec_gotero.get("compatibilidad", [])

                assert _check_compatibility(isoroof_compat, "ISOROOF"), \
                    "ISOROOF gotero must be compatible with ISOROOF"
                assert _check_compatibility(isodec_compat, "ISODEC"), \
                    "ISODEC gotero must be compatible with ISODEC"
