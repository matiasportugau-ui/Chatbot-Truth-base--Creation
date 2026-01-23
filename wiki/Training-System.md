# Training System

The Panelin Knowledge Base Training System is a comprehensive multi-level system for evolving and improving the chatbot's knowledge base through automated learning, evaluation, and leak detection.

---

## Table of Contents

1. [Overview](#overview)
2. [4-Level Training](#4-level-training)
3. [Evaluation System](#evaluation-system)
4. [Leak Detection](#leak-detection)
5. [Training Orchestrator](#training-orchestrator)
6. [Performance Metrics](#performance-metrics)
7. [Usage Guide](#usage-guide)

---

## Overview

The training system is designed to:

- **Detect leaks** in knowledge base coverage
- **Evaluate** chatbot interactions using industry-standard metrics
- **Train** the KB from quotes, customer interactions, and social media
- **Benchmark** the architecture and measure effectiveness

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRAINING SYSTEM                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              KB EVALUATOR                                │    │
│  │  • Relevance scoring                                    │    │
│  │  • Groundedness scoring                                 │    │
│  │  • Coherence scoring                                    │    │
│  │  • Source compliance                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              LEAK DETECTOR                               │    │
│  │  • Missing information detection                        │    │
│  │  • Incorrect response detection                         │    │
│  │  • Source mismatch detection                            │    │
│  │  • Coverage gap analysis                                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              TRAINING ORCHESTRATOR                       │    │
│  │  • Pipeline management                                  │    │
│  │  • Multi-level training                                 │    │
│  │  • Report generation                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4-Level Training

The training system operates on 4 progressive levels:

### Level 1: Static Grounding

**Purpose:** Convert quotes and documentation into structured KB

**Process:**
```
Quotes/Documentation → Extract Info → Structure → Update KB
```

**Capabilities:**
- Extract product information
- Extract pricing data
- Extract specifications
- Update Level 1 (Master) KB file

**Usage:**

```python
from kb_training_system import Level1StaticGrounding

trainer = Level1StaticGrounding(knowledge_base_path="Files/")

# Train from quotes
result = trainer.train_from_quotes(quotes_data)

print(f"Items added: {result.items_added}")
print(f"Items updated: {result.items_updated}")
```

### Level 2: Interaction-Driven Evolution

**Purpose:** Learn from customer support interactions

**Process:**
```
Customer Interactions → Identify Patterns → Create FAQs → Fill Gaps
```

**Capabilities:**
- Learn from customer support interactions
- Identify common queries and patterns
- Create FAQ entries
- Fill knowledge gaps automatically

**Usage:**

```python
from kb_training_system import Level2InteractionDriven

trainer = Level2InteractionDriven(knowledge_base_path="Files/")

# Train from interactions
result = trainer.train_from_interactions(interactions_data)

print(f"Patterns identified: {result.patterns_count}")
print(f"FAQs created: {result.faqs_created}")
```

### Level 3: Proactive Social & Synthetic Ingestion

**Purpose:** Monitor trends and generate test cases

**Process:**
```
Social Media/Synthetic → Monitor Trends → Generate Tests → Update KB
```

**Capabilities:**
- Monitor social media trends
- Generate synthetic test cases
- Update KB with emerging topics
- Proactive knowledge expansion

**Usage:**

```python
from kb_training_system import Level3ProactiveIngestion

trainer = Level3ProactiveIngestion(knowledge_base_path="Files/")

# Train from social media
result = trainer.train_from_social(social_data)

print(f"Trends detected: {result.trends_count}")
print(f"Topics added: {result.topics_added}")
```

### Level 4: Autonomous Agent Feedback Loop

**Purpose:** Continuous improvement through metrics

**Process:**
```
Performance Metrics → Analyze → Optimize → Autonomous Update
```

**Capabilities:**
- Continuous improvement based on metrics
- Autonomous KB optimization
- Performance-based updates
- Self-healing knowledge base

**Usage:**

```python
from kb_training_system import Level4AutonomousFeedback

trainer = Level4AutonomousFeedback(knowledge_base_path="Files/")

# Run autonomous optimization
result = trainer.run_optimization()

print(f"Optimizations applied: {result.optimizations_count}")
print(f"Performance improvement: {result.improvement_percentage}%")
```

---

## Evaluation System

### Metrics

The evaluation system uses industry-standard metrics based on Azure AI and RAG frameworks:

| Metric | Range | Description |
|--------|-------|-------------|
| **Relevance** | 0-1 | Query-response matching |
| **Groundedness** | 0-1 | KB data reliance |
| **Coherence** | 0-1 | Logical consistency |
| **Accuracy** | Various | BLEU, Precision, Recall, F1 |
| **Source Compliance** | 0-1 | Source of truth adherence |

### Evaluation Process

```python
from kb_training_system import KnowledgeBaseEvaluator

evaluator = KnowledgeBaseEvaluator(knowledge_base_path="Files/")

# Evaluate single interaction
result = evaluator.evaluate_interaction(
    query="¿Cuál es el precio de ISODEC 100mm?",
    response="El precio es $46.07 según BMC_Base_Conocimiento_GPT.json",
    sources_consulted=["BMC_Base_Conocimiento_GPT.json"]
)

print(f"Relevance: {result.relevance_score:.3f}")
print(f"Groundedness: {result.groundedness_score:.3f}")
print(f"Coherence: {result.coherence_score:.3f}")
print(f"Source Compliance: {result.source_compliance:.3f}")
```

### Benchmarking

```python
# Benchmark entire architecture
benchmark = evaluator.benchmark_architecture(evaluation_dataset)

print(f"Average Relevance: {benchmark.average_relevance:.3f}")
print(f"Average Groundedness: {benchmark.average_groundedness:.3f}")
print(f"Average Coherence: {benchmark.average_coherence:.3f}")
print(f"Source Compliance Rate: {benchmark.source_compliance_rate:.1%}")
```

---

## Leak Detection

### What is a Leak?

A "leak" occurs when the chatbot's response reveals a gap or error in the knowledge base.

### Leak Types

| Type | Description | Severity |
|------|-------------|----------|
| **Missing Information** | KB lacks required data | High |
| **Incorrect Response** | Contradicts ground truth | Critical |
| **Source Mismatch** | Wrong source used | Medium |
| **Coverage Gap** | KB doesn't cover query pattern | Medium |

### Detection Process

```python
from kb_training_system import KnowledgeBaseLeakDetector

detector = KnowledgeBaseLeakDetector(knowledge_base_path="Files/")

# Detect leaks in interaction
leaks = detector.detect_leaks_in_interaction(
    query="¿Cuál es el precio?",
    response="No tengo esa información",
    sources_consulted=[]
)

for leak in leaks:
    print(f"Type: {leak.leak_type}")
    print(f"Severity: {leak.severity}")
    print(f"Category: {leak.category}")
    print(f"Recommendation: {leak.recommendation}")
```

### Batch Detection

```python
# Detect leaks in batch
batch_leaks = detector.detect_leaks_batch(interactions_list)

# Analyze results
analysis = detector.analyze_leaks(batch_leaks)

print(f"Total leaks: {analysis.total_leaks}")
print(f"Critical leaks: {analysis.critical_count}")
print(f"Most common type: {analysis.most_common_type}")
print(f"Recommendations: {analysis.recommendations}")
```

### Leak History

```python
# Get leak history
history = detector.get_leak_history()

# Trend analysis
trends = detector.analyze_trends(history)

print(f"Leak rate trend: {'Improving' if trends.improving else 'Declining'}")
print(f"Resolution rate: {trends.resolution_rate:.1%}")
```

---

## Training Orchestrator

The Training Orchestrator coordinates all training levels and manages the complete pipeline.

### Pipeline Execution

```python
from kb_training_system import TrainingOrchestrator

# Initialize
orchestrator = TrainingOrchestrator(
    knowledge_base_path="Files/",
    quotes_path="quotes/",
    interactions_path="training_data/interactions/",
    social_data_path="training_data/social_media/"
)

# Run complete pipeline
result = orchestrator.run_complete_pipeline(
    quotes=quotes_data,
    interactions=interactions_data,
    social_interactions=social_data
)

# Export report
orchestrator.export_pipeline_report(result, "training_report.md")
```

### Pipeline Stages

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Level 1    │──▶│   Level 2    │──▶│   Level 3    │──▶│   Level 4    │
│   Static     │   │ Interaction  │   │  Proactive   │   │  Autonomous  │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
      │                  │                  │                  │
      ▼                  ▼                  ▼                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         EVALUATION                                    │
│  • Relevance  • Groundedness  • Coherence  • Source Compliance       │
└──────────────────────────────────────────────────────────────────────┘
      │                  │                  │                  │
      ▼                  ▼                  ▼                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       LEAK DETECTION                                  │
│  • Missing Info  • Incorrect Response  • Source Mismatch  • Gaps     │
└──────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         REPORT GENERATION                             │
└──────────────────────────────────────────────────────────────────────┘
```

### Custom Pipeline

```python
# Run specific levels only
result = orchestrator.run_pipeline(
    levels=[1, 2],  # Only Level 1 and 2
    quotes=quotes_data,
    interactions=interactions_data
)
```

---

## Performance Metrics

### Target Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| **Relevance** | > 0.75 | High query-response match |
| **Groundedness** | > 0.70 | Strong KB reliance |
| **Coherence** | > 0.75 | Logical consistency |
| **Source Compliance** | > 0.90 | High SoT adherence |
| **Leak Rate** | < 0.10 | Less than 0.1 leaks/query |

### Metric Calculation

```python
from kb_training_system.evaluation_metrics import (
    calculate_relevance,
    calculate_groundedness,
    calculate_coherence,
    calculate_bleu_score
)

# Calculate individual metrics
relevance = calculate_relevance(query, response)
groundedness = calculate_groundedness(response, kb_content)
coherence = calculate_coherence(response)
bleu = calculate_bleu_score(response, reference)

print(f"Relevance: {relevance:.3f}")
print(f"Groundedness: {groundedness:.3f}")
print(f"Coherence: {coherence:.3f}")
print(f"BLEU: {bleu:.3f}")
```

### Dashboard

```python
# Generate performance dashboard
dashboard = orchestrator.generate_dashboard()

print("=== PERFORMANCE DASHBOARD ===")
print(f"Overall Score: {dashboard.overall_score}/100")
print(f"Relevance: {dashboard.relevance:.2f} {'✅' if dashboard.relevance > 0.75 else '⚠️'}")
print(f"Groundedness: {dashboard.groundedness:.2f} {'✅' if dashboard.groundedness > 0.70 else '⚠️'}")
print(f"Coherence: {dashboard.coherence:.2f} {'✅' if dashboard.coherence > 0.75 else '⚠️'}")
print(f"Compliance: {dashboard.compliance:.1%} {'✅' if dashboard.compliance > 0.90 else '⚠️'}")
print(f"Leak Rate: {dashboard.leak_rate:.2f}/query {'✅' if dashboard.leak_rate < 0.10 else '⚠️'}")
```

---

## Usage Guide

### Quick Start

```python
from kb_training_system import TrainingOrchestrator

# Initialize
orchestrator = TrainingOrchestrator(
    knowledge_base_path="Files/",
    quotes_path="quotes/",
    interactions_path="training_data/interactions/",
    social_data_path="training_data/social_media/"
)

# Run complete pipeline
result = orchestrator.run_complete_pipeline(
    quotes=quotes_data,
    interactions=interactions_data,
    social_interactions=social_data
)

# Export report
orchestrator.export_pipeline_report(result, "training_report.md")
```

### Individual Components

#### Evaluator Only

```python
from kb_training_system import KnowledgeBaseEvaluator

evaluator = KnowledgeBaseEvaluator(knowledge_base_path="Files/")
result = evaluator.evaluate_interaction(query, response, sources)
```

#### Leak Detector Only

```python
from kb_training_system import KnowledgeBaseLeakDetector

detector = KnowledgeBaseLeakDetector(knowledge_base_path="Files/")
leaks = detector.detect_leaks_in_interaction(query, response, sources)
```

#### Single Training Level

```python
from kb_training_system import Level1StaticGrounding

trainer = Level1StaticGrounding(knowledge_base_path="Files/")
result = trainer.train_from_quotes(quotes)
```

### Scheduled Training

```python
from kb_auto_scheduler import KBAutoScheduler

scheduler = KBAutoScheduler()

# Schedule daily training
scheduler.schedule_training(
    levels=[1, 2],
    time="02:00",
    frequency="daily"
)

# Schedule weekly full pipeline
scheduler.schedule_full_pipeline(
    time="03:00",
    day="sunday"
)
```

---

## Output Files

| File | Description |
|------|-------------|
| `training_report.md` | Complete pipeline report |
| `evaluation_report.md` | Evaluation benchmark |
| `leak_analysis_report.md` | Leak detection report |
| `leak_history.json` | Historical leak data |

---

## Integration Points

The training system integrates with:

| Component | Purpose |
|-----------|---------|
| Quote Comparison System | `comparar_cotizaciones_vendedoras.py` |
| Social Media Ingestion | `gpt_simulation_agent/agent_social_ingestion.py` |
| Analytics Engine | `gpt_simulation_agent/utils/analytics_engine.py` |
| Source Validator | `panelin_improvements/source_of_truth_validator.py` |

---

## Related Documentation

- [[Knowledge-Base]] - Knowledge base hierarchy
- [[Agents-Overview]] - Agents documentation
- [[Multi-Model-Orchestration]] - Multi-model system

---

<p align="center">
  <a href="[[Knowledge-Base]]">← Knowledge Base</a> |
  <a href="[[Multi-Model-Orchestration]]">Multi-Model Orchestration →</a>
</p>
