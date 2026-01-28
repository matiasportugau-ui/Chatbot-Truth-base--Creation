# BMC Uruguay Quotation PDF Generation Plan

## Executive Summary

Based on the analysis of `Cotización 01042025 BASE - Isopanel xx mm - Isodec EPS xx mm -desc- WA.ods`, this document outlines the complete plan to implement PDF generation that replicates the exact structure, design, and branding of BMC Uruguay quotations.

---

## 1. Document Structure Analysis

### 1.1 Header Section (Rows 0-3)
```
┌─────────────────────────────────────────────────────────────┐
│ [BMC LOGO]              info@bmcuruguay.com.uy             │
│                         www.bmcuruguay.com.uy              │
│                         42224031                            │
│                         Fecha: 2025-03-10                   │
│                         Maldonado, Uy.                      │
│                                                Autoportancia: 5.5m│
│                                                Apoyos: 1           │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Title Section (Row 4)
```
Cotización: Isopanel 50 mm + Isodec EPS 100mm
```

### 1.3 Client Information (Rows 5-7)
```
Cliente: [NOMBRE]
Dirección: [DIRECCION]
Tel/cel: [TELEFONO]
```

### 1.4 Products Table (Rows 9-12)
| Producto | Largos (m) | Cantidades | Costo m2 (USD) | Costo Total (USD) |
|----------|------------|------------|----------------|-------------------|
| Isopanel EPS 50 mm (Fachada) | 0 | 0 | 33.21 | 0 |
| Isopanel EPS 50 mm (Fachada) | 0 | 0 | 33.21 | 0 |
| Isodec EPS 100 mm (Cubierta) | 0 | 0 | 36.54 | 0 |

### 1.5 Accesorios Section (Rows 13-22)
Table with linear cost items (profiles, gutters, etc.)

### 1.6 Fijaciones Section (Rows 23-35)
Table with unit cost items (fixings, sealants, etc.)

### 1.7 Totals Section (Rows 36-40)
```
Sub-Total:         16.63 USD
IVA 22%:           3.66 USD
Materiales:        20.29 USD
Traslado:          280.00 USD
TOTAL U$S:         300.29 USD
```

### 1.8 Comentarios Section (Rows 41-54)
Extensive terms and conditions in bullet points

### 1.9 Banking Information (Rows 55-57)
Bank account details for payment

---

## 2. PDF Generation Implementation Strategy

### 2.1 Technology Stack

**Recommended: ReportLab** ✅
- **Pros**: Professional-grade PDFs, precise control, supports complex layouts
- **Use Case**: Perfect for structured business documents with tables
- **Performance**: Fast, battle-tested

**Alternative: FPDF2**
- **Pros**: Simpler API, easier learning curve
- **Cons**: Less flexible for complex layouts

### 2.2 Required Dependencies

Add to `requirements.txt`:
```python
reportlab>=4.0.0
Pillow>=10.0.0  # Already installed, for logo handling
```

---

## 3. PDF Design Specifications

### 3.1 Page Layout
```
- Page Size: A4 (210mm x 297mm)
- Orientation: Portrait
- Margins: 
  - Top: 15mm
  - Bottom: 15mm
  - Left: 15mm
  - Right: 15mm
