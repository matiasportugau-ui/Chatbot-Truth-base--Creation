# 🤖 Guía: Agente Especialista en Build AI Apps

## 🎯 Resumen

El **Agente Build AI Apps** es un especialista en crear AI mini-apps y workflows personalizados usando **Google Labs Gems** (Opal). Te ayuda a diseñar, validar y optimizar workflows complejos que pueden ejecutarse como Gems en Google Labs.

## ✨ Características Principales

- ✅ **Diseño de Workflows**: Crea workflows multi-paso desde descripciones en lenguaje natural
- ✅ **Generación de Descripciones**: Genera descripciones optimizadas para Google Labs
- ✅ **Validación Automática**: Valida que los workflows estén bien estructurados
- ✅ **Optimización**: Detecta y sugiere mejoras en workflows
- ✅ **Plantillas Predefinidas**: Incluye plantillas listas para usar
- ✅ **Remix**: Crea variaciones de workflows existentes
- ✅ **Multi-plataforma**: Compatible con OpenAI, Claude y Gemini

---

## 🚀 Inicio Rápido

### Instalación

```bash
# Asegúrate de tener las dependencias
pip install openai anthropic google-generativeai
```

### Configuración

```bash
# Configurar variables de entorno
export OPENAI_API_KEY="tu-key"  # Opcional
export ANTHROPIC_API_KEY="tu-key"  # Opcional
export GOOGLE_API_KEY="tu-key"  # Opcional

# Ejecutar setup
python setup_build_ai_apps_agent.py
```

### Uso Básico

```python
from agente_build_ai_apps import diseñar_ai_app

# Diseñar un AI app
resultado = diseñar_ai_app(
    descripcion="Crea un app que tome una dirección de bienes raíces, investigue el vecindario, escriba una descripción de listado, y genere tres captions para Instagram"
)

print(resultado['descripcion_gem'])  # Descripción lista para Google Labs
print(resultado['instrucciones'])  # Instrucciones paso a paso
```

---

## 📚 Uso Detallado

### 1. Diseñar un Workflow desde Cero

```python
from agente_build_ai_apps import diseñar_ai_app

resultado = diseñar_ai_app(
    descripcion="Crea un app que analice un tema, busque información relevante, y genere un reporte completo con insights",
    tipo="research",  # Opcional: automation, research, content, data_processing, analysis, custom
    optimizar=True,
    exportar_formato="json"  # json, markdown, gem_description
)

# Acceder a los resultados
workflow = resultado['workflow']
print(f"Nombre: {workflow['nombre']}")
print(f"Pasos: {len(workflow['pasos'])}")
print(f"Válido: {resultado['valido']}")

# Descripción lista para Google Labs
print(resultado['descripcion_gem'])

# Instrucciones paso a paso
for instruccion in resultado['instrucciones']:
    print(instruccion)
```

### 2. Usar Plantillas Predefinidas

```python
from agente_build_ai_apps import listar_plantillas_ai_apps, usar_plantilla_ai_app

# Listar plantillas disponibles
plantillas = listar_plantillas_ai_apps()
for plantilla in plantillas['plantillas']:
    print(f"- {plantilla['id']}: {plantilla['nombre']}")

# Usar una plantilla
resultado = usar_plantilla_ai_app(
    id_plantilla="research_assistant",
    personalizar_nombre="Mi Asistente de Investigación"
)

print(resultado['descripcion_gem'])
```

### 3. Trabajar con el Agente Directamente

```python
from agente_build_ai_apps import AgenteBuildAIApps

agente = AgenteBuildAIApps()

# Diseñar workflow
workflow = agente.diseñar_workflow(
    descripcion="Crea un app que genere recetas basadas en ingredientes",
    tipo="content"
)

# Optimizar
workflow_optimizado = agente.optimizar_workflow(workflow)

# Remix
workflow_remix = agente.remix_workflow(
    workflow_base=workflow,
    modificaciones="Agrega un paso para traducir las recetas al español"
)

# Exportar
descripcion_md = agente.exportar_workflow(workflow, formato="markdown")
print(descripcion_md)

# Guardar
ruta = agente.guardar_workflow(workflow)
print(f"Guardado en: {ruta}")
```

---

## 🔧 Integración con Agentes de IA

### OpenAI Assistants API

