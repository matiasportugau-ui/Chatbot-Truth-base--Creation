# Configuration Guide

This guide covers all configuration options for the Panelin AI System, including environment variables, GPT setup, and system customization.

---

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [GPT Configuration](#gpt-configuration)
3. [Knowledge Base Configuration](#knowledge-base-configuration)
4. [Agent Configuration](#agent-configuration)
5. [Training Configuration](#training-configuration)
6. [Advanced Configuration](#advanced-configuration)

---

## Environment Variables

### Required Variables

Create a `.env` file in the project root:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Optional Variables

```bash
# Claude (Anthropic) - for multi-model support
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key

# Gemini (Google) - for multi-model support
GOOGLE_API_KEY=your-google-api-key

# MongoDB - for data persistence
MONGODB_URI=mongodb://localhost:27017/panelin

# Social Media APIs (for GPT Simulation Agent)
FACEBOOK_ACCESS_TOKEN=your-facebook-token
INSTAGRAM_ACCESS_TOKEN=your-instagram-token

# Debug mode
PANELIN_DEBUG=false

# Log level
PANELIN_LOG_LEVEL=INFO
```

### Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `ANTHROPIC_API_KEY` | No | - | Claude API key |
| `GOOGLE_API_KEY` | No | - | Gemini API key |
| `MONGODB_URI` | No | - | MongoDB connection string |
| `PANELIN_DEBUG` | No | false | Enable debug mode |
| `PANELIN_LOG_LEVEL` | No | INFO | Log level (DEBUG, INFO, WARNING, ERROR) |

### Loading Environment Variables

```python
from dotenv import load_dotenv
import os

# Load from .env file
load_dotenv()

# Access variables
openai_key = os.getenv("OPENAI_API_KEY")
debug_mode = os.getenv("PANELIN_DEBUG", "false").lower() == "true"
```

---

## GPT Configuration

### GPT Builder Setup

1. **Access GPT Builder**: [chatgpt.com/gpts/editor](https://chatgpt.com/gpts/editor)

2. **Basic Configuration**:
   - **Name**: Panelin - BMC Assistant Pro
   - **Description**: Experto técnico en cotizaciones y sistemas constructivos BMC

3. **Instructions**: Copy from `PANELIN_INSTRUCTIONS_FINAL.txt`

### GPT Configuration File Structure

```json
{
    "name": "Panelin - BMC Assistant Pro",
    "description": "Experto técnico en cotizaciones...",
    "instructions": "# IDENTIDAD Y ROL\n\nEres **Panelin**...",
    "model": "gpt-4",
    "capabilities": {
        "code_interpreter": true,
        "web_browsing": true
    },
    "knowledge_base_files": [
        "BMC_Base_Conocimiento_GPT-2.json",
        "PANELIN_KNOWLEDGE_BASE_GUIDE.md",
        "PANELIN_QUOTATION_PROCESS.md"
    ]
}
```

### Generate GPT Config Programmatically

```python
from gpt_kb_config_agent import GPTKnowledgeBaseAgent

agent = GPTKnowledgeBaseAgent(
    knowledge_base_path="Files/",
    output_path="gpt_configs/"
)

# Generate configuration
config = agent.configure_gpt(
    gpt_name="Panelin Assistant",
    use_case="quotation"  # Options: general, quotation, assistant
)

# Config is saved to gpt_configs/Panelin_Assistant_config.json
```

### Conversation Starters

Recommended conversation starters:

```
1. "Hola, mi nombre es [nombre]"
2. "Necesito cotizar ISODEC 100mm para un techo de 6m de luz"
3. "¿Qué diferencia hay entre EPS y PIR?"
4. "¿Cómo calculo los materiales para un techo?"
```

### Model Selection

| Model | Recommended For | Notes |
|-------|-----------------|-------|
| GPT-4 Turbo | Production | Best performance |
| GPT-4 | Production | Stable, reliable |
| GPT-3.5 | Not Recommended | Insufficient for technical calculations |

---

## Knowledge Base Configuration

### File Structure

```
Files/
├── BMC_Base_Conocimiento_GPT-2.json    # Level 1: Master
├── BMC_Base_Unificada_v4.json          # Level 2: Validation
├── panelin_truth_bmcuruguay_web_only_v2.json  # Level 3: Dynamic
├── Aleros -2.rtf                        # Level 4: Support
└── panelin_truth_bmcuruguay_catalog_v2_index.csv
```

### Level Configuration

```python
# Custom KB hierarchy
KB_HIERARCHY = {
    1: {
        "files": ["BMC_Base_Conocimiento_GPT-2.json"],
        "priority": "HIGHEST",
        "purpose": "Source of Truth"
    },
    2: {
        "files": ["BMC_Base_Unificada_v4.json"],
        "priority": "MEDIUM",
        "purpose": "Validation only"
    },
    3: {
        "files": ["panelin_truth_bmcuruguay_web_only_v2.json"],
        "priority": "LOW",
        "purpose": "Price updates"
    },
    4: {
        "files": ["Aleros -2.rtf", "*.csv", "*.md"],
        "priority": "LOWEST",
        "purpose": "Context"
    }
}
```

### Validate KB Structure

```bash
# Command line
python -m gpt_kb_config_agent.main validate --kb-path "Files/"

# Python
from gpt_kb_config_agent import GPTKnowledgeBaseAgent

agent = GPTKnowledgeBaseAgent(knowledge_base_path="Files/")
result = agent.validate_and_fix()
print(f"Health Score: {result['health_score']}/100")
```

---

## Agent Configuration

### Quotation Agent Configuration

```python
# Custom configuration for OpenAI Assistant
ASSISTANT_CONFIG = {
    "name": "Panelin - BMC Assistant Pro",
    "instructions": """...""",
    "model": "gpt-4",
    "tools": [
        {"type": "function", "function": get_cotizacion_function_schema()},
        {"type": "code_interpreter"}
    ]
}
```

### Claude Agent Configuration

```python
CLAUDE_CONFIG = {
    "system": """Eres Panelin, BMC Assistant Pro...""",
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 4096,
    "tools": [
        {
            "name": "calcular_cotizacion",
            "description": "...",
            "input_schema": {...}
        }
    ]
}
```

### Gemini Agent Configuration

```python
GEMINI_CONFIG = {
    "model_name": "gemini-1.5-pro",
    "system_instruction": """Eres Panelin...""",
    "tools": [
        {
            "function_declarations": [
                {
                    "name": "calcular_cotizacion",
                    "parameters": {...}
                }
            ]
        }
    ]
}
```

---

## Training Configuration

### Training Orchestrator Configuration

```python
from kb_training_system import TrainingOrchestrator

orchestrator = TrainingOrchestrator(
    knowledge_base_path="Files/",
    quotes_path="quotes/",
    interactions_path="training_data/interactions/",
    social_data_path="training_data/social_media/",
    
    # Configuration options
    config={
        "levels_to_run": [1, 2, 3, 4],
        "auto_backup": True,
        "notify_on_complete": True,
        "evaluation_threshold": 0.75
    }
)
```

### Evaluation Thresholds

```python
EVALUATION_CONFIG = {
    "relevance_threshold": 0.75,
    "groundedness_threshold": 0.70,
    "coherence_threshold": 0.75,
    "source_compliance_threshold": 0.90,
    "max_leak_rate": 0.10
}
```

### Scheduled Training

```python
from kb_auto_scheduler import KBAutoScheduler

scheduler = KBAutoScheduler()

# Configure schedule
scheduler.configure({
    "daily_validation": {
        "enabled": True,
        "time": "02:00",
        "levels": [1, 2]
    },
    "weekly_full_pipeline": {
        "enabled": True,
        "day": "sunday",
        "time": "03:00"
    },
    "monthly_evolution": {
        "enabled": True,
        "day": 1,
        "time": "04:00",
        "strategy": "auto"
    }
})
```

---

## Advanced Configuration

### Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('panelin.log'),
        logging.StreamHandler()
    ]
)

# Per-module logging
logging.getLogger('agente_cotizacion').setLevel(logging.DEBUG)
logging.getLogger('kb_training_system').setLevel(logging.INFO)
```

### Custom Model Assignments

Override default model assignments:

```python
from orquestador_multi_modelo import (
    OrquestadorMultiModelo, 
    TipoProcedimiento, 
    ModeloIA,
    AsignacionModelo
)

orchestrator = OrquestadorMultiModelo()

# Override assignment
orchestrator.ASIGNACIONES[TipoProcedimiento.PRESENTACION] = AsignacionModelo(
    procedimiento=TipoProcedimiento.PRESENTACION,
    modelo_principal=ModeloIA.OPENAI,
    modelo_alternativo=ModeloIA.CLAUDE,
    prioridad="alta",
    razon="Custom requirement"
)
```

### Business Rules Configuration

Configure business rules in the KB JSON:

```json
{
    "reglas_negocio": {
        "iva": 0.22,
        "pendiente_minima_techo": 0.07,
        "moneda": "USD",
        "incluir_envio": false,
        "descuento_volumen": {
            "umbral_m2": 100,
            "porcentaje": 0.05
        },
        "margen_seguridad_autoportancia": 0.1
    }
}
```

### Conflict Detection Configuration

```python
from panelin_improvements.conflict_detector import ConflictDetector

detector = ConflictDetector(
    kb_path="Files/",
    config={
        "price_tolerance": 0.01,  # 1% price difference allowed
        "auto_resolve": False,    # Don't auto-resolve
        "notify_critical": True,  # Notify on critical conflicts
        "log_all": True           # Log all conflicts
    }
)
```

---

## Configuration Files Reference

| File | Purpose | Location |
|------|---------|----------|
| `.env` | Environment variables | Project root |
| `PANELIN_INSTRUCTIONS_FINAL.txt` | GPT instructions | Project root |
| `gpt_configs/*.json` | GPT configurations | gpt_configs/ |
| `Files/*.json` | Knowledge base | Files/ |
| `training_data/` | Training data | training_data/ |

---

## Verification

### Verify Configuration

```python
from verificar_configuracion import verificar_todo

# Run all verifications
resultado = verificar_todo()

print("Configuration Status:")
print(f"  API Keys: {'✅' if resultado['api_keys_ok'] else '❌'}")
print(f"  KB Files: {'✅' if resultado['kb_files_ok'] else '❌'}")
print(f"  GPT Config: {'✅' if resultado['gpt_config_ok'] else '❌'}")
print(f"  Dependencies: {'✅' if resultado['dependencies_ok'] else '❌'}")
```

### Test Configuration

```bash
# Run configuration tests
python verificar_configuracion.py

# Run system tests
python prueba_sistema.py
```

---

## Related Documentation

- [[Getting-Started]] - Installation guide
- [[Knowledge-Base]] - KB configuration details
- [[Troubleshooting]] - Configuration issues

---

<p align="center">
  <a href="[[API-Reference]]">← API Reference</a> |
  <a href="[[Troubleshooting]]">Troubleshooting →</a>
</p>
