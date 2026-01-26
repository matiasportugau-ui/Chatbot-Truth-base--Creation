# Panelin Catalog Knowledge Guide
**Version**: 1.0  
**Last Updated**: 2026-01-25  
**Purpose**: Guide for regenerating and using the Shopify catalog in Panelin GPT

---

## 📚 Catalog Files Overview

### Primary Catalog File
- **File**: `catalog/out/shopify_catalog_v1.json`
- **Level**: 1.5 (Catalog - Descriptions Only)
- **Purpose**: Product descriptions, variants, images, search metadata
- **⚠️ CRITICAL**: This file contains **NO PRICES**. Prices come from `BMC_Base_Conocimiento_GPT-2.json` (Level 1).

### Supporting Files
- **Index CSV**: `catalog/out/shopify_catalog_index_v1.csv` - For Code Interpreter lookups
- **Quality Report**: `catalog/out/shopify_catalog_quality.md` - Quality metrics (reference only)

---

## 🔄 Regenerating the Catalog

### When to Regenerate
- **Weekly**: After major Shopify product updates
- **After bulk edits**: When multiple products are updated in Shopify
- **Before major releases**: Ensure catalog is current before GPT updates

### How to Regenerate

1. **Export from Shopify**:
   - Go to Shopify Admin → Products → Export
   - Export as CSV
   - Save to: `catalog/products_export.csv` (or specify path)

2. **Run Export Script**:
   ```bash
   cd /path/to/Chatbot-Truth-base--Creation-1
   python3 catalog/export_shopify_catalog.py catalog/products_export.csv --quality-report
   ```

3. **Verify Output**:
   - Check `catalog/out/shopify_catalog_v1.json` was created/updated
   - Review `catalog/out/shopify_catalog_quality.md` for issues
   - Check `catalog/out/shopify_catalog_index_v1.csv` for completeness

4. **Upload to GPT Builder**:
   - Go to GPT Builder → Configure → Knowledge
   - Remove old `shopify_catalog_v1.json`
   - Upload new `catalog/out/shopify_catalog_v1.json`
   - Wait 2-3 minutes for reindexing

---

## 📖 How Panelin Uses the Catalog

### Use Case 1: Product Descriptions
**User asks**: "Tell me about ISOROOF 3G"

**Panelin workflow**:
1. Search `shopify_catalog_v1.json` → find product by handle or search terms
2. Extract: `title`, `body_html`, `body_text`, `variants`, `images`
3. Present rich description with images
4. **If user asks for price**: Switch to `BMC_Base_Conocimiento_GPT-2.json` (Level 1)

### Use Case 2: SKU Lookup
**User provides**: "I need product SKU XYZ123"

**Panelin workflow**:
1. Use Code Interpreter to search `shopify_catalog_index_v1.csv` or JSON `indexes.sku_to_handle`
2. Resolve SKU → handle → product
3. Get description from `shopify_catalog_v1.json`
4. Get price from `BMC_Base_Conocimiento_GPT-2.json` (Level 1)

### Use Case 3: Variant Information
**User asks**: "What colors does ISOROOF come in?"

**Panelin workflow**:
1. Search `shopify_catalog_v1.json` → find product
2. Extract `variants` array → `option_values` (Color, Size, etc.)
3. Present available variants
4. **If user asks variant price**: Use Level 1 master file

---

## ⚠️ Critical Rules

### Rule 1: Catalog ≠ Prices
- **Catalog file**: Descriptions, variants, images, metadata
- **Master file**: Prices, formulas, technical specs
- **Never**: Use catalog prices (they don't exist in catalog file)
- **Always**: Use Level 1 master for any price query

### Rule 2: Search Priority
When searching for products:
1. **First**: Try `shopify_catalog_v1.json` for descriptions/variants
2. **Then**: Use `BMC_Base_Conocimiento_GPT-2.json` for prices/specs
3. **If conflict**: Level 1 master always wins

### Rule 3: Code Interpreter for Complex Searches
- **Simple searches**: Direct JSON lookup
- **SKU lookups**: Use Code Interpreter + CSV index
- **Bulk searches**: Use Code Interpreter + Pandas

---

## 📊 Catalog Structure

### Main JSON Structure
```json
{
  "meta": {
    "generated_at": "2026-01-25T23:27:23",
    "source_file": "products_export.csv",
    "total_rows_processed": 402,
    "unique_products": 97,
    "total_variants": 335
  },
  "products_by_handle": {
    "product-handle": {
      "handle": "product-handle",
      "title": "Product Title",
      "body_html": "<p>Description HTML</p>",
      "body_text": "Plain text description",
      "vendor": "BMC URUGUAY",
      "product_category": "Category Path",
      "type": "Product Type",
      "tags": ["tag1", "tag2"],
      "variants": [...],
      "images": [...],
      "search_document": "Searchable text"
    }
  },
  "indexes": {
    "sku_to_handle": {"SKU123": "product-handle"},
    "vendor_to_handles": {"BMC URUGUAY": ["handle1", "handle2"]},
    "type_to_handles": {"Type": ["handle1"]}
  }
}
```

### CSV Index Structure
```csv
handle,title,vendor,status,published,product_category,type,tags,option_names,variant_count,variant_skus,image_count,metafield_count,url
```

---

## 🔍 Troubleshooting

### Issue: Catalog not found in GPT
**Solution**: 
- Verify file uploaded: GPT Builder → Configure → Knowledge
- Check filename matches exactly: `shopify_catalog_v1.json`
- Wait 2-3 minutes after upload for reindexing

### Issue: Product not found
**Solution**:
- Check if product exists in `shopify_catalog_index_v1.csv`
- Verify handle spelling (case-sensitive)
- Use Code Interpreter to search CSV if direct lookup fails

### Issue: Price missing from catalog
**Expected**: Catalog file has NO prices. Prices are in Level 1 master file.
**Solution**: Use `BMC_Base_Conocimiento_GPT-2.json` for prices.

### Issue: Catalog out of date
**Solution**:
1. Regenerate catalog from latest Shopify export
2. Upload new file to GPT Builder
3. Wait for reindexing
4. Test with known product

---

## 📝 Maintenance Checklist

### Weekly
- [ ] Check if Shopify products updated
- [ ] Regenerate catalog if needed
- [ ] Upload new catalog to GPT Builder
- [ ] Test with sample product query

### Monthly
- [ ] Review quality report for issues
- [ ] Verify catalog completeness
- [ ] Check for duplicate products
- [ ] Validate SKU mappings

### Before Major Releases
- [ ] Regenerate catalog from latest export
- [ ] Run quality checks
- [ ] Upload to GPT Builder
- [ ] Run full test suite from `PANELIN_GPT_TEST_PLAN.md`

---

## 🔗 Related Files

- **Master KB**: `BMC_Base_Conocimiento_GPT-2.json` (Level 1 - Prices)
- **Export Script**: `catalog/export_shopify_catalog.py`
- **Knowledge Manifest**: `PANELIN_KNOWLEDGE_MANIFEST.md`
- **Capabilities Policy**: `PANELIN_CAPABILITIES_POLICY.md` (Code Interpreter usage)

---

**Last Updated**: 2026-01-25  
**Maintainer**: BMC Uruguay AI Team
