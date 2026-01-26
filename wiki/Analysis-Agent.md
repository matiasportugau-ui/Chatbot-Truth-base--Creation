# Analysis Agent

The Analysis Agent (`agente_analisis_inteligente.py`) reviews historical quotations, compares with real PDFs, and generates learning insights.

---

## Overview

The Analysis Agent provides:
- Historical input review
- Budget generation from inputs
- PDF document matching
- Data extraction from PDFs
- Comparison between generated and real quotations
- Learning and insight generation

---

## Process Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Review     │────▶│  Generate   │────▶│  Find PDF   │
│  Inputs     │     │  Budget     │     │  Match      │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Learn &    │◀────│  Compare    │◀────│  Extract    │
│  Improve    │     │  Results    │     │  PDF Data   │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## Quick Start

```python
from agente_analisis_inteligente import analizar_cotizacion_completa

result = analizar_cotizacion_completa(
    cliente="Cliente Test",
    producto="ISODEC EPS",
    fecha="2026-01-15",
    consulta="Techo de 50m2"
)

print(f"Inputs: {len(result.get('inputs', []))}")
print(f"Lessons: {len(result.get('lecciones', []))}")
```

---

## Capabilities

### 1. Input Review

Scans and reviews historical customer inputs:

```python
agent = AgenteAnalisisInteligente()
inputs = agent.revisar_inputs(
    cliente="Cliente Test",
    producto="ISODEC"
)
```

### 2. Budget Generation

Generates budgets using the Quotation Agent:

```python
budget = agent.generar_presupuesto(input_data)
```

### 3. PDF Matching

Finds matching real PDF quotations:

```python
pdf_match = agent.buscar_pdf_cotizacion(input_data)
# Returns: {"path": "quotes/2026/quote_123.pdf", "confidence": 0.85}
```

### 4. Data Extraction

Extracts data from PDF documents:

```python
pdf_data = agent.extraer_datos_pdf("quotes/quote_123.pdf")
# Returns structured data from PDF
```

### 5. Comparison

Compares generated vs real quotations:

```python
comparison = agent.comparar_resultados(budget, pdf_data)
# Returns differences and analysis
```

### 6. Learning

Generates insights and lessons:

```python
lessons = agent.generar_lecciones(comparisons)
```

---

## Function Schema

```json
{
    "name": "analizar_cotizacion_completa",
    "description": "Analiza cotizaciones históricas, compara con PDFs reales...",
    "parameters": {
        "type": "object",
        "properties": {
            "cliente": {"type": "string"},
            "producto": {"type": "string"},
            "fecha": {"type": "string"},
            "consulta": {"type": "string"}
        },
        "required": ["cliente", "producto"]
    }
}
```

---

## Response Structure

```python
{
    "inputs": [
        {
            "cliente": "Cliente Test",
            "producto": "ISODEC EPS",
            "fecha": "2026-01-15",
            "dimensiones": {...}
        }
    ],
    "presupuestos": [
        {
            "total": 2978.89,
            "materiales": {...}
        }
    ],
    "pdfs_encontrados": [
        {
            "path": "quotes/quote_123.pdf",
            "confidence": 0.85
        }
    ],
    "datos_pdfs": [...],
    "comparaciones": [
        {
            "diferencia_precio": 50.00,
            "diferencia_materiales": {...}
        }
    ],
    "lecciones": [
        {
            "tipo": "precio",
            "insight": "Shipping costs not included in calculation",
            "recomendacion": "Add shipping calculation"
        }
    ]
}
```

---

## Integration with Orchestrator

The Analysis Agent integrates with the Multi-Model Orchestrator:

```python
from orquestador_multi_modelo import OrquestadorMultiModelo, TipoProcedimiento

orchestrator = OrquestadorMultiModelo()

# Uses Claude for deep analysis
analysis = orchestrator.ejecutar_procedimiento(
    TipoProcedimiento.ANALISIS_DIFERENCIAS,
    comparacion=comparison_data
)
```

---

## Use Cases

### Training Improvement

Use analysis to improve the training system:

```python
# Analyze past quotes
result = analizar_cotizacion_completa(
    cliente=None,  # All clients
    producto="ISODEC"
)

# Feed lessons to training
from kb_training_system import Level2InteractionDriven

trainer = Level2InteractionDriven(kb_path="Files/")
trainer.train_from_lessons(result['lecciones'])
```

### Quality Assurance

Verify quotation accuracy:

```python
# Compare recent quotes with actual outcomes
for quote in recent_quotes:
    result = analizar_cotizacion_completa(
        cliente=quote['cliente'],
        producto=quote['producto'],
        fecha=quote['fecha']
    )
    
    if result['comparaciones']:
        diff = result['comparaciones'][0]['diferencia_precio']
        if abs(diff) > 100:
            flag_for_review(quote)
```

---

## Related

- [[Agents-Overview]] - All agents
- [[Quotation-Agent]] - Quotation generation
- [[Training-System]] - Uses analysis for training

---

<p align="center">
  <a href="[[Quotation-Agent]]">← Quotation Agent</a> |
  <a href="[[GPT-Simulation-Agent]]">GPT Simulation Agent →</a>
</p>