```python
from openai import OpenAI
from agente_build_ai_apps import get_build_ai_apps_function_schema

client = OpenAI(api_key="tu-key")

assistant = client.beta.assistants.create(
    name="Build AI Apps Specialist",
    instructions="Eres un especialista en crear AI apps...",
    model="gpt-4",
    tools=[{
        "type": "function",
        "function": get_build_ai_apps_function_schema()
    }]
)

# Usar el asistente
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Diseña un app que analice tweets y genere un resumen de sentimientos"
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)
```

### Claude (Anthropic)

```python
import anthropic
from agente_build_ai_apps import diseñar_ai_app

client = anthropic.Anthropic(api_key="tu-key")

# Definir herramientas
tools = [{
    "name": "diseñar_ai_app",
    "description": "Diseña un AI app completo...",
    "input_schema": {
        "type": "object",
        "properties": {
            "descripcion": {"type": "string"},
            "tipo": {"type": "string"}
        }
    }
}]

# Usar en mensajes
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[{
        "role": "user",
        "content": "Diseña un app que analice tweets y genere un resumen de sentimientos"
    }]
)
```

### Gemini (Google)

```python
import google.generativeai as genai
from agente_build_ai_apps import diseñar_ai_app

genai.configure(api_key="tu-key")

# Definir herramientas
tools = [{
    "function_declarations": [{
        "name": "diseñar_ai_app",
        "description": "Diseña un AI app completo...",
        "parameters": {
            "type": "object",
            "properties": {
                "descripcion": {"type": "string"}
            }
        }
    }]
}]

model = genai.GenerativeModel('gemini-pro', tools=tools)
response = model.generate_content("Diseña un app que analice tweets y genere un resumen de sentimientos")
```

---

## 📋 Tipos de Workflows

### 1. Automation
Workflows de automatización multi-paso que ejecutan tareas secuenciales.

**Ejemplo:**
```
"Crea un app que tome una dirección, busque información del vecindario, genere una descripción, y cree posts para redes sociales"
```

### 2. Research
Workflows de investigación que buscan, sintetizan y analizan información.

**Ejemplo:**
```
"Crea un app que investigue un tema, busque fuentes relevantes, y genere un reporte completo"
```

### 3. Content
Workflows de generación de contenido en múltiples formatos.

**Ejemplo:**
```
"Crea un app que genere recetas basadas en ingredientes disponibles"
```

### 4. Data Processing
Workflows que procesan y transforman datos.

**Ejemplo:**
```
"Crea un app que procese un CSV, analice los datos, y genere visualizaciones"
```

### 5. Analysis
Workflows de análisis y evaluación.

**Ejemplo:**
```
"Crea un app que analice un texto y genere un reporte de sentimientos y temas"
```

### 6. Custom
Workflows personalizados que no encajan en las categorías anteriores.

---

## 🎨 Plantillas Disponibles

### Recipe Genie
Genera recetas basadas en ingredientes disponibles.

```python
usar_plantilla_ai_app("recipe_genie")
```

### Marketing Maven
Genera estrategias y contenido de marketing.

```python
usar_plantilla_ai_app("marketing_maven")
```

### Research Assistant
Investiga un tema y genera un reporte completo.

```python
usar_plantilla_ai_app("research_assistant")
```

---

## 🔍 Estructura de un Workflow

Un workflow tiene la siguiente estructura:

```json
{
  "nombre": "Nombre del Workflow",
  "descripcion": "Descripción del propósito",
  "tipo": "research",
  "pasos": [
    {
      "orden": 1,
      "tipo": "input",
      "nombre": "Recibir entrada",
      "descripcion": "Recibe los datos de entrada",
      "configuracion": {}
    },
    {
      "orden": 2,
      "tipo": "search",
      "nombre": "Búsqueda",
      "descripcion": "Busca información",
      "configuracion": {}
    }
  ],
  "nodos": [
    {
      "id": "nodo_1",
      "tipo": "input",
      "nombre": "Recibir entrada",
      "conexiones": [{"target": "nodo_2", "tipo": "secuencial"}]
    }
  ],
  "validacion": {
    "valido": true,
    "errores": [],
    "advertencias": []
  }
}
```

---

## 🛠️ Funciones Disponibles

### Para Agentes de IA

1. **`diseñar_ai_app()`** - Diseña un AI app completo
2. **`listar_plantillas_ai_apps()`** - Lista plantillas disponibles
3. **`usar_plantilla_ai_app()`** - Crea un app desde una plantilla

### Métodos del Agente

