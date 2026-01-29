"""
Validators for Quotation Accuracy
=================================

Implements validation rules to ensure 100% accuracy in quotations.
All calculations must pass through deterministic tools and be verified.
"""

import json
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass, field
from datetime import datetime, timezone

KB_PATH = Path(__file__).parent.parent / "kb" / "panelin_truth_bmcuruguay.json"


class ValidationResult(TypedDict):
    """Result of a validation check"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    checked_at: str


@dataclass
class QuotationValidator:
    """Validates quotation results for accuracy"""
    
    tolerance_usd: float = 0.01  # Maximum acceptable rounding difference
    
    def validate_calculation_verified(
        self,
        result: Dict[str, Any],
    ) -> tuple[bool, str]:
        """
        Verify that calculation_verified flag is True.
        
        This flag confirms the result came from deterministic code,
        not from LLM calculations.
        """
        if not result.get("calculation_verified", False):
            return False, "CRITICAL: calculation_verified is False - LLM may have calculated directly"
        return True, ""
    
    def validate_price_positive(
        self,
        result: Dict[str, Any],
    ) -> tuple[bool, str]:
        """Verify all prices are positive"""
        price_fields = [
            "unit_price_usd",
            "subtotal_usd",
            "total_usd",
            "grand_total_usd",
        ]
        
        for field in price_fields:
            if field in result:
                value = result[field]
                if value is not None and value < 0:
                    return False, f"Negative price in {field}: {value}"
        
        return True, ""
    
    def validate_totals_match(
        self,
        result: Dict[str, Any],
    ) -> tuple[bool, str]:
        """Verify that totals add up correctly"""
        if "panels" in result and "grand_total_usd" in result:
            panels_total = result.get("panels_subtotal_usd", 0)
            profiles_total = result.get("profiles_subtotal_usd", 0) if "profiles" in result else 0
            
            expected_total = panels_total + profiles_total
            actual_total = result.get("grand_total_usd", 0)
            
            diff = abs(expected_total - actual_total)
            if diff > self.tolerance_usd:
                return False, f"Total mismatch: expected {expected_total}, got {actual_total} (diff: {diff})"
        
        return True, ""
    
    def validate_quantity_positive(
        self,
        result: Dict[str, Any],
    ) -> tuple[bool, str]:
        """Verify quantities are positive integers"""
        quantity_fields = [
            "quantity",
            "panel_count",
            "fixation_points",
            "rods_needed",
        ]
        
        for field in quantity_fields:
            if field in result:
                value = result[field]
                if not isinstance(value, int) or value < 0:
                    return False, f"Invalid quantity in {field}: {value}"
        
        return True, ""
    
    def validate_area_calculation(
        self,
        result: Dict[str, Any],
    ) -> tuple[bool, str]:
        """Verify area calculation is correct"""
        if "panels" in result:
            panels = result["panels"]
            length = panels.get("length_m", 0)
            width = panels.get("width_m", 0)
            area = panels.get("area_m2", 0)
            
            expected_area = length * width
            diff = abs(expected_area - area)
            
            if diff > 0.001:
                return False, f"Area mismatch: {length}×{width}={expected_area}, got {area}"
        
        return True, ""


def validate_quotation(
    quotation: Dict[str, Any],
    strict: bool = True,
) -> ValidationResult:
    """
    Validate a quotation result.
    
    Args:
        quotation: The quotation result to validate
        strict: If True, any error fails validation
        
    Returns:
        ValidationResult with validation status
    """
    validator = QuotationValidator()
    errors = []
    warnings = []
    
    # Critical check: calculation_verified
    valid, msg = validator.validate_calculation_verified(quotation)
    if not valid:
        errors.append(msg)
    
    # Price validation
    valid, msg = validator.validate_price_positive(quotation)
    if not valid:
        errors.append(msg)
    
    # Total validation
    valid, msg = validator.validate_totals_match(quotation)
    if not valid:
        errors.append(msg)
    
    # Quantity validation
    valid, msg = validator.validate_quantity_positive(quotation)
    if not valid:
        errors.append(msg)
    
    # Area validation
    valid, msg = validator.validate_area_calculation(quotation)
    if not valid:
        errors.append(msg)
    
    # Check for notes/warnings
    if "panels" in quotation and quotation["panels"].get("notes"):
        for note in quotation["panels"]["notes"]:
            warnings.append(note)
    
    return ValidationResult(
        valid=len(errors) == 0 if strict else True,
        errors=errors,
        warnings=warnings,
        checked_at=datetime.now(timezone.utc).isoformat(),
    )


def validate_tool_result(
    result: Dict[str, Any],
    expected_fields: Optional[List[str]] = None,
) -> ValidationResult:
    """
    Validate a tool result has required fields and calculation_verified.
    
    Args:
        result: Tool result to validate
        expected_fields: List of fields that must be present
        
    Returns:
        ValidationResult
    """
    errors = []
    warnings = []
    
    # Check calculation_verified
    if not result.get("calculation_verified", False):
        errors.append("calculation_verified is not True")
    
    # Check for error field
    if "error" in result:
        errors.append(f"Tool returned error: {result['error']}")
    
    # Check expected fields
    if expected_fields:
        for field in expected_fields:
            if field not in result:
                errors.append(f"Missing expected field: {field}")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        checked_at=datetime.now(timezone.utc).isoformat(),
    )


def validate_kb_integrity() -> ValidationResult:
    """
    Validate the Knowledge Base integrity.
    
    Checks:
    - All products have required fields
    - Prices are valid
    - No duplicate SKUs
    - Relationships are valid
    
    Returns:
        ValidationResult with any issues found
    """
    errors = []
    warnings = []
    
    # Load KB
    if not KB_PATH.exists():
        return ValidationResult(
            valid=False,
            errors=["Knowledge Base file not found"],
            warnings=[],
            checked_at=datetime.now(timezone.utc).isoformat(),
        )
    
    try:
        with open(KB_PATH, "r", encoding="utf-8") as f:
            kb = json.load(f)
    except json.JSONDecodeError as e:
        return ValidationResult(
            valid=False,
            errors=[f"Invalid JSON in KB: {str(e)}"],
            warnings=[],
            checked_at=datetime.now(timezone.utc).isoformat(),
        )
    
    products = kb.get("products", {})
    
    if not products:
        errors.append("No products in Knowledge Base")
    
    # Required fields for products
    required_fields = ["sku", "name", "price_usd"]
    skus_seen = set()
    
    for key, product in products.items():
        # Check required fields
        for field in required_fields:
            if field not in product or product[field] is None:
                errors.append(f"Product {key} missing required field: {field}")
        
        # Check for duplicate SKUs
        sku = product.get("sku", "")
        if sku in skus_seen:
            warnings.append(f"Duplicate SKU: {sku}")
        skus_seen.add(sku)
        
        # Validate prices
        price = product.get("price_usd", 0)
        if price <= 0:
            warnings.append(f"Product {key} has invalid price: {price}")
        
        # Check panel-specific fields
        if product.get("type") == "panel":
            if "thickness_mm" not in product:
                warnings.append(f"Panel {key} missing thickness_mm")
            if "useful_width_m" not in product:
                warnings.append(f"Panel {key} missing useful_width_m")
    
    # Check meta
    meta = kb.get("meta", {})
    if not meta.get("version"):
        warnings.append("KB missing version in meta")
    if not meta.get("last_sync"):
        warnings.append("KB missing last_sync timestamp")
    
    # Check pricing rules
    if not kb.get("pricing_rules"):
        warnings.append("KB missing pricing_rules section")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        checked_at=datetime.now(timezone.utc).isoformat(),
    )


def run_golden_tests() -> Dict[str, Any]:
    """
    Run golden dataset tests to verify calculation accuracy.
    
    Returns:
        Dict with test results
    """
    from ..tools.quotation_calculator import calculate_panel_quote, calculate_fixation_points
    
    test_cases = [
        {
            "name": "basic_isopanel_quote",
            "tool": "calculate_panel_quote",
            "args": {
                "panel_type": "Isopanel",
                "thickness_mm": 50,
                "length_m": 6.0,
                "width_m": 1.14,
                "quantity": 10,
                "price_type": "empresa",
            },
            "expected": {
                "area_m2": 6.84,
                "calculation_verified": True,
            },
        },
        {
            "name": "fixation_calculation",
            "tool": "calculate_fixation_points",
            "args": {
                "panel_count": 10,
                "panel_length_m": 6.0,
                "autoportancia_m": 5.5,
                "structure_type": "metal",
            },
            "expected": {
                "support_count": 2,
                "calculation_verified": True,
            },
        },
    ]
    
    results = {
        "passed": 0,
        "failed": 0,
        "tests": [],
    }
    
    for test in test_cases:
        try:
            if test["tool"] == "calculate_panel_quote":
                result = calculate_panel_quote(**test["args"])
            elif test["tool"] == "calculate_fixation_points":
                result = calculate_fixation_points(**test["args"])
            else:
                continue
            
            # Check expected values
            passed = True
            details = []
            
            for key, expected in test["expected"].items():
                actual = result.get(key)
                if isinstance(expected, float):
                    if abs(actual - expected) > 0.01:
                        passed = False
                        details.append(f"{key}: expected {expected}, got {actual}")
                else:
                    if actual != expected:
                        passed = False
                        details.append(f"{key}: expected {expected}, got {actual}")
            
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            results["tests"].append({
                "name": test["name"],
                "passed": passed,
                "details": details,
            })
            
        except Exception as e:
            results["failed"] += 1
            results["tests"].append({
                "name": test["name"],
                "passed": False,
                "error": str(e),
            })
    
    return results
