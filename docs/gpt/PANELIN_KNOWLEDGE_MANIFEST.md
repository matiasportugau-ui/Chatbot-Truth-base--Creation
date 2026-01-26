# Panelin Knowledge Manifest
**Version**: 1.0
**Last Updated**: 2026-01-25

This document defines the **authoritative list of files** to be uploaded to the Panelin GPT Knowledge Base, their priority order, and purpose.

---

## 📂 Upload Manifest

**Total Files**: 11
**Upload Strategy**: Strict priority order (Level 1 first).

| Priority | Level | Filename | Path in Repo | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Level 1 (MASTER)** | `BMC_Base_Conocimiento_GPT-2.json` | `BMC_Base_Conocimiento_GPT-2.json` | **Source of Truth**. Prices, formulas, specs. |
| **2** | **Level 2 (Catalog)** | `shopify_catalog_v1.json` | `catalog/out/shopify_catalog_v1.json` | Product descriptions, variants, images. **NO prices.** |
| **3** | **Level 4 (Process)** | `PANELIN_KNOWLEDGE_BASE_GUIDE.md` | `PANELIN_KNOWLEDGE_BASE_GUIDE.md` | Guide to the KB structure itself. |
| **4** | **Level 4 (Process)** | `PANELIN_QUOTATION_PROCESS.md` | `PANELIN_QUOTATION_PROCESS.md` | 5-phase quotation workflow rules. |
| **5** | **Level 4 (Process)** | `PANELIN_TRAINING_GUIDE.md` | `PANELIN_TRAINING_GUIDE.md` | Sales training and evaluation rubrics. |
| **6** | **Level 4 (Process)** | `panelin_context_consolidacion_sin_backend.md` | `panelin_context_consolidacion_sin_backend.md` | SOP commands (`/estado`, `/consolidar`). |
| **7** | **Level 2 (Validation)** | `BMC_Base_Unificada_v4.json` | `Files /BMC_Base_Unificada_v4.json` | Historical cross-reference. |
| **8** | **Level 3 (Dynamic)** | `panelin_truth_bmcuruguay_web_only_v2.json` | `panelin_truth_bmcuruguay_web_only_v2.json` | Web snapshot for price verification. |
| **9** | **Level 4 (Support)** | `Aleros -2.rtf` | `Files /Aleros -2.rtf` | Technical rules for overhangs (Aleros). |
| **10** | **Level 4 (Index)** | `shopify_catalog_index_v1.csv` | `catalog/out/shopify_catalog_index_v1.csv` | CSV index for Code Interpreter lookups. |
| **11** | **Level 4 (Support)** | `BMC_Catalogo_Completo_Shopify (1).json` | `BMC_Catalogo_Completo_Shopify (1).json` | Legacy catalog backup. |

---

## ⛔ Exclude List (NEVER Upload)

The following files contain sensitive data or secrets and **MUST NOT** be uploaded to the GPT:

1. **Secrets**: `.env`, any file with API keys.
2. **Internal Cost Data**:
   - `BROMYROS_Base_Costos_Precios_2026.json`
   - `MATRIZ de COSTOS y VENTAS 2026.xlsx`
   - Any file containing "Costo", "Margen", or "Utilidad".
3. **Duplicates**: Do not upload `Files /panelin_truth_bmcuruguay_web_only_v2.json` (duplicate of root file).

---

## 🔄 Refresh Cadence

- **Level 1 (Master)**: Update manually when BMC official prices change. Requires re-upload and version bump.
- **Level 2 (Catalog)**: Refresh weekly or after major Shopify updates:
  ```bash
  python3 catalog/export_shopify_catalog.py path/to/products_export.csv --quality-report
  ```
  Then re-upload `catalog/out/shopify_catalog_v1.json`.
- **Level 3 (Dynamic)**: Refresh monthly via web scraper.

---

## 📖 Usage Guidance for GPT

**How Panelin should use the catalog + pricing master together:**

1. **User asks**: "Tell me about ISOROOF 3G"
   - Step 1: Search `shopify_catalog_v1.json` → find handle, description, variants
   - Step 2: If user asks for price → get from `BMC_Base_Conocimiento_GPT-2.json`

2. **User asks**: "What's the price of ISODEC 100mm?"
   - Step 1: Collect client data (PRODUCTION MODE): nombre, teléfono, dirección obra
   - Step 2: Get price from `BMC_Base_Conocimiento_GPT-2.json`
   - Step 3: Optionally enhance with catalog description from `shopify_catalog_v1.json`

3. **User provides SKU**: "I need product SKU XYZ123"
   - Step 1: Use Code Interpreter to search `shopify_catalog_index_v1.csv` or `indexes.sku_to_handle` in JSON
   - Step 2: Resolve SKU → handle → product description
   - Step 3: For pricing → always use `BMC_Base_Conocimiento_GPT-2.json`
