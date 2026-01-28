# Panelin - Guía Completa de Knowledge Base
**Versión:** 2.0 Ultimate  
**Fecha:** 2026-01-20

**Doc canónico (merge):** `KNOWLEDGE_ANALYSIS_PLAN_MERGED.md` (knowledge + analysis + plan)

---

## 📚 Estructura de Knowledge Base

Esta guía describe todos los archivos que Panelin necesita en su Knowledge Base, su propósito, prioridad y cómo deben usarse.

---

## 🎯 Jerarquía de Archivos (Orden de Prioridad)

### NIVEL 1 - MASTER (Fuente de Verdad Absoluta) ⭐

**Propósito**: Única fuente autorizada para precios, fórmulas y especificaciones técnicas.

#### Archivo:
- **`BMC_Base_Conocimiento_GPT-2.json`** ⭐ (PRIMARIO - OBLIGATORIO)

**Contenido:**
- Productos completos (ISODEC, ISOPANEL, ISOROOF, ISOWALL, HM_RUBBER)
- Precios validados de Shopify
- Fórmulas de cotización exactas
- Especificaciones técnicas (autoportancia, coeficientes térmicos, resistencia térmica)
- Reglas de negocio
- Correcciones técnicas validadas

**Cuándo usar:**
- **SIEMPRE** para precios
- **SIEMPRE** para fórmulas de cálculo
- **SIEMPRE** para especificaciones técnicas
- **SIEMPRE** para validación de autoportancia

**Regla de oro**: Si hay conflicto con otros archivos, este gana.

---

### NIVEL 2 - VALIDACIÓN (Cross-Reference)

**Propósito**: Validación cruzada y detección de inconsistencias.

#### Archivo:
- **`BMC_Base_Unificada_v4.json`**

**Contenido:**
- Productos validados contra 31 presupuestos reales
- Fórmulas validadas
- Precios de referencia
- Notas sobre validación

**Cuándo usar:**
- **SOLO** para cross-reference
- **SOLO** para detectar inconsistencias
- **NO** usar para respuestas directas
- Si detectas diferencia, reportarla pero usar Nivel 1

---

### NIVEL 3 - DINÁMICO (Tiempo Real)

**Propósito**: Verificación de precios actualizados y estado de stock.

#### Archivo:
- **`panelin_truth_bmcuruguay_web_only_v2.json`**

**Contenido:**
- Snapshot público de la web
- Precios actualizados
- Estado de stock
- Catálogo web

**Cuándo usar:**
- Verificar precios actualizados (pero validar contra Nivel 1)
- Consultar estado de stock
- Refresh en tiempo real
- **Siempre verificar contra Nivel 1** antes de usar

---

### NIVEL 4 - SOPORTE (Contexto y Reglas)

**Propósito**: Información complementaria, reglas técnicas y workflows.

#### Archivos:

1. **`panelin_context_consolidacion_sin_backend.md`**
   - **Propósito**: SOP completo de consolidación, checkpoints y gestión de contexto
   - **Contenido**:
     - Comandos: `/estado`, `/checkpoint`, `/consolidar`
     - Estructura del Ledger incremental
     - Gestión de riesgo de contexto
     - Formatos de exportación
     - Reglas operativas consolidadas
   - **Cuándo usar**: Para entender y ejecutar comandos SOP

2. **`Aleros.rtf`** o **`Aleros -2.rtf`**
   - **Propósito**: Reglas técnicas específicas de voladizos y aleros
   - **Contenido**: Cálculos de voladizos, fórmulas de span efectivo
   - **Cuándo usar**: Para consultas sobre aleros y voladizos
   - **Nota**: Si OpenAI no acepta .rtf, convertir a .txt o .md primero

3. **`panelin_truth_bmcuruguay_catalog_v2_index.csv`**
   - **Propósito**: Índice de productos para búsquedas rápidas
   - **Contenido**: Claves de productos, URLs Shopify, estado de stock
   - **Cuándo usar**: Via Code Interpreter para operaciones batch o búsquedas indexadas

---

## 📋 Lista Completa de Archivos Necesarios

### Archivos Obligatorios (Nivel 1):
- [ ] `BMC_Base_Conocimiento_GPT-2.json` ⭐ (PRIMARIO - OBLIGATORIO)

### Archivos Recomendados (Nivel 2):
- [ ] `BMC_Base_Unificada_v4.json`

### Archivos Recomendados (Nivel 3):
- [ ] `panelin_truth_bmcuruguay_web_only_v2.json`

### Archivos de Soporte (Nivel 4):
- [ ] `panelin_context_consolidacion_sin_backend.md`
- [ ] `Aleros.rtf` o `Aleros -2.rtf` (convertir a .txt/.md si es necesario)
- [ ] `panelin_truth_bmcuruguay_catalog_v2_index.csv`

### Archivos Opcionales:
- [ ] `BMC_Catalogo_Completo_Shopify (1).json` (si está disponible)

---

## 🔍 Cómo Usar Cada Archivo

### Para Precios:
1. **PRIMERO**: Consultar `BMC_Base_Conocimiento_GPT-2.json`
2. **SEGUNDO**: Verificar en `panelin_truth_bmcuruguay_web_only_v2.json` si hay actualización
3. **NUNCA**: Usar `BMC_Base_Unificada_v4.json` como fuente primaria

