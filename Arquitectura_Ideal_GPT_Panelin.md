# Arquitectura Ideal del GPT: Panelin (BMC Assistant Pro)

## Resumen Ejecutivo

Este documento define la **arquitectura perfecta** para el GPT Assistant "Panelin", considerando:
- ✅ **Configuración actual inamovible** (personalidad, usuarios específicos, archivos existentes)
- ✅ **Mejores prácticas de arquitectura RAG** (Retrieval-Augmented Generation)
- ✅ **Optimización para dominio técnico-comercial** (cotizaciones, productos constructivos)
- ✅ **Escalabilidad y mantenibilidad** a largo plazo

> Nota 2026-01-28: Para la arquitectura 2025 de agente único con herramientas
> deterministas, sincronización Shopify y costos optimizados, ver
> `Arquitectura_Optima_Agentes_Cotizacion_2025.md`.

---

## Actualización 2025: Arquitectura óptima para agentes GPT de cotización en e-commerce

El sistema de cotización de paneles aislantes de BMC Uruguay requiere un **cambio arquitectónico fundamental**: abandonar el enfoque multi-agente actual de Panelin en favor de un **agente único con herramientas deterministas**. La investigación de 2025 confirma que ningún LLM puede garantizar precisión del 100% en cálculos; la solución es usar el LLM exclusivamente para comprensión de lenguaje natural mientras Python ejecuta toda la aritmética. Esta arquitectura híbrida, combinada con LangGraph 1.0 y sincronización automática con Shopify, puede lograr precisión total en cotizaciones a un costo de **~$0.002-0.01 por consulta**.

### Validación del análisis original: qué sigue vigente y qué cambió

El análisis exhaustivo de Matías sobre frameworks y patrones arquitectónicos **sigue siendo fundamentalmente correcto**, con actualizaciones importantes que refuerzan algunas conclusiones y modifican otras.

#### Hallazgos que permanecen vigentes

- La evaluación de **Auto-GPT y BabyAGI como no aptos para producción** se confirma completamente. Auto-GPT alcanzó v0.6.38 pero continúa experimentando bucles infinitos, alucinaciones con datos web y costos operativos excesivos. BabyAGI fue archivado oficialmente en septiembre 2024; su creador explícitamente declara que "no está diseñado para producción".
- El ranking de características que priorizaba **contexto/instrucciones e integración de herramientas** sobre complejidad arquitectónica resulta profético: la industria ha convergido hacia exactamente esta filosofía.
- Los patrones **ReAct loop y Plan-and-Execute** siguen siendo los dominantes. ReAct permanece como patrón fundacional (observar → pensar → actuar → observar) pero ahora se combina con **tool calling dentro de chain-of-thought** en modelos como o3/o4-mini de OpenAI. Plan-and-Execute se manifiesta en el patrón "Flows + Crews" de CrewAI: backbone determinista con agentes inteligentes en pasos específicos.

#### Cambios significativos desde 2024

| Aspecto | Estado 2024 | Estado 2025 |
|---|---|---|
| **LangChain** | Fragmentado, evolución rápida | LangGraph 1.0 GA (octubre 2025), framework líder |
| **OpenAI Assistants API** | API principal | **DEPRECADO** agosto 2025, sunset agosto 2026 |
| **Claude MCP** | Recién anunciado | Estándar de industria, adoptado por OpenAI y Microsoft |
| **CrewAI** | Framework emergente | **1.7B workflows procesados**, clientes enterprise |
| **Microsoft AutoGen** | Framework activo | En mantenimiento, reemplazado por Microsoft Agent Framework |

El cambio más relevante para BMC es la **transición de OpenAI Assistants API a Responses API**, que introduce un modelo más eficiente con herramientas nativas (web search, file search, code interpreter) y soporte para MCP. La nueva arquitectura es "agentic by default": el modelo puede llamar múltiples herramientas por request.

#### La conclusión sobre simplicidad vs complejidad se refuerza

Anthropic, en su guía 2025 "Building Effective Agents", establece: *"Encuentra la solución más simple posible y solo aumenta complejidad cuando sea necesario. Los sistemas agenticos frecuentemente intercambian latencia y costo por mejor rendimiento en tareas."* Cognition AI (creadores de Devin) publicó "Don't Build Multi-Agents" argumentando que la pérdida de contexto entre subagentes causa inconsistencias, exactamente el problema identificado.

### Comparativa técnica actualizada de LLMs y frameworks

#### Modelos LLM para cotizaciones con precisión crítica

La investigación reveló un hallazgo crucial: **ningún LLM garantiza precisión matemática del 100%**. GPT-4o alcanza ~73% en benchmarks de cálculos complejos; estudios médicos muestran **0% de precisión** en tareas de cálculo sin herramientas externas. La implicación arquitectónica es clara: el LLM debe orquestar, nunca calcular.

| Modelo | Costo Input/1M | Costo Output/1M | Contexto | Velocidad | Fortaleza |
|---|---:|---:|---:|---:|---|
| **GPT-4o** | $2.50 | $10.00 | 128K | ~100-150 t/s | Structured Outputs con 100% adherencia a schema |
| **GPT-4o-mini** | $0.15 | $0.60 | 128K | ~150-200 t/s | Mejor costo/rendimiento para extracción |
| **Claude 3.5 Sonnet** | $3.00 | $15.00 | 200K | ~77 t/s | Menor varianza en producción, razonamiento superior |
| **Claude 3.5 Haiku** | $0.80 | $4.00 | 200K | ~66 t/s | Balance óptimo costo/calidad |
| **Gemini 2.5 Flash** | $0.30 | $2.50 | 1M | ~250 t/s | Contexto masivo para KB completa, código integrado |
| **Gemini 2.5 Flash-Lite** | $0.10 | $0.40 | 1M | ~581 t/s | Ultra-económico para alto volumen |

