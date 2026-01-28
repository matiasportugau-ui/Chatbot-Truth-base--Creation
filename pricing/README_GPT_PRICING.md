# BROMYROS Pricing - GPT Knowledge Base

**Version:** 1.0.0  
**Generated:** 2026-01-27  
**File:** `pricing/out/bromyros_pricing_gpt_optimized.json`

---

## 📋 Overview

This JSON file contains the complete BROMYROS pricing matriz optimized for fast GPT access with multi-level indexing by **familia**, **sub_familia**, **tipo**, and **SKU**.

**Key Features:**
- ✅ 96 products with complete pricing and specifications
- ✅ Multi-level indices for O(1) lookup performance
- ✅ Familia groups with metadata and product collections
- ✅ 100% validated data integrity
- ✅ File size: 129 KB (optimized for GPT upload)

---

## 🗂️ JSON Structure

### Top-Level Keys

```json
{
  "metadata": { ... },           // Source info, stats, generation timestamp
  "indices": { ... },             // Fast lookup indices (by_sku, by_familia, etc.)
  "familia_groups": { ... },      // Familia-level metadata + products
  "products": [ ... ]             // Complete product array
}
```

---

## 🔍 Quick Start - Where to Look First

### 1. **Exact Product Lookup (by SKU)**

Use `indices.by_sku` for direct product identification:

```javascript
// Example: Find product IAGRO30
const sku = "IAGRO30";
const productRef = data.indices.by_sku[sku];
// Returns: { familia: "ISOROOF / FOIL", sub_familia: "PIR", tipo: "Panel" }

// Then get full product from products array
const product = data.products.find(p => p.sku === sku);
```

### 2. **Browse by Familia/Sub_Familia**

Use `indices.by_familia` or `indices.by_sub_familia` to group products:

```javascript
// Example: Find all ISOROOF products
const familia = "ISOROOF";
const skus = data.indices.by_familia[familia];
// Returns: ["IROOF30", "IROOF40", "IROOF50", ...]

// Example: Find all PIR products
const sub_familia = "PIR";
const skus = data.indices.by_sub_familia[sub_familia];
// Returns: ["IAGRO30", "IROOF30", "IW50", ...]
```

### 3. **Get Familia Groups (Metadata + Products)**

Use `familia_groups` for curated product collections with context:

```javascript
// Example: Get ISOROOF / FOIL familia group
const group = data.familia_groups["ISOROOF / FOIL"];
// Returns:
{
  "description": "Isoroof panels with foil coating for enhanced thermal performance",
  "sub_familia": "PIR",
  "tipo": "Panel",
  "thickness_range": "30-50mm",
  "product_count": 2,
  "products": [...]  // Full product objects
}
```

---

## 💰 Price Field Definitions

Each product contains a `pricing` object with the following fields:

| Field | Description | Use Case |
|-------|-------------|----------|
| `cost_sin_iva` | Internal cost (without IVA) | Factory direct pricing |
| `sale_sin_iva` | Base sale price (without IVA) | B2B pricing |
| `sale_iva_inc` | Customer price (with 22% IVA) | **Standard retail pricing** |
| `web_sin_iva` | Web base price (without IVA) | Online B2B pricing |
| `web_iva_inc` | Web customer price (with IVA) | **Online retail pricing** |

**For Quotations:** Use `sale_iva_inc` or `web_iva_inc` depending on sales channel.

---

## 🎯 Complex Query Workflow Example

### User Request: "I need ISODEC EPS 100"

**GPT Lookup Flow:**

#### Step 1: Identify Main Product

```javascript
// Search products where:
// - name contains "ISODEC" AND "EPS" AND "100"
// - tipo = "Panel"

const mainProduct = data.products.find(p => 
  p.name.includes("ISODEC") && 
  p.name.includes("EPS") && 
  p.specifications.thickness_mm === 100 &&
  p.tipo === "Panel"
);
// Result: ISD100EPS or ISD100EPS_1
```

