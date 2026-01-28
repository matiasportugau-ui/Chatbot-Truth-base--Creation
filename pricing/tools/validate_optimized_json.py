#!/usr/bin/env python3
"""
Validation script for optimized pricing JSON
Tests data integrity, index consistency, and structure
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Set

JSON_FILE = "pricing/out/bromyros_pricing_gpt_optimized.json"

class JSONValidator:
    """Validates the optimized pricing JSON"""
    
    def __init__(self, json_file: str):
        self.json_file = Path(json_file)
        self.data = None
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def load_json(self) -> bool:
        """Load and parse JSON file"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            return True
        except Exception as e:
            self.errors.append(f"Failed to load JSON: {e}")
            return False
    
    def validate_structure(self) -> bool:
        """Validate top-level JSON structure"""
        print("🔍 Validating structure...")
        
        required_keys = ["metadata", "indices", "familia_groups", "products"]
        for key in required_keys:
            if key not in self.data:
                self.errors.append(f"Missing required key: {key}")
        
        # Validate indices structure
        if "indices" in self.data:
            required_indices = ["by_sku", "by_familia", "by_sub_familia", "by_tipo"]
            for idx in required_indices:
                if idx not in self.data["indices"]:
                    self.errors.append(f"Missing index: indices.{idx}")
        
        if self.errors:
            return False
        
        print("   ✅ Structure valid")
        return True
    
    def validate_sku_uniqueness(self) -> bool:
        """Ensure all SKUs are unique"""
        print("🔍 Validating SKU uniqueness...")
        
        skus = [p["sku"] for p in self.data["products"]]
        sku_set = set(skus)
        
        if len(skus) != len(sku_set):
            duplicates = [sku for sku in sku_set if skus.count(sku) > 1]
            self.errors.append(f"Duplicate SKUs found: {duplicates}")
            return False
        
        print(f"   ✅ All {len(skus)} SKUs are unique")
        return True
    
    def validate_index_integrity(self) -> bool:
        """Validate that all indices reference valid products"""
        print("🔍 Validating index integrity...")
        
        product_skus = {p["sku"] for p in self.data["products"]}
        
        # Check by_sku index
        index_skus = set(self.data["indices"]["by_sku"].keys())
        if index_skus != product_skus:
            missing = product_skus - index_skus
            extra = index_skus - product_skus
            if missing:
                self.errors.append(f"Products missing from by_sku index: {missing}")
            if extra:
                self.errors.append(f"Extra SKUs in by_sku index: {extra}")
            return False
        
        # Check familia index references
        for familia, skus in self.data["indices"]["by_familia"].items():
            for sku in skus:
                if sku not in product_skus:
                    self.errors.append(f"by_familia[{familia}] references non-existent SKU: {sku}")
        
        # Check sub_familia index references
        for sub_familia, skus in self.data["indices"]["by_sub_familia"].items():
            for sku in skus:
                if sku not in product_skus:
                    self.errors.append(f"by_sub_familia[{sub_familia}] references non-existent SKU: {sku}")
        
        if self.errors:
            return False
        
        print(f"   ✅ All index references are valid")
        return True
    
    def validate_familia_groups(self) -> bool:
        """Validate familia groups structure and data"""
        print("🔍 Validating familia groups...")
        
        for familia, group in self.data["familia_groups"].items():
            required_fields = ["description", "sub_familia", "tipo", "product_count", "products"]
            for field in required_fields:
                if field not in group:
                    self.errors.append(f"familia_groups[{familia}] missing field: {field}")
            
            # Validate product count matches
            if "products" in group and "product_count" in group:
                actual_count = len(group["products"])
                declared_count = group["product_count"]
                if actual_count != declared_count:
                    self.errors.append(
                        f"familia_groups[{familia}] count mismatch: "
                        f"declared={declared_count}, actual={actual_count}"
                    )
        
        if self.errors:
            return False
        
        print(f"   ✅ All {len(self.data['familia_groups'])} familia groups valid")
        return True
    
    def validate_pricing_data(self) -> bool:
        """Validate pricing fields"""
        print("🔍 Validating pricing data...")
        
        products_with_prices = 0
        products_without_prices = 0
        
        for product in self.data["products"]:
            pricing = product.get("pricing", {})
            has_price = any([
                pricing.get("sale_iva_inc"),
                pricing.get("web_iva_inc"),
                pricing.get("cost_sin_iva")
            ])
            
            if has_price:
                products_with_prices += 1
            else:
                products_without_prices += 1
                self.warnings.append(f"Product {product['sku']} has no pricing data")
        
        print(f"   ✅ {products_with_prices} products with pricing")
        if products_without_prices > 0:
            print(f"   ⚠️  {products_without_prices} products without pricing")
        
        return True
    
    def validate_required_fields(self) -> bool:
        """Ensure all products have required fields"""
        print("🔍 Validating required fields...")
        
        required_product_fields = ["sku", "name", "familia", "sub_familia", "tipo", "specifications", "pricing"]
        
        for i, product in enumerate(self.data["products"]):
            for field in required_product_fields:
                if field not in product:
                    self.errors.append(f"Product {i} ({product.get('sku', 'UNKNOWN')}) missing field: {field}")
        
        if self.errors:
            return False
        
        print(f"   ✅ All products have required fields")
        return True
    
    def run_test_queries(self) -> bool:
        """Run example queries to test usability"""
        print("\n🧪 Running test queries...")
        
        tests_passed = 0
        tests_failed = 0
        
        # Test 1: Find product by SKU
        try:
            sku = "IAGRO30"
            if sku in self.data["indices"]["by_sku"]:
                product_ref = self.data["indices"]["by_sku"][sku]
                print(f"   ✅ Test 1: Found {sku} → familia={product_ref['familia']}")
                tests_passed += 1
            else:
                print(f"   ❌ Test 1: SKU {sku} not found")
                tests_failed += 1
        except Exception as e:
            print(f"   ❌ Test 1 failed: {e}")
            tests_failed += 1
        
        # Test 2: Find all products in a familia
        try:
            familia = "ISOROOF"
            if familia in self.data["indices"]["by_familia"]:
                skus = self.data["indices"]["by_familia"][familia]
                print(f"   ✅ Test 2: Found {len(skus)} products in familia {familia}")
                tests_passed += 1
            else:
                print(f"   ❌ Test 2: Familia {familia} not found")
                tests_failed += 1
        except Exception as e:
            print(f"   ❌ Test 2 failed: {e}")
            tests_failed += 1
        
        # Test 3: Find products by sub_familia
        try:
            sub_familia = "PIR"
            if sub_familia in self.data["indices"]["by_sub_familia"]:
                skus = self.data["indices"]["by_sub_familia"][sub_familia]
                print(f"   ✅ Test 3: Found {len(skus)} PIR products")
                tests_passed += 1
            else:
                print(f"   ❌ Test 3: Sub_familia {sub_familia} not found")
                tests_failed += 1
        except Exception as e:
            print(f"   ❌ Test 3 failed: {e}")
            tests_failed += 1
        
        # Test 4: Access familia_groups
        try:
            familia = "ISOROOF / FOIL"
            if familia in self.data["familia_groups"]:
                group = self.data["familia_groups"][familia]
                print(f"   ✅ Test 4: Familia group {familia} has {group['product_count']} products")
                tests_passed += 1
            else:
                print(f"   ⚠️  Test 4: Familia group {familia} not found (may not exist)")
                tests_passed += 1  # Not a failure
        except Exception as e:
            print(f"   ❌ Test 4 failed: {e}")
            tests_failed += 1
        
        print(f"\n   Tests: {tests_passed} passed, {tests_failed} failed")
        return tests_failed == 0
    
    def print_summary(self) -> None:
        """Print validation summary"""
        print("\n" + "="*60)
        print("📊 VALIDATION SUMMARY")
        print("="*60)
        
        if self.errors:
            print(f"❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        else:
            print("✅ No errors found")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Limit to 10
                print(f"   • {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more")
        else:
            print("✅ No warnings")
        
        print("\n" + "="*60)
        
        if not self.errors:
            print("✅ VALIDATION PASSED")
        else:
            print("❌ VALIDATION FAILED")
        print("="*60)
    
    def validate(self) -> bool:
        """Run all validations"""
        print("\n" + "="*60)
        print("🔍 OPTIMIZED JSON VALIDATION")
        print("="*60)
        print(f"File: {self.json_file}\n")
        
        if not self.load_json():
            self.print_summary()
            return False
        
        validations = [
            self.validate_structure,
            self.validate_sku_uniqueness,
            self.validate_index_integrity,
            self.validate_familia_groups,
            self.validate_pricing_data,
            self.validate_required_fields,
            self.run_test_queries
        ]
        
        all_passed = True
        for validation in validations:
            if not validation():
                all_passed = False
        
        self.print_summary()
        return all_passed

def main():
    validator = JSONValidator(JSON_FILE)
    success = validator.validate()
    
    if success:
        print("\n✅ JSON is ready for GPT deployment!")
    else:
        print("\n❌ Please fix errors before deployment")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
