# Proyecto Cloud: Chatbot BMC Live

**Project ID**: chatbot-bmc-live  
**Project Number**: 642127786762  
**Platform**: Google Cloud Platform (GCP)

---

## Información del Proyecto

### Identificación
- **Nombre**: Chatbot BMC Live
- **ID GCP**: chatbot-bmc-live
- **Número**: 642127786762
- **Región principal**: us-central1

### Servicios Desplegados

#### 1. Cloud Run - Panelin API
**URL**: `https://panelin-api-q74zutv7dq-uc.a.run.app`

**Configuración**:
- **Service Account**: panelin-runner@chatbot-bmc-live.iam.gserviceaccount.com
- **Memoria**: 512 Mi
- **CPU**: 1
- **Timeout**: 300s
- **Concurrency**: 80
- **Min instances**: 0
- **Max instances**: 10
- **Secrets**: WOLF_API_KEY (desde Secret Manager)
- **Auth**: API Key (X-API-Key header)

**Endpoints**:
- `GET /health` - Health check (sin auth)
- `POST /find_products` - Búsqueda de productos
- `POST /product_price` - Consulta de precio
- `POST /calculate_quote` - Generación de cotización

#### 2. Secret Manager
**Secrets almacenados**:
- `WOLF_API_KEY` - API key para autenticación
  - Versión: latest
  - Usado por: Cloud Run service

#### 3. Artifact Registry
**Repositorio**: panelin
- **Tipo**: Docker
- **Ubicación**: us-central1
- **Uso**: Almacena imágenes Docker para Cloud Run

---

## Arquitectura del Sistema

```
GPT Builder (OpenAI)
    ↓ (HTTPS + X-API-Key)
Cloud Run (panelin-api)
    ├─ Autenticación: X-API-Key
    ├─ FastAPI endpoints
    ├─ Lógica cotizaciones
    └─ Consulta KB
        ↓
Secret Manager (WOLF_API_KEY)
```

---

## Comandos Útiles

### Verificar proyecto actual
```bash
gcloud config get-value project
# Debería mostrar: chatbot-bmc-live
```

### Listar servicios Cloud Run
```bash
gcloud run services list --project=chatbot-bmc-live
```

### Ver logs del servicio
```bash
gcloud run services logs read panelin-api --project=chatbot-bmc-live --region=us-central1
```

### Describir servicio
```bash
gcloud run services describe panelin-api --region=us-central1 --project=chatbot-bmc-live
```

### Ver secrets
```bash
gcloud secrets list --project=chatbot-bmc-live
```

### Re-deploy del servicio
```bash
cd /path/to/repo
gcloud run deploy panelin-api \
  --source . \
  --region us-central1 \
  --service-account panelin-runner@chatbot-bmc-live.iam.gserviceaccount.com \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 80 \
  --min-instances 0 \
  --max-instances 10 \
  --set-secrets "WOLF_API_KEY=WOLF_API_KEY:latest" \
  --allow-unauthenticated \
  --project=chatbot-bmc-live
```

---

## Acceso y Permisos

### Service Account
**Email**: panelin-runner@chatbot-bmc-live.iam.gserviceaccount.com

**Roles**:
- Cloud Run Invoker
- Secret Manager Secret Accessor
- Logs Writer

### URLs de Console

**Cloud Run Dashboard**:
https://console.cloud.google.com/run?project=chatbot-bmc-live

**Service específico**:
https://console.cloud.google.com/run/detail/us-central1/panelin-api?project=chatbot-bmc-live

**Metrics**:
https://console.cloud.google.com/run/detail/us-central1/panelin-api/metrics?project=chatbot-bmc-live

**Logs**:
https://console.cloud.google.com/logs/query?project=chatbot-bmc-live

**Secret Manager**:
https://console.cloud.google.com/security/secret-manager?project=chatbot-bmc-live

**Artifact Registry**:
https://console.cloud.google.com/artifacts?project=chatbot-bmc-live

---

## Integración con GPT

### GPT Action Configuration

**OpenAPI Schema**: Usar `openapi_cloudrun.json`

