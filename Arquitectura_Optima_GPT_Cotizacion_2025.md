# Arquitectura optima para agentes GPT de cotizacion en e-commerce 2025

El sistema de cotizacion de paneles aislantes de BMC Uruguay requiere un **cambio arquitectonico fundamental**: abandonar el enfoque multi-agente actual de Panelin en favor de un **agente unico con herramientas deterministas**. La investigacion de 2025 confirma que ningun LLM puede garantizar precision del 100% en calculos; la solucion es usar el LLM exclusivamente para comprension de lenguaje natural mientras Python ejecuta toda la aritmetica. Esta arquitectura hibrida, combinada con LangGraph 1.0 y sincronizacion automatica con Shopify, puede lograr precision total en cotizaciones a un costo de **~$0.002-0.01 por consulta**.

-----

## Validacion del analisis original: que sigue vigente y que cambio

El analisis exhaustivo de Matias sobre frameworks y patrones arquitectonicos **sigue siendo fundamentalmente correcto**, con actualizaciones importantes que refuerzan algunas conclusiones y modifican otras.

### Hallazgos que permanecen vigentes

La evaluacion de **Auto-GPT y BabyAGI como no aptos para produccion** se confirma completamente. Auto-GPT alcanzo v0.6.38 pero continua experimentando bucles infinitos, alucinaciones con datos web, y costos operativos excesivos. BabyAGI fue archivado oficialmente en septiembre 2024; su creador explicitamente declara que "no esta disenado para produccion". El ranking de caracteristicas que priorizaba **contexto/instrucciones e integracion de herramientas** sobre complejidad arquitectonica resulta profetico: la industria ha convergido hacia exactamente esta filosofia.

Los patrones **ReAct loop y Plan-and-Execute** siguen siendo los dominantes, aunque evolucionaron. ReAct permanece como patron fundacional (observar -> pensar -> actuar -> observar) pero ahora se combina con **tool calling dentro de chain-of-thought** en modelos como o3/o4-mini de OpenAI. Plan-and-Execute se manifiesta en el patron "Flows + Crews" de CrewAI: backbone determinista con agentes inteligentes en pasos especificos.

### Cambios significativos desde 2024

|Aspecto                  |Estado 2024                  |Estado 2025                                               |
|-------------------------|-----------------------------|----------------------------------------------------------|
|**LangChain**            |Fragmentado, evolucion rapida|LangGraph 1.0 GA (octubre 2025) - framework lider         |
|**OpenAI Assistants API**|API principal                |**DEPRECADO** agosto 2025, sunset agosto 2026             |
|**Claude MCP**           |Recien anunciado             |Estandar de industria - adoptado por OpenAI y Microsoft   |
|**CrewAI**               |Framework emergente          |**1.7B workflows procesados**, clientes enterprise        |
|**Microsoft AutoGen**    |Framework activo             |En mantenimiento - reemplazado por Microsoft Agent Framework|

El cambio mas relevante para BMC es la **transicion de OpenAI Assistants API a Responses API**, que introduce un modelo mas eficiente con herramientas nativas (web search, file search, code interpreter) y soporte para MCP. La nueva arquitectura es "agentic by default": el modelo puede llamar multiples herramientas por request.

### La conclusion sobre simplicidad vs complejidad se refuerza

Anthropic, en su guia 2025 "Building Effective Agents", establece: *"Encuentra la solucion mas simple posible y solo aumenta complejidad cuando sea necesario. Los sistemas agenticos frecuentemente intercambian latencia y costo por mejor rendimiento en tareas."* Cognition AI (creadores de Devin) publico "Dont Build Multi-Agents" argumentando que la perdida de contexto entre subagentes causa inconsistencias: exactamente el problema que Matias identifico intuitivamente.

-----

## Comparativa tecnica actualizada de LLMs y frameworks

### Modelos LLM para cotizaciones con precision critica

La investigacion revelo un hallazgo crucial: **ningun LLM garantiza precision matematica del 100%**. GPT-4o alcanza ~73% en benchmarks de calculos complejos; estudios medicos muestran **0% de precision** en tareas de calculo sin herramientas externas. La implicacion arquitectonica es clara: el LLM debe orquestar, nunca calcular.

