"""
Panelin Quotation Agent V2 - LangGraph Implementation
======================================================

This module implements the single-agent architecture for BMC Uruguay quotations.

ARCHITECTURE PRINCIPLES:
1. LLM NEVER CALCULATES - All arithmetic is done by deterministic Python tools
2. Single Agent Pattern - No multi-agent complexity, uses tool calling
3. Structured Outputs - LLM extracts parameters in validated JSON schemas
4. Verification Layer - All outputs verified before returning to user

The agent uses LangGraph 1.0 patterns:
- State graph with typed state
- Tool nodes for deterministic operations
- Conditional routing based on tool results
"""

from typing import TypedDict, Annotated, Sequence, Optional, Any, Dict, List, Literal
from dataclasses import dataclass
import json
import logging

# LangGraph/LangChain imports (with fallback for development)
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None
    ToolNode = None
    BaseMessage = None
    HumanMessage = None
    AIMessage = None
    ToolMessage = None
    tool = None
    ChatOpenAI = None
    logging.warning("LangGraph not installed. Using fallback implementation.")

# Import deterministic tools
from ..tools.quotation_calculator import (
    calculate_panel_quote,
    lookup_product_specs,
    validate_quotation,
    calculate_accessories,
    QuotationResult,
)
from ..tools.product_lookup import (
    find_product_by_query,
    get_product_price,
    check_product_availability,
    list_all_products,
    get_pricing_rules,
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# STATE DEFINITION
# ============================================================================

if LANGGRAPH_AVAILABLE:
    class AgentState(TypedDict):
        """State maintained throughout the conversation"""
        messages: Annotated[Sequence[BaseMessage], "Conversation history"]
        
        # Extracted parameters from user query
        extracted_params: Optional[Dict[str, Any]]
        
        # Current quotation being processed
        current_quotation: Optional[QuotationResult]
        
        # Validation results
        validation_passed: bool
        validation_errors: List[str]
        
        # Tool call tracking
        last_tool_called: Optional[str]
        tool_results: Dict[str, Any]
        
        # Session metadata
        session_id: str
        turn_count: int
else:
    AgentState = Dict[str, Any]  # Fallback type


# ============================================================================
# SYSTEM PROMPT
# ============================================================================

SYSTEM_PROMPT = """Eres Panelin, el asistente de cotización de BMC Uruguay especializado en paneles aislantes térmicos.

## TU ROL FUNDAMENTAL
Tu ÚNICA función es extraer parámetros de las consultas del usuario y llamar las herramientas apropiadas.
NUNCA CALCULES PRECIOS, ÁREAS, O CUALQUIER OPERACIÓN MATEMÁTICA directamente.
SIEMPRE usa las herramientas disponibles para cálculos.

## HERRAMIENTAS DISPONIBLES

1. **find_product_by_query** - Buscar productos por descripción natural
2. **lookup_product_specs** - Obtener especificaciones técnicas de un producto
3. **get_product_price** - Consultar precio actual de un producto
4. **check_product_availability** - Verificar disponibilidad
5. **calculate_panel_quote** - OBLIGATORIO para cualquier cotización
6. **calculate_accessories** - Calcular accesorios necesarios
7. **list_all_products** - Listar productos por familia

## FLUJO DE COTIZACIÓN

1. Usuario describe lo que necesita
2. Usas find_product_by_query para identificar productos
3. Confirmas con el usuario el producto correcto
4. Extraes dimensiones (largo, ancho) de la consulta
5. OBLIGATORIO: Llamas calculate_panel_quote con los parámetros
6. Presentas el resultado formateado

## REGLAS CRÍTICAS

- NUNCA inventes precios o hagas cálculos mentales
- SIEMPRE verifica que calculation_verified=True en resultados
- Si el usuario pide descuento, valida que esté dentro del rango permitido (0-15%)
- Todos los precios están en USD
- El IVA en Uruguay es 22%

## PRODUCTOS BMC URUGUAY

- ISOPANEL EPS: Para paredes y fachadas (50-250mm)
- ISODEC EPS: Para techos y cubiertas (100-250mm)
- ISODEC PIR: Para techos con mejor aislación (50-120mm)
- ISOWALL PIR: Para fachadas premium (50-80mm)
- ISOROOF 3G: Solución de techo rápida
- ISOROOF FOIL: Para aplicaciones agrícolas

## FORMATO DE RESPUESTA

Cuando presentes una cotización, incluye:
- Producto y especificaciones
- Dimensiones calculadas
- Cantidad de paneles
- Precio unitario por m²
- Subtotal
- Descuentos aplicados (si corresponde)
- IVA
- TOTAL

Siempre sé profesional, claro y conciso. El cliente es rey.
"""


# ============================================================================
# TOOL WRAPPERS (for LangGraph)
# ============================================================================

if LANGGRAPH_AVAILABLE:
    @tool
    def tool_find_product(query: str, max_results: int = 5) -> str:
        """Busca productos basándose en descripción en lenguaje natural."""
        results = find_product_by_query(query, max_results)
        return json.dumps(results, indent=2, ensure_ascii=False)
    
    @tool
    def tool_lookup_specs(
        product_id: Optional[str] = None,
        family: Optional[str] = None,
        thickness_mm: Optional[int] = None,
        application: Optional[str] = None
    ) -> str:
        """Busca especificaciones de un producto en la base de conocimiento."""
        result = lookup_product_specs(product_id, family, thickness_mm, application)
        if result:
            return json.dumps(dict(result), indent=2, ensure_ascii=False)
        return json.dumps({"error": "Producto no encontrado"})
    
    @tool
    def tool_get_price(product_id: str) -> str:
        """Obtiene el precio exacto de un producto por su ID."""
        result = get_product_price(product_id)
        if result:
            return json.dumps(result, indent=2, ensure_ascii=False)
        return json.dumps({"error": f"Producto no encontrado: {product_id}"})
    
    @tool
    def tool_check_availability(product_id: str) -> str:
        """Verifica disponibilidad y stock de un producto."""
        result = check_product_availability(product_id)
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @tool
    def tool_calculate_quote(
        product_id: str,
        length_m: float,
        width_m: float,
        quantity: int = 1,
        discount_percent: float = 0.0,
        include_accessories: bool = False,
        include_tax: bool = True,
        installation_type: str = "techo"
    ) -> str:
        """
        Calcula cotización exacta para paneles térmicos BMC.
        USAR SIEMPRE para cualquier cálculo de precio.
        """
        try:
            result = calculate_panel_quote(
                product_id=product_id,
                length_m=length_m,
                width_m=width_m,
                quantity=quantity,
                discount_percent=discount_percent,
                include_accessories=include_accessories,
                include_tax=include_tax,
                installation_type=installation_type
            )
            
            # Validate result
            is_valid, errors = validate_quotation(result)
            if not is_valid:
                result["_validation_warnings"] = errors
            
            return json.dumps(dict(result), indent=2, ensure_ascii=False)
        except ValueError as e:
            return json.dumps({"error": str(e)})
        except Exception as e:
            return json.dumps({"error": f"Error en cálculo: {str(e)}"})
    
    @tool
    def tool_calculate_accessories(
        cantidad_paneles: int,
        apoyos: int,
        largo: float,
        ancho_util: float,
        installation_type: str = "techo"
    ) -> str:
        """Calcula accesorios necesarios para la instalación de paneles."""
        result = calculate_accessories(
            cantidad_paneles=cantidad_paneles,
            apoyos=apoyos,
            largo=largo,
            ancho_util=ancho_util,
            installation_type=installation_type
        )
        return json.dumps(dict(result), indent=2, ensure_ascii=False)
    
    @tool
    def tool_list_products(family: Optional[str] = None) -> str:
        """Lista todos los productos disponibles, opcionalmente filtrados por familia."""
        results = list_all_products(family)
        return json.dumps(results, indent=2, ensure_ascii=False)
    
    # Collect all tools
    AGENT_TOOLS = [
        tool_find_product,
        tool_lookup_specs,
        tool_get_price,
        tool_check_availability,
        tool_calculate_quote,
        tool_calculate_accessories,
        tool_list_products,
    ]


# ============================================================================
# AGENT GRAPH DEFINITION
# ============================================================================

class PanelinQuotationAgent:
    """
    Single-agent implementation for BMC Uruguay quotations.
    
    Uses LangGraph 1.0 state graph pattern with deterministic tools.
    The LLM only performs language understanding - all calculations
    are executed by Python code.
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0,
        api_key: Optional[str] = None
    ):
        """
        Initialize the Panelin quotation agent.
        
        Args:
            model_name: LLM model to use (default: gpt-4o-mini for cost efficiency)
            temperature: LLM temperature (0 for deterministic extraction)
            api_key: Optional OpenAI API key (uses env var if not provided)
        """
        self.model_name = model_name
        self.temperature = temperature
        
        if not LANGGRAPH_AVAILABLE:
            logger.warning("LangGraph not available - using fallback mode")
            self.graph = None
            return
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        ).bind_tools(AGENT_TOOLS)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph state graph"""
        
        # Define the graph
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("agent", self._agent_node)
        graph.add_node("tools", ToolNode(AGENT_TOOLS))
        graph.add_node("validate", self._validate_node)
        
        # Add edges
        graph.set_entry_point("agent")
        
        # Conditional routing after agent
        graph.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "tools": "tools",
                "validate": "validate",
                "end": END
            }
        )
        
        # After tools, go back to agent
        graph.add_edge("tools", "agent")
        
        # After validation, end
        graph.add_edge("validate", END)
        
        return graph.compile()
    
    def _agent_node(self, state: AgentState) -> AgentState:
        """
        Main agent node - processes messages and decides on actions.
        
        The agent extracts parameters from user queries and calls
        appropriate tools. It NEVER performs calculations directly.
        """
        messages = state["messages"]
        
        # Add system prompt if first turn
        if state.get("turn_count", 0) == 0:
            from langchain_core.messages import SystemMessage
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
        
        # Call LLM
        response = self.llm.invoke(messages)
        
        # Update state
        new_state = state.copy()
        new_state["messages"] = list(state["messages"]) + [response]
        new_state["turn_count"] = state.get("turn_count", 0) + 1
        
        # Track tool calls
        if hasattr(response, "tool_calls") and response.tool_calls:
            new_state["last_tool_called"] = response.tool_calls[0]["name"]
        else:
            new_state["last_tool_called"] = None
        
        return new_state
    
    def _validate_node(self, state: AgentState) -> AgentState:
        """
        Validation node - ensures quotation results are verified.
        
        Checks that:
        1. calculation_verified flag is True
        2. All numeric values are reasonable
        3. No LLM-generated calculations present
        """
        new_state = state.copy()
        
        quotation = state.get("current_quotation")
        if quotation:
            is_valid, errors = validate_quotation(quotation)
            new_state["validation_passed"] = is_valid
            new_state["validation_errors"] = errors
            
            if not is_valid:
                logger.error(f"Quotation validation failed: {errors}")
        
        return new_state
    
    def _should_continue(self, state: AgentState) -> Literal["tools", "validate", "end"]:
        """Decide whether to continue with tools, validate, or end"""
        last_message = state["messages"][-1]
        
        # If there are tool calls, execute them
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        
        # If we just completed a quotation calculation, validate it
        if state.get("last_tool_called") == "tool_calculate_quote":
            return "validate"
        
        # Otherwise, we're done
        return "end"
    
    def invoke(self, user_message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Process a user message and return the response.
        
        Args:
            user_message: User's query in natural language
            session_id: Session identifier for state tracking
            
        Returns:
            Dictionary with response and metadata
        """
        if not LANGGRAPH_AVAILABLE or self.graph is None:
            return self._fallback_invoke(user_message)
        
        # Initialize state
        initial_state = AgentState(
            messages=[HumanMessage(content=user_message)],
            extracted_params=None,
            current_quotation=None,
            validation_passed=True,
            validation_errors=[],
            last_tool_called=None,
            tool_results={},
            session_id=session_id,
            turn_count=0
        )
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Extract response
        last_message = final_state["messages"][-1]
        response_text = last_message.content if hasattr(last_message, "content") else str(last_message)
        
        return {
            "response": response_text,
            "quotation": final_state.get("current_quotation"),
            "validation_passed": final_state.get("validation_passed", True),
            "validation_errors": final_state.get("validation_errors", []),
            "tools_used": [m for m in final_state["messages"] if hasattr(m, "tool_calls")],
            "session_id": session_id
        }
    
    def _fallback_invoke(self, user_message: str) -> Dict[str, Any]:
        """
        Fallback implementation when LangGraph is not available.
        
        This demonstrates the tool-calling pattern without the full graph.
        """
        logger.info("Using fallback implementation (LangGraph not available)")
        
        # Simple pattern matching for demo
        message_lower = user_message.lower()
        
        # Try to extract product type and dimensions
        products = find_product_by_query(user_message, max_results=1)
        
        if not products:
            return {
                "response": "No encontré productos que coincidan con tu consulta. ¿Podrías especificar qué tipo de panel necesitas?",
                "quotation": None,
                "validation_passed": True,
                "validation_errors": []
            }
        
        product = products[0]
        
        return {
            "response": f"Encontré: {product['name']} a ${product['price_per_m2']}/m². Para generar una cotización, necesito las dimensiones (largo y ancho en metros).",
            "product_found": product,
            "quotation": None,
            "validation_passed": True,
            "validation_errors": []
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_agent(
    model_name: str = "gpt-4o-mini",
    temperature: float = 0,
    api_key: Optional[str] = None
) -> PanelinQuotationAgent:
    """
    Factory function to create a Panelin quotation agent.
    
    Args:
        model_name: LLM model to use
        temperature: LLM temperature
        api_key: OpenAI API key
        
    Returns:
        Configured PanelinQuotationAgent instance
    """
    return PanelinQuotationAgent(
        model_name=model_name,
        temperature=temperature,
        api_key=api_key
    )


def run_quotation_query(
    query: str,
    model_name: str = "gpt-4o-mini",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    One-shot function to process a quotation query.
    
    Args:
        query: User's quotation query
        model_name: LLM model to use
        api_key: OpenAI API key
        
    Returns:
        Quotation response dictionary
    """
    agent = create_agent(model_name=model_name, api_key=api_key)
    return agent.invoke(query)


# ============================================================================
# CLI INTERFACE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("PANELIN QUOTATION AGENT V2")
    print("BMC Uruguay - Paneles Aislantes Térmicos")
    print("=" * 60)
    print("\nArquitectura: Single-Agent con Herramientas Deterministas")
    print("LLM solo extrae parámetros - Python calcula todo")
    print("\nEjemplo de consulta:")
    print("  'Necesito 10 metros de isopanel de 100mm para un techo de 6x4m'")
    print("\n" + "=" * 60)
    
    # Demo mode without API key
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "panel para techo de 100mm"
    
    print(f"\nConsulta: {query}")
    print("-" * 40)
    
    # Test product lookup (works without API)
    products = find_product_by_query(query, max_results=3)
    print("\nProductos encontrados:")
    for p in products:
        print(f"  - {p['name']}: ${p['price_per_m2']}/m² ({p['stock_status']})")
    
    # Test quotation calculation (works without API)
    if products:
        print("\nEjemplo de cotización (6m x 4m):")
        try:
            quote = calculate_panel_quote(
                product_id=products[0]["product_id"],
                length_m=6.0,
                width_m=4.0,
                quantity=1,
                include_tax=True
            )
            print(f"  Producto: {quote['product_name']}")
            print(f"  Área: {quote['area_m2']} m²")
            print(f"  Paneles: {quote['panels_needed']}")
            print(f"  Subtotal: ${quote['subtotal_usd']:.2f}")
            print(f"  IVA (22%): ${quote['tax_amount_usd']:.2f}")
            print(f"  TOTAL: ${quote['total_usd']:.2f}")
            print(f"\n  [calculation_verified: {quote['calculation_verified']}]")
        except Exception as e:
            print(f"  Error: {e}")
