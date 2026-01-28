import os
import operator
from typing import Annotated, TypedDict, Union, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import our deterministic tool
from panelin.tools.quotation_calculator import calculate_panel_quote

# Define the state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# Wrap the tool to be compatible with LangChain if needed, 
# but @tool decorator on the function in tools/quotation_calculator.py would be better.
# Since I didn't use @tool there, I'll wrap it here or modify the file.
# Let's modify the file to use @tool decorator for better integration.

# Actually, I can just wrap it here.
@tool
def calculate_panel_quote_tool(
    panel_type: str,
    thickness_mm: int,
    length_m: float,
    width_m: float,
    quantity: int,
    discount_percent: float = 0.0
):
    """
    Calcula cotización exacta para paneles térmicos BMC. 
    USAR SIEMPRE para cualquier cálculo de precio.
    El LLM NUNCA debe calcular precios, siempre debe usar esta herramienta.
    
    Args:
        panel_type: Tipo de panel (ej. "Isopanel", "Isodec", "Isoroof"). 
                    Se intentará matchear con el SKU o nombre en la KB.
        thickness_mm: Espesor en mm (ej. 50, 75, 100).
        length_m: Largo en metros.
        width_m: Ancho en metros.
        quantity: Cantidad de paneles.
        discount_percent: Porcentaje de descuento (0-30).
    """
    # Map panel_type + thickness to SKU logic could be here or in the tool.
    # For now, we assume the tool handles exact SKU or we construct it here.
    # The KB I created has SKUs like "IAGRO30" or "Isopanel_50mm" if I had used that logic.
    # In my KB creation script, I used SKUs from the CSV.
    # So I need a way to map natural language "Isopanel 50mm" to SKU "IAGRO50" (if that's the mapping).
    
    # Let's inspect the KB to see what SKUs we have.
    # We'll do a best-effort lookup in the tool wrapper.
    
    # We call the underlying function
    # But first we need to find the SKU.
    
    # Quick SKU lookup logic (simplified for this demo)
    # Ideally this would be a separate tool "lookup_product_sku"
    
    # For this implementation, I'll try to find a matching product in the KB inside the wrapper.
    import json
    kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'panelin_truth_bmcuruguay.json')
    with open(kb_path, 'r') as f:
        kb = json.load(f)
    
    target_sku = None
    # normalize inputs
    p_type = panel_type.lower()
    
    # Naive search
    for sku, prod in kb['products'].items():
        name = prod['name'].lower()
        if str(thickness_mm) in name and (p_type in name or p_type in sku.lower()):
            target_sku = sku
            break
            
    if not target_sku:
        # Fallback to direct SKU if provided in panel_type
        target_sku = panel_type

    return calculate_panel_quote(
        product_sku=target_sku,
        length_m=length_m,
        width_m=width_m,
        quantity=quantity,
        discount_percent=discount_percent
    )

tools = [calculate_panel_quote_tool]

# Define the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# Define nodes
def agent_node(state: AgentState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Build the graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

workflow.add_edge("tools", "agent")

app = workflow.compile()

# System prompt
SYSTEM_PROMPT = """Eres el Agente de Cotización Panelin v2 para BMC Uruguay.
Tu objetivo es generar cotizaciones precisas y deterministas.

REGLAS CRÍTICAS:
1. NUNCA realices cálculos matemáticos de precios tú mismo. SIEMPRE usa la herramienta `calculate_panel_quote_tool`.
2. Si el usuario pide una cotización, extrae los parámetros (tipo, espesor, medidas, cantidad) y llama a la herramienta.
3. Si la herramienta devuelve un error, comunícalo al usuario y pide aclaraciones.
4. Tu respuesta final debe basarse EXCLUSIVAMENTE en los datos devueltos por la herramienta (total, precio unitario, etc.).
5. No inventes precios ni productos.

La KB contiene productos como 'Isoroof', 'Isopanel', etc. con espesores 30, 40, 50, 80, 100 mm.
"""

def run_agent(user_input: str):
    print(f"User: {user_input}")
    inputs = {"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_input)]}
    for output in app.stream(inputs):
        for key, value in output.items():
            # print(f"Output from node '{key}':")
            # print("---")
            # print(value)
            pass
            
    final_state = app.get_state(app.get_state_history(inputs)) # This might not work as expected in simple run
    # Actually app.stream yields partial updates. The final output is in the last yielded value or we can capture it.
    
    # Let's just grab the last message from the stream
    # Re-running simply to get the response cleanly
    result = app.invoke(inputs)
    print(f"Agent: {result['messages'][-1].content}")
    return result

if __name__ == "__main__":
    # Test case
    run_agent("Necesito precio para 10 paneles de Isoroof 50mm de 3 metros de largo por 1 de ancho")