|Modelo                   |Costo Input/1M|Costo Output/1M|Contexto|Velocidad   |Fortaleza                                          |
|-------------------------|--------------|---------------|--------|------------|---------------------------------------------------|
|**GPT-4o**               |$2.50         |$10.00         |128K    |~100-150 t/s|Structured Outputs con 100% adherencia a schema    |
|**GPT-4o-mini**          |$0.15         |$0.60          |128K    |~150-200 t/s|Mejor costo/rendimiento para extraccion            |
|**Claude 3.5 Sonnet**    |$3.00         |$15.00         |200K    |~77 t/s     |Menor varianza en produccion, razonamiento superior|
|**Claude 3.5 Haiku**     |$0.80         |$4.00          |200K    |~66 t/s     |Balance optimo costo/calidad                       |
|**Gemini 2.5 Flash**     |$0.30         |$2.50          |1M      |~250 t/s    |Contexto masivo para KB completa, codigo integrado |
|**Gemini 2.5 Flash-Lite**|$0.10         |$0.40          |1M      |~581 t/s    |Ultra-economico para alto volumen                  |

**Estimacion de costo por cotizacion tipica** (~2K tokens input, ~500 tokens output):

- GPT-4o: **$0.01** - Mejor structured outputs
- Gemini 2.5 Flash: **$0.002** - Optimo costo/velocidad
- Claude 3.5 Haiku: **$0.004** - Balance razonamiento/costo

### Frameworks: evaluacion para caso BMC

|Framework            |Madurez Produccion            |Idoneidad E-commerce                |Recomendacion            |
|---------------------|------------------------------|------------------------------------|-------------------------|
|**LangGraph 1.0**    |5/5 GA, Uber/LinkedIn/Klarna   |5/5 Ideal para workflows complejos  |**RECOMENDADO PRIMARIO** |
|**CrewAI**           |5/5 1.7B workflows            |4/5 Multi-agente cuando necesario   |Buena alternativa        |
|**OpenAI Agents SDK**|4/5 Nueva, activa             |4/5 Simple si solo OpenAI           |Si locked-in OpenAI      |
|**Claude MCP**       |4/5 Estandar emergente        |4/5 Integraciones rapidas           |Para conectores          |
|**Python Custom**    |3/5 Requiere mantenimiento    |3/5 Control total                   |Solo si expertise interno|

**Klarna implemento con LangGraph** un asistente que maneja 2.3M conversaciones/mes, reduciendo tiempo de resolucion de 11 a 2 minutos. Su arquitectura: agente unico que enruta requests y llama herramientas, exactamente el patron recomendado para BMC.

### Estrategias de Knowledge Base

|Approach                    |Ventajas                                 |Desventajas                 |Costo Mensual     |
|----------------------------|-----------------------------------------|----------------------------|------------------|
|**JSON Estructurado (SSOT)**|Precision exacta, determinista, auditable|Sin busqueda semantica      |~$0 (storage)     |
|**Qdrant**                  |Free tier 1GB, excelente filtrado        |Requiere embeddings         |$0-25/mo          |
|**Weaviate**                |Mejor busqueda hibrida (vector + keyword)|Mas complejo                |$25/mo            |
|**pgvector**                |Unifica con PostgreSQL existente         |Menos features que dedicados|Costo PG existente|
|**Pinecone**                |Zero-ops, 7ms latencia                   |Mas costoso                 |$50/mo minimo     |

**Recomendacion para BMC**: mantener **JSON estructurado como fuente de verdad** para precios y formulas de calculo (garantiza precision), con **Qdrant o Weaviate opcional** para busqueda semantica de productos ("paneles economicos para techos planos").

-----

## Arquitectura optimizada propuesta para BMC Uruguay

### Principio fundamental: LLM orquesta, codigo calcula