#### Step 2: Find Related Accessories

```javascript
// Get all ISODEC products
const isodecSkus = data.indices.by_familia["ISODEC"];

// Filter by:
// - sub_familia = "EPS" (material match)
// - thickness_mm = 100 (or compatible)
// - tipo = "Perfileria / Terminaciones" or "Accesorio"

const accessories = data.products.filter(p => 
  isodecSkus.includes(p.sku) &&
  p.sub_familia === "EPS" &&
  (p.specifications.thickness_mm === 100 || p.specifications.thickness_mm === null) &&
  (p.tipo === "Perfileria / Terminaciones" || p.tipo === "Accesorio")
);
// Result: Goteros, perfiles, babetas for ISODEC EPS 100mm
```

#### Step 3: Include Universal Accessories

```javascript
// Get ESTANDAR items (apply to all families)
const universalSkus = data.indices.by_familia["ESTANDAR"];
const universalItems = data.products.filter(p => universalSkus.includes(p.sku));
// Result: Cintas, siliconas, tornillos, anclajes
```

#### Step 4: Build Complete Quotation

```javascript
const quotation = {
  main_product: mainProduct,
  specific_accessories: accessories,
  universal_accessories: universalItems
};
```

---

## 🧭 Key Principles (Flexible Framework)

### Product Categorization

| Field | Purpose | Example Values |
|-------|---------|----------------|
| `tipo` | Product category | `"Panel"`, `"Perfileria / Terminaciones"`, `"Accesorio"` |
| `familia` | Product family | `"ISOROOF"`, `"ISODEC"`, `"ISOWALL"`, `"ESTANDAR"` |
| `sub_familia` | Material/variant | `"PIR"`, `"EPS"`, `"GOTERO FRONTAL PREPINTADO"` |
| `thickness_mm` | Panel thickness | `30`, `50`, `80`, `100`, `150` |

### Matching Logic

**For Panels:**
- Match by `familia` + `sub_familia` + `thickness_mm`

**For Accessories:**
- Match by `familia` (must match panel familia)
- Match by `thickness_mm` (if specified)
- If `familia = "ESTANDAR"` → applies to ALL families

**Example:**
- Panel: ISODEC EPS 100mm
- Specific accessories: `familia="ISODEC"` + `sub_familia="EPS"` + `thickness_mm=100`
- Universal accessories: `familia="ESTANDAR"`

---

## 📊 Available Familias

The JSON contains 11 product familias:

| Familia | Type | Sub_Familia | Products |
|---------|------|-------------|----------|
| ISOROOF / FOIL | Panel | PIR | 2 |
| ISOROOF | Panel | PIR, GOTERO FRONTAL PREPINTADO, etc. | 31 |
| ISOROOF Colonial | Panel | ISOROOF COLONIAL | 1 |
| Estandar | Accesorio | Estandar | 3 |
| ISODEC | Panel, Perfileria | PIR, EPS, GOTERO FRONTAL PREPINTADO | 25 |
| ISOWALL | Panel | PIR | 5 |
| ISOWALL-ISOPANEL | Perfileria | PIR / EPS | 1 |
| ISOFRIG | Panel, Perfileria | PIR | 8 |
| ISOPANEL | Perfileria | EPS | 3 |
| ISOPANEL / ISODEC | Perfileria | EPS, Estandar | 9 |
| ISOPANEL / ISODEC / ISOROOF | Perfileria | Estandar | 3 |

---

## 🔧 Recommended GPT Retrieval Order

1. **Exact SKU Match:** `indices.by_sku[sku]` → Fastest, O(1) lookup
2. **Familia/Sub_Familia Browse:** `indices.by_familia[familia]` → Category grouping
3. **Familia Groups:** `familia_groups[familia]` → Contextual information + products

---

## 📦 Product Specifications

Each product includes a `specifications` object:

