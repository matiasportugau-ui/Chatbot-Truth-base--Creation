# Quotation Engine

The Quotation Engine (`motor_cotizacion_panelin.py`) is the core calculation engine that powers all quotation operations in the Panelin system.

---

## Overview

The engine handles:
- Material quantity calculations
- Price lookups from Knowledge Base
- Autoportancia (load-bearing) validation
- IVA (22%) tax calculation
- Multiple fixing types
- Overhang (alero) calculations

---

## How It Works

```
Input Request
      │
      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      QUOTATION ENGINE                                     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. PARAMETER VALIDATION                                                  │
│     • Validate product type exists in KB                                 │
│     • Validate thickness available                                       │
│     • Validate dimensions are positive                                   │
│                                                                           │
│  2. AUTOPORTANCIA CHECK                                                   │
│     • Get max span from KB for product/thickness                        │
│     • Compare with requested luz (span)                                  │
│     • Generate warning if exceeded                                       │
│                                                                           │
│  3. AREA CALCULATION                                                      │
│     • area = largo × ancho                                               │
│     • Add aleros if specified                                            │
│                                                                           │
│  4. MATERIAL CALCULATION                                                  │
│     • Panels: ceil(area / (panel_length × useful_width))                │
│     • Fixings: Based on fixing type and panel count                     │
│     • Use KB formulas                                                    │
│                                                                           │
│  5. PRICE LOOKUP                                                          │
│     • Get prices from Level 1 KB (Source of Truth)                      │
│     • Apply per-unit pricing                                             │
│                                                                           │
│  6. COST CALCULATION                                                      │
│     • subtotal = sum(quantity × unit_price)                             │
│     • iva = subtotal × 0.22                                             │
│     • total = subtotal + iva                                             │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
      │
      ▼
Quotation Result
```

---

## Core Class

```python
class MotorCotizacionPanelin:
    """Core quotation calculation engine"""
    
    def __init__(self, kb_path: str = "Files/"):
        self.kb_path = kb_path
        self.kb_data = self._load_kb()
    
    def calcular_cotizacion(
        self,
        producto: str,
        espesor: str,
        largo: float,
        ancho: float,
        tipo_fijacion: str,
        luz: float,
        alero_1: float = 0,
        alero_2: float = 0
    ) -> Dict[str, Any]:
        """Calculate complete quotation"""
        pass
    
    def _validar_autoportancia(
        self, 
        producto: str, 
        espesor: str, 
        luz: float
    ) -> Dict:
        """Validate load-bearing capacity"""
        pass
    
    def _calcular_materiales(
        self,
        producto: str,
        espesor: str,
        area: float,
        tipo_fijacion: str
    ) -> Dict:
        """Calculate required materials"""
        pass
    
    def _obtener_precios(
        self, 
        producto: str, 
        espesor: str
    ) -> Dict:
        """Get prices from KB"""
        pass
    
    def _calcular_costos(
        self, 
        materiales: Dict, 
        precios: Dict
    ) -> Dict:
        """Calculate total costs"""
        pass
    
    def formatear_cotizacion(self, cotizacion: Dict) -> str:
        """Format quotation as text"""
        pass
```

---

## Formulas

### Panel Quantity

```
cantidad_paneles = ceil(area_total / (largo_panel × ancho_util))
```

Where:
- `area_total` = largo × ancho + aleros
- `largo_panel` = standard panel length (typically 6m)
- `ancho_util` = useful width (0.95m for most panels)

### Fixing Materials (Concrete)

```
varillas = ceil(cantidad_paneles / 2.5)
tuercas = varillas × 2
arandelas = varillas × 2
tacos = varillas
```

### Cost Calculation

```
subtotal = Σ(cantidad_i × precio_i)
iva = subtotal × 0.22
total = subtotal + iva
```

---

## Supported Products

| Product | Thicknesses | Type |
|---------|-------------|------|
| ISODEC EPS | 50, 80, 100, 150, 200 | Sandwich panel |
| ISODEC PIR | 80, 100, 150 | Sandwich panel (fire) |
| ISOPANEL EPS | 50, 80, 100, 150, 200 | Standard panel |
| ISOROOF 3G | 30, 50, 80 | Roof panel (light) |
| ISOROOF PLUS | 50, 80 | Roof panel (enhanced) |
| ISOROOF FOIL | 30, 50 | Roof panel (reflective) |
| ISOWALL PIR | 80, 100, 150 | Wall panel (fire) |

---

## Fixing Types

### Hormigón (Concrete)

For fixing panels to concrete structures:

```python
materials = {
    "varilla_roscada_3_8": calculated_quantity,
    "tuerca_hexagonal_3_8": calculated_quantity * 2,
    "arandela_plana_3_8": calculated_quantity * 2,
    "taco_expansivo_3_8": calculated_quantity
}
```

### Metal

For fixing panels to metal structures:

```python
materials = {
    "tornillo_autoperforante": calculated_quantity,
    "arandela_neopreno": calculated_quantity
}
```

### Madera (Wood)

For fixing ISOROOF to wood structures:

```python
materials = {
    "tornillo_madera": calculated_quantity,
    "caballete": calculated_quantity
}
```

---

## Autoportancia Reference

Maximum unsupported span:

| Product | 50mm | 80mm | 100mm | 150mm | 200mm |
|---------|------|------|-------|-------|-------|
| ISODEC EPS | 3.0m | 4.5m | 5.5m | 7.5m | 9.5m |
| ISODEC PIR | - | 5.0m | 6.0m | 8.0m | - |
| ISOPANEL EPS | 2.5m | 4.0m | 5.0m | 7.0m | 9.0m |

---

## Usage Examples

### Direct Usage

```python
from motor_cotizacion_panelin import MotorCotizacionPanelin

motor = MotorCotizacionPanelin()

cotizacion = motor.calcular_cotizacion(
    producto="ISODEC EPS",
    espesor="100",
    largo=10.0,
    ancho=5.0,
    luz=4.5,
    tipo_fijacion="hormigon"
)

print(motor.formatear_cotizacion(cotizacion))
```

### With Aleros (Overhangs)

```python
cotizacion = motor.calcular_cotizacion(
    producto="ISODEC EPS",
    espesor="150",
    largo=12.0,
    ancho=6.0,
    luz=6.0,
    tipo_fijacion="hormigon",
    alero_1=0.5,  # 50cm overhang on one end
    alero_2=0.5   # 50cm overhang on other end
)
```

### Validation Only

```python
motor = MotorCotizacionPanelin()

# Just check autoportancia
validacion = motor._validar_autoportancia(
    producto="ISODEC EPS",
    espesor="100",
    luz=6.0
)

if not validacion['cumple']:
    print(f"Warning: Max span is {validacion['autoportancia']}m")
    print(f"Suggestion: Use 150mm or add support")
```

---

## Output Format

```python
{
    "producto": "ISODEC EPS",
    "espesor": "100",
    "dimensiones": {
        "largo": 10.0,
        "ancho": 5.0,
        "area": 50.0,
        "alero_1": 0,
        "alero_2": 0
    },
    "validacion": {
        "autoportancia": 5.5,
        "luz_efectiva": 4.5,
        "cumple_autoportancia": True,
        "advertencia": None
    },
    "materiales": {
        "paneles_isodec_eps_100": {
            "cantidad": 53,
            "unidad": "unidades"
        },
        "varilla_roscada_3_8": {
            "cantidad": 21,
            "unidad": "unidades"
        },
        "tuerca_hexagonal_3_8": {
            "cantidad": 42,
            "unidad": "unidades"
        },
        "arandela_plana_3_8": {
            "cantidad": 42,
            "unidad": "unidades"
        },
        "taco_expansivo_3_8": {
            "cantidad": 21,
            "unidad": "unidades"
        }
    },
    "costos": {
        "desglose": [
            {"item": "Paneles ISODEC EPS 100mm", "cantidad": 53, "precio_unitario": 46.07, "subtotal": 2441.71}
        ],
        "subtotal": 2441.71,
        "iva": 537.18,
        "total": 2978.89,
        "moneda": "USD"
    }
}
```

---

## Error Handling

```python
# Product not found
cotizacion = motor.calcular_cotizacion(
    producto="INVALID",
    ...
)
# Returns: {"error": "Product 'INVALID' not found in knowledge base"}

# Thickness not available
cotizacion = motor.calcular_cotizacion(
    producto="ISODEC EPS",
    espesor="250",  # Not available
    ...
)
# Returns: {"error": "Thickness '250' not available for ISODEC EPS"}
```

---

## Integration

The engine is used by:
- [[Quotation-Agent]] - Primary agent
- [[Analysis-Agent]] - For budget generation
- [[Multi-Model-Orchestration]] - Direct Python execution

---

## Related

- [[Quotation-Agent]] - Agent using this engine
- [[Knowledge-Base]] - Price data source
- [[API-Reference]] - Full API docs

---

<p align="center">
  <a href="[[Architecture]]">← Architecture</a> |
  <a href="[[Knowledge-Base]]">Knowledge Base →</a>
</p>
