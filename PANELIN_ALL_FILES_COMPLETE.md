# Panelin - Lista Completa de Todos los Archivos
**Versión:** 1.1 Complete  
**Fecha:** 2026-01-21

---

## 📋 ARCHIVOS ESENCIALES PARA CONFIGURAR PANELIN

### ⭐ INSTRUCCIONES DEL SISTEMA (Elegir UNO)

1. **`PANELIN_INSTRUCTIONS_FINAL.txt`** ⭐ RECOMENDADO
   - **Ubicación**: Raíz del proyecto
   - **Caracteres**: 5,523 (dentro del límite de 8,000)
   - **Propósito**: Instrucciones optimizadas con referencias a KB
   - **Uso**: Copiar TODO el contenido y pegar en GPT Builder → Configure → Instructions

2. **`PANELIN_INSTRUCTIONS_COPY_PASTE.txt`**
   - **Ubicación**: Raíz del proyecto
   - **Propósito**: Versión alternativa lista para copiar/pegar

3. **`PANELIN_INSTRUCTIONS_COMPACT.md`**
   - **Ubicación**: Raíz del proyecto
   - **Propósito**: Versión compacta

4. **`PANELIN_INSTRUCTIONS_OPTIMIZED.md`**
   - **Ubicación**: Raíz del proyecto
   - **Caracteres**: 6,863
   - **Propósito**: Versión optimizada sin referencias (todo incluido)

5. **`PANELIN_INSTRUCTIONS_REFERENCE_BASED.md`**
   - **Ubicación**: Raíz del proyecto
   - **Propósito**: Versión con referencias a KB (formato Markdown)

6. **`PANELIN_ULTIMATE_INSTRUCTIONS.md`**
   - **Ubicación**: Raíz del proyecto
   - **Propósito**: Versión completa y detallada (más larga, puede exceder límite)

---

### 📚 KNOWLEDGE BASE - ARCHIVOS OBLIGATORIOS

#### NIVEL 1 - MASTER (Subir PRIMERO) ⭐

1. **`BMC_Base_Conocimiento_GPT-2.json`** ⭐ CRÍTICO
   - **Ubicación**: Raíz del proyecto
   - **Prioridad**: MÁXIMA - DEBE estar PRIMERO
   - **Propósito**: Fuente de verdad absoluta para precios, fórmulas y especificaciones
   - **Contenido**: Productos, precios Shopify, fórmulas, autoportancia, coeficientes térmicos, reglas de negocio

2. **`BMC_Base_Conocimiento_GPT.json`** (Opcional - Fallback)
   - **Ubicación**: Raíz del proyecto (si existe)
   - **Prioridad**: Alta (si GPT-2 no está disponible)

---

#### NIVEL 4 - SOPORTE (Referencias - Subir DESPUÉS del Master)

3. **`PANELIN_KNOWLEDGE_BASE_GUIDE.md`** ⭐
   - **Ubicación**: Raíz del proyecto
   - **Prioridad**: Alta
   - **Propósito**: Guía completa de jerarquía de archivos y cómo usarlos

4. **`PANELIN_QUOTATION_PROCESS.md`** ⭐
   - **Ubicación**: Raíz del proyecto
   - **Prioridad**: Alta
   - **Propósito**: Proceso completo de cotización (5 fases detalladas)

5. **`PANELIN_TRAINING_GUIDE.md`** ⭐
   - **Ubicación**: Raíz del proyecto
   - **Prioridad**: Alta
   - **Propósito**: Guía completa de evaluación y entrenamiento

6. **`panelin_context_consolidacion_sin_backend.md`** ⭐
   - **Ubicación**: Raíz del proyecto
   - **Prioridad**: Alta
   - **Propósito**: SOP completo de comandos (`/estado`, `/checkpoint`, `/consolidar`)

---

### 📚 KNOWLEDGE BASE - ARCHIVOS RECOMENDADOS

#### NIVEL 2 - VALIDACIÓN

7. **`BMC_Base_Unificada_v4.json`**
   - **Ubicación**: `Files/BMC_Base_Unificada_v4.json`
   - **Prioridad**: Alta
   - **Propósito**: Validación cruzada y detección de inconsistencias

---

#### NIVEL 3 - DINÁMICO

