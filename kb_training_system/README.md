# Knowledge Base Training System

Multi-level training system for chatbot knowledge base evolution using quotes, customer interactions, and social media data.

## Architecture

### Four Training Levels

1. **Level 1: Static Grounding** (Documentation & Quotes)
   - Converts existing PDFs, manuals, quotes into searchable KB
   - Forms the "source of truth" foundation
   - Extracts product info, pricing, specifications from quotes

2. **Level 2: Interaction-Driven Evolution** (Customer Support)
   - Uses real-world chat transcripts and service interactions
   - Creates ground truth pairs for evaluation
   - Identifies leaks where KB fails to answer questions

3. **Level 3: Proactive Social & Synthetic Ingestion**
   - Monitors social networks and feedback loops
   - Generates synthetic test cases
   - Updates KB with emerging trends and sentiment

4. **Level 4: Autonomous Agent Feedback Loop**
   - Specialized agents monitor and update KB autonomously
   - Continuous improvement based on performance metrics
   - Self-optimizing based on evaluation results

## Features

### Evaluation System
- **Relevance**: Query-response matching (0-1)
- **Groundedness**: KB data reliance (0-1)
- **Coherence**: Logical consistency (0-1)
- **Accuracy**: BLEU, Precision, Recall, F1 scores
- **Source Compliance**: Source of truth adherence

### Leak Detection
- **Missing Information**: Detects when KB lacks required data
- **Incorrect Response**: Identifies contradictions with ground truth
- **Source Mismatch**: Flags wrong source usage
- **Coverage Gap**: Identifies KB coverage issues

### Benchmarking
- Comprehensive architecture benchmarking
- Performance metrics tracking
- KB coverage analysis
- Instruction effectiveness measurement

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from kb_training_system import TrainingOrchestrator

# Initialize orchestrator
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
    social_interactions=social_data,
    evaluation_dataset=evaluation_data
)

# Export report
orchestrator.export_pipeline_report(result, "training_report.md")
```

## Usage Examples

### Level 1: Train from Quotes

```python
from kb_training_system import Level1StaticGrounding

trainer = Level1StaticGrounding(
    knowledge_base_path="Files/",
    quotes_path="quotes/"
)

result = trainer.train_from_quotes(quotes)
print(f"Added: {result.items_added}, Updated: {result.items_updated}")
```

### Level 2: Train from Interactions

```python
from kb_training_system import Level2InteractionEvolution

trainer = Level2InteractionEvolution(
    knowledge_base_path="Files/",
    interactions_path="training_data/interactions/"
)

result = trainer.train_from_interactions(interactions)
print(f"Patterns: {result.metrics['patterns_identified']}")
```

### Evaluate Interactions

```python
from kb_training_system import KnowledgeBaseEvaluator

evaluator = KnowledgeBaseEvaluator(knowledge_base_path="Files/")

result = evaluator.evaluate_interaction(
    query="¿Cuál es el precio de ISODEC 100mm?",
    response="El precio de ISODEC 100mm es $46.07 según BMC_Base_Conocimiento_GPT.json",
    sources_consulted=["BMC_Base_Conocimiento_GPT.json"]
)

print(f"Relevance: {result.relevance_score}")
print(f"Groundedness: {result.groundedness_score}")
```

### Detect Leaks

```python
from kb_training_system import KnowledgeBaseLeakDetector

detector = KnowledgeBaseLeakDetector(knowledge_base_path="Files/")

leaks = detector.detect_leaks_in_interaction(
    query="¿Cuál es el precio de ISODEC 100mm?",
    response="No tengo esa información en mi base de conocimiento",
    sources_consulted=[]
)

for leak in leaks:
    print(f"Leak: {leak.leak_type}, Severity: {leak.severity}")
```

## Benchmarking

```python
from kb_training_system import KnowledgeBaseEvaluator

evaluator = KnowledgeBaseEvaluator(knowledge_base_path="Files/")

benchmark = evaluator.benchmark_architecture(evaluation_dataset)

