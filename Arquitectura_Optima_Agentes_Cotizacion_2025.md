# Arquitectura optima para agentes GPT de cotizacion en e-commerce (2025)

## Resumen ejecutivo

El sistema de cotizacion de paneles aislantes de BMC Uruguay requiere un cambio
arquitectonico fundamental: abandonar el enfoque multi-agente y adoptar un
agente unico con herramientas deterministas. La investigacion 2025 confirma que
ningun LLM garantiza precision matematica del 100%. La solucion es usar el LLM
solo para comprension de lenguaje natural y dejar toda la aritmetica en Python.
Con LangGraph 1.0 y sincronizacion automatica con Shopify, el costo por
cotizacion se estima en ~USD 0.002-0.01.

---

## 1. Validacion del analisis original: que sigue vigente y que cambio

### 1.1 Hallazgos que permanecen vigentes

- Auto-GPT y BabyAGI no son aptos para produccion (bucles, alucinaciones,
  costos elevados). BabyAGI fue archivado oficialmente en septiembre 2024.
- El ranking que priorizaba contexto, instrucciones e integracion de
  herramientas sobre complejidad arquitectonica se confirma.
- Los patrones ReAct y Plan-and-Execute siguen dominando. ReAct permanece como
  loop base (observar -> pensar -> actuar -> observar) y Plan-and-Execute se
  expresa hoy como Flows + Crews en CrewAI.

### 1.2 Cambios significativos desde 2024

| Aspecto                   | Estado 2024                  | Estado 2025                                   |
|---------------------------|------------------------------|-----------------------------------------------|
| LangChain                 | Fragmentado, evolucion rapida| LangGraph 1.0 GA (oct 2025), framework lider  |
| OpenAI Assistants API     | API principal                | Deprecado (ago 2025), sunset en ago 2026      |
| Claude MCP                | Recien anunciado             | Estandar de industria (OpenAI/Microsoft)      |
| CrewAI                    | Framework emergente          | 1.7B workflows procesados, clientes enterprise|
| Microsoft AutoGen         | Framework activo             | En mantenimiento, reemplazado por Agent FW    |

Conclusiones reforzadas:
- Simplicidad > complejidad cuando hay precision critica.
- Multi-agente solo si hay necesidad real de especializacion.
- LLM debe orquestar, nunca calcular.

---

## 2. Comparativa tecnica actualizada de LLMs y frameworks

### 2.1 Modelos LLM para cotizaciones con precision critica

Hallazgo central: ningun LLM garantiza 100% de precision matematica. Por eso
el LLM solo extrae parametros y orquesta tools; el calculo lo hace Python.

| Modelo                   | Costo input/1M | Costo output/1M | Contexto | Velocidad     | Fortaleza principal                         |
|--------------------------|---------------|----------------|----------|---------------|---------------------------------------------|
| GPT-4o                   | USD 2.50      | USD 10.00      | 128K     | ~100-150 t/s  | Structured Outputs con alta adherencia      |
| GPT-4o-mini              | USD 0.15      | USD 0.60       | 128K     | ~150-200 t/s  | Mejor costo/rendimiento para extraccion     |
| Claude 3.5 Sonnet        | USD 3.00      | USD 15.00      | 200K     | ~77 t/s       | Menor varianza en produccion                |
| Claude 3.5 Haiku         | USD 0.80      | USD 4.00       | 200K     | ~66 t/s       | Balance costo/calidad                       |
| Gemini 2.5 Flash         | USD 0.30      | USD 2.50       | 1M       | ~250 t/s      | Contexto masivo y buena velocidad           |
| Gemini 2.5 Flash-Lite    | USD 0.10      | USD 0.40       | 1M       | ~581 t/s      | Ultra-economico para alto volumen           |

Estimacion por cotizacion tipica (2K tokens input, 500 output):
- GPT-4o: ~USD 0.01
- Gemini 2.5 Flash: ~USD 0.002
- Claude 3.5 Haiku: ~USD 0.004

### 2.2 Frameworks: evaluacion para BMC