- Font Family: Helvetica (or custom BMC font if available)
```

### 3.2 Color Scheme
```
- Primary Text: Black (#000000)
- Headers: Dark Blue (#003366) - BMC brand color
- Table Headers: Light Gray background (#E8E8E8)
- Table Borders: Medium Gray (#CCCCCC)
- Totals Section: Bold with highlight background
```

### 3.3 Typography
```
- Title (Cotización): 18pt Bold
- Section Headers: 12pt Bold
- Client Info Labels: 10pt Bold
- Client Info Values: 10pt Regular
- Table Headers: 9pt Bold
- Table Content: 9pt Regular
- Comments: 8pt Regular
- Bank Info: 8pt Regular
```

---

## 4. Component Breakdown

### 4.1 Logo Integration
```python
# Logo placement: Top-left corner
# Size: 80mm x 30mm (scaled proportionally)
# Format: PNG/JPG
# Location: /path/to/bmc_logo.png
```

**Action Required**: Obtain BMC Uruguay official logo
- High resolution (300 DPI minimum)
- Transparent background preferred
- Official brand colors

### 4.2 Header Block
```python
class QuotationHeader:
    - BMC Logo (left)
    - Contact Info (right):
      * Email: info@bmcuruguay.com.uy
      * Website: www.bmcuruguay.com.uy
      * Phone: 42224031
    - Date: [Dynamic]
    - Location: Maldonado, Uy.
    - Technical Specs (right side):
      * Autoportancia: [Dynamic] m
      * Apoyos: [Dynamic]
```

### 4.3 Client Information Block
```python
class ClientInfo:
    - Cliente: [input_data['client_name']]
    - Dirección: [input_data['client_address']]
    - Tel/cel: [input_data['client_phone']]
```

### 4.4 Products Table
```python
class ProductsTable:
    columns = [
        'Producto',          # 40% width
        'Largos (m)',        # 15% width
        'Cantidades',        # 15% width
        'Costo m2 (USD)',    # 15% width
        'Costo Total (USD)'  # 15% width
    ]
    
    # Dynamic rows from quotation data
    # Support for multiple product types:
    # - Panels (Isopanel, Isodec)
    # - Profiles (Accesorios)
    # - Fixings (Fijaciones)
```

### 4.5 Totals Calculation Block
```python
class TotalsSection:
    - Sub-Total: sum(all_items)
    - Total m² Fachada: [calculated]
    - Total m² Cubierta: [calculated]
    - IVA 22%: subtotal * 0.22
    - Materiales: subtotal + iva
    - Traslado: [input or default 280]
    - TOTAL U$S: materiales + traslado
```

### 4.6 Conditions Section
```python
class ConditionsBlock:
    # Standard BMC Uruguay conditions (from template):
    conditions = [
        "*Ancho útil paneles de Fachada = 1,14 m de Cubierta =1,12 m. Autoportancia de techo 5,5 m. *Pendiente mínima 7%.",
        "*Para saber más del sistema constructivo SPM haga click en https://youtu.be/Am4mZskFMgc",
        "*Fabricación y entrega de 10 a 15 días. Dependiendo de Producción. *Sujeto a cambios según fábrica.",
        # ... (all 14 conditions from template)
    ]
```

### 4.7 Banking Information Block
```python
class BankingInfo:
    bank_details = {
        'titular': 'Metalog SAS - RUT: 120403430012',
        'account_type': 'Caja de Ahorro - BROU',
        'account_number_usd': '110520638-00002'
    }
```

---

## 5. Implementation Plan

### 5.1 File Structure
```
panelin_reports/
├── __init__.py
├── pdf_generator.py          # New: Main PDF generator class
├── pdf_templates.py          # New: PDF-specific templates
├── pdf_styles.py             # New: ReportLab styles configuration
├── report_generator.py       # Existing: Update to use PDF generator
├── report_templates.py       # Existing
└── assets/
    ├── bmc_logo.png          # New: BMC Uruguay logo
    └── fonts/                # Optional: Custom fonts
        └── [custom_font].ttf
```

### 5.2 Core Classes

#### 5.2.1 BMCQuotationPDF
```python
class BMCQuotationPDF:
    """
    Main PDF generator for BMC Uruguay quotations.
    Replicates exact structure from ODS template.
    """
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.page_width = A4[0]
        self.page_height = A4[1]
        self.styles = self._setup_styles()
        
    def generate(self, quotation_data: Dict) -> str:
        """Generate PDF from quotation data"""
        pass
        
    def _draw_header(self, canvas, data):
        """Draw header with logo and contact info"""
        pass
        
    def _draw_client_info(self, canvas, data):
        """Draw client information block"""
        pass
        
    def _draw_products_table(self, canvas, products):
        """Draw products table with pricing"""
        pass
        
    def _draw_accessories_table(self, canvas, accessories):
        """Draw accessories/profiles table"""
        pass
        
    def _draw_fixings_table(self, canvas, fixings):
        """Draw fixings/fijaciones table"""
        pass
        
    def _draw_totals(self, canvas, totals):
        """Draw totals section with calculations"""
        pass
        
    def _draw_conditions(self, canvas):
        """Draw terms and conditions"""
        pass
        
    def _draw_banking_info(self, canvas):
        """Draw bank account information"""
        pass
```

#### 5.2.2 QuotationDataFormatter
```python
class QuotationDataFormatter:
    """
    Formats quotation data from KB/API into PDF-ready structure
    """
    
    @staticmethod
    def format_for_pdf(raw_data: Dict) -> Dict:
        """
        Transform raw quotation data into structured PDF format
        
        Input: BMC KB quotation data
        Output: PDF-ready dictionary with all sections
        """
        pass
        
    @staticmethod
    def calculate_totals(items: List[Dict]) -> Dict:
        """Calculate all totals: subtotal, IVA, materials, shipping, grand total"""
        pass
        
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format currency as USD with 2 decimals"""
        return f"${amount:,.2f}"
```

#### 5.2.3 PDFStyles
```python
class PDFStyles:
    """
    Centralized style definitions for BMC quotations
    """
    
    # Colors
    BMC_BLUE = colors.HexColor('#003366')
    TABLE_HEADER_BG = colors.HexColor('#E8E8E8')
    TABLE_BORDER = colors.HexColor('#CCCCCC')
    
    # Fonts
    TITLE_FONT = ('Helvetica-Bold', 18)
    HEADER_FONT = ('Helvetica-Bold', 12)
    NORMAL_FONT = ('Helvetica', 10)
    SMALL_FONT = ('Helvetica', 8)
    
    @classmethod
    def get_table_style(cls):
        """Return ReportLab TableStyle for quotation tables"""
        pass
```

---

## 6. Data Flow Architecture

```
┌─────────────────────────┐
│  Panelin GPT            │
│  (User Input)           │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Quotation Calculator   │
│  (KB-based formulas)    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  QuotationDataFormatter │
│  (Structure for PDF)    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  BMCQuotationPDF        │
│  (ReportLab Generator)  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Output PDF File        │
│  cotizacion_YYYYMMDD.pdf│
└─────────────────────────┘
```

---

## 7. Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Install ReportLab
- [ ] Obtain BMC logo (high-res)
- [ ] Create basic PDF structure (header, footer, margins)
- [ ] Implement `PDFStyles` class
- [ ] Create simple test PDF

### Phase 2: Core Components (Week 1-2)
- [ ] Implement `BMCQuotationPDF` base class
- [ ] Header section with logo
- [ ] Client information block
- [ ] Basic table structure

### Phase 3: Data Integration (Week 2)
- [ ] Implement `QuotationDataFormatter`
- [ ] Connect to BMC KB pricing data
- [ ] Products table with dynamic data
- [ ] Accessories and fixings tables
- [ ] Totals calculations (IVA 22%, shipping, etc.)

### Phase 4: Polish & Branding (Week 3)
- [ ] Exact color matching
- [ ] Typography refinement
- [ ] Conditions section formatting
- [ ] Banking information block
- [ ] Multi-page support (if needed)

### Phase 5: Testing & Validation (Week 3)
- [ ] Unit tests for calculations
- [ ] Visual comparison with original ODS
- [ ] Test with real quotation data
- [ ] GPT integration testing

### Phase 6: Deployment (Week 4)
- [ ] Update GPT instructions with PDF generation command
- [ ] Documentation for users
- [ ] Example quotations gallery
- [ ] Production deployment

---

## 8. GPT Integration

### 8.1 Command Structure
```
User: "Genera cotización PDF para cliente Juan Pérez, 200m² Isopanel 50mm"

GPT Process:
1. Calculate quotation using KB formulas
2. Format data with QuotationDataFormatter
3. Generate PDF with BMCQuotationPDF
4. Save to output directory
5. Return download link to user
```

### 8.2 Code Interpreter Workflow
```python
# GPT will execute this in Code Interpreter:
from panelin_reports.pdf_generator import BMCQuotationPDF
from panelin_reports.pdf_templates import QuotationDataFormatter

# 1. Prepare quotation data
quotation_data = {
    'client_name': 'Juan Pérez',
    'client_address': 'Av. Principal 123, Maldonado',
    'client_phone': '099 123 456',
    'date': '2025-01-28',
    'products': [
        {
            'name': 'Isopanel EPS 50 mm (Fachada)',
            'length_m': 6.0,
            'quantity': 33,
            'unit_price_usd': 33.21,
            'total_usd': 6600.00
        },
        # ... more products
    ],
    'accessories': [ ... ],
    'fixings': [ ... ],
    'autoportancia': 5.5,
    'apoyos': 1
}

# 2. Format for PDF
formatted_data = QuotationDataFormatter.format_for_pdf(quotation_data)

# 3. Generate PDF
pdf_gen = BMCQuotationPDF('cotizacion_20250128_juan_perez.pdf')
output_file = pdf_gen.generate(formatted_data)

# 4. Return to user
print(f"✅ PDF generado: {output_file}")
# GPT provides download link
```

---

## 9. Key Features to Implement

### 9.1 Dynamic Calculations
- [x] IVA 22% (Uruguay tax rate for 2026)
- [x] Subtotals per section (panels, accessories, fixings)
- [x] Area calculations (m² fachada, m² cubierta)
- [x] Autoportancia validation
- [x] Shipping cost (default 280 USD, configurable)

### 9.2 Template Variations
```python
# Support multiple quote types:
- Standard quotation (full detail)
- Express quotation (simplified)
- Multi-product comparison
- Revision history (v1, v2, v3...)
```

### 9.3 Branding Elements
- [ ] BMC Uruguay logo (header)
- [ ] Official color scheme
- [ ] Company contact information
- [ ] Bank details footer
- [ ] QR code for online validation (future)

### 9.4 Terms & Conditions
```python
# Load from configuration file for easy updates:
conditions_config.json:
{
    "version": "2026-01",
    "conditions": [
        "*Ancho útil paneles...",
        "*Fabricación y entrega...",
        # ... all conditions
    ],
    "banking": {
        "titular": "Metalog SAS",
        "rut": "120403430012",
        # ...
    }
}
```

---

## 10. Quality Assurance

### 10.1 Visual Validation Checklist
- [ ] Logo placement matches original
- [ ] Font sizes match original
- [ ] Table column widths match original
- [ ] Color scheme matches BMC branding
- [ ] Margins and spacing match original
- [ ] Multi-page handling (overflow)
- [ ] Currency formatting (USD with 2 decimals)
- [ ] Date formatting (DD/MM/YYYY)

### 10.2 Calculation Validation
- [ ] IVA 22% calculated correctly
- [ ] Subtotals sum correctly
- [ ] Area calculations (m²) accurate
- [ ] Unit price x quantity = total
- [ ] Grand total includes all components

### 10.3 Content Validation
- [ ] All standard conditions included
- [ ] Bank details correct
- [ ] Contact information current
- [ ] Links functional (YouTube video)
- [ ] Terms and conditions version date

---

## 11. Future Enhancements

### 11.1 Advanced Features (Post-MVP)
- [ ] Electronic signature integration
- [ ] QR code for quotation validation
- [ ] Multi-currency support (USD, UYU, ARS)
- [ ] Product images in PDF
- [ ] 3D visualization integration
- [ ] Email delivery automation
- [ ] Customer portal integration

### 11.2 Analytics & Tracking
- [ ] PDF generation metrics
- [ ] Most quoted products
- [ ] Average quotation value
- [ ] Conversion tracking (quote → sale)

---

## 12. Resources & Dependencies

### 12.1 Python Libraries
```txt
reportlab>=4.0.0         # PDF generation
Pillow>=10.0.0           # Image handling (already installed)
python-dateutil>=2.8.0   # Date formatting (already installed)
```

### 12.2 Assets Needed
1. **BMC Uruguay Logo**
   - Format: PNG with transparent background
   - Resolution: 300 DPI minimum
   - Size: ~800x300px recommended
   
2. **Custom Fonts** (optional)
   - BMC brand font (if different from Helvetica)
   - TTF/OTF format
   
3. **Configuration Files**
   - `conditions_2026.json`: Terms and conditions
   - `banking_info.json`: Bank account details
   - `company_info.json`: Contact information

### 12.3 Documentation
- ReportLab User Guide: https://www.reportlab.com/docs/reportlab-userguide.pdf
- BMC Uruguay brand guidelines (if available)
- Quotation process flowchart

---

## 13. Success Criteria

### 13.1 Functional Requirements
✅ PDF matches original ODS template visually (95%+ accuracy)
✅ All calculations correct (100% accuracy)
✅ Generates in under 2 seconds
✅ Works from GPT Code Interpreter
✅ Handles edge cases (empty fields, large quantities)

### 13.2 Business Requirements
✅ Sales team approves design
✅ Legal approves terms & conditions
✅ Finance approves pricing calculations
✅ IT approves security (no sensitive data leaks)

---

## 14. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Logo not available | High | Request from stakeholder immediately |
| Color scheme mismatch | Medium | Get official brand colors from marketing |
| Calculation errors | Critical | Extensive unit testing, validation |
| PDF too large | Low | Optimize images, use compression |
| Multi-page overflow | Medium | Implement page break logic early |

---

## 15. Action Items - IMMEDIATE

### Priority 1 (This Week):
1. ✅ **Add ReportLab to requirements.txt**
2. ⚠️ **Obtain BMC Uruguay logo** (blocking)
3. ⚠️ **Verify company contact information** (email, phone, bank details)
4. ✅ **Create `pdf_generator.py` skeleton**
5. ✅ **Create basic test PDF to validate setup**

### Priority 2 (Next Week):
6. **Implement header section with logo**
7. **Implement client information block**
8. **Implement products table**
9. **Implement totals calculations**
10. **Create unit tests for calculations**

---

## 16. Stakeholder Communication

### Weekly Updates To:
- **Sales Team**: PDF design approval
- **Finance**: Pricing formula validation
- **Legal**: Terms & conditions review
- **Management**: Progress report

---

**Document Version**: 1.0  
**Date**: 2026-01-28  
**Author**: AI Development Team  
**Next Review**: 2026-02-04
