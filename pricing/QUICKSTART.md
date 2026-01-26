# Bromyros Price Base - Quick Start Guide

## 🚀 Run the Pipeline

### Option 1: Full Pipeline (Recommended)

```bash
cd "/Users/matias/Chatbot Truth base Creation/Chatbot-Truth-base--Creation-1"

# Run on existing CSV
python3 pricing/price_base.py "MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv"
```

**Output:** All 6 reports in `pricing/out/`

### Option 2: Run Test Suite

```bash
cd "/Users/matias/Chatbot Truth base Creation/Chatbot-Truth-base--Creation-1"

# Run automated test
python3 pricing/test_pipeline.py
```

**Output:** Test results + all reports

### Option 3: Python API

```python
from pricing.price_base_parser import parse_price_base, save_price_base
from pricing.price_base_validate import run_validation
from pricing.compare_with_kb_gpt2 import run_comparison

# Parse
price_base = parse_price_base("export.csv", iva_rate=0.22)
save_price_base(price_base, output_dir="pricing/out")

# Validate
validation = run_validation(price_base, output_dir="pricing/out")

# Compare
comparison = run_comparison(
    price_base, 
    kb_path="BMC_Base_Conocimiento_GPT-2.json",
    output_dir="pricing/out"
)
```

## 📊 Check Results

### 1. Validation Summary
```bash
open pricing/out/validation_summary.md
```

**Look for:**
- IVA pass rates (should be >95%)
- Duplicate SKUs (investigate if found)
- Data quality issues (missing prices, etc.)

### 2. KB Comparison Summary
```bash
open pricing/out/compare_kb_gpt2.md
```

**Look for:**
- Match rate % (higher is better)
- High-severity mismatches (>5% delta)
- Missing in KB (need KB updates)

### 3. Detailed Data
```bash
# Open CSV files in Excel/Numbers
open pricing/out/bromyros_price_base_v1.csv
open pricing/out/validation_issues.csv
open pricing/out/compare_kb_gpt2.csv
```

## 🔍 Spot Checks

### Verify Known Prices

```python
import json

# Load canonical price base
with open("pricing/out/bromyros_price_base_v1.json") as f:
    pb = json.load(f)

# Find ISODEC EPS 100mm
for p in pb["products"]:
    if p["sku"] == "ISD100EPS" and p["thickness_mm"] == 100:
        print(f"Consumer price: ${p['sale_iva_inc']}")
        # Should be ~$46.07 (matches KB)
```

### Check Margin Analysis

```bash
# View margins in CSV
grep "ISD100EPS" pricing/out/bromyros_price_base_v1.csv
```

**Expected output:**
```
ISD100EPS,ISOPANEL EPS 100 mm,100,,panel,ISODEC_EPS,m2,39.04,37.77,46.07,,...,15.9,...
```

## ⚙️ Common Options

### Custom IVA Rate
```bash
python3 pricing/price_base.py export.csv --iva-rate 0.23
```

### Custom Tolerance (±2%)
```bash
python3 pricing/price_base.py export.csv --tolerance-pct 2.0
```

### Skip KB Comparison
```bash
python3 pricing/price_base.py export.csv --no-comparison
```

### Custom Output Directory
```bash
python3 pricing/price_base.py export.csv --output-dir custom/output
```

## 🔧 Troubleshooting

### Issue: "File not found"
**Solution:** Verify file path is correct
```bash
ls -la "MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv"
```

### Issue: Low IVA pass rate
**Solution:** Check if IVA rate is correct (should be 0.22 for Uruguay)
```bash
python3 pricing/price_base.py export.csv --iva-rate 0.22
```

### Issue: No matches in KB comparison
**Solution:** 
1. Check column indices match your export (D=SKU, M=sale_iva_inc)
2. Verify KB file path is correct
3. Check SKU formats in your export

### Issue: Low length extraction hit rate
**Solution:** This is normal for profiles without length in name. To improve:
1. Review `validation_issues.csv` for patterns
2. Add new regex patterns to `price_base_parser.py:extract_length_m()`

## 📚 Next Steps

1. **Review validation_summary.md**
   - Check IVA pass rates
   - Investigate duplicate SKUs
   - Review data quality issues

2. **Review compare_kb_gpt2.md**
   - Spot-check known prices (e.g., ISODEC EPS 100mm = $46.07)
   - Investigate high-severity mismatches
   - Update KB with missing items

3. **Update KB if needed**
   - Add ISOFRIG espesores (40/60/80/100/120/150/180mm)
   - Add ISOROOF 40mm variant
   - Review ISOROOF variant pricing (FOIL/Plus/Colonial)

4. **Fix source data issues**
   - Resolve duplicate SKUs
   - Fix IVA inconsistencies in web prices
   - Standardize profile naming for better length extraction

## 🆘 Help

- **Full docs:** `pricing/README.md`
- **Implementation details:** `pricing/IMPLEMENTATION_SUMMARY.md`
- **Test run:** `python3 pricing/test_pipeline.py`

---

**Current test results:** 103 products, 84 SKUs, 100% sale IVA pass rate, 19.4% KB match rate
