# Shopify Product Catalog for GPT Knowledge

This module converts Shopify product exports (CSV) into a clean, query-friendly catalog optimized for GPT Knowledge Base consumption.

---

## 📋 Overview

**Purpose**: Provide product descriptions, attributes, variants, images, and metafields to your GPT without including pricing data (which comes from your internal price base).

**Key Features**:
- ✅ Preserves all product descriptions, HTML body, and plain text versions
- ✅ Extracts variants, options, and SKUs
- ✅ Captures all metafields and Google Shopping attributes
- ✅ Generates search-friendly documents per product
- ✅ **Excludes prices and costs** (intentionally omitted)
- ✅ Creates CSV index for quick reference

---

## 🚀 Quick Start

### 1. Export Products from Shopify

In Shopify Admin:
1. Go to **Products** → **All products**
2. Click **Export**
3. Select **All products** and **CSV for Excel, Numbers, or other spreadsheet programs**
4. Download the CSV file

### 2. Run the Export Tool

```bash
# Basic usage (from repo root)
python3 catalog/export_shopify_catalog.py path/to/products_export.csv

# With quality report
python3 catalog/export_shopify_catalog.py path/to/products_export.csv --quality-report

# Custom output directory
python3 catalog/export_shopify_catalog.py path/to/products_export.csv --output-dir custom/path
```

### 3. Upload to GPT Knowledge

Upload the generated file to your GPT's Knowledge Base:
- **Primary file**: `catalog/out/shopify_catalog_v1.json`
- **Reference**: `catalog/out/shopify_catalog_index_v1.csv` (optional, for quick lookups)

---

## 📦 Output Files

### `shopify_catalog_v1.json`

Structured catalog with:
- **`meta`**: Generation info, stats, quality flags
- **`products_by_handle`**: Full product objects keyed by handle
  - Identity: handle, title, vendor, type, category, tags
  - Descriptions: body_html, body_text (HTML stripped)
  - SEO: seo_title, seo_description
  - Options & variants (no prices)
  - Images with positions
  - Metafields (all custom fields)
  - Google Shopping attributes
  - `search_document`: Plain-text summary for GPT retrieval
- **`indexes`**: Lookup helpers
  - `sku_to_handle`: Quick SKU → product mapping
  - `by_vendor`, `by_type`, `by_category`, `by_tag`: Grouped lists

**Example product structure**:

```json
{
  "handle": "isoroof-3g-gris-rojo-blanco-bromyros",
  "title": "ISOROOF. 3G.",
  "body_html": "<p>Panel aislante...</p>",
  "body_text": "Panel aislante...",
  "vendor": "Bromyros by KINGSPAN",
  "product_category": "Hardware > Building Materials > Roofing",
  "type": "Panel Aislante",
  "tags": ["Bromyros", "Panel"],
  "published": true,
  "status": "active",
  "seo_title": "...",
  "seo_description": "...",
  "options": {
    "option1_name": "Espesor",
    "option2_name": "Color",
    "option3_name": null
  },
  "variants": [
    {
      "option1_value": "30 mm",
      "option2_value": "Gris",
      "sku": "Subido con Éxito",
      "barcode": null,
      "grams": 0,
      "requires_shipping": false,
      "taxable": false,
      "weight_unit": "kg",
      "variant_image": "https://..."
    }
  ],
  "images": [
    {
      "src": "https://cdn.shopify.com/.../file.jpg",
      "position": 1,
      "alt": ""
    }
  ],
  "metafields": {
    "shopify.color-pattern": "blanco; gris; rojo",
    "shopify.material": "..."
  },
  "google_shopping": {
    "google_product_category": "123"
  },
  "search_document": "Title: ISOROOF. 3G.\nVendor: Bromyros by KINGSPAN\n..."
}
```

### `shopify_catalog_index_v1.csv`

Quick reference table with columns:
- `handle`, `title`, `vendor`, `status`, `published`
- `product_category`, `type`, `tags`
- `option_names`, `variant_count`, `variant_skus` (first 5)
- `image_count`, `metafield_count`, `url`

### `shopify_catalog_quality.md` (optional)

Quality report showing:
- Total products, variants, images processed
- Products missing title/body
- Duplicate SKUs detected
- Vendor name variations
- Index summaries

---

## 🧠 How GPT Should Use This Catalog

### In Your GPT Instructions

Add guidance like:

