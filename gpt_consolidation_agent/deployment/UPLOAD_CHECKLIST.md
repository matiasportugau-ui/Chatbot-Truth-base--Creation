# PANELIN v2.0 - Deployment Upload Checklist

Follow this checklist strictly to ensure a successful update of the Panelin GPT.

## Phase 1: Pre-Upload Verification

- [ ] **File Consistency**: Run `python3 verify_gpt_configuration.py` to ensure all JSON files are valid.
- [ ] **KB Size Check**: Verify that the total size of files in `knowledge_base/` is under 512MB (current total is ~15MB).
- [ ] **IVA Check**: Ensure `BMC_Base_Conocimiento_GPT-2.json` contains the updated "IVA ya incluido" rule.
- [ ] **Instructions Sync**: Verify that `instructions.md` in the deployment folder matches the canonical v2.2 instructions.

## Phase 2: GPT Builder Update

- [ ] **Step 1: Instructions**: Replace the existing instructions with the content of `instructions.md`.
- [ ] **Step 2: Knowledge Base**: 
    - [ ] Delete all old files from the "Knowledge" section.
    - [ ] Upload the 13 files listed in `GPT_BUILDER_CONFIG.md`.
    - [ ] Wait for all files to show "Processed" status.
- [ ] **Step 3: Capabilities**: Ensure Code Interpreter, Canvas, Web Browsing, and DALL-E are active.
- [ ] **Step 4: Starters**: Update the 6 conversation starters.

## Phase 3: Post-Upload Testing (Sandbox)

- [ ] **Greeting Test**: Say "Hola". 
    - *Expected*: Identity as Panelin, asks for name, professional tone.
- [ ] **Identity Test**: Say "Mi nombre es Mauro".
    - *Expected*: Personalized "rarito" response + offer help.
- [ ] **Pricing Test**: Ask "Costo de IAGRO30?".
    - *Expected*: Correct price from Optimized JSON, mentions IVA included.
- [ ] **PDF Test**: Say "Genera un PDF para Juan Perez, obra en Montevideo, 50m2 de Isoroof 30mm".
    - *Expected*: Executes Code Interpreter, uses `panelin_reports`, generates downloadable PDF.
- [ ] **Policy Test**: Ask "Pueden recomendarme un instalador?".
    - *Expected*: Strict refusal, derivation to BMC sales agents only.
- [ ] **Technical Test**: Ask about "Ángulo Aluminio" or "Tortugas PVC".
    - *Expected*: Correct technical description and v6.0 rule usage.

## Phase 4: Finalization

- [ ] **Save/Publish**: Click "Update" -> "Publish to Everyone" (or "Only People with link").
- [ ] **Version Log**: Note the deployment timestamp and version (v2.0) in the internal changelog.

---
**Verification Date**: 2026-01-28
**Verified By**: AI Engineering Agent
