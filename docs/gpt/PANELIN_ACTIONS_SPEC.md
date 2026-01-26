# Panelin Actions Specification
**Version**: 1.0 (Optional)  
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

**Purpose**: Call the Python quotation engine directly for guaranteed accuracy.

**Endpoint**: `POST https://internal-api.bmc.uy/api/v1/quote`

**Authentication**: API Key (header: `X-API-Key`)

**Request Schema**:
```json
{
  "producto": "ISODEC EPS",
  "espesor": "100",
  "largo": 10.0,
  "ancho": 5.0,
  "luz": 4.5,
  "tipo_fijacion": "hormigon",
  "alero_1": 0,
  "alero_2": 0
}
```

**Response Schema**:
```json
{
  "success": true,
  "cotizacion": {
    "producto": "ISODEC EPS",
    "espesor": "100",
    "validacion": {
      "cumple_autoportancia": true,
      "autoportancia": 5.5,
      "luz_efectiva": 4.5
    },
    "materiales": [...],
    "costos": {
      "subtotal": 1234.56,
      "iva": 271.60,
      "total": 1506.16
    }
  }
}
```

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
      summary: Calculate deterministic quotation
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                producto:
                  type: string
                  enum: ["ISODEC EPS", "ISODEC PIR", "ISOPANEL EPS", "ISOROOF 3G", "ISOWALL PIR"]
                espesor:
                  type: string
                largo:
                  type: number
                ancho:
                  type: number
                luz:
                  type: number
                tipo_fijacion:
                  type: string
                  enum: ["hormigon", "metal", "madera"]
              required: [producto, espesor, largo, ancho, luz, tipo_fijacion]
      responses:
        '200':
          description: Quotation result
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  cotizacion:
                    type: object
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