```
## Product Information Sources

You have access to two complementary knowledge sources:

1. **Product Catalog** (`shopify_catalog_v1.json`):
   - Use for: Product descriptions, attributes, variants, options, images, metafields
   - Contains: Full product details EXCEPT pricing
   - Query by: handle, SKU, title, category, tags, vendor

2. **Pricing Master** (`BMC_Base_Conocimiento_GPT-2.json`):
   - Use for: Prices, technical specs (autoportancia, thermal coefficients)
   - ALWAYS use this for pricing quotes

## Lookup Strategy

When a user asks about a product:
1. Search `shopify_catalog_v1.json` → `search_document` field for quick matches
2. Use `indexes.sku_to_handle` for SKU lookups
3. Get pricing from `BMC_Base_Conocimiento_GPT-2.json` using the product key

Example:
- User: "Tell me about ISOROOF 3G 30mm"
- Step 1: Search catalog → find handle "isoroof-3g-gris-rojo-blanco-bromyros"
- Step 2: Get description, options (Espesor: 30mm, 50mm, 80mm), images
- Step 3: Get price from pricing master → ISOROOF_3G.espesores.30.precio
```

### Example Queries GPT Can Answer

✅ **From Catalog**:
- "What products do you have in the 'Panel Aislante' category?"
- "Show me all Bromyros products"
- "What are the available options for ISOROOF?"
- "What metafields are set for this product?"
- "Give me the product description for handle X"

✅ **From Pricing Master**:
- "What's the price of ISODEC EPS 100mm?"
- "Calculate a quote for..."

---

## 🔄 Updating the Catalog

When products change in Shopify:

1. Export new CSV from Shopify
2. Re-run the export tool:
   ```bash
   python3 catalog/export_shopify_catalog.py new_export.csv --quality-report
   ```
3. Review the quality report for issues
4. Replace the old JSON in GPT Knowledge with the new one

**Tip**: Check the quality report first to catch issues like:
- Missing descriptions
- Duplicate SKUs
- Vendor name inconsistencies

---

## 🛠️ Advanced Usage

### Filtering Products

If you only want to export certain products, pre-filter the CSV before running the tool:

```bash
# Example: Only active products
awk -F',' 'NR==1 || $65=="active"' products_export.csv > active_only.csv
python3 catalog/export_shopify_catalog.py active_only.csv
```

### Customizing the Parser

Edit `catalog/shopify_export_parser.py` to:
- Add custom metafield parsing logic
- Modify the search_document generation
- Add product-specific transformations

### Debugging

Enable verbose output by adding print statements in `shopify_export_parser.py`:

```python
# In _process_row method
if handle == "problem-handle":
    print(f"DEBUG: Processing {handle}")
    print(f"  Variants: {len(product['variants'])}")
```

---

## 📊 Sample Statistics

From the current export (`products_export_1.csv`):
- **97 unique products**
- **335 variants** (multiple options per product)
- **261 images**
- **0.72 MB** JSON output (well within GPT limits)
- **4 vendors**, **20 categories**, **8 tags**

---

## ⚠️ Important Notes

1. **No Pricing Data**: This catalog intentionally excludes all price/cost columns. Keep your pricing source separate (e.g., `BMC_Base_Conocimiento_GPT-2.json`).

2. **Handle = Primary Key**: All products are keyed by their Shopify `handle` (URL-safe identifier).

3. **Variant Deduplication**: The parser automatically deduplicates variants and images when Shopify export has multiple rows per product.

4. **HTML Stripping**: The `body_text` field strips HTML tags for easier GPT searching. Original HTML is preserved in `body_html`.

5. **Metafield Capture**: All columns matching the pattern `(product.metafields.*)` are automatically captured.

---

## 🐛 Troubleshooting

### "Products missing body"

Some products in Shopify may not have descriptions. Check the quality report to see which handles are affected.

**Fix**: Add descriptions in Shopify or ignore if intentional (e.g., draft products).

### "Duplicate SKUs"

Multiple variants using the same SKU.

**Fix**: Ensure unique SKUs in Shopify or use option values for differentiation.

### "Vendor variations"

Inconsistent vendor names (e.g., `BMC URUGUAY` vs `BMC URUGUAY ` with trailing space).

**Fix**: Standardize vendor names in Shopify.

### JSON too large for GPT

If the JSON exceeds GPT Knowledge limits (~512 MB):

1. Filter products before export (remove drafts, archived)
2. Split by vendor/category and upload multiple files
3. Truncate `body_html` fields if extremely long

---

## 📞 Support

For issues or questions:
1. Check the quality report first
2. Review the sample product structure above
3. Inspect `shopify_catalog_v1.json` directly
4. Modify `shopify_export_parser.py` for custom needs

---

**Last Updated**: 2026-01-25  
**Version**: 1.0  
**Maintained by**: BMC Uruguay Automation Team
