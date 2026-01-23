# Panelin GPT Configuration

This page summarizes the full configuration steps for Panelin in GPT Builder
and via the API.

## GPT Builder setup
1. Open the GPT Builder: https://chatgpt.com/gpts/editor
2. Name: "Panelin - BMC Assistant Pro"
3. Description: use the text in `PANELIN_FULL_CONFIGURATION.md`
4. Conversation starters: use the examples in `PANELIN_FULL_CONFIGURATION.md`

## System instructions
Copy the entire content of `PANELIN_INSTRUCTIONS_FINAL.txt` into the
"Instructions" field. Do not edit or truncate.

## Knowledge base upload order
Required first (Level 1):
- `BMC_Base_Conocimiento_GPT-2.json`

Required supporting files:
- `PANELIN_KNOWLEDGE_BASE_GUIDE.md`
- `PANELIN_QUOTATION_PROCESS.md`
- `PANELIN_TRAINING_GUIDE.md`
- `panelin_context_consolidacion_sin_backend.md`

Recommended:
- `BMC_Base_Unificada_v4.json`
- `panelin_truth_bmcuruguay_web_only_v2.json`

## Model and capabilities
- Model: GPT-4 or GPT-4 Turbo (recommended)
- Capabilities:
  - Code Interpreter: required
  - Web Browsing: recommended

## Verification tests
Use the test prompts in `PANELIN_FULL_CONFIGURATION.md`:
- Personalization (name-based responses)
- Source of truth pricing
- Autoportancia validation
- Full quotation flow
- SOP commands (/estado, /checkpoint)
- Energy analysis comparisons

## API-based setup (optional)
To specify a model via API:
```bash
python setup_panelin_with_model.py --model gpt-4o
```
The assistant id is stored in `.panelin_assistant_id`.

## References
- PANELIN_FULL_CONFIGURATION.md
- PANELIN_INSTRUCTIONS_FINAL.txt
- PANELIN_QUOTATION_PROCESS.md
- PANELIN_TRAINING_GUIDE.md
- SETUP_PANELIN_API.md
