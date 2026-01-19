# 🛠️ Herramientas de Validación y KPIs - Panelin Training Bundle

## 📦 Componentes Creados

### ✅ 1. Schema JSON Schema
**Archivo:** `training_bundle_schema.json`

Schema completo para validar bundles de entrenamiento. Define la estructura exacta del bundle único (instructions + conversations).

### ✅ 2. Validador JSON
**Archivo:** `bundle_validator.py`

Valida bundles contra el schema JSON Schema. Incluye:
- Validación de estructura
- Validación de schema JSON Schema
- Validación de roles
- Opción de corregir roles automáticamente
- Integración con calculador de KPIs

### ✅ 3. Mapeador de Roles
**Archivo:** `role_mapper.py`

Mapea automáticamente roles (customer vs agent) basado en:
- Patrones de contenido (productos BMC, comandos SOP, etc.)
- Alternancia esperada user/assistant
- Validación de consistencia

### ✅ 4. Calculador de KPIs
**Archivo:** `kpi_calculator.py`

Calcula KPIs auditables y exactos:
- Métricas básicas (conversaciones, mensajes, distribución)
- Métricas de anotaciones (cobertura, distribución)
- Métricas de calidad (completitud, precisión, relevancia)
- Métricas de consistencia (IDs, timestamps)
- Métricas de entrenamiento (preparación para clasificación/generación)
- Score general (0-100) con recomendaciones

### ✅ 5. Documentación
**Archivos:**
- `ESTRUCTURA_BUNDLE_ENTRENAMIENTO.md`: Documentación completa de la estructura
- `README_VALIDACION_ENTRENAMIENTO.md`: Este archivo

---

## 🚀 Uso Rápido

### Paso 1: Validar Bundle

```bash
# Validación básica
python bundle_validator.py mi_bundle.json

# Validación con corrección automática de roles
python bundle_validator.py mi_bundle.json --fix-roles

# Validación completa con KPIs
python bundle_validator.py mi_bundle.json --full-report -o reporte.json
```

### Paso 2: Mapear Roles (si es necesario)

```bash
# Mapear roles y guardar bundle corregido
python role_mapper.py mi_bundle.json -o mi_bundle_mapped.json

# Solo generar reporte (sin modificar)
python role_mapper.py mi_bundle.json --report-only
```

### Paso 3: Calcular KPIs

```bash
# Calcular KPIs y guardar en JSON
python kpi_calculator.py mi_bundle.json -o kpis.json

# Mostrar KPIs en formato humano
python kpi_calculator.py mi_bundle.json --format human
```

---

## 📋 Workflow Completo

### 1. Crear/Preparar Bundle

```bash
# Tu bundle debe tener esta estructura mínima:
{
  "meta": {
    "version": "1.0.0",
    "created_at": "2026-01-16T10:00:00Z",
    "training_type": ["both"],
    "locale": "es-UY"
  },
  "instructions": {
    "system_prompt": "...",
    "personality": {...}
  },
  "conversations": [...]
}
```

### 2. Validar y Corregir

```bash
# Validar estructura y schema
python bundle_validator.py bundle.json

# Si hay errores de roles, corregir automáticamente
python bundle_validator.py bundle.json --fix-roles

# Esto genera: bundle_validated.json
```

### 3. Mapear Roles (si no se hizo en paso 2)

```bash
python role_mapper.py bundle.json -o bundle_mapped.json
```

### 4. Calcular KPIs

```bash
python kpi_calculator.py bundle.json -o kpis.json --format human
```

### 5. Revisar Score y Recomendaciones

El calculador de KPIs genera un score general (0-100) y recomendaciones:

- **80-100:** ✅ Excellent - Listo para entrenamiento
- **60-79:** ✅ Good - Bueno, algunas mejoras menores
- **40-59:** ⚠️ Fair - Necesita mejoras
- **0-39:** ❌ Needs Improvement - Requiere trabajo significativo

---

## 🔍 Ejemplos de Uso

### Ejemplo 1: Validación Rápida

```bash
python bundle_validator.py training_data.json
```

**Salida:**
```
============================================================
REPORTE DE VALIDACIÓN - TRAINING BUNDLE
============================================================

Estado: ✅ VÁLIDO

📊 Resumen:
   - Errores: 0
   - Advertencias: 2
   - Info: 1

🔍 Validaciones:
   - Estructura: ✅
   - Schema JSON: ✅
   - Roles: ✅
```

### Ejemplo 2: Corrección Automática

```bash
python bundle_validator.py bundle.json --fix-roles
```