**Authentication**:
- **Type**: API Key
- **Header name**: X-API-Key
- **Value**: [WOLF_API_KEY desde Secret Manager]

**Base URL**: https://panelin-api-q74zutv7dq-uc.a.run.app

### Test de Conexión

Desde GPT Builder Preview:
```
Test /health endpoint
Test /find_products con query "ISODEC"
Test /calculate_quote con quotation simple
```

---

## Monitoreo y Debugging

### Metrics Clave
- **Request count**: Número de requests
- **Request latency**: Tiempo de respuesta (p50, p95, p99)
- **Error rate**: Porcentaje de errores 4xx/5xx
- **CPU utilization**: Uso de CPU
- **Memory utilization**: Uso de memoria
- **Active instances**: Instancias activas

### Logs Importantes

**Buscar errores**:
```bash
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --project=chatbot-bmc-live \
  --limit=50
```

**Ver últimos requests**:
```bash
gcloud logging read "resource.type=cloud_run_revision" \
  --project=chatbot-bmc-live \
  --limit=20 \
  --format=json
```

---

## Costos Estimados

### Cloud Run (pay-per-use)
- **CPU**: $0.00002400 por vCPU-segundo
- **Memoria**: $0.00000250 por GiB-segundo
- **Requests**: $0.40 por millón de requests
- **Min instances = 0**: Sin costo cuando no hay tráfico

### Estimación Mensual
- **100 requests/día**: ~$1-2/mes
- **1000 requests/día**: ~$5-10/mes
- **10000 requests/día**: ~$30-50/mes

### Secret Manager
- **Storage**: $0.06 por secret por mes (1 secret = $0.06/mes)
- **Access**: $0.03 por 10,000 accesos

**Total estimado con tráfico bajo**: ~$2-5/mes

---

## Troubleshooting

### Problema: 403 Forbidden
**Causa**: Service no permite tráfico no autenticado
**Solución**: Re-deploy con `--allow-unauthenticated`

### Problema: API Key inválida
**Causa**: X-API-Key header incorrecto o secret desactualizado
**Solución**: Verificar WOLF_API_KEY en Secret Manager

### Problema: Cold start lento
**Causa**: Min instances = 0
**Solución**: Aumentar `--min-instances` a 1 (aumenta costos)

### Problema: Timeout
**Causa**: Request toma > 300s
**Solución**: Aumentar `--timeout` o optimizar endpoint

---

## Relación con Deployment GPT V3.1/V3.2

### Arquitectura Actual

**GPT Builder (Frontend)**:
- Panelin GPT V3.1 desplegado ✅
- Calculator V3.1 con validación autoportancia ✅
- Instructions condensadas (5,035 chars) ✅

**Cloud Run API (Backend)**:
- Endpoints REST para GPT Actions
- Cotizaciones, búsqueda productos, precios
- Autenticación API Key

### Sincronización Requerida

Si actualizamos calculator a V3.2 (panel dimensions):

**En GPT Builder**:
1. Upload nuevo `quotation_calculator_v3.py` (V3.2)
2. Update instructions para mostrar dimensiones

**En Cloud Run** (opcional):
1. Actualizar API si usa el calculator
2. Re-deploy con nueva versión

**Actualmente**: GPT y Cloud Run pueden funcionar independientemente.

---

## Próximos Pasos

### Corto Plazo
- [ ] Verificar que Cloud Run esté usando V3.1 del calculator
- [ ] Sincronizar versión GPT con Cloud Run
- [ ] Documentar API endpoints actualizados

### V3.2 Deployment
Si implementamos panel dimensions:
1. [ ] Actualizar calculator local → V3.2
2. [ ] Test local
3. [ ] Deploy a GPT Builder
4. [ ] (Opcional) Deploy a Cloud Run si aplica
5. [ ] Verificar sincronización

---

**Documentado**: 2026-02-07  
**Proyecto**: chatbot-bmc-live (642127786762)  
**Estado**: Cloud Run activo, GPT V3.1 desplegado  
**Próximo**: V3.2 (panel dimensions) en plan
