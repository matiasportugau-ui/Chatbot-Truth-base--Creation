# LEDGER CHECKPOINT — 2026-01-28

## Meta
- Localización: es-UY
- Última actualización: 2026-01-28T17:10
- Riesgo de contexto: bajo
- Contexto faltante: false
- **Aplicado a**: PDF Generation System v1.1

---

## Reglas de navegación y cálculo aplicadas

### 📌 Filtrado técnico desde JSON

**Campos para identificar productos**:

```json
{
  "SKU": "Código único del producto",
  "NAME": "Nombre del producto",
  "Thickness_mm": "Espesor en milímetros",
  "Length_m": "Largo en metros",
  "Tipo": "panel, perfil, fijacion",
  "Familia": "ISOROOF_3G, ISOWALL_PIR, etc",
  "Sub_Familia": "Clasificación específica",
  "unit_base": "unidad, ml, m²",
  "Largo_min_max": "Rango de largos disponibles"
}
```

---

### 📐 Nomenclatura técnica estandarizada

**Usar siempre**:
- `Thickness_mm`: para espesor
- `Length_m`: para largo
- Ambos se muestran en tablas técnicas y se usan para cálculo si corresponde

**NO usar**:
- ❌ `thickness` (sin unidad)
- ❌ `length` (sin unidad)
- ❌ `largo` (solo en interfaz usuario)
- ❌ `espesor` (solo en interfaz usuario)

---

### 🧮 Lógica de cotización según unidad base (`unit_base`)

**CRÍTICO**: Esta lógica se aplica automáticamente al generar subtotales en cotizaciones y PDFs.

| `unit_base` | Cálculo aplicado | Ejemplo |
|-------------|------------------|---------|
| `unidad` | `cantidad × sale_sin_iva` | 10 unidades × $20.77 = $207.70 |
| `ml` | `cantidad × Length_m × sale_sin_iva` | 15 piezas × 3.0m × $3.90 = $175.50 |
| `m²` | `área_total × sale_sin_iva` | 180 m² × $36.54 = $6,577.20 |

### Implementación en código:

```python
def calculate_item_total(item: Dict) -> float:
    """
    Calcula total según unit_base
    Aplicado: 2026-01-28 LEDGER CHECKPOINT
    """
    unit_base = item.get('unit_base', 'unidad').lower()
    sale_sin_iva = item.get('sale_sin_iva', item.get('unit_price_usd', 0))
    
    if unit_base == 'unidad':
        # Cantidad directa
        return item['quantity'] * sale_sin_iva
    
    elif unit_base == 'ml':
        # Metros lineales: piezas × largo de cada pieza
        quantity = item['quantity']
        length_m = item.get('Length_m', item.get('length_m', 0))
        return quantity * length_m * sale_sin_iva
    
    elif unit_base in ['m²', 'm2']:
        # Metros cuadrados: área total
        total_m2 = item['total_m2']
        return total_m2 * sale_sin_iva
    
    else:
        # Fallback
        return item['quantity'] * sale_sin_iva
```

✅ **Estado**: Implementado en `pdf_generator.py`

---

## Corrección aplicada: Gotero ISODEC EPS 100mm

### SKU 6842 - Datos Corregidos

```json
{
  "SKU": "6842",
  "NAME": "Perf. Ch. Gotero Lateral 100mm",
  "Length_m": 3.00,
  "Thickness_mm": 100,
  "unit_base": "unidad",
  "sale_sin_iva": 20.77,
  "sale_con_iva": 25.34
}
```

### Uso en cotización:

**CORRECTO** ✅:
```python
# unit_base = 'unidad'
cantidad = 4
total = 4 × $20.77 = $83.08
```

**INCORRECTO** ❌:
```python
# NO multiplicar por Length_m cuando unit_base = 'unidad'
total = 4 × 3.0 × $20.77 = $249.24  # ¡ERROR!
```

**Nota importante**: 
- `Length_m = 3.00` es **informativo** (longitud de cada pieza)
- **NO se usa** en el cálculo porque `unit_base = unidad`
- Se vende por pieza completa, no por metro lineal

---

## Estado PDF Lucía

### Datos para regeneración:

