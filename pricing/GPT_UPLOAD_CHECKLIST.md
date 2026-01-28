# GPT Upload Checklist - BROMYROS Pricing

## 📦 Files to Upload to GPT Knowledge Base

Upload these 3 files from `gpt_consolidation_agent/deployment/knowledge_base/`:

### ✅ 1. Main Pricing Data (Required)
**File:** `bromyros_pricing_gpt_optimized.json` (129 KB)

**What it contains:**
- 96 products with complete pricing
- Multi-level indices (by_sku, by_familia, by_sub_familia, by_tipo)
- Familia groups with metadata
- All specifications and price types

**Priority:** **CRITICAL** - This is the main data source

---

### ✅ 2. Usage Guide (Highly Recommended)
**File:** `README_GPT_PRICING.md` (10 KB)

**What it contains:**
- Quick start examples
- JSON structure explanation
- Query workflows (SKU lookup, familia browse, complex quotes)
- Price field definitions
- Product categorization framework
- Complete usage examples

**Priority:** **HIGHLY RECOMMENDED** - Helps GPT use the JSON correctly

---

### ✅ 3. GPT Instructions (Recommended)
**File:** `GPT_INSTRUCTIONS_PRICING.md` (6 KB)

**What it contains:**
- Step-by-step query instructions
- Price field selection logic
- Matching rules for accessories
- Example responses in Spanish
- Best practices

**Priority:** **RECOMMENDED** - Can also be added to GPT system instructions

---

## 🔧 GPT Configuration

### Option A: Add to System Instructions (Preferred)

Copy the content from `GPT_INSTRUCTIONS_PRICING.md` into your GPT's system instructions. This ensures the GPT always follows the correct lookup patterns.

### Option B: Upload as Knowledge Base File

Upload `GPT_INSTRUCTIONS_PRICING.md` as a knowledge base file. The GPT can reference it when needed.

**Recommendation:** Use both - add key instructions to system prompt, upload full file for reference.

---

## 📝 Suggested GPT System Instructions

Add this to your GPT's instructions:

```markdown
## Pricing Data Access

You have access to bromyros_pricing_gpt_optimized.json with 96 products.

### Quick Lookup Rules:
1. For exact SKU: Use indices.by_sku["SKU_CODE"]
2. For familia browse: Use indices.by_familia["FAMILIA_NAME"]
3. For complete info: Use familia_groups["FAMILIA_NAME"]

### Price Fields:
- Use pricing.sale_iva_inc for standard customer quotes (IVA included)
- Use pricing.web_iva_inc for web/online quotes
- All prices in USD

### Complex Quotations (e.g., "I need ISODEC EPS 100"):
1. Find main panel: tipo="Panel", match familia+sub_familia+thickness
2. Find specific accessories: same familia, same sub_familia, matching thickness
3. Include ESTANDAR items: familia="ESTANDAR" works with ALL products
4. Build complete quote with panel + accessories + universal items

### Important:
- ESTANDAR familia = universal accessories (apply to all families)
- Match accessories by familia, sub_familia, and thickness_mm
- Always verify pricing exists before quoting
```

---

## 🧪 Test Queries After Upload

Test these queries to verify everything works:

### Test 1: Simple Price Lookup
```
User: "Cuanto cuesta el IAGRO30?"
Expected: Should return $39.48 USD/m2 (IVA inc)
```

### Test 2: Familia Browse
```
User: "Mostrame todos los productos ISOROOF"
Expected: Should list 31 ISOROOF products
```

### Test 3: Complex Quotation
```
User: "Necesito ISODEC EPS 100mm con accesorios"
Expected: Should return:
- Main panel (ISD100EPS)
- ISODEC EPS 100mm accessories (goteros, perfiles)
- ESTANDAR universal accessories (cintas, silicona)
```

### Test 4: Material Filter
```
User: "Mostrame todos los paneles PIR de 50mm"
Expected: Should filter by sub_familia="PIR" and thickness_mm=50
```

---

## ✅ Verification Checklist

After uploading, verify:

- [ ] GPT can find products by SKU (Test: "precio IAGRO30")
- [ ] GPT can browse by familia (Test: "productos ISOROOF")
- [ ] GPT includes accessories in quotes (Test: "ISODEC EPS 100 completo")
- [ ] GPT recognizes ESTANDAR as universal (Test: "accesorios universales")
- [ ] GPT uses correct price field (sale_iva_inc for standard quotes)
- [ ] GPT shows prices in USD with IVA included
- [ ] GPT mentions unit (m2, Unit, metro lineal)

---

## 📊 Expected Behavior

### Good Response Example:
```
User: "Necesito ISODEC EPS 100"

GPT Response:
"Para ISODEC EPS 100mm, te recomiendo:

PANEL PRINCIPAL:
• ISD100EPS: ISODEC EPS 100mm - $46.07 USD/m2 (IVA inc)

ACCESORIOS ESPECÍFICOS:
• Gotero Frontal 100mm (6842) - $25.34 USD/unidad
• Perfil U 100mm (PU100MM) - $15.15 USD/unidad

ACCESORIOS UNIVERSALES (ESTANDAR):
• Cinta Butilo (C.But.) - $18.17 USD/unidad
• Silicona Bromplast - $11.58 USD/unidad

¿Cuántos m2 necesitas para calcular el presupuesto total?"
```

---

## 🔄 When to Regenerate

Regenerate and re-upload the JSON when:
- Prices change in the source CSV
- New products are added
- Product specifications change
- Familia/sub_familia categories are updated

**Regeneration command:**
```bash
python3 pricing/tools/csv_to_optimized_json.py
python3 pricing/tools/validate_optimized_json.py
```

---

## 📁 File Locations

**Source:**
- CSV: `wiki/matriz de costos adaptacion /mat design/Copy of MATRIZ de COSTOS y VENTAS 2026 update .xlsx - BROMYROS.csv`

**Generated:**
- JSON: `pricing/out/bromyros_pricing_gpt_optimized.json`
- README: `pricing/README_GPT_PRICING.md`
- Instructions: `pricing/GPT_INSTRUCTIONS_PRICING.md`

**Deployment:**
- All files copied to: `gpt_consolidation_agent/deployment/knowledge_base/`

---

## ✅ Ready to Upload!

All files are prepared and validated. Simply upload the 3 files to your GPT's knowledge base and test with the queries above.

**Total Upload Size:** ~145 KB (well within GPT limits)

---

**Last Updated:** 2026-01-27  
**Version:** 1.0.0
