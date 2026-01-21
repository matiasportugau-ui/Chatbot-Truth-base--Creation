# Panelin - Checklist de Archivos
**Versión:** 2.0 Ultimate  
**Fecha:** 2026-01-20

Checklist completo de todos los archivos necesarios para configurar Panelin.

---

## 📋 Archivos de Knowledge Base

### ✅ NIVEL 1 - MASTER (Fuente de Verdad Absoluta) ⭐

#### Obligatorios:
- [ ] **`BMC_Base_Conocimiento_GPT-2.json`** ⭐ **PRIMARIO - OBLIGATORIO**
  - Ubicación: Raíz del proyecto
  - Propósito: Fuente de verdad para precios, fórmulas y especificaciones
  - Prioridad: **MÁXIMA** - Subir PRIMERO
  - Contenido: Productos, precios, fórmulas, autoportancia, coeficientes térmicos

---

### ✅ NIVEL 2 - VALIDACIÓN (Cross-Reference)

#### Recomendados:
- [ ] **`BMC_Base_Unificada_v4.json`**
  - Ubicación: `Files /BMC_Base_Unificada_v4.json`
  - Propósito: Validación cruzada y detección de inconsistencias
  - Prioridad: Alta
  - Contenido: Productos validados contra 31 presupuestos reales

---

### ✅ NIVEL 3 - DINÁMICO (Tiempo Real)

#### Recomendados:
- [ ] **`panelin_truth_bmcuruguay_web_only_v2.json`**
  - Ubicación: `panelin_truth_bmcuruguay_web_only_v2.json` o `Files /panelin_truth_bmcuruguay_web_only_v2.json`
  - Propósito: Verificación de precios actualizados y estado de stock
  - Prioridad: Alta
  - Contenido: Snapshot público de la web, precios actualizados

---

### ✅ NIVEL 4 - SOPORTE (Contexto y Reglas)

#### Recomendados:
- [ ] **`panelin_context_consolidacion_sin_backend.md`**
  - Ubicación: `panelin_context_consolidacion_sin_backend.md`
  - Propósito: SOP completo de consolidación, checkpoints y gestión de contexto
  - Prioridad: Alta
  - Contenido: Comandos SOP, estructura Ledger, gestión de contexto

- [ ] **`Aleros.rtf`** o **`Aleros -2.rtf`**
  - Ubicación: `Files /Aleros -2.rtf`
  - Propósito: Reglas técnicas específicas de voladizos y aleros
  - Prioridad: Media
  - Contenido: Cálculos de voladizos, fórmulas de span efectivo
  - **Nota**: Si OpenAI no acepta .rtf, convertir a .txt o .md primero

- [ ] **`panelin_truth_bmcuruguay_catalog_v2_index.csv`**
  - Ubicación: `Files /panelin_truth_bmcuruguay_catalog_v2_index.csv`
  - Propósito: Índice de productos para búsquedas rápidas
  - Prioridad: Media
  - Contenido: Claves de productos, URLs Shopify, estado de stock
  - **Nota**: Accesible via Code Interpreter

---

### ⚪ OPCIONALES

- [ ] **`BMC_Catalogo_Completo_Shopify (1).json`**
  - Ubicación: `BMC_Catalogo_Completo_Shopify (1).json`
  - Propósito: Catálogo completo de productos con variantes
  - Prioridad: Baja
  - Contenido: 73 productos con variantes, precios de Shopify

---

## 📝 Archivos de Documentación (No subir a KB)

Estos archivos son para referencia, NO se suben al GPT:

- [ ] **`PANELIN_ULTIMATE_INSTRUCTIONS.md`** - Instrucciones completas del sistema
- [ ] **`PANELIN_KNOWLEDGE_BASE_GUIDE.md`** - Guía completa de Knowledge Base
- [ ] **`PANELIN_SETUP_COMPLETE.md`** - Guía de configuración paso a paso
- [ ] **`PANELIN_QUICK_REFERENCE.md`** - Referencia rápida
- [ ] **`PANELIN_FILES_CHECKLIST.md`** - Este archivo (checklist)
- [ ] **`Checklist_Verificacion_GPT_Configurado.md`** - Checklist de verificación
- [ ] **`Guia_Crear_GPT_OpenAI_Panelin.md`** - Guía de creación de GPT
- [ ] **`Arquitectura_Ideal_GPT_Panelin.md`** - Arquitectura de referencia

---

