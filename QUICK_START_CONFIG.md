# ⚡ Quick Start: Configuración Rápida

## 🎯 Pasos Rápidos

### 1. Crear archivo `.env`

```bash
# Crear archivo .env en la raíz del proyecto
touch .env
```

### 2. Agregar configuración mínima

Editar `.env` y agregar (al menos MongoDB si lo usas):

```bash
# MongoDB (mínimo requerido para extracción desde MongoDB)
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/panelin
MONGODB_DATABASE_NAME=panelin

# Facebook (opcional - para APIs reales)
FACEBOOK_APP_ID=
FACEBOOK_PAGE_ACCESS_TOKEN=
FACEBOOK_PAGE_ID=

# Instagram (opcional - para APIs reales)
INSTAGRAM_APP_ID=
INSTAGRAM_ACCESS_TOKEN=
INSTAGRAM_BUSINESS_ACCOUNT_ID=

# MercadoLibre (opcional - para APIs reales)
MERCADOLIBRE_ACCESS_TOKEN=
MERCADOLIBRE_USER_ID=
```

### 3. Verificar configuración

```bash
python3 verificar_configuracion.py
```

### 4. Ejecutar agente

```bash
python3 agente_ingestion_analisis.py --modo completo
```

---

## 📊 Consultar Base de Datos

### Opción 1: SQLite CLI

```bash
sqlite3 ingestion_database.db
```

Luego ejecutar consultas desde `consultas_utiles.sql`

### Opción 2: DB Browser (GUI)

```bash
# macOS
brew install --cask db-browser-for-sqlite
open ingestion_database.db
```

### Opción 3: Python

```python
import sqlite3

conn = sqlite3.connect('ingestion_database.db')
cursor = conn.cursor()

cursor.execute("SELECT source, COUNT(*) FROM ingestion_table GROUP BY source")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

conn.close()
```

---

## 📈 Ver Reportes

```bash
# Ver reportes generados
ls -lh ingestion_analysis_output/

# Ver el más reciente
python3 -c "
import json
from pathlib import Path

reports = sorted(Path('ingestion_analysis_output').glob('reporte_completo_*.json'), reverse=True)
if reports:
    with open(reports[0]) as f:
        data = json.load(f)
    print(f'Total: {data[\"ingestion_summary\"][\"total_records\"]}')
    print(f'Recomendaciones: {len(data[\"recommendations\"])}')
"
```

---

## ✅ Estado Actual

Según la última verificación:

- ✅ **CSV de cotizaciones**: Funcionando
- ✅ **Instagram (JSON)**: Funcionando (1 archivo)
- ✅ **Facebook (JSON)**: Funcionando (1 archivo)
- ✅ **Base de datos**: 21 registros, 72 KB
- ✅ **Reportes**: 2 reportes generados
- ⚠️ **MongoDB**: Requiere `MONGODB_CONNECTION_STRING` en `.env`
- ⚠️ **APIs reales**: Requieren tokens (opcional)

---

## 🔄 Próximos Pasos Recomendados

1. **Configurar MongoDB** (si tienes base de datos MongoDB):
   ```bash
   # Agregar a .env
   MONGODB_CONNECTION_STRING=mongodb://usuario:password@host:puerto/panelin
   ```

2. **Agregar más datos de MercadoLibre**:
   ```bash
   # Crear archivos JSON en:
   training_data/mercadolibre/
   ```

3. **Revisar reportes periódicamente**:
   ```bash
   # Ejecutar diariamente
   python3 agente_ingestion_analisis.py --modo completo
   ```

4. **Consultar base de datos**:
   ```bash
   # Usar consultas_utiles.sql
   sqlite3 ingestion_database.db < consultas_utiles.sql
   ```

---

## 📚 Documentación Completa

- `SETUP_COMPLETO_INGESTION.md` - Guía completa de configuración
- `GUIA_AGENTE_INGESTION_ANALISIS.md` - Guía de uso del agente
- `CONFIGURACION_MONGODB.md` - Configuración específica de MongoDB
- `consultas_utiles.sql` - Consultas SQL predefinidas
