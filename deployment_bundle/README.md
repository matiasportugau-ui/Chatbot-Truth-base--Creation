# Panelin GPT Deployment Bundle

Este bundle contiene los archivos necesarios para configurar el Custom GPT en ChatGPT.

## Archivos:
- `openapi.json`: Schema anterior (paths distintos). Para **Cloud Run** usar `openapi_cloudrun.json`.
- `openapi_cloudrun.json`: Schema que coincide con la API en Cloud Run (usa este en el GPT si el backend está en Cloud Run).
- `instructions.md`: Pegar en la sección **Instructions**.
- `knowledge/`: Subir estos archivos a la sección **Knowledge**.

## Configuración de Action (Cloud Run):
1. Crear una nueva Action.
2. Importar el contenido de **`openapi_cloudrun.json`** (no `openapi.json`).
3. La URL del servidor ya está en el schema: `https://panelin-api-q74zutv7dq-uc.a.run.app`.
4. En **Authentication**, seleccionar **API Key**, header **X-API-Key**, valor = tu WOLF_API_KEY.
5. Ver `GPT_ACTION_CLOUD_RUN.md` si recibes 403 Forbidden (hay que redesplegar con `--allow-unauthenticated`).

## Verificación:
Este bundle fue generado automáticamente después de pasar exitosamente todos los tests de cálculo.
