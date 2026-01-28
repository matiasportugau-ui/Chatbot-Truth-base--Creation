import unittest
from unittest.mock import patch, mock_open
import json
from decimal import Decimal
import sys
import os

# Add workspace to path to import modules
sys.path.append('/workspace')

from panelin.tools.quotation_calculator import calculate_panel_quote

class TestQuotationCalculations(unittest.TestCase):
    
    def setUp(self):
        self.mock_catalog = {
            "products": {
                "TEST_ISO_50": {
                    "sku": "TEST_ISO_50",
                    "name": "Isopanel 50mm Standard",
                    "category": "ISOPANEL",
                    "subcategory": "Pared",
                    "type": "Panel",
                    "price_per_m2": 22.50,
                    "specifications": {
                        "thickness_mm": 50,
                        "largo_min_max": "0.5 / 14"
                    }
                },
                "TEST_ISODEC_75": {
                    "sku": "TEST_ISODEC_75",
                    "name": "Isodec 75mm",
                    "category": "ISODEC",
                    "subcategory": "Techo",
                    "type": "Panel",
                    "price_per_m2": 28.00,
                    "specifications": {
                        "thickness_mm": 75,
                        "largo_min_max": "0.5 / 14"
                    }
                }
            }
        }

    @patch('panelin.tools.quotation_calculator.load_catalog')
    def test_basic_isopanel_quote(self, mock_load):
        mock_load.return_value = self.mock_catalog
        
        result = calculate_panel_quote(
            panel_type="Isopanel",
            thickness_mm=50,
            length_m=2.0,
            width_m=1.0,
            quantity=10
        )
        
        self.assertEqual(result['area_m2'], 20.0) # 2.0 * 1.0 * 10
        self.assertEqual(result['total_usd'], 450.0) # 20m² * $22.50
        self.assertTrue(result['calculation_verified'])
        self.assertEqual(result['product_id'], "TEST_ISO_50")

    @patch('panelin.tools.quotation_calculator.load_catalog')
    def test_discount_application(self, mock_load):
        mock_load.return_value = self.mock_catalog
        
        result = calculate_panel_quote(
            panel_type="Isodec",
            thickness_mm=75,
            length_m=3.0,
            width_m=1.2,
            quantity=50,
            discount_percent=10
        )
        
        # Expected:
        # Area per panel = 3.0 * 1.2 = 3.6 m2
        # Price per m2 = 28.00
        # Unit price = 3.6 * 28.00 = 100.80
        # Subtotal = 100.80 * 50 = 5040.00
        # Discount = 5040.00 * 0.10 = 504.00
        # Total = 5040.00 - 504.00 = 4536.00
        
        self.assertEqual(result['subtotal_usd'], 5040.00)
        self.assertEqual(result['discount_amount_usd'], 504.00)
        self.assertEqual(result['total_usd'], 4536.00)
        self.assertTrue(result['calculation_verified'])

    @patch('panelin.tools.quotation_calculator.load_catalog')
    def test_invalid_product(self, mock_load):
        mock_load.return_value = self.mock_catalog
        
        with self.assertRaises(ValueError):
            calculate_panel_quote("NonExistent", 999, 1.0, 1.0, 1)

if __name__ == '__main__':
    unittest.main()
