"""
Pytest configuration and fixtures for Panelin Hybrid Agent tests.
"""

import pytest
import sys
from pathlib import Path

# Ensure parent directory is in path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def sample_quotation_request():
    """Sample quotation request for testing."""
    return {
        "panel_type": "Isodec_EPS",
        "thickness_mm": 100,
        "length_m": 6.0,
        "quantity": 10,
        "base_type": "metal",
        "discount_percent": 0.0,
        "include_fijaciones": True,
        "include_perfileria": True
    }


@pytest.fixture
def sample_product_specs():
    """Sample product specifications."""
    return {
        "product_id": "Isodec_EPS",
        "name": "Isodec EPS (Techos y Cubiertas)",
        "tipo": "cubierta_pesada",
        "material": "EPS",
        "ancho_util_m": 1.12,
        "thickness_mm": 100,
        "price_per_m2": 46.07,
        "autoportancia_m": 5.5,
    }


@pytest.fixture
def golden_quotation_cases():
    """
    Golden dataset of verified quotation cases.
    
    These cases have been verified against real BMC quotations.
    """
    return [
        {
            "input": {
                "panel_type": "Isodec_EPS",
                "thickness_mm": 100,
                "length_m": 6.0,
                "quantity": 10,
            },
            "expected": {
                "area_m2": 67.2,  # 6 * 1.12 * 10
                "panels_subtotal_approx": 3096.29,  # 46.07 * 6 * 1.12 * 10
            }
        },
        {
            "input": {
                "panel_type": "Isopanel_EPS",
                "thickness_mm": 50,
                "length_m": 4.0,
                "quantity": 20,
                "discount_percent": 10.0,
            },
            "expected": {
                "area_m2": 91.2,  # 4 * 1.14 * 20
                "has_discount": True,
            }
        },
        {
            "input": {
                "panel_type": "Isoroof_3G",
                "thickness_mm": 30,
                "length_m": 5.0,
                "quantity": 8,
                "base_type": "madera",
            },
            "expected": {
                "area_m2": 40.0,  # 5 * 1.0 * 8
            }
        },
    ]


@pytest.fixture
def invalid_quotation_cases():
    """Cases that should raise errors."""
    return [
        {
            "input": {
                "panel_type": "InvalidPanel",
                "thickness_mm": 100,
                "length_m": 6.0,
                "quantity": 10,
            },
            "expected_error": "Producto no encontrado"
        },
        {
            "input": {
                "panel_type": "Isodec_EPS",
                "thickness_mm": 75,  # Invalid thickness
                "length_m": 6.0,
                "quantity": 10,
            },
            "expected_error": "Espesor"
        },
    ]


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "golden: marks tests as golden dataset tests (critical)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
