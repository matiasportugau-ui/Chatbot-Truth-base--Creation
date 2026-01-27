# Cost Matrix Workflow (Human + GPT Indexed)

This workflow keeps the **Matriz de Costos y Ventas** usable by humans (Excel) while ensuring **instant GPT access** via an **indexed JSON** file consumed by the KB Indexing Agent.

## Critical note (sensitive data)

The cost matrix contains **internal costs/margins**. Treat the optimized JSON and Excel template as **INTERNAL ONLY**. Do not publish to external GPTs or share with clients.

## Files (current BROMYROS setup)

- **Source (Excel export as HTML)**: `wiki/matriz de costos adaptacion /MATRIZ de COSTOS y VENTAS 2026 2.xlsx/BROMYROS.html`
- **Optimized JSON (GPT indexed)**: `wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_OPTIMIZED.json`
- **Human template (Excel)**: `wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_TEMPLATE.xlsx`

## Tools

- **Redesign / ingestion tool**: `panelin_improvements/cost_matrix_tools/redesign_tool.py`
  - Input: `.html` (Excel “Save as Web Page”), `.csv`, `.tsv`, or a directory of `.html` sheets
  - Output: optimized JSON with `indices` for fast lookup

- **Excel manager (bi-directional sync)**: `panelin_improvements/cost_matrix_tools/excel_manager.py`
  - `export`: JSON → Excel
  - `import`: Excel → JSON (rebuilds indices via `redesign_tool`)

- **KB access layer**: `agente_kb_indexing.py`
  - Fast path: `get_cost_matrix_product(code)`
  - Listing: `get_cost_matrix_products_by_category(category)`
  - Search: `search_knowledge_base(query)` (now includes a fast path for cost-matrix codes)

## Process A: Update using the Excel export (HTML is the source)

Use this if your “source of truth” is the original Excel workbook and you export to HTML.

1. Update the spreadsheet (human).
2. Export the BROMYROS sheet as HTML (Excel → “Save as Web Page”).
3. Regenerate the optimized JSON:

```bash
python3 -m panelin_improvements.cost_matrix_tools.redesign_tool \
  "wiki/matriz de costos adaptacion /MATRIZ de COSTOS y VENTAS 2026 2.xlsx/BROMYROS.html" \
  "wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_OPTIMIZED.json"
```

4. (Optional) Re-export the Excel template from the new JSON:

```bash
python3 -m panelin_improvements.cost_matrix_tools.excel_manager export \
  "wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_OPTIMIZED.json" \
  "wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_TEMPLATE.xlsx"
```

## Process B: Update using the Template (Excel is edited, then imported)

Use this if you want humans to edit **only** the generated template workbook.

1. Human edits: `wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_TEMPLATE.xlsx`
2. Import Excel → JSON (indices are rebuilt automatically):

```bash
python3 -m panelin_improvements.cost_matrix_tools.excel_manager import \
  "wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_TEMPLATE.xlsx" \
  "wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_OPTIMIZED.json" \
  "wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_OPTIMIZED.json"
```

Notes:
- The third argument (“base_json”) preserves meta/rules from the current JSON while importing updated rows.
- Canonical editable sheet is **`PRODUCTS`**.

## How GPT gets instant access

The KB Indexing Agent (`agente_kb_indexing.py`) now includes the optimized cost matrix JSON in its hierarchy:

- `KB_HIERARCHY["level_4_support"]` includes:
  - `wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_OPTIMIZED.json`

### Recommended access pattern

- **Direct lookup by code (fastest)**:
  - `get_cost_matrix_product("IAGRO30")`

- **List by category**:
  - `get_cost_matrix_products_by_category("isodec_eps")`

- **General search**:
  - `search_knowledge_base("IAGRO30")` (fast path triggers)
  - `search_knowledge_base("cinta butilo")` (normal hybrid search)

## Quick smoke tests

```bash
python3 - <<'PY'
from agente_kb_indexing import get_cost_matrix_product, get_cost_matrix_products_by_category
print(get_cost_matrix_product("IAGRO30")["product"]["nombre"])
print(get_cost_matrix_products_by_category("isoroof_foil")["count"])
PY
```

## Multi-supplier option (entire workbook export folder)

If you want a **single unified JSON** across *all* suppliers in the exported workbook folder:

```bash
python3 -m panelin_improvements.cost_matrix_tools.redesign_tool \
  "wiki/matriz de costos adaptacion /MATRIZ de COSTOS y VENTAS 2026 2.xlsx" \
  "wiki/matriz de costos adaptacion /redesigned/MATRIZ_Costos_Ventas_2026_ALL_SUPPLIERS_OPTIMIZED.json"
```

This adds `metadata.proveedor` based on the `.html` filename (sheet name).

