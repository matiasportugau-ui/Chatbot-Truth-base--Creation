# GPT Update Checklist - Knowledge Base v6.0

Follow these steps to synchronize your GPT with the latest modifications.

## 📋 Phase 1: File Preparation
- [ ] Locate `BMC_Base_Conocimiento_GPT-2.json` in your project.
- [ ] Locate `COST_MATRIX_ALL_SUPPLIERS_GPT_ANALYZE.json` in `wiki/matriz de costos adaptacion /redesigned/`.
- [ ] Locate `KB_UPDATE_v6.0_INSTRUCTIONS_SNIPPET.txt` in your project root.

## 📂 Phase 2: File Ingestion (GPT Builder)
1. Go to [ChatGPT GPT Builder](https://chat.openai.com/gpts/mine).
2. Select **Configure** tab.
3. Scroll to the **Knowledge** section.
4. **DELETE** the old version of `BMC_Base_Conocimiento_GPT-2.json`.
5. **UPLOAD** the new `BMC_Base_Conocimiento_GPT-2.json` (v6.0).
6. **UPLOAD** the new `COST_MATRIX_ALL_SUPPLIERS_GPT_ANALYZE.json` (if not already there).

## 📝 Phase 3: Instructions Update
1. Open `KB_UPDATE_v6.0_INSTRUCTIONS_SNIPPET.txt`.
2. Copy the entire content.
3. Paste it at the **TOP** of the **Instructions** text box in the GPT Builder.
4. (Optional) Review if old instructions contradict any new rules (e.g., external installers).

## 💾 Phase 4: Save & Publish
1. Click **Update** (top right).
2. Choose **Everyone** (or **Only me** if you want to test before going live).
3. Click **Confirm**.

## 🧪 Phase 5: Verification
- [ ] Run the tests defined in `TEST_PROTOCOL_v6.0.md` to ensure the GPT is following the new logic.

---
*Created on 2026-01-27*