### Para Fórmulas:
1. **SIEMPRE**: Usar fórmulas de `formulas_cotizacion` en `BMC_Base_Conocimiento_GPT-2.json`
2. **NUNCA**: Inventar o modificar fórmulas

### Para Validación Técnica (Autoportancia):
1. **SIEMPRE**: Consultar autoportancia en `BMC_Base_Conocimiento_GPT-2.json`
2. **VALIDAR**: Luz del cliente vs autoportancia del panel
3. **SI NO CUMPLE**: Sugerir espesor mayor o apoyo adicional

### Para Comandos SOP:
1. **CONSULTAR**: `panelin_context_consolidacion_sin_backend.md` para estructura completa
2. **EJECUTAR**: Comandos según especificación en ese archivo

### Para Reglas Técnicas Específicas:
1. **ALEROS**: Consultar `Aleros.rtf` o `Aleros -2.rtf`
2. **WORKFLOWS**: Consultar `panelin_context_consolidacion_sin_backend.md`

---

## ⚠️ Reglas Críticas

### Regla #1: Source of Truth
- **Nivel 1 siempre gana** en caso de conflicto
- **Nunca inventar datos** que no estén en Nivel 1
- **Si no está en Nivel 1**, decir "No tengo esa información"

### Regla #2: Prioridad de Consulta
1. Consultar Nivel 1 primero
2. Si no está, verificar Nivel 2 (pero reportar)
3. Si no está, verificar Nivel 3 (pero validar contra Nivel 1)
4. Si no está, consultar Nivel 4 para contexto
5. Si no está en ningún lado, decir "No tengo esa información"

### Regla #3: Validación Cruzada
- Usar Nivel 2 para detectar inconsistencias
- Reportar diferencias pero usar Nivel 1
- Nunca usar Nivel 2 para respuesta directa

### Regla #4: Actualización
- Nivel 3 puede tener precios más recientes
- Siempre validar contra Nivel 1 antes de usar
- Si hay diferencia, usar Nivel 1 y reportar

---

## 📊 Estructura de Datos Esperada

### En `BMC_Base_Conocimiento_GPT-2.json`:
```json
{
  "meta": {
    "version": "5.0-Unified",
    "fecha": "2026-01-16"
  },
  "products": {
    "ISODEC_EPS": {
      "espesores": {
        "100": {
          "autoportancia": 5.5,
          "precio": 46.07,
          "coeficiente_termico": 0.035,
          "resistencia_termica": 2.86
        }
      }
    }
  },
  "formulas_cotizacion": {
    "calculo_apoyos": "ROUNDUP((LARGO / AUTOPORTANCIA) + 1)",
    "puntos_fijacion_techo": "ROUNDUP(((CANTIDAD * APOYOS) * 2) + (LARGO * 2 / 2.5))"
  },
  "formulas_ahorro_energetico": {
    "diferencia_resistencia_termica": "RESISTENCIA_MAYOR - RESISTENCIA_MENOR"
  }
}
```

---

## 🔄 Proceso de Actualización

Cuando se actualiza un archivo en Knowledge Base:

1. **Eliminar** el archivo antiguo del GPT
2. **Subir** el nuevo archivo
3. **Esperar** unos minutos para reindexación
4. **Probar** que funcione correctamente
5. **Verificar** que Nivel 1 sigue siendo la fuente primaria

---

## ✅ Checklist de Verificación

Antes de considerar la Knowledge Base completa:

- [ ] `BMC_Base_Conocimiento_GPT-2.json` está subido (Nivel 1)
- [ ] `BMC_Base_Unificada_v4.json` está subido (Nivel 2)
- [ ] `panelin_truth_bmcuruguay_web_only_v2.json` está subido (Nivel 3)
- [ ] `panelin_context_consolidacion_sin_backend.md` está subido (Nivel 4)
- [ ] `Aleros.rtf` o equivalente está subido (Nivel 4)
- [ ] Instrucciones del sistema referencian correctamente la jerarquía
- [ ] Panelin lee correctamente Nivel 1 para precios
- [ ] Panelin usa correctamente las fórmulas del JSON
- [ ] Panelin detecta y reporta conflictos correctamente

---

## 🆘 Troubleshooting

### Problema: Panelin no lee el archivo correcto
**Solución**: 
- Verificar que `BMC_Base_Conocimiento_GPT-2.json` esté subido primero
- Reforzar en instrucciones: "SIEMPRE leer BMC_Base_Conocimiento_GPT-2.json primero"

### Problema: Panelin inventa precios
**Solución**:
- Agregar guardrail más estricto en instrucciones
- Verificar que Nivel 1 esté completo
- Probar con consulta simple: "¿Cuánto cuesta ISODEC 100mm?"

### Problema: Fórmulas incorrectas
**Solución**:
- Verificar que use fórmulas de `formulas_cotizacion` del JSON
- Agregar ejemplo en instrucciones
- Probar con caso conocido y comparar resultado

---

**Última actualización**: 2026-01-20  
**Versión**: 2.0 Ultimate
