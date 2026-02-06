"""
Integration Tests for Panelin Agent V2
======================================

Tests for the complete agent flow, ensuring the architecture principle
that LLM only extracts parameters and never calculates.
"""

import pytest
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.quotation_calculator import (
    calculate_panel_quote,
    validate_quotation,
    TOOL_DEFINITIONS as CALC_TOOLS,
)
from tools.product_lookup import (
    find_product_by_query,
    TOOL_DEFINITIONS as LOOKUP_TOOLS,
)

# Check if LangGraph is available for full integration tests
try:
    from agent.panelin_agent import (
        PanelinQuotationAgent,
        create_agent,
        SYSTEM_PROMPT,
    )
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


class TestToolDefinitions:
    """Test tool definitions are correctly structured for LLM"""
    
    def test_calc_tool_has_strict_schema(self):
        """Calculate quote tool should have strict=True"""
        calc_tool = next(
            t for t in CALC_TOOLS if t["name"] == "calculate_panel_quote"
        )
        assert calc_tool["strict"] == True
    
    def test_calc_tool_has_required_params(self):
        """Calculate quote tool has required parameters"""
        calc_tool = next(
            t for t in CALC_TOOLS if t["name"] == "calculate_panel_quote"
        )
        required = calc_tool["parameters"]["required"]
        
        assert "product_id" in required
        assert "length_m" in required
        assert "width_m" in required
    
    def test_lookup_tool_has_schema(self):
        """Lookup tool has proper schema"""
        lookup_tool = next(
            t for t in LOOKUP_TOOLS if t["name"] == "find_product_by_query"
        )
        
        assert "parameters" in lookup_tool
        assert "query" in lookup_tool["parameters"]["properties"]


class TestSystemPrompt:
    """Test system prompt enforces architecture principles"""
    
    @pytest.mark.skipif(not LANGGRAPH_AVAILABLE, reason="LangGraph not installed")
    def test_prompt_prohibits_llm_calculations(self):
        """System prompt should forbid LLM from calculating"""
        prompt = SYSTEM_PROMPT.lower()
        
        assert "nunca calcules" in prompt or "never calculate" in prompt.lower()
        assert "nunca" in prompt or "never" in prompt.lower()
    
    @pytest.mark.skipif(not LANGGRAPH_AVAILABLE, reason="LangGraph not installed")
    def test_prompt_requires_tool_usage(self):
        """System prompt should require tool usage for calculations"""
        prompt = SYSTEM_PROMPT.lower()
        
        assert "herramienta" in prompt or "tool" in prompt
        assert "calculate_panel_quote" in SYSTEM_PROMPT


class TestAgentFallback:
    """Test agent fallback mode (without API)"""
    
    @pytest.mark.skipif(not LANGGRAPH_AVAILABLE, reason="LangGraph not installed")
    def test_agent_initialization(self):
        """Agent should initialize without API key in fallback mode"""
        agent = PanelinQuotationAgent()
        assert agent is not None
    
    @pytest.mark.skipif(not LANGGRAPH_AVAILABLE, reason="LangGraph not installed")
    def test_fallback_product_search(self):
        """Fallback mode should still search products"""
        agent = PanelinQuotationAgent()
        result = agent._fallback_invoke("panel para techo 100mm")
        
        assert "response" in result
        assert result["validation_passed"] == True


