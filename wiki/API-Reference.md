# API Reference

Complete API reference for the Panelin AI System, including all public functions, classes, and their parameters.

---

## Table of Contents

1. [Quotation Agent API](#quotation-agent-api)
2. [Analysis Agent API](#analysis-agent-api)
3. [Orchestrator API](#orchestrator-api)
4. [Training System API](#training-system-api)
5. [KB Config Agent API](#kb-config-agent-api)
6. [Function Calling Schemas](#function-calling-schemas)

---

## Quotation Agent API

**Module:** `agente_cotizacion_panelin`

### Functions

#### `calcular_cotizacion_agente`

Calculate a complete quotation for construction panels.

```python
def calcular_cotizacion_agente(
    producto: str,
    espesor: str,
    largo: float,
    ancho: float,
    luz: float,
    tipo_fijacion: str = "hormigon",
    alero_1: float = 0,
    alero_2: float = 0
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `producto` | str | Yes | Product type (e.g., "ISODEC EPS", "ISOPANEL EPS") |
| `espesor` | str | Yes | Thickness in mm (e.g., "100", "150", "200") |
| `largo` | float | Yes | Length of area in meters |
| `ancho` | float | Yes | Width of area in meters |
| `luz` | float | Yes | Span between supports in meters |
| `tipo_fijacion` | str | No | Fixing type: "hormigon", "metal", "madera" |
| `alero_1` | float | No | Overhang at end 1 in meters |
| `alero_2` | float | No | Overhang at end 2 in meters |

**Returns:**

```python
{
    "success": bool,           # Whether calculation succeeded
    "error": str | None,       # Error message if failed
    "cotizacion": {
        "producto": str,
        "espesor": str,
        "dimensiones": {
            "largo": float,
            "ancho": float,
            "area": float
        },
        "validacion": {
            "autoportancia": float,
            "luz_efectiva": float,
            "cumple_autoportancia": bool,
            "advertencia": str | None
        },
        "materiales": Dict,
        "costos": {
            "subtotal": float,
            "iva": float,
            "total": float
        },
        "resumen": {
            "subtotal": float,
            "iva": float,
            "total": float,
            "moneda": "USD"
        }
    },
    "presentacion_texto": str  # Formatted text presentation
}
```

**Example:**

```python
from agente_cotizacion_panelin import calcular_cotizacion_agente

result = calcular_cotizacion_agente(
    producto="ISODEC EPS",
    espesor="100",
    largo=10.0,
    ancho=5.0,
    luz=4.5,
    tipo_fijacion="hormigon"
)

if result['success']:
    print(f"Total: ${result['cotizacion']['costos']['total']:.2f}")
```

---

#### `get_cotizacion_function_schema`

Get the Function Calling schema for AI integration.

```python
def get_cotizacion_function_schema() -> Dict
```

**Returns:** OpenAI-compatible function schema.

---

### Classes

#### `AgentePanelinOpenAI`

OpenAI-based quotation agent.

```python
class AgentePanelinOpenAI:
    def __init__(self, api_key: str, assistant_id: str = None)
    def crear_asistente(self) -> Assistant
    def procesar_mensaje(self, thread_id: str, mensaje: str) -> str
```

**Methods:**

| Method | Description |
|--------|-------------|
| `__init__` | Initialize with API key and optional assistant ID |
| `crear_asistente` | Create new OpenAI Assistant |
| `procesar_mensaje` | Process message and handle function calls |

---

#### `AgentePanelinClaude`

Claude-based quotation agent.

```python
class AgentePanelinClaude:
    def __init__(self, api_key: str)
    def chat(self, mensaje: str, model: str = "claude-3-5-sonnet-20241022") -> str
```

---

#### `AgentePanelinGemini`

Gemini-based quotation agent.

```python
class AgentePanelinGemini:
    def __init__(self, api_key: str)
    def chat(self, mensaje: str) -> str
```

---

## Analysis Agent API

**Module:** `agente_analisis_inteligente`

### Functions

#### `analizar_cotizacion_completa`

Analyze quotations, compare with real PDFs, and generate insights.

```python
def analizar_cotizacion_completa(
    cliente: str,
    producto: str,
    fecha: str = None,
    consulta: str = None
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cliente` | str | Yes | Client name or identifier |
| `producto` | str | Yes | Product type |
| `fecha` | str | No | Date filter (ISO format) |
| `consulta` | str | No | Original query text |

**Returns:**

```python
{
    "inputs": List[Dict],          # Reviewed inputs
    "presupuestos": List[Dict],    # Generated budgets
    "pdfs_encontrados": List[Dict], # Matching PDFs
    "datos_pdfs": List[Dict],      # Extracted PDF data
    "comparaciones": List[Dict],   # Comparisons
    "lecciones": List[Dict]        # Lessons learned
}
```

---

### Classes

#### `AgenteAnalisisInteligente`

Intelligent analysis agent for quotation review.

```python
class AgenteAnalisisInteligente:
    def __init__(self)
    def revisar_inputs(self, cliente: str = None, producto: str = None) -> List[Dict]
    def buscar_pdf_cotizacion(self, input_data: Dict) -> Dict | None
    def extraer_datos_pdf(self, pdf_path: str) -> Dict
    def comparar_resultados(self, presupuesto: Dict, pdf_real: Dict) -> Dict
```

---

## Orchestrator API

**Module:** `orquestador_multi_modelo`

### Enums

#### `TipoProcedimiento`

Available procedure types.

```python
class TipoProcedimiento(Enum):
    REVISION_INPUTS = "revision_inputs"
    GENERACION_PRESUPUESTO = "generacion_presupuesto"
    BUSQUEDA_PDF = "busqueda_pdf"
    EXTRACCION_DATOS = "extraccion_datos"
    COMPARACION = "comparacion"
    ANALISIS_DIFERENCIAS = "analisis_diferencias"
    APRENDIZAJE = "aprendizaje"
    COTIZACION_REALTIME = "cotizacion_realtime"
    VALIDACION_TECNICA = "validacion_tecnica"
    PRESENTACION = "presentacion"
```

#### `ModeloIA`

Available AI models.

```python
class ModeloIA(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    MOTOR_PYTHON = "motor_python"
```

---

### Classes

#### `OrquestadorMultiModelo`

Multi-model orchestrator.

```python
class OrquestadorMultiModelo:
    def __init__(self)
    def obtener_modelo_optimo(self, procedimiento: TipoProcedimiento) -> ModeloIA
    def ejecutar_procedimiento(
        self, 
        procedimiento: TipoProcedimiento, 
        **kwargs
    ) -> Dict[str, Any]
    def proceso_completo_inteligente(self, **kwargs) -> Dict[str, Any]
```

**Methods:**

| Method | Description |
|--------|-------------|
| `obtener_modelo_optimo` | Get optimal model for procedure |
| `ejecutar_procedimiento` | Execute procedure with optimal model |
| `proceso_completo_inteligente` | Run complete intelligent process |

**Example:**

```python
from orquestador_multi_modelo import OrquestadorMultiModelo, TipoProcedimiento

orchestrator = OrquestadorMultiModelo()

result = orchestrator.ejecutar_procedimiento(
    TipoProcedimiento.COTIZACION_REALTIME,
    mensaje="Cotiza ISODEC 100mm para 50m2"
)
```

---

## Training System API

**Module:** `kb_training_system`

### Classes

#### `KnowledgeBaseEvaluator`

Evaluate chatbot interactions.

```python
class KnowledgeBaseEvaluator:
    def __init__(self, knowledge_base_path: str)
    def evaluate_interaction(
        self,
        query: str,
        response: str,
        sources_consulted: List[str]
    ) -> EvaluationResult
    def benchmark_architecture(self, dataset: List[Dict]) -> BenchmarkResult
```

**EvaluationResult:**

```python
@dataclass
class EvaluationResult:
    relevance_score: float      # 0-1
    groundedness_score: float   # 0-1
    coherence_score: float      # 0-1
    source_compliance: float    # 0-1
    bleu_score: float          # 0-1
    precision: float
    recall: float
    f1: float
```

---

#### `KnowledgeBaseLeakDetector`

Detect knowledge base leaks.

```python
class KnowledgeBaseLeakDetector:
    def __init__(self, knowledge_base_path: str)
    def detect_leaks_in_interaction(
        self,
        query: str,
        response: str,
        sources_consulted: List[str]
    ) -> List[Leak]
    def detect_leaks_batch(self, interactions: List[Dict]) -> List[Leak]
    def analyze_leaks(self, leaks: List[Leak]) -> LeakAnalysis
```

**Leak:**

```python
@dataclass
class Leak:
    leak_type: str       # "missing_info", "incorrect_response", "source_mismatch", "coverage_gap"
    severity: str        # "critical", "high", "medium", "low"
    category: str
    description: str
    recommendation: str
```

---

#### `TrainingOrchestrator`

Coordinate training pipeline.

```python
class TrainingOrchestrator:
    def __init__(
        self,
        knowledge_base_path: str,
        quotes_path: str = None,
        interactions_path: str = None,
        social_data_path: str = None
    )
    def run_complete_pipeline(
        self,
        quotes: List[Dict] = None,
        interactions: List[Dict] = None,
        social_interactions: List[Dict] = None
    ) -> PipelineResult
    def export_pipeline_report(self, result: PipelineResult, output_path: str)
```

---

#### Training Levels

```python
# Level 1: Static Grounding
class Level1StaticGrounding:
    def __init__(self, knowledge_base_path: str)
    def train_from_quotes(self, quotes: List[Dict]) -> TrainingResult

# Level 2: Interaction-Driven
class Level2InteractionDriven:
    def __init__(self, knowledge_base_path: str)
    def train_from_interactions(self, interactions: List[Dict]) -> TrainingResult

# Level 3: Proactive Ingestion
class Level3ProactiveIngestion:
    def __init__(self, knowledge_base_path: str)
    def train_from_social(self, social_data: List[Dict]) -> TrainingResult

# Level 4: Autonomous Feedback
class Level4AutonomousFeedback:
    def __init__(self, knowledge_base_path: str)
    def run_optimization(self) -> OptimizationResult
```

---

## KB Config Agent API

**Module:** `gpt_kb_config_agent`

### Classes

#### `GPTKnowledgeBaseAgent`

Knowledge base configuration agent.

```python
class GPTKnowledgeBaseAgent:
    def __init__(
        self,
        knowledge_base_path: str,
        output_path: str = "gpt_configs/"
    )
    def analyze_and_review(self) -> AnalysisReport
    def configure_gpt(
        self,
        gpt_name: str,
        use_case: str = "assistant"
    ) -> GPTConfig
    def evolve_knowledge_base(
        self,
        strategy: str = "auto"
    ) -> EvolutionResult
    def validate_and_fix(self) -> ValidationResult
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `analyze_and_review` | None | AnalysisReport | Analyze KB structure |
| `configure_gpt` | gpt_name, use_case | GPTConfig | Generate GPT config |
| `evolve_knowledge_base` | strategy | EvolutionResult | Evolve KB |
| `validate_and_fix` | None | ValidationResult | Validate and fix issues |

**Example:**

```python
from gpt_kb_config_agent import GPTKnowledgeBaseAgent

agent = GPTKnowledgeBaseAgent(
    knowledge_base_path="Files/",
    output_path="gpt_configs/"
)

# Analyze
report = agent.analyze_and_review()
print(f"Health Score: {report.health_score}/100")

# Configure
config = agent.configure_gpt(
    gpt_name="Panelin Assistant",
    use_case="quotation"
)
```

---

## Function Calling Schemas

### Quotation Function Schema

```json
{
    "name": "calcular_cotizacion",
    "description": "Calcula una cotización completa para paneles ISODEC, ISOPANEL, ISOROOF o ISOWALL usando la base de conocimiento validada.",
    "parameters": {
        "type": "object",
        "properties": {
            "producto": {
                "type": "string",
                "enum": ["ISODEC EPS", "ISODEC PIR", "ISOPANEL EPS", "ISOROOF 3G", "ISOROOF PLUS", "ISOROOF FOIL", "ISOWALL PIR"],
                "description": "Tipo de producto a cotizar"
            },
            "espesor": {
                "type": "string",
                "description": "Espesor del panel en mm (ej: '100', '150', '200')"
            },
            "largo": {
                "type": "number",
                "description": "Largo del área a cubrir en metros"
            },
            "ancho": {
                "type": "number",
                "description": "Ancho del área a cubrir en metros"
            },
            "luz": {
                "type": "number",
                "description": "Distancia entre apoyos (luz) en metros. CRÍTICO para validar autoportancia."
            },
            "tipo_fijacion": {
                "type": "string",
                "enum": ["hormigon", "metal", "madera"],
                "description": "Tipo de fijación"
            },
            "alero_1": {
                "type": "number",
                "description": "Alero en extremo 1 en metros (opcional)",
                "default": 0
            },
            "alero_2": {
                "type": "number",
                "description": "Alero en extremo 2 en metros (opcional)",
                "default": 0
            }
        },
        "required": ["producto", "espesor", "largo", "ancho", "luz", "tipo_fijacion"]
    }
}
```

### Analysis Function Schema

```json
{
    "name": "analizar_cotizacion_completa",
    "description": "Analiza cotizaciones históricas, compara con PDFs reales, genera presupuestos y aprende de las diferencias.",
    "parameters": {
        "type": "object",
        "properties": {
            "cliente": {
                "type": "string",
                "description": "Nombre o identificador del cliente"
            },
            "producto": {
                "type": "string",
                "description": "Tipo de producto a analizar"
            },
            "fecha": {
                "type": "string",
                "description": "Filtro de fecha (formato ISO)"
            },
            "consulta": {
                "type": "string",
                "description": "Texto de la consulta original"
            }
        },
        "required": ["cliente", "producto"]
    }
}
```

---

## Error Handling

All API functions return consistent error structures:

```python
# Success response
{
    "success": True,
    "error": None,
    "data": {...}
}

# Error response
{
    "success": False,
    "error": "Error description",
    "data": None
}
```

### Common Error Codes

| Error | Description | Solution |
|-------|-------------|----------|
| `ModuleNotFoundError` | Missing dependency | Install with pip |
| `API key not found` | Missing environment variable | Set in .env file |
| `Product not found` | Product not in KB | Check KB files |
| `Autoportancia exceeded` | Span too large | Use larger thickness |

---

## Related Documentation

- [[Getting-Started]] - Installation and setup
- [[Agents-Overview]] - Agent documentation
- [[Troubleshooting]] - Common issues

---

<p align="center">
  <a href="[[Multi-Model-Orchestration]]">← Multi-Model Orchestration</a> |
  <a href="[[Configuration]]">Configuration →</a>
</p>
