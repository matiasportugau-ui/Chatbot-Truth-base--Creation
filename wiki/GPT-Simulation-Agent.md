# GPT Simulation Agent

The GPT Simulation Agent is a self-configuring AI agent that automatically gathers requirements, extracts information, and processes training data.

---

## Overview

Located in `gpt_simulation_agent/`, this agent provides:
- Self-diagnosis of workspace configuration
- Intelligent extraction from multiple file types
- Gap analysis for missing information
- Social media data ingestion
- Google Labs Gems generation

---

## Architecture

```
gpt_simulation_agent/
├── agent_system/
│   ├── gpt_simulation_agent.py      # Main orchestrator
│   ├── agent_self_diagnosis.py      # Self-diagnosis
│   ├── agent_extraction.py          # Data extraction
│   ├── agent_gap_analysis.py        # Gap analysis
│   ├── agent_social_ingestion.py    # Social media
│   ├── agent_training_processor.py  # Training data
│   ├── agent_gem_generator.py       # Gem generation
│   └── utils/
│       ├── analytics_engine.py
│       ├── facebook_api.py
│       ├── instagram_api.py
│       └── mongodb_client.py
├── output/
├── training_data/
└── example_usage.py
```

---

## Quick Start

```python
from gpt_simulation_agent.agent_system.gpt_simulation_agent import GPTSimulationAgent

# Initialize
agent = GPTSimulationAgent(workspace_path=".")

# Self-configure
config = agent.configure()

# Process training data
results = agent.process_training_data()
analytics = agent.generate_analytics()

# Generate Gems
gems = agent.generate_gems(generate_multiple=True)
```

---

## Components

### 1. Self-Diagnosis

Automatically scans the workspace and identifies configuration needs:

```python
from gpt_simulation_agent.agent_system.agent_self_diagnosis import AgentSelfDiagnosis

diagnosis = AgentSelfDiagnosis(workspace_path=".")
report = diagnosis.run()

print(f"Files found: {report['files_count']}")
print(f"Config files: {report['config_files']}")
print(f"Missing items: {report['missing']}")
```

### 2. Intelligent Extraction

Extracts data from JSON, Markdown, YAML files:

```python
from gpt_simulation_agent.agent_system.agent_extraction import AgentExtraction

extractor = AgentExtraction()
data = extractor.extract_from_file("config.json")
```

### 3. Gap Analysis

Identifies missing information:

```python
from gpt_simulation_agent.agent_system.agent_gap_analysis import AgentGapAnalysis

analyzer = AgentGapAnalysis()
gaps = analyzer.analyze(current_config, required_fields)

for gap in gaps:
    print(f"Missing: {gap['field']}")
    print(f"Suggestion: {gap['suggestion']}")
```

### 4. Social Media Ingestion

Connects to Facebook and Instagram APIs:

```python
from gpt_simulation_agent.agent_system.agent_social_ingestion import AgentSocialIngestion

ingestion = AgentSocialIngestion()

# Ingest from platforms
data = ingestion.ingest(platforms=['facebook', 'instagram'])

# Process conversations
processed = ingestion.process_conversations(data)
```

### 5. Training Data Processor

Processes training data for KB updates:

```python
from gpt_simulation_agent.agent_system.agent_training_processor import AgentTrainingProcessor

processor = AgentTrainingProcessor()
training_data = processor.process(raw_data)
```

### 6. Gem Generator

Generates Google Labs Gems:

```python
from gpt_simulation_agent.agent_system.agent_gem_generator import AgentGemGenerator

generator = AgentGemGenerator()
gems = generator.generate(
    config=gpt_config,
    generate_multiple=True
)

# Export for Google Labs
generator.export_gems(gems, "output/gems/")
```

---

## Configuration

### Environment Variables

```bash
# Social Media APIs
FACEBOOK_ACCESS_TOKEN=your-token
INSTAGRAM_ACCESS_TOKEN=your-token
FACEBOOK_PAGE_ID=your-page-id

# MongoDB (optional)
MONGODB_URI=mongodb://localhost:27017/panelin
```

### Configuration File

Create `agent_system/config/config.json`:

```json
{
    "workspace_path": ".",
    "output_path": "output/",
    "training_data_path": "training_data/",
    "platforms": ["facebook", "instagram"],
    "auto_extract": true,
    "generate_gems": true
}
```

---

## Complete Workflow

```python
from gpt_simulation_agent.agent_system.gpt_simulation_agent import GPTSimulationAgent

# Initialize
agent = GPTSimulationAgent(workspace_path=".")

# Step 1: Self-diagnosis
diagnosis = agent.diagnose()
print(f"Workspace health: {diagnosis['health_score']}/100")

# Step 2: Configure
config = agent.configure()

# Step 3: Ingest social media
agent.ingest_social_media(platforms=['facebook', 'instagram'])

# Step 4: Process training data
results = agent.process_training_data()

# Step 5: Generate analytics
analytics = agent.generate_analytics()
print(f"Total interactions: {analytics['total_interactions']}")
print(f"Common queries: {analytics['common_queries']}")

# Step 6: Generate Gems
gems = agent.generate_gems(generate_multiple=True)

# Step 7: Export
agent.export_all("output/")
```

---

## Output Files

| File | Description |
|------|-------------|
| `output/diagnosis_report.json` | Self-diagnosis results |
| `output/config.json` | Generated configuration |
| `output/analytics.json` | Analytics report |
| `output/gems/*.json` | Generated Gems |
| `training_data/processed/*.json` | Processed training data |

---

## Integration

### With KB Training System

```python
from gpt_simulation_agent.agent_system.gpt_simulation_agent import GPTSimulationAgent
from kb_training_system import Level3ProactiveIngestion

# Get social data
agent = GPTSimulationAgent(workspace_path=".")
social_data = agent.ingest_social_media(['facebook', 'instagram'])

# Feed to training
trainer = Level3ProactiveIngestion(kb_path="Files/")
trainer.train_from_social(social_data)
```

### With KB Config Agent

```python
from gpt_simulation_agent.agent_system.gpt_simulation_agent import GPTSimulationAgent
from gpt_kb_config_agent import GPTKnowledgeBaseAgent

# Generate config from simulation
sim_agent = GPTSimulationAgent(workspace_path=".")
sim_config = sim_agent.configure()

# Generate GPT config
kb_agent = GPTKnowledgeBaseAgent(kb_path="Files/")
gpt_config = kb_agent.configure_gpt(
    gpt_name="Panelin",
    use_case="quotation",
    additional_config=sim_config
)
```

---

## Related

- [[Agents-Overview]] - All agents
- [[Training-System]] - Training integration
- [[KB-Config-Agent]] - KB configuration

---

<p align="center">
  <a href="[[Analysis-Agent]]">← Analysis Agent</a> |
  <a href="[[KB-Config-Agent]]">KB Config Agent →</a>
</p>
