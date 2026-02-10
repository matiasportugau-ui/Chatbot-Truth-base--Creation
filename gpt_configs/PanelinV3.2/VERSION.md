# PanelinV3.2 — GPT Configuration Archive

**Version**: 3.2 (based on v3.1 2026-02-07)  
**Instructions**: Panelin BMC Assistant Pro v3.1 · BOM Completa + Validación Autoportancia  
**KB Version**: 7.0 (2026-02-07)  
**Archived**: 2026-02-10  
**Status**: Archived (superseded by PanelinV3.3)

---

## Description

This folder contains the GPT configuration files that were actively used before the PDF generation template improvements were introduced (PanelinV3.3). The actual system instructions used in GPT are in `INSTRUCCIONES_PANELIN_V3.2_ACTUAL.txt`.

### Key Features in V3.2

- ✅ 11-section compact system instructions (copy-paste ready)
- ✅ 6-phase quotation process with BOM (Paneles, Perfilería, Fijaciones, Selladores)
- ✅ Autoportancia validation v3.1 with `validate_autoportancia()` via Code Interpreter
- ✅ 4 KB levels: BMC_Base_Conocimiento → accessories_catalog → bom_rules → quotation_calculator_v3.py
- ✅ User personalization (Mauro, Martin, Rami, Carolina with access key)
- ✅ Commands: `/cotizar`, `/autoportancia`, `/estado`, `/evaluar_ventas`, `/entrenar`
- ✅ Business rules: USD, IVA 22% included, min slope 5%, internal derivation only

## What This Version Does NOT Include

- ❌ PDF professional generation (template v2.1 with branding BMC)
- ❌ Pre-generation validation checklist for PDF
- ❌ `unit_base` calculation logic (`unidad`, `ml`, `m²`) in instructions
- ❌ Standardized nomenclature enforcement (`Thickness_mm`, `Length_m`)
- ❌ `build_quote_pdf()` canonical function
- ❌ Error handling with text fallback for PDF
- ❌ `/pdf` command

## Files

| File | Description |
|------|-------------|
| **`INSTRUCCIONES_PANELIN_V3.2_ACTUAL.txt`** | **⭐ Actual GPT instructions used in production (V3.2)** |
| `Panelin_Asistente_Integral_BMC_config.json` | Original GPT config (v1 — basic capabilities) |
| `Panelin_Asistente_Integral_BMC_config_v2.0.json` | GPT config v2.3 (accessories + BOM) |
| `KB_Indexing_Expert_Agent_config.json` | KB indexing agent configuration |
| `Panelin Knowledge Base Assistant_config.json` | KB assistant agent configuration |
| `INSTRUCCIONES_PANELIN*.txt` | Legacy instruction variants (6 files) |
| `kb_analysis_report.json` | Knowledge base analysis report |
| `validation_fix_report.json` | Validation fix report |

## Upgrade Path

→ Upgrade to **PanelinV3.3** for PDF generation improvements with professional BMC branding template, pre-validation, and `/pdf` command.
