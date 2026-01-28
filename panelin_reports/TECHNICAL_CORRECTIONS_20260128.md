# Technical Corrections - 2026-01-28

## Meta
- Localización: es-UY
- Última actualización: 2026-01-28T17:10
- Aplicado a: PDF Generation System v1.1

---

## 📌 Nomenclatura Técnica Estandarizada

### Campos JSON para identificación de productos:

```python
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

### Uso en tablas y cálculos:

- **`Thickness_mm`**: Se muestra como especificación técnica del panel/perfil
- **`Length_m`**: Se usa para cálculos cuando `unit_base = ml`
- Ambos aparecen en tablas técnicas del PDF

---

## 🧮 Lógica de Cotización según `unit_base`

### Fórmulas de Cálculo:

| `unit_base` | Fórmula | Ejemplo |
|-------------|---------|---------|
| `unidad` | `cantidad × sale_sin_iva` | 10 unidades × $20.77 = $207.70 |
| `ml` | `cantidad × Length_m × sale_sin_iva` | 5 piezas × 3.0m × $6.70 = $100.50 |
| `m²` | `área_total × sale_sin_iva` | 200 m² × $33.21 = $6,642.00 |

### Aplicación en PDF:

1. **Productos (Paneles)**: Generalmente `unit_base = m²`
   - Calcular área total primero
   - Aplicar precio por m²
   
2. **Accesorios (Perfiles)**: Generalmente `unit_base = ml`
   - Multiplicar cantidad de piezas × longitud de cada pieza
   - Aplicar precio por metro lineal
   
3. **Fijaciones**: Generalmente `unit_base = unidad`
   - Cantidad directa × precio unitario

---

## 🔧 Corrección Específica: SKU 6842

### Producto: Perf. Ch. Gotero Lateral 100mm

**Datos corregidos**:
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

**Uso en cotización**:
- Si se necesitan 4 goteros: `4 × $20.77 = $83.08` (sin IVA)
- **NO** multiplicar por `Length_m` porque `unit_base = unidad`

---

## 📄 Impacto en PDF Generation

### Actualización de campos:

**Antes**:
```python
{
    'name': 'Producto',
    'length_m': 6.0,
    'thickness_mm': 50,  # Inconsistente
    'quantity': 10,
    'unit_price_usd': 33.21
}
```

**Después (Estandarizado)**:
```python
{
    'name': 'Producto',
    'Length_m': 6.0,      # Capitalizado, con guión bajo
    'Thickness_mm': 50,   # Capitalizado, con guión bajo
    'quantity': 10,
    'unit_base': 'm²',    # Especifica tipo de cálculo
    'sale_sin_iva': 33.21 # Nomenclatura BMC
}
```

### Función de cálculo actualizada:

```python
def calculate_item_total(item):
    """
    Calcula total según unit_base
    
    Args:
        item: Dict con keys: quantity, unit_base, sale_sin_iva, Length_m (opcional)
    
    Returns:
        float: Total calculado
    """
    unit_base = item.get('unit_base', 'unidad')
    
    if unit_base == 'unidad':
        # Cantidad directa
        return item['quantity'] * item['sale_sin_iva']
    
    elif unit_base == 'ml':
        # Metros lineales: cantidad de piezas × largo de cada pieza
        return item['quantity'] * item['Length_m'] * item['sale_sin_iva']
    
    elif unit_base == 'm²':
        # Metros cuadrados: área total
        return item['total_m2'] * item['sale_sin_iva']
    
    else:
        # Fallback a cantidad directa
        return item['quantity'] * item['sale_sin_iva']
```

---

## 📊 Ejemplo Completo: Cotización Lucía

### Productos:

**1. Isodec EPS 100mm (Cubierta)**
- `unit_base = m²`
- Área: 180 m²
- Precio s/IVA: $36.54/m²
- **Cálculo**: `180 × $36.54 = $6,577.20`

**2. Perfil Ch. Gotero Lateral 100mm (SKU 6842)**
- `unit_base = unidad`
- Cantidad: 4 piezas
- Precio s/IVA: $20.77/unidad
- `Length_m = 3.0` (informativo, NO se usa en cálculo)
- **Cálculo**: `4 × $20.77 = $83.08`

**3. Perfil U 50mm**
- `unit_base = ml`
- Cantidad: 15 piezas
- `Length_m = 3.0`
- Precio s/IVA: $3.90/ml
- **Cálculo**: `15 × 3.0 × $3.90 = $175.50`

---

## ✅ Checklist de Implementación

Aplicar estas correcciones en:

- [x] Nomenclatura de campos (Thickness_mm, Length_m)
- [x] Lógica de cálculo según unit_base
- [x] Datos SKU 6842 corregidos
- [ ] Actualizar pdf_generator.py con nueva lógica
- [ ] Actualizar pdf_styles.py con constantes
- [ ] Documentar en GPT_PDF_INSTRUCTIONS.md
- [ ] Test con cotización real (Lucía)

---

## 🎯 Próximos Pasos

1. **Regenerar PDF de Lucía** con correcciones aplicadas
2. **Validar cálculos** contra cotización original
3. **Actualizar GPT instructions** con nomenclatura técnica
4. **Probar** con diferentes tipos de productos (paneles, perfiles, fijaciones)

---

**Versión**: 1.0  
**Fecha**: 2026-01-28  
**Aplicado a**: BMC Uruguay PDF Generation System  
**Estado**: ✅ Logo agregado | 🔄 Código en actualización
