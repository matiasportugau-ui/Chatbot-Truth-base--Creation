"""
Source of Truth Validator
========================

Validates that all responses use the correct knowledge base source hierarchy.
Enforces Level 1 (Master) as the primary source for prices and formulas.

Part of P0.1: Enhanced Source of Truth Enforcement
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


@dataclass
class SourceValidationResult:
    """Result of source of truth validation"""
    valid: bool
    source_used: Optional[str]
    source_level: Optional[int]
    warnings: List[str]
    errors: List[str]
    timestamp: str
    product_id: Optional[str] = None
    field_validated: Optional[str] = None


class SourceOfTruthValidator:
    """
    Validates that responses use the correct knowledge base source hierarchy.
    
    Hierarchy:
    - Level 1 (Master): BMC_Base_Conocimiento_GPT.json - ALWAYS use first
    - Level 2 (Validation): BMC_Base_Unificada_v4.json - Cross-reference only
    - Level 3 (Dynamic): panelin_truth_bmcuruguay_web_only_v2.json - Price updates
    - Level 4 (Support): Other files - Contextual support
    """
    
    def __init__(self, knowledge_base_path: Optional[str] = None):
        """
        Initialize validator
        
        Args:
            knowledge_base_path: Path to knowledge base directory
        """
        self.kb_path = Path(knowledge_base_path) if knowledge_base_path else None
        self.level_1_files = [
            "BMC_Base_Conocimiento_GPT.json",
            "BMC_Base_Conocimiento_GPT-2.json"
        ]
        self.level_2_files = [
            "BMC_Base_Unificada_v4.json"
        ]
        self.level_3_files = [
            "panelin_truth_bmcuruguay_web_only_v2.json"
        ]
        
    def validate_response(
        self, 
        response_data: Dict[str, Any],
        sources_consulted: List[str],
        product_id: Optional[str] = None
    ) -> SourceValidationResult:
        """
        Validate that response uses correct source hierarchy
        
        Args:
            response_data: The response data to validate
            sources_consulted: List of source files that were consulted
            product_id: Optional product ID being queried
            
        Returns:
            SourceValidationResult with validation details
        """
        result = SourceValidationResult(
            valid=True,
            source_used=None,
            source_level=None,
            warnings=[],
            errors=[],
            timestamp=datetime.now().isoformat(),
            product_id=product_id
        )
        
        # Check if response contains price information
        if self._contains_price(response_data):
            result.field_validated = "price"
            validation = self._validate_price_source(sources_consulted, response_data)
            result.valid = validation["valid"]
            result.source_used = validation.get("source_used")
            result.source_level = validation.get("source_level")
            result.warnings.extend(validation.get("warnings", []))
            result.errors.extend(validation.get("errors", []))
        
        # Check if response contains formula calculations
        if self._contains_formula(response_data):
            result.field_validated = "formula"
            validation = self._validate_formula_source(sources_consulted, response_data)
            if not validation["valid"]:
                result.valid = False
            result.warnings.extend(validation.get("warnings", []))
            result.errors.extend(validation.get("errors", []))
        
        # Check if response contains technical specifications
        if self._contains_specifications(response_data):
            result.field_validated = "specifications"
            validation = self._validate_spec_source(sources_consulted, response_data)
            if not validation["valid"]:
                result.valid = False
            result.warnings.extend(validation.get("warnings", []))
            result.errors.extend(validation.get("errors", []))
        
        return result
    
    def _contains_price(self, data: Dict[str, Any]) -> bool:
        """Check if response contains price information"""
        data_str = json.dumps(data).lower()
        price_indicators = ["$", "precio", "price", "costo", "cost", "usd"]
        return any(indicator in data_str for indicator in price_indicators)
    
    def _contains_formula(self, data: Dict[str, Any]) -> bool:
        """Check if response contains formula calculations"""
        data_str = json.dumps(data).lower()
        formula_indicators = ["formula", "calculo", "calculation", "roundup", "round"]
        return any(indicator in data_str for indicator in formula_indicators)
    
    def _contains_specifications(self, data: Dict[str, Any]) -> bool:
        """Check if response contains technical specifications"""
        data_str = json.dumps(data).lower()
        spec_indicators = ["espesor", "autoportancia", "ancho", "thickness", "span"]
        return any(indicator in data_str for indicator in spec_indicators)
    
    def _validate_price_source(
        self, 
        sources_consulted: List[str], 
        response_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that price comes from Level 1 source
        
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": True,
            "source_used": None,
            "source_level": None,
            "warnings": [],
            "errors": []
        }
        
        # Check if Level 1 source was consulted
        level_1_consulted = any(
            any(level_1_file in source for level_1_file in self.level_1_files)
            for source in sources_consulted
        )
        
        if not level_1_consulted:
            result["valid"] = False
            result["errors"].append(
                "CRITICAL: Price response must use Level 1 (Master) source. "
                "Level 1 sources: " + ", ".join(self.level_1_files)
            )
            return result
        
        # Identify which source was used
        for source in sources_consulted:
            if any(level_1_file in source for level_1_file in self.level_1_files):
                result["source_used"] = source
                result["source_level"] = 1
                break
            elif any(level_2_file in source for level_2_file in self.level_2_files):
                result["source_used"] = source
                result["source_level"] = 2
                result["warnings"].append(
                    "Warning: Using Level 2 source for price. "
                    "Level 1 should be primary source."
                )
            elif any(level_3_file in source for level_3_file in self.level_3_files):
                result["source_used"] = source
                result["source_level"] = 3
                result["warnings"].append(
                    "Warning: Using Level 3 source for price. "
                    "Level 1 should be primary source."
                )
        
        # Check for conflicts if multiple sources consulted
        if len(sources_consulted) > 1:
            result["warnings"].append(
                f"Multiple sources consulted: {', '.join(sources_consulted)}. "
                "Level 1 should take precedence."
            )
        
        return result
    
    def _validate_formula_source(
        self, 
        sources_consulted: List[str], 
        response_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that formulas come from Level 1 source"""
        result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        level_1_consulted = any(
            any(level_1_file in source for level_1_file in self.level_1_files)
            for source in sources_consulted
        )
        
        if not level_1_consulted:
            result["valid"] = False
            result["errors"].append(
                "CRITICAL: Formulas must come from Level 1 (Master) source. "
                "Formulas are defined in: " + ", ".join(self.level_1_files)
            )
        
        return result
    
    def _validate_spec_source(
        self, 
        sources_consulted: List[str], 
        response_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that specifications come from appropriate source"""
        result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Specifications should prefer Level 1, but Level 2/3 acceptable for validation
        level_1_consulted = any(
            any(level_1_file in source for level_1_file in self.level_1_files)
            for source in sources_consulted
        )
        
        if not level_1_consulted:
            result["warnings"].append(
                "Recommendation: Technical specifications should use Level 1 source "
                "as primary reference."
            )
        
        return result
    
    def check_level_1_consultation(self, sources_consulted: List[str]) -> bool:
        """
        Check if Level 1 source was consulted
        
        Args:
            sources_consulted: List of source files consulted
            
        Returns:
            True if Level 1 source was consulted
        """
        return any(
            any(level_1_file in source for level_1_file in self.level_1_files)
            for source in sources_consulted
        )
    
    def get_source_hierarchy_info(self) -> Dict[str, Any]:
        """Get information about source hierarchy"""
        return {
            "level_1_master": {
                "files": self.level_1_files,
                "purpose": "Primary source for prices, formulas, and specifications",
                "priority": "HIGHEST - Always use first"
            },
            "level_2_validation": {
                "files": self.level_2_files,
                "purpose": "Cross-reference and validation only",
                "priority": "MEDIUM - Do not use for direct responses"
            },
            "level_3_dynamic": {
                "files": self.level_3_files,
                "purpose": "Price updates and stock status",
                "priority": "LOW - Verify against Level 1"
            }
        }


def validate_source_of_truth(
    response_data: Dict[str, Any],
    sources_consulted: List[str],
    product_id: Optional[str] = None
) -> SourceValidationResult:
    """
    Convenience function to validate source of truth
    
    Args:
        response_data: Response data to validate
        sources_consulted: Sources that were consulted
        product_id: Optional product ID
        
    Returns:
        SourceValidationResult
    """
    validator = SourceOfTruthValidator()
    return validator.validate_response(response_data, sources_consulted, product_id)


if __name__ == "__main__":
    # Example usage
    validator = SourceOfTruthValidator()
    
    # Example 1: Valid response using Level 1
    response1 = {
        "product": "ISODEC EPS 100mm",
        "price": "$46.07",
        "source": "BMC_Base_Conocimiento_GPT.json"
    }
    sources1 = ["BMC_Base_Conocimiento_GPT.json"]
    
    result1 = validator.validate_response(response1, sources1, "ISODEC_EPS_100")
    print("Example 1 - Valid Level 1:")
    print(f"Valid: {result1.valid}")
    print(f"Errors: {result1.errors}")
    print(f"Warnings: {result1.warnings}")
    print()
    
    # Example 2: Invalid - no Level 1 source
    response2 = {
        "product": "ISODEC EPS 100mm",
        "price": "$46.00",
        "source": "BMC_Base_Unificada_v4.json"
    }
    sources2 = ["BMC_Base_Unificada_v4.json"]
    
    result2 = validator.validate_response(response2, sources2, "ISODEC_EPS_100")
    print("Example 2 - Invalid (no Level 1):")
    print(f"Valid: {result2.valid}")
    print(f"Errors: {result2.errors}")
    print(f"Warnings: {result2.warnings}")
