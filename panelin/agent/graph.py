import os
from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from panelin.tools.quotation_calculator import calculate_panel_quote

def get_agent():
    """
    Creates the Panelin Quotation Agent v2.
    """
    # Configure the LLM
    # In a real scenario, API key would be loaded from environment
    # We default to gpt-4o-mini as recommended
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Define tools
    tools = [calculate_panel_quote]

    # Initialize memory
    memory = MemorySaver()

    # Create the agent
    graph = create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=memory,
        state_modifier="""You are the Panelin Quotation Agent. 
Your GOAL is to provide accurate price quotations for BMC Uruguay thermal panels.

CRITICAL RULES:
1. NEVER calculate prices yourself. You are bad at math.
2. ALWAYS use the `calculate_panel_quote` tool for any pricing query.
3. Extract parameters from the user's request (type, thickness, dimensions).
4. If parameters are missing, ask the user for clarification.
5. Provide the final price based ONLY on the tool output.

Products available: Isopanel, Isodec, Isoroof, Isowall.
thicknesses: 50mm, 75mm, 100mm, 150mm, 200mm, 250mm.
"""
    )

    return graph

if __name__ == "__main__":
    # Simple test execution (requires OPENAI_API_KEY)
    if "OPENAI_API_KEY" in os.environ:
        agent = get_agent()
        print("Agent initialized successfully.")
    else:
        print("Agent initialized (mock mode - set OPENAI_API_KEY to run).")