print(f"Average Relevance: {benchmark.average_relevance:.3f}")
print(f"Average Groundedness: {benchmark.average_groundedness:.3f}")
print(f"Source Compliance: {benchmark.source_compliance_rate:.1%}")

# Export report
evaluator.export_evaluation_report("evaluation_report.md", benchmark)
```

## Data Formats

### Quotes Format
```json
{
  "product_code": "ISODEC_EPS_100",
  "product_name": "ISODEC EPS 100mm",
  "price": 46.07,
  "currency": "USD",
  "thickness": "100mm",
  "quantity": 10
}
```

### Interactions Format
```json
{
  "query": "¿Cuál es el precio de ISODEC 100mm?",
  "response": "El precio es $46.07",
  "sources": ["BMC_Base_Conocimiento_GPT.json"],
  "timestamp": "2026-01-20T10:00:00",
  "metadata": {
    "is_question": true,
    "platform": "chat"
  }
}
```

### Social Interactions Format
```json
{
  "platform": "facebook",
  "content": "Consulta sobre precio de paneles",
  "timestamp": "2026-01-20T10:00:00",
  "engagement": {
    "likes": 5,
    "replies": 2
  }
}
```

## Evaluation Metrics

### Relevance Score
Measures how well the response matches the query intent.
- **0.0-0.5**: Poor match
- **0.5-0.7**: Moderate match
- **0.7-1.0**: Good match

### Groundedness Score
Measures how much the response relies on KB data vs. hallucination.
- **0.0-0.4**: Not grounded (hallucination risk)
- **0.4-0.7**: Partially grounded
- **0.7-1.0**: Well grounded

### Coherence Score
Measures logical consistency of the response.
- **0.0-0.5**: Incoherent
- **0.5-0.7**: Somewhat coherent
- **0.7-1.0**: Coherent

## Leak Types

1. **Missing Information**: KB lacks required data
2. **Incorrect Response**: Response contradicts ground truth
3. **Source Mismatch**: Wrong source used (e.g., Level 2 instead of Level 1)
4. **Coverage Gap**: KB doesn't cover common query patterns

## Recommendations

The system generates recommendations based on:
- Evaluation results
- Leak analysis
- Training metrics
- Performance benchmarks

## Integration

### With Existing Systems

```python
# Integrate with quote comparison system
from comparar_cotizaciones_vendedoras import comparar_cotizaciones

quotes = comparar_cotizaciones()
orchestrator = TrainingOrchestrator(knowledge_base_path="Files/")
result = orchestrator.run_complete_pipeline(quotes=quotes)
```

### With Social Media Ingestion

```python
# Integrate with social media processor
from gpt_simulation_agent.agent_system.agent_social_ingestion import SocialIngestionEngine

social_engine = SocialIngestionEngine()
social_data = social_engine.ingest_all()

orchestrator = TrainingOrchestrator(knowledge_base_path="Files/")
result = orchestrator.run_complete_pipeline(social_interactions=social_data)
```

## Output Files

- `training_report.md`: Complete pipeline report
- `evaluation_report.md`: Evaluation benchmark report
- `leak_analysis_report.md`: Leak detection report
- `leak_history.json`: Historical leak data

## Best Practices

1. **Run Level 1 first** to establish baseline KB
2. **Use Level 2** to identify and fill knowledge gaps
3. **Leverage Level 3** for trend detection and proactive updates
4. **Enable Level 4** for continuous autonomous improvement
5. **Regular benchmarking** to track KB quality over time
6. **Address critical leaks** immediately
7. **Monitor source compliance** to maintain data integrity

## Troubleshooting

### Low Relevance Scores
- Expand KB with synonyms and alternative phrasings
- Improve query understanding

### Low Groundedness Scores
- Ensure responses cite specific KB sources
- Reduce vague or generic responses

### High Leak Rate
- Add missing information to KB
- Review common query patterns
- Update FAQ sections

### Source Compliance Issues
- Enforce Level 1 (Master) source usage
- Update instructions to prioritize source hierarchy

## License

Part of the Chatbot Truth Base Creation project.
