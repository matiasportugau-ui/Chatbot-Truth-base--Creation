# Getting Started

This guide will help you set up and run the Panelin AI System on your local machine or server.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [First Run](#first-run)
5. [Verify Installation](#verify-installation)
6. [Next Steps](#next-steps)

---

## Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.11+ |
| Node.js | 16+ | 20+ (for TypeScript SDK) |
| RAM | 4GB | 8GB+ |
| Disk Space | 500MB | 2GB+ |

### Required API Keys

You'll need at least one of the following API keys:

| Provider | Required For | Get Key At |
|----------|--------------|------------|
| **OpenAI** | Core functionality | [platform.openai.com](https://platform.openai.com) |
| **Anthropic** | Claude agent | [console.anthropic.com](https://console.anthropic.com) |
| **Google** | Gemini agent | [makersuite.google.com](https://makersuite.google.com) |

> **Note**: OpenAI is the primary platform. The system will work with just an OpenAI key, but having multiple keys enables multi-model orchestration.

---

## Installation

### Option 1: Standard Installation

```bash
# Clone the repository
git clone https://github.com/your-org/panelin.git
cd panelin

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for TypeScript SDK)
npm install
```

### Option 2: Development Installation

```bash
# Clone the repository
git clone https://github.com/your-org/panelin.git
cd panelin

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### Dependencies

The main dependencies are:

```
jsonschema>=4.0.0      # JSON validation
openai>=1.0.0          # OpenAI API client
python-dotenv>=1.0.0   # Environment variable management
pymongo>=4.0.0         # MongoDB client (optional)
anthropic              # Claude API client (optional)
google-generativeai    # Gemini API client (optional)
```

---

## Configuration

### Step 1: Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# Or create a new one
touch .env
```

### Step 2: Add API Keys

Edit `.env` with your API keys:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-openai-key-here

# Optional: Claude (Anthropic)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Optional: Gemini (Google)
GOOGLE_API_KEY=your-google-api-key-here

# Optional: MongoDB (for data persistence)
MONGODB_URI=mongodb://localhost:27017/panelin
```

### Step 3: Verify Knowledge Base

Ensure the knowledge base files are present:

```bash
ls -la "Files /"
# Should show:
# - BMC_Base_Unificada_v4.json (Master knowledge base)
# - panelin_truth_bmcuruguay_catalog_v2_index.csv
# - panelin_truth_bmcuruguay_web_only_v2.json
# - Aleros -2.rtf
```

### Step 4: Configure GPT (Optional)

If you're setting up the GPT in OpenAI:

```bash
# Verify GPT configuration
python verificar_configuracion.py
```

---

## First Run

### Basic Quotation Example

```python
#!/usr/bin/env python3
"""First quotation example"""

from agente_cotizacion_panelin import calcular_cotizacion_agente

# Calculate a quotation
result = calcular_cotizacion_agente(
    producto="ISODEC EPS",    # Product type
    espesor="100",            # Thickness in mm
    largo=10.0,               # Length in meters
    ancho=5.0,                # Width in meters
    luz=4.5,                  # Span between supports
    tipo_fijacion="hormigon"  # Fixing type: hormigon/metal/madera
)

if result['success']:
    print("✅ Quotation successful!")
    print(result['presentacion_texto'])
else:
    print(f"❌ Error: {result['error']}")
```

### Run the Example

```bash
python -c "
from agente_cotizacion_panelin import calcular_cotizacion_agente

result = calcular_cotizacion_agente(
    producto='ISODEC EPS',
    espesor='100',
    largo=10.0,
    ancho=5.0,
    luz=4.5,
    tipo_fijacion='hormigon'
)

print(result['presentacion_texto'] if result['success'] else result['error'])
"
```

### Expected Output

```
================================================================================
                    COTIZACIÓN PANELIN - BMC ASSISTANT PRO
================================================================================

📋 PRODUCTO: ISODEC EPS 100mm
📐 DIMENSIONES: 10.0m x 5.0m = 50.0 m²
🔧 TIPO DE FIJACIÓN: Hormigón

✅ VALIDACIÓN TÉCNICA:
   • Autoportancia: 5.5m (cumple para luz de 4.5m)
   • Luz efectiva: 4.5m

📦 MATERIALES:
   • Paneles ISODEC EPS 100mm: 53 unidades
   • Varilla roscada 3/8": 21 unidades
   • Tuerca hexagonal 3/8": 42 unidades
   • Arandela plana 3/8": 42 unidades
   • Taco expansivo 3/8": 21 unidades

💰 COSTOS:
   • Subtotal: $2,441.71 USD
   • IVA (22%): $537.18 USD
   • TOTAL: $2,978.89 USD

================================================================================
```

---

## Verify Installation

### Run System Test

```bash
python prueba_sistema.py
```

### Check Agent Status

```python
from orquestador_multi_modelo import OrquestadorMultiModelo

orchestrator = OrquestadorMultiModelo()

# Check available models
print("Available Models:")
print(f"  OpenAI: {'✅' if orchestrator.openai_agente else '❌'}")
print(f"  Claude: {'✅' if orchestrator.claude_agente else '❌'}")
print(f"  Gemini: {'✅' if orchestrator.gemini_agente else '❌'}")
```

### Validate Knowledge Base

```bash
python -m gpt_kb_config_agent.main validate --kb-path "Files /"
```

---

## Next Steps

Now that you have Panelin installed and running, you can:

### 1. Learn the Architecture
Understand how the system components work together:
- [[Architecture]] - System architecture overview

### 2. Explore the Agents
Learn about each AI agent and its capabilities:
- [[Agents-Overview]] - Complete agents documentation

### 3. Configure the Knowledge Base
Set up and optimize your knowledge base:
- [[Knowledge-Base]] - KB hierarchy and management

### 4. Set Up Training
Configure the training system for continuous improvement:
- [[Training-System]] - Training system documentation

### 5. API Integration
Integrate Panelin into your applications:
- [[API-Reference]] - Complete API documentation

---

## Common Setup Issues

### Issue: `ModuleNotFoundError`

```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: API Key Not Found

```bash
# Check if .env is loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Issue: Knowledge Base Files Missing

```bash
# Check file structure
ls -la "Files /"

# If missing, check git status
git status
```

For more troubleshooting help, see [[Troubleshooting]].

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `python prueba_sistema.py` | Run system tests |
| `python verificar_configuracion.py` | Verify GPT configuration |
| `python ejercicio_cotizacion_panelin.py` | Run quotation exercises |
| `python orquestador_multi_modelo.py` | Run multi-model orchestrator |

---

<p align="center">
  <a href="[[Home]]">← Home</a> |
  <a href="[[Architecture]]">Architecture →</a>
</p>