8. **`panelin_truth_bmcuruguay_web_only_v2.json`**
   - **Ubicación**: Raíz del proyecto o `Files/panelin_truth_bmcuruguay_web_only_v2.json`
   - **Prioridad**: Alta
   - **Propósito**: Verificación de precios actualizados y estado de stock

---

#### NIVEL 4 - SOPORTE (Adicionales)

9. **`Aleros.rtf` o `Aleros -2.rtf`**
   - **Ubicación**: `Files/Aleros -2.rtf`
   - **Prioridad**: Media
   - **Propósito**: Reglas técnicas específicas de voladizos y aleros
   - **Nota**: Si OpenAI no acepta .rtf, convertir a .txt o .md primero

10. **`panelin_truth_bmcuruguay_catalog_v2_index.csv`**
    - **Ubicación**: `Files/panelin_truth_bmcuruguay_catalog_v2_index.csv`
    - **Prioridad**: Media
    - **Propósito**: Índice de productos para búsquedas rápidas

---

#### NIVEL 5 - INTERNO (Uso Interno - NO para GPT público) 🔒

11. **`BROMYROS_Base_Costos_Precios_2026.json`** 🔒 INTERNO
    - **Ubicación**: Raíz del proyecto (generado por script)
    - **Prioridad**: Solo para agentes internos
    - **Propósito**: Base de conocimiento de costos y precios BROMYROS 2026
    - **Contenido**: 138 productos en 22 categorías, costos de fábrica, precios para empresas/particulares/web
    - **⚠️ IMPORTANTE**: Contiene información sensible de costos y márgenes. NO debe ser compartido con clientes externos
    - **Uso**: Solo para agentes internos que necesiten consultar costos, calcular márgenes, obtener precios diferenciados
    - **Generación**: Ejecutar `python3 create_bromyros_kb.py` desde CSV: `MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv`

12. **`BROMYROS_KB_README.md`** 🔒 INTERNO
    - **Ubicación**: Raíz del proyecto
    - **Prioridad**: Solo para agentes internos
    - **Propósito**: Documentación completa de la base de conocimiento BROMYROS
    - **Contenido**: Estructura de datos, reglas de precios, categorías, uso para agentes internos

13. **`GUIA_BASE_CONOCIMIENTO_COSTOS.md`** 🔒 INTERNO
    - **Ubicación**: Raíz del proyecto
    - **Prioridad**: Solo para agentes internos
    - **Propósito**: Guía para analizar matrices de costos y ventas por proveedor
    - **Contenido**: Scripts disponibles, estructura de datos, procesamiento de múltiples proveedores

---

### 📖 GUÍAS Y DOCUMENTACIÓN

11. **`PANELIN_GPT_CREATION_COMPLETE.md`** ⭐⭐ NUEVO - CONSOLIDADO FINAL
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Guía completa consolidada para crear Panelin como GPT en ChatGPT Builder
    - **Contenido**: Todo lo necesario en un solo archivo (instrucciones, KB, configuración, tests, troubleshooting)
    - **Uso**: Usar este archivo para crear el GPT desde cero

12. **`PANELIN_AGENTS_SDK_COMPLETE.md`** ⭐⭐ NUEVO - CONSOLIDADO FINAL
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Guía completa consolidada para usar OpenAI Agents SDK
    - **Contenido**: Todo lo necesario en un solo archivo (instalación, configuración, tools, integración, testing)
    - **Uso**: Usar este archivo para desarrollo programático con Agents SDK

13. **`PANELIN_FULL_CONFIGURATION.md`** ⭐ RECOMENDADO
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Configuración completa paso a paso desde cero
    - **Contenido**: Todo lo necesario para configurar Panelin

12. **`PANELIN_SETUP_COMPLETE.md`** ⭐
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Guía paso a paso completa para configurar Panelin desde cero

13. **`PANELIN_QUICK_IMPLEMENTATION.md`** ⭐
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Guía rápida de implementación (5 minutos)

14. **`PANELIN_QUICK_REFERENCE.md`** ⭐
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Referencia rápida para uso diario

15. **`PANELIN_MASTER_INDEX.md`** ⭐
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Índice maestro de toda la documentación

16. **`PANELIN_ALL_FILES_GUIDE.md`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Guía de todos los archivos útiles organizados por categoría

17. **`PANELIN_FILES_CHECKLIST.md`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Checklist de todos los archivos necesarios

18. **`PANELIN_REFERENCE_STRATEGY.md`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Explicación de la estrategia de referencias a KB

