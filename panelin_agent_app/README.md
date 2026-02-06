# Panelin Agent V2 - Arquitectura Óptima para Cotizaciones E-commerce

Sistema de cotización de paneles aislantes para BMC Uruguay con **precisión 100%** mediante arquitectura híbrida: LLM para comprensión de lenguaje natural + Python/Decimal para toda la aritmética.

## Principio Fundamental

```
┌─────────────────────────────────────────────────────────────────┐
│                    PANELIN QUOTATION AGENT V2                    │
│                                                                  │
│  LLM NUNCA CALCULA → Solo extrae parámetros                     │
│  PYTHON SIEMPRE CALCULA → Decimal para precisión financiera     │
│                                                                  │
│  calculation_verified: true  ← Garantiza cálculo por código     │
└─────────────────────────────────────────────────────────────────┘
```

## Instalación

```bash
# Core (sin dependencias externas)
cd panelin_agent_v2
pip install pytest

# Con agente LangGraph
pip install -r requirements.txt
```

## Uso Rápido

### Cálculo de Cotización (sin API key)

```python
from panelin_agent_v2 import calculate_panel_quote, find_product_by_query

# Buscar producto
products = find_product_by_query("isopanel 100mm para pared")
print(f"Encontrado: {products[0]['name']} - ${products[0]['price_per_m2']}/m²")

# Calcular cotización (100% determinista)
quote = calculate_panel_quote(
    product_id=products[0]["product_id"],
    length_m=6.0,
    width_m=4.0,
    quantity=1,
    include_tax=True
)

print(f"Área: {quote['area_m2']} m²")
print(f"Paneles: {quote['panels_needed']}")
print(f"Subtotal: ${quote['subtotal_usd']:.2f}")
print(f"IVA (22%): ${quote['tax_amount_usd']:.2f}")
print(f"TOTAL: ${quote['total_usd']:.2f}")

# CRÍTICO: Verificar que el cálculo fue por Python, no LLM
assert quote["calculation_verified"] == True
assert quote["calculation_method"] == "python_decimal_deterministic"
```

### Agente Completo (requiere API key)

```python
from panelin_agent_v2 import create_agent
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

agent = create_agent(model_name="gpt-4o-mini")
result = agent.invoke("Necesito cotizar isopanel de 100mm para un techo de 6x4 metros")

print(result["response"])
```

## Arquitectura

```
panelin_agent_v2/
├── config/
│   └── panelin_truth_bmcuruguay.json  # Single Source of Truth (precios)
│
├── tools/
│   ├── quotation_calculator.py        # Cálculos deterministas (Decimal)
│   └── product_lookup.py              # Búsqueda de productos
│
├── agent/
│   └── panelin_agent.py               # LangGraph agent con tools
│
├── sync/
│   └── shopify_sync.py                # Webhooks Shopify ↔ KB
│
├── tests/
│   ├── test_quotation_calculator.py   # Golden dataset tests
│   ├── test_product_lookup.py         # Tests de búsqueda
│   └── test_agent_integration.py      # Tests E2E
│
└── panelin_improvement_guide.yaml     # Guía para AI agents
```

## Productos Soportados

| Familia   | Aplicación        | Espesores Disponibles |
|-----------|-------------------|-----------------------|
| ISOPANEL  | Paredes, Fachadas | 50, 100, 150, 200, 250 mm |
| ISODEC    | Techos, Cubiertas | 100, 150, 200, 250 mm (EPS) / 50, 80, 120 mm (PIR) |
| ISOWALL   | Fachadas Premium  | 50, 80 mm (PIR) |
| ISOROOF   | Techos Rápidos    | 30, 50, 80 mm |
| HIANSA    | Techos Trapezoidales | 50 mm |

## Tests

```bash
# Correr todos los tests
cd panelin_agent_v2
python -m pytest tests/ -v

# Solo tests de cálculo (golden dataset)
python -m pytest tests/test_quotation_calculator.py -v

# Verificar cobertura
python -m pytest tests/ --cov=. --cov-report=term-missing
```

## Sincronización con Shopify

El sistema mantiene la KB sincronizada con Shopify mediante:

1. **Webhooks en tiempo real** - `products/update`, `inventory_levels/update`
2. **Reconciliación diaria** - Verifica integridad KB vs Shopify API
3. **Audit trail** - Git commit automático en cada cambio

```python
from panelin_agent_v2 import ShopifySyncService

service = ShopifySyncService()

# Ver estado de sincronización
status = service.get_sync_status()
print(f"Última sync: {status['last_sync']}")
print(f"Productos: {status['products_count']}")

# Procesar webhook (en endpoint Flask/FastAPI)
result = service.handle_webhook(
    topic="products/update",
    payload=webhook_data,
    hmac_header=request.headers["X-Shopify-Hmac-SHA256"]
)
```

## Costos Estimados

| Modelo | Costo por Cotización | Velocidad |
|--------|---------------------|-----------|
| GPT-4o-mini | ~$0.002 | ~150 t/s |
| Gemini 2.5 Flash | ~$0.002 | ~250 t/s |
| Claude 3.5 Haiku | ~$0.004 | ~66 t/s |
| GPT-4o | ~$0.01 | ~100 t/s |

## Comparativa con Arquitectura Anterior

| Aspecto | Multi-Agent (Anterior) | Single-Agent V2 |
|---------|------------------------|-----------------|
| Cálculos | Potencialmente por LLM | 100% código Python |
| Precisión | Variable | **100% garantizada** |
| Costo/consulta | ~$0.03-0.05 | **~$0.002-0.01** |
| Latencia | 5-8 segundos | **1.5-3 segundos** |
| KB Sync | Manual | **Tiempo real (webhooks)** |

## Referencias

- [LangGraph 1.0 Documentation](https://langchain-ai.github.io/langgraph/)
- [Anthropic: Building Effective Agents (2025)](https://anthropic.com)
- [OpenAI Responses API](https://platform.openai.com/docs/api-reference)
- [Cognition AI: Don't Build Multi-Agents](https://cognition-labs.com)

## Licencia

Propiedad de BMC Uruguay. Uso interno solamente.