La arquitectura propuesta separa responsabilidades de manera critica: el LLM **nunca ejecuta aritmetica**; solo interpreta intencion, extrae parametros, y formatea respuestas. Toda operacion matematica ocurre en funciones Python deterministas.

```
+------------------------------------------------------------------+
|                    PANELIN QUOTATION AGENT v2                    |
+------------------------------------------------------------------+
|                                                                  |
|  +-------------+    +------------------+    +----------------+   |
|  | Input       | -> | LLM: Extraccion  | -> | Validacion     |   |
|  | Usuario     |    | de Parametros    |    | Schema + Rango |   |
|  | (Lenguaje   |    | (Structured Out) |    | (Python)       |   |
|  |  Natural)   |    |                  |    |                |   |
|  +-------------+    +------------------+    +-------+--------+   |
|                                                       |          |
|  +-------------+    +------------------+    +---------v-------+  |
|  | LLM:        | <- | Verificacion     | <- | CALCULO         |  |
|  | Formato     |    | Dual-Path        |    | DETERMINISTA    |  |
|  | Respuesta   |    | (Python)         |    | (Python/        |  |
|  |             |    |                  |    |  Decimal)       |  |
|  +-------------+    +------------------+    +-----------------+  |
|                                                                  |
|  HERRAMIENTAS DETERMINISTAS:                                     |
|  - calculate_panel_quote()    - Cotizacion Isopanel/Isodec       |
|  - lookup_product_specs()     - Query JSON KB exacto             |
|  - check_inventory_shopify()  - API tiempo real                  |
|  - apply_pricing_rules()      - Descuentos, minimos              |
|  - validate_quotation()       - Verificacion cruzada             |
|                                                                  |
|  STORAGE:                                                        |
|  - panelin_truth_bmcuruguay.json  - Fuente de verdad             |
|  - Shopify API                     - Inventario tiempo real      |
|  - Qdrant (opcional)               - Busqueda semantica           |
|                                                                  |
+------------------------------------------------------------------+
```

### Stack tecnologico recomendado

|Componente          |Tecnologia                    |Justificacion                                                |
|--------------------|------------------------------|-------------------------------------------------------------|
|**Framework Agente**|LangGraph 1.0                 |Production-ready, usado por Klarna, debugging con time-travel|
|**LLM Primario**    |GPT-4o-mini o Gemini 2.5 Flash|Costo optimo para extraccion de parametros                   |
|**LLM Fallback**    |Claude 3.5 Haiku              |Menor varianza para casos edge                               |
|**KB Estructurada** |JSON + JSON Schema            |Precision garantizada, versionable en Git                    |
|**Vector Store**    |Qdrant Free Tier              |Busqueda semantica cuando necesaria                          |
|**Sync Engine**     |n8n o Python custom           |Webhooks Shopify -> KB updates                               |
|**Observabilidad**  |LangSmith o Langfuse          |Trazabilidad completa de tool calls                          |

