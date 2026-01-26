# Panelin AI System - Complete Documentation

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Multi--AI-orange.svg" alt="Platform">
</p>

## Overview

**Panelin** is a comprehensive AI-powered system for managing construction panel quotations and technical assistance for **BMC (Building Materials Company)**. The system specializes in **Isopanels (EPS and PIR)**, **Dry Construction**, and **Waterproofing** products.

The platform combines multiple AI agents, a robust knowledge base system, and multi-model orchestration to provide accurate technical quotations, sales team training, and intelligent document processing.

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Platform AI Agents** | Support for OpenAI, Claude, Gemini, and more |
| **Intelligent Quotation Engine** | Calculates materials, validates load-bearing capacity, applies business rules |
| **Knowledge Base Training System** | 4-level training system with leak detection and evaluation metrics |
| **Multi-Model Orchestration** | Assigns tasks to optimal AI models based on procedure type |
| **GPT Configuration Agent** | Automatically configures and evolves GPT knowledge bases |
| **Social Media Ingestion** | Processes training data from Facebook and Instagram |
| **File Organization Agent** | Automatically organizes project files with version management |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PANELIN AI SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   OpenAI    │  │   Claude    │  │        Gemini           │ │
│  │   Agent     │  │   Agent     │  │        Agent            │ │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘ │
│         │                │                     │               │
│         └────────────────┼─────────────────────┘               │
│                          ▼                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │            MULTI-MODEL ORCHESTRATOR                        │ │
│  │   • Route tasks to optimal AI model                       │ │
│  │   • Fallback handling                                     │ │
│  │   • Priority-based assignment                             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                          ▼                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              QUOTATION ENGINE                              │ │
│  │   • Material calculations                                 │ │
│  │   • Autoportancia validation                              │ │
│  │   • Price lookup from Knowledge Base                      │ │
│  │   • IVA calculation (22%)                                 │ │
│  └───────────────────────────────────────────────────────────┘ │
│                          ▼                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              KNOWLEDGE BASE (4 Levels)                     │ │
│  │   Level 1: Master (Source of Truth)                       │ │
│  │   Level 2: Validation                                     │ │
│  │   Level 3: Dynamic (Price Updates)                        │ │
│  │   Level 4: Support (Contextual)                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Navigation

### Getting Started
- [[Getting-Started]] - Installation and setup guide
- [[Configuration]] - Configure API keys and system settings

### Core Components
- [[Architecture]] - System architecture overview
- [[Quotation-Engine]] - How the quotation system works
- [[Knowledge-Base]] - Knowledge base hierarchy and management

### AI Agents
- [[Agents-Overview]] - All AI agents documentation
- [[Quotation-Agent]] - Panelin quotation agent
- [[Analysis-Agent]] - Intelligent analysis agent
- [[GPT-Simulation-Agent]] - Self-configuring GPT agent
- [[KB-Config-Agent]] - Knowledge base configuration agent
- [[Files-Organizer-Agent]] - AI file organization agent

### Training & Learning
- [[Training-System]] - KB training system overview
- [[Multi-Model-Orchestration]] - Multi-model task assignment

### Reference
- [[API-Reference]] - Complete API documentation
- [[Troubleshooting]] - Common issues and solutions
- [[Changelog]] - Version history

---

## Supported AI Platforms

| Platform | Status | Function Calling | Best For |
|----------|--------|------------------|----------|
| **OpenAI** | ✅ Production | Native | Real-time quotations, Code Interpreter |
| **Claude** | ✅ Ready | Excellent | Deep analysis, learning synthesis |
| **Gemini** | ✅ Ready | Available | Backup, multimodal processing |
| **Grok** | ⚠️ Limited | Not Public | Direct motor only |

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
npm install  # For TypeScript SDK
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=...
```

### 3. Run Your First Quotation

```python
from agente_cotizacion_panelin import calcular_cotizacion_agente

result = calcular_cotizacion_agente(
    producto="ISODEC EPS",
    espesor="100",
    largo=10.0,
    ancho=5.0,
    luz=4.5,
    tipo_fijacion="hormigon"
)

print(result['presentacion_texto'])
```

---

## Project Structure

```
panelin/
├── agents/
│   ├── agente_cotizacion_panelin.py    # Quotation agent
│   ├── agente_analisis_inteligente.py  # Analysis agent
│   ├── orquestador_multi_modelo.py     # Multi-model orchestrator
│   └── ...
├── kb_training_system/                  # Training system
│   ├── kb_evaluator.py                 # Evaluation system
│   ├── kb_leak_detector.py             # Leak detection
│   ├── training_levels.py              # 4 training levels
│   └── training_orchestrator.py        # Pipeline orchestrator
├── gpt_kb_config_agent/                 # KB configuration agent
├── gpt_simulation_agent/                # GPT simulation agent
├── ai-project-files-organizer-agent/    # File organizer agent
├── panelin_improvements/                # System improvements
├── Files/                               # Knowledge base files
├── gpt_configs/                         # GPT configurations
└── training_data/                       # Training data
```

---

## Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| Home | ✅ Complete | 2026-01-23 |
| Getting Started | ✅ Complete | 2026-01-23 |
| Architecture | ✅ Complete | 2026-01-23 |
| Agents Overview | ✅ Complete | 2026-01-23 |
| Knowledge Base | ✅ Complete | 2026-01-23 |
| Training System | ✅ Complete | 2026-01-23 |
| API Reference | ✅ Complete | 2026-01-23 |
| Troubleshooting | ✅ Complete | 2026-01-23 |

---

## Contributing

We welcome contributions! Please see our [[Contributing]] guide for details on how to submit pull requests, report issues, and contribute to documentation.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

- 📖 [Documentation](wiki/)
- 🐛 [Issue Tracker](https://github.com/your-org/panelin/issues)
- 💬 [Discussions](https://github.com/your-org/panelin/discussions)

---

<p align="center">
  <strong>Panelin AI System</strong> - Intelligent Construction Panel Quotation System
  <br>
  <em>Built with ❤️ for BMC Uruguay</em>
</p>
