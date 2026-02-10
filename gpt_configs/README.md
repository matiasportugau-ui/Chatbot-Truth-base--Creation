# GPT Configurations — Version Management

This directory contains versioned GPT configuration snapshots for the Panelin chatbot system. Each version folder preserves a complete set of GPT system instructions and configuration files.

## Directory Structure

```
gpt_configs/
├── PanelinV3.2/              # Archived: Pre-PDF template improvements
│   ├── VERSION.md
│   ├── Panelin_Asistente_Integral_BMC_config.json
│   ├── Panelin_Asistente_Integral_BMC_config_v2.0.json
│   ├── KB_Indexing_Expert_Agent_config.json
│   ├── Panelin Knowledge Base Assistant_config.json
│   ├── INSTRUCCIONES_PANELIN*.txt (6 variants)
│   ├── kb_analysis_report.json
│   └── validation_fix_report.json
│
├── PanelinV3.3/              # Current: Enhanced PDF generation
│   ├── VERSION.md
│   ├── Panelin_GPT_config.json
│   └── instructions/
│       ├── GPT_PDF_INSTRUCTIONS.md
│       ├── GPT_INSTRUCTIONS_PRICING.md
│       ├── GPT_OPTIMIZATION_ANALYSIS.md
│       ├── PANELIN_KNOWLEDGE_BASE_GUIDE.md
│       ├── PANELIN_QUOTATION_PROCESS.md
│       └── PANELIN_TRAINING_GUIDE.md
│
└── (legacy files at root level — pre-versioning)
```

## Version History

| Version | Date | Instructions | Key Features |
|---------|------|-------------|--------------|
| **V3.2** | 2026-02-06 | v2.3 Canonical | Quotations, BOM, Accessories, Shopify Catalog, BROMYROS Pricing |
| **V3.3** | 2026-02-10 | v2.5 Canonical | Enhanced PDF (template v2.1, pre-validation, error handling) |

## How to Use

### Uploading to GPT

1. Navigate to the **latest version folder** (currently `PanelinV3.3/`)
2. Read the `VERSION.md` for upload instructions
3. Copy the `instructions` field from `Panelin_GPT_config.json` into GPT system prompt
4. Upload all files from `instructions/` as knowledge base documents

### Creating a New Version

When making significant changes to GPT configuration:

1. Create a new folder: `PanelinV3.X/`
2. Copy files from the previous version
3. Apply modifications
4. Create a `VERSION.md` documenting changes
5. Update this README with the new version entry

### Reverting to a Previous Version

Each version folder is self-contained. To revert:

1. Navigate to the desired version folder
2. Follow the upload instructions in its `VERSION.md`

## Naming Convention

- **Folder**: `PanelinV{major}.{minor}/`
- **Major version**: Significant architecture changes
- **Minor version**: Feature additions or improvements
