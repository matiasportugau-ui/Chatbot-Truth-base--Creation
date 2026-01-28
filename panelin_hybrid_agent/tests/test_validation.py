"""
Test Cases for Validation System
=================================

Tests for validators and KB integrity checks.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from panelin_hybrid_agent.validation.validators import (
    validate_quotation,
    validate_tool_result,
    validate_kb_integrity,
    QuotationValidator,
)


class TestQuotationValidation:
    """Test quotation validation"""
    
    def test_valid_quotation_passes(self):
        """Valid quotation should pass all checks"""
        quotation = {
            "panels": {
                "area_m2": 6.0,
                "length_m": 6.0,
                "width_m": 1.0,
                "unit_price_usd": 264.0,
                "notes": [],
            },
            "profiles": {
                "subtotal_usd": 200.0,
            },
            "panel_count": 10,
            "panels_subtotal_usd": 2640.0,
            "profiles_subtotal_usd": 200.0,
            "grand_total_usd": 2840.0,
            "calculation_verified": True,
        }
        
        result = validate_quotation(quotation)
        assert result["valid"] == True
        assert len(result["errors"]) == 0
    
    def test_missing_verification_fails(self):
        """Quotation without calculation_verified should fail"""
        quotation = {
            "panels": {"area_m2": 6.0},
            "grand_total_usd": 1000.0,
            "calculation_verified": False,  # CRITICAL
        }
        
        result = validate_quotation(quotation)
        assert result["valid"] == False
        assert any("calculation_verified" in e for e in result["errors"])
    
    def test_negative_price_fails(self):
        """Negative prices should fail validation"""
        quotation = {
            "panels": {"unit_price_usd": -10.0},
            "total_usd": -100.0,
            "calculation_verified": True,
        }
        
        result = validate_quotation(quotation)
        assert result["valid"] == False
        assert any("Negative" in e for e in result["errors"])
    
    def test_total_mismatch_fails(self):
        """Mismatched totals should fail validation"""
        quotation = {
            "panels": {"area_m2": 6.0},
            "panels_subtotal_usd": 1000.0,
            "profiles_subtotal_usd": 200.0,
            "grand_total_usd": 500.0,  # Wrong! Should be 1200
            "calculation_verified": True,
        }
        
        result = validate_quotation(quotation)
        assert result["valid"] == False
        assert any("mismatch" in e.lower() for e in result["errors"])


class TestToolResultValidation:
    """Test tool result validation"""
    
    def test_valid_tool_result(self):
        """Valid tool result should pass"""
        result = {
            "calculation_verified": True,
            "total_usd": 1000.0,
            "area_m2": 60.0,
        }
        
        validation = validate_tool_result(result)
        assert validation["valid"] == True
    
    def test_tool_error_fails(self):
        """Tool result with error should fail"""
        result = {
            "error": "Product not found",
            "calculation_verified": False,
        }
        
        validation = validate_tool_result(result)
        assert validation["valid"] == False
        assert any("error" in e.lower() for e in validation["errors"])
    
    def test_missing_fields_detected(self):
        """Missing expected fields should be reported"""
        result = {
            "calculation_verified": True,
            "total_usd": 1000.0,
        }
        
        validation = validate_tool_result(
            result,
            expected_fields=["total_usd", "area_m2", "panel_count"]
        )
        assert validation["valid"] == False
        assert any("area_m2" in e for e in validation["errors"])


class TestKBIntegrity:
    """Test Knowledge Base integrity validation"""
    
    def test_kb_exists(self):
        """KB file should exist and be valid JSON"""
        result = validate_kb_integrity()
        # May have warnings but should be valid
        assert "JSON" not in str(result["errors"])
    
    def test_kb_has_products(self):
        """KB should have products"""
        result = validate_kb_integrity()
        # Check there's no "No products" error
        assert not any("No products" in e for e in result["errors"])


class TestValidatorClass:
    """Test the QuotationValidator class directly"""
    
    def test_area_calculation_check(self):
        """Area validation should catch mismatches"""
        validator = QuotationValidator()
        
        # Correct
        good_result = {
            "panels": {
                "length_m": 6.0,
                "width_m": 1.0,
                "area_m2": 6.0,
            }
        }
        valid, msg = validator.validate_area_calculation(good_result)
        assert valid == True
        
        # Incorrect
        bad_result = {
            "panels": {
                "length_m": 6.0,
                "width_m": 1.0,
                "area_m2": 10.0,  # Wrong!
            }
        }
        valid, msg = validator.validate_area_calculation(bad_result)
        assert valid == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