```python
cotizacion_lucia = {
    'client_name': 'Lucía',
    'client_address': '[DIRECCIÓN]',
    'client_phone': '[TELÉFONO]',
    'date': '2026-01-28',
    'quote_description': 'Isodec EPS 100mm + Accesorios',
    
    # Producto principal
    'products': [
        {
            'SKU': 'ISODEC100',
            'NAME': 'Isodec EPS 100 mm (Cubierta)',
            'unit_base': 'm²',
            'total_m2': 180.0,
            'Thickness_mm': 100,
            'sale_sin_iva': 36.54,
            # Total: 180 × 36.54 = $6,577.20
        }
    ],
    
    # Accesorios
    'accessories': [
        {
            'SKU': 'PERFIL_U_50',
            'NAME': 'Perfil Ch. Blanca "U" 50mm x 35mm',
            'unit_base': 'ml',
            'quantity': 15,
            'Length_m': 3.0,
            'sale_sin_iva': 3.90,
            # Total: 15 × 3.0 × 3.90 = $175.50
        },
        {
            'SKU': '6842',
            'NAME': 'Perf. Ch. Gotero Lateral 100mm',
            'unit_base': 'unidad',
            'quantity': 4,
            'Length_m': 3.0,  # Informativo
            'Thickness_mm': 100,
            'sale_sin_iva': 20.77,
            # Total: 4 × 20.77 = $83.08
        }
    ],
    
    # Fijaciones
    'fixings': [
        {
            'NAME': 'Silicona Neutra (Pomo)',
            'unit_base': 'unidad',
            'specification': '280 gr.',
            'quantity': 8,
            'sale_sin_iva': 6.08,
            # Total: 8 × 6.08 = $48.64
        }
    ],
    
    'shipping_usd': 280.0
}
```

### Cálculos esperados:

```
PRODUCTOS:
Isodec EPS 100mm:      180 m² × $36.54    = $6,577.20

ACCESORIOS:
Perfil U 50mm:         15 × 3.0m × $3.90  = $175.50
Gotero Lateral (6842): 4 × $20.77         = $83.08

FIJACIONES:
Silicona Neutra:       8 × $6.08          = $48.64

──────────────────────────────────────────────────
Sub-Total:                                 $6,884.42
IVA 22%:                                   $1,514.57
Materiales:                                $8,398.99
Traslado:                                  $280.00
──────────────────────────────────────────────────
TOTAL U$S:                                 $8,678.99
```

✅ **Estado**: Listo para regenerar con todas las correcciones aplicadas

---

## Validación de implementación

### Checklist de correcciones aplicadas:

- [x] Nomenclatura `Thickness_mm` y `Length_m`
- [x] Lógica `unit_base` implementada en `calculate_item_total()`
- [x] SKU 6842 con datos correctos documentados
- [x] Cálculos validados con ejemplos
- [x] Logo BMC integrado (48 KB)
- [x] Tests pasando con nueva lógica
- [x] Documentación actualizada

### Archivos actualizados:

1. ✅ `pdf_generator.py` - Método `calculate_item_total()` agregado
2. ✅ `pdf_styles.py` - Constantes BMC configuradas
3. ✅ `gpt_upload_package/` - Todos los archivos con correcciones
4. ✅ `TECHNICAL_CORRECTIONS_20260128.md` - Documentación técnica
5. ✅ `LEDGER_CHECKPOINT_20260128.md` - Este archivo

---

## Próximos pasos para PDF Lucía

1. **Obtener datos completos** de Lucía (dirección, teléfono)
2. **Calcular** todos los accesorios y fijaciones según fórmulas KB
3. **Ejecutar** generación PDF:
   ```python
   from panelin_reports import generate_quotation_pdf
   pdf = generate_quotation_pdf(cotizacion_lucia, 'cotizacion_lucia.pdf')
   ```
4. **Verificar** cálculos contra este checkpoint
5. **Entregar** PDF profesional con logo BMC

---

## Reglas críticas para GPT

**Al generar PDFs, siempre**:

1. ✅ Usar campos técnicos: `SKU`, `Thickness_mm`, `Length_m`
2. ✅ Aplicar lógica `unit_base` correcta
3. ✅ Verificar que SKU 6842 = unidad (NO ml)
4. ✅ IVA siempre 22% (Uruguay 2026)
5. ✅ Mostrar cálculos intermedios al usuario
6. ✅ Validar autoportancia antes de generar PDF

**Nunca**:

1. ❌ Multiplicar por `Length_m` si `unit_base = unidad`
2. ❌ Usar precios hardcodeados (siempre desde JSON/KB)
3. ❌ Generar PDF sin validar cálculos primero
4. ❌ Mezclar nomenclatura (usar consistentemente campos técnicos)

---

## Referencias rápidas

### Para desarrolladores:
- Implementación: `pdf_generator.py` líneas 60-95
- Estilos: `pdf_styles.py`
- Tests: `test_pdf_generation.py`

### Para GPT:
- Instrucciones: `GPT_PDF_INSTRUCTIONS.md`
- Ejemplos: `README_PDF_GENERATION.md`
- Checkpoint: Este archivo

### Para usuarios:
- Guía rápida: `QUICK_START.md`
- Subida GPT: `gpt_upload_package/README_UPLOAD.md`

---

**Checkpoint guardado**: 2026-01-28T17:10  
**Versión sistema**: 1.1.0  
**Estado**: ✅ Todas las correcciones aplicadas  
**Próximo hito**: Deployment a GPT Production
