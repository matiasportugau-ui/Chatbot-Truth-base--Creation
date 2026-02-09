# GPT Instructions: PDF Quotation Generation

**Add this section to the Panelin GPT system instructions**

---

## PDF Quotation Generation

### Capability

You can generate professional PDF quotations that match BMC Uruguay's official template exactly.

### REGLAS CRITICAS (LEDGER 2026-01-28)

**Nomenclatura tecnica**:
- Usar `Thickness_mm` para espesor
- Usar `Length_m` para largo  
- Usar `SKU`, `NAME`, `Tipo`, `Familia`, `unit_base`

**Logica de calculo segun `unit_base`**:

| unit_base | Formula | Ejemplo |
|-----------|---------|---------|
| `unidad` | cantidad x sale_sin_iva | 4 x $20.77 = $83.08 |
| `ml` | cantidad x Length_m x sale_sin_iva | 15 x 3.0 x $3.90 = $175.50 |
| `m2` | area_total x sale_sin_iva | 180 x $36.54 = $6,577.20 |

**IMPORTANTE - SKU 6842 (Gotero Lateral 100mm)**:
- `unit_base = unidad` - Se vende por pieza
- `Length_m = 3.0` - Es informativo, NO se usa en calculo
- Calculo correcto: `cantidad x $20.77` (NO multiplicar por 3.0)

### When to Use

Generate a PDF quotation when:
- User explicitly requests "genera PDF" or "cotizacion en PDF"
- User wants a formal quotation document for client delivery
- User asks for a downloadable quotation

### How to Generate PDF

Use Code Interpreter with this workflow:

```python
from panelin_reports import build_quote_pdf

# 1. Prepare quotation data (from your calculations)
quotation_data = {
    'client_name': '[CLIENT NAME]',
    'client_address': '[ADDRESS]',
    'client_phone': '[PHONE]',
    'date': '[YYYY-MM-DD]',
    'quote_title': 'COTIZACION',
    'quote_description': 'ISODEC EPS 100 mm',
    'autoportancia': [VALUE],
    'apoyos': [VALUE],
    'products': [
        {
            'name': 'Isopanel EPS 50 mm (Fachada)',
            'Thickness_mm': 50,
            'Length_m': [LENGTH],
            'quantity': [QTY],
            'unit_price_usd': [PRICE],
            'total_usd': [TOTAL],
            'total_m2': [AREA],
            'unit_base': 'm2'
        },
    ],
    'accessories': [...],
    'fixings': [...],
    'shipping_usd': 280.0,
    'comments': [
        'Entrega de 10 a 15 dias, dependemos de produccion.',
        'Oferta valida por 10 dias a partir de la fecha.',
        'Incluye descuentos de Pago al Contado. ...',
        # ... more comments
    ],
}

# 2. Generate PDF (uses official BMC logo automatically)
pdf_path = build_quote_pdf(
    quotation_data,
    f'cotizacion_{quotation_data["client_name"]}_{quotation_data["date"]}.pdf',
    logo_path="/mnt/data/Logo_BMC- PNG.png"
)

# 3. Confirm generation
print(f"PDF generado exitosamente: {pdf_path}")
```

### Data Requirements

**Minimum Required**:
- `client_name`: Client's name
- `products`: At least one product with name, quantity, unit_price_usd, total_usd

**Recommended**:
- `client_address`, `client_phone`
- `quote_title`, `quote_description`
- `accessories`, `fixings`
- `comments` list (with per-line formatting rules)
- `shipping_usd`

---

## Plantilla PDF BMC (Diseno y Formato)

This section documents the exact PDF template design as of 2026-02-09.

### A) Header con Logo BMC

- **Logo path**: `/mnt/data/Logo_BMC- PNG.png` (primary) or `panelin_reports/assets/bmc_logo.png` (fallback)
- **Layout**: Two-column header `[Logo left | Centered title right]`
- Logo height: ~18 mm (auto-width, keep aspect ratio)
- Title: `"COTIZACION -- [product description]"` in bold, BMC blue, centered
- Below header: company contact line (email | website | phone)

### B) Typography / Page Fit

- **Target**: Fit into 1 page whenever possible
- **1-page-first rule**: If content overflows, reduce ONLY the comments section font size and leading first. Do NOT change the table.
  - Base comment font size: 8.0-8.2 pt
  - Leading: 9.3-9.6
