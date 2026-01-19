"""
JSON Parser Utility

Extracts structured data from JSON knowledge base files.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger


class JSONParser:
    """Parser for JSON knowledge base files"""

    def __init__(self):
        pass

    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse JSON file and return structured data"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Successfully parsed JSON file: {file_path.name}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path.name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing {file_path.name}: {e}")
            raise

    def extract_products(self, data: Dict) -> Dict:
        """Extract product specifications from JSON"""
        products = {}
        if "products" in data:
            products = data["products"]
        return products

    def extract_formulas(self, data: Dict) -> Dict:
        """Extract formulas from JSON"""
        formulas = {}
        if "formulas_cotizacion" in data:
            formulas = data["formulas_cotizacion"]
        elif "formulas" in data:
            formulas = data["formulas"]
        return formulas

    def extract_business_rules(self, data: Dict) -> Dict:
        """Extract business rules from JSON"""
        rules = {}
        if "reglas_negocio" in data:
            rules = data["reglas_negocio"]
        elif "business_rules" in data:
            rules = data["business_rules"]
        return rules

    def extract_identity(self, data: Dict) -> Dict:
        """Extract identity/role information from JSON"""
        identity = {}
        if "identidad" in data:
            identity = data["identidad"]
        elif "identity" in data:
            identity = data["identity"]
        return identity

    def extract_metadata(self, data: Dict) -> Dict:
        """Extract metadata from JSON"""
        metadata = {}
        if "meta" in data:
            metadata = data["meta"]
        elif "metadata" in data:
            metadata = data["metadata"]
        return metadata

    def validate_structure(self, data: Dict, expected_keys: List[str]) -> Dict[str, bool]:
        """Validate JSON structure against expected keys"""
        validation = {}
        for key in expected_keys:
            validation[key] = key in data
        return validation

    def get_nested_value(self, data: Dict, path: str, default: Any = None) -> Any:
        """Get nested value from JSON using dot notation path"""
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def find_by_pattern(self, data: Dict, pattern: str) -> List[Any]:
        """Find all values matching a pattern in JSON structure"""
        results = []
        pattern_lower = pattern.lower()

        def search_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if pattern_lower in key.lower():
                        results.append({"path": f"{path}.{key}", "value": value})
                    search_recursive(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    search_recursive(item, f"{path}[{i}]")
            elif isinstance(obj, str) and pattern_lower in obj.lower():
                results.append({"path": path, "value": obj})

        search_recursive(data)
        return results
