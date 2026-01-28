from typing import Annotated, Literal, TypedDict, Union
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from panelin.tools.quotation_calculator import calculate_panel_quote, lookup_product_specs

# Define state
class AgentState(TypedDict):
    messages: list

# Define tools
@tool
def calculate_quote(
    panel_type: Literal["Isopanel", "Isodec", "Isoroof"],
    thickness_mm: int,
    length_m: float,
    width_m: float,
    quantity: int,
    discount_percent: float = 0.0
) -> str:
    """
    Calcula cotización exacta para paneles térmicos BMC. 
    USAR SIEMPRE para cualquier cálculo de precio.
    """
    try:
        result = calculate_panel_quote(
            panel_type=panel_type,
            thickness_mm=thickness_mm,
            length_m=length_m,
            width_m=width_m,
            quantity=quantity,
            discount_percent=discount_percent
        )
        return str(result)
    except Exception as e:
        return f"Error en cálculo: {str(e)}"

@tool
def lookup_specs(panel_type: str) -> str:
    """
    Busca especificaciones de productos para ayudar a elegir el correcto.
    """
    try:
        specs = lookup_product_specs(panel_type)
        return str(specs)
    except Exception as e:
        return f"Error buscando specs: {str(e)}"

tools = [calculate_quote, lookup_specs]

# Define LLM with tools
# Note: In a real deployment, ensure OPENAI_API_KEY is set
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) 
llm_with_tools = llm.bind_tools(tools)

# Define nodes
def agent_node(state: AgentState):
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "__end__"

# Define graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

# Compile
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    print("Agent Graph compiled successfully.")
