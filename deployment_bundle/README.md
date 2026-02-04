# Panelin GPT Deployment Bundle

Este bundle contiene los archivos necesarios para configurar el Custom GPT en ChatGPT y desplegar la API en Google Cloud Run.

## Archivos:
- `openapi.json`: Pegar en la seccin **Actions** del GPT Builder.
- `instructions.md`: Pegar en la seccin **Instructions**.
- `knowledge/`: Subir estos archivos a la seccin **Knowledge**.

## Despliegue en Cloud Run

### Prerrequisitos
1. Cuenta de Google Cloud con facturacin habilitada
2. `gcloud` CLI instalado y autenticado
3. APIs habilitadas: Cloud Run, Cloud Build, Artifact Registry

### Pasos para desplegar

1. **Crear repositorio de Artifact Registry:**
```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1 \
  --description="Panelin API container images"
```

2. **Crear cuenta de servicio:**
```bash
gcloud iam service-accounts create panelin-runner \
  --display-name="Panelin API Runner"
```

3. **Desplegar a Cloud Run:**
```bash
cd "Copia de panelin_agent_v2"
gcloud run deploy panelin-api \
  --source . \
  --region us-central1 \
  --memory 512Mi --cpu 1 \
  --timeout 300 --concurrency 80 \
  --min-instances 0 --max-instances 10 \
  --allow-unauthenticated
```

4. **Obtener URL del servicio:**
```bash
gcloud run services describe panelin-api \
  --region us-central1 \
  --format='value(status.url)'
```

5. **Actualizar OpenAPI schema:**
   - Copiar la URL de Cloud Run
   - Actualizar el campo `servers[0].url` en `openapi.json`

### CI/CD Automtico
El archivo `cloudbuild.yaml` en la raz del repositorio configura Cloud Build para:
- Construir la imagen Docker
- Ejecutar tests
- Desplegar a Cloud Run automticamente en cada push

Para configurar CI/CD:
```bash
gcloud builds triggers create github \
  --repo-name=your-repo \
  --repo-owner=your-org \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

## Configuracin de Action en GPT:
1. Crear una nueva Action en GPT Builder
2. Importar el contenido de `openapi.json`
3. Actualizar la URL del servidor con la URL de Cloud Run
4. En **Authentication**, seleccionar 'None' para acceso pblico

## Endpoints de Salud:
- `GET /health` - Liveness check (200 = alive)
- `GET /ready` - Readiness check (200 = ready, 503 = not ready)

## Verificacin:
Este bundle fue actualizado para soportar despliegue en Google Cloud Run.
La API incluye endpoints de salud para monitoreo y orquestacin de contenedores.
