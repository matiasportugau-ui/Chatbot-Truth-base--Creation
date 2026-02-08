"""
Pytest Configuration and Shared Fixtures
=========================================

This module provides shared fixtures for the test suite.
Fixtures reduce code duplication and provide consistent test data.
"""

import pytest
from decimal import Decimal
from typing import Dict, List


@pytest.fixture
def mock_bom_rules() -> Dict:
    """
    Mock BOM rules with autoportancia table.
    
    Provides minimal but complete BOM rules structure for testing
    validation functions without loading the full file.
    """
    return {
        "autoportancia": {
            "descripcion": "Tabla de cargas y luces máximas",
            "tablas": {
                "ISODEC_EPS": {
                    "100": {"luz_max_m": 5.5, "peso_kg_m2": 12.5},
                    "150": {"luz_max_m": 7.5, "peso_kg_m2": 14.5},
                    "200": {"luz_max_m": 9.1, "peso_kg_m2": 16.5},
                    "250": {"luz_max_m": 10.4, "peso_kg_m2": 18.5}
                },
                "ISODEC_PIR": {
                    "50": {"luz_max_m": 3.5, "peso_kg_m2": 10.0},
                    "80": {"luz_max_m": 5.5, "peso_kg_m2": 11.5},
                    "120": {"luz_max_m": 7.6, "peso_kg_m2": 13.5}
                },
                "ISOROOF_3G": {
                    "30": {"luz_max_m": 2.8, "peso_kg_m2": 5.0},
                    "50": {"luz_max_m": 3.3, "peso_kg_m2": 6.5},
                    "80": {"luz_max_m": 4.0, "peso_kg_m2": 8.5}
                },
                "ISOPANEL_EPS": {
                    "50": {"luz_max_m": 3.0, "peso_kg_m2": 10.0},
                    "100": {"luz_max_m": 5.5, "peso_kg_m2": 12.5},
                    "150": {"luz_max_m": 7.5, "peso_kg_m2": 14.5},
                    "200": {"luz_max_m": 9.1, "peso_kg_m2": 16.5}
                }
            }
        },
        "sistemas": {
            "techo_isodec_eps": {"nombre": "Techo ISODEC EPS"},
            "techo_isodec_pir": {"nombre": "Techo ISODEC PIR"},
            "techo_isoroof_3g": {"nombre": "Techo ISOROOF 3G"},
            "pared_isopanel_eps": {"nombre": "Pared ISOPANEL EPS"},
            "pared_isowall_pir": {"nombre": "Pared ISOWALL PIR"},
            "pared_isofrig_pir": {"nombre": "Pared ISOFRIG PIR"}
        }
    }


@pytest.fixture
def sample_product_specs() -> Dict:
    """
    Sample product specifications for testing.
    
    Provides realistic product data for 4 families.
    """
    return {
        "ISODEC_EPS_100mm": {
            "family": "ISODEC_EPS",
            "sub_family": "EPS",
            "thickness_mm": 100,
            "price_per_m2": 45.50,
            "ancho_util_m": 1.12,
            "largo_min_m": 2.0,
            "largo_max_m": 14.0,
            "autoportancia_m": 5.5
        },
        "ISODEC_PIR_80mm": {
            "family": "ISODEC_PIR",
            "sub_family": "PIR",
            "thickness_mm": 80,
            "price_per_m2": 52.30,
            "ancho_util_m": 1.12,
            "largo_min_m": 2.0,
            "largo_max_m": 14.0,
            "autoportancia_m": 5.5
        },
        "ISOROOF_3G_50mm": {
            "family": "ISOROOF_3G",
            "sub_family": "3G",
            "thickness_mm": 50,
            "price_per_m2": 38.20,
            "ancho_util_m": 1.0,
            "largo_min_m": 2.0,
            "largo_max_m": 12.0,
            "autoportancia_m": 3.3
        },
        "ISOPANEL_EPS_100mm": {
            "family": "ISOPANEL_EPS",
            "sub_family": "EPS",
            "thickness_mm": 100,
            "price_per_m2": 42.80,
            "ancho_util_m": 1.0,
            "largo_min_m": 2.0,
            "largo_max_m": 12.0,
            "autoportancia_m": 5.5
        }
    }


@pytest.fixture
def test_quotation_params() -> Dict:
    """
    Common quotation parameters for testing.
    
    Provides standard parameters that result in valid quotations.
    """
    return {
        "product_id": "ISODEC_EPS_100mm",
        "length_m": 5.0,
        "width_m": 10.0,
        "quantity": 1,
        "discount_percent": 0.0,
        "include_accessories": False,
        "include_tax": True,
        "installation_type": "techo",
        "validate_span": False  # Disable for basic tests
    }


@pytest.fixture
def autoportancia_test_cases() -> List[Dict]:
    """
    Parameterized test cases for autoportancia validation.
    
    Each case includes:
    - family: Product family
    - thickness: Panel thickness (mm)
    - span: Requested span (m)
    - expected_valid: Expected validation result
    - description: Test case description
    """
    return [
        {
            "family": "ISODEC_EPS",
            "thickness": 100,
            "span": 4.0,
            "expected_valid": True,
            "description": "Valid span well within limit"
        },
        {
            "family": "ISODEC_EPS",
            "thickness": 100,
            "span": 4.675,
            "expected_valid": True,
            "description": "Valid span exactly at safe limit"
        },
        {
            "family": "ISODEC_EPS",
            "thickness": 100,
            "span": 5.0,
            "expected_valid": False,
            "description": "Invalid span exceeds safe limit"
        },
        {
            "family": "ISODEC_EPS",
            "thickness": 100,
            "span": 8.0,
            "expected_valid": False,
            "description": "Invalid span far exceeds limit"
        },
        {
            "family": "ISODEC_PIR",
            "thickness": 80,
            "span": 4.5,
            "expected_valid": True,
            "description": "PIR valid span"
        },
        {
            "family": "ISOROOF_3G",
            "thickness": 50,
            "span": 2.5,
            "expected_valid": True,
            "description": "ISOROOF valid span"
        },
        {
            "family": "ISOPANEL_EPS",
            "thickness": 100,
            "span": 4.0,
            "expected_valid": True,
            "description": "ISOPANEL valid span"
        }
    ]


@pytest.fixture
def decimal_test_values() -> Dict:
    """
    Decimal values for precision testing.
    
    Provides various Decimal values to test financial calculations.
    """
    return {
        "price_per_m2": Decimal("45.50"),
        "area": Decimal("50.00"),
        "discount_10pct": Decimal("10.0"),
        "discount_30pct": Decimal("30.0"),
        "tax_rate": Decimal("0.22"),
        "expected_subtotal": Decimal("2275.00"),  # 45.50 * 50
        "expected_discount_10": Decimal("227.50"),  # 2275 * 0.10
        "expected_total_after_discount": Decimal("2047.50"),  # 2275 - 227.50
        "expected_tax": Decimal("450.45"),  # 2047.50 * 0.22
        "expected_final": Decimal("2497.95")  # 2047.50 + 450.45
    }