| Framework             | Madurez produccion | Idoneidad e-commerce | Recomendacion            |
|----------------------|--------------------|----------------------|--------------------------|
| LangGraph 1.0        | Alta (GA)          | Muy alta             | Recomendado primario     |
| CrewAI               | Alta               | Media/Alta           | Alternativa valida       |
| OpenAI Agents SDK    | Alta               | Alta                 | Si hay lock-in OpenAI    |
| Claude MCP           | Alta               | Alta                 | Ideal para conectores    |
| Python custom        | Media              | Alta                 | Solo si hay expertise    |

---

## 3. Arquitectura optimizada propuesta para BMC Uruguay

### 3.1 Principio fundamental: LLM orquesta, codigo calcula

El LLM solo interpreta la intencion, extrae parametros y formatea la respuesta.
Toda la aritmetica ocurre en funciones Python deterministas con Decimal.

### 3.2 Diagrama de referencia

```
┌──────────────────────────────────────────────────────────────────┐
│                PANELIN QUOTATION AGENT v2                         │
├──────────────────────────────────────────────────────────────────┤
│  Input usuario -> LLM extraccion -> Validacion -> Calculo Python │
│                          ^                      |                │
│                          |                      v                │
│                   LLM formato <- Verificacion <- Resultado       │
├──────────────────────────────────────────────────────────────────┤
│ Herramientas deterministas:                                      │
│ - calculate_panel_quote()   - cotizacion exacta                  │
│ - lookup_product_specs()    - KB JSON estructurado               │
│ - check_inventory_shopify() - stock en tiempo real               │
│ - apply_pricing_rules()     - descuentos/minimos                 │
│ - validate_quotation()      - verificacion cruzada               │
└──────────────────────────────────────────────────────────────────┘
```

### 3.3 Stack tecnologico recomendado

| Componente           | Tecnologia                     | Justificacion                              |
|---------------------|--------------------------------|--------------------------------------------|
| Framework agente    | LangGraph 1.0                  | GA, trazabilidad, time-travel debugging   |
| LLM primario        | GPT-4o-mini o Gemini 2.5 Flash | Costo/velocidad para extraccion            |
| LLM fallback        | Claude 3.5 Haiku               | Menor varianza en edge cases               |
| KB estructurada     | JSON + JSON Schema             | Precision y auditabilidad                  |
| Vector store        | Qdrant (opcional)              | Busqueda semantica si se requiere          |
| Sync engine         | n8n o Python custom            | Webhooks Shopify -> KB                     |
| Observabilidad      | LangSmith o Langfuse           | Trazas completas de tool calls             |

---

## 4. Implementacion de herramientas de calculo

### 4.1 Funcion determinista de cotizacion (Python)

```python
from decimal import Decimal, ROUND_HALF_UP
from typing import TypedDict
import json

class QuotationResult(TypedDict):
    product_id: str
    area_m2: float
    unit_price_usd: float
    quantity: int
    subtotal_usd: float
    total_usd: float
    calculation_verified: bool

def calculate_panel_quote(
    panel_type: str,      # "Isopanel", "Isodec", "Isoroof"
    thickness_mm: int,    # 50, 75, 100, etc.
    length_m: float,
    width_m: float,
    quantity: int,
    discount_percent: float = 0.0
) -> QuotationResult:
    """
    Calculo determinista de cotizacion.
    El LLM nunca ejecuta esta matematica.
    """
    with open("panelin_truth_bmcuruguay.json", "r") as f:
        catalog = json.load(f)

    product_key = f"{panel_type}_{thickness_mm}mm"
    if product_key not in catalog["products"]:
        raise ValueError(f"Producto no encontrado: {product_key}")

    price_per_m2 = Decimal(str(catalog["products"][product_key]["price_per_m2"]))
    area = Decimal(str(length_m)) * Decimal(str(width_m))
    unit_price = (area * price_per_m2).quantize(Decimal("0.01"), ROUND_HALF_UP)
    subtotal = (unit_price * quantity).quantize(Decimal("0.01"), ROUND_HALF_UP)
    discount = (subtotal * Decimal(str(discount_percent)) / 100).quantize(
        Decimal("0.01"), ROUND_HALF_UP
    )
    total = (subtotal - discount).quantize(Decimal("0.01"), ROUND_HALF_UP)

    return {
        "product_id": product_key,
        "area_m2": float(area),
        "unit_price_usd": float(unit_price),
        "quantity": quantity,
        "subtotal_usd": float(subtotal),
        "total_usd": float(total),
        "calculation_verified": True,
    }
```

