# Autoportancia Validation Guide - Calculator V3.1

**Version**: 3.1  
**Date**: 2026-02-07  
**Feature**: Span/Load Validation for Structural Safety

---

## Overview

Autoportancia validation is a safety feature that checks whether requested panel spans exceed structural capacity limits. The system validates spans against manufacturer specifications from BMC Uruguay's technical data.

**What is Autoportancia?**  
Autoportancia (self-supporting capacity) is the maximum distance between supports (correas/vigas) that a panel can safely span without additional reinforcement. Exceeding this limit can cause structural failure.

---

## How It Works

### 1. Data Source

Validation uses the autoportancia table from `bom_rules.json`:

```json
{
  "autoportancia": {
    "tablas": {
      "ISODEC_EPS": {
        "100": {"luz_max_m": 5.5, "peso_kg_m2": 12.5},
        "150": {"luz_max_m": 7.5, "peso_kg_m2": 14.5},
        "200": {"luz_max_m": 9.1, "peso_kg_m2": 16.5},
        "250": {"luz_max_m": 10.4, "peso_kg_m2": 18.5}
      },
      "ISODEC_PIR": {...},
      "ISOROOF_3G": {...},
      "ISOPANEL_EPS": {...}
    }
  }
}
```

**Coverage**: 4 product families, ~15 thickness configurations

### 2. Safety Margin

The system applies a **15% safety margin** (industry standard):
- Absolute max: From manufacturer specs (e.g., 5.5m for ISODEC_EPS 100mm)
- Safe max: `absolute_max × 0.85` (e.g., 4.675m)
- Validation: Span must be ≤ safe max

**Why 15%?**
- Accounts for material tolerances
- Installation variation
- Load distribution uncertainties
- Conservative engineering practice

### 3. Validation Logic

```python
if span_requested <= span_max_safe:
    ✓ PASSED
else:
    ✗ FAILED → Suggest alternatives
```

---

## Usage

### Basic Usage

```python
from quotation_calculator_v3 import validate_autoportancia

result = validate_autoportancia(
    product_family="ISODEC_EPS",
    thickness_mm=100,
    span_m=4.5,
    safety_margin=0.15  # Optional, default 0.15
)

print(result['is_valid'])  # True
print(result['recommendation'])
```

### Integration with Calculator

```python
from quotation_calculator_v3 import calculate_panel_quote

quotation = calculate_panel_quote(
    product_id="ISODEC_EPS_100mm",
    length_m=4.5,
    width_m=10.0,
    validate_span=True  # Default True - validates automatically
)

# Access validation result
if quotation.get('autoportancia_validation'):
    validation = quotation['autoportancia_validation']
    if not validation['is_valid']:
        print(f"⚠️  WARNING: {validation['recommendation']}")
```

### Disable Validation (Not Recommended)

```python
quotation = calculate_panel_quote(
    product_id="ISODEC_EPS_100mm",
    length_m=8.0,  # Exceeds limit
    width_m=10.0,
    validate_span=False  # Disable for special cases only
)
# Quotation will be created without validation
```

---

## Return Structure

### AutoportanciaValidationResult

```python
{
    "is_valid": bool,                    # True if span within safe limits
    "span_requested_m": float,           # Requested span
    "span_max_m": float,                 # Absolute maximum from specs
    "span_max_safe_m": float,            # Safe maximum (with margin)
    "excess_pct": float,                 # % over safe limit (if failed)
    "recommendation": str,               # Human-readable message
    "alternative_thicknesses": List[int] # Suggested alternatives
}
```

---

## Examples

### Example 1: Valid Span (Passes)

**Input**: ISODEC_EPS 100mm, 4.5m span

```python
result = validate_autoportancia("ISODEC_EPS", 100, 4.5)
```

**Output**:
```python
{
    "is_valid": True,
    "span_requested_m": 4.5,
    "span_max_m": 5.5,
    "span_max_safe_m": 4.675,
    "excess_pct": 0.0,
    "recommendation": "✓ Span validation PASSED: 4.5m ≤ 4.7m safe limit (max 5.5m, using 81.8% of absolute capacity)",
    "alternative_thicknesses": []
}
```

### Example 2: Span Exceeds Limit (Fails)

**Input**: ISODEC_EPS 100mm, 8.0m span

```python
result = validate_autoportancia("ISODEC_EPS", 100, 8.0)
```

**Output**:
```python
{
    "is_valid": False,
    "span_requested_m": 8.0,
    "span_max_m": 5.5,
    "span_max_safe_m": 4.675,
    "excess_pct": 71.1,
    "recommendation": "⚠️  SPAN EXCEEDS SAFE LIMIT: Requested span of 8.0m exceeds the safe autoportancia of 4.7m for ISODEC_EPS 100mm (maximum 5.5m with 15% safety margin). Recommended: Use 250mm thickness instead. (Excess: 71.1%)",
    "alternative_thicknesses": [250]
}
```

### Example 3: Edge Case - At Absolute Limit

**Input**: ISODEC_EPS 100mm, 5.5m span (exactly at absolute limit)

```python
result = validate_autoportancia("ISODEC_EPS", 100, 5.5)
```