---

### 📄 ARCHIVOS DE CONFIGURACIÓN ALTERNATIVOS

19. **`Instrucciones_Sistema_Panelin_CopiarPegar.txt`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Versión anterior de instrucciones

20. **`Guia_Crear_GPT_OpenAI_Panelin.md`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Guía para crear GPT en OpenAI

21. **`Arquitectura_Ideal_GPT_Panelin.md`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Arquitectura ideal del GPT Panelin

22. **`Revision_Configuracion_GPT.md`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Revisión de configuración del GPT

23. **`Checklist_Verificacion_GPT_Configurado.md`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Checklist de verificación

---

### 🗂️ ARCHIVOS EN CARPETA `gpt_configs/`

24. **`gpt_configs/Panelin Knowledge Base Assistant_config.json`**
    - **Ubicación**: `gpt_configs/`
    - **Propósito**: Configuración JSON del GPT

25. **`gpt_configs/Panelin_Asistente_Integral_BMC_config.json`**
    - **Ubicación**: `gpt_configs/`
    - **Propósito**: Configuración alternativa del GPT

26. **`gpt_configs/INSTRUCCIONES_PANELIN.txt`**
    - **Ubicación**: `gpt_configs/`
    - **Propósito**: Instrucciones del sistema (versión anterior)

27. **`gpt_configs/INSTRUCCIONES_PANELIN_ACTUALIZADAS.txt`**
    - **Ubicación**: `gpt_configs/`
    - **Propósito**: Instrucciones actualizadas

---

### 🐍 SCRIPTS Y UTILIDADES

28. **`setup_panelin_with_model.py`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Script para configurar Panelin via API
    - **Uso**: `python setup_panelin_with_model.py --model gpt-4 --api-key YOUR_API_KEY`

29. **`verify_gpt_configuration.py`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Script para verificar configuración del GPT

30. **`actualizar_panelin_con_base_conocimiento.py`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Script para actualizar Panelin con base de conocimiento

31. **`agente_cotizacion_panelin.py`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Agente de cotización Panelin

32. **`motor_cotizacion_panelin.py`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Motor de cotización Panelin

33. **`cotizacion_completa_panelin.py`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Script de cotización completa

34. **`ejercicio_cotizacion_panelin.py`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Ejercicio de cotización

35. **`chat_with_panelin.py`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Script para chatear con Panelin

36. **`SETUP_PANELIN_API.md`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Guía de setup via API

37. **`create_bromyros_kb.py`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Script para generar base de conocimiento BROMYROS desde CSV
    - **Uso**: `python3 create_bromyros_kb.py`
    - **Entrada**: `MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv`
    - **Salida**: `BROMYROS_Base_Costos_Precios_2026.json`

38. **`analizar_matriz_costos.py`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Analiza un archivo CSV individual (un proveedor)
    - **Uso**: `python3 analizar_matriz_costos.py`
    - **Salida**: `BMC_Base_Costos_Precios_BROMYROS.json`, `resumen_analisis_costos_BROMYROS.json`

39. **`procesar_multiples_proveedores.py`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Procesa automáticamente todos los archivos CSV de proveedores
    - **Uso**: `python3 procesar_multiples_proveedores.py`
    - **Salida**: `BMC_Base_Costos_Precios_UNIFICADA.json`, `resumen_analisis_costos_UNIFICADO.json`

40. **`parse_costos_ventas.py`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Parser para archivos de costos y ventas

---

### 📊 ARCHIVOS DE DATOS

37. **`BMC_Catalogo_Completo_Shopify (1).json`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Catálogo completo de Shopify
    - **Prioridad**: Opcional

---

### 📝 DOCUMENTACIÓN ADICIONAL

38. **`Guia_Actions_Panelin.md`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Guía de Actions para Panelin

39. **`RESUMEN_EJERCICIO_PANELIN.md`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Resumen de ejercicios con Panelin

40. **`RESUMEN_EJERCICIO_COTIZACION_COMPLETA.md`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Resumen de ejercicio de cotización completa

---

### 🤖 OPENAI AGENTS SDK (TypeScript)

41. **`panelin_agents_sdk.ts`** ⭐
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Implementación de Panelin usando OpenAI Agents SDK
    - **Contenido**: Sistema multi-agente (Classification, Cotización, Evaluación, Información), Tools, Guardrails
    - **Uso**: Para desarrollo de agentes programáticos (no para GPT Builder)

