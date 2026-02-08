---
applyTo: "**/*.json"
---

# JSON Files - Copilot Instructions

These instructions apply to all JSON files in the repository, especially knowledge base files.

## ⚠️ CRITICAL - Protected Files

**JSON files contain business-sensitive pricing data and require @matiasportugau-ui approval** (see `.github/CODEOWNERS`).

Before modifying any JSON file:
1. Understand the knowledge base hierarchy
2. Verify changes with repository owner
3. Test changes don't break calculators
4. Validate JSON syntax

## 📊 Knowledge Base Hierarchy

JSON files follow a strict 4-level hierarchy:

### Level 1 - MASTER (Primary Source) ⭐
- `GPT_Panelin_copilotedit/01_KNOWLEDGE_BASE/Level_1_Master/BMC_Base_Conocimiento_GPT-2.json`
- `accessories_catalog.json`
- `bom_rules.json`

**These are authoritative sources**. In case of conflicts, Level 1 always wins.

### Level 2 - VALIDATION
- `BMC_Base_Unificada_v4.json` - For cross-reference only

### Level 3 - DYNAMIC
- `panelin_truth_bmcuruguay_web_only_v2.json` - Web-scraped prices

### Level 4 - SUPPORT
- Various documentation and context files

## 🔒 Security Rules

- **Never commit secrets** to JSON files
- **Never expose** internal pricing formulas in public-facing files
- **Validate all changes** to pricing data
- **Use consistent decimal precision** (2 decimal places for USD)

## ✅ JSON Structure Standards

### Consistent Formatting
```json
{
  "product_id": "ISOPANEL_EPS_50mm",
  "price_per_m2": "41.88",
  "unit": "USD",
  "min_length_m": "2.0"
}
```

### Price Values
- **ALWAYS** store prices as strings to maintain precision
- Use 2 decimal places for USD: `"41.88"` not `41.88`
- Never use floating point numbers for financial data

### Validation Rules Example
```json
{
  "calculation_rules": {
    "min_quantity": 1,
    "max_discount_percent": "15.00",
    "safety_margin": "1.2"
  }
}
```

## 🧪 Testing JSON Changes

After modifying JSON files:

```bash
# 1. Validate JSON syntax
python3 -m json.tool your_file.json > /dev/null

# 2. Run calculator tests
python3 -m pytest tests/test_quotation_calculations.py -v

# 3. Check knowledge base loading
python3 -c "import json; print(json.load(open('your_file.json')))"
```

## 📝 Common JSON File Types

### Knowledge Base Files
- Product specifications and pricing
- Calculation rules and formulas
- BOM (Bill of Materials) rules

### Configuration Files
- API endpoints and settings
- Model configurations
- Feature flags

### Catalog Files
- Accessories catalog
- Product families
- Technical specifications

## ⚡ Best Practices

1. **Maintain Consistency**: Match existing JSON structure
2. **Validate Syntax**: Use `json.tool` before committing
3. **Test Impact**: Run relevant tests after changes
4. **Document Changes**: Update related markdown documentation
5. **Preserve Comments**: Use accompanying .md files for documentation (JSON doesn't support comments)

## 🚫 What NOT to Do

- ❌ Don't use floating point numbers for prices
- ❌ Don't add inline comments (JSON doesn't support them)
- ❌ Don't commit secrets or credentials
- ❌ Don't break backward compatibility without testing
- ❌ Don't modify Level 1 files without owner approval

## 🔍 When Making Changes

1. Identify which hierarchy level the file belongs to
2. Check CODEOWNERS requirements
3. Understand the file's purpose in the system
4. Make minimal, targeted changes
5. Validate JSON syntax
6. Test with dependent calculators
7. Document the change reason in commit message

## 📖 Related Documentation

- `PANELIN_KNOWLEDGE_BASE_GUIDE.md` - Detailed KB structure
- `.github/copilot-instructions.md` - General guidelines
- `.github/CODEOWNERS` - File ownership and approval requirements
