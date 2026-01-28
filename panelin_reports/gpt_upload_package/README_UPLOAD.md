# GPT Upload Package - Quick Start

## ✅ What's In This Package

```
gpt_upload_package/
├── pdf_generator.py             ⭐ PDF generation engine
├── pdf_styles.py                ⭐ BMC branding & styles
├── GPT_PDF_INSTRUCTIONS.md      📋 Instructions to add to GPT
└── README_UPLOAD.md            📖 This file
```

**⚠️ MISSING**: `bmc_logo.png` - Add this before uploading!

---

## 🚀 Implementation in 5 Minutes

### Step 1: Get BMC Logo (2 min)

Choose one option:

**Option A - Download from Website**:
1. Go to https://bmcuruguay.com.uy
2. Right-click logo → "Save Image As"
3. Save as `bmc_logo.png` in this folder

**Option B - Search Your Files**:
```bash
# Run this to find existing logo files
find /Users/matias -name "*bmc*.png" 2>/dev/null | head -5
```

**Option C - Request from BMC**:
- Email: info@bmcuruguay.com.uy
- Subject: "Logo BMC Uruguay para PDF"

**Logo Specs**:
- Format: PNG
- Size: 800x300 pixels (approx)
- Resolution: 300 DPI minimum

---

### Step 2: Upload to GPT (1 min)

1. Go to: https://chat.openai.com/gpts/editor/
2. Select your **"Panelin - BMC Assistant"** GPT
3. Click **"Configure"**
4. Scroll to **"Knowledge"** section
5. Click **"Upload files"**
6. Select and upload:
   - [ ] `pdf_generator.py`
   - [ ] `pdf_styles.py`
   - [ ] `bmc_logo.png` (after you add it to this folder)

---

### Step 3: Update GPT Instructions (2 min)

1. Still in GPT Configure page
2. Find the **"Instructions"** text box
3. Open `GPT_PDF_INSTRUCTIONS.md` in this folder
4. Copy the **entire "📄 PDF Quotation Generation"** section
5. Paste it into your GPT Instructions (after quotation formulas section)
6. Click **"Save"** at top-right

---

### Step 4: Test (30 sec)

1. Start new chat with your GPT
2. Type: **"Genera cotización PDF de prueba para Juan Pérez, 100m² Isopanel 50mm"**
3. GPT should:
   - Calculate quotation
   - Generate PDF with logo
   - Provide download link

✅ **Done!** Your GPT can now generate professional PDFs.

---

## 📋 What Users Will See

### Example Interaction

**User**: "Genera PDF para arquitecto Rodríguez, 300m² Isopanel"

**GPT Response**:
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
✅ PDF generado exitosamente.

📄 El PDF incluye:
• Logo y branding BMC Uruguay
• Información completa del cliente
• Detalle de productos y accesorios
• Cálculos con IVA 22%
• Términos y condiciones
• Información bancaria

📥 Descargue el PDF arriba ⬆️
```

---

## 🎨 What's In The PDF

Every generated PDF includes:

### Header
- **BMC Uruguay logo** (your logo here)
- Company email: info@bmcuruguay.com.uy
- Website: www.bmcuruguay.com.uy
- Phone: 42224031
- Date & location
- Technical specs (autoportancia, apoyos)

### Client Info
- Client name, address, phone

### Products Table
| Producto | Largos | Cantidades | Costo m² | Total |
|----------|--------|------------|----------|-------|
| Isopanel... | 6.0 | 33 | $33.21 | $6,600.00 |

### Accessories & Fixings
All calculated items with pricing

### Totals
```
Sub-Total:      $XX,XXX.XX
IVA 22%:        $X,XXX.XX
Materiales:     $XX,XXX.XX
Traslado:       $280.00
──────────────────────────
TOTAL U$S:      $XX,XXX.XX
```

### Terms & Conditions
14 standard BMC Uruguay conditions

### Banking Info
BROU account details for payment

---

## ⚠️ Troubleshooting

### Logo Not Showing?

**Check**:
1. File is named exactly: `bmc_logo.png` (lowercase)
2. File is in this folder before upload
3. File is uploaded to GPT Knowledge
4. File format is PNG

**Fix**: Re-upload the logo file to GPT Knowledge

### "Module not found" Error?

**Fix**: Upload `pdf_generator.py` and `pdf_styles.py` to GPT Knowledge

### Calculations Wrong?

**Check**: Your GPT is using formulas from `BMC_Base_Conocimiento_GPT-2.json`

### PDF Download Not Working?

**Try**: Ask GPT to regenerate: "Genera de nuevo el PDF"

---

## 📞 Support

### Need Logo?
- Website: https://bmcuruguay.com.uy
- Email: info@bmcuruguay.com.uy
- Phone: 42224031

### Technical Issues?
- Check: `../GPT_FULL_IMPLEMENTATION_GUIDE.md`
- Test locally: `python3 ../test_pdf_generation.py`

### Update Content?
- Terms: Edit `pdf_styles.py` → QuotationConstants
- Colors: Edit `pdf_styles.py` → BMCStyles
- Re-upload edited file to GPT Knowledge

---

## 🎯 Success Checklist

Before announcing to users:

- [ ] Logo added to package
- [ ] All 3 files uploaded to GPT
- [ ] GPT instructions updated
- [ ] Test PDF generated successfully
- [ ] Logo appears in PDF
- [ ] Calculations are correct
- [ ] Company info is current
- [ ] Terms & conditions approved

---

## 📊 Expected Results

After implementation:

✅ **Professional PDFs** matching BMC Uruguay brand  
✅ **Automatic calculations** (IVA, totals, shipping)  
✅ **Consistent formatting** every time  
✅ **Time savings** vs manual quotation creation  
✅ **Client-ready** documents for immediate delivery  

---

## 🚀 Ready to Go!

**Current Status**: 
- ✅ PDF generation code ready
- ✅ Branding styles configured
- ✅ GPT instructions prepared
- ⚠️ **Need**: BMC logo file

**Next Action**: 
1. Add `bmc_logo.png` to this folder
2. Upload 3 files to GPT
3. Update GPT instructions
4. Test and enjoy! 🎉

---

**Package Created**: 2026-01-28  
**Version**: 1.0  
**For**: Panelin - BMC Assistant GPT
