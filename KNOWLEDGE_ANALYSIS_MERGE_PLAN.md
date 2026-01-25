# Knowledge Analysis and Merge Plan

## Scope
This document summarizes the current knowledge analysis findings and proposes
a concrete merge (consolidation) plan for the Panelin knowledge base.

## Sources reviewed
- TRUTH_BASE_STRUCTURE_ANALYSIS.md
- gpt_configs/kb_analysis_report.json
- PROMPT_ANALISIS_CONOCIMIENTO_GPT.md
- ANALISIS_UN_ARCHIVO_VS_MULTIPLES.md
- KB_UPDATE_TRAINING_STRATEGY.md
- panelin_context_consolidacion_sin_backend.md
- scripts/consolidar_kb_v5.py

## Current KB inventory (workspace)
Located under the directory named `Files ` (note the trailing space):
- Level 2 (validation): `Files /BMC_Base_Unificada_v4.json`
- Level 3 (dynamic): `Files /panelin_truth_bmcuruguay_web_only_v2.json`
- Support: `Files /Aleros -2.rtf`
- Support: `Files /panelin_truth_bmcuruguay_catalog_v2_index.csv`

Missing (critical):
- Level 1 (master): `BMC_Base_Conocimiento_GPT.json`
- Level 1 (master): `BMC_Base_Conocimiento_GPT-2.json`

## Key findings (from analysis)
1. The 4-level hierarchy is well defined, but Level 1 master files are missing
   in the current workspace. This blocks any reliable consolidation.
2. The current setup risks duplication and conflict across Level 2 and Level 3.
3. Prior analysis recommends a single consolidated JSON for data (products,
   prices, formulas, specs) while keeping documentation and technical rules
   as separate files.
4. A consolidation script already exists: `scripts/consolidar_kb_v5.py`.
   It merges Level 1/2/3 with Level 3 prices taking precedence when newer.

## Merge decision
Consolidate DATA into one JSON file (v5) while keeping documentation and
technical rules separate.

Rationale:
- Avoids conflicting data across files.
- Simplifies instructions and reduces context cost.
- Matches prior recommendations and existing tooling.

## Merge plan

### Phase 0 - Restore Level 1 (Blocker)
Goal: get the authoritative master file before merging.

Actions:
1. Locate `BMC_Base_Conocimiento_GPT.json` or `BMC_Base_Conocimiento_GPT-2.json`
   from backups or upstream sources.
2. Confirm the file contains:
   - Products with full specs
   - Formulas (cotizacion and ahorro energetico)
   - Business rules (IVA, pendiente, etc.)
3. Place the Level 1 file under `Files ` so the consolidator can read it.

Exit criteria:
- Level 1 file exists and passes JSON validation.

### Phase 1 - Pre-merge checks
1. Normalize product identifiers across Level 1/2/3.
2. Confirm precedence rules:
   - Level 1 is authoritative for formulas and specs.
   - Level 2 adds validation notes.
   - Level 3 provides most recent pricing (if date is newer).
3. Confirm date fields exist to compare recency (or force Level 3 for prices).

### Phase 2 - Execute consolidation
Use the existing script:

```
python scripts/consolidar_kb_v5.py \
  --base-path "Files " \
  --output "BMC_Base_Conocimiento_CONSOLIDADA_v5.0_YYYYMMDD.json"
```

Expected outputs:
- Consolidated JSON file (single source of truth)
- REPORTE_CONSOLIDACION_KB_v5.0.txt (summary report)

### Phase 3 - Validate and audit
1. Review the generated report for missing prices or formulas.
2. Run spot checks:
   - Pick 3-5 products and verify prices and specs match Level 1/3 sources.
3. Confirm formulas exist and are complete (9 formulas expected).

### Phase 4 - Update GPT knowledge configuration
1. Remove old JSON files from GPT builder:
   - BMC_Base_Conocimiento_GPT-2.json
   - BMC_Base_Unificada_v4.json
   - panelin_truth_bmcuruguay_web_only_v2.json
2. Upload the consolidated JSON only.
3. Keep documentation and technical rule files:
   - panelin_context_consolidacion_sin_backend.md
   - Aleros -2.rtf
   - panelin_truth_bmcuruguay_catalog_v2_index.csv
4. Simplify instructions to a single source of truth.

### Phase 5 - Update maintenance workflow
1. Update any automation to target the consolidated JSON (not multi-level).
2. Adopt versioned filenames for every update.
3. Keep a rollback archive of prior versions.

## Risks and mitigations
- Risk: Consolidation without Level 1 causes missing formulas/specs.
  Mitigation: Do not merge until Level 1 is restored.
- Risk: Mismatched product IDs across levels.
  Mitigation: Normalize IDs in Phase 1 before merging.
- Risk: Price recency ambiguity.
  Mitigation: Enforce Level 3 prices only when date is newer.

## Acceptance criteria
- Single JSON file exists and is used as the only data source.
- All required formulas present.
- No missing prices for active products.
- GPT instructions reference only the consolidated file for data.

## Open questions
1. Where is the authoritative Level 1 master file stored?
2. Are there current price conflicts that must be reconciled manually?
3. Should the consolidated file live in `Files ` or a new `kb_versions/` dir?
