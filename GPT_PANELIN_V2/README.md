GPT_PANELIN_V2

- Purpose: single-source package for Panelin GPT (upload, instructions, KB, configs, docs, deployment).
- Status: scaffolded. Populate each folder with the chosen canonical files (no duplicates).
- Source mapping: see per-folder READMEs for where to pull the canonical versions from the current workspace.

Folder map

- 01_UPLOAD: assets/scripts required for GPT upload (logo, PDF generator, styles).
- 02_INSTRUCTIONS: one canonical system/instructions set for the GPT + any optimized variants you decide to keep.
- 03_KNOWLEDGE_BASE: KB JSON files, ledger, and manifest.
- 04_CONFIGURATIONS: GPT config JSONs (only the canonical set).
- 05_DOCUMENTATION: quick start, policies, maintenance, security, test plan, changelog.
- 06_DEPLOYMENT: single deployment checklist + status.

Population order (suggested)

1) Copy/upload assets into 01_UPLOAD.
2) Select and place the single canonical instructions into 02_INSTRUCTIONS; archive other variants separately if needed.
3) Move KB JSON + ledger + manifest into 03_KNOWLEDGE_BASE.
4) Move only the canonical GPT config JSONs into 04_CONFIGURATIONS.
5) Centralize docs into 05_DOCUMENTATION (link out to wiki/agents rather than duplicating).
6) Keep one deployment checklist and status in 06_DEPLOYMENT.

Notes

- If a file is ambiguous, place it in an ARCHIVE/ folder (per subfolder) instead of duplicating.
- Keep changelog/version info in 05_DOCUMENTATION to track updates.
