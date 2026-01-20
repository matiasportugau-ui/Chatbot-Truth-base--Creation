# GPT Simulation Agent

An intelligent AI simulation agent that self-configures by gathering its own requirements, automatically extracting information from available sources, and processing training data from multiple platforms.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run example
python example_usage.py
```

## Features

- 🔍 **Self-Diagnosis**: Automatically scans workspace and identifies configuration needs
- 📥 **Intelligent Extraction**: Extracts from JSON, Markdown, YAML files
- 🔎 **Gap Analysis**: Identifies missing information and generates extraction guides
- 📱 **Social Media Ingestion**: Connects to Facebook & Instagram APIs
- 📊 **Analytics**: Processes training data and generates insights
- 🚀 **Gem Generation**: Automatically generates Google Labs Gems from extracted configurations

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 3-step setup guide
- **[USAGE.md](USAGE.md)** - Complete usage documentation
- **[GEM_GENERATION.md](GEM_GENERATION.md)** - Generate Google Labs Gems from configurations
- **[../TROUBLESHOOTING_MODEL_SELECTION.md](../TROUBLESHOOTING_MODEL_SELECTION.md)** - Troubleshooting model selection issues in GPT Builder

## Project Structure

```
gpt_simulation_agent/
├── agent_system/    ules
│   ├── gpt_simulation_agent.py      # Main orchestrator
│   ├── agent_self_diagnosis.py       # Self-diagnosis
│   ├── agent_extraction.py           # Extraction
│   ├── agent_gap_analysis.py         # Gap analysis
│   ├── agent_social_ingestion.ping_processor.py   # Training data
│   └── utils/                        # Utilities
├── output/               # Generated outputs
├── training_data/         # Training data storage
└── example_usage.py      # Example script
```

## Basic Usage

```python
from agent_system.gpt_simulation_agent import GPTSimulationAgent

# Initialize
agent = GPTSimulationAgent(workspace_path=".")

# Self-configure
config = agent.configure()

# Ingest social media (optional)
agent.ingest_social_media(platforms=['facebook', 'instagram'])

# Process training data
results = agent.process_training_data()
analytics = agent.generate_analytics()

# Generate Google Labs Gems
gems = agent.generate_gems(generate_multiple=True)
```

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## License

[Your License Here]
