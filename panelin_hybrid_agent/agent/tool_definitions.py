"""
Tool Definitions for LLM
========================

Define las herramientas disponibles para el agente LLM.
El LLM usa estas definiciones para entender qué herramientas puede llamar.

IMPORTANTE: El LLM solo extrae parámetros. Las funciones Python ejecutan
todos los cálculos de forma determinista.
"""

from typing import Any, Dict, List

# Tool definitions in OpenAI function calling format
QUOTATION_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "calculate_panel_quote",
        "description": """Calcula cotización exacta para paneles térmicos BMC.
USAR SIEMPRE para cualquier cálculo de precio de paneles.
El LLM NO debe hacer cálculos matemáticos—solo extraer los parámetros de la conversación.""",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "panel_type": {
                    "type": "string",
                    "enum": ["Isopanel", "Isodec", "Isoroof", "Isowall", "Isofrig"],
                    "description": "Tipo de panel solicitado"
                },
                "thickness_mm": {
                    "type": "integer",
                    "description": "Espesor en milímetros (30, 40, 50, 80, 100, 150, 200, 250)"
                },
                "length_m": {
                    "type": "number",
                    "minimum": 0.5,
                    "maximum": 14.0,
                    "description": "Largo del panel en metros"
                },
                "width_m": {
                    "type": "number",
                    "minimum": 0.5,
                    "maximum": 2.0,
                    "description": "Ancho del panel en metros (ancho útil)"
                },
                "quantity": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Cantidad de paneles"
                },
                "discount_percent": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 30,
                    "default": 0,
                    "description": "Porcentaje de descuento aplicable"
                },
                "price_type": {
                    "type": "string",
                    "enum": ["empresa", "particular", "web"],
                    "default": "empresa",
                    "description": "Tipo de cliente para determinar precio"
                },
                "insulation_type": {
                    "type": "string",
                    "enum": ["EPS", "PIR"],
                    "default": "EPS",
                    "description": "Tipo de aislación"
                }
            },
            "required": ["panel_type", "thickness_mm", "length_m", "width_m", "quantity"]
        }
    },
    {
        "name": "calculate_complete_quotation",
        "description": """Genera cotización completa incluyendo paneles, perfiles y fijaciones.
Usar cuando el cliente necesita cotización de un proyecto completo (techo, pared, etc).
Calcula automáticamente la cantidad de paneles según las dimensiones totales.""",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "panel_type": {
                    "type": "string",
                    "enum": ["Isopanel", "Isodec", "Isoroof", "Isowall", "Isofrig"],
                    "description": "Tipo de panel"
                },
                "thickness_mm": {
                    "type": "integer",
                    "description": "Espesor en milímetros"
                },
                "total_width_m": {
                    "type": "number",
                    "description": "Ancho total del área a cubrir en metros"
                },
                "total_length_m": {
                    "type": "number",
                    "description": "Largo total del área a cubrir en metros"
                },
                "include_accessories": {
                    "type": "boolean",
                    "default": True,
                    "description": "Incluir perfiles y accesorios en la cotización"
                },
                "include_fixation": {
                    "type": "boolean",
                    "default": True,
                    "description": "Incluir elementos de fijación"
                },
                "structure_type": {
                    "type": "string",
                    "enum": ["metal", "concrete"],
                    "default": "metal",
                    "description": "Tipo de estructura de soporte"
                },
                "discount_percent": {
                    "type": "number",
                    "default": 0,
                    "description": "Descuento aplicable"
                },
                "price_type": {
                    "type": "string",
                    "enum": ["empresa", "particular", "web"],
                    "default": "empresa"
                }
            },
            "required": ["panel_type", "thickness_mm", "total_width_m", "total_length_m"]
        }
    },
    {
        "name": "lookup_product_specs",
        "description": """Busca especificaciones exactas de un producto por SKU.
Usar para obtener detalles técnicos, precios, y disponibilidad de un producto específico.""",
        "parameters": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "Código SKU del producto (ej: IROOF50, ISD100EPS, GFS50)"
                }
            },
            "required": ["sku"]
        }
    },
    {
        "name": "search_products_by_criteria",
        "description": """Busca productos que cumplan ciertos criterios.
Usar cuando el cliente busca opciones o no especifica un producto exacto.""",
        "parameters": {
            "type": "object",
            "properties": {
                "family": {
                    "type": "string",
                    "description": "Familia de producto (ISOROOF, ISODEC, ISOPANEL, ISOWALL, ISOFRIG)"
                },
                "product_type": {
                    "type": "string",
                    "enum": ["panel", "perfil", "accesorio", "otro"],
                    "description": "Tipo de producto"
                },
                "thickness_mm": {
                    "type": "integer",
                    "description": "Espesor específico en mm"
                },
                "min_price": {
                    "type": "number",
                    "description": "Precio mínimo USD"
                },
                "max_price": {
                    "type": "number",
                    "description": "Precio máximo USD"
                },
                "in_stock_only": {
                    "type": "boolean",
                    "default": False,
                    "description": "Solo productos en stock"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_available_thicknesses",
        "description": """Obtiene los espesores disponibles para un tipo de panel.
Usar cuando el cliente pregunta qué espesores hay disponibles.""",
        "parameters": {
            "type": "object",
            "properties": {
                "panel_type": {
                    "type": "string",
                    "description": "Tipo de panel (Isopanel, Isodec, Isoroof, etc)"
                },
                "insulation_type": {
                    "type": "string",
                    "enum": ["EPS", "PIR"],
                    "description": "Tipo de aislación"
                }
            },
            "required": ["panel_type"]
        }
    },
    {
        "name": "calculate_fixation_points",
        "description": """Calcula puntos de fijación y materiales necesarios.
Usar para calcular varillas, tuercas, y tacos necesarios para la instalación.""",
        "parameters": {
            "type": "object",
            "properties": {
                "panel_count": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Cantidad de paneles"
                },
                "panel_length_m": {
                    "type": "number",
                    "description": "Largo de cada panel en metros"
                },
                "autoportancia_m": {
                    "type": "number",
                    "default": 5.5,
                    "description": "Distancia máxima entre apoyos (autoportancia)"
                },
                "structure_type": {
                    "type": "string",
                    "enum": ["metal", "concrete"],
                    "default": "metal",
                    "description": "Tipo de estructura"
                }
            },
            "required": ["panel_count", "panel_length_m"]
        }
    },
    {
        "name": "apply_bulk_pricing",
        "description": """Aplica precios por volumen según área total.
Usar para calcular descuentos por cantidad o recargos por pedido mínimo.""",
        "parameters": {
            "type": "object",
            "properties": {
                "total_area_m2": {
                    "type": "number",
                    "description": "Área total en metros cuadrados"
                },
                "base_price_per_m2": {
                    "type": "number",
                    "description": "Precio base por m²"
                },
                "product_type": {
                    "type": "string",
                    "description": "Tipo de producto (opcional)"
                }
            },
            "required": ["total_area_m2", "base_price_per_m2"]
        }
    },
    {
        "name": "calculate_delivery_cost",
        "description": """Calcula el costo de envío.
Usar cuando el cliente pregunta por flete o entrega.""",
        "parameters": {
            "type": "object",
            "properties": {
                "total_area_m2": {
                    "type": "number",
                    "description": "Área total en m²"
                },
                "destination_zone": {
                    "type": "string",
                    "enum": ["montevideo", "canelones", "interior", "exterior"],
                    "default": "montevideo",
                    "description": "Zona de destino"
                },
                "product_weight_kg_per_m2": {
                    "type": "number",
                    "default": 12.0,
                    "description": "Peso por m² (típico 10-15 kg/m²)"
                }
            },
            "required": ["total_area_m2"]
        }
    },
    {
        "name": "get_catalog_summary",
        "description": """Obtiene un resumen del catálogo disponible.
Usar para dar al cliente una visión general de los productos.""",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Retorna las definiciones de herramientas en formato OpenAI.
    """
    return QUOTATION_TOOLS


def get_tool_definitions_for_langchain() -> List[Dict[str, Any]]:
    """
    Retorna las definiciones adaptadas para LangChain/LangGraph.
    """
    tools = []
    for tool in QUOTATION_TOOLS:
        tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
            }
        })
    return tools


# System prompt for the agent
SYSTEM_PROMPT = """Eres Panelin, el asistente virtual de BMC Uruguay especializado en paneles térmicos aislantes.

## REGLA CRÍTICA: NUNCA CALCULES
Tienes herramientas deterministas para TODOS los cálculos. NUNCA hagas matemáticas mentalmente.
- Para precios: usa calculate_panel_quote o calculate_complete_quotation
- Para cantidades: usa calculate_fixation_points
- Para descuentos: usa apply_bulk_pricing
- Para fletes: usa calculate_delivery_cost

## Tu Rol
1. Entender qué necesita el cliente (techo, pared, cámara fría, etc.)
2. Extraer los parámetros necesarios de la conversación
3. Llamar a las herramientas apropiadas con esos parámetros
4. Presentar los resultados de forma clara y profesional

## Productos Principales
- **ISOROOF**: Techos tipo teja (30-80mm)
- **ISODEC**: Techos planos/cubiertas (100-250mm EPS, 50-120mm PIR)
- **ISOPANEL**: Paredes y fachadas (50-250mm EPS)
- **ISOWALL**: Fachadas (50-80mm PIR)
- **ISOFRIG**: Cámaras frigoríficas (40-100mm)

## Información que debes obtener para cotizar:
1. Tipo de aplicación (techo, pared, cámara fría)
2. Dimensiones (largo x ancho del área)
3. Espesor deseado o nivel de aislación requerido
4. Tipo de cliente (empresa o particular)
5. Ubicación para flete (opcional)

## Formato de Respuesta
Presenta las cotizaciones de forma estructurada:
- Producto y especificaciones
- Cantidad calculada
- Precio unitario y total
- Accesorios incluidos (si aplica)
- Notas importantes (pedidos mínimos, plazos, etc.)

Siempre verifica que calculation_verified=True en los resultados."""
