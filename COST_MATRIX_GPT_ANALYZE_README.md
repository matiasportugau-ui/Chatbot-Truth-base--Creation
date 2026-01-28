# Cost Matrix Multi-Supplier JSON for GPT Analyze

## Overview

Complete cost matrix JSON file optimized for GPT Analyze file upload. Contains data from 6 suppliers with full GPT-friendly optimizations.

## File Information

- **File**: `wiki/matriz de costos adaptacion /redesigned/COST_MATRIX_ALL_SUPPLIERS_GPT_ANALYZE.json`
- **Size**: 2.42 MB
- **Structure**: Option A (grouped by supplier)
- **Suppliers**: 6
- **Products**: 490
- **Categories**: 20

## Suppliers Included

1. **ALAMBRESA** - 2 products
2. **ARMCO** - 23 products
3. **BECAM** - 280 products
4. **BROMYROS** - 137 products (main supplier)
5. **HM RUBBER** - 47 products
6. **R y C Tornillos** - 1 product

## Structure

```json
{
  "meta": {
    "nombre": "Matriz de Costos y Ventas 2026 - Multi-Proveedor",
    "version": "3.0.0",
    "optimizado_para": "GPT Analyze - File Upload",
    "estructura": "Option A - Agrupado por Proveedor",
    "total_proveedores": 6,
    "total_productos": 490,
    "proveedores_incluidos": [...],
    "estadisticas_globales": {...}
  },
  "reglas_precios": {...},
  "indices": {
    "by_code": {...},      // 490 entries - O(1) lookup
    "by_supplier": {...},  // 6 suppliers
    "by_category": {...},  // 20 categories
    "by_thickness": {...}  // Thickness-based lookup
  },
  "proveedores": {
    "BROMYROS": {
      "nombre": "BROMYROS",
      "total_productos": 137,
      "estadisticas": {...},
      "productos": {
        "por_categoria": {...},
        "todos": [...]
      }
    },
    ...
  }
}
```

## GPT Analyze Optimizations

Each product includes enhanced `metadata.gpt_analyze` fields:

```json
{
  "codigo": "IAGRO30",
  "nombre": "Isoroof FOIL 30 mm - Color Gris-Rojo",
  "categoria": "isoroof_foil",
  "espesor_mm": "30",
  "metadata": {
    "proveedor": "BROMYROS",
    "gpt_analyze": {
      "description": "Isoroof FOIL 30 mm - Color Gris-Rojo. Espesor: 30mm. Panel aislante techo liviano con lámina. Proveedor: BROMYROS.",
      "keywords": ["iagro30", "isoroof foil", "30mm", "espesor 30", "panel", "techo", "bromyros"],
      "searchable_text": "iagro30 isoroof foil 30 mm isoroof_foil 30mm bromyros",
      "category_display": "Isoroof Foil",
      "usage_context": "Ideal para techos livianos residenciales y comerciales. Excelente aislamiento térmico y acústico. Espesor disponible: 30mm."
    }
  }
}
```

## Fields Included

All fields from original cost matrix are preserved:

- **Basic**: codigo, nombre, categoria, espesor_mm, estado
- **Costos**: costo_base_usd_iva, costo_con_aumento_usd_iva, costo_proximo_aumento_usd_iva
- **Precios**: venta_iva_usd, consumidor_iva_inc_usd, web_venta_iva_usd, web_venta_iva_inc_usd
- **Margen**: porcentaje, ganancia_usd
- **Linear pricing**: precio_base_usd, precios_por_largo (by length)
- **Metadata**: proveedor, shopify_status, notas, gpt_analyze

## Usage with GPT

### Upload to GPT

1. Go to GPT Builder or ChatGPT
2. Upload `COST_MATRIX_ALL_SUPPLIERS_GPT_ANALYZE.json` as a file
3. GPT can now search and analyze the cost matrix

### Example Queries

**By Product Code**:
> "Find product IAGRO30"

GPT can use the `indices.by_code` to quickly locate the product.

**By Supplier**:
> "List all BROMYROS products"

GPT can use `proveedores.BROMYROS.productos.todos`.

**By Category**:
> "Show all isoroof_foil products across all suppliers"

GPT can use `indices.by_category.isoroof_foil`.

**By Thickness**:
> "Find all 30mm panels"

GPT can use `indices.by_thickness.30`.

**Natural Language**:
> "What panels does BECAM have for roofs?"

GPT can search using `metadata.gpt_analyze.searchable_text` and `keywords`.

## Regeneration

To regenerate the file:

```bash
python3 generate_multi_supplier_gpt_analyze.py
```

## Validation

Run validation checks:

```bash
# Validate JSON
python3 -c "import json; json.load(open('wiki/matriz de costos adaptacion /redesigned/COST_MATRIX_ALL_SUPPLIERS_GPT_ANALYZE.json')); print('✓ Valid JSON')"

# Check structure
python3 -c "
import json
data = json.load(open('wiki/matriz de costos adaptacion /redesigned/COST_MATRIX_ALL_SUPPLIERS_GPT_ANALYZE.json'))
print(f'Suppliers: {len(data[\"proveedores\"])}')
print(f'Products: {data[\"meta\"][\"total_productos\"]}')
print(f'Index entries: {len(data[\"indices\"][\"by_code\"])}')
"
```

## Statistics

- **Total products**: 490
- **Active products**: 464
- **Products with cost data**: 401
- **Products with web pricing**: 160
- **Unique categories**: 20
- **File size**: 2.42 MB

## Notes

- This file contains internal cost/margin data - treat as **INTERNAL ONLY**
- Do not publish to external GPTs or share with clients
- For public GPTs, use the sanitized version without cost data
- Regenerate after updating the Excel cost matrix

## Related Files

- **Generator script**: `generate_multi_supplier_gpt_analyze.py`
- **Single supplier (BROMYROS)**: `wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_OPTIMIZED.json`
- **Source HTML files**: `wiki/matriz de costos adaptacion /MATRIZ de COSTOS y VENTAS 2026 2.xlsx/*.html`
- **Workflow documentation**: `wiki/Cost-Matrix-Workflow.md`
