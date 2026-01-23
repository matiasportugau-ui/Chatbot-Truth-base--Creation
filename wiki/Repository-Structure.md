# Repository Structure

This repo contains multiple systems that work together. The most important
directories and entry points are listed below.

## Top-level directories
- `Files/`: Knowledge base assets (JSON, CSV, RTF, Markdown).
- `gpt_kb_config_agent/`: KB analysis, validation, and GPT config generation.
- `kb_training_system/`: Multi-level training and evaluation pipeline.
- `gpt_simulation_agent/`: Self-configuring agent, ingestion, analytics, Gems.
- `ai-project-files-organizer-agent/`: Project file organization utilities.
- `panelin_improvements/`: Source of truth validators and improvements.
- `gpt_configs/`: Generated GPT configuration output files.
- `training_data/`: Training datasets (interactions, quotes, patterns).
- `ingestion_analysis_output/`: Output artifacts from ingestion analysis.
- `node_modules/`: Node dependencies for the Agents SDK.

## Core scripts and entry points
- `motor_cotizacion_panelin.py`: Quotation engine used by agents.
- `orquestador_multi_modelo.py`: Multi-model orchestration helpers.
- `kb_update_optimizer.py`: KB update orchestration.
- `training_data_optimizer.py`: Training data optimization pipeline.
- `kb_auto_scheduler.py`: Scheduler for automated updates.
- `setup_panelin_with_model.py`: API-based Panelin assistant setup.
- `setup_claude_agent.py`: Claude setup utilities.
- `setup_gemini_agent.py`: Gemini setup utilities.
- `setup_build_ai_apps_agent.py`: Build AI Apps agent setup.
- `setup_kb_update_system.sh`: One-shot setup for the KB update system.

## Agents SDK (TypeScript)
- `panelin_agents_sdk.ts`: OpenAI Agents SDK implementation.
- `panelin_agents_sdk_example.ts`: Example usage.
- `package.json`, `tsconfig.json`: Node project config.

## Key documentation files
- `PANELIN_FULL_CONFIGURATION.md`
- `PANELIN_INSTRUCTIONS_FINAL.txt`
- `KB_UPDATE_QUICKSTART.md`
- `KB_UPDATE_TRAINING_STRATEGY.md`
- `KB_TRAINING_SYSTEM_SUMMARY.md`
- `PANELIN_AGENTS_SDK_README.md`
