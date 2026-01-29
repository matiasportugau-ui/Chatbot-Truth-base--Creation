"""
Panelin Hybrid Agent - LangGraph 1.0 Implementation

Este agente implementa la arquitectura híbrida recomendada:
- LLM: Comprensión de lenguaje natural y extracción de parámetros
- Código: Cálculos deterministas con precisión Decimal

Arquitectura:
┌──────────────────────────────────────────────────────────────────┐
│  Input Usuario → LLM Extracción → Validación → CÁLCULO          │
│  (Lenguaje       (Structured Out)  Schema+Rango  DETERMINISTA   │
│   Natural)                         (Python)      (Python/Decimal)│
└──────────────────────────────────────────────────────────────────┘

Stack:
- LangGraph 1.0 para orquestación de workflows
- GPT-4o-mini / Gemini Flash para extracción (bajo costo, alta precisión)
- Claude 3.5 Haiku como fallback para casos edge
- Herramientas deterministas para todos los cálculos

Principios:
1. LLM NUNCA calcula - solo extrae parámetros
2. Toda aritmética en Python con Decimal
3. Verificación dual-path de resultados
4. calculation_verified=True en todos los outputs válidos
"""

import json
import logging
import os
from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict, Union
from datetime import datetime

# LangGraph imports (conditional for environments without it)
try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    from langgraph.prebuilt import ToolNode, tools_condition
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = "end"

# LangChain imports (conditional)
try:
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatOpenAI = None

# Local imports
from panelin.tools.quotation_calculator import (
    calculate_panel_quote,
    calculate_multi_panel_quote,
    apply_pricing_rules,
    validate_quotation,
)
from panelin.tools.knowledge_base import (
    lookup_product_specs,
    search_products,
    get_available_products,
)
from panelin.models.schemas import (
    QuotationResult,
    ValidationResult,
    CALCULATE_PANEL_QUOTE_TOOL_SCHEMA,
    LOOKUP_PRODUCT_SPECS_TOOL_SCHEMA,
    SEARCH_PRODUCTS_TOOL_SCHEMA,
)

# Configure logging
logger = logging.getLogger(__name__)


# System prompt for the agent
PANELIN_SYSTEM_PROMPT = """Eres Panelin, el asistente experto de BMC Uruguay para cotización de paneles aislantes térmicos.

## TU ROL FUNDAMENTAL
Ayudas a clientes a obtener cotizaciones precisas de paneles. NUNCA calculas precios directamente - 
SIEMPRE usas las herramientas proporcionadas que garantizan precisión matemática.

## REGLAS CRÍTICAS
1. **NUNCA hagas cálculos matemáticos** - Usa SIEMPRE la herramienta `calculate_panel_quote`
2. **Extrae parámetros del usuario**: tipo de panel, dimensiones, cantidad, descuentos
3. **Valida cada cotización** usando `validate_quotation` después de calcular
4. **Consulta la KB** con `lookup_product_specs` para verificar disponibilidad y precios

## PRODUCTOS DISPONIBLES
- **ISOPANEL EPS**: Paredes y fachadas (50-250mm)
- **ISODEC EPS**: Techos y cubiertas (100-250mm)
- **ISODEC PIR**: Techos premium (50-120mm)
- **ISOWALL PIR**: Fachadas premium (50-80mm)
- **ISOROOF 3G**: Techos estándar
- **ISOROOF PLUS 3G**: Techos premium
- **ISOROOF FOIL 3G**: Techos económico
- **HIANSA Panel 5G**: Trapezoidales BECAM

## FLUJO DE COTIZACIÓN
1. Identifica el producto y dimensiones del usuario
2. Usa `lookup_product_specs` para verificar existencia y precio
3. Usa `calculate_panel_quote` para obtener cotización exacta
4. Valida con `validate_quotation`
5. Presenta resultado claro al cliente

## FORMATO DE RESPUESTA
Presenta las cotizaciones de forma clara con:
- Producto y especificaciones
- Área por panel y cantidad
- Precio unitario y subtotal
- Descuentos aplicados (si los hay)
- Total final en USD

Recuerda: Los precios están en USD por m². Siempre verifica stock antes de cotizar.
"""


# State definition for LangGraph
class AgentState(TypedDict):
    """Estado del agente durante el workflow."""
    messages: Annotated[list, add_messages] if LANGGRAPH_AVAILABLE else list
    current_quotation: Optional[QuotationResult]
    validation_result: Optional[ValidationResult]
    error: Optional[str]
    step: str


