# 🤖 Guía: Panelin como Agente en Diferentes Plataformas

## 🎯 Resumen

Panelin puede funcionar como agente en múltiples plataformas usando **Function Calling**. El motor de cotización se expone como función que cualquier agente puede llamar.

## ✅ Plataformas Soportadas

### 1. OpenAI (✅ Implementado y Funcionando)

**Archivo:** `actualizar_panelin_con_base_conocimiento.py`

```bash
# Ya configurado
python actualizar_panelin_con_base_conocimiento.py
```

**Ventajas:**
- ✅ Function Calling nativo
- ✅ Acceso a archivos de conocimiento
- ✅ Ya funcionando

**Uso:**
```python
from agente_cotizacion_panelin import AgentePanelinOpenAI

agente = AgentePanelinOpenAI("tu-api-key", "asst_xxx")
thread = agente.client.beta.threads.create()
respuesta = agente.procesar_mensaje(thread.id, "Cotiza ISODEC 100mm...")
```

---

### 2. Claude (Anthropic) (✅ Listo para usar)

**Archivo:** `setup_claude_agent.py`

**Instalación:**
```bash
pip install anthropic
export ANTHROPIC_API_KEY=tu-key
```

**Uso:**
```bash
python setup_claude_agent.py
```

**Ventajas:**
- ✅ Excelente Function Calling
- ✅ Muy bueno para razonamiento
- ✅ API estable

---

### 3. Gemini (Google) (✅ Listo para usar)

**Archivo:** `setup_gemini_agent.py`

**Instalación:**
```bash
pip install google-generativeai
export GOOGLE_API_KEY=tu-key
```

**Uso:**
```bash
python setup_gemini_agent.py
```

**Ventajas:**
- ✅ Gratis para desarrollo
- ✅ Function Calling disponible
- ✅ Multimodal

---

### 4. Grok (xAI) (⚠️ Limitado)

Grok aún no tiene Function Calling público. Usa el motor directamente:

```python
from motor_cotizacion_panelin import MotorCotizacionPanelin

motor = MotorCotizacionPanelin()
cotizacion = motor.calcular_cotizacion(...)
print(motor.formatear_cotizacion(cotizacion))
```

---

### 5. GitHub Copilot / Agents

**Para Copilot Chat:**
Agrega comentarios en tu código:
```python
# Panelin: calcular_cotizacion_agente(producto, espesor, largo, ancho, luz, tipo_fijacion)
```

**Para GitHub Actions:**
Crea workflow que use el motor directamente.

---

## 🚀 Setup Rápido

### Opción A: OpenAI (Más fácil - Ya funciona)
```bash
# Ya está todo configurado
python actualizar_panelin_con_base_conocimiento.py
python ejercicio_cotizacion_panelin.py
```

### Opción B: Claude
```bash
pip install anthropic
export ANTHROPIC_API_KEY=tu-key
python setup_claude_agent.py
```

### Opción C: Gemini
```bash
pip install google-generativeai
export GOOGLE_API_KEY=tu-key
python setup_gemini_agent.py
```

---

## 📊 Comparación

| Plataforma | Function Calling | Facilidad | Costo | Estado |
|------------|------------------|-----------|-------|--------|
| **OpenAI** | ✅ Nativo | ⭐⭐⭐⭐⭐ | $$ | ✅ Funcionando |
| **Claude** | ✅ Excelente | ⭐⭐⭐⭐ | $$ | ✅ Listo |
| **Gemini** | ✅ Disponible | ⭐⭐⭐ | $ | ✅ Listo |
| **Grok** | ❌ No público | ⭐⭐ | $ | ⚠️ Motor directo |

---

## 💡 Recomendación

**Para máxima facilidad:** Usa **OpenAI** - ya está todo configurado y funcionando.

**Para desarrollo/testing:** Usa **Gemini** - es gratuito y funciona bien.

**Para producción:** **OpenAI** o **Claude** - ambos excelentes.

---

## 🔧 Arquitectura

```
┌─────────────────┐
│   Agente IA     │  (OpenAI/Claude/Gemini)
│   (Panelin)     │
└────────┬────────┘
         │ Function Call
         ▼
┌─────────────────┐
│ Motor Cotización│  (motor_cotizacion_panelin.py)
│   + Base KB     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Files/           │  (Base de conocimiento)
│ - BMC_Base_...   │
│ - panelin_...    │
└─────────────────┘
```

El motor funciona **independientemente** y puede integrarse con cualquier plataforma.
