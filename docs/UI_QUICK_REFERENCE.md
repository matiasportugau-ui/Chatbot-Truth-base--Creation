# Panelin UI Design - Quick Reference

**Quick access guide for developers implementing UI components**

## Color Codes

```css
/* Copy-paste ready CSS variables */
:root {
  /* Brand Colors */
  --bmc-blue-primary: #003366;
  --bmc-red-accent: #CC0000;
  
  /* Table Colors */
  --table-header-bg: #EDEDED;
  --table-alt-row-bg: #FAFAFA;
  
  /* Status Colors */
  --success: #28A745;
  --warning: #FFC107;
  --error: #DC3545;
  --info: #17A2B8;
}
```

## Typography

```python
# ReportLab Font Sizes
FONT_SIZES = {
    'title': 14,
    'header': 9.1,
    'body': 8.6,
    'comment': 8.1,
    'minimum': 8.0
}
```

## Message Format

```python
# User message
{
    "role": "user",
    "content": "Cotizar Isopanel 50mm 10m²"
}

# Assistant response with quotation
{
    "role": "assistant",
    "content": "Aquí está su cotización...",
    "quotation": {
        "quotation_id": "Q-20260218-abc123",
        "total_usd": "795.72"
    }
}
```

## Quotation Display Template

```
═══════════════════════════════════════════════════════════
            COTIZACIÓN PANELIN - BMC URUGUAY
═══════════════════════════════════════════════════════════

📋 ID: {quotation_id}
📦 Producto: {panel_type} {thickness_mm}mm
📏 Dimensiones: {length_m}m x {width_m}m x {quantity} unidades

─────────────────────────────────────────────────────────
💰 RESUMEN DE PRECIOS
─────────────────────────────────────────────────────────
Precio/m²:        USD {price_per_m2}
Área total:       {total_area_m2} m²
Subtotal:         USD {subtotal_usd}
Descuento ({discount_percent}%): USD {discount_amount}
─────────────────────────────────────────────────────────
TOTAL:            USD {total_usd}
─────────────────────────────────────────────────────────

✅ Validaciones:
  • Autoportancia: {autoportancia_status}
  • Cálculo verificado: {verification_status}
```

## BOM Table Structure

```python
# BOM Line Item
{
    "sku": "ISO-050-2M",
    "item": "Panel Isopanel 50mm x 2.0m",
    "quantity": 10,
    "unit": "panels",
    "price_usd": 83.76,
    "total_usd": 837.60,
    "category": "panel"
}
```

## PDF Table Style

```python
from reportlab.lib import colors
from reportlab.platypus import TableStyle

STANDARD_TABLE_STYLE = TableStyle([
    # Header
    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.93, 0.93, 0.93)),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9.1),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    
    # Body - alternating rows
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
     [colors.white, colors.Color(0.98, 0.98, 0.98)]),
    ('FONTSIZE', (0, 1), (-1, -1), 8.6),
    ('TOPPADDING', (0, 1), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    
    # Grid
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
])
```

## API Endpoints

```
POST   /api/conversations                    # Create new conversation
POST   /api/conversations/{id}/messages      # Send message
GET    /api/conversations/{id}/messages      # Get message history
GET    /api/quotations/{id}/pdf              # Download PDF
```

## Error Message Format

```python
{
    "error": True,
    "code": "INVALID_DIMENSIONS",
    "message": "Las dimensiones solicitadas están fuera de rango",
    "details": {
        "provided": {"length": 0.5, "width": 0.5},
        "minimum": {"length": 2.0, "width": 1.0}
    },
    "suggestion": "Ajuste las dimensiones al mínimo permitido"
}
```

## Status Icons

```
✅  Validation success
⚠️  Warning / Low stock
❌  Error / Unavailable
ℹ️  Information
📋  Quotation
📦  Product
💰  Pricing
📏  Dimensions
🔧  Technical specs
```

## Spacing Scale

```css
/* 8px base scale */
.space-xs  { margin: 4px; }   /* 0.5 × base */
.space-sm  { margin: 8px; }   /* 1 × base */
.space-md  { margin: 16px; }  /* 2 × base */
.space-lg  { margin: 24px; }  /* 3 × base */
.space-xl  { margin: 32px; }  /* 4 × base */
.space-xxl { margin: 48px; }  /* 6 × base */
```

## Validation Rules

