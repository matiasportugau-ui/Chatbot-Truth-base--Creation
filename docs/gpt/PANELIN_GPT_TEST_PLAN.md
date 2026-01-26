# Panelin GPT Test Plan
**Version**: 1.0
**Objective**: Verify Panelin adheres to Source-of-Truth and capabilities policies.

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

---

## 📝 Regression Checklist (Maintenance)

- [ ] Level 1 JSON matches current ERP prices.
- [ ] Code Interpreter does not error on CSV read.
- [ ] Autoportancia logic remains strict.
- [ ] Personalization triggers correctly.
