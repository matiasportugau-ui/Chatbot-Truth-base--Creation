# 🚀 Setup Completo: Agente de Ingestion y Análisis

## 📋 Checklist de Configuración

### ✅ 1. MongoDB Configuration

#### Crear/Actualizar archivo `.env`

```bash
# MongoDB Connection String
# Formato: mongodb://usuario:password@host:puerto/database?authSource=admin
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/panelin

# O para MongoDB Atlas (Cloud):
# MONGODB_CONNECTION_STRING=mongodb+srv://usuario:password@cluster.mongodb.net/panelin?retryWrites=true&w=majority

# Nombre de la base de datos (opcional, default: panelin)
MONGODB_DATABASE_NAME=panelin
```

#### Verificar conexión

```bash
python3 -c "
from gpt_simulation_agent.agent_system.utils.mongodb_client import MongoDBClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoDBClient()

if client.db:
    print('✅ MongoDB conectado')
    print(f'   Base de datos: {client.database_name}')
    print(f'   Colecciones: {client.list_collections()}')
else:
    print('❌ MongoDB no conectado')
    print('   Verificar MONGODB_CONNECTION_STRING en .env')
"
```

---

### ✅ 2. Facebook API Configuration

#### Agregar a `.env`

```bash
# Facebook API
FACEBOOK_APP_ID=tu_app_id
FACEBOOK_APP_SECRET=tu_app_secret
FACEBOOK_PAGE_ACCESS_TOKEN=tu_page_access_token
FACEBOOK_PAGE_ID=tu_page_id
```

#### Obtener tokens:
1. Ir a [Facebook Developers](https://developers.facebook.com/)
2. Crear una App
3. Agregar "Pages" como producto
4. Generar Page Access Token
5. Obtener Page ID desde la página

---

### ✅ 3. Instagram API Configuration

#### Agregar a `.env`

```bash
# Instagram API
INSTAGRAM_APP_ID=tu_app_id
INSTAGRAM_ACCESS_TOKEN=tu_access_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=tu_business_account_id
```

#### Obtener tokens:
1. Ir a [Facebook Developers](https://developers.facebook.com/)
2. Crear una App con Instagram Basic Display o Instagram Graph API
3. Conectar cuenta de Instagram Business
4. Generar Access Token
5. Obtener Business Account ID

---

### ✅ 4. MercadoLibre API Configuration

#### Agregar a `.env`

```bash
# MercadoLibre API
MERCADOLIBRE_ACCESS_TOKEN=tu_access_token
MERCADOLIBRE_USER_ID=tu_user_id
```

#### Obtener tokens:
1. Ir a [MercadoLibre Developers](https://developers.mercadolibre.com/)
2. Crear una aplicación
3. Obtener Access Token mediante OAuth
4. Obtener User ID desde el perfil

---

### ✅ 5. Verificar Configuración Completa

Ejecutar script de verificación:

```bash
python3 verificar_configuracion.py
```

---

## 📊 Uso del Agente

### Ejecución Completa

```bash
python3 agente_ingestion_analisis.py --modo completo
```

### Modos Individuales

```bash
# Solo ingestion
python3 agente_ingestion_analisis.py --modo ingestion

# Solo análisis de cotizaciones
python3 agente_ingestion_analisis.py --modo cotizaciones

# Solo análisis de redes sociales
python3 agente_ingestion_analisis.py --modo redes

# Solo análisis de respuestas
python3 agente_ingestion_analisis.py --modo respuestas
```

---

## 🔍 Consultar Base de Datos

### Usar SQLite Browser

```bash
# Instalar (macOS)
brew install --cask db-browser-for-sqlite

# Abrir base de datos
open ingestion_database.db
```

### Consultas SQL Útiles

```sql
-- Ver todos los registros
SELECT * FROM ingestion_table ORDER BY timestamp DESC LIMIT 100;

-- Contar por fuente
SELECT source, COUNT(*) as count 
FROM ingestion_table 
GROUP BY source;

-- Ver cotizaciones incompletas
SELECT qa.*, it.user_query
FROM quote_analysis qa
JOIN ingestion_table it ON qa.ingestion_id = it.id
WHERE json_extract(qa.analysis_result, '$.completeness_score') < 0.7;

-- Ver respuestas con baja relevancia
SELECT ra.*, it.user_query, it.chatbot_response
FROM response_analysis ra
JOIN ingestion_table it ON ra.ingestion_id = it.id
WHERE ra.relevance_score < 0.7;

-- Ver consultas de redes sociales que requieren respuesta
SELECT sma.*, it.user_query
FROM social_media_analysis sma
JOIN ingestion_table it ON sma.ingestion_id = it.id
WHERE sma.requires_response = 1;
```

---

## 📈 Revisar Reportes

### Ver reportes generados

```bash
ls -lh ingestion_analysis_output/
```

### Analizar reporte en Python

```python
import json
from pathlib import Path

# Cargar reporte más reciente
report_dir = Path('ingestion_analysis_output')
reports = sorted(report_dir.glob('reporte_completo_*.json'), reverse=True)

if reports:
    with open(reports[0], 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Ver resumen
    print(f"Total registros: {data['ingestion_summary']['total_records']}")
    print(f"Recomendaciones: {len(data['recommendations'])}")
    
    # Ver recomendaciones
    for rec in data['recommendations']:
        print(f"- {rec}")
```

---

## 🔄 Automatización

### Cron Job (Ejecutar diariamente)

```bash
# Agregar a crontab
crontab -e

# Ejecutar cada día a las 2 AM
0 2 * * * cd /ruta/al/proyecto && python3 agente_ingestion_analisis.py --modo completo >> logs/ingestion.log 2>&1
```

### Script de Ejecución Automática

```bash
#!/bin/bash
# ejecutar_ingestion.sh

cd "/Users/matias/Chatbot Truth base  Creation"
python3 agente_ingestion_analisis.py --modo completo

# Enviar notificación si hay errores
if [ $? -ne 0 ]; then
    echo "Error en ingestion" | mail -s "Alerta Ingestion" tu@email.com
fi
```

---

## 🐛 Troubleshooting

### MongoDB no conecta

1. Verificar connection string
2. Verificar que MongoDB esté corriendo
3. Verificar credenciales
4. Probar conexión manualmente

### APIs no funcionan

1. Verificar tokens en `.env`
2. Verificar que los tokens no hayan expirado
3. Verificar permisos de la aplicación
4. Revisar logs de error

### Base de datos bloqueada

1. Cerrar otras conexiones
2. Usar ruta diferente para la base de datos
3. Verificar permisos de archivo

---

## 📝 Notas Importantes

- El archivo `.env` NO debe commitearse (agregar a `.gitignore`)
- Los tokens tienen fecha de expiración, renovar periódicamente
- La base de datos crece con el tiempo, considerar limpieza periódica
- Los reportes se acumulan, considerar archivado periódico

---

## ✅ Estado Actual

- ✅ CSV de cotizaciones: Funcionando
- ✅ Instagram (archivos JSON): Funcionando
- ✅ Facebook (archivos JSON): Funcionando
- ⚠️ MongoDB: Requiere configuración
- ⚠️ APIs reales: Requieren tokens