42. **`panelin_agents_sdk_example.ts`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Ejemplos de uso del Agents SDK
    - **Contenido**: Ejemplos de cotización, información, evaluación

43. **`PANELIN_AGENTS_SDK_README.md`** ⭐
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Documentación completa del Agents SDK
    - **Contenido**: Instalación, estructura, uso básico, implementación de tools, integración con backend

44. **`PANELIN_AGENTS_SDK_QUICKSTART.md`** ⭐
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Guía rápida de inicio (5 minutos)
    - **Contenido**: Setup rápido, uso básico, próximos pasos

45. **`PANELIN_AGENTS_SDK_SUMMARY.md`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Resumen ejecutivo del Agents SDK

46. **`package.json`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Configuración npm para Agents SDK
    - **Dependencias**: @openai/agents, zod, openai, @openai/guardrails

47. **`tsconfig.json`**
    - **Ubicación**: Raíz del proyecto
    - **Propósito**: Configuración TypeScript para Agents SDK

---

## 🎯 ARCHIVOS MÍNIMOS PARA CONFIGURAR PANELIN

### Para Configuración Básica (Mínimo):

1. **Instrucciones**: `PANELIN_INSTRUCTIONS_FINAL.txt`
2. **KB Master**: `BMC_Base_Conocimiento_GPT-2.json` ⭐
3. **KB Referencias**: 
   - `PANELIN_KNOWLEDGE_BASE_GUIDE.md`
   - `PANELIN_QUOTATION_PROCESS.md`
   - `PANELIN_TRAINING_GUIDE.md`
   - `panelin_context_consolidacion_sin_backend.md`

**Total**: 5 archivos mínimos

---

### Para Configuración Completa (Recomendado):

**Instrucciones**:
- `PANELIN_INSTRUCTIONS_FINAL.txt` (usar este)

**KB Nivel 1 (Master)**:
- `BMC_Base_Conocimiento_GPT-2.json` ⭐

**KB Nivel 2 (Validación)**:
- `BMC_Base_Unificada_v4.json`

**KB Nivel 3 (Dinámico)**:
- `panelin_truth_bmcuruguay_web_only_v2.json`

**KB Nivel 4 (Soporte)**:
- `PANELIN_KNOWLEDGE_BASE_GUIDE.md`
- `PANELIN_QUOTATION_PROCESS.md`
- `PANELIN_TRAINING_GUIDE.md`
- `panelin_context_consolidacion_sin_backend.md`
- `Aleros.rtf` o `Aleros -2.rtf` (convertir si es necesario)
- `panelin_truth_bmcuruguay_catalog_v2_index.csv`

**Guías de Referencia**:
- `PANELIN_FULL_CONFIGURATION.md` ⭐
- `PANELIN_SETUP_COMPLETE.md`
- `PANELIN_QUICK_IMPLEMENTATION.md`
- `PANELIN_QUICK_REFERENCE.md`
- `PANELIN_MASTER_INDEX.md`

**Total**: 15 archivos recomendados

---

## 📦 ESTRUCTURA DE CARPETAS

```
Chatbot Truth base  Creation /
├── PANELIN_INSTRUCTIONS_FINAL.txt          ⭐ Instrucciones (usar este)
├── BMC_Base_Conocimiento_GPT-2.json        ⭐ KB Master (obligatorio)
├── PANELIN_KNOWLEDGE_BASE_GUIDE.md         ⭐ KB Referencia
├── PANELIN_QUOTATION_PROCESS.md            ⭐ KB Referencia
├── PANELIN_TRAINING_GUIDE.md               ⭐ KB Referencia
├── panelin_context_consolidacion_sin_backend.md ⭐ KB Referencia
├── PANELIN_FULL_CONFIGURATION.md           ⭐ Guía completa
├── PANELIN_SETUP_COMPLETE.md               ⭐ Guía paso a paso
├── PANELIN_QUICK_IMPLEMENTATION.md         ⭐ Guía rápida
├── PANELIN_QUICK_REFERENCE.md              ⭐ Referencia diaria
├── PANELIN_MASTER_INDEX.md                 ⭐ Índice maestro
├── PANELIN_ALL_FILES_GUIDE.md             ⭐ Guía de archivos
├── Files/
│   ├── BMC_Base_Unificada_v4.json         (KB Nivel 2)
│   ├── Aleros -2.rtf                      (KB Nivel 4)
│   └── panelin_truth_bmcuruguay_catalog_v2_index.csv (KB Nivel 4)
├── gpt_configs/
│   ├── Panelin Knowledge Base Assistant_config.json
│   └── INSTRUCCIONES_PANELIN.txt
└── [otros archivos de scripts y utilidades]
```