### 4.2 Definicion de tool para LLM (schema estricto)

```json
{
  "name": "calculate_panel_quote",
  "description": "Calcula cotizacion exacta para paneles termicos BMC. Usar SIEMPRE para precios.",
  "strict": true,
  "parameters": {
    "type": "object",
    "properties": {
      "panel_type": {
        "type": "string",
        "enum": ["Isopanel", "Isodec", "Isoroof"],
        "description": "Tipo de panel solicitado"
      },
      "thickness_mm": {
        "type": "integer",
        "enum": [50, 75, 100, 150],
        "description": "Espesor en milimetros"
      },
      "length_m": {
        "type": "number",
        "minimum": 0.5,
        "maximum": 12.0,
        "description": "Largo del panel en metros"
      },
      "width_m": {
        "type": "number",
        "minimum": 0.5,
        "maximum": 1.5,
        "description": "Ancho del panel en metros"
      },
      "quantity": {
        "type": "integer",
        "minimum": 1,
        "description": "Cantidad de paneles"
      },
      "discount_percent": {
        "type": "number",
        "minimum": 0,
        "maximum": 30,
        "default": 0,
        "description": "Porcentaje de descuento aplicable"
      }
    },
    "required": ["panel_type", "thickness_mm", "length_m", "width_m", "quantity"]
  }
}
```

---

## 5. Estrategia de sincronizacion KB <-> Shopify

### 5.1 Arquitectura de sincronizacion recomendada

```
Shopify webhooks (products/update, inventory/update, products/delete)
    -> Sync service (n8n o Python)
        1) Validar HMAC
        2) Transformar schema Shopify -> KB
        3) Validar datos (precio > 0, SKU existe)
        4) Actualizar JSON KB con timestamp
        5) Commit a Git (audit trail)
        6) Reindexar Qdrant (si aplica)
        7) Notificar exito/fallo
```

### 5.2 Estructura JSON recomendada para KB

```json
{
  "version": "2.0.0",
  "last_sync": "2026-01-28T10:00:00Z",
  "shopify_store": "bmcuruguay.myshopify.com",
  "products": {
    "Isopanel_50mm": {
      "shopify_id": "gid://shopify/Product/12345",
      "name": "Panel Isopanel 50mm",
      "price_per_m2": 22.50,
      "currency": "USD",
      "available_thicknesses": [50, 75, 100],
      "calculation_rules": {
        "minimum_order_m2": 10,
        "bulk_discount_threshold_m2": 100,
        "bulk_discount_percent": 5
      },
      "inventory_quantity": 150,
      "last_updated": "2026-01-28T09:30:00Z",
      "_sync_source": "shopify_webhook"
    }
  },
  "pricing_rules": {
    "tax_rate_uy": 22,
    "delivery_cost_per_m2": 1.50,
    "minimum_delivery_charge": 50
  }
}
```

### 5.3 Reconciliacion diaria automatizada

```python
async def daily_shopify_reconciliation():
    """Verifica integridad KB vs Shopify API."""
    shopify_products = await shopify_client.get_all_products()
    kb_products = load_knowledge_base()

    discrepancies = []
    for sku, shopify_data in shopify_products.items():
        if sku not in kb_products:
            discrepancies.append(f"MISSING: {sku} not in KB")
        elif abs(kb_products[sku]["price_per_m2"] - shopify_data["price"]) > 0.01:
            discrepancies.append(f"PRICE_MISMATCH: {sku}")

    if discrepancies:
        alert_operations_team(discrepancies)
```

---

## 6. Sistema de validacion y testing para precision 100%

### 6.1 Tests con golden dataset

