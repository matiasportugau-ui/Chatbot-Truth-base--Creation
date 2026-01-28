# Complete GPT PDF Implementation Guide

**Goal**: Integrate professional PDF quotation generation into your Panelin GPT with BMC Uruguay branding.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Access to your GPT configuration in OpenAI
- [ ] BMC Uruguay logo file (see instructions below)
- [ ] This codebase deployed and accessible
- [ ] Admin access to update GPT instructions

---

## Step 1: Get the BMC Uruguay Logo

### Option A: Find Logo in Existing Files

1. Check if logo exists in your system:
   ```bash
   find /Users/matias -name "*bmc*logo*.png" -o -name "*bmc*.png" 2>/dev/null | head -10
   ```

2. Common locations to check:
   - Downloads folder
   - BMC Uruguay website screenshots
   - Email attachments from BMC
   - Google Drive / Dropbox

### Option B: Download from BMC Website

1. Go to https://bmcuruguay.com.uy
2. Right-click on the logo in the header
3. "Save Image As..." → Save as `bmc_logo_original.png`
4. Or inspect element and find the high-res version

### Option C: Request from BMC Team

Contact:
- Email: info@bmcuruguay.com.uy
- Phone: 42224031
- Request: "Logo BMC Uruguay alta resolución para documentos PDF"

### Logo Specifications Required

- **Format**: PNG (with transparent background preferred)
- **Minimum Resolution**: 300 DPI
- **Recommended Size**: 800x300 pixels or larger
- **Aspect Ratio**: Preserve original (approximately 8:3)

---

## Step 2: Prepare the Logo File

Once you have the logo:

### 2.1 Save to Assets Folder

```bash
cd "/Users/matias/Chatbot Truth base Creation/Chatbot-Truth-base--Creation-1"

# Copy logo to assets folder
cp /path/to/your/downloaded/logo.png panelin_reports/assets/bmc_logo.png
```

### 2.2 Verify Logo File

```bash
# Check file exists
ls -lh panelin_reports/assets/bmc_logo.png

# Check image dimensions (if you have imagemagick)
# brew install imagemagick (if needed)
identify panelin_reports/assets/bmc_logo.png
```

Expected output:
```
bmc_logo.png PNG 800x300 8-bit sRGB 45KB
```

### 2.3 Test Logo in PDF

```bash
# Re-run PDF generation test with logo
python3 panelin_reports/test_pdf_generation.py
```

Open the generated PDF and verify logo appears in header.

---

## Step 3: Upload Code to GPT

### 3.1 Prepare PDF Generation Files

GPT Code Interpreter needs these files uploaded:

```bash
# Create a deployment package
mkdir -p gpt_pdf_package
cp panelin_reports/pdf_generator.py gpt_pdf_package/
cp panelin_reports/pdf_styles.py gpt_pdf_package/
cp panelin_reports/assets/bmc_logo.png gpt_pdf_package/
```

### 3.2 Upload to GPT

1. Go to your GPT configuration: https://chat.openai.com/gpts/editor/
2. Find your "Panelin - BMC Assistant" GPT
3. Click "Configure"
4. Under "Knowledge" section, click "Upload files"
5. Upload these 3 files:
   - `pdf_generator.py`
   - `pdf_styles.py`
   - `bmc_logo.png`

**Note**: These files become available to Code Interpreter automatically.

---

## Step 4: Update GPT Instructions

### 4.1 Add PDF Generation Section

Copy this entire section and paste it into your GPT instructions (in the appropriate location):

````markdown
---

## 📄 PDF Quotation Generation

### When to Generate PDF

Generate a professional PDF quotation when:
- User requests "genera PDF" or "cotización en PDF"
- User wants formal quotation for client delivery
- User asks for downloadable quotation

### PDF Generation Workflow

Use Code Interpreter to execute this workflow:

```python
# Import PDF generation functions
from pdf_generator import BMCQuotationPDF, QuotationDataFormatter, generate_quotation_pdf
from datetime import datetime

# 1. Calculate quotation using KB formulas (as you normally do)
quotation_data = {
    'client_name': '[CLIENT NAME FROM USER]',
    'client_address': '[ADDRESS FROM USER OR EMPTY]',
    'client_phone': '[PHONE FROM USER OR EMPTY]',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'quote_description': '[e.g., "Isopanel 50 mm + Isodec EPS 100mm"]',
    'autoportancia': [CALCULATED VALUE],
    'apoyos': [CALCULATED VALUE],
    'products': [
        {
            'name': 'Isopanel EPS 50 mm (Fachada)',
            'length_m': [LENGTH],
            'quantity': [QTY],
            'unit_price_usd': [PRICE FROM KB],
            'total_usd': [CALCULATED],
            'total_m2': [CALCULATED]
        },
        # ... add all calculated products
    ],
    'accessories': [
        # ... calculated accessories (perfiles, canalones)
    ],
    'fixings': [
        # ... calculated fixings (tornillos, silicona)
    ],
    'shipping_usd': 280.0  # Standard, or custom
}

# 2. Generate PDF
client_name_clean = quotation_data['client_name'].replace(' ', '_')
date_str = datetime.now().strftime('%Y%m%d')
pdf_filename = f'cotizacion_{client_name_clean}_{date_str}.pdf'

pdf_path = generate_quotation_pdf(quotation_data, pdf_filename)

# 3. Confirm generation
print(f"✅ PDF generado exitosamente: {pdf_path}")
print(f"📄 El archivo está listo para descargar.")
```