---

## ✅ CHECKLIST RÁPIDO

### Archivos Esenciales (5 archivos):
- [ ] `PANELIN_INSTRUCTIONS_FINAL.txt` (instrucciones)
- [ ] `BMC_Base_Conocimiento_GPT-2.json` (KB Master)
- [ ] `PANELIN_KNOWLEDGE_BASE_GUIDE.md` (KB Referencia)
- [ ] `PANELIN_QUOTATION_PROCESS.md` (KB Referencia)
- [ ] `PANELIN_TRAINING_GUIDE.md` (KB Referencia)
- [ ] `panelin_context_consolidacion_sin_backend.md` (KB Referencia)

### Archivos Recomendados (9 archivos adicionales):
- [ ] `BMC_Base_Unificada_v4.json` (KB Nivel 2)
- [ ] `panelin_truth_bmcuruguay_web_only_v2.json` (KB Nivel 3)
- [ ] `Aleros.rtf` o equivalente (KB Nivel 4)
- [ ] `panelin_truth_bmcuruguay_catalog_v2_index.csv` (KB Nivel 4)
- [ ] `PANELIN_FULL_CONFIGURATION.md` (guía)
- [ ] `PANELIN_SETUP_COMPLETE.md` (guía)
- [ ] `PANELIN_QUICK_IMPLEMENTATION.md` (guía)
- [ ] `PANELIN_QUICK_REFERENCE.md` (guía)
- [ ] `PANELIN_MASTER_INDEX.md` (índice)

---

## 🚀 ORDEN DE PRIORIDAD PARA SUBIR A KB

1. **PRIMERO**: `BMC_Base_Conocimiento_GPT-2.json` ⭐ (CRÍTICO)
2. **SEGUNDO**: `PANELIN_KNOWLEDGE_BASE_GUIDE.md`
3. **TERCERO**: `PANELIN_QUOTATION_PROCESS.md`
4. **CUARTO**: `PANELIN_TRAINING_GUIDE.md`
5. **QUINTO**: `panelin_context_consolidacion_sin_backend.md`
6. **SEXTO**: `BMC_Base_Unificada_v4.json`
7. **SÉPTIMO**: `panelin_truth_bmcuruguay_web_only_v2.json`
8. **OCTAVO**: `Aleros.rtf` o equivalente
9. **NOVENO**: `panelin_truth_bmcuruguay_catalog_v2_index.csv`

---

## 📋 RESUMEN POR TIPO DE ARCHIVO

### Instrucciones del Sistema: 6 archivos
- `PANELIN_INSTRUCTIONS_FINAL.txt` ⭐ (usar este)
- `PANELIN_INSTRUCTIONS_COPY_PASTE.txt`
- `PANELIN_INSTRUCTIONS_COMPACT.md`
- `PANELIN_INSTRUCTIONS_OPTIMIZED.md`
- `PANELIN_INSTRUCTIONS_REFERENCE_BASED.md`
- `PANELIN_ULTIMATE_INSTRUCTIONS.md`

### Knowledge Base: 13 archivos
- `BMC_Base_Conocimiento_GPT-2.json` ⭐ (obligatorio)
- `BMC_Base_Conocimiento_GPT.json` (opcional)
- `PANELIN_KNOWLEDGE_BASE_GUIDE.md` ⭐
- `PANELIN_QUOTATION_PROCESS.md` ⭐
- `PANELIN_TRAINING_GUIDE.md` ⭐
- `panelin_context_consolidacion_sin_backend.md` ⭐
- `BMC_Base_Unificada_v4.json`
- `panelin_truth_bmcuruguay_web_only_v2.json`
- `Aleros.rtf` o `Aleros -2.rtf`
- `panelin_truth_bmcuruguay_catalog_v2_index.csv`
- `BROMYROS_Base_Costos_Precios_2026.json` 🔒 (interno)
- `BROMYROS_KB_README.md` 🔒 (interno)
- `GUIA_BASE_CONOCIMIENTO_COSTOS.md` 🔒 (interno)

