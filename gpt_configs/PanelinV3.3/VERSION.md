# PanelinV3.3 — GPT Configuration with Enhanced PDF Generation

**Version**: 3.3  
**Instructions Version**: 2.5 Canonical - Full Capabilities + Accessories + BOM + Enhanced PDF Template  
**KB Version**: 7.0 (2026-02-10)  
**Created**: 2026-02-10  
**Status**: Current (ready to upload to GPT)

---

## Description

This folder contains the upgraded GPT configuration files with complete PDF generation improvements. This version builds on PanelinV3.2 by adding professional PDF quotation capabilities with robust validation and error handling.

## What's New in V3.3 (compared to V3.2)

### ✅ Enhanced PDF Generation (Template v2.1)
- **Pre-generation validation checklist**: Validates all required fields, `unit_base` consistency, and nomenclature before generating PDFs
- **Graceful error handling**: Logo fallback, text-based quotation fallback on PDF failure
- **Mandatory template blocks**: Logo header, formatted comments (BOLD/RED styling), bank transfer footer
- **`build_quote_pdf()` canonical function**: Single entry point for PDF generation
- **One-page-first rule**: Reduces comment font size before altering table layout

### ✅ Standardized Technical Nomenclature
- `Thickness_mm` for thickness (espesor)
- `Length_m` for length (largo)
- `unit_base` categories: `unidad`, `ml`, `m²`

### ✅ Unit Base Calculation Logic
- Clear formulas per `unit_base` type enforced in both calculations and PDF
- SKU 6842 special case documented (Gotero Lateral 100mm: `unit_base = unidad`)

### ✅ PDF Quality Checklist (v2.1)
- 12-point validation before PDF generation
- `validate_quotation_data()` function reference
- Logo file accessibility check

### ✅ Improved Error Messages
- Spanish-language error messages for user-facing issues
- `/pdf` command retry capability
- Detailed validation errors listing missing fields

## Files

| File | Description |
|------|-------------|
| `Panelin_GPT_config.json` | GPT config v2.5 (enhanced PDF + all capabilities) |
| `instructions/GPT_PDF_INSTRUCTIONS.md` | PDF generation guide v2.1 (enhanced) |
| `instructions/GPT_INSTRUCTIONS_PRICING.md` | Pricing logic and formulas |
| `instructions/GPT_OPTIMIZATION_ANALYSIS.md` | GPT optimization report |
| `instructions/PANELIN_KNOWLEDGE_BASE_GUIDE.md` | KB hierarchy and usage guide |
| `instructions/PANELIN_QUOTATION_PROCESS.md` | 5-phase quotation process |
| `instructions/PANELIN_TRAINING_GUIDE.md` | Training guide for sales staff |

## How to Upload to GPT

1. **System Instructions**: Copy the `instructions` field from `Panelin_GPT_config.json` into the GPT system prompt
2. **Knowledge Base Files**: Upload all files from `instructions/` as knowledge base documents
3. **Capabilities**: Enable Code Interpreter, Canvas, Web Browsing, and Image Generation as specified in config
4. **Conversation Starters**: Copy from `conversation_starters` in config JSON
5. **Logo**: Upload `Logo_BMC- PNG.png` to GPT files for PDF header

## Upgrade Path

- **From V3.2**: Replace system instructions and upload updated `GPT_PDF_INSTRUCTIONS.md`
- **To future versions**: This folder will be archived when V3.4+ is released