```python
# Minimum dimensions
MIN_LENGTH_M = 2.0
MIN_WIDTH_M = 1.0
MIN_THICKNESS_MM = 50

# Maximum dimensions
MAX_LENGTH_M = 12.0
MAX_WIDTH_M = 1.2  # Standard width

# Discount limits
MAX_DISCOUNT_PERCENT = 15.0

# Autoportancia validation
def validate_autoportancia(length_m, width_m, thickness_mm):
    """
    Validates self-supporting span based on panel specifications.
    Returns (is_valid: bool, message: str)
    """
    # Implementation in panelin/tools/autoportancia_validator.py
```

## Component Import Paths

```python
# Quotation calculator
from panelin.tools.quotation_calculator import calculate_panel_quote

# BOM calculator
from panelin.tools.bom_calculator import calculate_bom

# PDF generator
from panelin_reports.pdf_generator import generate_quotation_pdf

# Message models
from panelin_hybrid_agent.agent.state_manager import Message, AgentState
```

## Testing Helpers

```python
# Test quotation
test_quote = {
    "panel_type": "Isopanel",
    "thickness_mm": 50,
    "length_m": 2.0,
    "width_m": 1.0,
    "quantity": 10
}

# Expected result structure
expected_result = {
    "quotation_id": "Q-*",  # Dynamic ID
    "total_usd": "837.60",   # Decimal as string
    "calculation_verified": True
}
```

## Common Patterns

### Pattern: Format Currency

```python
from decimal import Decimal, ROUND_HALF_UP

def format_currency(amount: Decimal) -> str:
    """Format Decimal as USD currency string"""
    return f"USD {amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"

# Usage
price = Decimal('837.60')
formatted = format_currency(price)  # "USD 837.60"
```

### Pattern: Generate Quotation ID

```python
import hashlib
from datetime import datetime

def generate_quotation_id() -> str:
    """Generate unique quotation ID"""
    timestamp = datetime.now().strftime('%Y%m%d')
    hash_suffix = hashlib.sha256(
        f"{timestamp}{datetime.now().timestamp()}".encode()
    ).hexdigest()[:8]
    return f"Q-{timestamp}-{hash_suffix}"

# Example: "Q-20260218-abc12345"
```

### Pattern: Validate Input Dimensions

```python
def validate_dimensions(length_m, width_m, thickness_mm):
    """Validate panel dimensions"""
    errors = []
    
    if length_m < MIN_LENGTH_M:
        errors.append(f"Largo mínimo: {MIN_LENGTH_M}m")
    
    if width_m != 1.0:  # Standard width
        errors.append(f"Ancho estándar: 1.0m")
    
    if thickness_mm not in [50, 80, 100, 120, 150, 200]:
        errors.append(f"Espesores disponibles: 50, 80, 100, 120, 150, 200mm")
    
    return (len(errors) == 0, errors)
```

### Pattern: Build BOM Table

```python
def build_bom_table(bom_items):
    """Convert BOM items to table data"""
    headers = ['SKU', 'Descripción', 'Cantidad', 'Unidad', 'P.Unit.', 'Total']
    
    rows = [headers]
    for item in bom_items:
        rows.append([
            item['sku'],
            item['item'],
            str(item['quantity']),
            item['unit'],
            format_currency(item['price_usd']),
            format_currency(item['total_usd'])
        ])
    
    return rows
```

## Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('panelin.ui')
logger.debug("Quotation calculation started")
```

### Test PDF Generation

```bash
# Generate test PDF
python -m panelin_reports.pdf_generator \
  --quotation-id "Q-TEST-001" \
  --output "./test_quotation.pdf"
```

### Validate JSON Structure

```bash
# Validate BOM JSON
python -m json.tool bom_result.json
```

## Performance Benchmarks

| Operation | Target | Typical |
|-----------|--------|---------|
| Quotation calculation | < 1s | ~300ms |
| BOM generation | < 2s | ~800ms |
| PDF creation | < 3s | ~1.5s |
| Message response | < 2s | ~1s |

## Accessibility Checklist

- [ ] Color contrast ratio ≥ 4.5:1 for text
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible
- [ ] Alt text for images
- [ ] ARIA labels for complex components
- [ ] Error messages descriptive and actionable
- [ ] Form inputs have labels
- [ ] Tables have proper headers

## Browser Support

| Browser | Minimum Version |
|---------|----------------|
| Chrome | 90+ |
| Firefox | 88+ |
| Safari | 14+ |
| Edge | 90+ |
| Mobile Safari | 14+ |
| Mobile Chrome | 90+ |

---

**See Also:**
- [Full UI Design Guide](./UI_DESIGN_GUIDE.md)
- [API Reference](./API_REFERENCE.md)
- [Knowledge Base Guide](../PANELIN_KNOWLEDGE_BASE_GUIDE.md)

**Last Updated:** 2026-02-18
