# Panelin Hybrid Agent v2.0

Arquitectura óptima para agentes GPT de cotización en e-commerce para BMC Uruguay.

## 🎯 Principio Fundamental

**LLM orquesta, código calcula.**

El LLM NUNCA ejecuta aritmética—solo interpreta intención, extrae parámetros, y formatea respuestas. Toda operación matemática ocurre en funciones Python deterministas usando el tipo `Decimal`.

## 📊 Arquitectura

```
┌──────────────────────────────────────────────────────────────────┐
│                    PANELIN QUOTATION AGENT v2                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌──────────────────┐    ┌────────────────┐  │
│  │ Input       │───→│ LLM: Extracción  │───→│ Validación     │  │
│  │ Usuario     │    │ de Parámetros    │    │ Schema + Rango │  │
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
│  ├── calculate_panel_quote()      - Cotización paneles          │
│  ├── calculate_fixation_points()  - Puntos de fijación          │
│  ├── lookup_product_specs()       - Query JSON KB exacto        │
│  └── apply_pricing_rules()        - Descuentos, mínimos         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

```
panelin_hybrid_agent/
├── __init__.py                 # Exports principales
├── tools/                      # Herramientas deterministas
│   ├── quotation_calculator.py # Cálculos con Decimal
│   ├── product_lookup.py       # Búsqueda en KB
│   └── pricing_rules.py        # Reglas de negocio
├── agent/                      # Agente LangGraph
│   ├── panelin_agent.py        # Implementación
│   └── tool_definitions.py     # Definiciones para LLM
├── kb/                         # Knowledge Base
│   └── panelin_truth_bmcuruguay.json
├── sync/                       # Sincronización Shopify
│   ├── shopify_sync.py         # Service de sync
│   └── webhook_handler.py      # Handler webhooks
├── validation/                 # Validación
│   ├── validators.py           # Validadores
│   └── monitoring.py           # Observabilidad
├── tests/                      # Tests
│   ├── test_quotation_calculator.py
│   └── test_validation.py
├── panelin_improvement_guide.yaml  # Documentación YAML
└── requirements.txt            # Dependencias
```

## 🚀 Inicio Rápido

### Instalación

```bash
pip install -r panelin_hybrid_agent/requirements.txt
```

### Uso Básico

```python
from panelin_hybrid_agent import calculate_panel_quote, calculate_complete_quotation

# Cotización de paneles individual
result = calculate_panel_quote(
    panel_type="Isoroof",
    thickness_mm=50,
    length_m=6.0,
    width_m=1.0,
    quantity=10,
    price_type="empresa"
)

print(f"Total: USD {result['total_usd']:.2f}")
print(f"Verificado: {result['calculation_verified']}")  # SIEMPRE True

# Cotización completa con perfiles y fijaciones
complete = calculate_complete_quotation(
    panel_type="Isoroof",
    thickness_mm=50,
    total_width_m=10.0,
    total_length_m=6.0,
    include_accessories=True,
    include_fixation=True
)

print(f"Paneles: {complete['panel_count']}")
print(f"Total: USD {complete['grand_total_usd']:.2f}")
```

### Ejecutar Tests

```bash
cd panelin_hybrid_agent
pytest tests/ -v
```

## 🔢 Fórmulas de Cálculo

| Concepto | Fórmula |
|----------|---------|
| Cantidad de paneles | `ROUNDUP(ancho_total / ancho_útil)` |
| Apoyos | `ROUNDUP((largo / autoportancia) + 1)` |
| Puntos fijación | `ROUNDUP(((paneles × apoyos) × 2) + (largo × 2 / 2.5))` |
| Varillas | `ROUNDUP(puntos / 4)` |
| Tuercas metal | `puntos × 2` |
| Goteros frontales | `ROUNDUP((paneles × ancho_útil) / 3)` |
| Goteros laterales | `ROUNDUP((largo × 2) / 3)` |
| Remaches | `ROUNDUP(perfiles_total × 20)` |

## ✅ Validación

Todas las herramientas retornan `calculation_verified: True` para confirmar que el cálculo fue ejecutado por código determinista, no por el LLM.

```python
from panelin_hybrid_agent.validation import validate_quotation

result = validate_quotation(quotation)
if not result["valid"]:
    print("Errores:", result["errors"])
```

## 📊 Monitoreo

```python
from panelin_hybrid_agent.validation import get_metrics_summary

metrics = get_metrics_summary()
print(f"Requests: {metrics['total_requests']}")
print(f"Errores: {metrics['total_errors']}")
print(f"Sin verificación: {metrics['calculation_not_verified']}")  # DEBE ser 0
```

## 💰 Costos Estimados

| Modelo | Costo por consulta |
|--------|-------------------|
| GPT-4o | $0.01 |
| Gemini 2.5 Flash | $0.002 |
| Claude 3.5 Haiku | $0.004 |

## 📚 Documentación Adicional

- `panelin_improvement_guide.yaml`: Guía completa de arquitectura
- `kb/panelin_truth_bmcuruguay.json`: Knowledge Base de productos

## 🔑 Principios Clave

1. **LLM_NEVER_CALCULATES**: El LLM solo extrae parámetros
2. **SINGLE_SOURCE_OF_TRUTH**: JSON KB es la única fuente de precios
3. **DETERMINISTIC_FIRST**: Preferir herramientas sobre razonamiento
4. **VALIDATE_EVERYTHING**: Cada output debe ser verificado
5. **SINGLE_AGENT_PATTERN**: Un agente con tools, no multi-agente

---

*Basado en investigación 2025: Anthropic "Building Effective Agents", Cognition AI "Don't Build Multi-Agents", y arquitectura Klarna (2.3M conversaciones/mes).*