class TestEndToEndFlow:
    """Test end-to-end quotation flow"""
    
    def test_product_to_quote_flow(self):
        """Complete flow: search → lookup → calculate"""
        # Step 1: User query - find products
        query = "necesito panel isopanel de 100mm para una pared"
        products = find_product_by_query(query, max_results=1)
        
        assert len(products) > 0
        product = products[0]
        
        # Step 2: Get exact product specs
        product_id = product["product_id"]
        
        # Step 3: Calculate quote (simulating LLM extracting dimensions)
        result = calculate_panel_quote(
            product_id=product_id,
            length_m=6.0,
            width_m=4.0,
            quantity=1,
            include_tax=True
        )
        
        # Step 4: Validate result
        is_valid, errors = validate_quotation(result)
        
        assert is_valid == True
        assert result["calculation_verified"] == True
        assert result["total_usd"] > 0
    
    def test_complex_quote_flow(self):
        """Complex flow with accessories and discount"""
        # Search for roof panel
        products = find_product_by_query("isodec para techo", max_results=1)
        product = products[0]
        
        # Calculate with all options
        result = calculate_panel_quote(
            product_id=product["product_id"],
            length_m=10.0,
            width_m=8.0,
            quantity=2,
            discount_percent=5.0,
            include_accessories=True,
            include_tax=True,
            installation_type="techo"
        )
        
        assert result["calculation_verified"] == True
        assert result["discount_percent"] == 5.0
        assert result["accessories"] is not None


class TestCalculationVerification:
    """Test that calculation verification works correctly"""
    
    def test_all_quotes_have_verification(self):
        """Every quote should have verification flag"""
        products = [
            "ISOPANEL_EPS_50mm",
            "ISODEC_EPS_100mm",
            "ISOROOF_3G"
        ]
        
        for product_id in products:
            try:
                result = calculate_panel_quote(
                    product_id=product_id,
                    length_m=5.0,
                    width_m=4.0,
                    quantity=1
                )
                
                assert result["calculation_verified"] == True
                assert result["calculation_method"] == "python_decimal_deterministic"
            except ValueError:
                # Some products may have different min/max lengths
                pass
    
    def test_verification_catches_tampering(self):
        """Verification should catch if someone tampers with results"""
        result = calculate_panel_quote(
            product_id="ISOPANEL_EPS_50mm",
            length_m=6.0,
            width_m=4.0,
            quantity=1
        )
        
        # Original is valid
        is_valid, _ = validate_quotation(result)
        assert is_valid == True
        
        # Tamper with the verification flag
        result["calculation_verified"] = False
        is_valid, errors = validate_quotation(result)
        assert is_valid == False
        assert any("CRITICAL" in e for e in errors)
        
        # Tamper with the method
        result["calculation_verified"] = True
        result["calculation_method"] = "gpt-4-mental-math"
        is_valid, errors = validate_quotation(result)
        assert is_valid == False


class TestConcurrentQuotations:
    """Test concurrent quotation handling"""
    
    def test_multiple_quotes_independent(self):
        """Multiple quotes should be independent"""
        quote1 = calculate_panel_quote(
            product_id="ISOPANEL_EPS_50mm",
            length_m=6.0,
            width_m=4.0,
            quantity=1
        )
        
        quote2 = calculate_panel_quote(
            product_id="ISODEC_EPS_100mm",
            length_m=8.0,
            width_m=6.0,
            quantity=2
        )
        
        # Quotes should have different IDs
        assert quote1["quotation_id"] != quote2["quotation_id"]
        
        # Quotes should be independently valid
        is_valid1, _ = validate_quotation(quote1)
        is_valid2, _ = validate_quotation(quote2)
        
        assert is_valid1 == True
        assert is_valid2 == True


class TestErrorHandling:
    """Test error handling in agent flow"""
    
    def test_graceful_product_not_found(self):
        """Should handle product not found gracefully"""
        with pytest.raises(ValueError):
            calculate_panel_quote(
                product_id="NONEXISTENT_PRODUCT",
                length_m=6.0,
                width_m=4.0,
                quantity=1
            )
    
    def test_graceful_invalid_params(self):
        """Should handle invalid parameters gracefully"""
        # Negative quantity
        with pytest.raises(ValueError):
            calculate_panel_quote(
                product_id="ISOPANEL_EPS_50mm",
                length_m=6.0,
                width_m=4.0,
                quantity=-1
            )
        
        # Negative discount
        with pytest.raises(ValueError):
            calculate_panel_quote(
                product_id="ISOPANEL_EPS_50mm",
                length_m=6.0,
                width_m=4.0,
                quantity=1,
                discount_percent=-5.0
            )


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
