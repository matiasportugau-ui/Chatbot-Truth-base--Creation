# Estructura del Bundle de Entrenamiento - Panelin

## 📋 Resumen

Este documento describe la estructura del **bundle único** de entrenamiento para Panelin (BMC Assistant Pro). El bundle contiene tanto las instrucciones del sistema como las conversaciones de entrenamiento en un solo archivo JSON.

---

## 🎯 Decisión de Arquitectura

### ✅ 1 Archivo Bundle (Recomendado)

**Estructura elegida:** Bundle único que contiene:
- `meta`: Metadatos del bundle
- `instructions`: Instrucciones del sistema, personalidad, reglas
- `conversations`: Array de conversaciones de entrenamiento

**Ventajas:**
- ✅ Más simple para fine-tuning (formato estándar)
- ✅ Mantiene instrucciones y datos sincronizados
- ✅ Más fácil de versionar y auditar
- ✅ Compatible con formatos de OpenAI y otros proveedores

---

## 📦 Estructura Completa del Bundle

```json
{
  "meta": {
    "version": "1.0.0",
    "created_at": "2026-01-16T10:00:00Z",
    "training_type": ["classification", "generation", "both"],
    "locale": "es-UY",
    "source": "chatgpt_export|manual_curation|ledger_consolidation",
    "total_conversations": 150,
    "total_messages": 3000
  },
  "instructions": {
    "system_prompt": "...",
    "personality": {
      "name": "Panelin",
      "role": "Experto técnico en cotizaciones...",
      "tone": "Profesional, técnico pero accesible",
      "customization_rules": [...]
    },
    "source_of_truth": {...},
    "business_rules": {...},
    "quotation_process": [...]
  },
  "conversations": [
    {
      "id": "CONV-001",
      "messages": [
        {
          "role": "user",
          "content": "...",
          "timestamp": "2026-01-16T10:00:00Z",
          "metadata": {...},
          "annotations": {
            "intent": "quotation_request",
            "sentiment": "neutral",
            "entities": [...]
          }
        },
        {
          "role": "assistant",
          "content": "...",
          "timestamp": "2026-01-16T10:01:00Z",
          "metadata": {...},
          "annotations": {...}
        }
      ],
      "metadata": {...},
      "quality_scores": {...}
    }
  ],
  "validation_report": {...}
}
```

---

## 📝 Campos Detallados

### 1. `meta` (Metadatos del Bundle)

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `version` | string | ✅ | Versión semántica (ej: "1.0.0") |
| `created_at` | ISO-8601 | ✅ | Timestamp de creación |
| `training_type` | array | ✅ | `["classification"]`, `["generation"]`, o `["both"]` |
| `locale` | string | ✅ | Locale ISO (ej: "es-UY") |
| `source` | string | ❌ | Origen de los datos |
| `total_conversations` | integer | ❌ | Número total de conversaciones |
| `total_messages` | integer | ❌ | Número total de mensajes |

### 2. `instructions` (Instrucciones del Sistema)

#### 2.1 `system_prompt`
- **Tipo:** string (mínimo 100 caracteres)
- **Descripción:** Prompt completo del sistema con todas las instrucciones de Panelin
- **Ejemplo:** Contiene las instrucciones de `Instrucciones_Sistema_Panelin_CopiarPegar.txt`

#### 2.2 `personality`
- **Campos requeridos:**
  - `name`: "Panelin"
  - `role`: Descripción del rol
  - `tone`: Tono de comunicación
- **Opcional:**
  - `customization_rules`: Array con reglas de personalización por usuario (Mauro, Martin, Rami)

#### 2.3 `source_of_truth`
- **Estructura:** Define la jerarquía de fuentes de conocimiento
- **Campos:**
  - `primary`: Archivo fuente de verdad principal
  - `hierarchy`: Array con niveles de fuentes

#### 2.4 `business_rules`
- **Campos:**
  - `currency`: "USD"
  - `iva_rate`: 0.22
  - `minimum_slope`: "7%"

### 3. `conversations` (Array de Conversaciones)

