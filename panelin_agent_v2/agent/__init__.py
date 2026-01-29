"""
Panelin Agent V2 - Single Agent Architecture
=============================================

This module implements a single-agent architecture using LangGraph 1.0.
The agent uses deterministic tools for all calculations - the LLM only 
performs natural language understanding and parameter extraction.
"""

from .panelin_agent import (
    PanelinQuotationAgent,
    create_agent,
    run_quotation_query,
)

__all__ = [
    "PanelinQuotationAgent",
    "create_agent",
    "run_quotation_query",
]
