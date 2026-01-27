# Panelin GPT Deployment Package
Generated: 20260127_052513

## Contents

### 1. Instructions
- `instructions.md`: The canonical system prompt for the GPT. Copy this into the "Instructions" field of the GPT Builder.

### 2. Knowledge Base (`knowledge_base/`)
Upload these files to the "Knowledge" section of the GPT Builder.
- **Level 1 (Master)**: `BMC_Base_Conocimiento_GPT-2.json`
- **Level 2 (Validation)**: `BMC_Base_Unificada_v4.json`
- **Level 3 (Dynamic)**: `panelin_truth_bmcuruguay_web_only_v2.json`
- **Support Files**: Guides, contexts, and indexes.

### 3. Configuration (`config/`)
- `gpt_config.json`: The JSON representation of the GPT's settings, capabilities, and actions.

### 4. Actions (`actions/`)
- Scripts that define logic or can be uploaded for Code Interpreter use.

## Deployment Steps
1. Go to GPT Builder.
2. Name: **Panelin - BMC Assistant Pro**
3. Copy content from `instructions.md`.
4. Upload all files from `knowledge_base/`.
5. Enable "Code Interpreter" and "Canvas".
6. Disable "Web Browsing" (unless strictly necessary, per instructions).
