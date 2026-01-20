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

motor = MotorCotizacionPanelin()


# ============================================================================
# FUNCIONES PARA AGENTES (Function Calling)
# ============================================================================

def get_cotizacion_function_schema() -> Dict:
    """Retorna el schema de función para OpenAI/Claude Function Calling"""
    return {
        "name": "calcular_cotizacion",
        "description": "Calcula una cotización completa para paneles ISODEC, ISOPANEL, ISOROOF o ISOWALL usando la base de conocimiento validada. Incluye validación técnica, cálculo de materiales y costos con IVA.",
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
1. SIEMPRE usa la función calcular_cotizacion() para generar cotizaciones
2. NUNCA inventes precios - usa la función que accede a la base de conocimiento
3. Valida autoportancia ANTES de cotizar
4. Indaga: pregunta dimensiones, luz, tipo de fijación
5. Presenta resultados de forma profesional y consultiva

PROCESO:
1. Indagar: dimensiones, luz, tipo de fijación
2. Llamar calcular_cotizacion() con los datos
3. Validar resultado (especialmente autoportancia)
4. Presentar cotización completa con todos los detalles
5. Ofrecer recomendaciones técnicas si aplica""",
        "model": "gpt-4",
        "tools": [
            {
                "type": "function",
                "function": get_cotizacion_function_schema()
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
- Usa la función calcular_cotizacion() para TODAS las cotizaciones
- Valida autoportancia siempre
- Indaga dimensiones, luz, tipo de fijación antes de cotizar
- Presenta resultados profesionales""",
        "tools": [
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
        "system_instruction": """Eres Panelin, BMC Assistant Pro. Usa la función calcular_cotizacion() para generar cotizaciones precisas usando la base de conocimiento validada.""",
        "tools": [
            {
                "function_declarations": [
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
            "calcular_cotizacion": calcular_cotizacion_agente
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
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                tools=[crear_config_gemini()["tools"]]
            )
        except ImportError:
            raise ImportError("Instala google-generativeai: pip install google-generativeai")
        
        self.functions = {
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
- `calcular_cotizacion()`: Calcula cotización completa con validación técnica

## Uso
```python
from agente_cotizacion_panelin import calcular_cotizacion_agente

resultado = calcular_cotizacion_agente(
    producto="ISODEC EPS",
    espesor="100",
    largo=10.0,
    ancho=5.0,
    luz=4.5,
    tipo_fijacion="hormigon"
)
```

## Archivos de Conocimiento
- Files/BMC_Base_Unificada_v4.json
- Files/panelin_truth_bmcuruguay_web_only_v2.json
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