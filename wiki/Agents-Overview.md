# AI Agents Overview

The Panelin system includes multiple specialized AI agents, each designed for specific tasks. This document provides an overview of all agents and their capabilities.

---

## Table of Contents

1. [Agent Summary](#agent-summary)
2. [Quotation Agent](#quotation-agent)
3. [Analysis Agent](#analysis-agent)
4. [GPT Simulation Agent](#gpt-simulation-agent)
5. [KB Config Agent](#kb-config-agent)
6. [Files Organizer Agent](#files-organizer-agent)
7. [Agent Comparison](#agent-comparison)

---

## Agent Summary

| Agent | Primary Function | Platform Support | Status |
|-------|------------------|------------------|--------|
| **Quotation Agent** | Calculate quotations | OpenAI, Claude, Gemini | ✅ Production |
| **Analysis Agent** | Analyze & learn from quotes | OpenAI | ✅ Production |
| **GPT Simulation Agent** | Self-configure GPT | Python | ✅ Production |
| **KB Config Agent** | Configure knowledge base | Python | ✅ Production |
| **Files Organizer Agent** | Organize project files | Python | ✅ Production |

---

## Quotation Agent

**File:** `agente_cotizacion_panelin.py`

The Quotation Agent is the primary agent for generating technical quotations for construction panels.

### Capabilities

- Calculate complete quotations with material breakdown
- Validate autoportancia (load-bearing capacity)
- Apply business rules (IVA 22%, minimum slope 7%)
- Present results professionally
- Support multiple fixing types (concrete, metal, wood)

### Supported Platforms

| Platform | Class | Status |
|----------|-------|--------|
| OpenAI | `AgentePanelinOpenAI` | ✅ Production |
| Claude | `AgentePanelinClaude` | ✅ Ready |
| Gemini | `AgentePanelinGemini` | ✅ Ready |

### Usage

```python
from agente_cotizacion_panelin import calcular_cotizacion_agente

# Calculate quotation
result = calcular_cotizacion_agente(
    producto="ISODEC EPS",
    espesor="100",
    largo=10.0,
    ancho=5.0,
    luz=4.5,
    tipo_fijacion="hormigon"
)

if result['success']:
    print(result['presentacion_texto'])
```

### Function Schema

The agent exposes a Function Calling schema for AI integration:

```python
{
    "name": "calcular_cotizacion",
    "description": "Calcula una cotización completa para paneles...",
    "parameters": {
        "type": "object",
        "properties": {
            "producto": {
                "type": "string",
                "enum": ["ISODEC EPS", "ISODEC PIR", "ISOPANEL EPS", ...]
            },
            "espesor": {"type": "string"},
            "largo": {"type": "number"},
            "ancho": {"type": "number"},
            "luz": {"type": "number"},
            "tipo_fijacion": {
                "type": "string",
                "enum": ["hormigon", "metal", "madera"]
            }
        },
        "required": ["producto", "espesor", "largo", "ancho", "luz", "tipo_fijacion"]
    }
}
```

### Platform-Specific Usage

#### OpenAI

```python
from agente_cotizacion_panelin import AgentePanelinOpenAI
import os

agent = AgentePanelinOpenAI(os.getenv("OPENAI_API_KEY"))
agent.crear_asistente()

thread = agent.client.beta.threads.create()
response = agent.procesar_mensaje(
    thread.id,
    "Cotiza ISODEC EPS 100mm para un techo de 10m x 5m con luz de 4.5m"
)
print(response)
```

#### Claude

```python
from agente_cotizacion_panelin import AgentePanelinClaude
import os

agent = AgentePanelinClaude(os.getenv("ANTHROPIC_API_KEY"))
response = agent.chat(
    "Cotiza ISODEC EPS 100mm para un techo de 10m x 5m con luz de 4.5m"
)
print(response)
```

#### Gemini

```python
from agente_cotizacion_panelin import AgentePanelinGemini
import os

agent = AgentePanelinGemini(os.getenv("GOOGLE_API_KEY"))
response = agent.chat(
    "Cotiza ISODEC EPS 100mm para un techo de 10m x 5m con luz de 4.5m"
)
print(response)
```

---

## Analysis Agent

**File:** `agente_analisis_inteligente.py`

The Analysis Agent reviews inputs, compares quotations with real PDFs, and generates learning insights.

### Capabilities

- Review historical inputs
- Generate budgets from inputs
- Find matching real PDFs
- Extract data from PDFs
- Compare generated vs real quotations
- Identify differences and learn

### Process Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Review     │────▶│  Generate   │────▶│  Find PDF   │
│  Inputs     │     │  Budget     │     │  Match      │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Learn &    │◀────│  Compare    │◀────│  Extract    │
│  Improve    │     │  Results    │     │  PDF Data   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Usage

```python
from agente_analisis_inteligente import analizar_cotizacion_completa

# Analyze quotation
result = analizar_cotizacion_completa(
    cliente="Cliente Test",
    producto="ISODEC EPS",
    fecha="2026-01-15",
    consulta="Techo de 50m2"
)

print(f"Inputs reviewed: {len(result.get('inputs', []))}")
print(f"Lessons learned: {len(result.get('lecciones', []))}")
```

### Function Schema

```python
{
    "name": "analizar_cotizacion_completa",
    "description": "Analiza cotizaciones históricas, compara con PDFs reales...",
    "parameters": {
        "type": "object",
        "properties": {
            "cliente": {"type": "string"},
            "producto": {"type": "string"},
            "fecha": {"type": "string"},
            "consulta": {"type": "string"}
        },
        "required": ["cliente", "producto"]
    }
}
```

---

## GPT Simulation Agent

**File:** `gpt_simulation_agent/agent_system/gpt_simulation_agent.py`

A self-configuring agent that automatically gathers requirements and processes training data.

### Capabilities

- **Self-Diagnosis**: Scans workspace and identifies configuration needs
- **Intelligent Extraction**: Extracts from JSON, Markdown, YAML files
- **Gap Analysis**: Identifies missing information
- **Social Media Ingestion**: Connects to Facebook & Instagram APIs
- **Analytics**: Processes training data and generates insights
- **Gem Generation**: Generates Google Labs Gems

### Components

| Component | File | Purpose |
|-----------|------|---------|
| Main Agent | `gpt_simulation_agent.py` | Orchestration |
| Self-Diagnosis | `agent_self_diagnosis.py` | Workspace scanning |
| Extraction | `agent_extraction.py` | Data extraction |
| Gap Analysis | `agent_gap_analysis.py` | Missing data detection |
| Social Ingestion | `agent_social_ingestion.py` | Social media processing |
| Training Processor | `agent_training_processor.py` | Training data |
| Gem Generator | `agent_gem_generator.py` | Gem generation |

### Usage

```python
from gpt_simulation_agent.agent_system.gpt_simulation_agent import GPTSimulationAgent

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

### Directory Structure

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
│       ├── analytics_engine.py      # Analytics
│       ├── facebook_api.py          # Facebook integration
│       ├── instagram_api.py         # Instagram integration
│       ├── mongodb_client.py        # Database
│       └── ...
├── output/                          # Generated outputs
├── training_data/                   # Training data
└── example_usage.py                 # Examples
```

---

## KB Config Agent

**File:** `gpt_kb_config_agent/kb_config_agent.py`

Specialized agent for configuring and evolving GPT knowledge bases.

### Capabilities

- **Comprehensive Analysis**: Analyzes KB structure, content, quality
- **Validation**: Validates source of truth hierarchy
- **Evolution**: Evolves KB based on best practices
- **GPT Configuration**: Generates optimal GPT configurations
- **Conflict Resolution**: Detects and resolves conflicts
- **Health Scoring**: Calculates KB health score (0-100)

### Components

| Component | File | Purpose |
|-----------|------|---------|
| Main Agent | `kb_config_agent.py` | Orchestration |
| Analyzer | `kb_analyzer.py` | Structure analysis |
| Evolver | `kb_evolver.py` | KB evolution |
| Config Generator | `gpt_config_generator.py` | GPT config generation |

### Usage

```python
from gpt_kb_config_agent import GPTKnowledgeBaseAgent

# Initialize
agent = GPTKnowledgeBaseAgent(
    knowledge_base_path="Files/",
    output_path="gpt_configs/"
)

# Analyze
report = agent.analyze_and_review()
print(f"Health Score: {report['health_score']}/100")

# Generate GPT configuration
config = agent.configure_gpt(
    gpt_name="Panelin Assistant",
    use_case="quotation"
)

# Evolve knowledge base
evolution = agent.evolve_knowledge_base(strategy="auto")

# Validate and fix
validation = agent.validate_and_fix()
```

### CLI Commands

```bash
# Analyze knowledge base
python -m gpt_kb_config_agent.main analyze --kb-path Files/

# Generate GPT configuration
python -m gpt_kb_config_agent.main configure \
  --kb-path Files/ \
  --gpt-name "Panelin Assistant" \
  --use-case quotation

# Evolve knowledge base
python -m gpt_kb_config_agent.main evolve \
  --kb-path Files/ \
  --strategy auto

# Validate and fix
python -m gpt_kb_config_agent.main validate --kb-path Files/
```

### Health Score Guidelines

| Score | Status | Action |
|-------|--------|--------|
| 90-100 | Excellent | Ready for production |
| 70-89 | Good | Minor improvements |
| 50-69 | Fair | Needs attention |
| 0-49 | Poor | Critical issues |

---

## Files Organizer Agent

**File:** `ai-project-files-organizer-agent/ai_files_organizer/`

An intelligent agent that automatically organizes project files with version management and Git integration.

### Capabilities

- **Automatic Organization**: Organizes files into best-practice structures
- **Version Management**: Adds version codes (ddmm_vN format)
- **Outdated Detection**: Identifies outdated files
- **Real-time Monitoring**: Watches for new files
- **Approval Workflow**: Requests approval before changes
- **Git Integration**: Safe Git operations with approval
- **Smart Categorization**: Automatically categorizes files
- **Automatic Backup**: Creates backups before moving

### Usage

#### CLI

```bash
# Organize existing files
files-organizer organize /path/to/project

# Watch for new files
files-organizer watch /path/to/project

# Scan without making changes
files-organizer scan /path/to/project
```

#### Python API

```python
from ai_files_organizer import FileOrganizerAgent

# Initialize
organizer = FileOrganizerAgent(workspace_path="/path/to/project")

# Organize existing files
organizer.organize_existing_files()

# Start monitoring
organizer.start_monitoring()
```

### Target Structure

```
project_root/
├── docs/
│   ├── architecture/
│   ├── guides/
│   ├── configuration/
│   └── knowledge_base/
├── src/ or code/
│   ├── agents/
│   ├── validators/
│   └── utils/
├── data/
│   ├── training/
│   ├── bundles/
│   └── knowledge/
├── config/
├── output/
├── logs/
└── archived/
```

---

## Agent Comparison

### Feature Matrix

| Feature | Quotation | Analysis | GPT Sim | KB Config | Files Org |
|---------|-----------|----------|---------|-----------|-----------|
| OpenAI Support | ✅ | ✅ | ❌ | ❌ | ❌ |
| Claude Support | ✅ | ❌ | ❌ | ❌ | ❌ |
| Gemini Support | ✅ | ❌ | ❌ | ❌ | ❌ |
| Function Calling | ✅ | ✅ | ❌ | ❌ | ❌ |
| KB Validation | ✅ | ✅ | ❌ | ✅ | ❌ |
| Training | ❌ | ✅ | ✅ | ✅ | ❌ |
| Social Media | ❌ | ❌ | ✅ | ❌ | ❌ |
| File Management | ❌ | ❌ | ❌ | ❌ | ✅ |
| Git Integration | ❌ | ❌ | ❌ | ❌ | ✅ |
| CLI | ❌ | ❌ | ❌ | ✅ | ✅ |

### Use Case Guide

| Use Case | Recommended Agent |
|----------|-------------------|
| Generate quotation | Quotation Agent |
| Review past quotes | Analysis Agent |
| Configure GPT | KB Config Agent |
| Train from social media | GPT Simulation Agent |
| Organize project files | Files Organizer Agent |
| Detect KB conflicts | KB Config Agent |
| Generate Gems | GPT Simulation Agent |

---

## Related Documentation

- [[Quotation-Engine]] - Detailed quotation engine documentation
- [[Knowledge-Base]] - Knowledge base hierarchy
- [[Training-System]] - Training system documentation
- [[API-Reference]] - Complete API reference

---

<p align="center">
  <a href="[[Architecture]]">← Architecture</a> |
  <a href="[[Knowledge-Base]]">Knowledge Base →</a>
</p>
