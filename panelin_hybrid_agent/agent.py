"""
Panelin Hybrid Agent - LangGraph Implementation

Single-agent architecture with deterministic tools.

CRITICAL PRINCIPLE:
- LLM orquesta, código calcula
- The LLM NEVER performs arithmetic
- All calculations are done by Python tools with Decimal precision

Architecture:
1. User input → LLM extracts parameters (Structured Outputs)
2. Parameters → Deterministic Python tools
3. Tool results → LLM formats response
4. Response → Validation layer
5. Validated response → User
"""

import json
from typing import TypedDict, Annotated, Sequence, Literal, Optional, Dict, Any
from datetime import datetime, timezone

# LangGraph imports (conditional for development)
try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    from langgraph.prebuilt import ToolNode, tools_condition
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Warning: LangGraph not installed. Run: pip install langgraph")

# LangChain imports (conditional)
try:
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
    from langchain_core.tools import tool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Warning: LangChain not installed. Run: pip install langchain-core")

# Local imports
from .tools.quotation_calculator import (
    calculate_panel_quote,
    lookup_product_specs,
    validate_quotation,
    calculate_fijaciones,
    calculate_perfileria,
    QuotationResult,
)
from .tools.inventory_tools import check_inventory_shopify
from .models.types import TOOL_SCHEMAS


# === Agent State ===

class AgentState(TypedDict):
    """State for the Panelin quotation agent."""
    messages: Annotated[Sequence, add_messages] if LANGGRAPH_AVAILABLE else Sequence
    current_quotation: Optional[QuotationResult]
    validation_result: Optional[Dict[str, Any]]
    error: Optional[str]


# === System Prompt ===

SYSTEM_PROMPT = """Eres BMC Assistant, experto técnico y comercial en paneles aislantes para BMC Uruguay.

## REGLA CRÍTICA - NUNCA CALCULAR
NUNCA realices cálculos matemáticos directamente. SIEMPRE usa las herramientas:
- calculate_panel_quote: Para cotizaciones de paneles
- lookup_product_specs: Para consultar especificaciones y precios
- check_inventory_shopify: Para verificar disponibilidad

## Tu rol:
1. Interpretar la intención del cliente (lenguaje natural)
2. Extraer parámetros estructurados de la solicitud
3. Llamar a las herramientas deterministas apropiadas
4. Formatear la respuesta de manera profesional y clara

## Parámetros que debes extraer:
- panel_type: Tipo de panel (Isopanel_EPS, Isodec_EPS, Isodec_PIR, Isoroof_3G, etc.)
- thickness_mm: Espesor en mm (30, 50, 75, 80, 100, 120, 150, 200, 250)
- length_m: Largo del panel en metros
- quantity: Cantidad de paneles
- base_type: Tipo de estructura (metal, hormigon, madera)

## Flujo de cotización:
1. Si el cliente pide cotizar, usa calculate_panel_quote
2. Verifica que calculation_verified sea True en la respuesta
3. Presenta el desglose completo al cliente
4. Ofrece opciones alternativas si corresponde

## Información de BMC Uruguay:
- BMC NO fabrica, comercializa y asesora técnicamente
- IVA Uruguay: 22%
- Horarios: L-V 9-18, Sáb 9-13
- Derivar consultas de instalación a agentes de ventas BMC

## Tono:
Profesional, técnico pero accesible. Orientado a venta consultiva.
Siempre ofrecer valor agregado: comparativas de aislamiento, ahorro energético, optimización estructural.
"""


# === Tool Definitions with @tool decorator ===