### Important Notes

1. **Always calculate first**: Use your KB formulas to calculate all items before PDF generation
2. **IVA is automatic**: The PDF generator automatically calculates 22% IVA
3. **Validate data**: Ensure all prices are from official catalog
4. **Check autoportancia**: Verify it's within safe limits before generating PDF
5. **Logo is included**: BMC Uruguay logo appears automatically in header

### Data Requirements

**Minimum Required**:
- `client_name`: Client's name
- `products`: At least one product with price and quantity

**Recommended**:
- `client_address`: Client's full address
- `client_phone`: Client's contact number
- `quote_description`: Brief description
- `accessories`: All calculated profiles and accessories
- `fixings`: All calculated fixings and sealants

### Example User Interaction

**User**: "Genera cotización PDF para arquitecto Rodríguez, 300m² Isopanel 50mm"

**Your Response**:

1. Calculate quotation using KB formulas
2. Display calculation summary:
   ```
   📋 Cotización calculada:
   
   Cliente: Arquitecto Rodríguez
   Producto: Isopanel EPS 50 mm (Fachada)
   Área: 300 m²
   
   PANELES:
   • Isopanel EPS 50 mm: 300 m² × $33.21 = $9,963.00
   
   ACCESORIOS:
   • Perfil U 50mm: 45 ml × $3.90 = $175.50
   [... más items ...]
   
   💰 TOTALES:
   Sub-Total:      $10,500.00
   IVA 22%:        $2,310.00
   Materiales:     $12,810.00
   Traslado:       $280.00
   ────────────────────────
   TOTAL U$S:      $13,090.00
   
   Generando PDF profesional...
   ```

3. Execute PDF generation in Code Interpreter
4. Confirm completion:
   ```
   ✅ Cotización PDF generada exitosamente.
   
   📄 El PDF incluye:
   • Logo y branding BMC Uruguay
   • Información completa del cliente
   • Detalle de productos y accesorios
   • Cálculos con IVA 22%
   • Términos y condiciones
   • Información bancaria para pago
   
   📥 Descargue el PDF usando el botón de descarga arriba.
   ```

### Error Handling

If PDF generation fails:

```python
try:
    pdf_path = generate_quotation_pdf(quotation_data, pdf_filename)
    print(f"✅ PDF generado: {pdf_path}")
except Exception as e:
    print(f"❌ Error generando PDF: {e}")
    print("📋 Mostrando cotización en formato texto:")
    # Display text-based quotation as fallback
```

### Quality Checklist Before PDF Generation

Verify:
- [ ] All calculations are correct (double-check totals)
- [ ] Prices are from official catalog (BMC_Base_Conocimiento_GPT-2.json)
- [ ] IVA rate is 22% (Uruguay 2026)
- [ ] Autoportancia is validated
- [ ] Accessories calculated per KB formulas
- [ ] Fixings calculated per KB formulas
- [ ] Client information is complete

---
````

### 4.2 Where to Insert This Section

Insert the PDF section **after** your quotation calculation instructions and **before** your general conversation guidelines.

Recommended location:
```
[... existing quotation formulas ...]

## 📄 PDF Quotation Generation
[INSERT THE SECTION ABOVE]

[... general conversation guidelines ...]
```

---

## Step 5: Test the Integration

### 5.1 Basic Test

1. Start a new chat with your GPT
2. Say: "Genera cotización PDF de prueba para Juan Pérez, 100m² Isopanel 50mm"
3. GPT should:
   - Calculate the quotation
   - Generate PDF using Code Interpreter
   - Provide download link

### 5.2 Verify PDF Quality

Download and check:
- [ ] Logo appears in header
- [ ] Company contact info correct
- [ ] Client information populated
- [ ] Products table formatted correctly
- [ ] Accessories and fixings included
- [ ] Totals calculated correctly (IVA 22%)
- [ ] Terms & conditions present
- [ ] Banking information correct

### 5.3 Test Edge Cases

Test with:
- Minimal data (only client name + 1 product)
- Large quotation (many products)
- Missing client address/phone
- Different product types

---

## Step 6: Production Deployment

### 6.1 Final Checklist

Before announcing to users:

- [ ] Logo displays correctly in PDFs
- [ ] All calculations are accurate
- [ ] Company information is current
- [ ] Banking details are correct
- [ ] Terms & conditions are up to date
- [ ] Multiple test PDFs generated successfully
- [ ] Sales team has reviewed sample PDFs
- [ ] Legal has approved terms & conditions

### 6.2 Announce to Users

Update your GPT description to mention PDF capability:

```
Panelin - BMC Assistant Pro

Tu asistente integral para cotizaciones BMC Uruguay.

✅ Cotizaciones precisas con fórmulas validadas
✅ Generación de PDF profesional con logo BMC
✅ IVA 22% automático (2026)
✅ Términos y condiciones incluidos
✅ Listo para enviar a clientes
```

---

## Troubleshooting

### Issue: Logo Not Appearing

**Solution**:
```bash
# Verify logo file exists
ls -la panelin_reports/assets/bmc_logo.png

# If missing, re-upload to GPT Knowledge
# Make sure file is named exactly: bmc_logo.png
```

### Issue: "Module not found" Error

**Solution**:
```python
# GPT Code Interpreter needs files uploaded
# Re-upload pdf_generator.py and pdf_styles.py to Knowledge section
```

### Issue: Calculations Wrong

**Solution**:
```python
# Verify you're using KB formulas, not hardcoded values
# Check IVA rate is 0.22
# Validate against BMC_Base_Conocimiento_GPT-2.json
```

### Issue: PDF Too Large

**Solution**:
```bash
# Optimize logo file
# Reduce to 800x300 pixels max
# Use PNG compression
```

### Issue: Missing Accessories/Fixings

**Solution**:
```python
# Ensure you're calculating ALL items per KB formulas
# Don't skip accessories or fixings
# Use complete formulas from BMC_Base_Conocimiento_GPT-2.json
```

---

## Advanced Configuration

### Customize Colors

Edit `pdf_styles.py` in GPT Knowledge:

```python
class BMCStyles:
    # Change brand color
    BMC_BLUE = colors.HexColor('#003366')  # Original
    BMC_BLUE = colors.HexColor('#YOUR_COLOR')  # Custom
```

### Customize Conditions

Edit `pdf_styles.py`:

```python
@classmethod
def get_standard_conditions(cls):
    return [
        "*Your custom condition here",
        # ... add or modify conditions
    ]
```

### Add Custom Fields

Edit `pdf_generator.py`:

```python
def _build_header(self, data: Dict) -> List:
    # Add custom header fields
    elements.append(Paragraph("Custom field: " + data.get('custom'), style))
```

---

## Maintenance

### Update Logo

```bash
# Replace logo file
cp /path/to/new/logo.png panelin_reports/assets/bmc_logo.png

# Re-upload to GPT Knowledge
# (GPT → Configure → Knowledge → Upload bmc_logo.png)
```

### Update Terms & Conditions

```bash
# Edit pdf_styles.py
# Find get_standard_conditions() method
# Update conditions array
# Re-upload to GPT Knowledge
```

### Update Banking Info

```bash
# Edit pdf_styles.py
# Find QuotationConstants class
# Update BANK_* variables
# Re-upload to GPT Knowledge
```

---

## Quick Reference Card

### User Commands

| User Says | GPT Action |
|-----------|------------|
| "Genera PDF" | Calculate + generate PDF |
| "Cotización PDF para [nombre]" | Full quotation PDF |
| "PDF de prueba" | Test PDF with sample data |

### GPT Workflow

```
1. User requests PDF
   ↓
2. Calculate quotation (KB formulas)
   ↓
3. Display calculation summary
   ↓
4. Execute PDF generation (Code Interpreter)
   ↓
5. Provide download link
```

### File Locations

```
GPT Knowledge Files:
├── pdf_generator.py       (PDF generation engine)
├── pdf_styles.py          (Branding & styles)
└── bmc_logo.png          (Company logo)

Local System:
/Users/matias/Chatbot Truth base Creation/
└── Chatbot-Truth-base--Creation-1/
    └── panelin_reports/
        ├── pdf_generator.py
        ├── pdf_styles.py
        ├── assets/
        │   └── bmc_logo.png
        └── output/
            └── [generated PDFs]
```

---

## Support Contacts

### Technical Issues
- Check: `README_PDF_GENERATION.md`
- Test: `python3 panelin_reports/test_pdf_generation.py`

### Logo/Branding Issues
- BMC Email: info@bmcuruguay.com.uy
- BMC Phone: 42224031

### Content Updates
- Edit: `panelin_reports/pdf_styles.py`
- Re-upload to GPT Knowledge

---

## Success Metrics

Track these to measure success:

- [ ] PDFs generated per day
- [ ] Download rate (PDFs downloaded vs generated)
- [ ] User satisfaction feedback
- [ ] Calculation accuracy (manual verification)
- [ ] Time saved vs manual quotation creation

---

## Next Steps After Implementation

1. **Week 1**: Monitor closely for errors
2. **Week 2**: Gather user feedback
3. **Week 3**: Optimize based on feedback
4. **Month 2**: Consider enhancements:
   - Multi-page support
   - Product images in PDF
   - QR codes for validation
   - Email delivery automation

---

**Implementation Status**: Ready to deploy ✅  
**Last Updated**: 2026-01-28  
**Version**: 1.0  

**Estimated Implementation Time**: 30-60 minutes (depending on logo availability)
