# Panelin - Guía Completa de Todos los Archivos Útiles
**Versión:** 1.0  
**Fecha:** 2026-01-20

---

## 📋 ÍNDICE

1. [Archivos de Instrucciones](#archivos-de-instrucciones)
2. [Archivos de Knowledge Base (Obligatorios)](#archivos-de-knowledge-base-obligatorios)
3. [Archivos de Knowledge Base (Referencias)](#archivos-de-knowledge-base-referencias)
4. [Guías y Documentación](#guías-y-documentación)
5. [Archivos de Datos](#archivos-de-datos)
6. [Scripts y Utilidades](#scripts-y-utilidades)

---

## 📝 ARCHIVOS DE INSTRUCCIONES

### ⭐ **PANELIN_INSTRUCTIONS_FINAL.txt** (RECOMENDADO)
**Ubicación**: Raíz del proyecto  
**Propósito**: Instrucciones optimizadas con referencias a KB  
**Caracteres**: 5,394 (dentro del límite de 8,000)  
**Cuándo usar**: Para copiar y pegar en el campo "Instructions" del GPT Builder  
**Ventajas**: 
- Usa referencias a archivos KB (más corto)
- Fácil de actualizar
- Bien organizado

**Acción**: Copiar TODO el contenido y pegar en GPT Builder → Configure → Instructions

---

### PANELIN_INSTRUCTIONS_COPY_PASTE.txt
**Ubicación**: Raíz del proyecto  
**Propósito**: Versión alternativa lista para copiar/pegar  
**Cuándo usar**: Si prefieres esta versión sobre FINAL.txt

---

### PANELIN_INSTRUCTIONS_REFERENCE_BASED.md
**Ubicación**: Raíz del proyecto  
**Propósito**: Versión con referencias (formato Markdown)  
**Cuándo usar**: Para referencia o si prefieres formato MD

---

### PANELIN_INSTRUCTIONS_OPTIMIZED.md
**Ubicación**: Raíz del proyecto  
**Propósito**: Versión optimizada sin referencias (todo en instrucciones)  
**Caracteres**: 6,863  
**Cuándo usar**: Si prefieres tener todo en las instrucciones sin referencias

---

### PANELIN_ULTIMATE_INSTRUCTIONS.md
**Ubicación**: Raíz del proyecto  
**Propósito**: Versión completa y detallada (más larga)  
**Cuándo usar**: Para referencia completa, pero puede exceder límite

---

## 🗂️ ARCHIVOS DE KNOWLEDGE BASE (OBLIGATORIOS)

### ⭐ **BMC_Base_Conocimiento_GPT-2.json** (CRÍTICO - PRIMARIO)
**Ubicación**: Raíz del proyecto  
**Nivel**: 1 - MASTER  
**Prioridad**: MÁXIMA - Subir PRIMERO  
**Propósito**: Fuente de verdad absoluta para precios, fórmulas y especificaciones  
**Contenido**:
- Productos completos (ISODEC, ISOPANEL, ISOROOF, ISOWALL, HM_RUBBER)
- Precios validados de Shopify
- Fórmulas de cotización exactas (`formulas_cotizacion`)
- Fórmulas de ahorro energético (`formulas_ahorro_energetico`)
- Especificaciones técnicas (autoportancia, coeficientes térmicos, resistencia térmica)
- Reglas de negocio (`reglas_negocio`)
- Datos de referencia Uruguay (`datos_referencia_uruguay`)

**Acción**: Subir PRIMERO en Knowledge Base del GPT Builder

---

### BMC_Base_Conocimiento_GPT.json (Opcional - Fallback)
**Ubicación**: Raíz del proyecto (si existe)  
**Nivel**: 1 - MASTER (fallback)  
**Prioridad**: Alta (si GPT-2 no está disponible)  
**Propósito**: Versión alternativa del archivo master

---

## 📚 ARCHIVOS DE KNOWLEDGE BASE (REFERENCIAS)

### ⭐ **PANELIN_KNOWLEDGE_BASE_GUIDE.md** (RECOMENDADO)
**Ubicación**: Raíz del proyecto  
**Nivel**: 4 - SOPORTE  
**Prioridad**: Alta  
**Propósito**: Guía completa de jerarquía de archivos y cómo usarlos  
**Contenido**:
- Estructura de Knowledge Base
- Jerarquía de archivos (4 niveles)
- Cómo usar cada archivo
- Reglas críticas
- Proceso de actualización
- Troubleshooting

**Acción**: Subir a Knowledge Base para que Panelin pueda consultarlo

---

### ⭐ **PANELIN_QUOTATION_PROCESS.md** (RECOMENDADO)
**Ubicación**: Raíz del proyecto  
**Nivel**: 4 - SOPORTE  
**Prioridad**: Alta  
**Propósito**: Proceso completo de cotización (5 fases detalladas)  
**Contenido**:
- FASE 1: Identificación
- FASE 2: Validación Técnica (Autoportancia)
- FASE 3: Recuperación de Datos
- FASE 4: Cálculos (Fórmulas Exactas)
- FASE 5: Presentación
- Reglas especiales
- Ejemplos

**Acción**: Subir a Knowledge Base (referenciado en instrucciones)

---

### ⭐ **PANELIN_TRAINING_GUIDE.md** (RECOMENDADO)
**Ubicación**: Raíz del proyecto  
**Nivel**: 4 - SOPORTE  
**Prioridad**: Alta  
**Propósito**: Guía completa de evaluación y entrenamiento  
**Contenido**:
- Evaluación de personal de ventas
- Proporcionar feedback
- Simular escenarios
- Entrenamiento basado en prácticas
- Métricas de evaluación

**Acción**: Subir a Knowledge Base (referenciado en instrucciones)

---

### panelin_context_consolidacion_sin_backend.md
**Ubicación**: Raíz del proyecto  
**Nivel**: 4 - SOPORTE  
**Prioridad**: Alta  
**Propósito**: SOP completo de consolidación, checkpoints y gestión de contexto  
**Contenido**:
- Comandos SOP (`/estado`, `/checkpoint`, `/consolidar`)
- Estructura del Ledger incremental
- Gestión de riesgo de contexto
- Formatos de exportación

**Acción**: Subir a Knowledge Base

---

### BMC_Base_Unificada_v4.json
**Ubicación**: `Files /BMC_Base_Unificada_v4.json`  
**Nivel**: 2 - VALIDACIÓN  
**Prioridad**: Alta  
**Propósito**: Validación cruzada y detección de inconsistencias  
**Contenido**: Productos validados contra 31 presupuestos reales

**Acción**: Subir a Knowledge Base (solo para cross-reference)

---

### panelin_truth_bmcuruguay_web_only_v2.json
**Ubicación**: Raíz del proyecto  
**Nivel**: 3 - DINÁMICO  
**Prioridad**: Alta  
**Propósito**: Verificación de precios actualizados y estado de stock  
**Contenido**: Snapshot público de la web, precios actualizados

**Acción**: Subir a Knowledge Base

---

### Aleros.rtf o Aleros -2.rtf
**Ubicación**: `Files /Aleros -2.rtf`  
**Nivel**: 4 - SOPORTE  
**Prioridad**: Media  
**Propósito**: Reglas técnicas específicas de voladizos y aleros  
**Nota**: Si OpenAI no acepta .rtf, convertir a .txt o .md primero

**Acción**: Subir a Knowledge Base (o convertir antes)

---

### panelin_truth_bmcuruguay_catalog_v2_index.csv
**Ubicación**: `Files /panelin_truth_bmcuruguay_catalog_v2_index.csv`  
**Nivel**: 4 - SOPORTE  
**Prioridad**: Media  
**Propósito**: Índice de productos para búsquedas rápidas  
**Contenido**: Claves de productos, URLs Shopify, estado de stock

**Acción**: Subir a Knowledge Base (accesible via Code Interpreter)

---

## 📖 GUÍAS Y DOCUMENTACIÓN

### ⭐ **PANELIN_SETUP_COMPLETE.md** (RECOMENDADO)
**Propósito**: Guía paso a paso completa para configurar Panelin desde cero  
**Cuándo usar**: Primera vez que configuras Panelin  
**Contenido**:
- Requisitos previos
- Acceso al GPT Builder
- Configuración básica
- Instrucciones del sistema
- Subida de archivos de KB
- Configuración de modelo
- Habilitación de capacidades
- Tests de verificación
- Troubleshooting

**Acción**: Seguir paso a paso para configurar Panelin

---

### ⭐ **PANELIN_QUICK_IMPLEMENTATION.md** (RECOMENDADO)
**Propósito**: Guía rápida de implementación (5 minutos)  
**Cuándo usar**: Cuando ya sabes cómo funciona y solo necesitas recordar pasos  
**Contenido**: Pasos esenciales resumidos

**Acción**: Consultar para implementación rápida

---

### ⭐ **PANELIN_QUICK_REFERENCE.md** (RECOMENDADO)
**Propósito**: Referencia rápida para uso diario  
**Cuándo usar**: Consulta rápida durante uso diario  
**Contenido**:
- Inicio rápido
- Jerarquía de archivos (resumen)
- Reglas críticas
- Proceso de cotización (5 fases)
- Fórmulas clave
- Comandos SOP
- Reglas de negocio
- Guardrails
- Tests rápidos
- Troubleshooting rápido

**Acción**: Mantener a mano para consulta rápida

---

### ⭐ **PANELIN_MASTER_INDEX.md** (RECOMENDADO)
**Propósito**: Índice maestro de toda la documentación  
**Cuándo usar**: Para navegar toda la documentación  
**Contenido**: Índice completo con enlaces a todos los documentos

**Acción**: Usar como punto de entrada a toda la documentación

---

### PANELIN_FILES_CHECKLIST.md
**Propósito**: Checklist de todos los archivos necesarios  
**Cuándo usar**: Para verificar que tienes todos los archivos  
**Contenido**: Lista completa con checkboxes

**Acción**: Usar para verificar antes de configurar

---

### PANELIN_REFERENCE_STRATEGY.md
**Propósito**: Explicación de la estrategia de referencias a KB  
**Cuándo usar**: Para entender por qué usamos referencias  
**Contenido**: Ventajas, implementación, mejores prácticas

**Acción**: Consultar para entender la estrategia

---

## 💾 ARCHIVOS DE DATOS

### BMC_Catalogo_Completo_Shopify (1).json
**Ubicación**: Raíz del proyecto  
**Propósito**: Catálogo completo de Shopify  
**Prioridad**: Opcional  
**Cuándo usar**: Si necesitas referencia adicional de productos

---

## 🛠️ SCRIPTS Y UTILIDADES

### setup_panelin_with_model.py
**Propósito**: Script para configurar Panelin via API  
**Cuándo usar**: Si prefieres configurar via API en lugar de GPT Builder  
**Requisitos**: API key de OpenAI

---

### verify_gpt_configuration.py
**Propósito**: Script para verificar configuración del GPT  
**Cuándo usar**: Para validar que todo está configurado correctamente

---

## 📊 RESUMEN DE ARCHIVOS ESENCIALES

### Para Configurar Panelin (Mínimo):

1. **Instrucciones**: `PANELIN_INSTRUCTIONS_FINAL.txt`
2. **KB Master**: `BMC_Base_Conocimiento_GPT-2.json` ⭐
3. **KB Referencias**: 
   - `PANELIN_KNOWLEDGE_BASE_GUIDE.md`
   - `PANELIN_QUOTATION_PROCESS.md`
   - `PANELIN_TRAINING_GUIDE.md`
   - `panelin_context_consolidacion_sin_backend.md`

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
- `PANELIN_SETUP_COMPLETE.md`
- `PANELIN_QUICK_IMPLEMENTATION.md`
- `PANELIN_QUICK_REFERENCE.md`
- `PANELIN_MASTER_INDEX.md`

---

## 🎯 ORDEN DE PRIORIDAD PARA SUBIR A KB

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

## ✅ CHECKLIST RÁPIDO

### Antes de Configurar:
- [ ] Tener `PANELIN_INSTRUCTIONS_FINAL.txt` listo
- [ ] Tener `BMC_Base_Conocimiento_GPT-2.json` disponible
- [ ] Tener archivos de referencia MD listos
- [ ] Leer `PANELIN_SETUP_COMPLETE.md` o `PANELIN_QUICK_IMPLEMENTATION.md`

### Durante Configuración:
- [ ] Copiar instrucciones de `PANELIN_INSTRUCTIONS_FINAL.txt`
- [ ] Subir `BMC_Base_Conocimiento_GPT-2.json` PRIMERO
- [ ] Subir archivos de referencia MD
- [ ] Subir archivos de validación y dinámicos
- [ ] Configurar modelo (GPT-4 o GPT-4 Turbo)
- [ ] Habilitar Code Interpreter y Web Search

### Después de Configurar:
- [ ] Probar con pregunta simple: "¿Cuánto cuesta ISODEC 100mm?"
- [ ] Verificar que lee de `BMC_Base_Conocimiento_GPT-2.json`
- [ ] Probar personalización (preguntar nombre)
- [ ] Probar cotización completa
- [ ] Verificar comandos SOP (`/estado`)

---

## 📝 NOTAS IMPORTANTES

1. **Siempre subir `BMC_Base_Conocimiento_GPT-2.json` PRIMERO** - Es la fuente de verdad
2. **Los archivos MD de referencia deben estar en KB** - Las instrucciones los referencian
3. **Verificar nombres exactos** - Los nombres en instrucciones deben coincidir con archivos
4. **Si un archivo no se sube** - Verificar formato (.rtf puede necesitar conversión)
5. **Después de subir archivos** - Esperar unos minutos para reindexación

---

**Última actualización**: 2026-01-20  
**Versión**: 1.0