**Salida:**
```
✅ Bundle con roles corregidos guardado en: bundle_validated.json
✅ Roles mapeados automáticamente

📊 Estadísticas:
   - Total mensajes: 1500
   - User: 750
   - Assistant: 750
   - Correcciones: 12
```

### Ejemplo 3: KPIs Completos

```bash
python kpi_calculator.py bundle.json --format human
```

**Salida:**
```
============================================================
RESUMEN EJECUTIVO - KPIs DE ENTRENAMIENTO
============================================================

📊 Score General: 85.5/100 (excellent)

📈 Métricas Clave:
   - total_conversations: 150
   - total_messages: 3000
   - annotation_coverage: 92.5
   - avg_quality_score: 88.3

💡 Recomendaciones:
   ✅ Bundle en buen estado. Listo para entrenamiento.
```

---

## 📊 KPIs Disponibles

### Básicos
- `total_conversations`: Número total de conversaciones
- `total_messages`: Número total de mensajes
- `user_messages`: Mensajes de usuario
- `assistant_messages`: Mensajes del asistente
- `avg_messages_per_conversation`: Promedio de mensajes por conversación

### Anotaciones
- `annotation_coverage`: Porcentaje de mensajes anotados (0-1)
- `intent_coverage`: Porcentaje con intención anotada
- `sentiment_coverage`: Porcentaje con sentimiento anotado
- `intent_distribution`: Distribución de intenciones
- `sentiment_distribution`: Distribución de sentimientos

### Calidad
- `avg_completeness`: Score promedio de completitud (0-1)
- `avg_accuracy`: Score promedio de precisión (0-1)
- `avg_relevance`: Score promedio de relevancia (0-1)
- `role_alternation_errors`: Errores de alternancia de roles

### Entrenamiento
- `classification_readiness`: Preparación para clasificación (0-1)
- `generation_readiness`: Preparación para generación (0-1)
- `both_ready_conversations`: Conversaciones listas para ambos

### Score General
- `overall_score`: Score general (0-100)
- `level`: Nivel (`excellent`, `good`, `fair`, `needs_improvement`)
- `recommendations`: Array de recomendaciones

---

## ⚙️ Requisitos

### Python 3.7+

### Dependencias

```bash
pip install jsonschema
```

O crear `requirements.txt`:

```
jsonschema>=4.0.0
```

---

## 🐛 Solución de Problemas

### Error: "No se encontraron role_mapper.py o kpi_calculator.py"

**Solución:** Asegúrate de que todos los archivos estén en el mismo directorio:
- `bundle_validator.py`
- `role_mapper.py`
- `kpi_calculator.py`
- `training_bundle_schema.json`

### Error: "Schema validation failed"

**Solución:** 
1. Revisa que el bundle tenga la estructura correcta (ver `ESTRUCTURA_BUNDLE_ENTRENAMIENTO.md`)
2. Valida contra el schema: `python bundle_validator.py bundle.json`

### Error: "Role alternation errors"

**Solución:**
1. Usa `--fix-roles` para corregir automáticamente
2. O usa `role_mapper.py` directamente: `python role_mapper.py bundle.json -o bundle_fixed.json`

### KPIs muestran score bajo

**Revisa:**
1. Cobertura de anotaciones (debe ser > 70% para entrenamiento)
2. Calidad de datos (sin mensajes vacíos, roles correctos)
3. Preparación para entrenamiento (classification/generation readiness)

---

## 📚 Documentación Adicional

- **Estructura del Bundle:** Ver `ESTRUCTURA_BUNDLE_ENTRENAMIENTO.md`
- **Schema JSON:** Ver `training_bundle_schema.json`
- **Instrucciones del Sistema:** Ver `Instrucciones_Sistema_Panelin_CopiarPegar.txt`

---

## ✅ Checklist Pre-Entrenamiento

Antes de usar el bundle para entrenamiento:

- [ ] ✅ Bundle valida contra schema (`bundle_validator.py`)
- [ ] ✅ Roles mapeados correctamente (user/assistant)
- [ ] ✅ KPIs calculados y score > 60
- [ ] ✅ Sin errores críticos
- [ ] ✅ Cobertura de anotaciones > 70% (si training_type incluye "classification")
- [ ] ✅ Mensajes assistant de calidad (si training_type incluye "generation")
- [ ] ✅ IDs únicos en todas las conversaciones
- [ ] ✅ Timestamps válidos (ISO-8601)

---

**Versión:** 1.0.0  
**Fecha:** 2026-01-16