## ✅ Checklist de Verificación

### Antes de Configurar:
- [ ] Todos los archivos de Nivel 1 están disponibles
- [ ] Archivos de Nivel 2-4 están disponibles (o al menos los recomendados)
- [ ] `PANELIN_ULTIMATE_INSTRUCTIONS.md` está listo para copiar

### Durante la Configuración:
- [ ] `BMC_Base_Conocimiento_GPT-2.json` subido PRIMERO
- [ ] Todos los archivos de KB subidos en orden de prioridad
- [ ] Instrucciones del sistema copiadas completamente
- [ ] Web Browsing habilitado
- [ ] Code Interpreter habilitado
- [ ] Modelo configurado (GPT-4 o superior)

### Después de Configurar:
- [ ] Test de personalización funciona
- [ ] Test de source of truth funciona
- [ ] Test de validación técnica funciona
- [ ] Test de cotización completa funciona
- [ ] Test de comandos SOP funciona
- [ ] Test de guardrails funciona (no inventa datos)

---

## 📊 Resumen de Archivos por Prioridad

### Prioridad MÁXIMA (Obligatorios):
1. `BMC_Base_Conocimiento_GPT-2.json` ⭐

### Prioridad ALTA (Recomendados):
2. `BMC_Base_Unificada_v4.json`
3. `panelin_truth_bmcuruguay_web_only_v2.json`
4. `panelin_context_consolidacion_sin_backend.md`

### Prioridad MEDIA (Útiles):
5. `Aleros.rtf` o `Aleros -2.rtf`
6. `panelin_truth_bmcuruguay_catalog_v2_index.csv`

### Prioridad BAJA (Opcionales):
7. `BMC_Catalogo_Completo_Shopify (1).json`
8. `BMC_Base_Conocimiento_GPT.json` (si existe)

---

## 🔍 Verificación de Ubicación

### Archivos en Raíz:
- `BMC_Base_Conocimiento_GPT-2.json`
- `BMC_Base_Conocimiento_GPT.json` (si existe)
- `panelin_truth_bmcuruguay_web_only_v2.json`
- `panelin_context_consolidacion_sin_backend.md`
- `BMC_Catalogo_Completo_Shopify (1).json`

### Archivos en `Files /`:
- `Files /BMC_Base_Unificada_v4.json`
- `Files /Aleros -2.rtf`
- `Files /panelin_truth_bmcuruguay_catalog_v2_index.csv`
- `Files /panelin_truth_bmcuruguay_web_only_v2.json` (puede estar aquí también)

---

## ⚠️ Notas Importantes

1. **Orden de subida**: Subir `BMC_Base_Conocimiento_GPT-2.json` PRIMERO
2. **Formato RTF**: Si OpenAI no acepta .rtf, convertir a .txt o .md
3. **Archivos duplicados**: No subir archivos duplicados (puede confundir al GPT)
4. **Reindexación**: Después de subir archivos, esperar unos minutos para reindexación
5. **Verificación**: Probar que Panelin lee correctamente Nivel 1 antes de continuar

---

## 🆘 Si Faltan Archivos

### Si falta `BMC_Base_Conocimiento_GPT-2.json`:
- **CRÍTICO**: Panelin NO funcionará correctamente
- **Solución**: Este archivo es OBLIGATORIO

### Si faltan archivos de Nivel 2-4:
- Panelin funcionará pero con capacidades limitadas
- Recomendado: Subir al menos los de Prioridad ALTA

### Si falta `panelin_context_consolidacion_sin_backend.md`:
- Los comandos SOP (/estado, /checkpoint, /consolidar) pueden no funcionar correctamente
- Recomendado: Subir este archivo

---

## 📝 Checklist Final

Antes de considerar Panelin "listo para producción":

- [ ] ✅ `BMC_Base_Conocimiento_GPT-2.json` subido y verificado
- [ ] ✅ Al menos 3 archivos de KB subidos (Nivel 1 + 2 archivos más)
- [ ] ✅ Instrucciones del sistema completas
- [ ] ✅ Web Browsing habilitado
- [ ] ✅ Code Interpreter habilitado
- [ ] ✅ Modelo configurado (GPT-4 o superior)
- [ ] ✅ Todos los tests básicos pasan
- [ ] ✅ Source of truth funciona correctamente
- [ ] ✅ Guardrails previenen inventar datos

---

**Última actualización**: 2026-01-20  
**Versión**: 2.0 Ultimate
