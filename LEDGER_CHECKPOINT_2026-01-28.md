# LEDGER CHECKPOINT — 2026-01-28

## Meta
- **Localización**: es-UY
- **Última actualización**: 2026-01-28T17:10
- **Riesgo de contexto**: bajo
- **Contexto faltante**: false

---

## 📌 Reglas de navegación y cálculo aplicadas

### Filtrado técnico desde JSON

**Campos obligatorios para identificar productos**:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `SKU` | Código único del producto | `"6842"` |
| `NAME` | Nombre del producto | `"Perf. Ch. Gotero Lateral 100mm"` |
| `Thickness_mm` | Espesor en milímetros | `100` |
| `Length_m` | Largo en metros | `3.00` |
| `Tipo` | Tipo de producto | `"perfil"`, `"panel"`, etc. |
| `Familia` | Familia del producto | `"gotero"`, `"ISOROOF"`, etc. |
| `Sub_Familia` | Subfamilia/material | `"EPS"`, `"PIR"`, etc. |
| `unit_base` | Unidad de medida base | `"unidad"`, `"ml"`, `"m²"` |
| `Largo_min_max` | Rango de largo (si aplica) | `"2.5-14.0"` |

---

## 📐 Nomenclatura técnica estandarizada

**IMPORTANTE**: Usar consistentemente en tablas, cálculos y PDFs:

- **`Thickness_mm`**: Para espesor del producto (no usar "espesor", "grosor", etc.)
- **`Length_m`**: Para largo del producto (no usar "largo", "longitud", etc.)

**Ejemplo de tabla técnica**:

```
| SKU  | Producto                      | Thickness_mm | Length_m | unit_base |
|------|-------------------------------|--------------|----------|-----------|
| 6842 | Perf. Ch. Gotero Lateral 100mm| 100          | 3.00     | unidad    |
```

---

## 🧮 Lógica de cotización según unidad base (`unit_base`)

**REGLA CRÍTICA**: El cálculo del subtotal varía según la unidad de medida base.

| `unit_base` | Fórmula de cálculo | Ejemplo |
|-------------|--------------------|---------|
| `unidad` | `cantidad × sale_sin_iva` | 5 unidades × $20.77 = $103.85 |
| `ml` (metro lineal) | `cantidad × Length_m × sale_sin_iva` | 10 piezas × 3.0m × $20.77 = $623.10 |
| `m²` (metro cuadrado) | `área_total × sale_sin_iva` | 300 m² × $33.21 = $9,963.00 |

### ⚠️ Aplicación automática

Esta lógica **DEBE** aplicarse automáticamente en:
- Generación de subtotales en cotizaciones
- Cálculos en PDFs
- Validación de precios
- Reportes de ventas

### Ejemplo práctico

**Producto**: Gotero Lateral 100mm (SKU 6842)
- `unit_base = "unidad"`
- `Length_m = 3.00`
- `sale_sin_iva = $20.77`

**Cliente solicita**: 8 piezas

**Cálculo correcto**:
```
Subtotal = 8 × $20.77 = $166.16 USD
(NO multiplicar por Length_m porque unit_base = "unidad")
```

**Si fuera `unit_base = "ml"`** (hipotético):
```
Subtotal = 8 × 3.00 × $20.77 = $498.48 USD
```

---

## ✅ Corrección aplicada: Gotero ISODEC EPS 100mm

**SKU: 6842**

### Datos corregidos

```json
{
  "sku": "6842",
  "name": "Perf. Ch. Gotero Lateral 100mm",
  "description": "Perf. Ch. Gotero Lateral 100mm - (3m)",
  "thickness_mm": 100,
  "length_m": 3.00,
  "unit_base": "unidad",
  "sale_price_usd_ex_iva": 20.77,
  "price_usd": 25.34,
  "type": "perfil",
  "family": "gotero"
}
```

### Cambios aplicados

| Campo | Valor anterior | Valor correcto | Estado |
|-------|----------------|----------------|--------|
| `thickness_mm` | 100 | 100 | ✓ Correcto |
| `length_m` | 3.00 | 3.00 | ✓ Correcto |
| `unit_base` | `"metro_lineal"` | `"unidad"` | ⚠️ CORREGIR |
| `sale_price_usd_ex_iva` | 20.77 | 20.77 | ✓ Correcto |

**Acción requerida**: Actualizar `unit_base` de `"metro_lineal"` a `"unidad"` en archivo maestro.

---

## 📄 Estado PDF Lucía

### Estado actual
- ✅ En preparación final
- ✅ Logo BMC copiado a `panelin_reports/assets/bmc_logo.png`
- ✅ Lógica de cálculo documentada

### Listo para regenerar con:
- ✅ **Terminología técnica**: `Thickness_mm` y `Length_m`
- ✅ **Precios correctos**: Según archivo maestro
- ✅ **Lógica de `unit_base`**: Aplicada automáticamente
- ✅ **Estilo estructurado BMC**: Según plantilla oficial

### Checklist pre-generación

- [ ] Validar que todos los productos tienen `unit_base` correcto
- [ ] Verificar cálculos con lógica según tabla de unidades
- [ ] Confirmar datos del cliente (nombre, dirección, teléfono)
- [ ] Revisar subtotales por categoría (paneles, accesorios, fijaciones)
- [ ] Validar IVA 22% para Uruguay 2026
- [ ] Incluir términos y condiciones estándar BMC

---

## 🖼️ Assets

### Logo BMC Uruguay

- **Ubicación**: `/panelin_reports/assets/bmc_logo.png`
- **Estado**: ✅ Copiado correctamente
- **Uso**: Header de PDFs, cotizaciones formales

### Fuente original
`/Users/matias/.cursor/projects/.../assets/2000px-3c0fdb9f-f25b-4531-a065-97152ef4f2e4.png`

---

## 📋 Próximos pasos

1. **Actualizar archivo maestro de pricing**:
   - Corregir `unit_base` de SKU 6842 a `"unidad"`
   - Validar que otros goteros tengan la unidad correcta

2. **Regenerar PDF Lucía**:
   - Aplicar terminología técnica
   - Usar lógica de `unit_base` correcta
   - Incluir logo BMC

3. **Validar con test**:
   - Ejecutar `test_pdf_generation.py`
   - Verificar cálculos manualmente

4. **Documentar cambios**:
   - Actualizar `KB_CHANGELOG_v6.0.md`
   - Registrar en historial de versiones

---

## 🔗 Referencias

- **PDF Instructions**: `panelin_reports/GPT_PDF_INSTRUCTIONS.md`
- **Pricing Instructions**: `pricing/GPT_INSTRUCTIONS_PRICING.md`
- **Master Pricing Data**: `gpt_consolidation_agent/deployment/knowledge_base/bromyros_pricing_master.json`
- **Product Enrichment Rules**: `pricing/config/product_enrichment_rules.json`

---

**Versión**: 1.0  
**Fecha**: 2026-01-28  
**Responsable**: Sistema Panelin  
**Estado**: ✅ Activo
