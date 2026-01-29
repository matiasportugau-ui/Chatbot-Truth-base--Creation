# Panelin Quotation Agent v2 - Arquitectura Híbrida

Sistema de cotización de paneles aislantes para BMC Uruguay con **precisión 100%** en cálculos mediante arquitectura híbrida: LLM orquesta, código Python calcula.

## Principio Fundamental

> **El LLM NUNCA calcula - solo extrae parámetros y formatea respuestas.**
> 
> Toda la aritmética financiera ocurre en funciones Python usando `Decimal` para precisión garantizada.

## Arquitectura

```
┌──────────────────────────────────────────────────────────────────┐
│                    PANELIN QUOTATION AGENT v2                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌──────────────────┐    ┌────────────────┐  │
│  │ Input       │───→│ LLM: Extracción  │───→│ Validación     │  │
│  │ Usuario     │    │ de Parámetros    │    │ Schema + Rango │  │
│  │ (Lenguaje   │    │ (Structured Out) │    │ (Python)       │  │
│  │  Natural)   │    │                  │    │                │  │
│  └─────────────┘    └──────────────────┘    └───────┬────────┘  │
│                                                     │            │
│  ┌─────────────┐    ┌──────────────────┐    ┌───────▼────────┐  │
│  │ LLM:        │←───│ Verificación     │←───│ CÁLCULO        │  │
│  │ Formato     │    │ Dual-Path        │    │ DETERMINISTA   │  │
│  │ Respuesta   │    │ (Python)         │    │ (Python/       │  │
│  │             │    │                  │    │  Decimal)      │  │
│  └─────────────┘    └──────────────────┘    └────────────────┘  │
│                                                                  │
│  HERRAMIENTAS DETERMINISTAS:                                     │
│  ├── calculate_panel_quote()      - Cotización Isopanel/Isodec  │
│  ├── lookup_product_specs()       - Query JSON KB exacto        │
│  ├── check_inventory_shopify()    - API tiempo real             │
│  ├── apply_pricing_rules()        - Descuentos, mínimos         │
│  └── validate_quotation()         - Verificación cruzada        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar API key (opcional para desarrollo)
export OPENAI_API_KEY="sk-..."
```

## Uso Rápido

### Cálculo Directo (Sin LLM)

```python
from panelin.tools.quotation_calculator import calculate_panel_quote, validate_quotation

# Calcular cotización
result = calculate_panel_quote(
    panel_type="Isopanel EPS",
    thickness_mm=100,
    length_m=4.0,
    width_m=1.14,
    quantity=20,
    discount_percent=5.0,
)

# Validar resultado
validation = validate_quotation(result)

print(f"Total: USD {result['total_usd']:.2f}")
print(f"Verificado: {result['calculation_verified']}")  # Siempre True
print(f"Válido: {validation['is_valid']}")
```

### Con Agente Híbrido (LLM + Tools)

```python
from panelin.agent.hybrid_agent import run_quotation_sync

# Lenguaje natural → Cotización precisa
result = run_quotation_sync(
    "Necesito 50 paneles Isodec de 4m x 1.12m, espesor 100mm, con envío"
)

print(result["response"])  # Respuesta formateada
print(result["quotation"]["total_usd"])  # Precio exacto
```

### Búsqueda en Knowledge Base

```python
from panelin.tools.knowledge_base import lookup_product_specs, search_products

# Búsqueda exacta
specs = lookup_product_specs("Isopanel EPS", thickness_mm=50)
print(f"Precio: USD {specs['price_per_m2']}/m²")

# Búsqueda semántica
results = search_products("paneles económicos para techos planos")
for r in results:
    print(f"{r['name']}: USD {r['price_per_m2']}/m²")
```

## Estructura del Paquete

```
panelin/
├── __init__.py              # Exports principales
├── README.md                # Esta documentación
├── requirements.txt         # Dependencias Python
├── panelin_improvement_guide.yaml  # Guía para AI agents
│
├── agent/                   # Agente LangGraph
│   ├── __init__.py
│   └── hybrid_agent.py      # Implementación del agente híbrido
│
├── config/                  # Configuración
│   ├── __init__.py
│   └── settings.py          # Configuración centralizada
│
├── data/                    # Base de conocimiento
│   └── panelin_truth_bmcuruguay.json  # FUENTE ÚNICA DE VERDAD
│
├── models/                  # Schemas y tipos
│   ├── __init__.py
│   └── schemas.py           # TypedDict definitions
│
├── tests/                   # Tests
│   ├── __init__.py
│   └── test_quotation_calculations.py  # Golden dataset tests
│
└── tools/                   # Herramientas deterministas
    ├── __init__.py
    ├── quotation_calculator.py  # Cálculos con Decimal
    ├── knowledge_base.py        # Operaciones de KB
    └── shopify_sync.py          # Sincronización Shopify
```

## Productos Disponibles

| Producto | Familia | Espesores | Precio/m² |
|----------|---------|-----------|-----------|
| ISOPANEL EPS | Paredes/Fachadas | 50-250mm | USD 41.88+ |
| ISODEC EPS | Techos/Cubiertas | 100-250mm | USD 46.07+ |
| ISODEC PIR | Techos Premium | 50-120mm | USD 51.02+ |
| ISOWALL PIR | Fachadas Premium | 50-80mm | USD 54.65+ |
| ISOROOF 3G | Techos Estándar | 30-50mm | USD 48.74 |
| ISOROOF PLUS 3G | Techos Premium | 50-80mm | USD 71.76 |
| ISOROOF FOIL 3G | Techos Económico | 30-50mm | USD 39.54 |
| HIANSA Panel 5G | Trapezoidales | - | USD 46.73 |

## Tests

```bash
# Ejecutar todos los tests
pytest panelin/tests/ -v

# Solo tests de cálculo
pytest panelin/tests/test_quotation_calculations.py -v

# Con coverage
pytest panelin/tests/ --cov=panelin --cov-report=html
```

### Golden Dataset Tests

El archivo `test_quotation_calculations.py` incluye 50+ casos de prueba pre-calculados manualmente que **DEBEN pasar antes de deployment**.

## Sincronización Shopify

El sistema soporta sincronización automática con Shopify:

1. **Webhooks tiempo real**: `products/update`, `inventory_levels/update`
2. **Reconciliación diaria**: Detecta discrepancias KB ↔ Shopify
3. **Audit trail**: Todos los cambios se registran en `sync_history.json`

```python
from panelin.tools.shopify_sync import handle_shopify_webhook

# Procesar webhook
event = handle_shopify_webhook(
    topic="products/update",
    payload=shopify_payload,
)
print(f"Sync status: {event['sync_status']}")
```

## Métricas de Rendimiento

| Métrica | Valor Objetivo |
|---------|----------------|
| Costo por consulta | $0.002-0.01 |
| Latencia p95 | < 3 segundos |
| Precisión cálculos | 100% |
| Sync KB-Shopify | Tiempo real |

## Principios para Contribuidores

1. **calculation_verified = True**: Toda cotización DEBE tener este campo en True
2. **Usar Decimal**: Nunca usar `float` para cálculos financieros
3. **Cargar precios de KB**: Nunca hardcodear precios en código
4. **Validar siempre**: Llamar `validate_quotation()` después de cada cálculo
5. **Tests primero**: Agregar tests antes de modificar funciones de cálculo

Ver `panelin_improvement_guide.yaml` para documentación completa.

## Licencia

Propiedad de BMC Uruguay. Uso interno únicamente.
