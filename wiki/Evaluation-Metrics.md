# Evaluation Metrics

This document details the evaluation metrics used by the Panelin Training System to measure chatbot performance.

---

## Overview

The evaluation system uses industry-standard metrics based on Azure AI and RAG (Retrieval-Augmented Generation) frameworks to ensure consistent, measurable quality.

---

## Core Metrics

### 1. Relevance Score

**Range:** 0.0 - 1.0  
**Target:** > 0.75

Measures how well the response matches the query intent.

```python
from kb_training_system.evaluation_metrics import calculate_relevance

score = calculate_relevance(
    query="¿Cuál es el precio de ISODEC 100mm?",
    response="El precio de ISODEC 100mm es $46.07 USD"
)
# Returns: 0.92
```

**Factors:**
- Keyword overlap
- Semantic similarity
- Query intent matching
- Topic alignment

---

### 2. Groundedness Score

**Range:** 0.0 - 1.0  
**Target:** > 0.70

Measures how much the response relies on KB data vs. hallucination.

```python
from kb_training_system.evaluation_metrics import calculate_groundedness

score = calculate_groundedness(
    response="El precio es $46.07 según BMC_Base_Conocimiento_GPT.json",
    kb_content=kb_data
)
# Returns: 0.95
```

**Factors:**
- Data verification against KB
- Source citation
- Factual accuracy
- Absence of hallucination

---

### 3. Coherence Score

**Range:** 0.0 - 1.0  
**Target:** > 0.75

Measures logical consistency and readability.

```python
from kb_training_system.evaluation_metrics import calculate_coherence

score = calculate_coherence(response)
# Returns: 0.88
```

**Factors:**
- Logical flow
- Sentence structure
- Consistency
- Readability

---

### 4. Source Compliance

**Range:** 0.0 - 1.0  
**Target:** > 0.90

Measures adherence to source of truth hierarchy.

```python
from kb_training_system.evaluation_metrics import calculate_source_compliance

score = calculate_source_compliance(
    response=response,
    sources_consulted=["BMC_Base_Conocimiento_GPT-2.json"],
    expected_source="Level 1"
)
# Returns: 1.0 (Level 1 used correctly)
```

**Factors:**
- Correct hierarchy usage
- Level 1 priority
- Source citation
- Conflict handling

---

## Accuracy Metrics

### BLEU Score

**Range:** 0.0 - 1.0

Measures n-gram overlap with reference responses.

```python
from kb_training_system.evaluation_metrics import calculate_bleu_score

bleu = calculate_bleu_score(
    response="El precio es $46.07",
    reference="El precio de ISODEC 100mm es $46.07 USD"
)
# Returns: 0.65
```

---

### Precision

Measures accuracy of retrieved information.

```
Precision = True Positives / (True Positives + False Positives)
```

---

### Recall

Measures completeness of retrieved information.

```
Recall = True Positives / (True Positives + False Negatives)
```

---

### F1 Score

Harmonic mean of precision and recall.

```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

---

## Composite Metrics

### Overall Score

Weighted combination of all metrics:

```python
overall_score = (
    relevance * 0.25 +
    groundedness * 0.30 +
    coherence * 0.20 +
    source_compliance * 0.25
)
```

### KB Health Score

Measures knowledge base quality (0-100):

| Component | Weight |
|-----------|--------|
| Level 1 Present | 40% |
| Content Richness | 30% |
| Structure Clarity | 30% |
| Conflicts (deduction) | -10% each |

---

## Leak Metrics

### Leak Rate

```
Leak Rate = Total Leaks / Total Queries
```

**Target:** < 0.10 leaks/query

### Leak Types

| Type | Description | Weight |
|------|-------------|--------|
| Missing Information | KB lacks data | 1.0 |
| Incorrect Response | Wrong answer | 2.0 |
| Source Mismatch | Wrong source | 0.5 |
| Coverage Gap | Topic not covered | 0.5 |

---

## Benchmarking

### Run Benchmark

```python
from kb_training_system import KnowledgeBaseEvaluator

evaluator = KnowledgeBaseEvaluator(kb_path="Files/")

# Benchmark dataset
dataset = [
    {
        "query": "¿Precio ISODEC 100mm?",
        "expected_response": "El precio es $46.07",
        "expected_sources": ["BMC_Base_Conocimiento_GPT-2.json"]
    },
    # ... more test cases
]

benchmark = evaluator.benchmark_architecture(dataset)

print(f"Average Relevance: {benchmark.average_relevance:.3f}")
print(f"Average Groundedness: {benchmark.average_groundedness:.3f}")
print(f"Average Coherence: {benchmark.average_coherence:.3f}")
print(f"Source Compliance: {benchmark.source_compliance_rate:.1%}")
```

### Benchmark Report

```
================================================================================
                         BENCHMARK REPORT
================================================================================

Dataset: 50 test cases
Date: 2026-01-23

CORE METRICS:
  Relevance:        0.82 ± 0.05  ✅ (target: 0.75)
  Groundedness:     0.78 ± 0.08  ✅ (target: 0.70)
  Coherence:        0.85 ± 0.04  ✅ (target: 0.75)
  Source Compliance: 92%         ✅ (target: 90%)

ACCURACY METRICS:
  BLEU Score:       0.68
  Precision:        0.89
  Recall:           0.85
  F1 Score:         0.87

LEAK METRICS:
  Leak Rate:        0.08/query  ✅ (target: 0.10)
  Critical Leaks:   2
  Resolved:         48/50 (96%)

OVERALL SCORE: 84/100 ✅

================================================================================
```

---

## Performance Thresholds

| Metric | Poor | Fair | Good | Excellent |
|--------|------|------|------|-----------|
| Relevance | <0.5 | 0.5-0.7 | 0.7-0.85 | >0.85 |
| Groundedness | <0.4 | 0.4-0.6 | 0.6-0.8 | >0.8 |
| Coherence | <0.5 | 0.5-0.7 | 0.7-0.85 | >0.85 |
| Compliance | <70% | 70-85% | 85-95% | >95% |
| Leak Rate | >0.2 | 0.1-0.2 | 0.05-0.1 | <0.05 |

---

## Related

- [[Training-System]] - Training documentation
- [[Knowledge-Base]] - KB documentation
- [[API-Reference]] - Metric APIs

---

<p align="center">
  <a href="[[Training-System]]">← Training System</a> |
  <a href="[[API-Reference]]">API Reference →</a>
</p>
