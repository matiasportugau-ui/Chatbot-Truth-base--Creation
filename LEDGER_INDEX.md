# 📚 Ledger Checkpoint Index

**Quick Navigation for 2026-01-28 Ledger Checkpoint Documentation**

---

## 🎯 Start Here

**New to the ledger checkpoint?** Start with:

1. **[Corrections Applied Summary](CORRECTIONS_APPLIED_2026-01-28.md)** ← Visual summary, what changed
2. **[Quick Reference - Unit Base](QUICK_REFERENCE_UNIT_BASE.md)** ← Fast lookup for calculations
3. **[Ledger Checkpoint Full](LEDGER_CHECKPOINT_2026-01-28.md)** ← Complete context

---

## 📖 Documentation Structure

### Level 1: Quick Reference
**For**: Developers, GPT, quick lookups

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [Quick Reference - Unit Base](QUICK_REFERENCE_UNIT_BASE.md) | Fast lookup for unit_base calculation formulas | 2 min |
| [Corrections Applied](CORRECTIONS_APPLIED_2026-01-28.md) | Visual summary of what changed | 3 min |

### Level 2: Complete Context
**For**: Understanding full context, implementation details

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [Ledger Checkpoint 2026-01-28](LEDGER_CHECKPOINT_2026-01-28.md) | Complete checkpoint documentation | 10 min |
| [Implementation Summary](LEDGER_IMPLEMENTATION_SUMMARY.md) | Technical implementation details | 8 min |

### Level 3: Technical Documentation
**For**: PDF generation, pricing, product data

| Document | Purpose | Location |
|----------|---------|----------|
| PDF Generation Instructions | How to generate PDFs with correct logic | `panelin_reports/GPT_PDF_INSTRUCTIONS.md` |
| Pricing Instructions | How to use pricing data correctly | `pricing/GPT_INSTRUCTIONS_PRICING.md` |
| Product Corrections Registry | Track product data corrections | `pricing/config/product_corrections_2026-01-28.json` |
| Enrichment Rules | Product data enrichment configuration | `pricing/config/product_enrichment_rules.json` |

### Level 4: Scripts & Tools
**For**: Applying corrections, automation

| Script | Purpose | Location |
|--------|---------|----------|
| Apply SKU 6842 Correction | Automated correction application | `pricing/tools/apply_sku_6842_correction.py` |
| Test PDF Generation | Test PDF creation | `panelin_reports/test_pdf_generation.py` |

---

## 🔑 Key Concepts

### 1. Unit Base Calculation Logic

**File**: [Quick Reference - Unit Base](QUICK_REFERENCE_UNIT_BASE.md)

```
unidad → cantidad × price
ml     → cantidad × Length_m × price
m²     → área_total × price
```

### 2. SKU 6842 Correction

