# Troubleshooting: Model Selection Issue - Only AUTO Available

## 🔴 Problema

No puedes seleccionar modelos específicos (GPT-4, GPT-4 Turbo, etc.) en el GPT Builder, solo aparece la opción "AUTO".

## ✅ Soluciones

### Solución 1: Verificar Ubicación del Selector de Modelo

El selector de modelo puede estar en diferentes lugares según la versión del GPT Builder:

1. **Pestaña "Configure"** → Busca sección **"Model"** o **"Modelo recomendado"**
2. **Pestaña "Create"** → A veces aparece en la parte superior
3. **Configuración avanzada** → Puede estar en un menú desplegable

**Pasos**:
- Abre tu GPT en el editor
- Revisa todas las pestañas y secciones
- Busca cualquier menú desplegable que diga "AUTO" o "Model"

### Solución 2: Verificar Plan de OpenAI

El acceso a modelos específicos depende de tu plan:

| Plan | Acceso a Modelos |
|------|------------------|
| **ChatGPT Free** | ❌ Solo AUTO |
| **ChatGPT Plus** | ✅ GPT-4, GPT-4 Turbo |
| **ChatGPT Team** | ✅ Todos los modelos |
| **ChatGPT Enterprise** | ✅ Todos los modelos + prioridad |

**Cómo verificar**:
1. Ve a [chatgpt.com](https://chatgpt.com)
2. Click en tu nombre (esquina superior derecha)
3. Selecciona **"Settings"** → **"Plan"**
4. Verifica tu plan actual

**Si tienes Free**:
- Considera actualizar a **Plus** ($20/mes) para acceso a GPT-4
- O usa la API directamente (ver Solución 4)

### Solución 3: Limpiar Cache y Recargar

A veces es un problema de interfaz:

1. **Cierra completamente el navegador**
2. **Limpia el cache**:
   - Chrome/Edge: `Ctrl+Shift+Delete` (Windows) o `Cmd+Shift+Delete` (Mac)
   - Selecciona "Cached images and files"
   - Click "Clear data"
3. **Abre el GPT Builder nuevamente**
4. **Intenta cambiar el modelo de nuevo**

### Solución 4: Usar OpenAI API Directamente

Si el GPT Builder no te permite cambiar el modelo, puedes crear tu propio cliente usando la API:

#### Opción A: Python Script

```python
import openai
from openai import OpenAI

client = OpenAI(api_key="tu-api-key")

def chat_with_panelin(user_message, system_prompt):
    response = client.chat.completions.create(
        model="gpt-4",  # Puedes cambiar a "gpt-4-turbo", "gpt-4o", etc.
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

# Uso
system_prompt = """
# IDENTIDAD Y ROL
Te llamas Panelin, eres el BMC Assistant Pro...
[resto de instrucciones]
"""

response = chat_with_panelin("Hola, necesito cotizar ISODEC 100mm", system_prompt)
print(response)
```

#### Opción B: Usar Assistants API

La API de Assistants te da más control:

```python
import openai
from openai import OpenAI

client = OpenAI(api_key="tu-api-key")

# Crear un Assistant con modelo específico
assistant = client.beta.assistants.create(
    name="Panelin - BMC Assistant Pro",
    instructions="""
    # IDENTIDAD Y ROL
    Te llamas Panelin, eres el BMC Assistant Pro...
    [instrucciones completas]
    """,
    model="gpt-4",  # Especificas el modelo aquí
    tools=[{"type": "code_interpreter"}],
)

# Usar el assistant
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Hola, necesito cotizar ISODEC 100mm"
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)
```

### Solución 5: Contactar Soporte de OpenAI

Si ninguna solución funciona:

1. Ve a [help.openai.com](https://help.openai.com)
2. Crea un ticket de soporte
3. Menciona:
   - Tu plan de OpenAI
   - Que no puedes cambiar el modelo de "AUTO"
   - Captura de pantalla del GPT Builder
   - Qué modelos esperas ver disponibles

## 📋 Checklist de Diagnóstico

Antes de contactar soporte, verifica:

- [ ] ¿Qué plan de OpenAI tienes? (Free/Plus/Team/Enterprise)
- [ ] ¿Dónde estás buscando el selector de modelo? (¿Revisaste todas las pestañas?)
- [ ] ¿Has limpiado el cache del navegador?
- [ ] ¿Has probado en otro navegador? (Chrome, Firefox, Safari, Edge)
- [ ] ¿Has probado en modo incógnito?
- [ ] ¿Tienes acceso a GPT-4 en el chat normal de ChatGPT? (Verifica en chatgpt.com)

## 🎯 Modelo Recomendado para Panelin

Para el mejor rendimiento de Panelin, usa:

1. **GPT-4** o **GPT-4 Turbo** (recomendado)
   - Mejor precisión en cálculos técnicos
   - Mejor comprensión de contexto largo
   - Respuestas más consistentes

2. **GPT-4o** (si está disponible)
   - Última versión
   - Mejor rendimiento general

3. **Evitar**: GPT-3.5 Turbo
   - Menos preciso para cálculos técnicos
   - Puede inventar precios si no encuentra información

## 📚 Recursos Adicionales

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [GPT Builder Guide](https://platform.openai.com/docs/guides/gpt)
- [Pricing Information](https://openai.com/pricing)

## 💡 Workaround Temporal

Si necesitas usar un modelo específico AHORA y no puedes cambiarlo en el Builder:

1. Usa el chat normal de ChatGPT
2. Selecciona el modelo que quieras (GPT-4, etc.)
3. Copia las instrucciones de Panelin en el primer mensaje
4. Adjunta los archivos de Knowledge Base como contexto

**Nota**: Esto no es ideal, pero funciona como solución temporal mientras resuelves el problema del GPT Builder.
