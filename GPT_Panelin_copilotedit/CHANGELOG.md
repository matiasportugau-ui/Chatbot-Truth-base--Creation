# CHANGELOG - Panelin GPT Calculator

## [3.1.0] - 2026-02-07

### Added - Autoportancia Validation
- **Span validation** to prevent structural failures
- New `validate_autoportancia()` function checks span against manufacturer limits
- `AutoportanciaValidationResult` TypedDict with validation details
- Optional `validate_span` parameter in `calculate_panel_quote()` (default True)
- 15% safety margin applied to all validations (industry standard)
- Intelligent recommendations when validation fails:
  - Suggests alternative thicknesses that would work
  - Or suggests adding intermediate support
- Coverage for 4 product families:
  - ISODEC_EPS (100, 150, 200, 250mm)
  - ISODEC_PIR (50, 80, 120mm)
  - ISOROOF_3G (30, 50, 80mm)
  - ISOPANEL_EPS (50, 100, 150, 200mm)

### Testing
- 9 comprehensive test cases added
- All tests pass (9/9)
- No regression in existing functionality (4/4 V3 tests still pass)

### Documentation
- `autoportancia_validation_guide.md` created (9.7 KB)
- Updated `calculator_v3_implementation_guide.md`
- Function docstrings with examples
- Usage examples for developers and GPT

### Technical Details
- Data source: `bom_rules.json` autoportancia table
- Warning mode: Non-blocking (quotations proceed with warnings)
- Performance: <5ms overhead per validation
- Backward compatible: Optional parameter, existing code unaffected

---

## [3.0.0] - 2026-02-07

### Added - Accessories Pricing (Phase 2)
- **Solved**: Critical TODO at line 602 (accessories valorization)
- Full accessories pricing with 97 catalog items
- `calculate_accessories_pricing()` function
- BOM system auto-detection (6 construction systems)
- Extended `AccessoriesResult` TypedDict with:
  - `line_items: List[QuotationLineItem]`
  - `accessories_subtotal_usd: float`
- Catalog caching for performance
- Sistema mapping from product family

### Changed
- TypedDict extended with pricing fields
- Accessories now return detailed line items with prices
- Grand total includes valorized accessories

### Testing
- 4 test cases added
- Validated: $452.19 accessories total
- All tests pass (4/4)

### Documentation
- `calculator_v3_implementation_guide.md` created
- `TEST_RESULTS_V3.md` created
- Implementation log maintained

---

## [2.0.0] - 2026-02-06 (Base Version)

### Features
- Deterministic quotation calculations with Decimal precision
- Panel quantity calculations
- Accessories quantity calculations (no pricing)
- Cut-to-length support
- Discount application
- IVA handling (22%)
- Verification flags (`calculation_verified: True`)

### Known Issues
- Line 450: `accessories_total = Decimal("0")  # TODO: Calculate from accessories prices`
- Accessories quantities calculated but not priced
- "Pendiente de precio" issue

---

## Version Comparison

| Feature | V2.0 | V3.0 | V3.1 |
|---------|------|------|------|
| **Panel pricing** | ✅ | ✅ | ✅ |
| **Accessories quantities** | ✅ | ✅ | ✅ |
| **Accessories pricing** | ❌ | ✅ | ✅ |
| **BOM valorization** | ❌ | ✅ | ✅ |
| **Span validation** | ❌ | ❌ | ✅ |
| **Safety recommendations** | ❌ | ❌ | ✅ |
| **Line items detail** | ❌ | ✅ | ✅ |
| **Lines of code** | 654 | 830 | 920+ |
| **Test coverage** | Basic | 4 tests | 13 tests |

---

## Upgrade Path

### From V2 to V3.1

**Breaking Changes**: None - fully backward compatible

**Recommended Actions**:
1. Update imports if using from separate module
2. Enable span validation: `validate_span=True` (default)
3. Handle `autoportancia_validation` in results
4. Update GPT instructions to mention safety validation

**Example Migration**:

```python
# V2 Code (still works)
result = calculate_panel_quote(
    product_id="ISODEC_EPS_100mm",
    length_m=4.5,
    width_m=10.0
)

# V3.1 Code (enhanced)
result = calculate_panel_quote(
    product_id="ISODEC_EPS_100mm",
    length_m=4.5,
    width_m=10.0,
    validate_span=True  # NEW: Optional parameter
)

# Check validation
if result.get('autoportancia_validation'):
    validation = result['autoportancia_validation']
    if not validation['is_valid']:
        print(f"⚠️  {validation['recommendation']}")
```

---

## Future Roadmap

### V3.2 - Strict Validation Mode (Planned)
- Add `strict_validation: bool = False` parameter
- Block quotations when validation fails (if strict mode enabled)
- Configurable safety margins per application

### V3.3 - Load Calculations (Planned)
- Add wind load validation
- Add snow load validation
- Roof slope validation
- Multi-factor analysis

### V4.0 - AI Optimization (Future)
- AI-powered thickness optimization (cost vs safety)
- Predictive load analysis
- Historical validation data analytics

---

## Breaking Changes History

None to date - all updates maintain backward compatibility.

---

## Contributors

- Phase 2 Implementation: GitHub Copilot CLI (2026-02-07)
- Autoportancia Validation: GitHub Copilot CLI (2026-02-07)
- Base Calculator V2: Panelin Team (2026-02-06)

---

## License

Internal use - BMC Uruguay / Panelin GPT Project
