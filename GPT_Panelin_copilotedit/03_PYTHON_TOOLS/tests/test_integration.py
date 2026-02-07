"""
Integration Tests
=================

End-to-end tests for complete quotation workflows.
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from quotation_calculator_v3 import (
    validate_autoportancia,
    _load_accessories_catalog,
    _load_bom_rules
)


@pytest.mark.integration
class TestAutoportanciaIntegration:
    """Integration tests for autoportancia validation with real data"""
    
    def test_validation_with_real_bom_rules(self):
        """Test validation using real BOM rules file"""
        # Load real BOM rules
        rules = _load_bom_rules()
        
        # Validate against real data
        result = validate_autoportancia("ISODEC_EPS", 100, 4.5)
        
        assert result['is_valid'] is True
        assert result['span_max_m'] == 5.5  # From real data
        assert abs(result['span_max_safe_m'] - 4.675) < 0.01
    
    def test_all_product_families_validate(self):
        """Test that all product families in BOM rules can be validated"""
        rules = _load_bom_rules()
        families = rules['autoportancia']['tablas'].keys()
        
        for family in families:
            # Test with a reasonable span
            result = validate_autoportancia(family, 100, 4.0)
            
            # Should return a result (even if validation fails)
            assert 'is_valid' in result
            assert 'recommendation' in result


@pytest.mark.integration
class TestCatalogIntegration:
    """Integration tests for catalog loading and usage"""
    
    def test_accessories_catalog_loads(self):
        """Test that real accessories catalog loads"""
        catalog = _load_accessories_catalog()
        
        assert len(catalog['accesorios']) >= 90
        assert 'gotero_frontal' in catalog['indices']['by_tipo']
    
    def test_bom_rules_and_catalog_consistency(self):
        """Test that BOM rules and catalog are consistent"""
        rules = _load_bom_rules()
        catalog = _load_accessories_catalog()
        
        # Both should load successfully
        assert rules is not None
        assert catalog is not None
        
        # BOM rules should have sistemas
        assert len(rules['sistemas']) >= 6
        
        # Catalog should have accessories
        assert len(catalog['accesorios']) >= 90


@pytest.mark.integration
class TestValidationWorkflow:
    """Integration tests for validation workflow"""
    
    def test_validate_then_suggest_alternative(self):
        """Test workflow: validate span, get alternative suggestion"""
        # Step 1: Validate a span that exceeds limit
        result1 = validate_autoportancia("ISODEC_EPS", 100, 8.0)
        
        assert result1['is_valid'] is False
        assert len(result1['alternative_thicknesses']) > 0
        
        # Step 2: Use suggested alternative
        suggested_thickness = result1['alternative_thicknesses'][0]
        result2 = validate_autoportancia("ISODEC_EPS", suggested_thickness, 8.0)
        
        # Should now be valid
        assert result2['is_valid'] is True
    
    def test_iterate_through_thicknesses(self):
        """Test finding minimum thickness for a given span"""
        target_span = 7.0
        thicknesses = [100, 150, 200, 250]
        
        for thickness in thicknesses:
            result = validate_autoportancia("ISODEC_EPS", thickness, target_span)
            if result['is_valid']:
                # Found minimum thickness
                assert thickness >= 150  # 7.0m requires at least 150mm
                break
        else:
            pytest.fail("No valid thickness found for 7.0m span")


@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Performance tests for integration scenarios"""
    
    def test_validation_performance(self):
        """Test that validation is fast enough"""
        import time
        
        start = time.time()
        for _ in range(100):
            validate_autoportancia("ISODEC_EPS", 100, 4.5)
        elapsed = time.time() - start
        
        # Should complete 100 validations in less than 1 second
        assert elapsed < 1.0, f"Too slow: {elapsed}s for 100 validations"
    
    def test_catalog_loading_performance(self):
        """Test that catalog loading (with cache) is fast"""
        import time
        
        # First load (cold cache)
        start = time.time()
        _load_accessories_catalog()
        _load_bom_rules()
        cold_time = time.time() - start
        
        # Subsequent loads (warm cache)
        start = time.time()
        for _ in range(100):
            _load_accessories_catalog()
            _load_bom_rules()
        warm_time = time.time() - start
        
        # Cached loads should be extremely fast
        assert warm_time < 0.1, f"Cached loads too slow: {warm_time}s"


@pytest.mark.integration
class TestDataConsistency:
    """Tests for data consistency across modules"""
    
    def test_thickness_options_match_bom_rules(self):
        """Test that thickness options in BOM rules are consistent"""
        rules = _load_bom_rules()
        
        families = rules['autoportancia']['tablas']
        
        for family, thicknesses in families.items():
            # All families should have multiple thickness options
            assert len(thicknesses) >= 3, f"{family} has too few thickness options"
            
            # Thicknesses should be in ascending order
            thickness_values = [int(t) for t in thicknesses.keys()]
            assert thickness_values == sorted(thickness_values)
    
    def test_span_values_increase_with_thickness(self):
        """Test that span capacity increases with thickness"""
        rules = _load_bom_rules()
        
        for family, thicknesses in rules['autoportancia']['tablas'].items():
            thickness_list = sorted([int(t) for t in thicknesses.keys()])
            
            prev_luz_max = 0
            for thickness in thickness_list:
                luz_max = thicknesses[str(thickness)]['luz_max_m']
                
                # Luz max should increase (or stay same) with thickness
                assert luz_max >= prev_luz_max, f"{family}: span should increase with thickness"
                prev_luz_max = luz_max


@pytest.mark.integration
class TestRealWorldScenarios:
    """Tests based on real-world usage scenarios"""
    
    def test_typical_roof_span(self):
        """Test typical residential roof span (4-5m)"""
        result = validate_autoportancia("ISODEC_EPS", 100, 4.5)
        assert result['is_valid'] is True
    
    def test_typical_commercial_span(self):
        """Test typical commercial span (6-8m)"""
        # 100mm won't work
        result1 = validate_autoportancia("ISODEC_EPS", 100, 7.0)
        assert result1['is_valid'] is False
        
        # 150mm should work
        result2 = validate_autoportancia("ISODEC_EPS", 150, 7.0)
        assert result2['is_valid'] is True
    
    def test_industrial_span(self):
        """Test industrial span (8-10m)"""
        # Requires thick panel
        result = validate_autoportancia("ISODEC_EPS", 250, 9.0)
        assert result['is_valid'] is True
    
    def test_minimum_span(self):
        """Test minimum practical span (2-3m)"""
        result = validate_autoportancia("ISOROOF_3G", 30, 2.5)
        assert result['is_valid'] is True
