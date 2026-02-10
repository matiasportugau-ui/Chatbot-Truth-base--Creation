# GPT Configurations — Version Management

This directory contains versioned GPT configuration snapshots for the Panelin chatbot system. Each version folder preserves a complete set of GPT system instructions and configuration files.

## Directory Structure

```
gpt_configs/
├── PanelinV3.2/              # Archived: BOM + Autoportancia (pre-PDF)
│   ├── VERSION.md
│   ├── INSTRUCCIONES_PANELIN_V3.2_ACTUAL.txt  ← Actual V3.2 instructions (11 sections)
│   ├── Panelin_Asistente_Integral_BMC_config*.json
│   ├── KB_Indexing_Expert_Agent_config.json
│   ├── Panelin Knowledge Base Assistant_config.json
│   ├── INSTRUCCIONES_PANELIN*.txt (6 legacy variants)
│   ├── kb_analysis_report.json
│   └── validation_fix_report.json
│
├── PanelinV3.3/              # Current: BOM + Autoportancia + PDF Profesional
│   ├── VERSION.md
│   ├── Panelin_GPT_config.json              ← Full config JSON
│   ├── INSTRUCCIONES_PANELIN_V3.3.txt       ← Copy-paste ready (12 sections)
│   └── instructions/
│       ├── GPT_PDF_INSTRUCTIONS.md           ← PDF workflow (v2.1)
│       ├── GPT_INSTRUCTIONS_PRICING.md
│       ├── GPT_OPTIMIZATION_ANALYSIS.md
│       ├── PANELIN_KNOWLEDGE_BASE_GUIDE.md
│       ├── PANELIN_QUOTATION_PROCESS.md
│       └── PANELIN_TRAINING_GUIDE.md
│
└── (legacy files at root level — pre-versioning)
```

## Version History

| Version | Date | Sections | Key Features |
|---------|------|----------|--------------|
| **V3.2** | 2026-02-07 | 11 | BOM Completa, Autoportancia V3.1, 4 KB levels, `/cotizar`, `/autoportancia` |
| **V3.3** | 2026-02-10 | 12 | + PDF Profesional (branding BMC, `/pdf`, unit_base, pre-validation), expanded KB to 8 levels |

## How to Use

### Uploading to GPT

1. Navigate to the **latest version folder** (currently `PanelinV3.3/`)
2. Read the `VERSION.md` for upload instructions
3. Copy content from `INSTRUCCIONES_PANELIN_V3.3.txt` into GPT system prompt
4. Upload all KB files listed in `deployment.files_to_upload` from `Panelin_GPT_config.json`
5. Upload `Logo_BMC- PNG.png` for PDF header
6. Enable capabilities: Code Interpreter (critical), Canvas, Web Browsing, Image Generation

### Creating a New Version

When making significant changes to GPT configuration:

1. Create a new folder: `PanelinV3.X/`
2. Copy files from the previous version
3. Apply modifications
4. Create `INSTRUCCIONES_PANELIN_V3.X.txt` (copy-paste ready)
5. Create `Panelin_GPT_config.json` (full config with metadata)
6. Create a `VERSION.md` documenting changes from previous version
7. Update this README with the new version entry

### Reverting to a Previous Version

Each version folder is self-contained. To revert:

1. Navigate to the desired version folder
2. Follow the upload instructions in its `VERSION.md`

## Naming Convention

- **Folder**: `PanelinV{major}.{minor}/`
- **Major version**: Significant architecture changes
- **Minor version**: Feature additions or improvements