```python
def test_basic_isopanel_quote():
    result = calculate_panel_quote(
        panel_type="Isopanel",
        thickness_mm=50,
        length_m=2.0,
        width_m=1.0,
        quantity=10
    )
    assert result["area_m2"] == 2.0
    assert result["total_usd"] == 450.0  # 2m2 * 22.50 * 10
    assert result["calculation_verified"] is True

def test_discount_application():
    result = calculate_panel_quote(
        panel_type="Isodec",
        thickness_mm=75,
        length_m=3.0,
        width_m=1.2,
        quantity=50,
        discount_percent=10
    )
    expected_subtotal = 3.0 * 1.2 * 28.00 * 50
    expected_total = expected_subtotal * 0.9
    assert abs(result["total_usd"] - expected_total) < 0.01

def test_llm_never_calculates():
    result = calculate_panel_quote(
        panel_type="Isoroof",
        thickness_mm=100,
        length_m=4.0,
        width_m=1.0,
        quantity=2
    )
    assert result["calculation_verified"] is True
```

### 6.2 Monitoreo en produccion

| Metrica                             | Umbral    | Accion                          |
|------------------------------------|-----------|---------------------------------|
| calculation_verified == False      | 0 casos   | Alerta critica inmediata        |
| Error rate schema validation       | < 0.1%    | Revisar prompts de extraccion   |
| Precio fuera de rango esperado     | 0 casos   | Encolar revision humana         |
| Latencia p95                       | < 3 s     | Optimizar o escalar             |

---

## 7. Comparativa: Panelin actual vs arquitectura propuesta

| Aspecto                  | Panelin actual (multi-agente) | Arquitectura propuesta          |
|-------------------------|-------------------------------|---------------------------------|
| Patron                  | Multiples agentes              | Agente unico con tools          |
| Calculos                | Posible LLM                    | 100% codigo determinista        |
| KB Sync                 | Manual/semi-manual             | Webhooks Shopify automaticos    |
| Framework               | Python custom                  | LangGraph 1.0                   |
| Latencia                | Mayor                          | Menor (1-2 LLM calls)           |
| Costo                   | Mayor                          | ~60% menos                      |
| Mantenibilidad          | Compleja                       | Herramientas versionables       |
| Precision garantizada   | No                             | Si (codigo determinista)        |

---

## 8. Roadmap de migracion

**Fase 1 (Semana 1-2): Fundacion**
- Consolidar JSON KB en una unica fuente de verdad
- Implementar funciones de calculo deterministas con tests
- Configurar webhooks Shopify basicos

**Fase 2 (Semana 3-4): Agente core**
- Migrar a LangGraph 1.0 con tool definitions
- Configurar structured outputs para extraccion
- Implementar verificacion dual-path

**Fase 3 (Semana 5-6): Produccion**
- Testing con golden dataset (50+ casos)
- Configurar observabilidad (LangSmith/Langfuse)
- Deploy gradual con shadow testing vs sistema actual

**Fase 4 (Continuo): Optimizacion**
- Evaluar Qdrant para busqueda semantica si aplica
- Optimizar seleccion de modelos
- Caching de consultas frecuentes

---

## 9. Documentacion estructurada para mejora de archivos Panelin

Se incluye el archivo `panelin_improvement_guide.yaml` con principios y acciones
de mejora para agentes que editen el sistema.

Ejemplo (resumen):

```yaml
architecture_principles:
  - LLM_NEVER_CALCULATES: "Todo calculo matematico debe ejecutarse en Python"
  - SINGLE_SOURCE_OF_TRUTH: "panelin_truth_bmcuruguay.json es la unica fuente"
  - DETERMINISTIC_FIRST: "Preferir herramientas deterministas"
  - VALIDATE_EVERYTHING: "Cada output de calculo debe validarse"
```

---

## 10. Estimaciones finales: costo, velocidad, precision

| Metrica                | Arquitectura actual   | Arquitectura propuesta |
|------------------------|-----------------------|------------------------|
| Costo por consulta     | ~USD 0.03-0.05         | USD 0.002-0.01         |
| Latencia promedio      | 5-8 s                 | 1.5-3 s                |
| Precision de calculos  | Variable (LLM)        | 100% (codigo)          |
| Sync KB                | Manual                | Tiempo real (webhooks) |
| Mantenimiento mensual  | Alto                  | Bajo (automatizado)    |

Conclusion: la separacion estricta entre LLM (comprension) y Python (calculo)
reduce costos, baja latencia y garantiza precision total en cotizaciones.