### Guías y Documentación: 8 archivos
- `PANELIN_FULL_CONFIGURATION.md` ⭐
- `PANELIN_SETUP_COMPLETE.md` ⭐
- `PANELIN_QUICK_IMPLEMENTATION.md` ⭐
- `PANELIN_QUICK_REFERENCE.md` ⭐
- `PANELIN_MASTER_INDEX.md` ⭐
- `PANELIN_ALL_FILES_GUIDE.md`
- `PANELIN_FILES_CHECKLIST.md`
- `PANELIN_REFERENCE_STRATEGY.md`

### Scripts y Utilidades: 13 archivos
- `setup_panelin_with_model.py`
- `verify_gpt_configuration.py`
- `actualizar_panelin_con_base_conocimiento.py`
- `agente_cotizacion_panelin.py`
- `motor_cotizacion_panelin.py`
- `cotizacion_completa_panelin.py`
- `ejercicio_cotizacion_panelin.py`
- `chat_with_panelin.py`
- `SETUP_PANELIN_API.md`
- `create_bromyros_kb.py` 🔒 (interno)
- `analizar_matriz_costos.py` 🔒 (interno)
- `procesar_multiples_proveedores.py` 🔒 (interno)
- `parse_costos_ventas.py` 🔒 (interno)

### Configuraciones: 4 archivos
- `gpt_configs/Panelin Knowledge Base Assistant_config.json`
- `gpt_configs/Panelin_Asistente_Integral_BMC_config.json`
- `gpt_configs/INSTRUCCIONES_PANELIN.txt`
- `gpt_configs/INSTRUCCIONES_PANELIN_ACTUALIZADAS.txt`

### OpenAI Agents SDK: 7 archivos
- `panelin_agents_sdk.ts` ⭐
- `panelin_agents_sdk_example.ts`
- `PANELIN_AGENTS_SDK_README.md` ⭐
- `PANELIN_AGENTS_SDK_QUICKSTART.md` ⭐
- `PANELIN_AGENTS_SDK_SUMMARY.md`
- `package.json`
- `tsconfig.json`

---

## 🎯 QUÉ ARCHIVOS USAR

### Para Configurar Panelin por Primera Vez:

1. **Lee primero**: `PANELIN_FULL_CONFIGURATION.md` ⭐
2. **O lee**: `PANELIN_QUICK_IMPLEMENTATION.md` (más rápido)
3. **Copia instrucciones de**: `PANELIN_INSTRUCTIONS_FINAL.txt`
4. **Sube a KB**: Los 5 archivos esenciales en orden de prioridad

### Para Uso Diario:

1. **Consulta**: `PANELIN_QUICK_REFERENCE.md`
2. **Navega**: `PANELIN_MASTER_INDEX.md`

### Para Entender la Estructura:

1. **Lee**: `PANELIN_KNOWLEDGE_BASE_GUIDE.md`
2. **Consulta**: `PANELIN_ALL_FILES_GUIDE.md`

---

## 📝 NOTAS IMPORTANTES

1. **Siempre subir `BMC_Base_Conocimiento_GPT-2.json` PRIMERO** - Es la fuente de verdad
2. **Los archivos MD de referencia deben estar en KB** - Las instrucciones los referencian
3. **Verificar nombres exactos** - Los nombres en instrucciones deben coincidir con archivos
4. **Si un archivo no se sube** - Verificar formato (.rtf puede necesitar conversión)
5. **Después de subir archivos** - Esperar unos minutos para reindexación

---

**Última actualización**: 2026-01-21  
**Versión**: 1.1 Complete  
**Total de archivos listados**: 50+ archivos

---

## 🔒 ARCHIVOS INTERNOS (NO para GPT público)

Los siguientes archivos contienen información sensible de costos y márgenes. **NO deben ser subidos al GPT público**:

- `BROMYROS_Base_Costos_Precios_2026.json` - Costos de fábrica y precios internos
- `BROMYROS_KB_README.md` - Documentación de costos
- `GUIA_BASE_CONOCIMIENTO_COSTOS.md` - Guía de análisis de costos
- Scripts relacionados (`create_bromyros_kb.py`, `analizar_matriz_costos.py`, etc.)

**Uso**: Solo para agentes internos que necesiten consultar costos, calcular márgenes o acceder a información financiera sensible.