1. **`diseñar_workflow()`** - Diseña un workflow
2. **`optimizar_workflow()`** - Optimiza un workflow
3. **`remix_workflow()`** - Crea una variación
4. **`generar_descripcion_gem()`** - Genera descripción para Google Labs
5. **`exportar_workflow()`** - Exporta en diferentes formatos
6. **`guardar_workflow()`** - Guarda en archivo JSON

---

## 📝 Ejemplos Completos

### Ejemplo 1: App de Análisis de Sentimientos

```python
from agente_build_ai_apps import diseñar_ai_app

resultado = diseñar_ai_app(
    descripcion="Crea un app que analice tweets sobre un tema, determine el sentimiento de cada tweet, y genere un reporte con estadísticas y ejemplos",
    tipo="analysis"
)

print("Descripción para Google Labs:")
print(resultado['descripcion_gem'])
```

### Ejemplo 2: App de Generación de Contenido

```python
from agente_build_ai_apps import diseñar_ai_app

resultado = diseñar_ai_app(
    descripcion="Crea un app que tome un brief de marketing, investigue la competencia, genere estrategias, y cree contenido para Instagram, Twitter y LinkedIn",
    tipo="content",
    optimizar=True
)

# Guardar workflow
from agente_build_ai_apps import AgenteBuildAIApps
agente = AgenteBuildAIApps()
ruta = agente.guardar_workflow(resultado['workflow'], "marketing_content_workflow.json")
print(f"Workflow guardado en: {ruta}")
```

### Ejemplo 3: Remix de una Plantilla

```python
from agente_build_ai_apps import AgenteBuildAIApps

agente = AgenteBuildAIApps()

# Usar plantilla base
workflow_base = agente.usar_plantilla("research_assistant")

# Remix con modificaciones
workflow_remix = agente.remix_workflow(
    workflow_base,
    modificaciones="Agrega un paso para traducir el reporte al español y generar un resumen ejecutivo"
)

# Exportar como markdown
md = agente.exportar_workflow(workflow_remix, formato="markdown")
print(md)
```

---

## 🎯 Mejores Prácticas

1. **Sé Específico**: Describe claramente qué debe hacer cada paso del workflow
2. **Usa Plantillas**: Empieza con una plantilla y personaliza según necesites
3. **Valida Siempre**: Revisa que el workflow sea válido antes de usarlo
4. **Optimiza**: Usa la función de optimización para mejorar workflows complejos
5. **Exporta en el Formato Correcto**: Usa `gem_description` para Google Labs
6. **Guarda tus Workflows**: Guarda workflows exitosos para reutilizarlos

---

## 🐛 Troubleshooting

### Error: "Workflow debe tener entrada"
- **Solución**: Asegúrate de que tu descripción mencione qué datos recibe el app

### Error: "Workflow debe tener salida"
- **Solución**: Asegúrate de que tu descripción mencione qué genera el app

### Workflow muy complejo
- **Solución**: Usa `optimizar_workflow()` o divide en sub-workflows más pequeños

### Descripción no se entiende
- **Solución**: Sé más específico y menciona acciones claras (buscar, generar, analizar, etc.)

---

## 📚 Recursos Adicionales

- [Google Labs Gems Documentation](https://support.google.com/gemini/answer/16802014)
- [Opal Documentation](https://developers.google.com/opal)
- [Gemini Overview](https://gemini.google/overview/gems/)

---

## 💡 Tips y Trucos

1. **Usa Verbos de Acción**: "buscar", "generar", "analizar", "comparar" ayudan al agente a entender mejor
2. **Menciona Formatos**: Si necesitas un formato específico (JSON, Markdown, etc.), menciónalo
3. **Especifica Múltiples Salidas**: Puedes pedir múltiples outputs (ej: "genera un reporte Y tres posts")
4. **Combina Plantillas**: Usa una plantilla como base y remixéala para tus necesidades
5. **Valida con Ejemplos**: Prueba el workflow con ejemplos reales antes de usarlo en producción

---

## ✅ Checklist para Crear un AI App

- [ ] Describir claramente el propósito del app
- [ ] Identificar las entradas necesarias
- [ ] Definir los pasos del workflow
- [ ] Especificar el formato de salida
- [ ] Validar el workflow generado
- [ ] Optimizar si es necesario
- [ ] Probar con ejemplos reales
- [ ] Exportar descripción para Google Labs
- [ ] Seguir instrucciones paso a paso
- [ ] Probar el Gem en Google Labs
- [ ] Ajustar según sea necesario

---

¡Listo para crear tus propios AI apps! 🚀
