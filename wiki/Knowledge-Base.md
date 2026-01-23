# Knowledge Base

## Overview
The knowledge base (KB) is organized into a strict hierarchy to protect pricing
accuracy and prevent conflicting data from leaking into responses. The system
always prioritizes the Master level for prices and formulas.

## Levels
| Level | Purpose | Typical files | Usage priority |
|------:|---------|---------------|----------------|
| 1 | Master source of truth | `BMC_Base_Conocimiento_GPT-2.json` | Highest |
| 2 | Validation | `BMC_Base_Unificada_v4.json` | Cross-check only |
| 3 | Dynamic | `panelin_truth_bmcuruguay_web_only_v2.json` | Verify changes |
| 4 | Support | `panelin_context_consolidacion_sin_backend.md`, CSV, RTF | Context only |

## Required files (core setup)
These are required to configure Panelin correctly:
- `BMC_Base_Conocimiento_GPT-2.json` (Level 1 Master)
- `PANELIN_KNOWLEDGE_BASE_GUIDE.md`
- `PANELIN_QUOTATION_PROCESS.md`
- `PANELIN_TRAINING_GUIDE.md`
- `panelin_context_consolidacion_sin_backend.md`

Recommended additions:
- `BMC_Base_Unificada_v4.json` (Level 2 validation)
- `panelin_truth_bmcuruguay_web_only_v2.json` (Level 3 dynamic)

## Usage rules (source of truth)
1. Always consult Level 1 for pricing and formulas.
2. Do not invent prices or compute them from cost x margin.
3. If data is missing, respond with "No tengo esa informacion en mi base de
   conocimiento".
4. If conflict exists, use Level 1 and report the discrepancy.

## Sensitive data
Some files contain internal cost information and must not be uploaded to public
GPTs. Examples:
- `BROMYROS_Base_Costos_Precios_2026.json`

See [Security and Data Handling](Security-and-Data-Handling) for guidance.

## References
- PANELIN_FULL_CONFIGURATION.md
- PANELIN_INSTRUCTIONS_FINAL.txt
- GUIA_BASE_CONOCIMIENTO_COSTOS.md
