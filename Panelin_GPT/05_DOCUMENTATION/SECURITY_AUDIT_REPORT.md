# Informe de Auditoría de Seguridad – Proyecto Panelin

**Fecha:** 30 de enero de 2025  
**Alcance:** Chatbot-Truth-base--Creation (Panelin GPT + panelin agent)  
**Clasificación:** Uso interno

---

## 1. Resumen Ejecutivo

Se realizó una revisión de seguridad sobre el proyecto Panelin (configuración GPT, agente híbrido de cotización, sincronización Shopify y scripts de soporte). Se identificaron **vulnerabilidades críticas** (credenciales en código), **riesgos medios** (webhooks, .gitignore) y buenas prácticas ya aplicadas. Las correcciones críticas ya fueron aplicadas en esta auditoría.

| Severidad | Cantidad | Estado |
|-----------|----------|--------|
| Crítica   | 1 (credenciales en código) | ✅ Corregido |
| Media     | 2 | Documentado / recomendado |
| Baja      | Varias | Recomendaciones |

---

## 2. Hallazgos Críticos (Corregidos)

### 2.1 Credenciales hardcodeadas en código

**Riesgo:** Exposición de API keys de Anthropic y Google en el repositorio. Cualquier persona con acceso al repo o historial de Git podría usar o revender las claves.

**Archivos afectados (corregidos):**
- `test_sistema_completo.py`
- `prueba_sistema.py`
- `probar_pdfs_pequenos.py`
- `probar_ocr_pdfs.py`
- `comparar_cotizaciones_vendedoras.py`
- `analisis_completo.py`

**Acción tomada:** Se eliminaron las cadenas literales de API keys y se reemplazaron por carga desde variables de entorno vía `python-dotenv` (archivo `.env`). Los scripts ahora comprueban que las variables estén definidas y muestran un aviso si no lo están.

**Acción recomendada para ti:**
1. **Rotar de inmediato** las API keys que estuvieron en el código (Anthropic y Google) desde los paneles de cada proveedor.
2. Crear un archivo `.env` en la raíz del proyecto (no se sube a Git) con:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=...
   OPENAI_API_KEY=sk-...
   SHOPIFY_ACCESS_TOKEN=...
   SHOPIFY_WEBHOOK_SECRET=...
   ```
3. Si el repositorio ya fue compartido o pusheado a un remoto, considerar el historial como comprometido y rotar todas las claves que alguna vez estuvieron en él.

---

## 3. Hallazgos de Severidad Media

### 3.1 Verificación de webhooks Shopify

**Ubicación:** `panelin/tools/shopify_sync.py`, función `verify_webhook_signature()`.

**Problema:** Si `SHOPIFY_WEBHOOK_SECRET` no está configurado, la función devuelve `True` (acepta cualquier webhook) para facilitar desarrollo. En producción esto permite que un atacante envíe peticiones falsas al endpoint de webhooks.

**Recomendación:** En entorno de producción, no aceptar webhooks si el secret está vacío. Ejemplo de refuerzo:

```python
if not secret:
    if os.environ.get("PANELIN_ENV") == "production":
        return False  # En producción, rechazar si no hay secret
    logger.warning("SHOPIFY_WEBHOOK_SECRET not set, skipping verification")
    return True
```

Y definir `PANELIN_ENV=production` solo en despliegue real.

### 3.2 Archivo .gitignore con conflictos de merge

**Problema:** El `.gitignore` contenía marcadores de conflicto de Git (`<<<<<<<`, `=======`, `>>>>>>>`) y no incluía `.env`, por lo que había riesgo de subir archivos de entorno por error.

**Acción tomada:** Se reescribió `.gitignore` limpio, incluyendo `.env`, `.env.local`, `**/credentials.json` y patrones estándar de Python/IDE.

---

## 4. Buenas Prácticas Observadas

- **Política de seguridad documentada:** `Panelin_GPT/05_DOCUMENTATION/SECURITY_POLICY.md` define clasificación de datos, acciones prohibidas y respuesta a incidentes.
- **Secrets por entorno:** En `panelin/config/settings.py` las claves (OpenAI, Shopify, LangSmith) se leen de `os.environ.get(...)` sin valores por defecto en código.
- **Verificación HMAC en webhooks:** Uso de `hmac.compare_digest()` para comparación segura contra timing attacks en `shopify_sync.py`.
- **Validación de cotizaciones:** En `quotation_calculator.py` hay validación de dimensiones, cantidad, descuentos y checksum; uso de `Decimal` para cálculos financieros.
- **Datos sensibles en GPT:** La política prohíbe subir costos, márgenes y PII a la Knowledge Base del GPT; solo datos de nivel permitido.

---

## 5. Recomendaciones Adicionales

| Prioridad | Recomendación |
|-----------|----------------|
| Alta | Rotar todas las API keys que hayan estado en el código y no reutilizarlas. |
| Alta | Añadir un `.env.example` (sin valores reales) con la lista de variables necesarias para que nuevos desarrolladores sepan qué configurar. |
| Media | En producción, exigir siempre `SHOPIFY_WEBHOOK_SECRET` para webhooks (ver 3.1). |
| Media | Revisar dependencias con `pip audit` o `safety check` de forma periódica. |
| Baja | Considerar un secret manager (AWS Secrets Manager, HashiCorp Vault, etc.) en despliegue en lugar de solo `.env`. |
| Baja | En CI/CD, usar secretos del pipeline (GitHub Actions secrets, GitLab CI variables) y nunca escribir claves en el código. |

---

## 6. Checklist Post-Auditoría

- [x] Eliminar credenciales hardcodeadas de todos los scripts.
- [x] Unificar y corregir `.gitignore` (incluir `.env` y `credentials.json`).
- [ ] **Tú:** Rotar API keys de Anthropic y Google que estuvieron en el repo.
- [ ] Crear `.env.example` y documentar variables necesarias.
- [ ] En producción, configurar `SHOPIFY_WEBHOOK_SECRET` y (opcional) rechazar webhooks si no está definido.
- [ ] Ejecutar `pip install safety && safety check` o `pip audit` periódicamente.

---

*Este informe complementa la política existente en `SECURITY_POLICY.md`. Para incidentes (filtración de instrucciones, precios incorrectos, datos sensibles), seguir el proceso descrito en esa política.*
