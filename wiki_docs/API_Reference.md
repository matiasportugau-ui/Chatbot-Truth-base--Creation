# API Reference & SDK

Panelin can be integrated into other applications using its Python SDK.

## Panelin SDK

The project includes a TypeScript SDK example (`panelin_agents_sdk.ts`) and Python modules that act as an SDK.

### Core Functions

#### `calcular_cotizacion(params)`
Located in `motor_cotizacion_panelin.py`.

**Parameters:**
*   `producto` (str): Product name (e.g., "ISODEC").
*   `espesor` (int): Thickness in mm (e.g., 100).
*   `luz` (float): Span in meters.
*   `area` (float): Total area in m2.

**Returns:**
*   JSON object with detailed line items, total price, and validation warnings.

### Function Calling Definitions

When configuring an AI agent (OpenAI/Claude), use the following schema for the quotation tool:

```json
{
  "name": "calcular_cotizacion",
  "description": "Calculates a detailed quote for BMC products.",
  "parameters": {
    "type": "object",
    "properties": {
      "producto": {"type": "string"},
      "espesor": {"type": "integer"},
      "luz": {"type": "number", "description": "Distance between supports in meters"},
      "cantidad": {"type": "number", "description": "Quantity or Area"}
    },
    "required": ["producto", "espesor", "cantidad"]
  }
}
```

## API Server

The `panelin_api_server.py` (if deployed) exposes these functions via REST endpoints.

*   `POST /api/quote`: Accepts JSON body with quote parameters.
*   `POST /api/chat`: Send a message to the agent.
