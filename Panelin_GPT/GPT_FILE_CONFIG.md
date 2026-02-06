# GPT Panelin – File Config (v3.0 BOM Completa)

Single reference for **which files** to use when configuring the **Panelin - BMC Assistant Pro** GPT.

**Config file (reference):** `04_CONFIGURATIONS/Panelin_Asistente_config.json`  
**Instructions (canonical):** `02_INSTRUCTIONS/SYSTEM_INSTRUCTIONS_CANONICAL.md`

---

## 1. Instructions (Configure → Instructions)

| File | Path | Use |
|------|------|-----|
| **SYSTEM_INSTRUCTIONS_CANONICAL.md** | 02_INSTRUCTIONS/ | **Primary** – Full system instructions v3.0 (BOM, slash-commands, 6 phases) |
| GPT_PDF_INSTRUCTIONS.md | 02_INSTRUCTIONS/ | PDF generation workflow |
| INSTRUCCIONES_PANELIN_OPTIMIZADAS.txt | 02_INSTRUCTIONS/ | Alternate / legacy instructions |

---

## 2. Knowledge Base (Configure → Knowledge)

Upload these files so the GPT can read them. **Order = priority (Nivel 1 first).**

### Nivel 1 – Master (precios paneles y fórmulas)

| File | Path | Role |
|------|------|------|
| BMC_Base_Conocimiento_GPT-2.json | 03_KNOWLEDGE_BASE/ or project root | Precios paneles, fórmulas, autoportancia, reglas negocio |
| bromyros_pricing_master.json | (wherever you store it) | Master pricing BROMYROS |
| bromyros_pricing_gpt_optimized.json | (wherever you store it) | Lookup rápido por SKU/familia |

### Nivel 1A – Accesorios (BOM v3.0)

| File | Path | Role |
|------|------|------|
| **accessories_catalog.json** | Project root or 03_KNOWLEDGE_BASE/ | Precios perfilería, fijaciones, selladores (97 ítems) |

### Nivel 1B – BOM Rules (BOM v3.0)

| File | Path | Role |
|------|------|------|
| **bom_rules.json** | Project root or 03_KNOWLEDGE_BASE/ | Reglas paramétricas BOM, autoportancia consolidada, kits fijación |

### Nivel 1.5 – Catálogo (sin precios)

| File | Path | Role |
|------|------|------|
| shopify_catalog_v1.json | (catalog output) | Descripciones, variantes, imágenes |
| shopify_catalog_index_v1.csv | (optional) | Índice rápido catálogo |

### Nivel 2–4 – Validación y soporte

| File | Path | Role |
|------|------|------|
| BMC_Base_Unificada_v4.json | 03_KNOWLEDGE_BASE/ or project | Cross-reference histórico |
| panelin_truth_bmcuruguay_web_only_v2.json | 03_KNOWLEDGE_BASE/ or project | Precios web (validar vs Nivel 1) |
| panelin_truth_bmcuruguay.json | 03_KNOWLEDGE_BASE/ | Truth base principal |
| product_catalog.json | 03_KNOWLEDGE_BASE/ | Catálogo productos con precios |
| PANELIN_KNOWLEDGE_BASE_GUIDE.md | docs or 02_INSTRUCTIONS/ | Guía jerarquía KB |
| PANELIN_QUOTATION_PROCESS.md | docs or 02_INSTRUCTIONS/ | Proceso cotización (6 fases v3.0) |
| PANELIN_TRAINING_GUIDE.md | docs or 02_INSTRUCTIONS/ | Entrenamiento |
| GPT_INSTRUCTIONS_PRICING.md | docs or 02_INSTRUCTIONS/ | Instrucciones pricing |
| GPT_PDF_INSTRUCTIONS.md | 02_INSTRUCTIONS/ | Instrucciones PDF |
| panelin_context_consolidacion_sin_backend.md | docs | Workflow y comandos SOP |
| Aleros -2.rtf | (if used) | Reglas técnicas aleros |
| README.md | Panelin_GPT/ | Referencia proyecto |

---

## 3. Upload files (Configure → Files – Code Interpreter / tools)

| File | Path | Role |
|------|------|------|
| pdf_generator.py | 01_UPLOAD_FILES/ | Generación PDF cotizaciones |
| pdf_styles.py | 01_UPLOAD_FILES/ | Estilos PDF |
| bmc_logo.png | 01_UPLOAD_FILES/ | Logo BMC para PDF |

---

## 4. Checklist mínima para BOM v3.0

Para que el GPT haga **cotización BOM completa** (paneles + accesorios valorizados), debe tener en la KB:

- [ ] BMC_Base_Conocimiento_GPT-2.json  
- [ ] **accessories_catalog.json**  
- [ ] **bom_rules.json**  
- [ ] SYSTEM_INSTRUCTIONS_CANONICAL.md (o instrucciones que referencien estos 3 + proceso 6 fases)

Opcional pero recomendado: shopify_catalog_v1.json, PANELIN_QUOTATION_PROCESS.md.

---

## 5. Ubicación de archivos en este repo

| Archivo | Ubicación típica |
|---------|-------------------|
| BMC_Base_Conocimiento_GPT-2.json | `03_KNOWLEDGE_BASE/` o raíz del repo |
| accessories_catalog.json | Raíz del repo o `panelin/data/` |
| bom_rules.json | Raíz del repo o `panelin/data/` |
| SYSTEM_INSTRUCTIONS_CANONICAL.md | `Panelin_GPT/02_INSTRUCTIONS/` y `docs/gpt/` |
| Panelin_Asistente_config.json | `Panelin_GPT/04_CONFIGURATIONS/` |

---

**Versión:** 3.0 (BOM Completa)  
**Fecha:** 2026-02-06
