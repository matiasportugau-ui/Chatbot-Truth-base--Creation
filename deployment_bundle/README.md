# Panelin GPT Deployment Bundle

Este bundle contiene los archivos necesarios para configurar el Custom GPT en ChatGPT.

## Archivos:
- `openapi.json`: Pegar en la sección **Actions** del GPT Builder.
- `instructions.md`: Pegar en la sección **Instructions**.
- `knowledge/`: Subir estos archivos a la sección **Knowledge**.

## Despliegue en Cloud Run

Para desplegar el API en Google Cloud Run:

1. **Requisitos previos**:
   - Cuenta de Google Cloud con billing habilitado
   - gcloud CLI instalado y configurado

2. **Despliegue rápido**:
   ```bash
   gcloud run deploy panelin-api --source . --region us-central1 --allow-unauthenticated
   ```

3. **Obtener URL**:
   ```bash
   gcloud run services describe panelin-api --region=us-central1 --format='value(status.url)'
   ```

4. **Actualizar OpenAPI**: Reemplazar la URL en `openapi.json` con la URL de Cloud Run.

Para instrucciones detalladas, ver `CLOUD_DEPLOYMENT_GUIDE.md` en la raíz del repositorio.

## Configuración de Action:
1. Crear una nueva Action en el GPT Builder.
2. Importar el contenido de `openapi.json`.
3. La URL del servidor ya está configurada para Cloud Run.
4. En **Authentication**, seleccionar 'None' para acceso público.

## Endpoints de Salud:
- `/health` - Verificación de vida del servicio
- `/ready` - Verificación de disponibilidad

## Verificación:
Este bundle fue generado automáticamente después de pasar exitosamente todos los tests de cálculo.
