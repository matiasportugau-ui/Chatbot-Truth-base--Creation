## Panelin Quotation Agent v2 (2025/2026)

### Principio rector

- **El LLM orquesta**: interpreta lenguaje natural, extrae parámetros y decide qué herramienta llamar.
- **Python calcula**: toda aritmética financiera y validación es determinista (con `Decimal`).

### Fuente de verdad (SSOT)

- **Archivo**: `panelin_truth_bmcuruguay.json`
- **Esquema**: `schemas/panelin_truth_bmcuruguay.schema.json`

Regla: precios/fórmulas **no se hardcodean** en prompts ni en el LLM.

### Herramienta determinista principal

- **Tool**: `panelin.tools.quotation_calculator.calculate_panel_quote`
- **Garantía**: la salida siempre incluye `calculation_verified: true` y pasa `validate_quotation()`.

Además, el agente legacy (`agente_cotizacion_panelin.py`) expone este tool para Function Calling:

- **Nombre de tool**: `calculate_panel_quote`
- **Wrapper**: `calculate_panel_quote_agente(...)`

### Integración incremental (sin romper el sistema actual)

El repo ya contiene motores/agents legacy (`motor_cotizacion_panelin.py`, `agente_cotizacion_panelin.py`).
La ruta recomendada es:

1. Introducir herramientas deterministas nuevas (este módulo).
2. Migrar el agente a **single-agent + tools** (LangGraph-ready) llamando estas funciones.
3. Reemplazar gradualmente cálculos en float/hardcode por SSOT + `Decimal`.

