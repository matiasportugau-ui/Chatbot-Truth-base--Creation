"""
Unit Tests: Catalog Loading
============================

Tests for catalog and data loading functions.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from quotation_calculator_v3 import _load_accessories_catalog, _load_bom_rules


class TestAccessoriesCatalogLoading:
    """Tests for accessories catalog loading"""
    
    def test_catalog_loads_successfully(self):
        """Test that catalog loads without errors"""
        catalog = _load_accessories_catalog()
        
        assert catalog is not None
        assert 'accesorios' in catalog
        assert 'indices' in catalog
    
    def test_catalog_has_items(self):
        """Test that catalog contains accessory items"""
        catalog = _load_accessories_catalog()
        
        accesorios = catalog['accesorios']
        assert len(accesorios) > 0
        assert len(accesorios) >= 90  # Should have ~97 items
    
    def test_catalog_structure(self):
        """Test catalog has expected structure"""
        catalog = _load_accessories_catalog()
        
        assert 'meta' in catalog
        assert 'accesorios' in catalog
        assert 'indices' in catalog
        
        # Check indices structure
        indices = catalog['indices']
        assert 'by_tipo' in indices
        assert 'by_compatibilidad' in indices
        assert 'by_uso' in indices
    
    def test_accessory_item_structure(self):
        """Test that accessory items have required fields"""
        catalog = _load_accessories_catalog()
        
        first_item = catalog['accesorios'][0]
        assert 'sku' in first_item
        assert 'nombre' in first_item
        assert 'tipo' in first_item
        assert 'precio_unit_iva_inc' in first_item
    
    def test_catalog_caching(self):
        """Test that catalog is cached after first load"""
        catalog1 = _load_accessories_catalog()
        catalog2 = _load_accessories_catalog()
        
        # Should be the same object (cached)
        assert catalog1 is catalog2


class TestBOMRulesLoading:
    """Tests for BOM rules loading"""
    
    def test_bom_rules_loads_successfully(self):
        """Test that BOM rules load without errors"""
        rules = _load_bom_rules()
        
        assert rules is not None
        assert 'sistemas' in rules
        assert 'autoportancia' in rules
    
    def test_bom_rules_has_sistemas(self):
        """Test that BOM rules contain sistemas"""
        rules = _load_bom_rules()
        
        sistemas = rules['sistemas']
        assert len(sistemas) >= 6  # Should have 6 sistemas
        
        # Check for expected sistemas
        assert 'techo_isodec_eps' in sistemas
        assert 'techo_isodec_pir' in sistemas
        assert 'techo_isoroof_3g' in sistemas
    
    def test_autoportancia_table_exists(self):
        """Test that autoportancia table exists and has data"""
        rules = _load_bom_rules()
        
        autoportancia = rules['autoportancia']
        assert 'tablas' in autoportancia
        
        tablas = autoportancia['tablas']
        assert 'ISODEC_EPS' in tablas
        assert 'ISODEC_PIR' in tablas
        assert 'ISOROOF_3G' in tablas
        assert 'ISOPANEL_EPS' in tablas
    
    def test_autoportancia_data_structure(self):
        """Test autoportancia table structure"""
        rules = _load_bom_rules()
        
        isodec_eps = rules['autoportancia']['tablas']['ISODEC_EPS']
        
        # Check thickness entries
        assert '100' in isodec_eps
        assert '150' in isodec_eps
        
        # Check data structure
        thickness_100 = isodec_eps['100']
        assert 'luz_max_m' in thickness_100
        assert 'peso_kg_m2' in thickness_100
        assert thickness_100['luz_max_m'] > 0
    
    def test_bom_rules_caching(self):
        """Test that BOM rules are cached after first load"""
        rules1 = _load_bom_rules()
        rules2 = _load_bom_rules()
        
        # Should be the same object (cached)
        assert rules1 is rules2


@pytest.mark.unit
class TestCatalogErrorHandling:
    """Tests for error handling in catalog loading"""
    
    def test_accessories_catalog_exists(self):
        """Test that accessories catalog file exists"""
        # This test verifies the file path is correct
        try:
            catalog = _load_accessories_catalog()
            assert catalog is not None
        except FileNotFoundError as e:
            pytest.fail(f"Accessories catalog not found: {e}")
    
    def test_bom_rules_exists(self):
        """Test that BOM rules file exists"""
        # This test verifies the file path is correct
        try:
            rules = _load_bom_rules()
            assert rules is not None
        except FileNotFoundError as e:
            pytest.fail(f"BOM rules not found: {e}")


class TestCatalogDataQuality:
    """Tests for data quality in catalogs"""
    
    def test_all_accessories_have_prices(self):
        """Test that all accessories have valid prices"""
        catalog = _load_accessories_catalog()
        
        for item in catalog['accesorios']:
            assert 'precio_unit_iva_inc' in item
            assert item['precio_unit_iva_inc'] > 0
    
    def test_all_accessories_have_sku(self):
        """Test that all accessories have SKU"""
        catalog = _load_accessories_catalog()
        
        skus = []
        for item in catalog['accesorios']:
            assert 'sku' in item
            assert item['sku'] != ''
            skus.append(item['sku'])
        
        # Check for duplicate SKUs
        assert len(skus) == len(set(skus)), "Found duplicate SKUs"
    
    def test_autoportancia_values_reasonable(self):
        """Test that autoportancia values are reasonable"""
        rules = _load_bom_rules()
        
        for family, thicknesses in rules['autoportancia']['tablas'].items():
            for thickness, data in thicknesses.items():
                luz_max = data['luz_max_m']
                peso = data['peso_kg_m2']
                
                # Sanity checks
                assert luz_max > 0, f"{family} {thickness}: luz_max must be > 0"
                assert luz_max < 20, f"{family} {thickness}: luz_max seems too large"
                assert peso > 0, f"{family} {thickness}: peso must be > 0"
                assert peso < 100, f"{family} {thickness}: peso seems too large"
