# Getting Started

## Prerequisites
- Python 3.8+ (used by most automation and training scripts)
- Node.js 18+ (for the Agents SDK TypeScript project)
- API keys as needed:
  - OPENAI_API_KEY (required for most workflows)
  - ANTHROPIC_API_KEY (optional, for Claude)
  - GOOGLE_API_KEY (optional, for Gemini)

## Repository setup
1. Ensure the knowledge base files exist in `Files/`.
2. Create a `.env` file in the repo root or export environment variables.

Example `.env`:
```
OPENAI_API_KEY=your-key
OPENAI_ASSISTANT_ID=asst_optional_id
ANTHROPIC_API_KEY=your-optional-key
GOOGLE_API_KEY=your-optional-key
```

## Install dependencies
Python (root utilities):
```bash
pip install -r requirements.txt
```

Python (subprojects as needed):
```bash
pip install -r gpt_kb_config_agent/requirements.txt
```
For GPT Simulation Agent dependencies, follow gpt_simulation_agent/README.md.

Node (Agents SDK):
```bash
npm install
```

## Quick validation commands
Knowledge base analysis:
```bash
python -m gpt_kb_config_agent.main analyze --kb-path "Files/"
```

KB update status:
```bash
python kb_update_optimizer.py --stats
python training_data_optimizer.py --stats
```

Agents SDK smoke test:
```bash
ts-node panelin_agents_sdk_example.ts
```

## Optional: create Panelin via API
Use the API-based setup script if you want explicit model selection:
```bash
python setup_panelin_with_model.py --model gpt-4o
```
This script stores the assistant id in `.panelin_assistant_id`.

## Next steps
- [Panelin GPT Configuration](Panelin-GPT-Configuration)
- [Knowledge Base](Knowledge-Base)
- [KB Update and Training](KB-Update-and-Training)
- [Agents and SDK](Agents-and-SDK)