**File**: [Ledger Checkpoint](LEDGER_CHECKPOINT_2026-01-28.md#corrección-aplicada-gotero-isodec-eps-100mm)

Changed: `unit_base` from `"metro_lineal"` to `"unidad"`

### 3. Technical Nomenclature

**File**: [Ledger Checkpoint](LEDGER_CHECKPOINT_2026-01-28.md#nomenclatura-técnica-estandarizada)

Standards:
- `Thickness_mm` (not: espesor, thickness)
- `Length_m` (not: largo, length)
- `unit_base` (not: unidad, unit)

---

## 🚀 Common Tasks

### Task 1: Generate a Quotation
1. Read: [Quick Reference - Unit Base](QUICK_REFERENCE_UNIT_BASE.md)
2. Check product's `unit_base` field
3. Apply correct formula
4. Follow: [Pricing Instructions](pricing/GPT_INSTRUCTIONS_PRICING.md)

### Task 2: Generate a PDF
1. Read: [PDF Instructions](panelin_reports/GPT_PDF_INSTRUCTIONS.md)
2. Use BMC logo from: `panelin_reports/assets/bmc_logo.png`
3. Apply unit_base logic from: [Quick Reference](QUICK_REFERENCE_UNIT_BASE.md)

### Task 3: Apply SKU 6842 Correction
1. Read: [Corrections Applied](CORRECTIONS_APPLIED_2026-01-28.md#2-sku-6842-product-data-correction)
2. Run: `python3 pricing/tools/apply_sku_6842_correction.py`
3. Validate output

### Task 4: Understand What Changed
1. Read: [Corrections Applied Summary](CORRECTIONS_APPLIED_2026-01-28.md)
2. Review: [Changelog Entry](KB_CHANGELOG_v6.0.md)

---

## 📊 Documentation Map

```
LEDGER_INDEX.md (you are here)
│
├─ Quick References (Start Here)
│  ├─ CORRECTIONS_APPLIED_2026-01-28.md
│  └─ QUICK_REFERENCE_UNIT_BASE.md
│
├─ Complete Context
│  ├─ LEDGER_CHECKPOINT_2026-01-28.md
│  └─ LEDGER_IMPLEMENTATION_SUMMARY.md
│
├─ Technical Documentation
│  ├─ panelin_reports/GPT_PDF_INSTRUCTIONS.md
│  ├─ pricing/GPT_INSTRUCTIONS_PRICING.md
│  └─ KB_CHANGELOG_v6.0.md
│
├─ Configuration
│  ├─ pricing/config/product_corrections_2026-01-28.json
│  └─ pricing/config/product_enrichment_rules.json
│
└─ Scripts & Tools
   ├─ pricing/tools/apply_sku_6842_correction.py
   └─ panelin_reports/test_pdf_generation.py
```

---

## 🔍 Search by Topic

### Calculations
- **Unit base logic**: [Quick Reference](QUICK_REFERENCE_UNIT_BASE.md#calculation-formulas)
- **PDF calculations**: [PDF Instructions](panelin_reports/GPT_PDF_INSTRUCTIONS.md#unit-base-calculation-logic)
- **Pricing formulas**: [Pricing Instructions](pricing/GPT_INSTRUCTIONS_PRICING.md#unit-base-calculation-logic)

### Product Data
- **SKU 6842 correction**: [Ledger Checkpoint](LEDGER_CHECKPOINT_2026-01-28.md#corrección-aplicada-gotero-isodec-eps-100mm)
- **Corrections registry**: [Product Corrections](pricing/config/product_corrections_2026-01-28.json)
- **Enrichment rules**: [Enrichment Rules](pricing/config/product_enrichment_rules.json)

### Standards
- **Nomenclature**: [Ledger Checkpoint](LEDGER_CHECKPOINT_2026-01-28.md#nomenclatura-técnica-estandarizada)
- **Field names**: [Quick Reference](QUICK_REFERENCE_UNIT_BASE.md#standardized-field-names)

### Assets
- **BMC logo**: `panelin_reports/assets/bmc_logo.png`
- **Location documented**: [Ledger Checkpoint](LEDGER_CHECKPOINT_2026-01-28.md#assets)

---

## ✅ Quick Checklist

**Have you applied the corrections?**

- [ ] Read corrections summary
- [ ] Understood unit_base logic
- [ ] Applied SKU 6842 correction (run script)
- [ ] Tested PDF generation with BMC logo
- [ ] Validated calculations with new logic

---

## 📞 Need Help?

### Question Type → Reference Document

| Question | Document |
|----------|----------|
| "How do I calculate a quotation?" | [Quick Reference - Unit Base](QUICK_REFERENCE_UNIT_BASE.md) |
| "What changed in this update?" | [Corrections Applied](CORRECTIONS_APPLIED_2026-01-28.md) |
| "How do I apply the correction?" | [Implementation Summary](LEDGER_IMPLEMENTATION_SUMMARY.md#next-steps) |
| "How do I generate a PDF?" | [PDF Instructions](panelin_reports/GPT_PDF_INSTRUCTIONS.md) |
| "What is the unit_base for product X?" | [Pricing Instructions](pricing/GPT_INSTRUCTIONS_PRICING.md) |
| "What files were created?" | [Implementation Summary](LEDGER_IMPLEMENTATION_SUMMARY.md#files-createdmodified) |

---

## 🎯 Next Actions

1. **Review**: [Corrections Applied Summary](CORRECTIONS_APPLIED_2026-01-28.md)
2. **Apply**: Run `pricing/tools/apply_sku_6842_correction.py`
3. **Test**: Generate a test PDF with BMC logo
4. **Validate**: Check SKU 6842 calculation in a quotation

---

**Index Version**: 1.0  
**Last Updated**: 2026-01-28  
**Status**: ✅ Complete

---

**📌 Bookmark this page** for quick access to all ledger checkpoint documentation!