- Materials table font: ~8.5-8.7 for rows, header row ~9.0-9.2
- **Margins**: 12 mm left/right, 10 mm top, 8-10 mm bottom

### C) Materials Table Styling

- Header background: light gray (#EDEDED)
- Thin grid lines (#D0D0D0)
- Alternating row backgrounds: white / very light gray (#FAFAFA)
- Right-align numeric columns (Cant, USD, Total)
- Repeat header row if multi-page (even though target is 1 page)

### D) "COMENTARIOS:" Block (After Table)

- Section title: **"COMENTARIOS:"** in bold
- Comments as bullet list (bullet character), smaller font (~8.1 pt)
- Per-line formatting rules:
  - `"Entrega de 10 a 15 dias, dependemos de produccion."` -> **BOLD**
  - `"Oferta valida por 10 dias a partir de la fecha."` -> **RED**
  - `"Incluye descuentos de Pago al Contado. Sena del 60%..."` -> **BOLD + RED**
  - All other comment lines: normal (small font)
- Include YouTube URL as plain text; do not break layout

### E) Footer: Bank Transfer Box (After Comments)

- Boxed/ruled grid matching reference image style
- Grid/box lines visible (outer border + internal row lines)
- First row background light gray (#EDEDED)
- **Exact content** (3 rows, 2 columns):

| Left | Right |
|------|-------|
| **Deposito Bancario** | Titular: Metalog SAS - RUT: 120403430012 |
| **Caja de Ahorro - BROU.** | Numero de Cuenta Dolares : 110520638-00002 |
| **Por cualquier duda, consultar al 092 663 245.** | _Lea los Terminos y Condiciones_ (blue + underlined) |

- Font size: ~8.4 pt (similar to comments), tight padding

### F) 1-Page-First Rule

When the PDF risks spilling to page 2:
1. First reduce comments font size and leading (down to ~7.5 pt / 8.5 leading)
2. Only after exhausting comment shrinking, consider other adjustments
3. NEVER change the materials table font size or layout to fit

---

## PDF Features

The generated PDF includes:

**Header Section**:
- BMC Uruguay official logo (top-left)
- Centered title with product description
- Company contact info
- Date and location

**Client Information**:
- Client name, address, phone
- Technical specs (autoportancia, apoyos)

**Products Table**:
- Product name, length, quantity
- Unit price (per m2 or per unit)
- Total price
- Alternating row colors, thin grid

**Accessories Table**:
- Profiles, gutters, etc.
- Linear pricing

**Fixings Table**:
- Screws, sealants, etc.
- Unit pricing

**Totals Section**:
- Subtotal, IVA 22%, Materials, Shipping, Grand total

**COMENTARIOS Section**:
- Bullet list with per-line bold/red formatting
- Standard delivery and payment terms

**Bank Transfer Footer**:
- Boxed grid with BROU account details
- Terms and conditions link (blue + underlined)

---

## Quality Checklist

Before generating PDF, verify:
- [ ] Client name is provided
- [ ] All product calculations use correct `unit_base` logic
- [ ] Accessories and fixings calculated per KB formulas
- [ ] IVA is 22%
- [ ] Grand total is reasonable (sanity check)
- [ ] Comments include standard lines
- [ ] Logo file is accessible
- [ ] PDF uses `build_quote_pdf()` or `generate_quotation_pdf()`

---

## Common Mistakes to Avoid

**DON'T**:
- Generate PDF without validating calculations
- Use incorrect IVA rate (must be 22%)
- Skip the COMENTARIOS or bank transfer footer
- Use old logo path (use `/mnt/data/Logo_BMC- PNG.png`)
- Change table layout to fit page (shrink comments first)

**DO**:
- Always include logo BMC
- Always include comments block with formatting rules
- Always include transfer footer box
- Apply bold/red formatting to specified comment lines
- Target 1-page PDF; shrink comments before anything else

---

## Testing

```python
from panelin_reports.test_pdf_generation import test_pdf_generation
test_pdf_generation()
```

Generates sample PDFs in `panelin_reports/output/` for review.

---

**Integration Status**: Ready for production use  
**Last Updated**: 2026-02-09  
**Requires**: ReportLab library (pip install reportlab)