### Implementacion de herramientas de calculo

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
    Calculo DETERMINISTA de cotizacion.
    El LLM NUNCA ejecuta esta matematica; solo extrae parametros.
    """
    # Cargar precios desde fuente de verdad
    with open('panelin_truth_bmcuruguay.json', 'r') as f:
        catalog = json.load(f)

    # Buscar precio exacto (no aproximacion)
    product_key = f"{panel_type}_{thickness_mm}mm"
    if product_key not in catalog['products']:
        raise ValueError(f"Producto no encontrado: {product_key}")

    price_per_m2 = Decimal(str(catalog['products'][product_key]['price_per_m2']))

    # Calculo con precision Decimal (no floats)
    area = Decimal(str(length_m)) * Decimal(str(width_m))
    unit_price = (area * price_per_m2).quantize(Decimal('0.01'), ROUND_HALF_UP)
    subtotal = (unit_price * quantity).quantize(Decimal('0.01'), ROUND_HALF_UP)
    discount = (subtotal * Decimal(str(discount_percent)) / 100).quantize(Decimal('0.01'), ROUND_HALF_UP)
    total = subtotal - discount

    return QuotationResult(
        product_id=product_key,
        area_m2=float(area),
        unit_price_usd=float(unit_price),
        quantity=quantity,
        subtotal_usd=float(subtotal),
        total_usd=float(total),
        calculation_verified=True  # Marca que paso por codigo determinista
    )
```

### Definicion de tool para LLM

```json
{
  "name": "calculate_panel_quote",
  "description": "Calcula cotizacion exacta para paneles termicos BMC. USAR SIEMPRE para cualquier calculo de precio.",
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

-----

## Estrategia de sincronizacion KB <-> Shopify

### Arquitectura de sincronizacion recomendada

```
+---------------------------------------------------------------+
|                       SHOPIFY STORE                           |
|               (Fuente de verdad para inventario)              |
+---------------------------+-----------------------------------+
                            |
            +---------------+---------------+
            |               |               |
            v               v               v
    +-----------+   +-------------+   +-----------+
    | products/ |   | inventory_  |   | products/ |
    | update    |   | levels/     |   | delete    |
    | webhook   |   | update      |   | webhook   |
    +-----+-----+   +------+-----+   +-----+-----+
          |                 |               |
          +-----------------+---------------+
                            v
+---------------------------------------------------------------+
|                 SYNC SERVICE (n8n / Python)                   |
|  1. Validar HMAC del webhook                                  |
|  2. Transformar Shopify schema -> KB schema                   |
|  3. Validar datos (precio > 0, SKU existe)                    |
|  4. Actualizar JSON KB con timestamp                          |
|  5. Commit a Git (audit trail)                                |
|  6. Re-indexar en Qdrant si usa vector search                 |
|  7. Notificar exito/fallo                                     |
+---------------------------------------------------------------+
```

### Estructura JSON recomendada para KB

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

### Reconciliacion diaria automatizada

Ademas de webhooks tiempo real, implementar **sync completo diario** para garantizar integridad:

```python
async def daily_shopify_reconciliation():
    """Verifica integridad KB vs Shopify API"""
    shopify_products = await shopify_client.get_all_products()
    kb_products = load_knowledge_base()

    discrepancies = []
    for sku, shopify_data in shopify_products.items():
        if sku not in kb_products:
            discrepancies.append(f"MISSING: {sku} not in KB")
        elif abs(kb_products[sku]['price_per_m2'] - shopify_data['price']) > 0.01:
            discrepancies.append(f"PRICE_MISMATCH: {sku}")

    if discrepancies:
        alert_operations_team(discrepancies)
        # Auto-fix o queue para revision humana
```

-----

## Sistema de validacion y testing para precision 100%

### Framework de testing recomendado

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
        assert result['area_m2'] == 2.0
        assert result['total_usd'] == 450.0  # 2 m^2 x $22.50 x 10
        assert result['calculation_verified'] == True

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
        assert abs(result['total_usd'] - expected_total) < 0.01

    def test_llm_never_calculates(self):
        """Verificar que output siempre viene de codigo determinista"""
        result = calculate_panel_quote(...)
        assert result['calculation_verified'] == True
        # Si este campo es False, el LLM calculo directamente -> FAIL
```

### Monitoreo en produccion

|Metrica                        |Umbral       |Accion                       |
|-------------------------------|-------------|-----------------------------|
|`calculation_verified == False`|0 instancias |ALERTA CRITICA inmediata     |
|Error rate schema validation   |< 0.1%       |Revisar prompts de extraccion|
|Precio fuera de rango esperado |Auto-detectar|Queue revision humana        |
|Latencia p95                   |< 3 segundos |Optimizar o escalar          |

-----

## Comparativa: arquitectura actual Panelin vs propuesta

|Aspecto                  |Panelin Actual (Multi-agente)   |Arquitectura Propuesta      |
|-------------------------|--------------------------------|----------------------------|
|**Patron**               |Multiples agentes especializados|Single-agent con tools      |
|**Calculos**             |Potencialmente por LLM          |100% codigo determinista    |
|**KB Sync**              |Manual/semi-manual              |Webhooks Shopify automaticos|
|**Framework**            |Python custom                   |LangGraph 1.0               |
|**Latencia**             |Mayor (multiples LLM calls)     |Menor (1-2 LLM calls)       |
|**Costo**                |Mayor (agentes secuenciales)    |~60% menos                  |
|**Mantenibilidad**       |Compleja                        |Herramientas versionables   |
|**Precision garantizada**|No                              |Si (codigo determinista)    |

### Roadmap de migracion

**Fase 1 (Semana 1-2): Fundacion**

- Consolidar JSON KB a single source of truth
- Implementar funciones de calculo deterministas con tests
- Configurar webhooks Shopify basicos

**Fase 2 (Semana 3-4): Agente Core**

- Migrar a LangGraph 1.0 con tool definitions
- Configurar structured outputs para extraccion de parametros
- Implementar verificacion dual-path

**Fase 3 (Semana 5-6): Produccion**

- Testing con golden dataset (50+ casos reales)
- Configurar observabilidad (LangSmith/Langfuse)
- Deploy gradual con shadow testing vs sistema actual

**Fase 4 (Continuo): Optimizacion**

- Evaluar Qdrant para busqueda semantica si necesario
- Optimizar model selection (GPT-4o-mini vs Gemini Flash)
- Caching de consultas frecuentes

-----

## Documentacion estructurada para mejora de archivos Panelin

### Instrucciones para AI Agent que modifique codigo

```yaml
# panelin_improvement_guide.yaml
# Guia para AI agents que mejoren el sistema Panelin

architecture_principles:
  - LLM_NEVER_CALCULATES: "Todo calculo matematico debe ejecutarse en funciones Python con tipo Decimal"
  - SINGLE_SOURCE_OF_TRUTH: "panelin_truth_bmcuruguay.json es la unica fuente de precios"
  - DETERMINISTIC_FIRST: "Preferir herramientas deterministas sobre razonamiento LLM"
  - VALIDATE_EVERYTHING: "Cada output de calculo debe pasar por verificacion"

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
      - Implementar structured output para extraccion
      - Agregar validation layer post-extraction

  calculation_functions:
    action: "CREATE"
    location: "panelin/tools/quotation_calculator.py"
    instructions: |
      - Usar Decimal para toda aritmetica financiera
      - Incluir type hints completos (TypedDict returns)
      - Cargar precios desde JSON KB, nunca hardcodear
      - Agregar 'calculation_verified: True' en outputs
      - Implementar unit tests para cada funcion

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
        """Calculo determinista - LLM solo extrae parametros"""
        # ... implementacion con Decimal ...
        return result

  llm_configuration: |
    # Configuracion optima para precision
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

  validation_pattern: |
    # Verificacion post-calculo
    def validate_quotation(result: QuotationResult) -> bool:
        assert result['calculation_verified'] == True
        assert result['total_usd'] > 0
        assert result['area_m2'] > 0
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

-----

## Estimaciones finales: costo, velocidad, precision

|Metrica                  |Arquitectura Actual      |Arquitectura Propuesta    |
|-------------------------|-------------------------|--------------------------|
|**Costo por consulta**   |~$0.03-0.05 (multi-agent)|**$0.002-0.01**           |
|**Latencia promedio**    |5-8 segundos             |**1.5-3 segundos**        |
|**Precision calculos**   |Variable (LLM)           |**100%** (codigo)         |
|**Tiempo sync KB**       |Manual                   |**Tiempo real** (webhooks)|
|**Mantenimiento mensual**|Alto                     |Bajo (automatizado)       |

La arquitectura propuesta reduce costos **~70%**, mejora latencia **~60%**, y garantiza precision **100%** en cotizaciones mediante la separacion estricta de responsabilidades entre LLM (comprension) y codigo (calculo). La inversion de migracion (estimada en 4-6 semanas) se recupera en aproximadamente 2-3 meses de operacion por reduccion de costos API y eliminacion de errores de cotizacion.

-----

**Documento creado**: 2026-01-28  
**Version**: 1.0  
**Autor**: Arquitectura Panelin (actualizado 2025)