Cada conversación contiene:

#### 3.1 `id`
- **Tipo:** string
- **Formato:** `^[A-Z0-9_-]+$` (ej: "CONV-001", "QUOTE-20260116-001")
- **Requerido:** ✅

#### 3.2 `messages` (Array de Mensajes)

Cada mensaje contiene:

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `role` | string | ✅ | `"user"`, `"assistant"`, o `"system"` |
| `content` | string | ✅ | Contenido del mensaje (mínimo 1 carácter) |
| `timestamp` | ISO-8601 | ❌ | Timestamp del mensaje |
| `metadata` | object | ❌ | Metadatos adicionales |
| `annotations` | object | ❌ | Anotaciones para entrenamiento |

##### 3.2.1 `metadata`
- `message_ref`: Referencia del mensaje (ej: "msg_001_user")
- `source`: Fuente del mensaje (ej: "chatgpt", "whatsapp")
- `user_name`: Nombre del usuario (si aplica)

##### 3.2.2 `annotations` (Para Clasificación y Generación)

**Para Clasificación:**
- `intent`: Intención del mensaje
  - Valores: `"quotation_request"`, `"technical_consultation"`, `"product_inquiry"`, `"price_check"`, `"greeting"`, `"personalization"`, `"sop_command"`, `"correction"`, `"other"`
- `sentiment`: Sentimiento
  - Valores: `"positive"`, `"neutral"`, `"negative"`
- `entities`: Array de entidades extraídas
  - Tipos: `"product"`, `"dimension"`, `"price"`, `"location"`, `"date"`, `"person"`

**Para Generación:**
- `requires_knowledge_base`: boolean
- `knowledge_base_files_used`: Array de archivos consultados

#### 3.3 `metadata` (Metadatos de la Conversación)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `conversation_type` | string | `"quotation"`, `"consultation"`, `"support"`, `"training"`, `"correction"` |
| `user_name` | string | Nombre del usuario |
| `outcome` | string | `"completed"`, `"incomplete"`, `"abandoned"`, `"error"` |
| `quotation_generated` | boolean | Si se generó una cotización |
| `pdf_generated` | boolean | Si se generó un PDF |
| `corrections_made` | integer | Número de correcciones |
| `sop_commands_used` | array | Comandos SOP usados (`["/estado", "/checkpoint", "/consolidar"]`) |

#### 3.4 `quality_scores` (Scores de Calidad)

| Campo | Tipo | Rango | Descripción |
|-------|------|-------|-------------|
| `completeness` | number | 0-1 | Score de completitud |
| `accuracy` | number | 0-1 | Score de precisión |
| `relevance` | number | 0-1 | Score de relevancia |
| `annotated` | boolean | - | Si tiene anotaciones completas |

---

## 🔍 Validación

### Schema JSON Schema

El bundle debe validar contra `training_bundle_schema.json` usando un validador JSON Schema.

### Validaciones Adicionales

1. **Alternancia de Roles:** Los mensajes deben alternar entre `user` y `assistant` (excepto `system`)
2. **IDs Únicos:** Todos los `id` de conversaciones deben ser únicos
3. **Timestamps:** Deben ser ISO-8601 válidos
4. **Anotaciones:** Si `training_type` incluye `"classification"`, se recomienda anotar intención/sentimiento

---

## 🛠️ Herramientas

### 1. Validador JSON (`bundle_validator.py`)

Valida el bundle contra el schema:

```bash
python bundle_validator.py bundle.json
python bundle_validator.py bundle.json --fix-roles
python bundle_validator.py bundle.json --full-report -o report.json
```

### 2. Mapeador de Roles (`role_mapper.py`)

Mapea automáticamente roles (user/assistant):

```bash
python role_mapper.py bundle.json -o bundle_mapped.json
python role_mapper.py bundle.json --report-only
```

### 3. Calculador de KPIs (`kpi_calculator.py`)

Calcula KPIs auditables:

```bash
python kpi_calculator.py bundle.json -o kpis.json
python kpi_calculator.py bundle.json --format human
```

