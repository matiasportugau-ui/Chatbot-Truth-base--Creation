"""
Panelin Agent - LangGraph Implementation
========================================

Single-agent architecture using LangGraph 1.0.
The agent orchestrates tools but NEVER performs calculations directly.
"""

import json
from typing import Any, Dict, List, Optional, TypedDict, Annotated, Sequence
from dataclasses import dataclass
import operator

# Import our deterministic tools
from ..tools.quotation_calculator import (
    calculate_panel_quote,
    calculate_fixation_points,
    calculate_profiles_quote,
    calculate_accessories_quote,
    calculate_complete_quotation,
)
from ..tools.product_lookup import (
    lookup_product_specs,
    search_products_by_criteria,
    get_available_thicknesses,
    get_catalog_summary,
)
from ..tools.pricing_rules import (
    apply_bulk_pricing,
    calculate_delivery_cost,
    get_minimum_order_value,
    calculate_tax,
)

from .tool_definitions import SYSTEM_PROMPT, get_tool_definitions


# Tool registry - maps tool names to functions
TOOL_REGISTRY = {
    "calculate_panel_quote": calculate_panel_quote,
    "calculate_complete_quotation": calculate_complete_quotation,
    "calculate_fixation_points": calculate_fixation_points,
    "lookup_product_specs": lookup_product_specs,
    "search_products_by_criteria": search_products_by_criteria,
    "get_available_thicknesses": get_available_thicknesses,
    "get_catalog_summary": get_catalog_summary,
    "apply_bulk_pricing": apply_bulk_pricing,
    "calculate_delivery_cost": calculate_delivery_cost,
}


class Message(TypedDict):
    """Message in the conversation"""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]]
    tool_call_id: Optional[str]
    name: Optional[str]


