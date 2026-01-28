# Panelin_GPT - GPT Upload Package

**BMC Uruguay - Panelin Asistente Integral**
**Version**: 2.0
**Date**: 2026-01-28
**Status**: Production Ready

---

## Overview

This folder contains all organized and uploadable files for configuring and deploying the **Panelin - BMC Assistant GPT**. The GPT generates professional quotations for BMC Uruguay's construction panels and accessories.

---

## Folder Structure

```
Panelin_GPT/
├── 01_UPLOAD_FILES/        # Files to upload directly to GPT
├── 02_INSTRUCTIONS/        # GPT Instructions (copy to editor)
├── 03_KNOWLEDGE_BASE/      # Knowledge files for GPT
├── 04_CONFIGURATIONS/      # GPT configuration JSONs
├── 05_DOCUMENTATION/       # Reference documentation
└── 06_DEPLOYMENT/          # Deployment guides & checklists
```

---

## Quick Start Upload Checklist

### Step 1: Upload Core Files to GPT Editor

Navigate to **GPT Editor > Configure > Files** and upload:

| File | Location | Purpose |
|------|----------|---------|
| `pdf_generator.py` | `01_UPLOAD_FILES/` | PDF generation engine |
| `pdf_styles.py` | `01_UPLOAD_FILES/` | BMC branding & styles |
| `bmc_logo.png` | `01_UPLOAD_FILES/` | BMC logo asset |

### Step 2: Copy Instructions to GPT

Navigate to **GPT Editor > Configure > Instructions** and paste content from:

| File | Purpose |
|------|---------|
| `02_INSTRUCTIONS/GPT_PDF_INSTRUCTIONS.md` | PDF integration instructions |
| `02_INSTRUCTIONS/INSTRUCCIONES_PANELIN_OPTIMIZADAS.txt` | Spanish system instructions |

### Step 3: Upload Knowledge Base Files

Navigate to **GPT Editor > Configure > Knowledge** and upload:

| File | Purpose |
|------|---------|
| `03_KNOWLEDGE_BASE/panelin_truth_bmcuruguay.json` | Main truth base |
| `03_KNOWLEDGE_BASE/product_catalog.json` | Product catalog with pricing |
| `03_KNOWLEDGE_BASE/LEDGER_CHECKPOINT.md` | Critical business rules |

### Step 4: Verify Configuration

Review settings against:
- `04_CONFIGURATIONS/Panelin_Asistente_config.json`

---

## Folder Contents Detail

### 01_UPLOAD_FILES/ (Direct Upload)

Files that must be uploaded directly to GPT:

- **pdf_generator.py** - Core PDF generation using ReportLab
- **pdf_styles.py** - BMC branding, colors, terms & conditions
- **bmc_logo.png** - Official BMC Uruguay logo (48 KB)

### 02_INSTRUCTIONS/ (Copy to Instructions Field)

GPT instruction files:

- **GPT_PDF_INSTRUCTIONS.md** - Technical instructions for PDF generation
- **INSTRUCCIONES_PANELIN_OPTIMIZADAS.txt** - Optimized Spanish instructions (8000 chars)
- **SYSTEM_INSTRUCTIONS_CANONICAL.md** - Official canonical system prompt

### 03_KNOWLEDGE_BASE/ (Knowledge Files)

Knowledge base files for GPT:

- **panelin_truth_bmcuruguay.json** - Main truth base with company info
- **product_catalog.json** - GPT-optimized product catalog with pricing
- **LEDGER_CHECKPOINT.md** - Critical calculation rules & business logic

### 04_CONFIGURATIONS/ (Reference Configs)

GPT configuration files for reference:

- **Panelin_Asistente_config.json** - Main GPT configuration
- **KB_Indexing_Expert_Agent_config.json** - KB indexing agent config

### 05_DOCUMENTATION/ (Reference Docs)

Supporting documentation:

- **QUICK_START.md** - Quick start guide for developers
- **CAPABILITIES_POLICY.md** - Feature capabilities & limitations
- **SECURITY_POLICY.md** - Security guidelines
- **MAINTENANCE.md** - Maintenance procedures

### 06_DEPLOYMENT/ (Deployment Guides)

Deployment checklists and status:

- **DEPLOYMENT_CHECKLIST.md** - Step-by-step deployment guide
- **FINAL_STATUS.txt** - Current deployment status

---

## Critical Business Rules (LEDGER CHECKPOINT)

### Calculation Logic by `unit_base`

| unit_base | Formula | Example |
|-----------|---------|---------|
| `unidad` | quantity x sale_sin_iva | 4 units x $20.77 = $83.08 |
| `ml` | quantity x Length_m x sale_sin_iva | 15 pcs x 3.0m x $3.90 = $175.50 |
| `m2` | area_total x sale_sin_iva | 180 m2 x $36.54 = $6,577.20 |

### Key Constants

- **IVA Rate**: 22% (Uruguay 2026)
- **Standard Shipping**: $280 USD
- **Primary Color**: #003366 (BMC Blue)

### CRITICAL FIX - SKU 6842 (Gotero Lateral 100mm)

- `unit_base = "unidad"` (NOT "ml")
- `Length_m = 3.00` is informational only
- **Correct**: 4 x $20.77 = $83.08
- **WRONG**: 4 x 3.0 x $20.77 = $249.24

---

## Company Information

- **Company**: Metalog SAS (BMC Uruguay)
- **Email**: info@bmcuruguay.com.uy
- **Phone**: 42224031
- **Website**: www.bmcuruguay.com.uy
- **Location**: Maldonado, Uruguay
- **Bank**: BROU Caja de Ahorro - 110520638-00002

---

## Testing

After uploading, test with this prompt:

```
Genera una cotizacion PDF para:
- Cliente: Juan Perez
- 180 m2 de Isopanel 50mm
- 15 unidades de Perfil Omega 35x12x3000mm
- 4 unidades de Gotero Lateral 100mm x 3m
```

Expected behavior:
1. GPT calculates totals using correct formulas
2. PDF generated with BMC branding
3. All prices include IVA 22%
4. Shipping $280 USD added

---

## Support

For issues or updates:
- Review `05_DOCUMENTATION/MAINTENANCE.md`
- Check `06_DEPLOYMENT/FINAL_STATUS.txt` for current status
- Refer to `03_KNOWLEDGE_BASE/LEDGER_CHECKPOINT.md` for calculation rules
