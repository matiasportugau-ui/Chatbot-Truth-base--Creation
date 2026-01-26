# Quotation Agent

The Quotation Agent (`agente_cotizacion_panelin.py`) is the primary agent for generating technical quotations for construction panels.

---

## Overview

The Quotation Agent handles all quotation calculations for:
- **ISODEC EPS/PIR** - Sandwich panels with steel faces
- **ISOPANEL EPS** - Standard construction panels  
- **ISOROOF 3G/PLUS/FOIL** - Roof panels for light structures
- **ISOWALL PIR** - Wall panels with PIR insulation

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Platform** | OpenAI, Claude, Gemini support |
| **Function Calling** | Native AI integration |
| **Autoportancia Validation** | Load-bearing capacity check |
| **Material Calculation** | Complete material breakdown |
| **IVA Calculation** | Automatic 22% tax |
| **Professional Output** | Formatted quotation text |

---

## Quick Start

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
    print(result['presentacion_texto'])
```

---

## Parameters

| Parameter | Type | Required | Options | Description |
|-----------|------|----------|---------|-------------|
| `producto` | str | Yes | ISODEC EPS, ISODEC PIR, ISOPANEL EPS, ISOROOF 3G, ISOROOF PLUS, ISOROOF FOIL, ISOWALL PIR | Product type |
| `espesor` | str | Yes | 50, 80, 100, 150, 200 | Thickness in mm |
| `largo` | float | Yes | - | Length in meters |
| `ancho` | float | Yes | - | Width in meters |
| `luz` | float | Yes | - | Span between supports (critical) |
| `tipo_fijacion` | str | No | hormigon, metal, madera | Fixing type (default: hormigon) |
| `alero_1` | float | No | - | Overhang end 1 (default: 0) |
| `alero_2` | float | No | - | Overhang end 2 (default: 0) |

---

## Response Structure

```python
{
    "success": True,
    "error": None,
    "cotizacion": {
        "producto": "ISODEC EPS",
        "espesor": "100",
        "dimensiones": {
            "largo": 10.0,
            "ancho": 5.0,
            "area": 50.0
        },
        "validacion": {
            "autoportancia": 5.5,
            "luz_efectiva": 4.5,
            "cumple_autoportancia": True,
            "advertencia": None
        },
        "materiales": {
            "paneles": 53,
            "varilla_roscada": 21,
            "tuerca_hexagonal": 42,
            "arandela_plana": 42,
            "taco_expansivo": 21
        },
        "costos": {
            "subtotal": 2441.71,
            "iva": 537.18,
            "total": 2978.89
        }
    },
    "presentacion_texto": "..."
}
```

---

## Platform-Specific Usage

### OpenAI

```python
from agente_cotizacion_panelin import AgentePanelinOpenAI
import os

agent = AgentePanelinOpenAI(os.getenv("OPENAI_API_KEY"))

# Create or use existing assistant
agent.assistant_id = "asst_xxx"  # Or agent.crear_asistente()

# Create thread and process
thread = agent.client.beta.threads.create()
response = agent.procesar_mensaje(
    thread.id,
    "Cotiza ISODEC 100mm para 50m2 con luz de 4.5m"
)
print(response)
```

### Claude

```python
from agente_cotizacion_panelin import AgentePanelinClaude
import os

agent = AgentePanelinClaude(os.getenv("ANTHROPIC_API_KEY"))
response = agent.chat("Cotiza ISODEC 100mm para 50m2")
print(response)
```

### Gemini

```python
from agente_cotizacion_panelin import AgentePanelinGemini
import os

agent = AgentePanelinGemini(os.getenv("GOOGLE_API_KEY"))
response = agent.chat("Cotiza ISODEC 100mm para 50m2")
print(response)
```

---

## Autoportancia Reference

| Product | Thickness | Max Span (m) |
|---------|-----------|--------------|
| ISODEC EPS | 100mm | 5.5m |
| ISODEC EPS | 150mm | 7.5m |
| ISODEC EPS | 200mm | 9.5m |
| ISODEC PIR | 100mm | 6.0m |
| ISODEC PIR | 150mm | 8.0m |
| ISOROOF | All | Varies |

---

## Fixing Types

### Hormigón (Concrete)

Materials included:
- Threaded rod 3/8"
- Hex nut 3/8"
- Flat washer 3/8"
- Expansion anchor 3/8"

### Metal

Materials included:
- Self-drilling screws
- Washers

### Madera (Wood)

Materials included:
- Wood screws
- Trestle supports

---

## Related

- [[Agents-Overview]] - All agents
- [[API-Reference]] - Full API docs
- [[Knowledge-Base]] - Price data source

---

<p align="center">
  <a href="[[Agents-Overview]]">← Agents Overview</a> |
  <a href="[[Analysis-Agent]]">Analysis Agent →</a>
</p>
