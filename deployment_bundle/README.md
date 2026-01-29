# Panelin GPT Deployment Bundle

Este bundle contiene los archivos necesarios para configurar el Custom GPT en ChatGPT.

## Archivos:
- `openapi.json`: Pegar en la sección **Actions** del GPT Builder.
- `instructions.md`: Pegar en la sección **Instructions**.
- `knowledge/`: Subir estos archivos a la sección **Knowledge**.

## Configuración de Action:
1. Crear una nueva Action.
2. Importar el contenido de `openapi.json`.
3. Configurar la URL del servidor (donde despliegues `api.py`).
4. En **Authentication**, seleccionar 'API Key' si has configurado seguridad en tu servidor.

## Verificación:
Este bundle fue generado automáticamente después de pasar exitosamente todos los tests de cálculo.
