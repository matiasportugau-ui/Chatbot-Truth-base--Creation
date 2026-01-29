#!/usr/bin/env python3
"""
Agente de Cotización Panelin
=============================

Motor de cotización expuesto como función para agentes de IA.
Compatible con OpenAI, Claude, Gemini, etc.
"""

import json
import math
from pathlib import Path
from typing import Dict, Optional, Any
import sys

# Importar motor
sys.path.insert(0, str(Path(__file__).parent))
from motor_cotizacion_panelin import MotorCotizacionPanelin
from panelin.tools.quotation_calculator import calculate_panel_quote as _calculate_panel_quote

motor = MotorCotizacionPanelin()

# Importar agente de análisis (lazy import para evitar dependencias circulares)
def get_analisis_function_schema():
    """Importa y retorna schema de análisis"""
    from agente_analisis_inteligente import get_analisis_function_schema as _get_schema
    return _get_schema()

def analizar_cotizacion_completa(*args, **kwargs):
    """Importa y ejecuta análisis completo"""
    from agente_analisis_inteligente import analizar_cotizacion_completa as _analizar
    return _analizar(*args, **kwargs)


# ============================================================================
# FUNCIONES PARA AGENTES (Function Calling)
# ============================================================================

def get_calculate_panel_quote_function_schema() -> Dict:
    """
    Schema de función para cotización determinista por m².

    Principio: el LLM solo extrae parámetros; Python calcula con Decimal.
    """
    return {
        "name": "calculate_panel_quote",
        "description": "Calcula cotización exacta determinista por m² para paneles BMC. USAR SIEMPRE para cualquier cálculo de precio. No inventar precios.",
        "parameters": {
            "type": "object",
            "properties": {
                "panel_type": {
                    "type": "string",
                    "enum": ["Isopanel", "Isodec", "Isoroof"],
                    "description": "Tipo de panel solicitado"
                },
                "thickness_mm": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Espesor en milímetros"
                },
                "length_m": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 20.0,
                    "description": "Largo del panel/área en metros"
                },
                "width_m": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 5.0,
                    "description": "Ancho del panel/área en metros"
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
                }
            },
            "required": ["panel_type", "thickness_mm", "length_m", "width_m", "quantity"]
        }
    }


def get_cotizacion_function_schema() -> Dict:
    """Retorna el schema de función para OpenAI/Claude Function Calling"""
    return {
        "name": "calcular_cotizacion",
        "description": "LEGACY: Calcula una cotización completa (materiales + IVA) usando la base de conocimiento validada. Para cálculo de precio por m² usar calculate_panel_quote().",
        "parameters": {
            "type": "object",
            "properties": {
                "producto": {
                    "type": "string",
                    "enum": ["ISODEC EPS", "ISODEC PIR", "ISOPANEL EPS", "ISOROOF 3G", "ISOROOF PLUS", "ISOROOF FOIL", "ISOWALL PIR"],
                    "description": "Tipo de producto a cotizar"
                },
                "espesor": {
                    "type": "string",
                    "description": "Espesor del panel en mm (ej: '100', '150', '200')"
                },
                "largo": {
                    "type": "number",
                    "description": "Largo del área a cubrir en metros"
                },
                "ancho": {
                    "type": "number",
                    "description": "Ancho del área a cubrir en metros"
                },
                "luz": {
                    "type": "number",
                    "description": "Distancia entre apoyos (luz) en metros. CRÍTICO para validar autoportancia."
                },
                "tipo_fijacion": {
                    "type": "string",
                    "enum": ["hormigon", "metal", "madera"],
                    "description": "Tipo de fijación: 'hormigon' para hormigón, 'metal' para metal, 'madera' para ISOROOF"
                },
                "alero_1": {
                    "type": "number",
                    "description": "Alero en extremo 1 en metros (opcional, default 0)",
                    "default": 0
                },
                "alero_2": {
                    "type": "number",
                    "description": "Alero en extremo 2 en metros (opcional, default 0)",
                    "default": 0
                }
            },
            "required": ["producto", "espesor", "largo", "ancho", "luz", "tipo_fijacion"]
        }
    }

