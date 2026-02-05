# Panelin_GPT – Required Files to Run

Only these files are needed to configure and run the **Panelin BMC Assistant GPT**. Everything else in this folder is optional reference or removed.

---

## 1. Upload to GPT (Configure → Files)

| File | Path |
|------|------|
| pdf_generator.py | 01_UPLOAD_FILES/ |
| pdf_styles.py | 01_UPLOAD_FILES/ |
| bmc_logo.png | 01_UPLOAD_FILES/ |

## 2. Instructions (Copy to Configure → Instructions)

| File | Path |
|------|------|
| GPT_PDF_INSTRUCTIONS.md | 02_INSTRUCTIONS/ |
| INSTRUCCIONES_PANELIN_OPTIMIZADAS.txt | 02_INSTRUCTIONS/ |

(Optional: SYSTEM_INSTRUCTIONS_CANONICAL.md as alternate full instructions.)

## 3. Knowledge Base (Configure → Knowledge)

| File | Path |
|------|------|
| panelin_truth_bmcuruguay.json | 03_KNOWLEDGE_BASE/ |
| product_catalog.json | 03_KNOWLEDGE_BASE/ |
| LEDGER_CHECKPOINT.md | 03_KNOWLEDGE_BASE/ |

## 4. Configuration Reference

| File | Path |
|------|------|
| Panelin_Asistente_config.json | 04_CONFIGURATIONS/ |

Use this to verify GPT settings (name, model, tools, etc.).

---

## Removed as Unnecessary

- **01_UPLOAD_FILES/test_pdf.py** – Local test only; not uploaded to GPT.
- **04_CONFIGURATIONS/KB_Indexing_Expert_Agent_config.json** – Different agent (KB Indexing), not Panelin GPT.
- **05_DOCUMENTATION/QUICK_START.md** – Outdated paths; README has the correct Quick Start.

## Optional Reference (Keep or Delete)

- **05_DOCUMENTATION/** – CAPABILITIES_POLICY.md, MAINTENANCE.md, SECURITY_POLICY.md.
- **06_DEPLOYMENT/** – DEPLOYMENT_CHECKLIST.md, FINAL_STATUS.txt.
