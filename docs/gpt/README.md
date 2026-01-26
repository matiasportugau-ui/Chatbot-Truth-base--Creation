# Panelin GPT Builder — Documentation Pack
**Version**: 1.0 (Full Capabilities)  
**Created**: 2026-01-25  
**Status**: Ready for GPT Builder configuration

---

## What's in This Folder

Complete documentation pack for creating, testing, and maintaining the **Panelin GPT (Internal)** in the ChatGPT GPT Builder.

---

## Quick Start (Copy/Paste Guide)

**Use this file**: [`PANELIN_GPT_BUILDER_QUICK_FILL.md`](PANELIN_GPT_BUILDER_QUICK_FILL.md)

It contains step-by-step copy/paste instructions for every GPT Builder field.

---

## Documentation Files

### 1. Configuration & Setup
- **[`PANELIN_GPT_BUILDER_CONFIG.md`](PANELIN_GPT_BUILDER_CONFIG.md)**: Complete Builder field configuration
- **[`PANELIN_GPT_BUILDER_QUICK_FILL.md`](PANELIN_GPT_BUILDER_QUICK_FILL.md)**: 10-step copy/paste quick guide ⭐ **START HERE**

### 2. Core Instructions
- **[`PANELIN_SYSTEM_INSTRUCTIONS_CANONICAL.md`](PANELIN_SYSTEM_INSTRUCTIONS_CANONICAL.md)**: Canonical system prompt (paste into Builder "Instrucciones" field)

### 3. Knowledge Base
- **[`PANELIN_KNOWLEDGE_MANIFEST.md`](PANELIN_KNOWLEDGE_MANIFEST.md)**: Authoritative list of 11 files to upload, with priority order

### 4. Policies
- **[`PANELIN_CAPABILITIES_POLICY.md`](PANELIN_CAPABILITIES_POLICY.md)**: Rules for web/code/image/canvas usage
- **[`PANELIN_GPT_SECURITY_POLICY.md`](PANELIN_GPT_SECURITY_POLICY.md)**: Data classification, do-not-upload list, access control

### 5. Testing
- **[`PANELIN_GPT_TEST_PLAN.md`](PANELIN_GPT_TEST_PLAN.md)**: 5 test suites with pass/fail criteria (20+ tests)

### 6. Operations
- **[`PANELIN_GPT_MAINTENANCE.md`](PANELIN_GPT_MAINTENANCE.md)**: Maintenance runbook (KB updates, versioning, reindex waits)
- **[`PANELIN_CHANGELOG.md`](PANELIN_CHANGELOG.md)**: Version history for Level 1 KB + instructions

### 7. Optional (Future)
- **[`PANELIN_ACTIONS_SPEC.md`](PANELIN_ACTIONS_SPEC.md)**: Actions specification for backend API integration (not required for MVP)

---

## Key Features of This Setup

### New in v1.0
- ✅ **Full capabilities enabled**: Web, Canvas, Image, Code Interpreter
- ✅ **Shopify catalog integration**: `shopify_catalog_v1.json` for product descriptions (no prices)
- ✅ **Client data collection**: Requires nombre, teléfono (validated Uruguay 09X), dirección obra before formal quotes
- ✅ **Production mode flag**: Can toggle off during training/testing

### Source of Truth Model
- **Level 1**: `BMC_Base_Conocimiento_GPT-2.json` (prices, formulas, specs) — **ALWAYS WINS**
- **Level 1.5**: `shopify_catalog_v1.json` (descriptions, variants, images) — **NO PRICES**
- **Level 2-4**: Validation, dynamic snapshots, support docs

### Capabilities Policies
- **Web browsing**: Level 5 (non-authoritative); never overrides Level 1 prices
- **Code Interpreter**: Required for PDFs, CSV lookups, formula verification
- **Image generation**: Educational diagrams only, never claim real photos
- **Canvas**: Long-form outputs (quotes, training docs)

---

## How to Use This Pack

### For Initial GPT Creation
1. Open [`PANELIN_GPT_BUILDER_QUICK_FILL.md`](PANELIN_GPT_BUILDER_QUICK_FILL.md)
2. Follow steps 1–10
3. Copy/paste from the files it references
4. Upload Knowledge files in exact order
5. Enable all capabilities
6. Save as "Only me" (internal)

