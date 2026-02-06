# Panelin Actions Specification
**Version**: 1.1 (Optional)  
**Status**: Not yet implemented  
**Purpose**: Future integration for deterministic backend operations

---

## Overview

Actions are **optional** for the Panelin GPT. The initial setup uses Knowledge + Code Interpreter only.

**When to implement Actions**:
- When you need **live stock/price verification** from an external API
- When you want to **offload deterministic quotation** to a trusted backend
- When you need to **avoid uploading sensitive data** as Knowledge

---

## Proposed Actions

### 1. `calculate_quote` (Deterministic Quotation)

**Purpose**: Call the quotation engine directly for guaranteed accuracy, **returning
valued line items** (panels + accessories + fixings) using BOM rules.

**Dependencies**:
- `accessories_catalog.json` for accessory pricing + units
- `bom_rules.json` for deterministic BOM quantities

**Endpoint**: `POST https://internal-api.bmc.uy/api/v1/quote`

**Authentication**: API Key (header: `X-API-Key`)

**Request Schema**:
```json
{
  "product_id": "ISODEC_EPS_100mm",
  "length_m": 5.0,
  "width_m": 11.0,
  "bom_preset": "techo_isodec",
  "finish": {
    "material": "GP",
    "esp": "0.5",
    "color": "Blanco"
  },
  "correas": {
    "separacion_m": 1.2,
    "tipo": "C"
  },
  "cargas": {
    "nieve_kg_m2": 0,
    "viento_categoria": "C3"
  },
  "iva_incluido": true
}
```

**Response Schema**:
```json
{
  "calculation_verified": true,
  "area_m2": 56.0,
  "panels_needed": 10,
  "autoportancia": {
    "cumple": true,
    "margen_seguridad": "OK"
  },
  "line_items": [
    {
      "sku": "PANEL-ISODEC-EPS-100",
      "name": "ISODEC EPS 100 mm",
      "unidad": "m2",
      "cant": 56.0,
      "precio_unit": 46.07,
      "total": 2579.92
    },
    {
      "sku": "PERF-BABETA-LAT-0.5-GP-B",
      "name": "Babeta lateral 0.5 GP Blanco",
      "unidad": "ml",
      "cant": 10.0,
      "precio_unit": 12.5,
      "total": 125.0
    }
  ],
  "subtotales": {
    "paneles": 2579.92,
    "perfileria": 0.0,
    "fijaciones": 0.0
  },
  "total_final_iva_inc": 2579.92
}
```
*Note: Example values only (not real prices).*

**Safety Rules**:
- Rate limit: 10 requests/minute
- Timeout: 30 seconds
- Error handling: If 500, fallback to asking user to contact BMC directly

---

### 2. `search_kb` (Hybrid Knowledge Retrieval)

**Purpose**: Search the Knowledge Base with hybrid semantic + keyword + structured queries.

**Endpoint**: `POST https://internal-api.bmc.uy/api/v1/kb/search`

**Authentication**: API Key

**Request Schema**:
```json
{
  "query": "precio ISODEC 100mm",
  "level_priority": "1",
  "search_strategy": "hybrid"
}
```

**Response Schema**:
```json
{
  "results": [
    {
      "source_file": "BMC_Base_Conocimiento_GPT-2.json",
      "level": 1,
      "content": "...",
      "metadata": {
        "confidence": 0.95,
        "path": "products.ISODEC_EPS.espesores.100"
      }
    }
  ]
}
```

---

### 3. `verify_stock` (Live Stock Check)

**Purpose**: Check real-time inventory for a product/SKU.

**Endpoint**: `GET https://internal-api.bmc.uy/api/v1/stock/{sku}`

**Authentication**: API Key

**Response Schema**:
```json
{
  "sku": "ISODEC-EPS-100",
  "in_stock": true,
  "quantity_available": 120,
  "lead_time_days": 3,
  "last_updated": "2026-01-25T10:00:00Z"
}
```

---

## OpenAPI Schema (for GPT Builder)

If implementing Actions, create a file `docs/gpt/panelin-actions.openapi.yaml`:

```yaml
openapi: 3.0.0
info:
  title: Panelin Internal API
  version: 1.0.0
servers:
  - url: https://internal-api.bmc.uy/api/v1
paths:
  /quote:
    post:
      operationId: calculate_quote
      summary: Calculate deterministic quotation with valued line items
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                product_id:
                  type: string
                length_m:
                  type: number
                width_m:
                  type: number
                bom_preset:
                  type: string
                finish:
                  type: object
                  properties:
                    material:
                      type: string
                    esp:
                      type: string
                    color:
                      type: string
                correas:
                  type: object
                  properties:
                    separacion_m:
                      type: number
                    tipo:
                      type: string
                cargas:
                  type: object
                  properties:
                    nieve_kg_m2:
                      type: number
                    viento_categoria:
                      type: string
                iva_incluido:
                  type: boolean
              required: [product_id, length_m, width_m, bom_preset]
      responses:
        '200':
          description: Quotation result with line items
          content:
            application/json:
              schema:
                type: object
                properties:
                  calculation_verified:
                    type: boolean
                  area_m2:
                    type: number
                  panels_needed:
                    type: integer
                  autoportancia:
                    type: object
                  line_items:
                    type: array
                    items:
                      type: object
                  subtotales:
                    type: object
                  total_final_iva_inc:
                    type: number
  /kb/search:
    post:
      operationId: search_kb
      summary: Hybrid KB search
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                level_priority:
                  type: string
                  enum: ["1", "2", "3", "4"]
              required: [query]
      responses:
        '200':
          description: Search results
  /stock/{sku}:
    get:
      operationId: verify_stock
      summary: Check real-time stock
      parameters:
        - name: sku
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Stock info
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
security:
  - ApiKeyAuth: []
```

---

## Authentication Setup (in GPT Builder)

When adding an Action in GPT Builder:
1. Click "Create new action"
2. Paste the OpenAPI schema above
3. Choose "API Key" authentication
4. Add header: `X-API-Key` with your internal API key
5. Test each action before saving

---

## Security Notes

- **Do NOT embed API keys in Knowledge Base or Canvas**
- Use GPT Builder's secure authentication flow
- Rate limits should be enforced on the backend
- Actions should only return non-confidential data (no internal costs/margins)
