# KB Update and Training

## Overview
This repo includes an automated knowledge base update pipeline and a multi-level
training system to keep Panelin accurate while minimizing costs.

## KB update system
Primary scripts:
- `kb_update_optimizer.py` (tiered KB update)
- `training_data_optimizer.py` (incremental training processing)
- `kb_auto_scheduler.py` (automation and scheduling)
- `setup_kb_update_system.sh` (one-shot setup)

Basic commands:
```bash
# Status checks
python kb_update_optimizer.py --stats
python training_data_optimizer.py --stats

# Update KB tiers
python kb_update_optimizer.py --tier all
python kb_update_optimizer.py --tier level_3

# Training data processing
python training_data_optimizer.py --process
python training_data_optimizer.py --extract-patterns
```

## Scheduling
Testing:
```bash
python kb_auto_scheduler.py --once
```

Daemon mode:
```bash
nohup python kb_auto_scheduler.py --daemon > scheduler.log 2>&1 &
```

Cron example:
```
0 2 * * * cd /path/to/repo && python kb_update_optimizer.py --tier level_3
0 4 * * * cd /path/to/repo && python training_data_optimizer.py --process
0 3 * * 0 cd /path/to/repo && python kb_update_optimizer.py --tier level_2
0 5 * * 0 cd /path/to/repo && python training_data_optimizer.py --extract-patterns
0 4 1 * * cd /path/to/repo && python kb_update_optimizer.py --tier level_1
```

## Training system (kb_training_system)
The training system evolves the KB using evaluation metrics, leak detection, and
multi-level training:
- Evaluation: relevance, groundedness, coherence, accuracy
- Leak detection: missing info, source mismatch, coverage gaps
- Level 1..4 training pipeline

Example usage:
```python
from kb_training_system import TrainingOrchestrator

orchestrator = TrainingOrchestrator(
    knowledge_base_path="Files/",
    quotes_path="quotes/",
    interactions_path="training_data/interactions/",
    social_data_path="training_data/social_media/"
)

result = orchestrator.run_complete_pipeline(
    quotes=quotes_data,
    interactions=interactions_data,
    social_interactions=social_data
)
```

## Monitoring and expected results
The strategy targets cost reductions of 55-80% using hash checks, incremental
updates, and local-first processing.

## References
- KB_UPDATE_QUICKSTART.md
- KB_UPDATE_TRAINING_STRATEGY.md
- KB_TRAINING_SYSTEM_SUMMARY.md
