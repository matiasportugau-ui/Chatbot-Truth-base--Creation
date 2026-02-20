# Panelin Chatbot - User Interface Design Guide

**Version:** 1.0  
**Last Updated:** 2026-02-18  
**Status:** Comprehensive UI Design Documentation

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Conversation Interface](#conversation-interface)
4. [Quotation Display](#quotation-display)
5. [PDF Templates](#pdf-templates)
6. [BOM Presentation](#bom-presentation)
7. [User Flows](#user-flows)
8. [Visual Design System](#visual-design-system)
9. [Accessibility Guidelines](#accessibility-guidelines)
10. [Technical Implementation](#technical-implementation)

---

## Overview

The Panelin chatbot system provides an AI-powered conversational interface for BMC Uruguay's construction panel quotation and technical assistance services. The UI design focuses on professional presentation, accuracy, and ease of use for both customers and sales representatives.

### Key UI Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Chat Interface | Natural language interaction | FastAPI + Message Model |
| Quotation Display | Structured pricing breakdown | Pydantic TypedDict |
| PDF Generation | Professional document output | ReportLab |
| BOM Tables | Detailed material lists | Formatted tables with valuation |
| Analytics Dashboard | Interactive data visualization | HTML/CSS Grid |

---

## Design Principles

### 1. **Clarity & Precision**
- All financial calculations use `Decimal` type for exact precision
- Clear, unambiguous presentation of prices and quantities
- Explicit units and measurements (m², mm, USD)
- Structured data formats with verification checksums

### 2. **Professional Branding**
- Consistent BMC Uruguay brand colors:
  - Primary Blue: `#003366`
  - Accent Red: `#CC0000`
  - Neutral Gray: `#EDEDED` (headers)
  - Light Gray: `#FAFAFA` (alternating rows)
- Professional typography and spacing
- Logo placement on all generated documents

### 3. **Responsive & Accessible**
- Mobile-friendly conversation interface
- Readable font sizes (minimum 8.1pt for comments)
- High contrast ratios for text
- Screen reader compatible structure

### 4. **Contextual & Personalized**
- User profile-based personalization
- Conversation history retention
- Contextual recommendations
- Previous interaction references

### 5. **Error Prevention & Recovery**
- Input validation with clear error messages
- Autoportancia (self-supporting span) validation
- Minimum dimension checks
- Graceful error handling with Spanish messages

---

## Conversation Interface

### Message Structure

The chatbot uses a typed message model for structured conversations:

```typescript
interface Message {
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  tool_calls?: ToolCall[];
  tool_call_id?: string;
  name?: string;
}
```

### Conversation Flow

1. **User Input**
   - Natural language queries in Spanish
   - Structured parameter extraction
   - Validation and clarification requests

2. **Assistant Response**
   - Conversational tone matching BMC Uruguay's professional style
   - Technical accuracy with friendly explanations
   - Citations to knowledge base when possible

3. **Tool Integration**
   - Seamless calculator invocation
   - Transparent BOM generation
   - PDF creation on request

### State Management

```python
class AgentState(TypedDict):
    messages: Annotated[list[Message], operator.add]
    current_quotation: Optional[QuotationResult]
    tool_results: list[ToolResult]
    error: Optional[str]
```

**Key Features:**
- Message accumulation using `operator.add`
- Current quotation tracking for reference
- Tool results for multi-step operations
- Error state for graceful failure handling

### Personalization Layer

The system tracks user interactions to provide personalized responses:

- **User Profile**: Name, type (customer/representative), preferences
- **Interaction Patterns**: Frequently requested products, typical quantities
- **Context Retrieval**: "Based on your previous quotations..."
- **Recommendations**: Suggestions for accessories or alternatives

---

## Quotation Display

### Data Structure

```python
class QuotationResult:
    quotation_id: str           # Format: Q-YYYYMMDD-{hash}
    panel_type: str             # ISOPANEL, ISODEC, ISOROOF, ISOWALL
    thickness_mm: int           # 50, 80, 100, 120, 150, 200
    dimensions: {
        length_m: Decimal,
        width_m: Decimal,
        quantity: int
    }
    pricing: {
        price_per_m2: Decimal,
        total_area_m2: Decimal,
        total_usd: Decimal,
        discount_percent: Decimal,
        subtotal_usd: Decimal
    }
    validation: {
        autoportancia_ok: bool,
        calculation_verified: bool,
        warnings: list[str]
    }
    bom: list[BOMLineItem]
```

### Display Format

**Text-Based Quotation:**
```
═══════════════════════════════════════════════════════════
            COTIZACIÓN PANELIN - BMC URUGUAY
═══════════════════════════════════════════════════════════

📋 ID: Q-20260218-abc123
📦 Producto: Isopanel EPS 50mm
📏 Dimensiones: 2.0m x 1.0m x 10 unidades

─────────────────────────────────────────────────────────
💰 RESUMEN DE PRECIOS
─────────────────────────────────────────────────────────
Precio/m²:        USD 41.88
Área total:       20.0 m²
Subtotal:         USD 837.60
Descuento (5%):   USD -41.88
─────────────────────────────────────────────────────────
TOTAL:            USD 795.72
─────────────────────────────────────────────────────────

✅ Validaciones:
  • Autoportancia: OK
  • Cálculo verificado: OK
  • Sin advertencias

📦 Lista de Materiales (BOM): Ver detalle completo...
```

### Interactive Elements

- **Expand/Collapse BOM**: Toggle detailed material lists
- **PDF Download**: Generate professional PDF quotation
- **Modify Quote**: Adjust parameters and recalculate
- **Add to Cart**: Integration with ordering system (future)

---

## PDF Templates

### Professional Quotation PDF

**Location:** `/panelin_reports/pdf_generator.py`

**Layout Structure:**

```
┌─────────────────────────────────────────────────┐
│ [BMC Logo]         COTIZACIÓN PANELIN           │ ← Header (Blue #003366)
├─────────────────────────────────────────────────┤
│ ID: Q-20260218-xyz                              │
│ Fecha: 18/02/2026                               │
│ Cliente: [Nombre]                               │
├─────────────────────────────────────────────────┤
│ MATERIALES                                      │ ← Table Header (#EDEDED)
│┌────────┬─────────┬──────┬─────────┬──────────┐│
││ SKU    │ Descrip.│ Cant.│ P.Unit. │ Total    ││
│├────────┼─────────┼──────┼─────────┼──────────┤│
││ISO-050 │ Panel...│  10  │ 83.76   │ 837.60   ││ ← Row (#FAFAFA)
│├────────┼─────────┼──────┼─────────┼──────────┤│
││TOR-05  │ Tornillo│ 120  │  0.15   │  18.00   ││ ← Alt Row (White)
│└────────┴─────────┴──────┴─────────┴──────────┘│
├─────────────────────────────────────────────────┤
│ COMENTARIOS Y CONDICIONES:                      │
│ • Forma de pago: 50% anticipo, 50% contra entre│
│   ga (texto en NEGRITA y ROJO para destacar)   │
│ • Plazo de entrega: 10-15 días hábiles         │
│ • Precios en USD, IVA incluido                  │
├─────────────────────────────────────────────────┤
│ DATOS PARA TRANSFERENCIA BANCARIA:             │ ← Footer
│ Banco: [Banco]                                  │
│ Cuenta: [Número]                                │
└─────────────────────────────────────────────────┘
```

### Typography & Spacing

| Element | Font Size | Style | Color |
|---------|-----------|-------|-------|
| Title | 14pt | Bold | #003366 |
| Table Header | 9.1pt | Bold | Black on #EDEDED |
| Table Content | 8.6pt | Regular | Black |
| Comments | 8.1pt | Regular/Bold | Black/#CC0000 |
| Footer | 8pt | Regular | Gray |

### Comment Formatting Rules

Special formatting for important information:

1. **Payment Terms**: Bold + Red (#CC0000)
   - "Forma de pago: 50% anticipo..."
   
2. **Delivery Information**: Bold + Red
   - "Plazo de entrega: 10-15 días..."
   
3. **Validity Period**: Regular text
   - "Validez de cotización: 30 días"

### 1-Page-First Logic

The PDF generator optimizes for single-page output:

1. Calculate full content size
2. If > 1 page, reduce comment font size progressively
3. If still > 1 page, reduce table row height
4. Always maintain minimum readability (8pt minimum)

---

## BOM Presentation

### BOM Line Item Structure

```python
class BOMLineItem:
    sku: str                    # Product SKU
    item: str                   # Description
    quantity: Decimal           # Precise quantity
    unit: str                   # m², panels, units, ml
    price_usd: Decimal          # Unit price
    total_usd: Decimal          # Line total
    category: str               # panel, accessory, profile, etc.
    notes: Optional[str]        # Additional info
```

### Display Formats

#### **Compact View** (Chat/Text)
```
📦 LISTA DE MATERIALES (BOM)
─────────────────────────────────────────────────────
Panel Isopanel 50mm x 2.0m        10 panels  @ USD 83.76 = USD 837.60
Tornillos autoperforantes ø4.8   120 units  @ USD  0.15 = USD  18.00
Perfil U lateral 2m               20 ml      @ USD  2.50 = USD  50.00
Sellador silicona BMC             2 units    @ USD 12.00 = USD  24.00
─────────────────────────────────────────────────────
SUBTOTAL:                                              USD 929.60
```

#### **Detailed View** (PDF)
- Full table with all columns
- Category grouping (Panels, Accessories, Profiles, Finishes)
- Subtotals per category
- Notes and specifications
- Calculation verification checksum

#### **Interactive View** (Web/Dashboard)
- Expandable categories
- Click-to-edit quantities (for representatives)
- Real-time recalculation
- Product detail popups
- Inventory status indicators

### Validation Indicators

Visual feedback for BOM validation:

- ✅ **Green checkmark**: All items available
- ⚠️ **Yellow warning**: Some items low stock
- ❌ **Red X**: Items unavailable or validation failed
- ℹ️ **Info icon**: Additional specifications needed

---

## User Flows

### Flow 1: Simple Quotation Request

```
[User] → "Necesito cotizar Isopanel 50mm, 10 metros cuadrados"
    ↓
[Bot] → Extract parameters (panel type, thickness, area)
    ↓
[Bot] → Calculate dimensions (assume standard width)
    ↓
[Bot] → Run quotation calculator
    ↓
[Bot] → Display formatted quotation
    ↓
[Bot] → Offer: "¿Desea que genere el PDF profesional?"
```

### Flow 2: Complete Quotation with BOM

```
[User] → "Cotización completa con materiales para 20m² de Isopanel 50mm"
    ↓
[Bot] → Extract parameters
    ↓
[Bot] → Calculate panels needed
    ↓
[Bot] → Run BOM calculator (accessories, fixation, profiles)
    ↓
[Bot] → Display quotation + BOM
    ↓
[Bot] → Validate autoportancia
    ↓
[Bot] → Generate PDF with command /pdf
```

### Flow 3: Technical Consultation

```
[User] → "¿Qué espesor necesito para una luz de 4 metros?"
    ↓
[Bot] → Access autoportancia rules
    ↓
[Bot] → Calculate minimum thickness
    ↓
[Bot] → Present recommendations with safety margins
    ↓
[Bot] → Offer to generate quotation
```

### Flow 4: Multi-Product Comparison

```
[User] → "Comparar Isopanel vs Isodec para techo"
    ↓
[Bot] → Extract comparison parameters
    ↓
[Bot] → Generate quotations for both
    ↓
[Bot] → Present side-by-side comparison
    ↓
[Bot] → Highlight pros/cons of each option
```

### Flow 5: Error Recovery

```
[User] → "Cotizar panel 0.5m x 0.5m"
    ↓
[Bot] → Validation fails (below minimum)
    ↓
[Bot] → "Las dimensiones solicitadas están por debajo del mínimo.
         El panel Isopanel tiene un ancho estándar de 1m y largo
         mínimo de 2m. ¿Desea cotizar con las dimensiones mínimas?"
    ↓
[User] → "Sí, por favor"
    ↓
[Bot] → Recalculate with adjusted dimensions
```

---

## Visual Design System

### Color Palette

```css
/* Primary Colors - BMC Uruguay Branding */
--bmc-blue-primary: #003366;      /* Headers, titles, brand elements */
--bmc-blue-dark: #002244;         /* Hover states, emphasis */
--bmc-blue-light: #4a7ba7;        /* Secondary elements */

/* Accent Colors */
--bmc-red-accent: #CC0000;        /* Warnings, important notices */
--bmc-red-light: #FF6666;         /* Error states, alerts */

/* Neutral Colors */
--gray-header: #EDEDED;           /* Table headers */
--gray-alt-row: #FAFAFA;          /* Alternating table rows */
--gray-border: #CCCCCC;           /* Dividers, borders */
--gray-text: #666666;             /* Secondary text */

/* Status Colors */
--success-green: #28A745;         /* Validation success */
--warning-yellow: #FFC107;        /* Warnings */
--error-red: #DC3545;             /* Errors */
--info-blue: #17A2B8;             /* Information */
```

### Typography Scale

```css
/* Font Family */
font-family: 'Helvetica', 'Arial', sans-serif;

/* Font Sizes */
--font-xxl: 18pt;   /* Page titles */
--font-xl: 14pt;    /* Section headers */
--font-lg: 11pt;    /* Subheaders */
--font-md: 9.1pt;   /* Table headers */
--font-sm: 8.6pt;   /* Body text, table content */
--font-xs: 8.1pt;   /* Comments, footnotes */
--font-min: 8pt;    /* Minimum readable size */

/* Line Heights */
--line-height-tight: 1.2;
--line-height-normal: 1.4;
--line-height-relaxed: 1.6;
```

### Spacing System

```css
/* Consistent spacing scale (8px base) */
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;
--space-xxl: 48px;
```

### Component Library

#### **Button Styles**

```css
/* Primary Button */
.btn-primary {
  background: var(--bmc-blue-primary);
  color: white;
  padding: var(--space-sm) var(--space-lg);
  border-radius: 4px;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.btn-primary:hover {
  background: var(--bmc-blue-dark);
}

/* Secondary Button */
.btn-secondary {
  background: white;
  color: var(--bmc-blue-primary);
  border: 2px solid var(--bmc-blue-primary);
  padding: var(--space-sm) var(--space-lg);
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
}
```

#### **Table Styles**

```python
# ReportLab Table Style
table_style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.93, 0.93, 0.93)),  # Header
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9.1),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.98, 0.98, 0.98)]),
])
```

#### **Message Bubbles**

```css
/* User Message */
.message-user {
  background: #E3F2FD;
  padding: var(--space-sm) var(--space-md);
  border-radius: 18px 18px 4px 18px;
  max-width: 70%;
  margin-left: auto;
}

/* Assistant Message */
.message-assistant {
  background: #F5F5F5;
  padding: var(--space-sm) var(--space-md);
  border-radius: 18px 18px 18px 4px;
  max-width: 70%;
  margin-right: auto;
}
```

---

## Accessibility Guidelines

### WCAG 2.1 Level AA Compliance

#### **Color Contrast**
- All text meets minimum contrast ratio 4.5:1
- Large text (14pt+ bold) meets 3:1 ratio
- Important UI elements meet 3:1 contrast against background

#### **Keyboard Navigation**
- All interactive elements accessible via Tab
- Logical tab order following visual flow
- Visible focus indicators
- Escape key to cancel/close modals

#### **Screen Reader Support**
- Semantic HTML structure
- ARIA labels for complex components
- Alt text for all meaningful images
- Status announcements for async operations

#### **Text Scalability**
- Layouts support text zoom up to 200%
- No horizontal scrolling at 320px width
- Relative units (rem, em) for font sizes

### Spanish Language Accessibility

- Clear, professional Spanish terminology
- Avoid excessive jargon
- Provide explanations for technical terms
- Use consistent terminology across all interfaces

### Error Messaging

**Format:**
```
❌ Error: [Brief description]
ℹ️ Causa: [Explanation of what went wrong]
✅ Solución: [How to fix it]
```

**Example:**
```
❌ Error: Dimensiones no válidas
ℹ️ Causa: El ancho solicitado (0.5m) es menor al ancho estándar del panel (1m)
✅ Solución: Ajuste el ancho a 1m o consulte opciones especiales
```

---

## Technical Implementation

### Frontend Stack (Future Enhancement)

**Recommended:**
- **Framework**: React or Vue.js
- **State Management**: Redux or Pinia
- **Styling**: Tailwind CSS + custom theme
- **Charts**: Chart.js or D3.js
- **PDF Viewer**: PDF.js

### Backend Integration

**Current Architecture:**
```
FastAPI Backend (Python)
    ↓
Pydantic Models (Validation)
    ↓
LangGraph Agent (Orchestration)
    ↓
Quotation Calculator (Business Logic)
    ↓
ReportLab (PDF Generation)
```

### Message Transport

**REST API Endpoints:**
```
POST   /api/conversations              # Create conversation
POST   /api/conversations/{id}/messages # Send message
GET    /api/conversations/{id}/messages # Get history
GET    /api/conversations/{id}          # Get conversation state
DELETE /api/conversations/{id}          # End conversation
```

**WebSocket Support (Future):**
```
WS /api/conversations/{id}/stream      # Real-time message streaming
```

### Data Formats

**JSON Response Structure:**
```json
{
  "conversation_id": "conv-20260218-abc123",
  "timestamp": "2026-02-18T01:12:12Z",
  "message": {
    "role": "assistant",
    "content": "Aquí está su cotización...",
    "quotation": {
      "quotation_id": "Q-20260218-xyz789",
      "panel_type": "Isopanel",
      "total_usd": "795.72"
    }
  },
  "actions": [
    {
      "type": "download_pdf",
      "label": "Descargar PDF",
      "url": "/api/quotations/Q-20260218-xyz789/pdf"
    }
  ]
}
```

### Performance Considerations

| Component | Target | Optimization Strategy |
|-----------|--------|----------------------|
| Message Response | < 2s | Async tool execution, caching |
| PDF Generation | < 3s | Template caching, parallel processing |
| BOM Calculation | < 1s | Pre-computed lookup tables |
| Page Load | < 1.5s | Code splitting, lazy loading |
| Message History | < 500ms | Pagination, virtual scrolling |

### Security

- **Input Sanitization**: All user inputs validated and sanitized
- **Rate Limiting**: Prevent abuse of calculation endpoints
- **Authentication**: JWT tokens for user sessions
- **HTTPS Only**: All communications encrypted
- **XSS Prevention**: Output encoding, CSP headers
- **CSRF Protection**: Token-based validation

---

## Future Enhancements

### Phase 1: Enhanced Interactivity
- [ ] Real-time typing indicators
- [ ] Message read receipts
- [ ] Inline editing of quotation parameters
- [ ] Drag-and-drop file upload for specs

### Phase 2: Advanced Features
- [ ] 3D panel visualization
- [ ] Augmented reality preview (mobile)
- [ ] Interactive installation guides
- [ ] Customer portal with order tracking

### Phase 3: Multi-Channel Support
- [ ] WhatsApp Business integration
- [ ] Email quotation requests
- [ ] SMS notifications
- [ ] Voice interface (Spanish voice commands)

### Phase 4: Analytics Dashboard
- [ ] Usage statistics
- [ ] Popular products tracking
- [ ] Conversion funnel analysis
- [ ] Customer satisfaction metrics

---

## References

### Related Documentation
- [Knowledge Base Guide](../PANELIN_KNOWLEDGE_BASE_GUIDE.md)
- [API Reference](./API_REFERENCE.md)
- [Security Implementation](./SECURITY_IMPLEMENTATION_GUIDE.md)
- [Configuration Guide](./CONFIGURATION.md)

### Design Resources
- BMC Uruguay Brand Guidelines (internal)
- Material Design for Conversational UI
- WCAG 2.1 Guidelines

### Code Locations
- PDF Generation: `/panelin_reports/pdf_generator.py`
- Quotation Calculator: `/panelin/tools/quotation_calculator.py`
- Agent State: `/panelin_hybrid_agent/agent/state_manager.py`
- Backend API: `/panelin_backend/main.py`

---

**Document Maintained By:** @matiasportugau-ui  
**Last Review:** 2026-02-18  
**Next Review:** 2026-05-18
