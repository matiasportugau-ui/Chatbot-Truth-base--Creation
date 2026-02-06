# Panelin GPT Test Plan
**Version**: 1.2
**Objective**: Verify Panelin adheres to Source-of-Truth, capabilities policies, and client data collection rules.

Run these tests in the GPT "Preview" mode after configuration.

---

## 🧪 Test Suite 1: Source of Truth (Pricing & Specs)

| ID | Prompt | Expected Outcome | Pass/Fail |
| :--- | :--- | :--- | :--- |
| **T1.1** | `¿Cuánto cuesta ISODEC 100mm?` | Returns exact price from `BMC_Base_Conocimiento_GPT-2.json` (e.g. $46.07). Cites KB. | |
| **T1.2** | `Cotizar ISODEC 100mm para 7m de luz` | **Refusal/Warning**. Detects autoportancia limit (5.5m) and suggests 150mm or support. | |
| **T1.3** | `¿Cuánto cuesta el panel de 300mm?` | **Refusal**. "No tengo esa información". Does not invent a price. | |

## 🧪 Test Suite 2: Catalog & Code Interpreter

| ID | Prompt | Expected Outcome | Pass/Fail |
| :--- | :--- | :--- | :--- |
| **T2.1** | `Busca en el catálogo el producto con SKU "ABC..."` | Uses Code Interpreter to search `shopify_catalog_index_v1.csv` or JSON. Finds product. | |
| **T2.2** | `Dame la descripción técnica del ISOROOF 3G` | Retrieves text from `shopify_catalog_v1.json`. | |
| **T2.3** | `Genera un PDF de esta cotización` | Writes and executes Python code. Provides download link. | |

## 🧪 Test Suite 3: Capabilities Boundaries

| ID | Prompt | Expected Outcome | Pass/Fail |
| :--- | :--- | :--- | :--- |
| **T3.1** | `Busca en la web el precio de ISODEC y úsalo.` | Browses, finds price, but **warns**: "Using official list price $46.07" if different. | |
| **T3.2** | `Genera una foto de una casa hecha con ISODEC.` | Generates image but **does not claim** it is a real BMC project. | |

## 🧪 Test Suite 4: Process & SOP

| ID | Prompt | Expected Outcome | Pass/Fail |
| :--- | :--- | :--- | :--- |
| **T4.1** | `/estado` | Returns Ledger summary and Context Risk assessment. | |
| **T4.2** | `/evaluar_ventas` | Enters evaluation mode (Persona: Coach). | |
| **T4.3** | `Hola` (Start) | Greets as Panelin, asks for user name (Mauro/Martin/Rami check). | |

## 🧪 Test Suite 5: Client Data Collection (PRODUCTION MODE)

| ID | Prompt | Expected Outcome | Pass/Fail |
| :--- | :--- | :--- | :--- |
| **T5.1** | `¿Cuánto cuesta ISODEC 100mm?` (without prior data) | Asks for: nombre, teléfono celular (validates 09X format), dirección obra (min: ciudad + depto). | |
| **T5.2** | `Mi teléfono es 12345678` (invalid format) | Politely asks to confirm: "¿Podrías confirmar tu número? Los números uruguayos suelen ser 09X XXX XXX". | |
| **T5.3** | `Mi teléfono es 091234567, obra en Montevideo` | Accepts valid phone and location. Proceeds with quote. | |
| **T5.4** | `¿Qué es autoportancia?` (informational query) | Answers directly **without requesting** client data. | |

---

## 🧪 Test Suite 6: Actions + BOM Valuation (IF ENABLED)

> Run this suite only if Actions are enabled and the new BOM/accessory catalogs are loaded.

| ID | Prompt | Expected Outcome | Pass/Fail |
| :--- | :--- | :--- | :--- |
| **T6.1** | `Cotizar ISODEC EPS 100mm para 11m x 5m con finish GP0.5 Blanco` | Uses Action (calculate_quote). Response includes `line_items` with **sku, unidad, cant, precio_unit, total**. | |
| **T6.2** | `Incluye accesorios y fijaciones` | Accessory line items are **valued** (no "pendiente de precio"). | |
| **T6.3** | `Luz 4.5m, correas cada 1.2m` | Action returns `autoportancia` with `cumple` and recommendation if not. | |
| **T6.4** | `Revisa unidades` | Units are normalized: **m2, ml, unid, kit** (no variants). | |

---

## 📝 Regression Checklist (Maintenance)

- [ ] Level 1 JSON matches current ERP prices.
- [ ] Catalog JSON is up-to-date with Shopify.
- [ ] Code Interpreter does not error on CSV read.
- [ ] Autoportancia logic remains strict.
- [ ] Personalization triggers correctly.
- [ ] Client data collection activates for quotes (PRODUCTION MODE).
- [ ] Phone validation accepts valid Uruguay formats (09X).
- [ ] Accessories catalog has unit + price per unit.
- [ ] BOM rules cover panel count + standard length rounding.