class AgentState(TypedDict):
    """State of the agent during execution"""
    messages: Annotated[Sequence[Message], operator.add]
    current_quotation: Optional[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    error: Optional[str]


@dataclass
class PanelinAgent:
    """
    Panelin Quotation Agent using LangGraph architecture.
    
    This agent:
    1. Receives natural language requests
    2. Extracts parameters using LLM
    3. Calls deterministic tools for calculations
    4. Formats and returns the response
    
    The LLM NEVER performs calculations - only parameter extraction
    and response formatting.
    """
    
    model: str = "gpt-4o-mini"
    temperature: float = 0
    max_tool_calls: int = 10
    
    def __post_init__(self):
        """Initialize the agent"""
        self.tool_definitions = get_tool_definitions()
        self.system_prompt = SYSTEM_PROMPT
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with the given arguments.
        
        All tools return results with 'calculation_verified' = True
        to confirm deterministic execution.
        """
        if tool_name not in TOOL_REGISTRY:
            return {
                "error": f"Tool not found: {tool_name}",
                "calculation_verified": False,
            }
        
        try:
            tool_fn = TOOL_REGISTRY[tool_name]
            result = tool_fn(**arguments)
            return result
        except Exception as e:
            return {
                "error": str(e),
                "tool": tool_name,
                "arguments": arguments,
                "calculation_verified": False,
            }
    
    def process_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process all tool calls from the LLM response.
        
        Returns list of tool results, each marked with calculation_verified.
        """
        results = []
        
        for call in tool_calls:
            tool_name = call.get("function", {}).get("name", call.get("name", ""))
            arguments_str = call.get("function", {}).get("arguments", call.get("arguments", "{}"))
            
            # Parse arguments
            if isinstance(arguments_str, str):
                try:
                    arguments = json.loads(arguments_str)
                except json.JSONDecodeError:
                    arguments = {}
            else:
                arguments = arguments_str
            
            # Execute tool
            result = self.execute_tool(tool_name, arguments)
            
            results.append({
                "tool_call_id": call.get("id", ""),
                "tool_name": tool_name,
                "arguments": arguments,
                "result": result,
            })
        
        return results
    
    def format_tool_result_message(self, result: Dict[str, Any]) -> str:
        """Format tool result for the conversation"""
        if "error" in result.get("result", {}):
            return f"Error: {result['result']['error']}"
        
        # Pretty print the result
        return json.dumps(result["result"], indent=2, ensure_ascii=False)


def create_panelin_agent(
    model: str = "gpt-4o-mini",
    temperature: float = 0,
) -> PanelinAgent:
    """
    Factory function to create a Panelin agent.
    
    Args:
        model: LLM model to use (gpt-4o-mini recommended for cost efficiency)
        temperature: Temperature for LLM (0 recommended for consistency)
    
    Returns:
        Configured PanelinAgent instance
    """
    return PanelinAgent(model=model, temperature=temperature)


def run_quotation_request(
    user_message: str,
    agent: Optional[PanelinAgent] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Process a quotation request using the Panelin agent.
    
    This is a simplified execution flow for testing without LLM.
    In production, this would integrate with LangGraph for full agent loop.
    
    Args:
        user_message: The user's natural language request
        agent: PanelinAgent instance (created if not provided)
        conversation_history: Previous messages (optional)
    
    Returns:
        Dict with response and any quotation results
    """
    if agent is None:
        agent = create_panelin_agent()
    
    # For demo purposes, parse common patterns and call tools directly
    # In production, this would use LangGraph with LLM
    
    result = {
        "user_message": user_message,
        "tool_calls": [],
        "quotation": None,
        "response": "",
    }
    
    # Simple pattern matching for demo
    message_lower = user_message.lower()
    
    # Try to extract parameters from message
    if "cotiza" in message_lower or "precio" in message_lower or "costo" in message_lower:
        # Example: Extract panel type and dimensions
        # This is a simplified demo - real implementation uses LLM
        
        if "isoroof" in message_lower:
            panel_type = "Isoroof"
        elif "isodec" in message_lower:
            panel_type = "Isodec"
        elif "isopanel" in message_lower:
            panel_type = "Isopanel"
        elif "isowall" in message_lower:
            panel_type = "Isowall"
        elif "isofrig" in message_lower:
            panel_type = "Isofrig"
        else:
            panel_type = "Isodec"  # Default for techos
        
        # Try to extract dimensions (simplified)
        import re
        
        # Look for patterns like "10x5" or "10 x 5" or "10m x 5m"
        dim_match = re.search(r'(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)', message_lower)
        
        if dim_match:
            width = float(dim_match.group(1))
            length = float(dim_match.group(2))
            
            # Try to extract thickness
            thickness_match = re.search(r'(\d+)\s*mm', message_lower)
            thickness = int(thickness_match.group(1)) if thickness_match else 100
            
            try:
                quotation = calculate_complete_quotation(
                    panel_type=panel_type,
                    thickness_mm=thickness,
                    total_width_m=width,
                    total_length_m=length,
                    include_accessories=True,
                    include_fixation=True,
                    price_type="empresa",
                )
                
                result["tool_calls"].append({
                    "tool": "calculate_complete_quotation",
                    "arguments": {
                        "panel_type": panel_type,
                        "thickness_mm": thickness,
                        "total_width_m": width,
                        "total_length_m": length,
                    },
                })
                result["quotation"] = quotation
                result["response"] = format_quotation_response(quotation)
                
            except Exception as e:
                result["response"] = f"Error al generar cotización: {str(e)}"
        else:
            result["response"] = (
                "Para generar una cotización, necesito las dimensiones del área. "
                "Por ejemplo: 'Cotizame paneles Isodec de 100mm para un techo de 10x5 metros'"
            )
    
    elif "catálogo" in message_lower or "catalogo" in message_lower or "productos" in message_lower:
        summary = get_catalog_summary()
        result["tool_calls"].append({"tool": "get_catalog_summary", "arguments": {}})
        result["response"] = format_catalog_summary(summary)
    
    elif "espesores" in message_lower or "espesor" in message_lower:
        panel_type = "Isodec"  # Default
        if "isoroof" in message_lower:
            panel_type = "Isoroof"
        elif "isopanel" in message_lower:
            panel_type = "Isopanel"
        
        thicknesses = get_available_thicknesses(panel_type)
        result["tool_calls"].append({
            "tool": "get_available_thicknesses",
            "arguments": {"panel_type": panel_type}
        })
        result["response"] = f"Espesores disponibles para {panel_type}: {', '.join(map(str, thicknesses))} mm"
    
    else:
        result["response"] = (
            "¡Hola! Soy Panelin, tu asistente para paneles térmicos BMC Uruguay.\n\n"
            "Puedo ayudarte con:\n"
            "- **Cotizaciones**: 'Cotizame paneles Isodec 100mm para 10x5 metros'\n"
            "- **Catálogo**: 'Mostrame el catálogo de productos'\n"
            "- **Espesores**: '¿Qué espesores de Isoroof tienen?'\n"
            "- **Precios**: 'Precio del Isopanel 50mm'\n\n"
            "¿En qué te puedo ayudar?"
        )
    
    return result


def format_quotation_response(quotation: Dict[str, Any]) -> str:
    """Format quotation result into a readable response"""
    panels = quotation.get("panels", {})
    
    lines = [
        "## Cotización Panelin",
        "",
        f"**Producto**: {panels.get('product_name', 'Panel')}",
        f"**Espesor**: {panels.get('thickness_mm', 0)} mm",
        f"**Dimensiones por panel**: {panels.get('length_m', 0)} x {panels.get('width_m', 0)} m",
        "",
        "### Detalle",
        f"- Cantidad de paneles: **{quotation.get('panel_count', 0)}**",
        f"- Área total: **{quotation.get('total_area_m2', 0):.2f} m²**",
        f"- Precio unitario: **USD {panels.get('unit_price_usd', 0):.2f}**",
        f"- Subtotal paneles: **USD {quotation.get('panels_subtotal_usd', 0):.2f}**",
    ]
    
    if "profiles" in quotation:
        profiles = quotation["profiles"]
        lines.extend([
            "",
            "### Perfiles y Accesorios",
            f"- Goteros frontales: {profiles.get('frontal_drip_count', 0)} unidades",
            f"- Goteros laterales: {profiles.get('lateral_drip_count', 0)} unidades",
            f"- Cumbreras: {profiles.get('ridge_count', 0)} unidades",
            f"- Remaches: {profiles.get('rivets_needed', 0)} unidades",
            f"- Silicona: {profiles.get('silicone_tubes', 0)} tubos",
            f"- Subtotal perfiles: **USD {profiles.get('subtotal_usd', 0):.2f}**",
        ])
    
    if "fixation" in quotation:
        fix = quotation["fixation"]
        lines.extend([
            "",
            "### Fijaciones",
            f"- Puntos de fijación: {fix.get('fixation_points', 0)}",
            f"- Varillas necesarias: {fix.get('rods_needed', 0)}",
            f"- Tuercas: {fix.get('metal_nuts', 0) or fix.get('concrete_nuts', 0)}",
        ])
    
    lines.extend([
        "",
        "---",
        f"## TOTAL: **USD {quotation.get('grand_total_usd', 0):.2f}**",
        f"*(Precio {quotation.get('price_type', 'empresa')} + IVA)*",
        "",
        "_Cotización sujeta a confirmación de stock. Producción bajo pedido._",
    ])
    
    # Add notes from panels if any
    if panels.get("notes"):
        lines.extend(["", "**Notas:**"])
        for note in panels["notes"]:
            lines.append(f"- {note}")
    
    return "\n".join(lines)


def format_catalog_summary(summary: Dict[str, Any]) -> str:
    """Format catalog summary into readable response"""
    lines = [
        "## Catálogo BMC Uruguay",
        "",
        f"**Total de productos**: {summary.get('total_products', 0)}",
        "",
        "### Por Tipo",
    ]
    
    for ptype, count in summary.get("by_type", {}).items():
        lines.append(f"- {ptype.capitalize()}: {count}")
    
    lines.extend(["", "### Familias de Paneles"])
    
    for family, count in summary.get("by_family", {}).items():
        if "ISO" in family.upper():
            lines.append(f"- {family}: {count} variantes")
    
    lines.extend([
        "",
        f"_Última sincronización: {summary.get('last_sync', 'N/A')}_"
    ])
    
    return "\n".join(lines)
