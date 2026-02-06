# GPT Configuration Review — Panelin / BMC Assistant Pro

**Date**: 2026-02-06
**Reviewer**: Claude (automated review)
**Scope**: All GPT config files, Python SDK settings, environment config

---

## Configs Reviewed

| File | Version | KB Version | Role |
|------|---------|------------|------|
| `gpt_configs/Panelin_Asistente_Integral_BMC_config_v2.0.json` | 2.3 Canonical | 7.0 | Latest (primary) |
| `Panelin_GPT/04_CONFIGURATIONS/Panelin_Asistente_config.json` | 2.2 Canonical | 6.0 | Deployment package |
| `gpt_configs/Panelin_Asistente_Integral_BMC_config.json` | 1.0.0 | N/A | Legacy |
| `gpt_configs/KB_Indexing_Expert_Agent_config.json` | 1.0.0 | 4-level | Specialist agent |
| `panelin/config/settings.py` | 2.0.0 | N/A | Python SDK |

---

## Critical Issues

### 1. Version Drift Between Configs (HIGH)

The deployment config (`Panelin_GPT/04_CONFIGURATIONS/`) is on KB v6.0 while the primary config is on KB v7.0.

**Impact**:
- `accessories_catalog.json` and `bom_rules.json` missing from deployment upload list
- v7.0 features (parametric BOM, 70+ accessories, unified autoportancia, multi-supplier pricing) not in deployed GPT
- v2.2 deployment instructions don't reference these files at all

**Action**: Sync the deployment config to v2.3 / KB 7.0, or retire the duplicate file.

### 2. Legacy v1.0 Config Still Present (MEDIUM)

`gpt_configs/Panelin_Asistente_Integral_BMC_config.json` is a v1.0 config with no pricing sub-levels (1.5, 1.6), no BROMYROS integration, no PDF generation, no accessories.

**Action**: Archive or delete to avoid confusion.

### 3. KB Indexing Agent Outdated (MEDIUM)

`KB_Indexing_Expert_Agent_config.json` references only the original 4-level hierarchy. Uses `gpt-4` model. No awareness of BROMYROS, accessories, or BOM.

**Action**: Update to reflect current 7-sub-level hierarchy and current model.

---

## Instruction Quality Issues

### 4. Instruction Token Count (HIGH)

The v2.3 instructions field is ~4,000+ words. This causes:
- Increased latency per turn
- Middle-section instruction following degradation
- Higher cost per interaction

**Duplicated content found**:
- KB hierarchy described in prose AND in JSON `knowledge_base` object
- Business rules in instructions AND in `business_rules_v6` JSON block
- Product catalog and audio policy stated twice each
- Guardrails repeat rules already in other sections
- IVA rule appears 6 times

**Action**: Offload reference material to KB files. Keep instructions behavioral, not informational.

### 5. Personality Hardcoding (LOW-MEDIUM)

- No fallback greeting for unrecognized names
- "Never say you're an AI" may conflict with OpenAI usage policies

**Action**: Add generic fallback. Review identity masking policy.

---

## Python SDK Issues

### 6. Model/Token Config (MEDIUM)

`settings.py`:
- `max_tokens: 2000` — too low for full BOM quotations with accessories
- `temperature: 0.0` — correct for extraction, too rigid for consultative persona

**Action**: Increase `max_tokens` to 4000+. Consider `temperature: 0.1-0.2` for conversational agent.

### 7. Shopify API Version Stale (LOW)

`api_version: "2024-01"` is over 2 years old. Shopify deprecates after ~12 months.

**Action**: Update to current version (2025-10+).

---

## Architecture Observations

### 8. File Upload Bloat (LOW-MEDIUM)

17 files uploaded to GPT. Non-operational files in upload list:
- `GPT_OPTIMIZATION_ANALYSIS.md` (analysis, not operational)
- `README.md` (project docs)
- `panelin_context_consolidacion_sin_backend.md` (workflow doc)

**Action**: Only upload files needed at runtime.

### 9. No Graceful Degradation (LOW-MEDIUM)

No behavior defined for:
- Partial matches (product exists, thickness doesn't)
- Stale pricing (Level 3 newer than Level 1)
- KB file access failures

**Action**: Add instructions for partial matches, stale data, and access failures.

### 10. Metadata Version Mismatch (LOW)

| Config | `instructions_version` | `metadata.version` |
|--------|----------------------|-------------------|
| v2.3 config | "2.3 Canonical" | "2.1.0" |
| v2.2 deployment | "2.2 Canonical" | "2.0.0" |

**Action**: Align version numbers.

---

## Security

### 11. `.env.example` Contains Real Identifiers

- `WOLF_API_KEY=mywolfykey123XYZ` — looks like a placeholder but could be confused for real
- `OPENAI_ASSISTANT_ID=asst_7LdhJMasW5HHGZh0cgchTGkX` — real assistant ID exposed

**Action**: Replace with clearly fake placeholders.

---

## Summary — Priority Actions

| # | Priority | Action |
|---|----------|--------|
| 1 | **HIGH** | Sync deployment config to v2.3 / KB 7.0 |
| 2 | **HIGH** | Reduce instruction length (offload to KB files) |
| 3 | **MEDIUM** | Archive/delete legacy v1.0 config |
| 4 | **MEDIUM** | Update KB Indexing Agent to current hierarchy |
| 5 | **MEDIUM** | Increase max_tokens in settings.py to 4000+ |
| 6 | **MEDIUM** | Align metadata.version across configs |
| 7 | **LOW** | Remove non-operational files from upload list |
| 8 | **LOW** | Update Shopify API version |
| 9 | **LOW** | Sanitize .env.example |
| 10 | **LOW** | Add graceful degradation for partial matches |

---

## What's Working Well

- **Hierarchical KB system**: Well-designed priority chain with clear conflict resolution
- **Deterministic temperature (0.0)**: Correct for price/formula extraction
- **Guardrails checklist**: Good pattern for preventing hallucination
- **IVA enforcement**: Repeated enough to ensure compliance (though could be consolidated)
- **Strict derivation policy**: Prevents sending customers to competitors
- **5-phase quotation process**: Well-structured workflow
- **v6.0/v7.0 formula additions**: Good granularity with BOM accessories
