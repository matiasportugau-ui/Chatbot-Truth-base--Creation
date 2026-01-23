# Architecture

## High-level view
The system combines a structured knowledge base with multiple agent runtimes and
an automation pipeline for updates and training.

Key building blocks:
- Knowledge base with strict source-of-truth hierarchy (Levels 1-4).
- Quotation engine (`motor_cotizacion_panelin.py`) that applies validated
  formulas and business rules.
- Multi-platform agent layer (OpenAI, Claude, Gemini) and a TypeScript Agents
  SDK implementation.
- Update and training automation (KB update optimizer and training pipeline).

## Runtime flow (Panelin response)
```
User request
    |
    v
Agent or SDK (guardrails + routing + personalization)
    |
    v
Knowledge Base (Level 1 -> Level 4)
    |
    v
Quotation engine + business rules + formulas
    |
    v
Structured response (pricing, materials, IVA, recommendations)
```

## Knowledge base hierarchy
```
Level 1 (Master)     -> Prices, formulas, specs (source of truth)
Level 2 (Validation) -> Cross-reference and conflict detection
Level 3 (Dynamic)    -> Web updates, stock status
Level 4 (Support)    -> SOPs, guides, CSV/RTF/MD context
```

## Update and training pipeline
```
Scheduler / Cron
    |
    v
KB Update Optimizer (kb_update_optimizer.py)
    |        |        |
    v        v        v
 Level 1   Level 2   Level 3
 (hash)   (conflict) (delta)
    |
    v
Training Data Optimizer (training_data_optimizer.py)
    |
    v
KB Training System (kb_training_system/)
    |
    v
Reports + Updated KB
```

## Multi-platform agents
```
OpenAI / Claude / Gemini
    |
    v
Function calling tools
    |
    v
Quotation engine + KB search
```

## Relevant docs
- PANELIN_FULL_CONFIGURATION.md
- KB_UPDATE_TRAINING_STRATEGY.md
- KB_TRAINING_SYSTEM_SUMMARY.md
- PANELIN_AGENTS_SDK_README.md