class PanelinHybridAgent:
    """
    Agente híbrido para cotización de paneles BMC.
    
    Combina:
    - LLM para comprensión de lenguaje natural
    - Herramientas deterministas para cálculos precisos
    
    Example:
        >>> agent = PanelinHybridAgent()
        >>> response = await agent.run("Necesito 20 paneles Isopanel de 3m x 1.14m, espesor 100mm")
        >>> print(response["quotation"]["total_usd"])
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0,
        fallback_model: str = "gpt-4o",
        api_key: Optional[str] = None,
    ):
        """
        Inicializa el agente híbrido.
        
        Args:
            model_name: Modelo LLM principal (gpt-4o-mini recomendado)
            temperature: Temperatura para generación (0 para determinismo)
            fallback_model: Modelo de respaldo para casos difíciles
            api_key: API key de OpenAI (o de env var)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.fallback_model = fallback_model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        # Initialize LLM if available
        self.llm = None
        self.graph = None
        
        if LANGCHAIN_AVAILABLE and self.api_key:
            self._initialize_llm()
        
        if LANGGRAPH_AVAILABLE and self.llm:
            self._build_graph()
        
        logger.info(f"PanelinHybridAgent initialized with {model_name}")
    
    def _initialize_llm(self) -> None:
        """Inicializa el modelo LLM con herramientas."""
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key,
        )
        
        # Bind tools to LLM
        self.tools = self._create_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
    
    def _create_tools(self) -> list:
        """Crea las herramientas LangChain para el agente."""
        if not LANGCHAIN_AVAILABLE:
            return []
        
        @tool
        def calculate_quote(
            panel_type: str,
            length_m: float,
            width_m: float,
            quantity: int,
            thickness_mm: Optional[int] = None,
            discount_percent: float = 0.0,
            include_delivery: bool = False,
            include_tax: bool = False,
        ) -> dict:
            """
            Calcula cotización exacta para paneles térmicos BMC.
            USAR SIEMPRE para cualquier cálculo de precio.
            El LLM NO debe calcular precios directamente.
            """
            try:
                result = calculate_panel_quote(
                    panel_type=panel_type,
                    length_m=length_m,
                    width_m=width_m,
                    quantity=quantity,
                    thickness_mm=thickness_mm,
                    discount_percent=discount_percent,
                    include_delivery=include_delivery,
                    include_tax=include_tax,
                )
                return dict(result)
            except Exception as e:
                return {"error": str(e), "calculation_verified": False}
        
        @tool
        def lookup_product(
            product_identifier: str,
            thickness_mm: Optional[int] = None,
        ) -> dict:
            """
            Busca especificaciones exactas de un producto.
            Usar para obtener precios, dimensiones y disponibilidad.
            """
            try:
                result = lookup_product_specs(
                    product_identifier=product_identifier,
                    thickness_mm=thickness_mm,
                )
                if result:
                    return dict(result)
                return {"error": f"Producto no encontrado: {product_identifier}"}
            except Exception as e:
                return {"error": str(e)}
        
        @tool
        def search_products_kb(
            query: str,
            limit: int = 5,
        ) -> list:
            """
            Búsqueda semántica de productos por descripción o uso.
            Ejemplo: 'paneles económicos para techos planos'
            """
            try:
                results = search_products(query=query, limit=limit)
                return [dict(r) for r in results]
            except Exception as e:
                return [{"error": str(e)}]
        
        @tool
        def validate_quote(quotation: dict) -> dict:
            """
            Valida una cotización para verificar integridad.
            SIEMPRE usar después de calculate_quote.
            """
            try:
                result = validate_quotation(quotation)
                return dict(result)
            except Exception as e:
                return {"is_valid": False, "errors": [str(e)]}
        
        @tool
        def list_available_products(
            familia: Optional[str] = None,
            in_stock_only: bool = False,
        ) -> list:
            """
            Lista todos los productos disponibles.
            Útil para mostrar catálogo al cliente.
            """
            try:
                results = get_available_products(
                    familia=familia,
                    in_stock_only=in_stock_only,
                )
                return results
            except Exception as e:
                return [{"error": str(e)}]
        
        return [
            calculate_quote,
            lookup_product,
            search_products_kb,
            validate_quote,
            list_available_products,
        ]
    
    def _build_graph(self) -> None:
        """Construye el grafo LangGraph."""
        if not LANGGRAPH_AVAILABLE:
            return
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.add_node("validate", self._validation_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add edges
        workflow.add_conditional_edges(
            "agent",
            tools_condition,
            {
                "tools": "tools",
                END: END,
            }
        )
        workflow.add_edge("tools", "validate")
        workflow.add_edge("validate", "agent")
        
        # Compile
        self.graph = workflow.compile()
    
    def _agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Nodo principal del agente."""
        messages = state.get("messages", [])
        
        # Add system message if not present
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=PANELIN_SYSTEM_PROMPT)] + messages
        
        # Call LLM
        response = self.llm_with_tools.invoke(messages)
        
        return {"messages": [response], "step": "agent"}
    
    def _validation_node(self, state: AgentState) -> Dict[str, Any]:
        """Nodo de validación de cotización."""
        messages = state.get("messages", [])
        
        # Look for quotation in last tool message
        for msg in reversed(messages):
            if isinstance(msg, ToolMessage):
                try:
                    content = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                    if content.get("calculation_verified"):
                        validation = validate_quotation(content)
                        return {
                            "current_quotation": content,
                            "validation_result": dict(validation),
                            "step": "validated",
                        }
                except (json.JSONDecodeError, TypeError):
                    pass
        
        return {"step": "no_quotation_found"}
    
    async def run(self, user_message: str) -> Dict[str, Any]:
        """
        Ejecuta el agente con un mensaje de usuario.
        
        Args:
            user_message: Mensaje del usuario en lenguaje natural
        
        Returns:
            Diccionario con respuesta, cotización y validación
        """
        if not self.graph:
            return await self._run_simple(user_message)
        
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=user_message)],
            "current_quotation": None,
            "validation_result": None,
            "error": None,
            "step": "start",
        }
        
        # Run graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Extract response
        messages = final_state.get("messages", [])
        last_ai_message = None
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                last_ai_message = msg
                break
        
        return {
            "response": last_ai_message.content if last_ai_message else "",
            "quotation": final_state.get("current_quotation"),
            "validation": final_state.get("validation_result"),
            "messages": messages,
        }
    
    async def _run_simple(self, user_message: str) -> Dict[str, Any]:
        """
        Ejecución simple sin LangGraph (para desarrollo/testing).
        
        Implementa el flujo básico:
        1. Extrae parámetros del mensaje
        2. Llama herramienta de cálculo
        3. Valida resultado
        """
        # Simple parameter extraction using keywords
        params = self._extract_parameters_simple(user_message)
        
        if not params:
            return {
                "response": "No pude extraer los parámetros necesarios. Por favor indica: tipo de panel, dimensiones (largo x ancho), espesor y cantidad.",
                "quotation": None,
                "validation": None,
            }
        
        try:
            # Calculate quote
            quotation = calculate_panel_quote(**params)
            
            # Validate
            validation = validate_quotation(quotation)
            
            # Format response
            response = self._format_quotation_response(quotation, validation)
            
            return {
                "response": response,
                "quotation": quotation,
                "validation": dict(validation),
            }
        except Exception as e:
            return {
                "response": f"Error al calcular cotización: {str(e)}",
                "quotation": None,
                "validation": None,
                "error": str(e),
            }
    
    def _extract_parameters_simple(self, message: str) -> Optional[Dict[str, Any]]:
        """Extracción simple de parámetros (fallback sin LLM)."""
        import re
        
        message_lower = message.lower()
        
        # Extract panel type
        panel_type = None
        panel_patterns = [
            (r'isopanel\s*(?:eps)?', 'Isopanel EPS'),
            (r'isodec\s*(?:eps)?', 'Isodec EPS'),
            (r'isodec\s*pir', 'Isodec PIR'),
            (r'isowall\s*(?:pir)?', 'Isowall PIR'),
            (r'isoroof\s*plus', 'Isoroof Plus 3G'),
            (r'isoroof\s*foil', 'Isoroof Foil 3G'),
            (r'isoroof(?:\s*3g)?', 'Isoroof 3G'),
            (r'hiansa', 'Hiansa Panel 5G'),
        ]
        
        for pattern, ptype in panel_patterns:
            if re.search(pattern, message_lower):
                panel_type = ptype
                break
        
        if not panel_type:
            return None
        
        # Extract dimensions
        dim_patterns = [
            r'(\d+(?:[.,]\d+)?)\s*(?:m|metros?)?\s*[x×]\s*(\d+(?:[.,]\d+)?)\s*(?:m|metros?)?',
            r'largo\s*(?:de\s*)?(\d+(?:[.,]\d+)?)\s*(?:m|metros?)?.*ancho\s*(?:de\s*)?(\d+(?:[.,]\d+)?)',
            r'(\d+(?:[.,]\d+)?)\s*(?:m|metros?)\s*(?:de\s*)?largo',
        ]
        
        length_m = None
        width_m = 1.0  # Default width
        
        for pattern in dim_patterns:
            match = re.search(pattern, message_lower)
            if match:
                length_m = float(match.group(1).replace(',', '.'))
                if len(match.groups()) > 1:
                    width_m = float(match.group(2).replace(',', '.'))
                break
        
        if not length_m:
            # Try single dimension
            dim_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:m|metros?)', message_lower)
            if dim_match:
                length_m = float(dim_match.group(1).replace(',', '.'))
        
        if not length_m:
            return None
        
        # Extract thickness
        thickness_mm = None
        thick_match = re.search(r'(\d+)\s*(?:mm|milímetros?)', message_lower)
        if thick_match:
            thickness_mm = int(thick_match.group(1))
        
        # Extract quantity
        quantity = 1
        qty_patterns = [
            r'(\d+)\s*(?:paneles?|unidades?|piezas?)',
            r'cantidad\s*(?:de\s*)?(\d+)',
            r'necesito\s*(\d+)',
            r'quiero\s*(\d+)',
        ]
        
        for pattern in qty_patterns:
            match = re.search(pattern, message_lower)
            if match:
                quantity = int(match.group(1))
                break
        
        return {
            "panel_type": panel_type,
            "length_m": length_m,
            "width_m": width_m,
            "quantity": quantity,
            "thickness_mm": thickness_mm,
        }
    
    def _format_quotation_response(
        self,
        quotation: QuotationResult,
        validation: ValidationResult,
    ) -> str:
        """Formatea la cotización como respuesta para el usuario."""
        lines = ["## Cotización BMC Uruguay\n"]
        
        for item in quotation.get("line_items", []):
            lines.append(f"**Producto:** {item['product_name']}")
            if item.get("thickness_mm"):
                lines.append(f"**Espesor:** {item['thickness_mm']}mm")
            lines.append(f"**Dimensiones:** {item['length_m']}m x {item['width_m']}m = {item['area_m2']}m² por panel")
            lines.append(f"**Cantidad:** {item['quantity']} paneles")
            lines.append(f"**Precio unitario:** USD {item['unit_price_usd']:.2f}")
            lines.append(f"**Subtotal línea:** USD {item['line_total_usd']:.2f}")
            lines.append("")
        
        lines.append("---")
        lines.append(f"**Subtotal:** USD {quotation['subtotal_usd']:.2f}")
        
        if quotation.get("discount_amount_usd", 0) > 0:
            lines.append(f"**Descuento ({quotation['discount_percent']:.1f}%):** -USD {quotation['discount_amount_usd']:.2f}")
        
        if quotation.get("delivery_cost_usd", 0) > 0:
            lines.append(f"**Envío:** USD {quotation['delivery_cost_usd']:.2f}")
        
        if quotation.get("tax_amount_usd", 0) > 0:
            lines.append(f"**IVA ({quotation['tax_rate']:.0f}%):** USD {quotation['tax_amount_usd']:.2f}")
        
        lines.append(f"\n### **TOTAL: USD {quotation['total_usd']:.2f}**")
        
        # Add notes
        if quotation.get("notes"):
            lines.append("\n**Notas:**")
            for note in quotation["notes"]:
                lines.append(f"- {note}")
        
        # Validation status
        if validation.get("is_valid"):
            lines.append("\n✅ Cotización verificada")
        else:
            lines.append("\n⚠️ Advertencias en validación:")
            for error in validation.get("errors", []):
                lines.append(f"- {error}")
        
        lines.append(f"\n_Cotización #{quotation['quotation_id']}_")
        lines.append(f"_Generada: {quotation['timestamp']}_")
        
        return "\n".join(lines)


def create_panelin_agent(
    model_name: str = "gpt-4o-mini",
    **kwargs,
) -> PanelinHybridAgent:
    """
    Factory function para crear el agente Panelin.
    
    Args:
        model_name: Modelo a usar (gpt-4o-mini, gpt-4o, gemini-1.5-flash)
        **kwargs: Argumentos adicionales para PanelinHybridAgent
    
    Returns:
        Instancia configurada del agente
    """
    return PanelinHybridAgent(model_name=model_name, **kwargs)


async def run_quotation_workflow(
    user_message: str,
    model_name: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """
    Ejecuta un workflow completo de cotización.
    
    Esta es la función principal para usar el agente.
    
    Args:
        user_message: Mensaje del usuario en lenguaje natural
        model_name: Modelo LLM a usar
    
    Returns:
        Diccionario con respuesta, cotización y validación
    
    Example:
        >>> result = await run_quotation_workflow(
        ...     "Necesito 50 paneles Isodec de 4m x 1.12m, espesor 100mm"
        ... )
        >>> print(result["quotation"]["total_usd"])
    """
    agent = create_panelin_agent(model_name=model_name)
    return await agent.run(user_message)


# Synchronous wrapper for non-async contexts
def run_quotation_sync(
    user_message: str,
    model_name: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """
    Versión síncrona del workflow de cotización.
    
    Args:
        user_message: Mensaje del usuario
        model_name: Modelo LLM
    
    Returns:
        Resultado de la cotización
    """
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(
        run_quotation_workflow(user_message, model_name)
    )
