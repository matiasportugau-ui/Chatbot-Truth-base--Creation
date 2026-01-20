# Configuraciones para Agentes de IA

Este documento muestra cómo configurar Panelin en diferentes plataformas de agentes.

## 🎯 Opción 1: OpenAI Assistants API (Recomendado)

### Ventajas
- ✅ Function Calling nativo
- ✅ Acceso a archivos de conocimiento
- ✅ Ya implementado y funcionando

### Configuración

```python
from agente_cotizacion_panelin import AgentePanelinOpenAI, get_cotizacion_function_schema
from openai import OpenAI

client = OpenAI(api_key="tu-api-key")

# Crear asistente con función
assistant = client.beta.assistants.create(
    name="Panelin - BMC Assistant Pro",
    instructions="""Eres Panelin. Usa calcular_cotizacion() para TODAS las cotizaciones.
    NUNCA inventes precios - siempre usa la función.""",
    model="gpt-4",
    tools=[{
        "type": "function",
        "function": get_cotizacion_function_schema()
    }]
)

# Usar
agente = AgentePanelinOpenAI("tu-api-key", assistant.id)
thread = client.beta.threads.create()
respuesta = agente.procesar_mensaje(thread.id, "Cotiza ISODEC 100mm, 10m x 5m, luz 4.5m")
```

### Archivo: `setup_openai_agent.py`
Ya creado: `actualizar_panelin_con_base_conocimiento.py`

---

## 🎯 Opción 2: Claude (Anthropic)

### Ventajas
- ✅ Function Calling excelente
- ✅ Muy bueno para razonamiento
- ✅ API estable

### Instalación
```bash
pip install anthropic
```

### Configuración

```python
from agente_cotizacion_panelin import AgentePanelinClaude, calcular_cotizacion_agente
import anthropic

client = anthropic.Anthropic(api_key="tu-api-key")

# Definir función
tools = [{
    "name": "calcular_cotizacion",
    "description": "Calcula cotización usando base de conocimiento validada",
    "input_schema": {
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
}]

# Usar
agente = AgentePanelinClaude("tu-api-key")
respuesta = agente.chat("Cotiza ISODEC 100mm, 10m x 5m, luz 4.5m")
```

### Archivo: `setup_claude_agent.py`
```python
#!/usr/bin/env python3
from agente_cotizacion_panelin import AgentePanelinClaude
import os

api_key = os.getenv("ANTHROPIC_API_KEY")
agente = AgentePanelinClaude(api_key)

respuesta = agente.chat("Hola, necesito cotizar ISODEC EPS 100mm...")
print(respuesta)
```

---

## 🎯 Opción 3: Gemini (Google)

### Ventajas
- ✅ Gratis para desarrollo
- ✅ Function Calling disponible
- ✅ Multimodal

### Instalación
```bash
pip install google-generativeai
```

### Configuración

```python
from agente_cotizacion_panelin import AgentePanelinGemini
import os

api_key = os.getenv("GOOGLE_API_KEY")
agente = AgentePanelinGemini(api_key)

respuesta = agente.chat("Cotiza ISODEC 100mm, 10m x 5m, luz 4.5m")
print(respuesta)
```

### Archivo: `setup_gemini_agent.py`
```python
#!/usr/bin/env python3
from agente_cotizacion_panelin import AgentePanelinGemini
import os

api_key = os.getenv("GOOGLE_API_KEY")
agente = AgentePanelinGemini(api_key)

respuesta = agente.chat("Hola, necesito cotizar...")
print(respuesta)
```

---

## 🎯 Opción 4: Grok (xAI)

### Configuración

Grok aún no tiene Function Calling público, pero puedes usar el motor directamente:

```python
from motor_cotizacion_panelin import MotorCotizacionPanelin

motor = MotorCotizacionPanelin()
cotizacion = motor.calcular_cotizacion(
    producto="ISODEC EPS",
    espesor="100",
    largo=10.0,
    ancho=5.0,
    luz=4.5,
    tipo_fijacion="hormigon"
)

# Luego pasar resultado a Grok para presentación
print(motor.formatear_cotizacion(cotizacion))
```

---

## 🎯 Opción 5: GitHub Copilot / GitHub Agents

### Para GitHub Copilot Chat

Agrega este comentario en tu código:

```python
# Panelin Cotización Agent
# Usa: calcular_cotizacion_agente(producto, espesor, largo, ancho, luz, tipo_fijacion)
# Ejemplo:
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

### Para GitHub Actions / Agents

Crea `.github/agents/panelin-cotizacion.yml`:

```yaml
name: Panelin Cotización Agent
description: Agente para generar cotizaciones de paneles BMC

tools:
  - name: calcular_cotizacion
    description: Calcula cotización usando base de conocimiento
    parameters:
      producto: string
      espesor: string
      largo: number
      ancho: number
      luz: number
      tipo_fijacion: string
```

---

## 🎯 Opción 6: LangChain / LlamaIndex

### Con LangChain

```python
from langchain.agents import create_openai_functions_agent
from langchain.tools import Tool
from agente_cotizacion_panelin import calcular_cotizacion_agente

tool = Tool(
    name="calcular_cotizacion",
    func=lambda **kwargs: str(calcular_cotizacion_agente(**kwargs)),
    description="Calcula cotización de paneles BMC"
)

# Crear agente
agent = create_openai_functions_agent(
    llm=llm,
    tools=[tool],
    prompt=prompt
)
```

---

## 🎯 Opción 7: AutoGen / CrewAI

### Con AutoGen

```python
from autogen import AssistantAgent, UserProxyAgent
from agente_cotizacion_panelin import calcular_cotizacion_agente

cotizador = AssistantAgent(
    name="cotizador",
    system_message="Eres Panelin. Usa calcular_cotizacion() para cotizar.",
    function_map={"calcular_cotizacion": calcular_cotizacion_agente}
)
```

---

## 📊 Comparación de Plataformas

| Plataforma | Function Calling | Facilidad | Costo | Recomendado |
|------------|------------------|-----------|-------|-------------|
| **OpenAI** | ✅ Nativo | ⭐⭐⭐⭐⭐ | $$ | ✅ Sí |
| **Claude** | ✅ Excelente | ⭐⭐⭐⭐ | $$ | ✅ Sí |
| **Gemini** | ✅ Disponible | ⭐⭐⭐ | $ | ✅ Sí |
| **Grok** | ❌ No público | ⭐⭐ | $ | ⚠️ Parcial |
| **GitHub** | ⚠️ Limitado | ⭐⭐⭐ | $$ | ⚠️ Parcial |
| **LangChain** | ✅ Flexible | ⭐⭐⭐⭐ | Variable | ✅ Sí |

---

## 🚀 Setup Rápido Recomendado

### Para OpenAI (Más fácil)
```bash
# Ya está configurado
python actualizar_panelin_con_base_conocimiento.py
python ejercicio_cotizacion_panelin.py
```

### Para Claude
```bash
pip install anthropic
export ANTHROPIC_API_KEY=tu-key
python setup_claude_agent.py  # Crear este archivo
```

### Para Gemini
```bash
pip install google-generativeai
export GOOGLE_API_KEY=tu-key
python setup_gemini_agent.py  # Crear este archivo
```

---

## 💡 Recomendación Final

**Para máxima compatibilidad y facilidad:**
1. ✅ **OpenAI Assistants API** - Ya funcionando, mejor integración
2. ✅ **Claude** - Excelente para razonamiento complejo
3. ✅ **Gemini** - Buena opción gratuita para desarrollo

**El motor de cotización funciona independientemente** y puede integrarse con cualquier plataforma que soporte Function Calling.