**Estimación de costo por cotización típica** (~2K tokens input, ~500 tokens output):

- GPT-4o: **$0.01** — mejor structured outputs
- Gemini 2.5 Flash: **$0.002** — óptimo costo/velocidad
- Claude 3.5 Haiku: **$0.004** — balance razonamiento/costo

#### Frameworks: evaluación para caso BMC

| Framework | Madurez Producción | Idoneidad E-commerce | Recomendación |
|---|---|---|---|
| **LangGraph 1.0** | ⭐⭐⭐⭐⭐ GA, Uber/LinkedIn/Klarna | ⭐⭐⭐⭐⭐ Ideal para workflows complejos | **RECOMENDADO PRIMARIO** |
| **CrewAI** | ⭐⭐⭐⭐⭐ 1.7B workflows | ⭐⭐⭐⭐ Multi-agente cuando necesario | Buena alternativa |
| **OpenAI Agents SDK** | ⭐⭐⭐⭐ Nueva, activa | ⭐⭐⭐⭐ Simple si solo OpenAI | Si locked-in OpenAI |
| **Claude MCP** | ⭐⭐⭐⭐ Estándar emergente | ⭐⭐⭐⭐ Integraciones rápidas | Para conectores |
| **Python Custom** | ⭐⭐⭐ Requiere mantenimiento | ⭐⭐⭐ Control total | Solo si expertise interno |

Klarna implementó con LangGraph un asistente que maneja 2.3M conversaciones/mes, reduciendo tiempo de resolución de 11 a 2 minutos. Su arquitectura: **agente único** que enruta requests y llama herramientas.

#### Estrategias de Knowledge Base

| Approach | Ventajas | Desventajas | Costo Mensual |
|---|---|---|---|
| **JSON Estructurado (SSOT)** | Precisión exacta, determinista, auditable | Sin búsqueda semántica | ~$0 (storage) |
| **Qdrant** | Free tier 1GB, excelente filtrado | Requiere embeddings | $0-25/mo |
| **Weaviate** | Mejor búsqueda híbrida (vector + keyword) | Más complejo | $25/mo |
| **pgvector** | Unifica con PostgreSQL existente | Menos features que dedicados | Costo PG existente |
| **Pinecone** | Zero-ops, 7ms latencia | Más costoso | $50/mo mínimo |

**Recomendación para BMC**: mantener **JSON estructurado como fuente de verdad** para precios y fórmulas de cálculo (garantiza precisión), con **Qdrant o Weaviate opcional** para búsqueda semántica.

### Arquitectura optimizada propuesta para BMC Uruguay

#### Principio fundamental: LLM orquesta, código calcula

La arquitectura propuesta separa responsabilidades de manera crítica: el LLM **nunca ejecuta aritmética**; solo interpreta intención, extrae parámetros y formatea respuestas. Toda operación matemática ocurre en funciones Python deterministas.

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
│  STORAGE:                                                        │
│  ├── panelin_truth_bmcuruguay.json  - Fuente de verdad           │
│  ├── Shopify API                     - Inventario tiempo real   │
│  └── Qdrant (opcional)               - Búsqueda semántica        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

#### Stack tecnológico recomendado

| Componente | Tecnología | Justificación |
|---|---|---|
| **Framework Agente** | LangGraph 1.0 | Production-ready, usado por Klarna, debugging con time-travel |
| **LLM Primario** | GPT-4o-mini o Gemini 2.5 Flash | Costo óptimo para extracción de parámetros |
| **LLM Fallback** | Claude 3.5 Haiku | Menor varianza para casos edge |
| **KB Estructurada** | JSON + JSON Schema | Precisión garantizada, versionable en Git |
| **Vector Store** | Qdrant Free Tier | Búsqueda semántica cuando necesaria |
| **Sync Engine** | n8n o Python custom | Webhooks Shopify → KB updates |
| **Observabilidad** | LangSmith o Langfuse | Trazabilidad completa de tool calls |