def calculate_panel_quote_agente(
    panel_type: str,
    thickness_mm: int,
    length_m: float,
    width_m: float,
    quantity: int,
    discount_percent: float = 0.0,
) -> Dict[str, Any]:
    """
    Wrapper para exponer `calculate_panel_quote()` a agentes vía Function Calling.
    """
    try:
        result = _calculate_panel_quote(
            panel_type=panel_type,  # type: ignore[arg-type]
            thickness_mm=thickness_mm,
            length_m=length_m,
            width_m=width_m,
            quantity=quantity,
            discount_percent=discount_percent,
        )
        return {"success": True, "error": None, "quote": result}
    except Exception as e:
        return {"success": False, "error": str(e), "quote": None}


def calcular_cotizacion_agente(
    producto: str,
    espesor: str,
    largo: float,
    ancho: float,
    luz: float,
    tipo_fijacion: str = "hormigon",
    alero_1: float = 0,
    alero_2: float = 0
) -> Dict[str, Any]:
    """
    Calcula cotización - Función para agentes de IA
    
    Esta función puede ser llamada por agentes usando Function Calling.
    """
    try:
        cotizacion = motor.calcular_cotizacion(
            producto=producto,
            espesor=espesor,
            largo=largo,
            ancho=ancho,
            tipo_fijacion=tipo_fijacion,
            luz=luz,
            alero_1=alero_1,
            alero_2=alero_2
        )
        
        if 'error' in cotizacion:
            return {
                "success": False,
                "error": cotizacion['error'],
                "cotizacion": None
            }
        
        # Formatear respuesta para agente
        return {
            "success": True,
            "error": None,
            "cotizacion": {
                "producto": cotizacion['producto'],
                "espesor": cotizacion['espesor'],
                "dimensiones": cotizacion['dimensiones'],
                "validacion": {
                    "autoportancia": cotizacion['validacion']['autoportancia'],
                    "luz_efectiva": cotizacion['validacion']['luz_efectiva'],
                    "cumple_autoportancia": cotizacion['validacion']['cumple_autoportancia'],
                    "advertencia": cotizacion['validacion'].get('advertencia')
                },
                "materiales": cotizacion['materiales'],
                "costos": cotizacion['costos'],
                "resumen": {
                    "subtotal": cotizacion['costos']['subtotal'],
                    "iva": cotizacion['costos']['iva'],
                    "total": cotizacion['costos']['total'],
                    "moneda": "USD"
                }
            },
            "presentacion_texto": motor.formatear_cotizacion(cotizacion)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "cotizacion": None
        }


# ============================================================================
# CONFIGURACIONES PARA DIFERENTES PLATAFORMAS
# ============================================================================

def crear_config_openai_assistant() -> Dict:
    """Configuración para OpenAI Assistant con Function Calling"""
    return {
        "name": "Panelin - BMC Assistant Pro",
        "instructions": """Eres Panelin, BMC Assistant Pro - experto técnico en cotizaciones y sistemas constructivos BMC.

INSTRUCCIONES CRÍTICAS:
1. SIEMPRE usa la función calculate_panel_quote() para cálculos de precio (determinista con Decimal)
2. Usa calcular_cotizacion() SOLO si necesitas una cotización legacy completa (materiales + IVA)
3. NUNCA inventes precios - usa funciones que acceden a la base de conocimiento (SSOT)
4. Valida autoportancia ANTES de cotizar (si aplica)
5. Indaga: pregunta dimensiones, luz, tipo de fijación
6. Presenta resultados de forma profesional y consultiva
7. Usa analizar_cotizacion_completa() para revisar inputs, generar presupuestos, encontrar PDFs reales, comparar y aprender

PROCESO DE COTIZACIÓN:
1. Indagar: dimensiones, luz, tipo de fijación
2. Llamar calculate_panel_quote() con los datos (precio determinista)
3. Validar resultado (especialmente autoportancia)
4. Presentar cotización completa con todos los detalles
5. Ofrecer recomendaciones técnicas si aplica

PROCESO DE ANÁLISIS Y APRENDIZAJE:
1. Usa analizar_cotizacion_completa() para revisar inputs históricos
2. El sistema generará presupuestos, buscará PDFs reales, comparará y aprenderá
3. Analiza las diferencias y lecciones aprendidas
4. Incorpora el conocimiento para mejorar futuras cotizaciones""",
        "model": "gpt-4",
        "tools": [
            {
                "type": "function",
                "function": get_calculate_panel_quote_function_schema()
            },
            {
                "type": "function",
                "function": get_cotizacion_function_schema()
            },
            {
                "type": "function",
                "function": get_analisis_function_schema()
            },
            {
                "type": "code_interpreter"
            }
        ],
        "tool_resources": {
            "code_interpreter": {
                "file_ids": []  # Se llenan con archivos de conocimiento
            }
        }
    }


