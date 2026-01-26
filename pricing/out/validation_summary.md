# Bromyros Price Base - Validation Summary

## Overview

- **Total products**: 103
- **Unique SKUs**: 84
- **Duplicate SKUs**: 14

## Data Quality

- Missing cost (col F): 0
- Missing sale price (cols L/M): 0
- Missing web price (cols T/U): 1
- Negative prices: 0

## IVA Consistency

- Sale price IVA inconsistencies: 0 (100.00% pass rate)
- Web price IVA inconsistencies: 8 (92.23% pass rate)

## Length Extraction (Profiles)

- Total profiles: 60
- Profiles with length extracted: 31
- Hit rate: 51.67%

## Category Breakdown

- Panels: 36
- Profiles: 60
- Consumables: 3

## Issues by Severity

### HIGH (22)

- **IAGRO30**: SKU appears 2 times
- **BBAL**: SKU appears 2 times
- **CUMROOF3M**: SKU appears 2 times
- **IW50**: SKU appears 3 times
- **ISD100EPS**: SKU appears 2 times
- **ISD150EPS**: SKU appears 2 times
- **ISD200EPS**: SKU appears 2 times
- **ISD250EPS**: SKU appears 2 times
- **PU50MM**: SKU appears 4 times
- **PU150MM**: SKU appears 3 times
- **ISD80PIR**: SKU appears 2 times
- **GF120DC**: SKU appears 2 times
- **GL80DC**: SKU appears 2 times
- **CAN.ISDC120**: SKU appears 3 times
- **IAGRO30**: IVA inconsistency in web price: 47.21% delta
- **IAGRO50**: IVA inconsistency in web price: 47.21% delta
- **IROOF30**: IVA inconsistency in web price: 47.21% delta
- **IROOF40**: IVA inconsistency in web price: 47.21% delta
- **IROOF50**: IVA inconsistency in web price: 47.21% delta
- **IROOF80**: IVA inconsistency in web price: 47.21% delta

*... and 2 more. See `validation_issues.csv` for full list.*

### MEDIUM (0)

No issues.

### LOW (29)

- **GFS30**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GFS50**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GFS80**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GFSUP30**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GFSUP40**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GFSUP50**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GFSUP80**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GFCGR30**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GSDECAM30**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GSDECAM40**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GSDECAM50**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GSDECAM80**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GL30**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GL40**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GL50**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GL80**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GLDCAM50**: Profile without length extraction (col E) - cannot compute per_ml prices
- **GLDCAM80**: Profile without length extraction (col E) - cannot compute per_ml prices
- **BBAS3G**: Profile without length extraction (col E) - cannot compute per_ml prices
- **BBESUP**: Profile without length extraction (col E) - cannot compute per_ml prices

*... and 9 more. See `validation_issues.csv` for full list.*

---

*Generated: 2026-01-25T22:44:10.380251*