### Implementación de herramientas de cálculo

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
    Cálculo DETERMINISTA de cotización.
    El LLM NUNCA ejecuta esta matemática; solo extrae parámetros.
    """
    # Cargar precios desde fuente de verdad
    with open("panelin_truth_bmcuruguay.json", "r") as f:
        catalog = json.load(f)

    # Buscar precio exacto (no aproximación)
    product_key = f"{panel_type}_{thickness_mm}mm"
    if product_key not in catalog["products"]:
        raise ValueError(f"Producto no encontrado: {product_key}")

    price_per_m2 = Decimal(str(catalog["products"][product_key]["price_per_m2"]))

    # Cálculo con precisión Decimal (no floats)
    area = Decimal(str(length_m)) * Decimal(str(width_m))
    unit_price = (area * price_per_m2).quantize(Decimal("0.01"), ROUND_HALF_UP)
    subtotal = (unit_price * quantity).quantize(Decimal("0.01"), ROUND_HALF_UP)
    discount = (subtotal * Decimal(str(discount_percent)) / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)
    total = subtotal - discount

    return QuotationResult(
        product_id=product_key,
        area_m2=float(area),
        unit_price_usd=float(unit_price),
        quantity=quantity,
        subtotal_usd=float(subtotal),
        total_usd=float(total),
        calculation_verified=True  # Marca que pasó por código determinista
    )
```

### Definición de tool para LLM

```json
{
  "name": "calculate_panel_quote",
  "description": "Calcula cotización exacta para paneles térmicos BMC. USAR SIEMPRE para cualquier cálculo de precio.",
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
        "description": "Espesor en milímetros"
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

### Estrategia de sincronización KB ↔ Shopify

#### Arquitectura de sincronización recomendada

```
┌─────────────────────────────────────────────────────────────────┐
│                      SHOPIFY STORE                               │
│              (Fuente de verdad para inventario)                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │ products/ │   │ inventory_│   │ products/ │
    │ update    │   │ levels/   │   │ delete    │
    │ webhook   │   │ update    │   │ webhook   │
    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
          │               │               │
          └───────────────┼───────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SYNC SERVICE (n8n / Python)                   │
│  1. Validar HMAC del webhook                                     │
│  2. Transformar Shopify schema → KB schema                       │
│  3. Validar datos (precio > 0, SKU existe)                       │
│  4. Actualizar JSON KB con timestamp                             │
│  5. Commit a Git (audit trail)                                   │
│  6. Re-indexar en Qdrant si usa vector search                    │
│  7. Notificar éxito/fallo                                        │
└─────────────────────────────────────────────────────────────────┘
```

#### Estructura JSON recomendada para KB

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

#### Reconciliación diaria automatizada

Además de webhooks tiempo real, implementar **sync completo diario** para garantizar integridad:

```python
async def daily_shopify_reconciliation():
    """Verifica integridad KB vs Shopify API"""
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
        # Auto-fix o queue para revisión humana
```

### Sistema de validación y testing para precisión 100%

#### Framework de testing recomendado

```python
# tests/test_quotation_calculations.py
import pytest
from decimal import Decimal

class TestQuotationCalculations:
    """Golden dataset tests - MUST pass before deployment"""

    def test_basic_isopanel_quote(self):
        result = calculate_panel_quote(
            panel_type="Isopanel",
            thickness_mm=50,
            length_m=2.0,
            width_m=1.0,
            quantity=10
        )
        assert result["area_m2"] == 2.0
        assert result["total_usd"] == 450.0  # 2m² × $22.50 × 10
        assert result["calculation_verified"] is True

    def test_discount_application(self):
        result = calculate_panel_quote(
            panel_type="Isodec",
            thickness_mm=75,
            length_m=3.0,
            width_m=1.2,
            quantity=50,
            discount_percent=10
        )
        # Verificar que descuento se aplica correctamente
        expected_subtotal = 3.0 * 1.2 * 28.00 * 50  # Precio Isodec 75mm
        expected_total = expected_subtotal * 0.9
        assert abs(result["total_usd"] - expected_total) < 0.01

    def test_llm_never_calculates(self):
        """Verificar que output siempre viene de código determinista"""
        result = calculate_panel_quote(...)
        assert result["calculation_verified"] is True
        # Si este campo es False, el LLM calculó directamente -> FAIL
```

#### Monitoreo en producción

| Métrica | Umbral | Acción |
|---|---|---|
| `calculation_verified == False` | 0 instancias | ALERTA CRÍTICA inmediata |
| Error rate schema validation | < 0.1% | Revisar prompts de extracción |
| Precio fuera de rango esperado | Auto-detectar | Queue revisión humana |
| Latencia p95 | < 3 segundos | Optimizar o escalar |

### Comparativa: arquitectura actual Panelin vs propuesta

| Aspecto | Panelin Actual (Multi-agente) | Arquitectura Propuesta |
|---|---|---|
| **Patrón** | Múltiples agentes especializados | Single-agent con tools |
| **Cálculos** | Potencialmente por LLM | 100% código determinista |
| **KB Sync** | Manual/semi-manual | Webhooks Shopify automáticos |
| **Framework** | Python custom | LangGraph 1.0 |
| **Latencia** | Mayor (múltiples LLM calls) | Menor (1-2 LLM calls) |
| **Costo** | Mayor (agentes secuenciales) | ~60% menos |
| **Mantenibilidad** | Compleja | Herramientas versionables |
| **Precisión garantizada** | No | Sí (código determinista) |

### Roadmap de migración

**Fase 1 (Semana 1-2): Fundación**

- Consolidar JSON KB a single source of truth
- Implementar funciones de cálculo deterministas con tests
- Configurar webhooks Shopify básicos

**Fase 2 (Semana 3-4): Agente Core**

- Migrar a LangGraph 1.0 con tool definitions
- Configurar structured outputs para extracción de parámetros
- Implementar verificación dual-path

**Fase 3 (Semana 5-6): Producción**

- Testing con golden dataset (50+ casos reales)
- Configurar observabilidad (LangSmith/Langfuse)
- Deploy gradual con shadow testing vs sistema actual

**Fase 4 (Continuo): Optimización**

- Evaluar Qdrant para búsqueda semántica si necesario
- Optimizar modelo selection (GPT-4o-mini vs Gemini Flash)
- Caching de consultas frecuentes

### Documentación estructurada para mejora de archivos Panelin

```yaml
# panelin_improvement_guide.yaml
# Guía para AI agents que mejoren el sistema Panelin

architecture_principles:
  - LLM_NEVER_CALCULATES: "Todo cálculo matemático debe ejecutarse en funciones Python con tipo Decimal"
  - SINGLE_SOURCE_OF_TRUTH: "panelin_truth_bmcuruguay.json es la única fuente de precios"
  - DETERMINISTIC_FIRST: "Preferir herramientas deterministas sobre razonamiento LLM"
  - VALIDATE_EVERYTHING: "Cada output de cálculo debe pasar por verificación"

file_modifications:
  kb_training_system:
    action: "CONSOLIDATE"
    target: "panelin_truth_bmcuruguay.json"
    instructions: |
      - Eliminar archivos KB duplicados
      - Migrar todos los precios a formato standardizado
      - Agregar campo 'calculation_rules' por producto
      - Incluir 'last_sync' timestamp en cada producto

  gpt_consolidation_agent:
    action: "SIMPLIFY"
    instructions: |
      - Reducir a single-agent architecture
      - Convertir sub-agents a tool functions
      - Implementar structured output para extracción
      - Agregar validation layer post-extraction

  calculation_functions:
    action: "CREATE"
    location: "panelin/tools/quotation_calculator.py"
    instructions: |
      - Usar Decimal para toda aritmética financiera
      - Incluir type hints completos (TypedDict returns)
      - Cargar precios desde JSON KB, nunca hardcodear
      - Agregar 'calculation_verified: True' en outputs
      - Implementar unit tests para cada función

code_patterns:
  tool_definition: |
    # Ejemplo de herramienta correcta
    @tool
    def calculate_panel_quote(
        panel_type: Literal["Isopanel", "Isodec", "Isoroof"],
        thickness_mm: int,
        length_m: float,
        width_m: float,
        quantity: int,
        discount_percent: float = 0.0
    ) -> QuotationResult:
        """Cálculo determinista - LLM solo extrae parámetros"""
        # ... implementación con Decimal ...
        return result

  llm_configuration: |
    # Configuración óptima para precisión
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

  validation_pattern: |
    # Verificación post-cálculo
    def validate_quotation(result: QuotationResult) -> bool:
        assert result["calculation_verified"] is True
        assert result["total_usd"] > 0
        assert result["area_m2"] > 0
        # Verificar que total = sum(line_items)
        return True

testing_requirements:
  - minimum_golden_tests: 50
  - coverage_threshold: 95%
  - required_test_categories:
    - basic_calculations
    - discount_applications
    - edge_cases_dimensions
    - error_handling
    - shopify_sync_verification
```

### Estimaciones finales: costo, velocidad, precisión

| Métrica | Arquitectura Actual | Arquitectura Propuesta |
|---|---|---|
| **Costo por consulta** | ~$0.03-0.05 (multi-agente) | **$0.002-0.01** |
| **Latencia promedio** | 5-8 segundos | **1.5-3 segundos** |
| **Precisión cálculos** | Variable (LLM) | **100%** (código) |
| **Tiempo sync KB** | Manual | **Tiempo real** (webhooks) |
| **Mantenimiento mensual** | Alto | Bajo (automatizado) |

La arquitectura propuesta reduce costos **~70%**, mejora latencia **~60%**, y garantiza precisión **100%** en cotizaciones mediante la separación estricta de responsabilidades entre LLM (comprensión) y código (cálculo). La inversión de migración (estimada en 4-6 semanas) se recupera en aproximadamente 2-3 meses de operación por reducción de costos API y eliminación de errores de cotización.

## 1. Arquitectura de Capas (Layered Architecture)

### 1.1 Capa de Identidad y Personalidad (INAMOVIBLE)

**Función**: Define quién es Panelin y cómo se comporta.

```
┌─────────────────────────────────────────┐
│  IDENTIDAD FIJA                         │
│  - Nombre: Panelin                      │
│  - Rol: Experto técnico en cotizaciones │
│  - Personalización por usuario:          │
│    • Mauro → Respuesta única            │
│    • Martin → Respuesta única           │
│    • Rami → Respuesta única             │
└─────────────────────────────────────────┘
```

**Características**:
- Instrucciones del sistema que NO cambian
- Lógica condicional para usuarios específicos
- Estilo de comunicación (rioplatense, técnico pero accesible)
- **No se modifica** sin revisión exhaustiva

---

### 1.2 Capa de Conocimiento Base (Knowledge Base Layer)

**Función**: Almacenamiento estructurado de toda la información técnica y comercial.

#### Estructura Actual (7 archivos):

```
Knowledge Base/
│
├── PRIMARY SOURCE OF TRUTH
│   └── BMC_Base_Conocimiento_GPT.json ⭐ (MASTER)
│       - Productos, fórmulas, precios validados
│       - Reglas de negocio
│       - Especificaciones técnicas
│
├── VALIDATION & BACKUP
│   ├── BMC_Base_Unificada_v4.json
│   │   - Validado contra 31 presupuestos reales
│   │   - Usado para cross-reference
│   │
│   └── BMC_Catalogo_Completo_Shopify (1).json
│       - 73 productos con variantes
│       - Precios de Shopify
│
├── DYNAMIC DATA
│   └── panelin_truth_bmcuruguay_web_only_v2.json
│       - Snapshot público web
│       - Políticas de recrawl
│       - Refresh en tiempo real
│
├── WORKFLOW & PROCESS
│   └── panelin_context_consolidacion_sin_backend.md
│       - SOP de consolidación
│       - Comandos: /estado, /checkpoint, /consolidar
│       - Gestión de contexto
│
├── TECHNICAL RULES
│   └── Aleros.rtf
│       - Cálculos de voladizos
│       - Fórmulas de span efectivo
│
└── INDEX (Code Interpreter only)
    └── panelin_truth_bmcuruguay_catalog_v2_index.csv
        - Claves de productos
        - URLs Shopify
        - Estado de stock
```

#### Arquitectura Ideal Recomendada:

**Jerarquía de Prioridad**:
1. **Nivel 1 - Master**: `BMC_Base_Conocimiento_GPT.json`
   - Única fuente para precios y fórmulas
   - Siempre consultar primero
   - Si hay conflicto, este gana

2. **Nivel 2 - Validación**: `BMC_Base_Unificada_v4.json`
   - Cross-reference para verificación
   - Detección de inconsistencias
   - No usar para respuestas directas

3. **Nivel 3 - Dinámico**: `panelin_truth_bmcuruguay_web_only_v2.json`
   - Verificación de precios en tiempo real
   - Estado de stock
   - Refresh automático

4. **Nivel 4 - Soporte**: Resto de archivos
   - Reglas técnicas (Aleros.rtf)
   - Workflow (panelin_context_consolidacion_sin_backend.md)
   - Índices (CSV via Code Interpreter)

---

### 1.3 Capa de Recuperación (Retrieval Layer)

**Función**: Encontrar información relevante en la Knowledge Base de forma eficiente.

#### Estrategia Híbrida de Búsqueda:

```
┌─────────────────────────────────────────────┐
│  QUERY DEL USUARIO                          │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  BÚSQUEDA HÍBRIDA                           │
│                                              │
│  1. Búsqueda Semántica (Vector Search)      │
│     • Embeddings de la consulta             │
│     • Similaridad con chunks de KB          │
│     • Captura intención, no solo palabras   │
│                                              │
│  2. Búsqueda por Palabras Clave (Sparse)    │
│     • Términos técnicos exactos             │
│     • Códigos de producto (ISODEC_EPS)      │
│     • Números (espesores, precios)          │
│                                              │
│  3. Búsqueda Estructurada (JSON Path)      │
│     • Queries directas a JSON               │
│     • Filtros por tipo, espesor, precio    │
│                                              │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  RERANKING                                  │
│  • Relevancia semántica                     │
│  • Prioridad por fuente (Nivel 1 > 2 > 3)  │
│  • Frescura de datos                        │
│  • Confianza técnica                        │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  CONTEXTO ENSAMBLADO                        │
│  • Top N chunks relevantes                  │
│  • Metadatos (fuente, versión, fecha)      │
│  • Referencias cruzadas                     │
└──────────────────────────────────────────────┘
```

#### Chunking Inteligente:

**Estrategia Recomendada**:
- **Por estructura lógica**: Productos, fórmulas, reglas (no solo por tamaño)
- **Overlapping**: Fragmentos que se solapan ligeramente para preservar contexto
- **Metadatos ricos**: Cada chunk incluye:
  ```json
  {
    "chunk_id": "KB-ISODEC-EPS-100",
    "source_file": "BMC_Base_Conocimiento_GPT.json",
    "source_path": "products.ISODEC_EPS.espesores.100",
    "version": "5.0-Unified",
    "last_updated": "2026-01-16",
    "type": "product_spec",
    "tags": ["techo", "eps", "100mm", "autoportancia"],
    "confidence": 1.0
  }
  ```

---

### 1.4 Capa de Generación (Generation Layer)

**Función**: Producir respuestas precisas basadas en el contexto recuperado.

#### Pipeline de Generación:

```
┌─────────────────────────────────────────────┐
│  CONTEXTO RECUPERADO                        │
│  + Instrucciones del Sistema                │
│  + Personalidad (Panelin)                   │
│  + Memoria de Usuario                       │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  GUARDRAILS / VALIDACIÓN                    │
│  ✓ ¿La información está en KB?             │
│  ✓ ¿Es de fuente autorizada (Nivel 1)?     │
│  ✓ ¿Hay conflictos detectados?             │
│  ✓ ¿Cumple reglas de negocio?              │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  GENERACIÓN DE RESPUESTA                    │
│  • Modelo: GPT-5.2 Thinking (recomendado)  │
│  • Estilo: Consultivo, técnico, accesible  │
│  • Formato: Cotización estructurada        │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  POST-PROCESAMIENTO                        │
│  • Validación de fórmulas                  │
│  • Verificación de precios                 │
│  • Formato de salida (PDF si se solicita)  │
└──────────────────────────────────────────────┘
```

#### Guardrails Críticos:

1. **Source of Truth Enforcement**:
   ```
   SI pregunta sobre precio:
     → LEER SIEMPRE BMC_Base_Conocimiento_GPT.json primero
     → Si no está, buscar en Nivel 2
     → Si no está, decir "No tengo esa información"
     → NUNCA inventar precios
   ```

2. **Validación de Fórmulas**:
   ```
   SI calcula cotización:
     → Usar fórmulas de formulas_cotizacion
     → Validar autoportancia vs luz del cliente
     → Redondear según reglas (ROUNDUP)
     → Mostrar desglose completo
   ```

3. **Detección de Conflictos**:
   ```
   SI encuentra datos contradictorios:
     → Priorizar Nivel 1 (Master)
     → Reportar conflicto en respuesta
     → Sugerir verificación manual
   ```

---

### 1.5 Capa de Memoria y Personalización

**Función**: Recordar interacciones y personalizar respuestas.

#### Memoria de Usuario:

```
┌─────────────────────────────────────────────┐
│  MEMORIA POR USUARIO                        │
│                                              │
│  Usuario: Mauro                              │
│  - Personalización: Respuesta única         │
│  - Historial: [cotizaciones previas]        │
│  - Preferencias: [si las hay]               │
│                                              │
│  Usuario: Martin                             │
│  - Personalización: Respuesta única         │
│  - Historial: [cotizaciones previas]        │
│                                              │
│  Usuario: Rami                               │
│  - Personalización: Respuesta única         │
│  - Historial: [cotizaciones previas]        │
└──────────────────────────────────────────────┘
```

**Nota**: Las respuestas personalizadas son **siempre distintas**, guiadas por concepto, no scripted.

---

### 1.6 Capa de Orquestación (Orchestration Layer)

**Función**: Coordinar todas las capas y decidir el flujo de ejecución.

#### Flujo de Decisión:

```
USUARIO: "Necesito cotizar ISODEC 100mm para 6m de luz"

┌─────────────────────────────────────────────┐
│  1. IDENTIFICAR TIPO DE CONSULTA            │
│     → Cotización técnica                    │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  2. RECUPERAR INFORMACIÓN                   │
│     → Buscar ISODEC_EPS en KB               │
│     → Validar autoportancia 100mm           │
│     → Obtener precio de Nivel 1             │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  3. APLICAR FÓRMULAS                        │
│     → Calcular apoyos                       │
│     → Calcular puntos de fijación          │
│     → Calcular accesorios                   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  4. GENERAR RESPUESTA                      │
│     → Aplicar personalidad                  │
│     → Formatear cotización                  │
│     → Validar guardrails                    │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  5. ENTREGAR RESPUESTA                     │
│     → Texto estructurado                   │
│     → Opción PDF si se solicita             │
└──────────────────────────────────────────────┘
```

---

## 2. Arquitectura de Datos (Data Architecture)

### 2.1 Esquema de Prioridad de Fuentes

```
┌─────────────────────────────────────────────────┐
│  JERARQUÍA DE FUENTES DE VERDAD                │
└─────────────────────────────────────────────────┘

NIVEL 1 - MASTER (Autoridad Absoluta)
├── BMC_Base_Conocimiento_GPT.json
│   ├── Precios → SIEMPRE usar este
│   ├── Fórmulas → SIEMPRE usar este
│   ├── Especificaciones → SIEMPRE usar este
│   └── Reglas de negocio → SIEMPRE usar este
│
NIVEL 2 - VALIDACIÓN (Cross-Reference)
├── BMC_Base_Unificada_v4.json
│   └── Usar SOLO para detectar inconsistencias
│
NIVEL 3 - DINÁMICO (Tiempo Real)
├── panelin_truth_bmcuruguay_web_only_v2.json
│   └── Verificar precios actualizados
│
NIVEL 4 - SOPORTE (Contextual)
├── Aleros.rtf → Reglas técnicas específicas
├── panelin_context_consolidacion_sin_backend.md → Workflow
└── CSV (Code Interpreter) → Operaciones batch
```

### 2.2 Resolución de Conflictos

**Regla de Oro**: Si hay conflicto entre archivos, **Nivel 1 siempre gana**.

**Proceso de Detección**:
1. Al recuperar información, verificar si existe en múltiples fuentes
2. Si hay diferencia:
   - **Nivel 1 vs Nivel 2**: Usar Nivel 1, reportar diferencia
   - **Nivel 1 vs Nivel 3**: Usar Nivel 1, sugerir verificar web
   - **Nivel 2 vs Nivel 3**: Usar Nivel 1 (si existe), si no, reportar conflicto

**Ejemplo**:
```
CONFLICTO DETECTADO:
- BMC_Base_Conocimiento_GPT.json: ISODEC 100mm = $46.07
- BMC_Base_Unificada_v4.json: ISODEC 100mm = $46.0

ACCIÓN:
→ Usar $46.07 (Nivel 1)
→ Reportar: "Nota: Hay una pequeña diferencia con otra fuente, 
   usando el precio de la fuente maestra."
```

---

## 3. Arquitectura de Procesamiento (Processing Architecture)

### 3.1 Pipeline de Cotización

```
┌─────────────────────────────────────────────────┐
│  PIPELINE COMPLETO DE COTIZACIÓN                │
└─────────────────────────────────────────────────┘

ENTRADA: "Cotizar ISODEC 100mm, 6m luz, 4 paneles"

┌─────────────────────────────────────────────────┐
│  FASE 1: IDENTIFICACIÓN                         │
│  • Producto: ISODEC_EPS                         │
│  • Espesor: 100mm                                │
│  • Luz: 6m                                       │
│  • Cantidad: 4 paneles                           │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  FASE 2: VALIDACIÓN TÉCNICA                     │
│  • Consultar autoportancia 100mm = 5.5m         │
│  • Validar: 6m > 5.5m → ⚠️ NO CUMPLE           │
│  • Sugerir: 150mm (autoportancia 7.5m)          │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  FASE 3: RECUPERACIÓN DE DATOS                  │
│  • Precio: $46.07 (Nivel 1)                     │
│  • Ancho útil: 1.12m                            │
│  • Sistema fijación: varilla_tuerca             │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  FASE 4: CÁLCULOS                               │
│  • Apoyos: ROUNDUP((6/5.5)+1) = 3               │
│  • Puntos fijación: [fórmula compleja]          │
│  • Varillas: ROUNDUP(puntos/4)                  │
│  • Accesorios: [según tipo fijación]            │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  FASE 5: PRESENTACIÓN                           │
│  • Desglose detallado                           │
│  • Subtotal + IVA (22%)                         │
│  • Recomendaciones técnicas                      │
└──────────────────────────────────────────────────┘
```

### 3.2 Gestión de Contexto (SOP Integration)

**Comandos Integrados**:
- `/estado` → Resumen del Ledger + riesgo de contexto
- `/checkpoint` → Exportar snapshot actual
- `/consolidar` → Pack completo para ingestión

**Arquitectura de Contexto**:
```
┌─────────────────────────────────────────────────┐
│  CONTEXTO PERMANENTE                            │
│  • Ledger incremental                           │
│  • Historial de correcciones                    │
│  • Conflictos pendientes                        │
│  • TODOs de ingeniería                          │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  MONITOR DE RIESGO                              │
│  • Heurístico de tokens                         │
│  • Alertas automáticas                          │
│  • Recomendación de checkpoint                  │
└─────────────────────────────────────────────────┘
```

---

## 4. Arquitectura de Optimización

### 4.1 Estrategias de Indexación

**Recomendación**: Implementar indexación híbrida (semántica + keyword)

1. **Vector Database** (para búsqueda semántica):
   - Embeddings de chunks de KB
   - Búsqueda por similaridad
   - Captura intención del usuario

2. **Inverted Index** (para búsqueda exacta):
   - Términos técnicos: "ISODEC", "autoportancia", "100mm"
   - Códigos de producto: "ISODEC_EPS", "ISOROOF_3G"
   - Números y precios

3. **Structured Index** (para queries JSON):
   - Paths: `products.ISODEC_EPS.espesores.100`
   - Filtros: `tipo=cubierta_pesada`, `espesor>=100`

### 4.2 Caching Strategy

**Cache por Tipo de Consulta**:
- **Precios**: Cache de 1 hora (pueden cambiar)
- **Especificaciones técnicas**: Cache de 1 día (casi estático)
- **Fórmulas**: Cache permanente (no cambian)
- **Reglas de negocio**: Cache de 1 semana

**Invalidación**:
- Cuando se actualiza `BMC_Base_Conocimiento_GPT.json` → Invalidar todo
- Cuando se refresca web snapshot → Invalidar precios
- Manual: `/consolidar` → Invalidar y reconstruir

---

## 5. Arquitectura de Evaluación y Mejora

### 5.1 Métricas de Calidad

**Precisión**:
- % de respuestas que usan fuente correcta (Nivel 1)
- % de cotizaciones con fórmulas correctas
- % de conflictos detectados y resueltos

**Completitud**:
- % de consultas respondidas sin "no sé"
- Cobertura de productos en KB
- Detección de gaps de información

**Eficiencia**:
- Tiempo de respuesta promedio
- Tokens usados por consulta
- Tasa de uso de cache

### 5.2 Feedback Loop

```
┌─────────────────────────────────────────────────┐
│  CICLO DE MEJORA CONTINUA                       │
└─────────────────────────────────────────────────┘

1. INTERACCIÓN
   Usuario pregunta → Panelin responde

2. EVALUACIÓN
   • ¿Respuesta correcta?
   • ¿Usó fuente correcta?
   • ¿Fórmulas correctas?

3. FEEDBACK
   • Usuario corrige
   • Sistema detecta error
   • Se registra en Ledger

4. ACTUALIZACIÓN
   • Corrección en KB
   • Ajuste de instrucciones
   • Mejora de guardrails

5. VALIDACIÓN
   • Test con casos similares
   • Verificación de mejora
```

---

## 6. Recomendaciones de Implementación

### 6.1 Fase 1: Optimización Inmediata (Semana 1-2)

**Sin cambios a configuración inamovible**:

1. **Refinar Instrucciones del Sistema**:
   - Enfatizar jerarquía de fuentes
   - Mejorar guardrails de source of truth
   - Clarificar resolución de conflictos

2. **Organizar Knowledge Base**:
   - Documentar qué archivo usar para qué
   - Crear índice de contenido por archivo
   - Establecer naming conventions

3. **Mejorar Chunking**:
   - Revisar cómo se fragmentan los JSONs
   - Agregar metadatos a chunks
   - Optimizar overlapping

### 6.2 Fase 2: Mejoras Estructurales (Mes 1)

1. **Implementar Búsqueda Híbrida**:
   - Si es posible, agregar vector search
   - Mejorar búsqueda por keywords
   - Optimizar reranking

2. **Sistema de Cache**:
   - Implementar cache de consultas frecuentes
   - Invalidación inteligente
   - Métricas de hit rate

3. **Monitoreo y Logging**:
   - Registrar todas las consultas
   - Trackear uso de fuentes
   - Detectar patrones de error

### 6.3 Fase 3: Escalabilidad (Trimestre 1)

1. **Automatización**:
   - Refresh automático de web snapshot
   - Detección automática de conflictos
   - Alertas de datos obsoletos

2. **Integración Avanzada**:
   - Conexión directa con Shopify API (si es posible)
   - Sincronización automática de precios
   - Validación cruzada automática

---

## 7. Top Pro Tips para Arquitectura Perfecta

### ✅ DO's (Hacer)

1. **Mantener jerarquía de fuentes clara**: Nivel 1 siempre gana
2. **Usar metadatos ricos**: Cada chunk debe tener source, version, type
3. **Implementar guardrails estrictos**: Nunca inventar datos
4. **Cache inteligente**: Cachear lo estático, refrescar lo dinámico
5. **Monitoreo continuo**: Trackear qué funciona y qué no
6. **Chunking lógico**: Por estructura, no solo por tamaño
7. **Overlapping de chunks**: Preservar contexto entre fragmentos
8. **Validación post-generación**: Verificar fórmulas y precios
9. **Feedback loop activo**: Aprender de cada corrección
10. **Documentación viva**: Mantener KB actualizada y documentada

### ❌ DON'Ts (No Hacer)

1. **No inventar precios**: Si no está en KB, decir "no sé"
2. **No ignorar conflictos**: Siempre reportar y resolver
3. **No usar fuentes secundarias para respuestas directas**: Solo validación
4. **No fragmentar sin contexto**: Chunks deben tener sentido completo
5. **No cachear datos dinámicos por mucho tiempo**: Precios cambian
6. **No mezclar fuentes sin priorizar**: Siempre seguir jerarquía
7. **No generar respuestas sin validar guardrails**: Verificar siempre
8. **No ignorar feedback del usuario**: Cada corrección es valiosa
9. **No mantener datos obsoletos**: Archivar o actualizar
10. **No complicar innecesariamente**: Simplicidad cuando es posible

### ⚠️ PITFALLS (Trampas Comunes)

1. **Confiar en fuente incorrecta**: Siempre verificar nivel de prioridad
2. **Fragmentar demasiado**: Perder contexto importante
3. **Cachear demasiado tiempo**: Datos desactualizados
4. **Ignorar conflictos**: Pueden indicar problemas serios
5. **No validar fórmulas**: Errores de cálculo son críticos
6. **Personalización excesiva**: Mantener balance con precisión técnica
7. **Sobrecargar contexto**: Usar solo lo necesario
8. **No documentar cambios**: Perder trazabilidad

### 🚀 OPTIMIZACIONES (Performance)

1. **Búsqueda híbrida**: Semántica + keyword para mejor recall
2. **Reranking inteligente**: Priorizar por fuente y relevancia
3. **Cache estratégico**: Cachear consultas frecuentes
4. **Chunking optimizado**: Balance entre tamaño y contexto
5. **Lazy loading**: Cargar solo archivos necesarios
6. **Compresión de contexto**: Usar solo chunks relevantes
7. **Paralelización**: Búsquedas en múltiples fuentes simultáneas
8. **Indexación incremental**: Solo reindexar lo que cambia

---

## 8. Diagrama de Arquitectura Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           CAPA DE IDENTIDAD (INAMOVIBLE)                     │
│  • Panelin (personalidad)                                    │
│  • Personalización por usuario                               │
│  • Instrucciones del sistema                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              ORQUESTADOR                                     │
│  • Identificar tipo de consulta                              │
│  • Decidir flujo de ejecución                               │
│  • Coordinar capas                                          │
└──────────┬───────────────────────────────┬──────────────────┘
           │                               │
           ▼                               ▼
┌──────────────────────┐      ┌──────────────────────────────┐
│  RECUPERACIÓN        │      │  GENERACIÓN                  │
│  • Búsqueda híbrida  │      │  • LLM (GPT-5.2 Thinking)   │
│  • Reranking         │──────▶│  • Guardrails                │
│  • Context assembly  │      │  • Post-procesamiento       │
└──────────┬───────────┘      └──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│           KNOWLEDGE BASE (7 archivos)                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Nivel 1: BMC_Base_Conocimiento_GPT.json ⭐        │    │
│  │ Nivel 2: BMC_Base_Unificada_v4.json                │    │
│  │ Nivel 3: panelin_truth_bmcuruguay_web_only_v2.json │    │
│  │ Nivel 4: Aleros.rtf, SOP, CSV                      │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│           MEMORIA Y PERSONALIZACIÓN                          │
│  • Historial por usuario                                     │
│  • Preferencias                                              │
│  • Contexto de conversación                                  │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│           EVALUACIÓN Y FEEDBACK                              │
│  • Métricas de calidad                                       │
│  • Detección de errores                                      │
│  • Mejora continua                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Conclusión

Esta arquitectura ideal para Panelin está diseñada para:

✅ **Mantener lo inamovible**: Personalidad, usuarios específicos, archivos existentes
✅ **Optimizar lo mejorable**: Búsqueda, cache, validación, guardrails
✅ **Escalar a futuro**: Modularidad, monitoreo, mejora continua
✅ **Garantizar precisión**: Source of truth estricto, validación múltiple

**Próximos Pasos**:
1. Revisar y validar esta arquitectura
2. Implementar mejoras de Fase 1 (inmediatas)
3. Planificar Fase 2 y 3 según prioridades
4. Establecer métricas y monitoreo
5. Iterar y mejorar continuamente

---

**Documento creado**: 2026-01-16
**Versión**: 1.0
**Autor**: AI Configuration Architect
**Basado en**: Configuración actual de Panelin + Mejores prácticas RAG 2024-2025
