# BMC Uruguay PDF Generator - Quick Start

## ✅ System is Ready!

Your PDF generation system has been **implemented, tested, and validated**.

---

## 🚀 Generate Your First PDF

### Option 1: Using the convenience function

```python
from panelin_reports import generate_quotation_pdf

data = {
    'client_name': 'Juan Pérez',
    'client_address': 'Av. Principal 123, Maldonado',
    'products': [
        {
            'name': 'Isopanel EPS 50 mm (Fachada)',
            'length_m': 6.0,
            'quantity': 33,
            'unit_price_usd': 33.21,
            'total_usd': 6600.00,
            'total_m2': 200.0
        }
    ]
}

pdf = generate_quotation_pdf(data, 'mi_cotizacion.pdf')
print(f"✅ PDF creado: {pdf}")
```

### Option 2: Run the test script

```bash
cd "/Users/matias/Chatbot Truth base Creation/Chatbot-Truth-base--Creation-1"
python3 panelin_reports/test_pdf_generation.py
```

**Result**: 3 sample PDFs in `panelin_reports/output/`

---

## 📋 What's Included in the PDF?

Every PDF contains:

### 1. Header
- 📧 info@bmcuruguay.com.uy
- 🌐 www.bmcuruguay.com.uy
- ☎️ 42224031
- 📅 Date & Location
- 📐 Technical Specs (Autoportancia, Apoyos)

### 2. Client Info
- Cliente: [Name]
- Dirección: [Address]
- Tel/cel: [Phone]

### 3. Products Table
| Producto | Largos | Cantidades | Costo m² | Costo Total |
|----------|--------|------------|----------|-------------|
| Isopanel... | 6.0 | 33 | $33.21 | $6,600.00 |

### 4. Accessories (Perfiles)
- Perfil U, Perfil K2, Canalones, etc.

### 5. Fixings (Fijaciones)
- Silicona, Tornillos, Remaches, etc.

### 6. Totals
```
Sub-Total:      $16,678.36
IVA 22%:        $3,669.24
Materiales:     $20,347.60
Traslado:       $280.00
──────────────────────────
TOTAL U$S:      $20,627.60
```

### 7. Terms & Conditions
All 14 standard BMC Uruguay conditions

### 8. Banking Info
BROU account details for payment

---

## 🎨 Visual Preview

```
┌─────────────────────────────────────────────────────────┐
│ [BMC LOGO]         info@bmcuruguay.com.uy              │
│                    www.bmcuruguay.com.uy               │
│                    42224031                             │
│                    Fecha: 28/01/2026                    │
│                    Maldonado, Uy.                       │
│                                    Autoportancia: 5.5m  │
│                                    Apoyos: 1            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Cotización: Isopanel 50 mm + Isodec EPS 100mm          │
│                                                          │
│ Cliente: Juan Pérez                                     │
│ Dirección: Av. Principal 123, Maldonado                │
│ Tel/cel: 099 123 456                                    │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                    PRODUCTOS                             │
├──────────────┬────────┬──────────┬──────────┬──────────┤
│ Producto     │Largos  │Cantidades│Costo m²  │Total     │
├──────────────┼────────┼──────────┼──────────┼──────────┤
│ Isopanel...  │  6.0   │    33    │ $33.21   │$6,600.00 │
│ Isopanel...  │  5.5   │    15    │ $33.21   │$2,745.00 │
│ Isodec...    │  7.0   │    25    │ $36.54   │$6,388.50 │
├──────────────┴────────┴──────────┴──────────┴──────────┤
│                   ACCESORIOS                             │
├──────────────┬────────┬──────────┬──────────┬──────────┤
│ Perfil U...  │  3.0   │    10    │  $3.90   │  $117.00 │
│ Perfil Alu...│  6.8   │     5    │  $8.95   │  $304.30 │
├──────────────┴────────┴──────────┴──────────┴──────────┤
│                   FIJACIONES                             │
├──────────────┬────────┬──────────┬──────────┬──────────┤
│ Silicona...  │ 600gr  │     5    │  $9.78   │   $48.90 │
│ Tornillos... │  ⅜"    │    40    │  $0.15   │    $6.00 │
├──────────────┴────────┴──────────┴──────────┴──────────┤
│                     TOTALES                              │
│                                                          │
│                        Sub-Total:       $16,678.36      │
│                        Total m² Fachada:    282.5       │
│                        Total m² Cubierta:   175.0       │
│                        IVA 22%:          $3,669.24      │
│                        Materiales:      $20,347.60      │
│                        Traslado:           $280.00      │
│                        ═════════════════════════════     │
│                        TOTAL U$S:       $20,627.60      │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ Comentarios                                              │
│ *Ancho útil paneles de Fachada = 1,14 m...             │
│ *Para saber más del sistema constructivo SPM...        │
│ *Fabricación y entrega de 10 a 15 días...              │
│ [... 14 conditions total ...]                          │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ Depósito Bancario                                       │
│ Titular: Metalog SAS - RUT: 120403430012               │
│ Caja de Ahorro - BROU                                   │
│ Número de Cuenta Dólares: 110520638-00002              │
└─────────────────────────────────────────────────────────┘
```

---

## ⚡ For GPT Code Interpreter

Copy this into your GPT system:

```python
# When user requests PDF quotation:
from panelin_reports import generate_quotation_pdf

# 1. Calculate quotation (use your KB formulas)
quotation_data = {
    'client_name': '[FROM USER]',
    'products': [...],  # From your calculations
    'accessories': [...],
    'fixings': [...]
}

# 2. Generate PDF
pdf_path = generate_quotation_pdf(
    quotation_data,
    f'cotizacion_{client_name}.pdf'
)

print(f"✅ PDF generado: {pdf_path}")
```

---

## 🔴 ONE THING MISSING: BMC Logo

**Action Required**: Add BMC Uruguay logo to:

```
panelin_reports/assets/bmc_logo.png
```

**Specifications**:
- Format: PNG (transparent background)
- Resolution: 300 DPI minimum
- Recommended size: 800x300 pixels

Once added, logo will automatically appear in all PDFs.

---

## 📚 Documentation

- **Full Guide**: `README_PDF_GENERATION.md`
- **GPT Instructions**: `GPT_PDF_INSTRUCTIONS.md`
- **Implementation Plan**: `pdf_quotation_plan.md`
- **Summary**: `PDF_GENERATION_IMPLEMENTATION_SUMMARY.md`

---

## ✅ Verification Checklist

Test your first PDF:

- [ ] Run test script: `python3 panelin_reports/test_pdf_generation.py`
- [ ] Check output folder: `panelin_reports/output/`
- [ ] Open generated PDF
- [ ] Verify calculations are correct
- [ ] Verify all sections present
- [ ] Add BMC logo to assets folder
- [ ] Re-run test to see logo in PDF

---

## 🎉 You're Ready!

The PDF generation system is **complete and tested**. 

**Next Steps**:
1. Add BMC logo (see above)
2. Test with real quotation data
3. Integrate with Panelin GPT
4. Start generating professional quotations!

---

**Need Help?** Check `README_PDF_GENERATION.md` for full documentation.
