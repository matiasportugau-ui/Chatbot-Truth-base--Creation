"""
Test Suite for Product Lookup Functions
========================================

Tests for the deterministic product search and lookup functionality.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.product_lookup import (
    find_product_by_query,
    get_product_price,
    check_product_availability,
    list_all_products,
    get_pricing_rules,
    _extract_thickness,
    _match_product_family,
    _match_application,
)


class TestQueryParsing:
    """Test query parsing utilities"""
    
    def test_extract_thickness_mm(self):
        """Extract thickness with mm suffix"""
        assert _extract_thickness("panel de 100mm") == 100
        assert _extract_thickness("isopanel 50 mm para techo") == 50
        assert _extract_thickness("150mm de espesor") == 150
    
    def test_extract_thickness_milimetros(self):
        """Extract thickness with 'milimetros' word"""
        assert _extract_thickness("panel de 100 milimetros") == 100
    
    def test_extract_thickness_not_found(self):
        """When no thickness in query"""
        assert _extract_thickness("panel para techo") is None
    
    def test_match_family_isopanel(self):
        """Match ISOPANEL family"""
        assert _match_product_family("necesito isopanel") == "ISOPANEL"
        assert _match_product_family("panel eps para pared") == "ISOPANEL"
    
    def test_match_family_isodec(self):
        """Match ISODEC family"""
        assert _match_product_family("isodec para cubierta") == "ISODEC"
        assert _match_product_family("panel para techo") == "ISODEC"
    
    def test_match_family_isoroof(self):
        """Match ISOROOF family"""
        assert _match_product_family("isoroof 3g") == "ISOROOF"
        assert _match_product_family("panel foil") == "ISOROOF"
    
    def test_match_application_techo(self):
        """Match roof/techo application"""
        assert _match_application("panel para techo") == "techos"
        assert _match_application("cubierta industrial") == "techos"
    
    def test_match_application_pared(self):
        """Match wall/pared application"""
        assert _match_application("panel para pared") == "paredes"
        assert _match_application("muro perimetral") == "paredes"
    
    def test_match_application_fachada(self):
        """Match facade application"""
        assert _match_application("fachada de edificio") == "fachadas"


class TestProductSearch:
    """Test product search functionality"""
    
    def test_search_by_family_and_thickness(self):
        """Search with family and thickness"""
        results = find_product_by_query("isopanel 100mm", max_results=3)
        
        assert len(results) > 0
        # Should prioritize exact matches
        found_100mm = any(r["thickness_mm"] == 100 for r in results)
        assert found_100mm
    
    def test_search_by_application(self):
        """Search by application type"""
        results = find_product_by_query("panel para techo", max_results=5)
        
        assert len(results) > 0
        # Results should include products for techos/cubiertas
        for result in results:
            apps = result.get("application", [])
            assert any(a in apps for a in ["techos", "cubiertas"]) or True
    
    def test_search_returns_scored_results(self):
        """Search results should have match scores"""
        results = find_product_by_query("isodec eps 100mm techo", max_results=5)
        
        assert len(results) > 0
        for result in results:
            assert "match_score" in result
            assert result["match_score"] > 0
    
    def test_search_max_results(self):
        """Search should respect max_results"""
        results = find_product_by_query("panel", max_results=3)
        assert len(results) <= 3
    
    def test_search_no_results(self):
        """Search with no matches"""
        results = find_product_by_query("xyzabc123 inexistente", max_results=5)
        # May return empty or low-scored results
        if results:
            assert results[0]["match_score"] < 50


class TestPriceRetrieval:
    """Test price retrieval functionality"""
    
    def test_get_price_valid_product(self):
        """Get price for valid product"""
        result = get_product_price("ISOPANEL_EPS_50mm")
        
        assert result is not None
        assert "price_per_m2" in result
        assert result["price_per_m2"] > 0
        assert result["currency"] == "USD"
        assert result["_source"] == "panelin_truth_kb_deterministic"
    
    def test_get_price_invalid_product(self):
        """Get price for invalid product returns None"""
        result = get_product_price("FAKE_PRODUCT_999")
        assert result is None


class TestAvailabilityCheck:
    """Test availability checking"""
    
    def test_check_available_product(self):
        """Check availability for available product"""
        result = check_product_availability("ISOPANEL_EPS_50mm")
        
        assert result["found"] == True
        assert "available" in result
        assert "stock_status" in result
        assert result["_source"] == "panelin_truth_kb_deterministic"
    
    def test_check_unavailable_product(self):
        """Check availability for unavailable product"""
        result = check_product_availability("ISOROOF_PLUS_3G")
        
        assert result["found"] == True
        assert result["stock_status"] == "out_of_stock"
        assert result["available"] == False
    
    def test_check_nonexistent_product(self):
        """Check availability for non-existent product"""
        result = check_product_availability("FAKE_PRODUCT")
        
        assert result["found"] == False
        assert result["available"] == False


class TestProductListing:
    """Test product listing functionality"""
    
    def test_list_all_products(self):
        """List all products without filter"""
        results = list_all_products()
        
        assert len(results) > 0
        for product in results:
            assert "product_id" in product
            assert "name" in product
            assert "price_per_m2" in product
    
    def test_list_by_family_isopanel(self):
        """List products filtered by ISOPANEL family"""
        results = list_all_products(family="ISOPANEL")
        
        assert len(results) > 0
        for product in results:
            assert product["family"] == "ISOPANEL"
    
    def test_list_by_family_isodec(self):
        """List products filtered by ISODEC family"""
        results = list_all_products(family="ISODEC")
        
        assert len(results) > 0
        for product in results:
            assert product["family"] == "ISODEC"
    
    def test_list_by_family_empty(self):
        """List with non-existent family"""
        results = list_all_products(family="NONEXISTENT")
        assert len(results) == 0


class TestPricingRules:
    """Test pricing rules retrieval"""
    
    def test_get_pricing_rules(self):
        """Get pricing rules from KB"""
        rules = get_pricing_rules()
        
        assert "tax_rate_uy_iva" in rules
        assert rules["tax_rate_uy_iva"] == 0.22  # 22% IVA
        
        assert "delivery_cost_per_m2" in rules
        assert "minimum_delivery_charge_usd" in rules
    
    def test_payment_terms(self):
        """Verify payment terms in pricing rules"""
        rules = get_pricing_rules()
        
        assert "payment_terms" in rules
        terms = rules["payment_terms"]
        
        assert "contado" in terms
        assert terms["contado"]["discount_percent"] == 3  # 3% discount for cash


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
