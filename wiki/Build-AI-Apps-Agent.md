# Build AI Apps Agent

## Overview
The Build AI Apps agent is a specialist for designing AI mini-apps and
workflows that can be exported as Google Labs Gems (Opal). It supports multiple
LLM platforms and provides validation and optimization.

## Key capabilities
- Workflow design from natural language descriptions
- Validation and optimization of workflows
- Templates and remixing
- Export formats: JSON, Markdown, Gem description
- Multi-platform compatibility (OpenAI, Claude, Gemini)

## Quick start
Install dependencies:
```bash
pip install openai anthropic google-generativeai
```

Run setup:
```bash
python setup_build_ai_apps_agent.py
```

Basic usage:
- Import the helpers from `agente_build_ai_apps.py`.
- Call the workflow design and export helpers as documented in
  `GUIA_BUILD_AI_APPS.md`.

## Workflow types
- automation
- research
- content
- data_processing
- analysis
- custom

## References
- GUIA_BUILD_AI_APPS.md
- GEMS_READY_FOR_GOOGLE_LABS.pdf
