# 🤖 Guía: Agente de Ingestion y Análisis Completo

## 📋 Descripción

El **Agente de Ingestion y Análisis Completo** es un sistema integral que:

1. ✅ **Genera tabla de ingestion** para el sistema de chatbot
2. ✅ **Analiza todos los inputs de cotizaciones** desde CSV
3. ✅ **Analiza consultas de MercadoLibre, Instagram y Facebook**
4. ✅ **Analiza y revisa respuestas del chatbot** contra consultas de usuarios
5. ✅ **Genera reportes completos** con recomendaciones

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│         Agente de Ingestion y Análisis                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Quotes     │  │  MercadoLibre│  │  Instagram   │  │
│  │   (CSV)      │  │              │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│  ┌──────┴─────────────────┴──────────────────┴───────┐ │
│  │         Ingestion Table (SQLite)                    │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Quote      │  │   Social     │  │   Response   │  │
│  │   Analysis   │  │   Analysis   │  │   Analysis   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │         Reporte Completo (JSON)                      │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Uso Rápido

### Modo Completo (Recomendado)

```bash
python agente_ingestion_analisis.py --modo completo
```

Esto ejecuta:
- ✅ Ingestion desde todas las fuentes
- ✅ Análisis de cotizaciones
- ✅ Análisis de redes sociales
- ✅ Análisis de respuestas
- ✅ Generación de reporte completo

### Modos Individuales

```bash
# Solo ingestion
python agente_ingestion_analisis.py --modo ingestion

# Solo análisis de cotizaciones
python agente_ingestion_analisis.py --modo cotizaciones

# Solo análisis de redes sociales
python agente_ingestion_analisis.py --modo redes

# Solo análisis de respuestas
python agente_ingestion_analisis.py --modo respuestas
```

## 📊 Estructura de Datos

### Base de Datos SQLite

El agente crea una base de datos SQLite (`ingestion_database.db`) con las siguientes tablas:

#### 1. `ingestion_table`
Tabla principal con todos los registros de ingestion.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | TEXT | ID único del registro |
| `source` | TEXT | Fuente: 'quote', 'mercadolibre', 'instagram', 'facebook' |
| `platform` | TEXT | Plataforma específica |
| `timestamp` | TEXT | Timestamp ISO del registro |
| `user_query` | TEXT | Consulta del usuario |
| `chatbot_response` | TEXT | Respuesta del chatbot (si existe) |
| `metadata` | TEXT | Metadatos JSON |
| `analysis` | TEXT | Análisis JSON |

#### 2. `quote_analysis`
Análisis de cotizaciones.

#### 3. `social_media_analysis`
Análisis de redes sociales.

#### 4. `response_analysis`
Análisis de respuestas del chatbot.

## 📁 Fuentes de Datos

### 1. Cotizaciones (CSV)

**Ubicación**: `/Volumes/My Passport for Mac/2.0 -  Administrador de Cotizaciones  - Admin..csv`

**Formato esperado**:
- Columna `Consulta`: Consulta del cliente
- Columna `Cliente`: Nombre del cliente
- Columna `Producto`: Producto mencionado
- Columna `Dimensiones`: Dimensiones (ej: "10m x 5m")
- Columna `Luz`: Distancia entre apoyos
- Columna `Fijación`: Tipo de fijación

### 2. MercadoLibre

**Ubicación**: `training_data/mercadolibre/*.json`

**Formato esperado**:
```json
[
  {
    "id": "ml_001",
    "timestamp": "2025-01-20T10:00:00",
    "question": "¿Cuál es el precio?",
    "response": "El precio es...",
    "product_id": "MLU123456",
    "user_id": "user_123"
  }
]
```

### 3. Instagram

**Ubicación**: `training_data/social_media/instagram/*.json`

El agente usa el `SocialIngestionEngine` existente para ingestion automática.

### 4. Facebook

**Ubicación**: `training_data/social_media/facebook/*.json`

El agente usa el `SocialIngestionEngine` existente para ingestion automática.

## 🔍 Análisis Realizados

### Análisis de Cotizaciones

- ✅ Detección de producto (ISODEC, ISOPANEL, ISOROOF, etc.)
- ✅ Detección de espesor
- ✅ Detección de dimensiones
- ✅ Detección de luz
- ✅ Detección de tipo de fijación
- ✅ Score de completitud (0-1)
- ✅ Issues detectados
- ✅ Recomendaciones

### Análisis de Redes Sociales

- ✅ Detección de preguntas
- ✅ Detección de necesidad de respuesta
- ✅ Análisis de sentimiento (positive/negative/neutral)
- ✅ Detección de productos mencionados
- ✅ Detección de mención de precios
- ✅ Detección de urgencia
- ✅ Score de engagement (0-1)
- ✅ Extracción de topics

### Análisis de Respuestas

- ✅ **Relevance Score** (0-1): ¿La respuesta es relevante?
- ✅ **Accuracy Score** (0-1): ¿La respuesta es precisa?
- ✅ **Completeness Score** (0-1): ¿La respuesta es completa?
- ✅ **Sentiment Match**: ¿El tono coincide?
- ✅ Issues detectados
- ✅ Recomendaciones

