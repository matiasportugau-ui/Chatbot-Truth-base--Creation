# Quick Reference: Unit Base Calculation Logic

**Version**: 1.0  
**Date**: 2026-01-28  
**Context**: Ledger Checkpoint 2026-01-28

---

## 🎯 TL;DR

**Before calculating any quotation subtotal, CHECK the `unit_base` field!**

---

## 📐 Standardized Field Names

| Field | Use | Example |
|-------|-----|---------|
| `Thickness_mm` | Product thickness | `100` |
| `Length_m` | Product length | `3.00` |
| `unit_base` | Unit of measurement | `"unidad"` |

---

## 🧮 Calculation Formulas

### Case 1: `unit_base = "unidad"`

```
Subtotal = cantidad × sale_sin_iva
```

**Example**:
- Product: Gotero Lateral 100mm (SKU 6842)
- Quantity: 8 pieces
- Price s/IVA: $20.77
- Calculation: `8 × $20.77 = $166.16`

**❌ WRONG**: `8 × 3.0 × $20.77 = $498.48` ← Don't multiply by length!

---

### Case 2: `unit_base = "ml"` (metro lineal)

```
Subtotal = cantidad × Length_m × sale_sin_iva
```

**Example**:
- Product: Perfil U 50mm
- Quantity: 10 pieces (each 3m)
- Price s/IVA: $3.90/ml
- Calculation: `10 × 3.0 × $3.90 = $117.00`

---

### Case 3: `unit_base = "m²"`

```
Subtotal = área_total × sale_sin_iva
```

**Example**:
- Product: Isopanel EPS 50mm
- Area: 300 m²
- Price s/IVA: $33.21/m²
- Calculation: `300 × $33.21 = $9,963.00`

---

## 🔍 How to Identify Unit Base

1. **Check JSON field**: `product.unit_base`
2. **Common patterns**:
   - Panels → usually `"m²"`
   - Profiles (3m pieces sold as units) → `"unidad"`
   - Profiles (sold per meter) → `"ml"`
   - Accessories → varies, check individually

---

## ⚠️ Critical Cases

### Goteros (SKU 6842 and similar)

```json
{
  "sku": "6842",
  "name": "Perf. Ch. Gotero Lateral 100mm - (3m)",
  "unit_base": "unidad",  // ← Note: unidad, not ml!
  "length_m": 3.00
}
```

**Why `unidad`?**
- Sold as complete 3m pieces
- Price is per piece, not per meter
- Client orders "8 goteros", not "24 meters"

---

## 📋 Checklist for Every Quotation

- [ ] Read `unit_base` from product JSON
- [ ] Apply correct formula based on unit_base
- [ ] For `unidad`: DO NOT multiply by length
- [ ] For `ml`: DO multiply by length
- [ ] For `m²`: Calculate area first
- [ ] Validate total makes sense (sanity check)

---

## 🔗 See Also

- **Ledger Checkpoint**: `LEDGER_CHECKPOINT_2026-01-28.md`
- **PDF Instructions**: `panelin_reports/GPT_PDF_INSTRUCTIONS.md`
- **Pricing Instructions**: `pricing/GPT_INSTRUCTIONS_PRICING.md`
- **Product Corrections**: `pricing/config/product_corrections_2026-01-28.json`
- **Enrichment Rules**: `pricing/config/product_enrichment_rules.json`

---

**🚨 Remember**: This logic applies to ALL quotations, PDFs, and calculations!
