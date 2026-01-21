# Panelin - Guía Rápida de Implementación

**Cómo crear Panelin como nuevo GPT en ChatGPT**

---

## 🚀 Pasos Rápidos (5 minutos)

### 1️⃣ Acceder al GPT Builder

1. Ve a [chatgpt.com](https://chatgpt.com) e inicia sesión
2. Haz clic en tu nombre (esquina superior derecha)
3. Selecciona **"GPTs"** o **"Explore GPTs"**
4. Haz clic en **"+ Create"** o ve a [chatgpt.com/gpts/editor](https://chatgpt.com/gpts/editor)

---

### 2️⃣ Configuración Básica

En la pestaña **"Create"**:

**Nombre:**

```
Panelin - BMC Assistant Pro
```

**Descripción:**

```
Experto técnico en cotizaciones y sistemas constructivos BMC. Especializado en Isopaneles (EPS y PIR), Construcción Seca e Impermeabilizantes.
```

**Conversation starters (opcional):**

```
1. "Hola, mi nombre es [nombre]"
2. "Necesito cotizar ISODEC 100mm para un techo de 6m de luz"
3. "¿Qué diferencia hay entre EPS y PIR?"
```

---

### 3️⃣ Instrucciones del Sistema (CRÍTICO)

1. Ve a la pestaña **"Configure"**
2. En el campo **"Instructions"**, copia y pega **TODO** el contenido de:
   - **`PANELIN_ULTIMATE_INSTRUCTIONS.md`**

   **O copia desde:**
   - Línea que dice: `# IDENTIDAD Y ROL`
   - Hasta la línea que dice: `# FIN DE INSTRUCCIONES`

**⚠️ IMPORTANTE:** Copia TODO el contenido, no solo una parte.

---

### 4️⃣ Subir Archivos de Knowledge Base

En la sección **"Knowledge"**, haz clic en **"Upload files"** y sube en este orden:

#### ⭐ OBLIGATORIO (Subir PRIMERO)

1. **`BMC_Base_Conocimiento_GPT-2.json`** ⭐
   - Este es el archivo más importante
   - **DEBE estar primero**

#### 📚 Recomendados (en orden)

2. **`BMC_Base_Unificada_v4.json`** (ubicación: `Files /BMC_Base_Unificada_v4.json`)
2. **`panelin_truth_bmcuruguay_web_only_v2.json`**
3. **`panelin_context_consolidacion_sin_backend.md`**
4. **`Aleros -2.rtf`** (si OpenAI no acepta .rtf, convierte a .txt o .md)
5. **`panelin_truth_bmcuruguay_catalog_v2_index.csv`** (ubicación: `Files /`)

---

### 5️⃣ Configurar Modelo y Capacidades

#### Modelo

1. En **"Configure"**, busca **"Model"**
2. Selecciona: **GPT-4** o **GPT-4 Turbo** (recomendado)

#### Capacidades

Habilita:

- ✅ **Web Browsing** (para verificar precios)
- ✅ **Code Interpreter** (OBLIGATORIO - para PDFs y cálculos)

---

### 6️⃣ Guardar y Probar

1. Haz clic en **"Save"** (esquina superior derecha)
2. Elige visibilidad: **"Only me"** (recomendado para empezar)
3. Prueba con estos tests:

**Test 1: Personalización**

```
Usuario: Hola
Esperado: Panelin pregunta tu nombre y aplica personalización
```

**Test 2: Source of Truth**

```
Usuario: ¿Cuánto cuesta ISODEC 100mm?
Esperado: $46.07 (del JSON), NO inventa precio
```

**Test 3: Validación Técnica**

```
Usuario: Necesito ISODEC 100mm para 7m de luz
Esperado: Detecta que NO cumple, sugiere 150mm
```

---

## ✅ Checklist Final

Antes de considerar Panelin "listo":

- [ ] Instrucciones del sistema copiadas completamente
- [ ] `BMC_Base_Conocimiento_GPT-2.json` subido PRIMERO
- [ ] Al menos 3 archivos de KB subidos
- [ ] Web Browsing habilitado
- [ ] Code Interpreter habilitado
- [ ] Modelo: GPT-4 o superior
- [ ] Test de personalización funciona
- [ ] Test de source of truth funciona (no inventa precios)

---

## 🆘 Si Algo No Funciona

### Panelin inventa precios

- Verifica que `BMC_Base_Conocimiento_GPT-2.json` esté subido primero
- Revisa que las instrucciones estén completas
- Prueba: "¿Cuánto cuesta ISODEC 100mm?" y verifica que lea el archivo

### No aplica personalización

- Verifica que las instrucciones de personalización estén en el campo "Instructions"
- Prueba iniciando una conversación nueva

### No lee el archivo correcto

- Asegúrate que `BMC_Base_Conocimiento_GPT-2.json` esté subido PRIMERO
- Espera unos minutos después de subir archivos (reindexación)

---

## 📚 Documentación Completa

Para más detalles, consulta:

- **`PANELIN_SETUP_COMPLETE.md`** - Guía completa paso a paso
- **`PANELIN_ULTIMATE_INSTRUCTIONS.md`** - Instrucciones del sistema
- **`PANELIN_KNOWLEDGE_BASE_GUIDE.md`** - Guía de Knowledge Base
- **`PANELIN_QUICK_REFERENCE.md`** - Referencia rápida

---

## 🎯 Resumen Ultra-Rápido

1. Ve a [chatgpt.com/gpts/editor](https://chatgpt.com/gpts/editor)
2. Nombre: "Panelin - BMC Assistant Pro"
3. Pega instrucciones de `PANELIN_ULTIMATE_INSTRUCTIONS.md`
4. Sube `BMC_Base_Conocimiento_GPT-2.json` PRIMERO
5. Habilita Web Browsing + Code Interpreter
6. Modelo: GPT-4
7. Guarda y prueba

**¡Listo!** 🚀

---

**Última actualización**: 2026-01-20
