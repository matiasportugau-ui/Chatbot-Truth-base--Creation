# 🔧 Configuración de MongoDB para Agente de Ingestion

## 📋 Descripción

El agente de ingestion ahora soporta extracción de datos directamente desde MongoDB.

## 🚀 Configuración Rápida

### 1. Instalar Dependencias

```bash
pip install pymongo>=4.0.0
```

O actualizar requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Agregar a tu archivo `.env`:

```bash
# MongoDB Connection String
MONGODB_CONNECTION_STRING=mongodb://usuario:password@host:puerto/database?authSource=admin

# MongoDB Database Name (opcional, default: panelin)
MONGODB_DATABASE_NAME=panelin
```

### Ejemplos de Connection Strings

#### MongoDB Local
```bash
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/panelin
```

#### MongoDB Atlas (Cloud)
```bash
MONGODB_CONNECTION_STRING=mongodb+srv://usuario:password@cluster.mongodb.net/panelin?retryWrites=true&w=majority
```

#### MongoDB con Autenticación
```bash
MONGODB_CONNECTION_STRING=mongodb://usuario:password@host:27017/panelin?authSource=admin
```

## 📊 Colecciones Soportadas

El agente busca automáticamente en las siguientes colecciones:

### Cotizaciones
- `quotes`
- `cotizaciones`
- `quotations`
- `presupuestos`

### Conversaciones
- `conversations`
- `conversaciones`
- `chats`
- `messages`
- `interactions`
- `interacciones`

### Redes Sociales
- `facebook_interactions`
- `instagram_interactions`
- `mercadolibre_interactions`
- `social_media`
- `redes_sociales`

## 📝 Formato de Datos Esperado

### Cotizaciones

```json
{
  "_id": "ObjectId(...)",
  "timestamp": "2025-01-20T10:00:00",
  "query": "Cotiza ISODEC 100mm, 10m x 5m",
  "response": "El precio es...",
  "cliente": "Cliente XYZ",
  "producto": "ISODEC EPS",
  "dimensiones": "10m x 5m"
}
```

### Conversaciones

```json
{
  "_id": "ObjectId(...)",
  "timestamp": "2025-01-20T10:00:00",
  "message": "¿Cuál es el precio?",
  "reply": "El precio es...",
  "user_id": "user_123",
  "session_id": "session_456"
}
```

### Redes Sociales

```json
{
  "_id": "ObjectId(...)",
  "timestamp": "2025-01-20T10:00:00",
  "platform": "facebook",
  "content": "Consulta sobre precio",
  "response": "Respuesta del chatbot",
  "user": {
    "id": "user_123",
    "name": "Usuario"
  }
}
```

## 🔍 Uso

### Uso Automático

El agente detecta automáticamente MongoDB si está configurado:

```bash
python agente_ingestion_analisis.py --modo completo
```

### Verificar Conexión

```python
from gpt_simulation_agent.agent_system.utils.mongodb_client import MongoDBClient

client = MongoDBClient()
if client.db:
    print("✅ Conectado a MongoDB")
    print(f"Colecciones disponibles: {client.list_collections()}")
else:
    print("❌ No conectado. Verificar MONGODB_CONNECTION_STRING")
```

### Extraer Datos Manualmente

```python
from gpt_simulation_agent.agent_system.utils.mongodb_client import MongoDBClient
from datetime import datetime, timedelta

client = MongoDBClient()

# Extraer cotizaciones de los últimos 30 días
since = datetime.now() - timedelta(days=30)
quotes = client.extract_quotes(limit=1000, since=since)

# Extraer conversaciones
conversations = client.extract_conversations(limit=500)

# Extraer redes sociales
social = client.extract_social_media(platform="facebook", limit=200)
```

## 📊 Estadísticas de Colecciones

```python
from gpt_simulation_agent.agent_system.utils.mongodb_client import MongoDBClient

client = MongoDBClient()

# Listar todas las colecciones
collections = client.list_collections()
print(f"Colecciones: {collections}")

# Obtener estadísticas de una colección
stats = client.get_collection_stats("quotes")
print(f"Total documentos: {stats['total_documents']}")
print(f"Documento más antiguo: {stats['oldest_document']}")
print(f"Documento más reciente: {stats['newest_document']}")
```

## 🔧 Personalización

### Especificar Colección Personalizada

```python
from gpt_simulation_agent.agent_system.utils.mongodb_client import MongoDBClient

client = MongoDBClient()

# Extraer de colección personalizada
custom_data = client.extract_from_collection(
    collection_name="mi_coleccion_personalizada",
    query={"status": "active"},
    limit=1000
)
```

### Query Personalizado

```python
# Extraer solo cotizaciones de un cliente específico
quotes = client.extract_from_collection(
    collection_name="quotes",
    query={"cliente": "Cliente XYZ"},
    limit=100
)

# Extraer conversaciones con respuestas
conversations = client.extract_from_collection(
    collection_name="conversations",
    query={"response": {"$exists": True, "$ne": None}},
    limit=500
)
```

## ⚠️ Troubleshooting

### Error: "pymongo not installed"

**Solución**: 
```bash
pip install pymongo>=4.0.0
```

### Error: "MongoDB not connected"

**Solución**: Verificar que `MONGODB_CONNECTION_STRING` esté configurado correctamente en `.env`

### Error: "Authentication failed"

**Solución**: Verificar credenciales y `authSource` en el connection string

### Error: "Collection not found"

**Solución**: El agente intenta múltiples nombres de colección automáticamente. Si ninguna existe, simplemente no extraerá datos de esa fuente.

## 📈 Rendimiento

- **Límite por defecto**: 1000 documentos por colección
- **Filtro por fecha**: Opcional, reduce tiempo de consulta
- **Proyección**: Opcional, reduce transferencia de datos

## 🔒 Seguridad

- Usar variables de entorno para connection strings
- No commitear credenciales en el código
- Usar autenticación en producción
- Considerar usar MongoDB Atlas con IP whitelist

## 📝 Notas

- El agente normaliza automáticamente los documentos de MongoDB al formato unificado
- Los ObjectId se convierten a strings
- Los timestamps se normalizan a formato ISO
- Los campos se mapean automáticamente según el tipo de documento
