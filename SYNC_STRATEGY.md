# Estrategia de Sincronización KB ↔ Shopify

## Arquitectura de Sincronización

La "Fuente de Verdad" para precios e inventario es la tienda Shopify. La Knowledge Base (KB) `panelin_truth_bmcuruguay.json` debe mantenerse sincronizada para que el agente tenga datos frescos.

### Diagrama de Flujo

```
SHOPIFY STORE (Truth)
      │
      ▼
   Webhooks (products/update, inventory_levels/update)
      │
      ▼
SYNC SERVICE (n8n / Python)
      │
      ├── Valida HMAC
      ├── Transforma Schema
      └── Actualiza JSON KB
            │
            ▼
    GIT REPO (panelin_truth_bmcuruguay.json)
```

## Estructura JSON de la KB

El archivo `panelin_truth_bmcuruguay.json` sigue este esquema:

```json
{
  "version": "2.0.0",
  "last_sync": "ISO8601 Timestamp",
  "shopify_store": "bmcuruguay.myshopify.com",
  "products": {
    "SKU_123": {
      "name": "Nombre Producto",
      "price_per_m2": 22.50,
      "currency": "USD",
      "specifications": { ... },
      "calculation_rules": { ... },
      "last_updated": "ISO8601 Timestamp"
    }
  },
  "pricing_rules": { ... }
}
```

## Procedimiento de Reconciliación

Se debe ejecutar un script diario (`scripts/sync_shopify.py` - *por implementar*) que:

1.  Descargue todos los productos de Shopify vía Admin API.
2.  Compare con `panelin_truth_bmcuruguay.json`.
3.  Reporte discrepancias.
4.  Actualice la KB si es seguro (cambios menores) o alerte si hay cambios drásticos.

## Implementación de Webhooks (Recomendado)

Usar n8n o un endpoint simple en Python (FastAPI/Flask) para recibir:

- `products/update`: Actualizar precio, nombre, tags.
- `products/delete`: Marcar como discontinuado en KB.

El agente SIEMPRE lee de `panelin_truth_bmcuruguay.json`.
