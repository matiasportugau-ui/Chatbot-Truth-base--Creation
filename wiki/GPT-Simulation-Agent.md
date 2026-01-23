# GPT Simulation Agent

## Overview
The GPT Simulation Agent is a self-configuring system that scans the workspace,
extracts requirements, and generates structured outputs for training and Gem
generation.

## Core features
- Self-diagnosis of workspace configuration
- Extraction from JSON, Markdown, and YAML files
- Gap analysis and extraction guides
- Social media ingestion (Facebook, Instagram)
- Analytics and training data processing
- Google Labs Gem generation

## Quick start
```bash
pip install -r requirements.txt
# See gpt_simulation_agent/README.md for any extra dependencies.
python gpt_simulation_agent/example_usage.py
```

## Basic usage
```python
from agent_system.gpt_simulation_agent import GPTSimulationAgent

agent = GPTSimulationAgent(workspace_path=".")
config = agent.configure()
agent.ingest_social_media(platforms=["facebook", "instagram"])
results = agent.process_training_data()
analytics = agent.generate_analytics()
gems = agent.generate_gems(generate_multiple=True)
```

## Outputs
- `gpt_simulation_agent/output/`: generated configurations and reports
- `gpt_simulation_agent/training_data/`: local training data

## References
- gpt_simulation_agent/README.md
- gpt_simulation_agent/QUICKSTART.md
- gpt_simulation_agent/USAGE.md