## 📈 Reporte Completo

El reporte completo incluye:

```json
{
  "timestamp": "2025-01-20T10:00:00",
  "ingestion_summary": {
    "total_records": 150,
    "by_source": {
      "quote": 50,
      "mercadolibre": 30,
      "instagram": 40,
      "facebook": 30
    },
    "by_platform": {...},
    "date_range": {...}
  },
  "quote_analysis": {
    "total_quotes": 50,
    "summary": {
      "avg_completeness": 0.75,
      "product_distribution": {...},
      "total_issues": 15
    }
  },
  "social_media_analysis": {
    "total_queries": 100,
    "summary": {
      "question_rate": 0.65,
      "response_rate": 0.70,
      "avg_engagement_score": 0.68
    }
  },
  "response_analysis": {
    "total_responses": 80,
    "summary": {
      "avg_relevance_score": 0.82,
      "avg_accuracy_score": 0.78,
      "avg_completeness_score": 0.75
    }
  },
  "recommendations": [
    "📊 Mejorar completitud de inputs de cotizaciones",
    "💬 Mejorar relevancia de respuestas del chatbot"
  ]
}
```

## 🔧 Configuración

### Variables de Entorno

```bash
# MercadoLibre (opcional)
export MERCADOLIBRE_ACCESS_TOKEN="tu_token"
export MERCADOLIBRE_USER_ID="tu_user_id"

# Facebook (opcional, para ingestion automática)
export FACEBOOK_APP_ID="tu_app_id"
export FACEBOOK_APP_SECRET="tu_app_secret"
export FACEBOOK_PAGE_ACCESS_TOKEN="tu_token"
export FACEBOOK_PAGE_ID="tu_page_id"

# Instagram (opcional, para ingestion automática)
export INSTAGRAM_APP_ID="tu_app_id"
export INSTAGRAM_ACCESS_TOKEN="tu_token"
export INSTAGRAM_BUSINESS_ACCOUNT_ID="tu_account_id"
```

### Personalizar Rutas

Edita el archivo `agente_ingestion_analisis.py`:

```python
# Cambiar ruta del CSV
self.csv_inputs = "/tu/ruta/al/csv.csv"

# Cambiar directorio de training data
self.training_data_dir = Path("tu/directorio")

# Cambiar ruta de base de datos
agente = AgenteIngestionAnalisis(db_path="mi_base_datos.db")
```

## 📊 Consultas SQL Útiles

### Ver todos los registros

```sql
SELECT * FROM ingestion_table ORDER BY timestamp DESC LIMIT 100;
```

### Contar por fuente

```sql
SELECT source, COUNT(*) as count 
FROM ingestion_table 
GROUP BY source;
```

### Ver cotizaciones incompletas

```sql
SELECT qa.*, it.user_query
FROM quote_analysis qa
JOIN ingestion_table it ON qa.ingestion_id = it.id
WHERE json_extract(qa.analysis_result, '$.completeness_score') < 0.7;
```

### Ver respuestas con baja relevancia

```sql
SELECT ra.*, it.user_query, it.chatbot_response
FROM response_analysis ra
JOIN ingestion_table it ON ra.ingestion_id = it.id
WHERE ra.relevance_score < 0.7;
```

## 🎯 Uso como Función para Agentes de IA

El agente puede ser usado como función en otros agentes de IA:

```python
from agente_ingestion_analisis import (
    generar_analisis_ingestion_completo,
    get_ingestion_analysis_function_schema
)

# Schema para Function Calling
schema = get_ingestion_analysis_function_schema()

# Ejecutar análisis
resultado = generar_analisis_ingestion_completo(
    generar_tabla=True,
    analizar_cotizaciones=True,
    analizar_redes_sociales=True,
    analizar_respuestas=True
)
```

## 🐛 Troubleshooting

### Error: CSV no encontrado

**Solución**: Verificar que el CSV existe en la ruta especificada o cambiar la ruta en el código.

### Error: No se encuentran datos de MercadoLibre

**Solución**: Crear directorio `training_data/mercadolibre/` y agregar archivos JSON con el formato correcto.

### Error: Base de datos bloqueada

**Solución**: Cerrar otras conexiones a la base de datos o usar una ruta diferente.

### Error: SocialIngestionEngine no disponible

**Solución**: El agente funciona sin el engine, pero la ingestion automática de Instagram/Facebook no estará disponible. Los archivos JSON existentes seguirán siendo procesados.

## 📝 Notas

- La base de datos se crea automáticamente en la primera ejecución
- Los reportes se guardan en `ingestion_analysis_output/`
- El agente es compatible con el sistema existente de training data
- Los análisis se guardan tanto en la base de datos como en archivos JSON

## 🔄 Próximos Pasos

1. **Integración con APIs reales**: Conectar con APIs reales de MercadoLibre, Instagram y Facebook
2. **Análisis avanzado**: Agregar análisis de sentimiento con ML, detección de intención, etc.
3. **Dashboard**: Crear dashboard web para visualizar los análisis
4. **Alertas**: Sistema de alertas para issues críticos detectados
5. **Exportación**: Exportar datos a otros formatos (CSV, Excel, etc.)
