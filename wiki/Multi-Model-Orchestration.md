# Multi-Model Orchestration

The Panelin system uses a sophisticated multi-model orchestration layer that routes tasks to the most appropriate AI model based on the procedure type, availability, and performance characteristics.

---

## Table of Contents

1. [Overview](#overview)
2. [Model Assignment Matrix](#model-assignment-matrix)
3. [Orchestrator Architecture](#orchestrator-architecture)
4. [Procedure Types](#procedure-types)
5. [Model Handlers](#model-handlers)
6. [Fallback System](#fallback-system)
7. [Usage Guide](#usage-guide)

---

## Overview

The Multi-Model Orchestrator (`orquestador_multi_modelo.py`) intelligently assigns tasks to the optimal AI model based on:

- **Procedure type**: What kind of task is being performed
- **Model strengths**: Each model's unique capabilities
- **Availability**: Which API keys are configured
- **Priority**: How critical the task is

### Key Benefits

| Benefit | Description |
|---------|-------------|
| **Optimal Performance** | Each task uses the best model for that specific job |
| **Fault Tolerance** | Automatic fallback when primary model unavailable |
| **Cost Optimization** | Use cheaper models for appropriate tasks |
| **Flexibility** | Easy to add new models or modify assignments |

---

## Model Assignment Matrix

The orchestrator uses a predefined assignment matrix to route tasks:

| Procedure | Primary Model | Alternative | Priority | Reason |
|-----------|---------------|-------------|----------|--------|
| **Real-time Quotation** | OpenAI | Claude | Critical | Native Function Calling integration |
| **Budget Generation** | OpenAI | Motor Python | Critical | Code Interpreter for precise calculations |
| **PDF Search** | Claude | OpenAI | Medium | Excellent reasoning for intelligent matching |
| **Data Extraction** | OpenAI | Gemini | High | Code Interpreter for complex parsing, multimodal |
| **Comparison** | OpenAI | Motor Python | High | Code Interpreter for precise calculations |
| **Difference Analysis** | Claude | OpenAI | Medium | Deep reasoning, cause identification |
| **Learning** | Claude | OpenAI | Low | Excellent synthesis, insight generation |
| **Technical Validation** | OpenAI | Motor Python | Critical | Mathematical validation |
| **Presentation** | Claude | OpenAI | Medium | Natural communication, professional formatting |

### Visual Representation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MODEL ASSIGNMENT MATRIX                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CRITICAL TASKS ────────────────────────────────────────────────────────   │
│  ├─ Quotation Real-time ──────────▶ OpenAI (Function Calling)              │
│  ├─ Budget Generation ────────────▶ OpenAI (Code Interpreter)              │
│  └─ Technical Validation ─────────▶ OpenAI (Mathematical)                  │
│                                                                              │
│  HIGH PRIORITY TASKS ───────────────────────────────────────────────────   │
│  ├─ Input Revision ───────────────▶ OpenAI (Structured Parsing)            │
│  ├─ Data Extraction ──────────────▶ OpenAI (Complex Parsing)               │
│  └─ Comparison ───────────────────▶ OpenAI (Precise Calculations)          │
│                                                                              │
│  MEDIUM PRIORITY TASKS ─────────────────────────────────────────────────   │
│  ├─ PDF Search ───────────────────▶ Claude (Intelligent Matching)          │
│  ├─ Difference Analysis ──────────▶ Claude (Deep Reasoning)                │
│  └─ Presentation ─────────────────▶ Claude (Natural Communication)         │
│                                                                              │
│  LOW PRIORITY TASKS ────────────────────────────────────────────────────   │
│  └─ Learning ─────────────────────▶ Claude (Synthesis, Insights)           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Orchestrator Architecture

### Class Structure

```python
class OrquestadorMultiModelo:
    """Routes tasks to optimal AI models"""
    
    # Assignment definitions
    ASIGNACIONES = {
        TipoProcedimiento.COTIZACION_REALTIME: AsignacionModelo(
            procedimiento=TipoProcedimiento.COTIZACION_REALTIME,
            modelo_principal=ModeloIA.OPENAI,
            modelo_alternativo=ModeloIA.CLAUDE,
            prioridad="critica",
            razon="Function Calling nativo, integración perfecta"
        ),
        # ... more assignments
    }
    
    def __init__(self):
        self.openai_agente = None
        self.claude_agente = None
        self.gemini_agente = None
        self.analisis_agente = None
        self._inicializar_agentes()
    
    def obtener_modelo_optimo(self, procedimiento: TipoProcedimiento) -> ModeloIA:
        """Get optimal model for a procedure"""
        pass
    
    def ejecutar_procedimiento(self, procedimiento: TipoProcedimiento, **kwargs) -> Dict:
        """Execute procedure using optimal model"""
        pass
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        ASSIGNMENT MATRIX                               │  │
│  │   Procedure Type ─────▶ Primary Model + Alternative + Priority        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      MODEL AVAILABILITY CHECK                          │  │
│  │   Check API key ─────▶ Initialize agent ─────▶ Mark available         │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │   OpenAI    │   │   Claude    │   │   Gemini    │   │   Motor     │     │
│  │   Handler   │   │   Handler   │   │   Handler   │   │   Python    │     │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘     │
│         │                │                │                │                │
│         └────────────────┴────────────────┴────────────────┘                │
│                                    │                                         │
│                                    ▼                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                           RESULT                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Procedure Types

### Available Procedures

```python
class TipoProcedimiento(Enum):
    """Types of procedures in the system"""
    REVISION_INPUTS = "revision_inputs"         # Review input data
    GENERACION_PRESUPUESTO = "generacion_presupuesto"  # Generate budget
    BUSQUEDA_PDF = "busqueda_pdf"               # Search for PDFs
    EXTRACCION_DATOS = "extraccion_datos"       # Extract data
    COMPARACION = "comparacion"                 # Compare results
    ANALISIS_DIFERENCIAS = "analisis_diferencias"  # Analyze differences
    APRENDIZAJE = "aprendizaje"                 # Learning
    COTIZACION_REALTIME = "cotizacion_realtime" # Real-time quotation
    VALIDACION_TECNICA = "validacion_tecnica"   # Technical validation
    PRESENTACION = "presentacion"               # Presentation
```

### Procedure Details

#### COTIZACION_REALTIME (Real-time Quotation)
- **Primary**: OpenAI
- **Priority**: Critical
- **Description**: Real-time customer quotation requests
- **Why OpenAI**: Native Function Calling for seamless tool integration

#### GENERACION_PRESUPUESTO (Budget Generation)
- **Primary**: OpenAI
- **Priority**: Critical
- **Description**: Detailed budget calculation
- **Why OpenAI**: Code Interpreter for precise mathematical calculations

#### BUSQUEDA_PDF (PDF Search)
- **Primary**: Claude
- **Priority**: Medium
- **Description**: Find matching PDF documents
- **Why Claude**: Excellent reasoning for intelligent document matching

#### ANALISIS_DIFERENCIAS (Difference Analysis)
- **Primary**: Claude
- **Priority**: Medium
- **Description**: Analyze discrepancies between expected and actual results
- **Why Claude**: Deep reasoning capability for root cause identification

#### APRENDIZAJE (Learning)
- **Primary**: Claude
- **Priority**: Low
- **Description**: Extract insights and lessons from comparisons
- **Why Claude**: Strong synthesis and insight generation

---

## Model Handlers

### OpenAI Handler

Handles procedures best suited for OpenAI's capabilities:

```python
def _ejecutar_openai(self, procedimiento: TipoProcedimiento, **kwargs) -> Dict:
    """Execute procedure with OpenAI"""
    handlers = {
        TipoProcedimiento.COTIZACION_REALTIME: self._cotizacion_openai,
        TipoProcedimiento.VALIDACION_TECNICA: self._validacion_openai,
        TipoProcedimiento.GENERACION_PRESUPUESTO: self._generacion_openai,
    }
    
    handler = handlers.get(procedimiento)
    if handler:
        return handler(**kwargs)
    
    # Fallback to Python motor
    return self._ejecutar_motor_python(procedimiento, **kwargs)
```

### Claude Handler

Handles procedures requiring deep reasoning:

```python
def _ejecutar_claude(self, procedimiento: TipoProcedimiento, **kwargs) -> Dict:
    """Execute procedure with Claude"""
    handlers = {
        TipoProcedimiento.ANALISIS_DIFERENCIAS: self._analisis_claude,
        TipoProcedimiento.APRENDIZAJE: self._aprendizaje_claude,
        TipoProcedimiento.PRESENTACION: self._presentacion_claude,
        TipoProcedimiento.BUSQUEDA_PDF: self._busqueda_claude,
    }
    
    handler = handlers.get(procedimiento)
    if handler:
        return handler(**kwargs)
    
    return self._ejecutar_motor_python(procedimiento, **kwargs)
```

### Python Motor Handler

Direct Python execution without AI API:

```python
def _ejecutar_motor_python(self, procedimiento: TipoProcedimiento, **kwargs) -> Dict:
    """Execute procedure with Python motor directly"""
    handlers = {
        TipoProcedimiento.GENERACION_PRESUPUESTO: 
            lambda **kw: calcular_cotizacion_agente(**kw),
        TipoProcedimiento.REVISION_INPUTS: 
            lambda **kw: self.analisis_agente.revisar_inputs(**kw),
        TipoProcedimiento.BUSQUEDA_PDF: 
            lambda **kw: self.analisis_agente.buscar_pdf_cotizacion(kw.get('input_data')),
        TipoProcedimiento.EXTRACCION_DATOS: 
            lambda **kw: self.analisis_agente.extraer_datos_pdf(kw.get('pdf_path')),
        TipoProcedimiento.COMPARACION: 
            lambda **kw: self.analisis_agente.comparar_resultados(
                kw.get('presupuesto'), kw.get('pdf_real')
            ),
    }
    
    handler = handlers.get(procedimiento)
    if handler:
        return handler(**kwargs)
    
    return {"error": f"Procedure {procedimiento.value} not implemented"}
```

---

## Fallback System

### Fallback Logic

```
┌─────────────────┐
│ Request Task    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Try Primary     │─Yes─▶│ Execute Primary │
│ Model Available?│     └─────────────────┘
└────────┬────────┘
         │ No
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Try Alternative │─Yes─▶│ Execute Alt.    │
│ Model Available?│     └─────────────────┘
└────────┬────────┘
         │ No
         ▼
┌─────────────────┐
│ Execute Motor   │
│ Python (Always) │
└─────────────────┘
```

### Implementation

```python
def obtener_modelo_optimo(self, procedimiento: TipoProcedimiento) -> ModeloIA:
    """Get optimal model for a procedure with fallback"""
    asignacion = self.ASIGNACIONES.get(procedimiento)
    
    if not asignacion:
        return ModeloIA.OPENAI  # Default
    
    # Try primary model
    if self._modelo_disponible(asignacion.modelo_principal):
        return asignacion.modelo_principal
    
    # Fallback to alternative
    if self._modelo_disponible(asignacion.modelo_alternativo):
        return asignacion.modelo_alternativo
    
    # Final fallback - Python motor always available
    return ModeloIA.MOTOR_PYTHON

def _modelo_disponible(self, modelo: ModeloIA) -> bool:
    """Check if model is available"""
    if modelo == ModeloIA.OPENAI:
        return self.openai_agente is not None
    elif modelo == ModeloIA.CLAUDE:
        return self.claude_agente is not None
    elif modelo == ModeloIA.GEMINI:
        return self.gemini_agente is not None
    elif modelo == ModeloIA.MOTOR_PYTHON:
        return True  # Always available
    return False
```

---

## Usage Guide

### Basic Usage

```python
from orquestador_multi_modelo import OrquestadorMultiModelo, TipoProcedimiento

# Initialize orchestrator
orchestrator = OrquestadorMultiModelo()

# Execute a procedure
result = orchestrator.ejecutar_procedimiento(
    TipoProcedimiento.COTIZACION_REALTIME,
    mensaje="Cotiza ISODEC 100mm para 50m2"
)
```

### Check Model Availability

```python
# View available models
print("Available Models:")
print(f"  OpenAI: {'✅' if orchestrator.openai_agente else '❌'}")
print(f"  Claude: {'✅' if orchestrator.claude_agente else '❌'}")
print(f"  Gemini: {'✅' if orchestrator.gemini_agente else '❌'}")
print(f"  Python Motor: ✅ (always)")
```

### View Assignments

```python
# View all assignments
print("\n📊 MODEL ASSIGNMENTS:\n")
for proc, asignacion in orchestrator.ASIGNACIONES.items():
    modelo_optimo = orchestrator.obtener_modelo_optimo(proc)
    disponible = "✅" if orchestrator._modelo_disponible(modelo_optimo) else "❌"
    
    print(f"{disponible} {proc.value:30} → {modelo_optimo.value:15} "
          f"(alt: {asignacion.modelo_alternativo.value:15}, "
          f"priority: {asignacion.prioridad})")
```

### Complete Intelligent Process

```python
# Run complete process with optimal model routing
result = orchestrator.proceso_completo_inteligente(
    cliente="Cliente Test",
    producto="ISODEC EPS"
)

print("=" * 70)
print("📊 FINAL SUMMARY")
print("=" * 70)
print(f"   📋 Inputs processed: {len(result.get('inputs', []))}")
print(f"   🔧 Budgets generated: {len(result.get('presupuestos', []))}")
print(f"   📄 PDFs found: {len(result.get('pdfs_encontrados', []))}")
print(f"   ⚖️  Comparisons made: {len(result.get('comparaciones', []))}")
print(f"   🧠 Analyses completed: {len(result.get('analisis', []))}")
print(f"   📚 Lessons learned: {len(result.get('lecciones', []))}")
```

### Custom Pipeline

```python
# Execute specific procedures manually
from orquestador_multi_modelo import TipoProcedimiento

# Step 1: Review inputs
inputs = orchestrator.ejecutar_procedimiento(
    TipoProcedimiento.REVISION_INPUTS,
    cliente="Test",
    producto="ISODEC"
)

# Step 2: Generate budget for each input
for input_data in inputs:
    budget = orchestrator.ejecutar_procedimiento(
        TipoProcedimiento.GENERACION_PRESUPUESTO,
        input_data=input_data
    )
    
    # Step 3: Analyze (uses Claude)
    analysis = orchestrator.ejecutar_procedimiento(
        TipoProcedimiento.ANALISIS_DIFERENCIAS,
        comparacion=budget
    )
```

---

## Configuration

### Environment Variables

```bash
# Required for OpenAI
OPENAI_API_KEY=sk-your-key

# Optional for Claude
ANTHROPIC_API_KEY=sk-ant-your-key

# Optional for Gemini
GOOGLE_API_KEY=your-key
```

### Custom Assignment Override

```python
# Override default assignment
orchestrator.ASIGNACIONES[TipoProcedimiento.PRESENTACION] = AsignacionModelo(
    procedimiento=TipoProcedimiento.PRESENTACION,
    modelo_principal=ModeloIA.OPENAI,  # Changed from Claude
    modelo_alternativo=ModeloIA.CLAUDE,
    prioridad="alta",
    razon="Custom requirement"
)
```

---

## Related Documentation

- [[Architecture]] - Overall system architecture
- [[Agents-Overview]] - Individual agent documentation
- [[API-Reference]] - Complete API reference

---

<p align="center">
  <a href="[[Training-System]]">← Training System</a> |
  <a href="[[API-Reference]]">API Reference →</a>
</p>
