# GPT Configuration and Evaluation Review
Date: 2026-02-06

## Scope
This review checks the current GPT configuration and evaluation plan against the
requirements described in the request. Sources reviewed:
- docs/gpt/PANELIN_SYSTEM_INSTRUCTIONS_CANONICAL.md
- docs/gpt/PANELIN_GPT_TEST_PLAN.md
- docs/gpt/PANELIN_ACTIONS_SPEC.md
- gpt_configs/Panelin_Asistente_Integral_BMC_config_v2.0.json
- panelin_agent_v2/tools/quotation_calculator.py
- panelin_agent_v2/config/panelin_truth_bmcuruguay.json

## Current Configuration Snapshot
1. System instructions already define a KB hierarchy and strict source of truth.
2. Deterministic quotation code exists (panelin_agent_v2/tools/quotation_calculator.py).
3. Action spec is optional and still uses an older request/response shape.
4. Test plan focuses on KB compliance, client data collection, and core capabilities.

## Findings vs Requested Requirements

### 1) Accessories without price in KB
Evidence:
- panelin_agent_v2/config/panelin_truth_bmcuruguay.json has a small accessories
  section with limited SKUs.
- panelin_agent_v2/tools/quotation_calculator.py keeps accessories_total at 0
  (TODO: pricing not implemented).
Impact:
- Accessories are calculated but not valued. Quotes return "pending price"
  behavior in practice.

### 2) Action does not return valued line items
Evidence:
- docs/gpt/PANELIN_ACTIONS_SPEC.md returns "materiales" and a top-level total,
  but no per-SKU line items with unit price and totals.
Impact:
- Action output cannot directly produce a full BOM valuation table.

### 3) BOM rules are only partially codified
Evidence:
- PANELIN_QUOTATION_PROCESS.md lists a subset of formulas.
- No dedicated bom_rules.json (standard lengths, overlap, waste, cutting rules).
Impact:
- Profiles and accessory rounding rules are not centrally enforced.

### 4) Autoportancia is not integrated in deterministic flow
Evidence:
- Canonical instructions mention autoportancia validation.
- Deterministic calculator does not return an explicit "autoportancia complies"
  result in the quotation output.
Impact:
- The check lives in the conversational layer, not in the calculation output.

### 5) Field normalization gaps
Evidence:
- No single schema that standardizes unit (m2, ml, unid, kit), iva_included flag,
  finish/color pricing modifiers, or standard length rounding fields.
Impact:
- Harder to reason about line-item calculations and reuse across actions.

## Evaluation Plan Gaps (Test Plan Check)
The current test plan does not cover:
- Line items with unit price and totals for accessories and profiles.
- BOM rounding to standard length and waste/overlap.
- Autoportancia compliance returned in calculation output.
- Validation of unit normalization (m2, ml, unid, kit) and iva_included flag.

## Recommended Updates (Short List)
1. Add KB catalogs:
   - accessories_catalog.json with unit, price, length, finish, and compatibility.
   - bom_rules.json with parametric formulas per system (techo_isodec, etc).
2. Extend calculate_quote action response:
   - line_items[] with sku, name, unidad, cant, precio_unit, total.
   - autoportancia result object (cumple, margen, recomendacion).
   - subtotals by category and total_final_iva_inc.
3. Update deterministic calculator to price accessories using the new catalogs.
4. Normalize fields:
   - unit set (m2, ml, unid, kit)
   - iva_included flag
   - finish/color recargo pct
   - standard length rounding rule
5. Expand test plan with a BOM valuation suite and action output checks.

## Suggested Data Source for Accessories
The uploaded normalized_full.csv / normalized_full.json appear to contain SKU
level pricing for accessories and perfileria and can seed accessories_catalog.

## Conclusion
Configuration is strong for core pricing and governance, but the accessory BOM
valuation path is not fully implemented or tested. The above updates align the
configuration, action spec, and evaluation plan with the requested behavior.