---

## 📊 KPIs Auditables

El calculador de KPIs genera métricas exactas y computables:

### KPIs Básicos
- Total de conversaciones
- Total de mensajes
- Distribución user/assistant
- Promedio de mensajes por conversación

### KPIs de Anotaciones
- Cobertura de anotaciones
- Cobertura de intención
- Cobertura de sentimiento
- Distribución de intenciones
- Distribución de sentimientos

### KPIs de Calidad
- Score promedio de completitud
- Score promedio de precisión
- Score promedio de relevancia
- Errores de alternancia de roles
- Problemas de calidad de datos

### KPIs de Entrenamiento
- Preparación para clasificación
- Preparación para generación
- Conversaciones listas para ambos

### Score General
- Score general (0-100)
- Nivel: `excellent`, `good`, `fair`, `needs_improvement`
- Recomendaciones automáticas

---

## 🎓 Tipos de Entrenamiento

### Clasificación (`"classification"`)
- **Objetivo:** Detectar intención y sentimiento
- **Requiere:** Anotaciones de `intent` y `sentiment` en mensajes
- **Uso:** Clasificar mensajes entrantes del usuario

### Generación (`"generation"`)
- **Objetivo:** Generar respuestas del agente
- **Requiere:** Mensajes `assistant` con contenido de calidad
- **Uso:** Entrenar el modelo para generar respuestas como Panelin

### Ambos (`"both"`)
- **Recomendado:** Entrena tanto clasificación como generación
- **Requiere:** Anotaciones completas + mensajes assistant de calidad

---

## 📋 Checklist de Creación

Antes de usar el bundle para entrenamiento:

- [ ] ✅ Bundle valida contra `training_bundle_schema.json`
- [ ] ✅ Todos los roles están mapeados correctamente (user/assistant)
- [ ] ✅ IDs de conversaciones son únicos
- [ ] ✅ Timestamps son ISO-8601 válidos
- [ ] ✅ Si `training_type` incluye `"classification"`: anotaciones de intención/sentimiento presentes
- [ ] ✅ Si `training_type` incluye `"generation"`: mensajes assistant de calidad presentes
- [ ] ✅ KPIs calculados y score general > 60
- [ ] ✅ Sin errores críticos en validación
- [ ] ✅ Metadatos completos en `meta`

---

## 🔗 Referencias

- **Schema JSON:** `training_bundle_schema.json`
- **Validador:** `bundle_validator.py`
- **Mapeador de Roles:** `role_mapper.py`
- **Calculador de KPIs:** `kpi_calculator.py`
- **Instrucciones del Sistema:** `Instrucciones_Sistema_Panelin_CopiarPegar.txt`

---

## 📝 Ejemplo Mínimo

```json
{
  "meta": {
    "version": "1.0.0",
    "created_at": "2026-01-16T10:00:00Z",
    "training_type": ["both"],
    "locale": "es-UY"
  },
  "instructions": {
    "system_prompt": "Te llamas Panelin, eres el BMC Assistant Pro...",
    "personality": {
      "name": "Panelin",
      "role": "Experto técnico en cotizaciones y sistemas constructivos BMC",
      "tone": "Profesional, técnico pero accesible"
    }
  },
  "conversations": [
    {
      "id": "CONV-001",
      "messages": [
        {
          "role": "user",
          "content": "Hola, necesito cotizar ISODEC 100mm para 5m de luz",
          "annotations": {
            "intent": "quotation_request",
            "sentiment": "neutral"
          }
        },
        {
          "role": "assistant",
          "content": "Hola! Para cotizar ISODEC 100mm necesito algunos datos...",
          "annotations": {
            "requires_knowledge_base": true,
            "knowledge_base_files_used": ["BMC_Base_Conocimiento_GPT.json"]
          }
        }
      ],
      "metadata": {
        "conversation_type": "quotation",
        "quotation_generated": true
      }
    }
  ]
}
```

---

**Última actualización:** 2026-01-16  
**Versión del Schema:** 1.0.0
