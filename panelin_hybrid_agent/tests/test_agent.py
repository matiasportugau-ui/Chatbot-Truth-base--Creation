"""
Test suite for Panelin Hybrid Agent.

Tests the agent's ability to:
1. Extract parameters from natural language
2. Call the correct tools
3. Format responses appropriately
4. Never calculate directly (always use tools)
"""

import pytest
import json
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from panelin_hybrid_agent.agent import PanelinAgent, SYSTEM_PROMPT
from panelin_hybrid_agent.tools.quotation_calculator import (
    calculate_panel_quote,
    validate_quotation,
)


class TestPanelinAgentDirect:
    """Test agent direct quotation method (no LLM)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = PanelinAgent()
    
    def test_direct_quote_basic(self):
        """Test direct quotation without LLM."""
        result = self.agent.quote_direct(
            panel_type="Isodec_EPS",
            thickness_mm=100,
            length_m=6.0,
            quantity=10
        )
        
        assert result['success'] == True
        assert result['quotation']['calculation_verified'] == True
        assert result['validation']['is_valid'] == True
    
    def test_direct_quote_with_options(self):
        """Test direct quotation with all options."""
        result = self.agent.quote_direct(
            panel_type="Isopanel_EPS",
            thickness_mm=50,
            length_m=4.0,
            quantity=20,
            base_type="metal",
            discount_percent=10.0,
            include_fijaciones=True,
            include_perfileria=True
        )
        
        assert result['success'] == True
        assert result['quotation']['discount_usd'] > 0
    
    def test_direct_quote_error_handling(self):
        """Test direct quotation error handling."""
        result = self.agent.quote_direct(
            panel_type="InvalidPanel",
            thickness_mm=100,
            length_m=6.0,
            quantity=10
        )
        
        assert result['success'] == False
        assert 'error' in result


class TestAgentFallback:
    """Test agent fallback behavior when LangGraph unavailable."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = PanelinAgent()
    
    def test_fallback_quotation_request(self):
        """Test fallback for quotation request."""
        response = self.agent.chat("Necesito cotizar paneles")
        
        # Should ask for parameters
        assert 'tipo de panel' in response['response'].lower() or \
               'panel' in response['response'].lower()
    
    def test_fallback_product_lookup(self):
        """Test fallback for product lookup."""
        response = self.agent.chat("Qué productos tienen?")
        
        # Should return some products
        assert 'producto' in response['response'].lower() or \
               'catálogo' in response['response'].lower() or \
               response.get('products')


class TestSystemPrompt:
    """Test system prompt configuration."""
    
    def test_system_prompt_contains_critical_rules(self):
        """System prompt must contain critical rules."""
        assert "NUNCA" in SYSTEM_PROMPT
        assert "calculate_panel_quote" in SYSTEM_PROMPT
        assert "deterministic" in SYSTEM_PROMPT.lower() or \
               "herramientas" in SYSTEM_PROMPT
    
    def test_system_prompt_contains_tool_names(self):
        """System prompt must reference all tools."""
        assert "calculate_panel_quote" in SYSTEM_PROMPT
        assert "lookup_product_specs" in SYSTEM_PROMPT
        assert "check_inventory_shopify" in SYSTEM_PROMPT


class TestToolSchemas:
    """Test tool schemas for LLM structured outputs."""
    
    def test_calculate_quote_schema(self):
        """Test calculate_panel_quote tool schema."""
        from panelin_hybrid_agent.models.types import TOOL_SCHEMAS
        
        schema = TOOL_SCHEMAS['calculate_panel_quote']
        
        assert schema['name'] == 'calculate_panel_quote'
        assert schema['strict'] == True
        
        params = schema['parameters']['properties']
        assert 'panel_type' in params
        assert 'thickness_mm' in params
        assert 'length_m' in params
        assert 'quantity' in params
        
        # Check required fields
        required = schema['parameters']['required']
        assert 'panel_type' in required
        assert 'thickness_mm' in required
        assert 'length_m' in required
        assert 'quantity' in required
    
    def test_lookup_specs_schema(self):
        """Test lookup_product_specs tool schema."""
        from panelin_hybrid_agent.models.types import TOOL_SCHEMAS
        
        schema = TOOL_SCHEMAS['lookup_product_specs']
        
        assert schema['name'] == 'lookup_product_specs'
        assert 'panel_type' in schema['parameters']['properties']


class TestIntegration:
    """Integration tests for complete quotation flow."""
    
    def test_complete_quotation_flow(self):
        """Test complete quotation flow."""
        # 1. Calculate quotation
        quote_result = calculate_panel_quote(
            panel_type="Isodec_EPS",
            thickness_mm=100,
            length_m=6.0,
            quantity=10,
            include_fijaciones=True,
            include_perfileria=True
        )
        
        # 2. Validate quotation
        validation = validate_quotation(quote_result)
        
        # 3. Verify all checks pass
        assert validation['is_valid'] == True
        assert quote_result['calculation_verified'] == True
        
        # 4. Verify total makes sense
        assert quote_result['total_usd'] > quote_result['panels_subtotal_usd'] * 0.9
        assert quote_result['total_with_iva_usd'] > quote_result['total_usd']
    
    def test_quotation_with_all_options(self):
        """Test quotation with all optional parameters."""
        quote_result = calculate_panel_quote(
            panel_type="Isodec_PIR",
            thickness_mm=80,
            length_m=7.0,
            quantity=15,
            base_type="hormigon",
            discount_percent=15.0,
            include_fijaciones=True,
            include_perfileria=True
        )
        
        validation = validate_quotation(quote_result)
        
        assert validation['is_valid'] == True
        assert quote_result['fijaciones_subtotal_usd'] > 0
        assert quote_result['perfileria_subtotal_usd'] > 0
        assert quote_result['discount_usd'] > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_minimum_quantity(self):
        """Test with minimum quantity."""
        result = calculate_panel_quote(
            panel_type="Isodec_EPS",
            thickness_mm=100,
            length_m=2.5,
            quantity=1
        )
        
        assert result['calculation_verified'] == True
        assert result['quantity'] == 1
    
    def test_maximum_length(self):
        """Test with maximum panel length."""
        result = calculate_panel_quote(
            panel_type="Isodec_EPS",
            thickness_mm=100,
            length_m=14.0,  # Max length
            quantity=5
        )
        
        assert result['calculation_verified'] == True
        assert result['area_m2'] == pytest.approx(14.0 * 1.12 * 5, rel=0.01)
    
    def test_large_quantity(self):
        """Test with large quantity."""
        result = calculate_panel_quote(
            panel_type="Isopanel_EPS",
            thickness_mm=100,
            length_m=6.0,
            quantity=100
        )
        
        assert result['calculation_verified'] == True
        # Should handle large numbers without overflow
        assert result['total_usd'] > 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