def crear_config_claude() -> Dict:
    """Configuración para Claude (Anthropic)"""
    return {
        "system": """Eres Panelin, BMC Assistant Pro - experto técnico en cotizaciones.

INSTRUCCIONES:
- Usa la función calculate_panel_quote() para TODO cálculo de precio (determinista)
- Usa calcular_cotizacion() solo si necesitas legacy completo (materiales + IVA)
- Valida autoportancia siempre
- Indaga dimensiones, luz, tipo de fijación antes de cotizar
- Presenta resultados profesionales""",
        "tools": [
            {
                "name": "calculate_panel_quote",
                "description": get_calculate_panel_quote_function_schema()["description"],
                "input_schema": get_calculate_panel_quote_function_schema()["parameters"]
            },
            {
                "name": "calcular_cotizacion",
                "description": get_cotizacion_function_schema()["description"],
                "input_schema": get_cotizacion_function_schema()["parameters"]
            }
        ]
    }


def crear_config_gemini() -> Dict:
    """Configuración para Gemini (Google)"""
    return {
        "system_instruction": """Eres Panelin, BMC Assistant Pro. Usa calculate_panel_quote() para TODO cálculo de precio (determinista).""",
        "tools": [
            {
                "function_declarations": [
                    {
                        "name": "calculate_panel_quote",
                        "description": get_calculate_panel_quote_function_schema()["description"],
                        "parameters": get_calculate_panel_quote_function_schema()["parameters"],
                    },
                    {
                        "name": "calcular_cotizacion",
                        "description": get_cotizacion_function_schema()["description"],
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "producto": {"type": "string"},
                                "espesor": {"type": "string"},
                                "largo": {"type": "number"},
                                "ancho": {"type": "number"},
                                "luz": {"type": "number"},
                                "tipo_fijacion": {"type": "string"}
                            },
                            "required": ["producto", "espesor", "largo", "ancho", "luz", "tipo_fijacion"]
                        }
                    }
                ]
            }
        ]
    }


# ============================================================================
# IMPLEMENTACIONES POR PLATAFORMA
# ============================================================================

class AgentePanelinOpenAI:
    """Agente Panelin para OpenAI"""
    
    def __init__(self, api_key: str, assistant_id: str = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        self.functions = {
            "calculate_panel_quote": calculate_panel_quote_agente,
            "calcular_cotizacion": calcular_cotizacion_agente,
            "analizar_cotizacion_completa": analizar_cotizacion_completa
        }
    
    def crear_asistente(self):
        """Crea asistente con función de cotización"""
        config = crear_config_openai_assistant()
        assistant = self.client.beta.assistants.create(**config)
        self.assistant_id = assistant.id
        return assistant
    
    def procesar_mensaje(self, thread_id: str, mensaje: str):
        """Procesa mensaje y ejecuta funciones si es necesario"""
        # Agregar mensaje
        message = self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=mensaje
        )
        
        # Ejecutar asistente
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        )
        
        # Esperar y manejar function calls
        import time
        while run.status in ["queued", "in_progress", "requires_action"]:
            if run.status == "requires_action":
                # Ejecutar función
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name in self.functions:
                        result = self.functions[function_name](**function_args)
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(result, ensure_ascii=False)
                        })
                
                # Enviar resultados
                run = self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            else:
                time.sleep(1)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
        
        if run.status == "completed":
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)
            return messages.data[0].content[0].text.value
        
        return None


