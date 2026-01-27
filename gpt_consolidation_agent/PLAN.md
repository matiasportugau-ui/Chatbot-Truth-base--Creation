# GPT Consolidation Agent Plan

This agent is responsible for consolidating the GPT configuration, instructions, files, and actions into a unified package.

## Components

1.  **Source of Truth**:
    -   Instructions: `docs/gpt/PANELIN_SYSTEM_INSTRUCTIONS_CANONICAL.md`
    -   Knowledge Base: `BMC_Base_Conocimiento_GPT-2.json` (Level 1 Master)
    -   Configuration: `gpt_configs/Panelin_Asistente_Integral_BMC_config.json`

2.  **Actions**:
    -   `verify_gpt_configuration.py`: Validates the configuration.
    -   `gpt_kb_config_agent/gpt_config_generator.py`: Generates config.

3.  **Output**:
    -   A consolidated `deployment/` folder containing:
        -   `instructions.md`: The final system prompt.
        -   `knowledge_base/`: Folder with all referenced KB files.
        -   `actions/`: Folder with python scripts for the agent (if applicable to code interpreter).
        -   `config.json`: The GPT configuration file.
    -   `report.md`: A summary of the consolidation process and verification results.

## Steps

1.  Identify all source files.
2.  Run verification (`verify_gpt_configuration.py`).
3.  Create `deployment/` structure.
4.  Copy and normalize files into `deployment/`.
5.  Generate `report.md`.
