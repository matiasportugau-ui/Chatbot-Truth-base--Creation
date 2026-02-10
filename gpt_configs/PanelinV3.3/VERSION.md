# PanelinV3.3 — GPT Configuration with Enhanced PDF Generation

**Version**: 3.3  
**Instructions**: Panelin BMC Assistant Pro v3.3 · BOM Completa + Validación Autoportancia + PDF Profesional  
**KB Version**: 7.0 (2026-02-10)  
**Created**: 2026-02-10  
**Status**: Current (ready to upload to GPT)  
**Based on**: PanelinV3.2 (v3.1 actual instructions)

---

## Description

This folder contains the upgraded GPT configuration that evolves directly from the V3.2 actual instructions (11-section compact format). V3.3 adds a new **Section 12: PDF Profesional** and enhances several existing sections to integrate PDF generation capabilities seamlessly.

## What's New in V3.3 (compared to V3.2)

### ✅ New Section 12: PDF Profesional
- Professional PDF quotation generation with BMC Uruguay branding
- `/pdf` command to generate PDF from current quotation
- `build_quote_pdf()` canonical function via Code Interpreter
- Mandatory template blocks: Logo header, formatted comments (BOLD/RED), bank transfer footer
- Pre-generation validation checklist (client name, products, unit_base, autoportancia)
- Graceful error handling: logo fallback, text fallback on failure

### ✅ Unit Base Calculation Logic (Section 5 - F5 enhanced)
- `unidad`: cantidad × sale_sin_iva
- `ml`: cantidad × Length_m × sale_sin_iva
- `m²`: área_total × sale_sin_iva
- SKU 6842 special case documented (Gotero Lateral 100mm: `unit_base = unidad`)

### ✅ Standardized Technical Nomenclature (Section 12)
- `Thickness_mm` for espesor, `Length_m` for largo
- `unit_base` categories: `unidad`, `ml`, `m²`

### ✅ Enhanced KB Hierarchy (Section 4)
- Added Nivel 1.5 (bromyros_pricing_gpt_optimized.json) for fast lookups
- Added Nivel 1.6 (shopify catalog — descriptions/images only)
- Added Niveles 2-4 for validation, dynamic, and support files
- Added GPT_PDF_INSTRUCTIONS.md to Level 4 support

### ✅ New Command: `/pdf` (Section 9)
- Generates professional PDF from current quotation
- Integrates with Code Interpreter + reportlab

### ✅ Updated Capabilities (Section 11)
- Code Interpreter now explicitly includes `build_quote_pdf()` for PDF generation

### ✅ Section 6 Presentation (F6) Enhanced
- Now offers PDF generation after presenting quotation

## Files

| File | Description |
|------|-------------|
| **`Panelin_GPT_config.json`** | GPT config v3.3 (complete JSON with instructions + metadata) |
| **`INSTRUCCIONES_PANELIN_V3.3.txt`** | ⭐ Copy-paste ready instructions for GPT (12 sections) |
| `instructions/GPT_PDF_INSTRUCTIONS.md` | PDF generation guide v2.1 (detailed workflow + code) |
| `instructions/GPT_INSTRUCTIONS_PRICING.md` | Pricing logic and formulas |
| `instructions/GPT_OPTIMIZATION_ANALYSIS.md` | GPT optimization report |
| `instructions/PANELIN_KNOWLEDGE_BASE_GUIDE.md` | KB hierarchy and usage guide |
| `instructions/PANELIN_QUOTATION_PROCESS.md` | 5-phase quotation process |
| `instructions/PANELIN_TRAINING_GUIDE.md` | Training guide for sales staff |

## How to Upload to GPT

1. **System Instructions**: Copy content from `INSTRUCCIONES_PANELIN_V3.3.txt` into the GPT system prompt (or use the `instructions` field from `Panelin_GPT_config.json`)
2. **Knowledge Base Files**: Upload all files listed in `deployment.files_to_upload` from `Panelin_GPT_config.json`
3. **Logo**: Upload `Logo_BMC- PNG.png` to GPT files for PDF header
4. **Capabilities**: Enable Code Interpreter (CRITICAL), Canvas, Web Browsing, Image Generation
5. **Conversation Starters**: Copy from `conversation_starters` in config JSON

## Changes from V3.2 → V3.3 (Summary)

| Section | V3.2 | V3.3 |
|---------|------|------|
| 1. Identity | Same | + "PDFs profesionales con branding BMC" in mission |
| 4. KB Hierarchy | 4 levels (1, 1A, 1B, 1C) | 8 levels (1, 1A, 1B, 1C, 1.5, 1.6, 2, 3, 4) |
| 5. F5 Valorización | Basic total | + unit_base logic (unidad/ml/m²) |
| 5. F6 Presentación | Table only | + "Ofrecer generar PDF profesional" |
| 7. Style | 4 points | + "Ofrecer PDF cuando cotización completa" |
| 8. Business Rules | Basic | + shipping ref 280 USD, + website URL |
| 9. Commands | 7 commands | + `/pdf` (NEW) |
| 11. Capabilities | Code Interpreter basic | + build_quote_pdf() explicit |
| 12. PDF Generation | ❌ Not present | ✅ NEW full section |

## Upgrade Path

- **From V3.2**: Replace system instructions with `INSTRUCCIONES_PANELIN_V3.3.txt` and upload `GPT_PDF_INSTRUCTIONS.md` + `Logo_BMC- PNG.png`
- **To future versions**: This folder will be archived when V3.4+ is released