### For Testing
1. Open the GPT Preview
2. Run tests from [`PANELIN_GPT_TEST_PLAN.md`](PANELIN_GPT_TEST_PLAN.md)
3. Check all 5 test suites (20+ tests)
4. Mark pass/fail in the table
5. Fix failures by updating instructions or KB files

### For Maintenance
1. When Level 1 changes: follow [`PANELIN_GPT_MAINTENANCE.md`](PANELIN_GPT_MAINTENANCE.md)
2. When catalog changes: regenerate using `python3 catalog/export_shopify_catalog.py`
3. Update [`PANELIN_CHANGELOG.md`](PANELIN_CHANGELOG.md)
4. Rerun regression tests

---

## File Map (Where Everything Lives)

```
Chatbot-Truth-base--Creation-1/
│
├── docs/gpt/                          ← YOU ARE HERE (governance docs)
│   ├── README.md                      ← This file
│   ├── PANELIN_GPT_BUILDER_QUICK_FILL.md    ⭐ START HERE
│   ├── PANELIN_SYSTEM_INSTRUCTIONS_CANONICAL.md
│   ├── PANELIN_KNOWLEDGE_MANIFEST.md
│   ├── PANELIN_GPT_BUILDER_CONFIG.md
│   ├── PANELIN_CAPABILITIES_POLICY.md
│   ├── PANELIN_GPT_TEST_PLAN.md
│   ├── PANELIN_GPT_MAINTENANCE.md
│   ├── PANELIN_GPT_SECURITY_POLICY.md
│   ├── PANELIN_CHANGELOG.md
│   └── PANELIN_ACTIONS_SPEC.md
│
├── BMC_Base_Conocimiento_GPT-2.json   ← Level 1 Master (upload FIRST)
├── catalog/out/
│   ├── shopify_catalog_v1.json        ← Level 1.5 Catalog (upload 2nd)
│   ├── shopify_catalog_index_v1.csv   ← CSV Index
│   └── shopify_catalog_quality.md     ← Quality report
│
├── PANELIN_KNOWLEDGE_BASE_GUIDE.md    ← Process anchor
├── PANELIN_QUOTATION_PROCESS.md       ← Process anchor
├── PANELIN_TRAINING_GUIDE.md          ← Process anchor
├── panelin_context_consolidacion_sin_backend.md  ← SOP commands
│
├── Files /
│   ├── BMC_Base_Unificada_v4.json     ← Level 2 Validation
│   ├── Aleros -2.rtf                  ← Level 4 Support
│   └── panelin_truth_bmcuruguay_catalog_v2_index.csv
│
├── panelin_truth_bmcuruguay_web_only_v2.json  ← Level 3 Dynamic (root version)
└── BMC_Catalogo_Completo_Shopify (1).json     ← Optional legacy
```

---

## What's Different from Previous Setups

### New Components
1. **Shopify catalog system** (`catalog/out/shopify_catalog_v1.json`)
   - Clean separation: catalog = descriptions, KB master = prices
   - Search-optimized with `search_document` field
   - CSV index for Code Interpreter lookups

2. **Client data collection** (PRODUCTION MODE)
   - Requires: nombre, teléfono (09X validated), dirección obra
   - Triggers before formal quotes/prices
   - Toggleable for training mode

3. **Full capabilities enabled** with strict policies
   - All toggles ON (web, code, image, canvas)
   - Each capability has clear allowed/forbidden uses
   - Policies prevent capabilities from breaking Source-of-Truth

### Unified Documentation
- One canonical instructions source (no more drift between variants)
- Complete governance pack in `docs/gpt/`
- Maintenance procedures defined

---

## Support

- **Questions about setup**: See [`PANELIN_GPT_BUILDER_QUICK_FILL.md`](PANELIN_GPT_BUILDER_QUICK_FILL.md)
- **Questions about testing**: See [`PANELIN_GPT_TEST_PLAN.md`](PANELIN_GPT_TEST_PLAN.md)
- **Questions about maintenance**: See [`PANELIN_GPT_MAINTENANCE.md`](PANELIN_GPT_MAINTENANCE.md)
- **Questions about security**: See [`PANELIN_GPT_SECURITY_POLICY.md`](PANELIN_GPT_SECURITY_POLICY.md)

---

**Last Updated**: 2026-01-25  
**Maintainer**: BMC Uruguay AI Team  
**License**: Internal Use Only