class AgentePanelinClaude:
    """Agente Panelin para Claude (Anthropic)"""
    
    def __init__(self, api_key: str):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Instala anthropic: pip install anthropic")
        
        self.functions = {
            "calculate_panel_quote": calculate_panel_quote_agente,
            "calcular_cotizacion": calcular_cotizacion_agente
        }
    
    def chat(self, mensaje: str, model: str = "claude-3-5-sonnet-20241022"):
        """Chat con Claude usando función de cotización"""
        config = crear_config_claude()
        
        response = self.client.messages.create(
            model=model,
            max_tokens=4096,
            system=config["system"],
            tools=config["tools"],
            messages=[{"role": "user", "content": mensaje}]
        )
        
        # Si hay tool use, ejecutar función
        if response.stop_reason == "tool_use":
            tool_use = response.content[0]
            if tool_use.name == "calcular_cotizacion":
                result = calcular_cotizacion_agente(**tool_use.input)
            elif tool_use.name == "calculate_panel_quote":
                result = calculate_panel_quote_agente(**tool_use.input)
            else:
                result = {"success": False, "error": f"Tool no soportada: {tool_use.name}", "quote": None}
                # Continuar conversación con resultado
                response = self.client.messages.create(
                    model=model,
                    max_tokens=4096,
                    system=config["system"],
                    tools=config["tools"],
                    messages=[
                        {"role": "user", "content": mensaje},
                        {"role": "assistant", "content": response.content},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use.id,
                                    "content": json.dumps(result, ensure_ascii=False)
                                }
                            ]
                        }
                    ]
                )
        
        return response.content[0].text


class AgentePanelinGemini:
    """Agente Panelin para Gemini (Google)"""
    
    def __init__(self, api_key: str):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            # crear_config_gemini()["tools"] ya retorna una lista, no necesita wrapping adicional
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                tools=crear_config_gemini()["tools"]
            )
        except ImportError:
            raise ImportError("Instala google-generativeai: pip install google-generativeai")
        
        self.functions = {
            "calculate_panel_quote": calculate_panel_quote_agente,
            "calcular_cotizacion": calcular_cotizacion_agente
        }
    
    def chat(self, mensaje: str):
        """Chat con Gemini usando función de cotización"""
        response = self.model.generate_content(mensaje)
        
        # Si hay function call, ejecutarlo
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call'):
                        func_name = part.function_call.name
                        func_args = dict(part.function_call.args)
                        
                        if func_name in self.functions:
                            result = self.functions[func_name](**func_args)
                            # Continuar con resultado
                            follow_up = f"Resultado de {func_name}: {json.dumps(result, ensure_ascii=False)}"
                            response = self.model.generate_content(follow_up)
        
        return response.text


# ============================================================================
# CONFIGURACIÓN PARA GITHUB COPILOT / AGENTS
# ============================================================================

def crear_config_github_copilot() -> str:
    """Configuración para GitHub Copilot Agents"""
    return """# Panelin - BMC Assistant Pro

## Descripción
Agente de cotización para paneles constructivos BMC usando base de conocimiento validada.

## Funciones Disponibles
- `calculate_panel_quote()`: Cotización determinista por m² (Decimal + SSOT) **RECOMENDADA**
- `calcular_cotizacion()`: Calcula cotización completa con validación técnica

## Uso
```python
from agente_cotizacion_panelin import calculate_panel_quote_agente

resultado = calculate_panel_quote_agente(
    panel_type="Isodec",
    thickness_mm=100,
    length_m=3.0,
    width_m=1.2,
    quantity=50,
    discount_percent=10
)
```

## Archivos de Conocimiento
- Files/BMC_Base_Unificada_v4.json
- Files/panelin_truth_bmcuruguay_web_only_v2.json
- panelin_truth_bmcuruguay.json (SSOT para cálculo determinista)
"""


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

def ejemplo_uso_openai():
    """Ejemplo usando OpenAI"""
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY no configurada")
        return
    
    agente = AgentePanelinOpenAI(api_key)
    
    # Crear o usar asistente existente
    assistant_id = "asst_7LdhJMasW5HHGZh0cgchTGkX"  # O crear nuevo
    agente.assistant_id = assistant_id
    
    # Crear thread
    thread = agente.client.beta.threads.create()
    
    # Procesar mensaje
    respuesta = agente.procesar_mensaje(
        thread.id,
        "Hola, necesito cotizar ISODEC EPS 100mm para un techo de 10m x 5m con luz de 4.5m, fijación a hormigón"
    )
    
    print(respuesta)


if __name__ == "__main__":
    print("=" * 70)
    print("🤖 AGENTE DE COTIZACIÓN PANELIN")
    print("=" * 70)
    print("\nPlataformas soportadas:")
    print("  ✅ OpenAI (Assistants API)")
    print("  ✅ Claude (Anthropic)")
    print("  ✅ Gemini (Google)")
    print("  ✅ GitHub Copilot/Agents")
    print("\nVer ejemplos en el código o ejecutar:")
    print("  python agente_cotizacion_panelin.py")