```json
{
  "thickness_mm": 30,              // Panel thickness (null if N/A)
  "length_m": "on demand",         // Available length (or fixed value)
  "unit_base": "m2",               // Unit of measurement (m2, Unit, metro_lineal)
  "largo_min_max": "3.5 / 14"      // Min/max production length
}
```

---

## 🚀 Usage Examples

### Example 1: Get Price for SKU IAGRO30

```javascript
const sku = "IAGRO30";
const product = data.products.find(p => p.sku === sku);

console.log(`Product: ${product.name}`);
console.log(`Price (IVA inc): $${product.pricing.sale_iva_inc} USD/${product.specifications.unit_base}`);
// Output: Isoroof FOIL 30 mm - Color Gris-Rojo
//         Price (IVA inc): $39.48 USD/m2
```

### Example 2: List All ISOROOF Products

```javascript
const familia = "ISOROOF";
const skus = data.indices.by_familia[familia];
const products = data.products.filter(p => skus.includes(p.sku));

products.forEach(p => {
  console.log(`${p.sku}: ${p.name} - $${p.pricing.sale_iva_inc}`);
});
```

### Example 3: Find All 50mm PIR Panels

```javascript
const panels = data.products.filter(p => 
  p.tipo === "Panel" &&
  p.sub_familia === "PIR" &&
  p.specifications.thickness_mm === 50
);

console.log(`Found ${panels.length} panels:`);
panels.forEach(p => console.log(`- ${p.sku}: ${p.name}`));
```

### Example 4: Get Familia Group Info

```javascript
const group = data.familia_groups["ISOROOF"];

console.log(`Familia: ${group.description}`);
console.log(`Type: ${group.tipo}`);
console.log(`Material: ${group.sub_familia}`);
console.log(`Thickness Range: ${group.thickness_range}`);
console.log(`Products: ${group.product_count}`);
```

---

## 🔄 Update Process

To regenerate the JSON from the CSV:

```bash
# 1. Update source CSV
cd "wiki/matriz de costos adaptacion /mat design/"
# ... edit CSV ...

# 2. Run converter
cd /path/to/project
python3 pricing/tools/csv_to_optimized_json.py

# 3. Validate output
python3 pricing/tools/validate_optimized_json.py

# 4. Deploy to KB
cp pricing/out/bromyros_pricing_gpt_optimized.json \
   gpt_consolidation_agent/deployment/knowledge_base/

# 5. Update GPT knowledge base file
# Upload new JSON to GPT configuration
```

---

## ⚠️ Important Notes

### Duplicate SKUs

The CSV contains some duplicate SKUs for different products. These are automatically renamed with suffixes:

- Original: `BBAL`
- Renamed: `BBAL`, `BBAL_1`

Products with renamed SKUs include an `original_sku` field for reference.

### ESTANDAR Products

Products with `familia = "ESTANDAR"` are universal accessories that apply to **all** product families (e.g., cinta butilo, silicona, tornillos).

### Null Values

Some fields may be `null`:
- `thickness_mm`: For non-panel products
- `length_m`: For "on demand" products
- Pricing fields: If not available in source CSV

---

## 📈 Performance Benefits

| Operation | Before (Flat JSON) | After (Indexed JSON) | Improvement |
|-----------|-------------------|---------------------|-------------|
| Find product by SKU | O(n) scan | O(1) lookup | ~96x faster |
| Find familia products | O(n) scan | O(1) lookup | ~96x faster |
| Get familia metadata | Not available | O(1) lookup | ∞ faster |
| Browse by material type | O(n) scan | O(1) lookup | ~96x faster |

---

## 📞 Support

**File Location:** `pricing/out/bromyros_pricing_gpt_optimized.json`  
**Converter Script:** `pricing/tools/csv_to_optimized_json.py`  
**Validation Script:** `pricing/tools/validate_optimized_json.py`

**Deployment Location:**  
`gpt_consolidation_agent/deployment/knowledge_base/bromyros_pricing_gpt_optimized.json`

---

**Last Updated:** 2026-01-27  
**Version:** 1.0.0