**Output**:
```python
{
    "is_valid": False,  # Fails because exceeds SAFE limit (not absolute)
    "span_requested_m": 5.5,
    "span_max_m": 5.5,
    "span_max_safe_m": 4.675,
    "excess_pct": 17.6,
    "recommendation": "⚠️  SPAN EXCEEDS SAFE LIMIT: ... Recommended: Use 150mm thickness instead.",
    "alternative_thicknesses": [150]
}
```

---

## Product Family Coverage

| Family | Thicknesses | Span Range |
|--------|-------------|------------|
| **ISODEC_EPS** | 100, 150, 200, 250mm | 5.5m - 10.4m |
| **ISODEC_PIR** | 50, 80, 120mm | 3.5m - 7.6m |
| **ISOROOF_3G** | 30, 50, 80mm | 2.8m - 4.0m |
| **ISOPANEL_EPS** | 50, 100, 150, 200mm | 3.0m - 9.1m |

---

## Recommendations Algorithm

When validation fails, the system provides intelligent recommendations:

### 1. Suggest Thicker Panel

Searches for next available thickness that would support the requested span:

```
If ISODEC_EPS 100mm fails for 8.0m span:
  → Check 150mm: 7.5m max (still insufficient)
  → Check 200mm: 9.1m max (insufficient)
  → Check 250mm: 10.4m max ✓ (works!)
  → Recommend: "Use 250mm thickness instead"
```

### 2. Suggest Intermediate Support

If no thickness works:

```
Recommended: Add intermediate support to reduce span to 4.0m
```

This splits the span in half, reducing the distance each panel must support.

---

## Best Practices

### For Developers

1. **Always validate** - Use `validate_span=True` (default)
2. **Show warnings** - Display validation messages to users
3. **Log failures** - Track when spans exceed limits for analytics
4. **Don't bypass** - Only disable validation for exceptional cases

### For End Users (GPT Instructions)

When presenting quotations:
- ✓ **Valid spans**: Proceed normally
- ⚠️ **Warning spans** (80-100% of safe limit): Include note about approaching limit
- ✗ **Failed spans**: 
  - Show warning prominently
  - Present alternative thickness options
  - Explain intermediate support option
  - DO NOT block quotation (warning mode)

---

## Testing

### Test Coverage

9 comprehensive test cases validate:
1. Valid span (passes)
2. Span exceeds limit (fails with alternatives)
3. Span at absolute limit (edge case)
4. Span within safety margin (comfortable)
5. Alternative thickness recommendations
6. All 4 product families
7. Edge cases (unknown thickness)
8. Integration with calculator
9. Validation disabled mode

**Run tests**:
```bash
cd 03_PYTHON_TOOLS
python3 test_autoportancia_validation.py
```

**Expected output**: 9/9 tests passed

---

## Performance

- **Overhead**: <5ms per validation
- **Caching**: BOM rules cached after first load
- **No API calls**: All data local

---

## Future Enhancements

### Phase 1 (Current - V3.1)
- [x] Basic span validation
- [x] 15% safety margin
- [x] Alternative thickness suggestions
- [x] Warning mode (non-blocking)

### Phase 2 (Future)
- [ ] Strict mode (blocking) - `strict_validation=True`
- [ ] Load calculations (not just span)
- [ ] Wind/snow load factors
- [ ] Roof slope validation
- [ ] Historical validation logs

### Phase 3 (Advanced)
- [ ] AI-powered optimization (suggest optimal thickness for cost/safety)
- [ ] Multi-factor analysis (span + load + wind + slope)
- [ ] Real-time price comparison with alternatives

---

## Troubleshooting

### "No autoportancia data available"

**Cause**: Thickness not in table  
**Solution**: Manual verification required - check manufacturer specs

### Validation always returns True

**Cause**: `validate_span=False` or missing product family  
**Solution**: Enable validation, verify product_id format

### Suggested thickness unavailable

**Cause**: No thicker option in that family  
**Solution**: Use intermediate support recommendation instead

---

## Technical Details

### Function Signature

```python
def validate_autoportancia(
    product_family: str,      # ISODEC_EPS, ISODEC_PIR, etc.
    thickness_mm: int,        # 50, 80, 100, 150, 200, 250
    span_m: float,            # Requested span in meters
    safety_margin: float = 0.15  # Safety factor (default 15%)
) -> AutoportanciaValidationResult:
```

### Family Name Mapping

The function handles both formats:
- Short: `"ISODEC_EPS"` (from BOM rules)
- Long: `"ISODEC_EPS_100mm"` (from product IDs)

It extracts the base family name automatically.

### Safety Margin Calculation

```
span_max_safe_m = luz_max_m × (1 - safety_margin)
                = luz_max_m × 0.85
```

Example: 5.5m × 0.85 = 4.675m

---

## References

- **BOM Rules**: `01_KNOWLEDGE_BASE/Level_1_3_BOM_Rules/bom_rules.json`
- **Calculator**: `03_PYTHON_TOOLS/quotation_calculator_v3.py`
- **Tests**: `03_PYTHON_TOOLS/test_autoportancia_validation.py`
- **Implementation Guide**: `05_ANALYSIS/calculator_v3_implementation_guide.md`

---

## Support

For questions or issues:
1. Check test suite for usage examples
2. Review function docstrings in code
3. Consult BOM rules autoportancia table structure

**Version History**:
- V3.1 (2026-02-07): Initial implementation with warning mode
- V3.0 (2026-02-07): Base calculator with accessories pricing