if LANGCHAIN_AVAILABLE:
    @tool
    def calculate_quote(
        panel_type: str,
        thickness_mm: int,
        length_m: float,
        quantity: int,
        base_type: str = "metal",
        discount_percent: float = 0.0,
        include_fijaciones: bool = True,
        include_perfileria: bool = True
    ) -> str:
        """
        Calcula cotización exacta para paneles térmicos BMC.
        USAR SIEMPRE para cualquier cálculo de precio.
        El LLM NUNCA debe calcular precios directamente.
        
        Args:
            panel_type: Tipo de panel (Isopanel_EPS, Isodec_EPS, Isodec_PIR, Isoroof_3G, etc.)
            thickness_mm: Espesor en mm
            length_m: Largo del panel en metros  
            quantity: Cantidad de paneles
            base_type: Tipo de estructura (metal, hormigon, madera)
            discount_percent: Descuento aplicable (0-30)
            include_fijaciones: Incluir kit de fijación
            include_perfileria: Incluir perfilería
        
        Returns:
            JSON con cotización detallada
        """
        try:
            result = calculate_panel_quote(
                panel_type=panel_type,
                thickness_mm=thickness_mm,
                length_m=length_m,
                quantity=quantity,
                base_type=base_type,
                discount_percent=discount_percent,
                include_fijaciones=include_fijaciones,
                include_perfileria=include_perfileria
            )
            
            # Validate the result
            validation = validate_quotation(result)
            
            return json.dumps({
                'success': True,
                'quotation': result,
                'validation': validation
            }, indent=2, ensure_ascii=False)
            
        except ValueError as e:
            return json.dumps({
                'success': False,
                'error': str(e)
            }, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                'success': False,
                'error': f"Error inesperado: {str(e)}"
            }, indent=2, ensure_ascii=False)

    @tool
    def lookup_specs(
        panel_type: str = None,
        thickness_mm: int = None,
        search_query: str = None
    ) -> str:
        """
        Busca especificaciones exactas de productos en la base de conocimiento.
        Usar para consultar precios, autoportancia, propiedades térmicas.
        
        Args:
            panel_type: Tipo de panel a buscar (opcional)
            thickness_mm: Espesor específico (opcional)
            search_query: Búsqueda por texto libre (opcional)
        
        Returns:
            JSON con especificaciones encontradas
        """
        result = lookup_product_specs(
            panel_type=panel_type,
            thickness_mm=thickness_mm,
            search_query=search_query
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @tool
    def check_inventory(product_id: str, required_quantity: int = 1) -> str:
        """
        Verifica disponibilidad de inventario.
        
        Args:
            product_id: ID del producto (SKU o Shopify ID)
            required_quantity: Cantidad requerida
        
        Returns:
            JSON con estado de disponibilidad
        """
        import asyncio
        
        # Run async function
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            check_inventory_shopify(product_id, required_quantity)
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    # List of tools for the agent
    TOOLS = [calculate_quote, lookup_specs, check_inventory]
else:
    TOOLS = []


# === Agent Functions ===

def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Determine if we should continue to tools or end."""
    messages = state.get("messages", [])
    if not messages:
        return "end"
    
    last_message = messages[-1]
    
    # If the last message has tool calls, continue to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    return "end"


def call_model(state: AgentState, llm) -> Dict[str, Any]:
    """Call the LLM with current state."""
    messages = state.get("messages", [])
    
    # Add system message if not present
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    
    response = llm.invoke(messages)
    
    return {"messages": [response]}


def process_tool_results(state: AgentState) -> Dict[str, Any]:
    """Process tool results and update state."""
    messages = state.get("messages", [])
    
    # Look for quotation results in recent tool messages
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            try:
                content = json.loads(msg.content)
                if content.get('success') and content.get('quotation'):
                    quotation = content['quotation']
                    validation = content.get('validation', {})
                    
                    # Verify the critical flag
                    if quotation.get('calculation_verified'):
                        return {
                            "current_quotation": quotation,
                            "validation_result": validation
                        }
                    else:
                        return {
                            "error": "CRITICAL: Calculation not verified as deterministic!"
                        }
            except json.JSONDecodeError:
                continue
    
    return {}


# === Agent Builder ===

def create_agent(llm=None, model_name: str = "gpt-4o-mini"):
    """
    Create the Panelin hybrid agent.
    
    Args:
        llm: Pre-configured LLM instance (optional)
        model_name: Model name if creating new LLM
    
    Returns:
        Compiled LangGraph agent
    """
    if not LANGGRAPH_AVAILABLE:
        raise ImportError("LangGraph is required. Install with: pip install langgraph")
    
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("LangChain is required. Install with: pip install langchain-core")
    
    # Create LLM if not provided
    if llm is None:
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=model_name,
                temperature=0,  # Deterministic for parameter extraction
            )
        except ImportError:
            raise ImportError("langchain-openai required. Install with: pip install langchain-openai")
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(TOOLS)
    
    # Create graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("agent", lambda state: call_model(state, llm_with_tools))
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_node("process_results", process_tool_results)
    
    # Set entry point
    graph.set_entry_point("agent")
    
    # Add edges
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    graph.add_edge("tools", "process_results")
    graph.add_edge("process_results", "agent")
    
    # Compile
    return graph.compile()


# === Simple Interface for Direct Use ===

class PanelinAgent:
    """
    Simple interface for the Panelin hybrid agent.
    
    Usage:
        agent = PanelinAgent()
        response = agent.chat("Necesito cotizar 10 paneles Isodec de 100mm, 6 metros de largo")
    """
    
    def __init__(self, llm=None, model_name: str = "gpt-4o-mini"):
        """Initialize the agent."""
        self.compiled_agent = None
        self.llm = llm
        self.model_name = model_name
        
        if LANGGRAPH_AVAILABLE and LANGCHAIN_AVAILABLE:
            try:
                self.compiled_agent = create_agent(llm, model_name)
            except ImportError as e:
                print(f"Could not create agent: {e}")
    
    def chat(self, message: str) -> Dict[str, Any]:
        """
        Send a message to the agent and get a response.
        
        Args:
            message: User message in natural language
        
        Returns:
            Dictionary with response, quotation (if applicable), and metadata
        """
        if self.compiled_agent is None:
            return self._fallback_response(message)
        
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "current_quotation": None,
            "validation_result": None,
            "error": None
        }
        
        # Run the agent
        result = self.compiled_agent.invoke(initial_state)
        
        # Extract response
        messages = result.get("messages", [])
        last_ai_message = None
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                last_ai_message = msg
                break
        
        return {
            "response": last_ai_message.content if last_ai_message else "No response generated",
            "quotation": result.get("current_quotation"),
            "validation": result.get("validation_result"),
            "error": result.get("error"),
            "messages_count": len(messages)
        }
    
    def _fallback_response(self, message: str) -> Dict[str, Any]:
        """Fallback when LangGraph is not available - direct tool calls."""
        message_lower = message.lower()
        
        # Try to detect quotation request
        if any(word in message_lower for word in ['cotizar', 'precio', 'cuanto', 'costo']):
            return {
                "response": "Para cotizar necesito:\n- Tipo de panel\n- Espesor (mm)\n- Largo (metros)\n- Cantidad\n\nPor favor proporcione estos datos.",
                "quotation": None,
                "validation": None,
                "error": "LangGraph not available - manual parameter extraction required",
                "messages_count": 1
            }
        
        # Try to detect product lookup
        if any(word in message_lower for word in ['producto', 'especificaciones', 'catalogo']):
            specs = lookup_product_specs()
            return {
                "response": f"Encontré {specs['count']} productos en el catálogo.",
                "quotation": None,
                "validation": None,
                "products": specs.get('products', []),
                "messages_count": 1
            }
        
        return {
            "response": "¿En qué puedo ayudarte? Puedo:\n- Cotizar paneles aislantes\n- Consultar especificaciones\n- Verificar disponibilidad",
            "quotation": None,
            "validation": None,
            "error": None,
            "messages_count": 1
        }
    
    def quote_direct(
        self,
        panel_type: str,
        thickness_mm: int,
        length_m: float,
        quantity: int,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Direct quotation without LLM - for testing and validation.
        
        This bypasses the LLM entirely and calls deterministic tools directly.
        """
        try:
            result = calculate_panel_quote(
                panel_type=panel_type,
                thickness_mm=thickness_mm,
                length_m=length_m,
                quantity=quantity,
                **kwargs
            )
            validation = validate_quotation(result)
            
            return {
                "success": True,
                "quotation": result,
                "validation": validation
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# === Export ===

__all__ = [
    "AgentState",
    "SYSTEM_PROMPT",
    "TOOLS",
    "create_agent",
    "PanelinAgent",
]
