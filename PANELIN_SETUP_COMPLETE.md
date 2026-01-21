# Panelin - Guía de Configuración Completa
**Versión:** 2.0 Ultimate  
**Fecha:** 2026-01-20

Esta guía te lleva paso a paso para configurar Panelin desde cero en el GPT Builder de OpenAI.

---

## 📋 Requisitos Previos

- ✅ Cuenta de OpenAI con plan **Plus, Team, Enterprise o Edu**
- ✅ Acceso al **GPT Builder** (Creador de GPTs)
- ✅ Todos los archivos de Knowledge Base listos (ver lista abajo)
- ✅ Instrucciones del sistema preparadas (ver `PANELIN_ULTIMATE_INSTRUCTIONS.md`)

---

## 🚀 Paso 1: Acceder al GPT Builder

1. Ve a [chatgpt.com](https://chatgpt.com)
2. Haz clic en tu nombre (esquina superior derecha)
3. Selecciona **"GPTs"** o **"Explore GPTs"**
4. Haz clic en **"+ Create"** o ve directamente a [chatgpt.com/gpts/editor](https://chatgpt.com/gpts/editor)

---

## 📝 Paso 2: Configuración Básica (Pestaña "Create")

### 2.1 Nombre y Descripción

**Nombre del GPT:**
```
Panelin - BMC Assistant Pro
```

**Descripción:**
```
Experto técnico en cotizaciones y sistemas constructivos BMC. Especializado en Isopaneles (EPS y PIR), Construcción Seca e Impermeabilizantes. Genera cotizaciones técnicas precisas y asesora en soluciones constructivas.
```

**Instrucciones para el usuario (opcional):**
```
Pregúntame sobre techos, paredes, impermeabilización o solicita una cotización técnica. Soy Panelin, tu asistente experto en construcción seca.
```

---

## ⚙️ Paso 3: Instrucciones del Sistema (Pestaña "Configure")

### 3.1 Instrucciones Completas del Sistema

1. Ve a la pestaña **"Configure"**
2. En el campo **"Instructions"**, copia y pega el contenido completo de:
   - **`PANELIN_ULTIMATE_INSTRUCTIONS.md`** (archivo completo)

   O copia directamente desde la sección "# IDENTIDAD Y ROL" hasta "# FIN DE INSTRUCCIONES"

**IMPORTANTE**: Asegúrate de copiar TODO el contenido, no solo una parte.

---

## 📚 Paso 4: Subir Archivos de Knowledge Base

### 4.1 Orden de Subida (CRÍTICO)

En la sección **"Knowledge"**, haz clic en **"Upload files"** y sube en este orden:

#### PRIORIDAD 1 - Nivel 1 (MASTER) ⭐
1. **`BMC_Base_Conocimiento_GPT-2.json`** ⭐ (PRIMERO - OBLIGATORIO)
   - Este es el archivo principal y único de Nivel 1
   - Fuente de verdad para precios y fórmulas
   - **DEBE estar primero**

#### PRIORIDAD 2 - Nivel 2 (Validación)
3. **`BMC_Base_Unificada_v4.json`**
   - Para validación y cross-reference
   - Ubicación: `Files /BMC_Base_Unificada_v4.json`

#### PRIORIDAD 3 - Nivel 3 (Dinámico)
4. **`panelin_truth_bmcuruguay_web_only_v2.json`**
   - Snapshot web para verificación dinámica
   - Ubicación: `panelin_truth_bmcuruguay_web_only_v2.json` o `Files /panelin_truth_bmcuruguay_web_only_v2.json`

#### PRIORIDAD 4 - Nivel 4 (Soporte)
5. **`panelin_context_consolidacion_sin_backend.md`**
   - SOP de consolidación y comandos
   - Ubicación: `panelin_context_consolidacion_sin_backend.md`

6. **`Aleros.rtf`** o **`Aleros -2.rtf`**
   - Reglas técnicas de voladizos
   - Ubicación: `Files /Aleros -2.rtf`
   - **Nota**: Si OpenAI no acepta .rtf, convierte el archivo a .txt o .md primero

7. **`panelin_truth_bmcuruguay_catalog_v2_index.csv`**
   - Índice de productos (accesible via Code Interpreter)
   - Ubicación: `Files /panelin_truth_bmcuruguay_catalog_v2_index.csv`

#### OPCIONAL
8. **`BMC_Catalogo_Completo_Shopify (1).json`** (si está disponible)
   - Catálogo completo de productos

---

## 🤖 Paso 5: Configurar Modelo

### 5.1 Seleccionar Modelo

1. En la pestaña **"Configure"**, busca la sección **"Model"**
2. Haz clic en el dropdown que dice **"AUTO"**
3. Selecciona:
   - **GPT-4** (recomendado para tareas complejas) ⭐
   - **GPT-4 Turbo** (más rápido, buena calidad)
   - **GPT-4o** (última versión, mejor rendimiento)

**Recomendación**: Usa **GPT-4** o **GPT-4 Turbo** para garantizar:
- Precisión en cálculos técnicos
- Comprensión de contexto complejo
- Generación de cotizaciones detalladas

### 5.2 Si Solo Aparece "AUTO"

**Causa posible**: Tu plan de OpenAI puede no incluir acceso a modelos específicos.

**Verifica tu plan**:
- **ChatGPT Plus**: Debería tener acceso a GPT-4
- **ChatGPT Team/Enterprise**: Acceso completo a todos los modelos
- **ChatGPT Free**: Solo AUTO disponible

**Cómo verificar**:
1. Ve a [chatgpt.com](https://chatgpt.com)
2. Haz clic en tu nombre → **"Settings"** → **"Plan"**
3. Verifica qué plan tienes activo

---

## 🛠️ Paso 6: Habilitar Capacidades (Capabilities)

En la sección **"Capabilities"**, habilita:

- ✅ **Web Browsing** (Búsqueda en la web)
  - Para verificar precios actualizados en Shopify
  - Para buscar información técnica adicional si es necesario

- ✅ **Code Interpreter** (Análisis de datos) ⭐ OBLIGATORIO
  - Para generar PDFs
  - Para procesar el CSV
  - Para cálculos complejos

- ❌ **Image Generation** (Opcional)
  - Solo si quieres que pueda generar diagramas o ilustraciones

**NO habilitar** (a menos que lo necesites):
- ❌ Canvas (por ahora)

---

## 🎯 Paso 7: Prompt Starters (Opcional pero Recomendado)

En la sección **"Conversation starters"**, agrega ejemplos:

```
1. "Hola, mi nombre es [nombre]"
2. "Necesito cotizar ISODEC 100mm para un techo de 6m de luz"
3. "¿Qué diferencia hay entre EPS y PIR?"
4. "Genera un PDF de la cotización"
5. "/estado"
6. "/evaluar_ventas"
7. "/entrenar"
```

---

## 🔧 Paso 8: Configuración Avanzada (Opcional)

### 8.1 Actions (APIs) - Si necesitas integración externa

Si quieres conectar con Shopify API u otros servicios:

1. Haz clic en **"Create new action"**
2. Define el schema OpenAPI
3. Configura autenticación si es necesario

**Nota**: Esto es opcional. Panelin funciona perfectamente sin Actions.

### 8.2 Configuración de Privacidad

- **Visibilidad**: 
  - "Only me" (solo tú) - Recomendado para empezar
  - "Anyone with a link" (compartir link)
  - "Public" (público en GPT Store)

---

## ✅ Paso 9: Guardar y Probar

### 9.1 Guardar el GPT

1. Haz clic en **"Save"** (esquina superior derecha)
2. Elige visibilidad:
   - **"Only me"** (recomendado para empezar)
   - **"Anyone with a link"**
   - **"Public"**

### 9.2 Probar el GPT

Haz clic en **"Preview"** o ve a la pestaña de chat y prueba estos casos:

#### Test 1: Personalización
```
Usuario: Hola
Panelin debe: Preguntar nombre y aplicar personalización
```

#### Test 2: Source of Truth
```
Usuario: ¿Cuánto cuesta ISODEC 100mm?
Panelin debe:
- Leer de BMC_Base_Conocimiento_GPT-2.json
- Dar precio exacto del JSON (ej: $46.07)
- NO inventar precio
```

#### Test 3: Validación Técnica
```
Usuario: Necesito ISODEC 100mm para 7m de luz
Panelin debe:
- Detectar que NO cumple (autoportancia 5.5m < 7m)
- Sugerir 150mm o 200mm
- Explicar por qué
```

#### Test 4: Cotización Completa
```
Usuario: Cotizar ISODEC 100mm, 5m de luz, 4 paneles, fijación a metal
Panelin debe:
- Validar autoportancia (5.5m > 5m ✓)
- Calcular apoyos, puntos fijación, varillas, etc.
- Usar fórmulas del JSON
- Presentar desglose con IVA
```

#### Test 5: Comando SOP
```
Usuario: /estado
Panelin debe:
- Mostrar resumen del Ledger
- Indicar riesgo de contexto
- Dar recomendación
```

#### Test 6: Guardrails
```
Usuario: ¿Cuánto cuesta ISODEC 300mm?
Panelin debe:
- Buscar en JSON
- NO encontrar 300mm (no existe)
- Responder: "No tengo esa información en mi base de conocimiento"
- NO inventar precio
```

---

## 🔍 Paso 10: Verificación y Ajustes

### 10.1 Checklist de Verificación

- [ ] ✅ Instrucciones del sistema completas y correctas
- [ ] ✅ `BMC_Base_Conocimiento_GPT-2.json` subido (Nivel 1)
- [ ] ✅ `BMC_Base_Unificada_v4.json` subido (Nivel 2)
- [ ] ✅ `panelin_truth_bmcuruguay_web_only_v2.json` subido (Nivel 3)
- [ ] ✅ `panelin_context_consolidacion_sin_backend.md` subido (Nivel 4)
- [ ] ✅ `Aleros.rtf` o equivalente subido (Nivel 4)
- [ ] ✅ Web Browsing habilitado
- [ ] ✅ Code Interpreter habilitado
- [ ] ✅ Modelo configurado (GPT-4 o superior)
- [ ] ✅ Personalización funciona (Mauro, Martin, Rami)
- [ ] ✅ Source of truth funciona (lee JSON correcto)
- [ ] ✅ Cotizaciones calculan correctamente
- [ ] ✅ Validación técnica funciona (autoportancia)
- [ ] ✅ Comandos SOP funcionan (/estado, /checkpoint, /consolidar)
- [ ] ✅ Guardrails funcionan (no inventa datos)

### 10.2 Ajustes Comunes

**Si Panelin no lee el archivo correcto:**
- Revisa que `BMC_Base_Conocimiento_GPT-2.json` esté subido primero
- Refuerza en instrucciones: "SIEMPRE leer BMC_Base_Conocimiento_GPT-2.json primero"

**Si inventa precios:**
- Agrega guardrail más estricto: "NUNCA dar precio sin leer JSON primero"
- Prueba con: "¿Cuánto cuesta X?" y verifica que lea el archivo

**Si no aplica personalización:**
- Verifica que las instrucciones de personalización estén claras
- Prueba iniciando conversación nueva

**Si las fórmulas están mal:**
- Verifica que use fórmulas de `formulas_cotizacion` del JSON
- Agrega ejemplo en instrucciones

---

## 📊 Paso 11: Monitoreo y Mejora Continua

### 11.1 Métricas a Monitorear

1. **Precisión**:
   - ¿Usa fuente correcta (Nivel 1)?
   - ¿Fórmulas correctas?
   - ¿Precios correctos?

2. **Completitud**:
   - ¿Responde sin "no sé" innecesariamente?
   - ¿Cubre todos los productos?

3. **Eficiencia**:
   - ¿Tiempo de respuesta razonable?
   - ¿Usa contexto eficientemente?

### 11.2 Actualización de Archivos

Cuando actualices archivos en Knowledge Base:

1. Ve a **"Configure"** → **"Knowledge"**
2. Elimina el archivo antiguo
3. Sube el nuevo archivo
4. **IMPORTANTE**: El GPT puede tardar unos minutos en reindexar
5. Prueba que funcione correctamente

---

## 🎓 Tips Finales

### ✅ DO's

1. **Empieza simple**: Crea el GPT básico primero, luego agrega complejidad
2. **Prueba exhaustivamente**: Testea todos los casos de uso
3. **Documenta cambios**: Anota qué modificas y por qué
4. **Mantén archivos actualizados**: Sincroniza KB con cambios reales
5. **Refuerza guardrails**: Si algo falla, agrega regla más estricta

### ❌ DON'Ts

1. **No subas archivos duplicados**: Puede confundir al GPT
2. **No cambies instrucciones sin probar**: Cada cambio afecta comportamiento
3. **No ignores errores**: Si inventa datos, corrígelo inmediatamente
4. **No uses fuentes secundarias para respuestas**: Siempre Nivel 1 primero
5. **No olvides probar personalización**: Es parte inamovible

---

## 📝 Resumen Rápido

1. ✅ Ve a [chatgpt.com/gpts/editor](https://chatgpt.com/gpts/editor)
2. ✅ Nombre: "Panelin - BMC Assistant Pro"
3. ✅ Pega instrucciones completas de `PANELIN_ULTIMATE_INSTRUCTIONS.md`
4. ✅ Sube archivos de Knowledge Base en orden de prioridad:
   - `BMC_Base_Conocimiento_GPT-2.json` (PRIMERO)
   - `BMC_Base_Unificada_v4.json`
   - `panelin_truth_bmcuruguay_web_only_v2.json`
   - `panelin_context_consolidacion_sin_backend.md`
   - `Aleros.rtf` (o .txt/.md)
   - `panelin_truth_bmcuruguay_catalog_v2_index.csv`
5. ✅ Habilita Web Browsing y Code Interpreter
6. ✅ Configura modelo: GPT-4 o GPT-4 Turbo
7. ✅ Guarda y prueba
8. ✅ Verifica que funcione correctamente
9. ✅ Monitorea y mejora continuamente

---

## 🔗 Archivos de Referencia

- **`PANELIN_ULTIMATE_INSTRUCTIONS.md`** - Instrucciones completas del sistema
- **`PANELIN_KNOWLEDGE_BASE_GUIDE.md`** - Guía completa de Knowledge Base
- **`PANELIN_QUICK_REFERENCE.md`** - Referencia rápida
- **`PANELIN_FILES_CHECKLIST.md`** - Checklist de archivos
- **`Checklist_Verificacion_GPT_Configurado.md`** - Checklist de verificación

---

**¡Listo!** Tu GPT "Panelin" debería estar funcionando con toda la arquitectura ideal.

**¿Problemas?** Revisa la sección "Verificación y Ajustes" o consulta los archivos de referencia.

---

**Última actualización**: 2026-01-20  
**Versión**: 2.0 Ultimate
