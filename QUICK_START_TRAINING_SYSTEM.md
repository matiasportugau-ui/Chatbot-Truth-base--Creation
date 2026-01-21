# Quick Start: KB Training System

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
pip install -r kb_training_system/requirements.txt
```

### Step 2: Run Integration Script

```bash
python3 integrate_training_system.py
```

This script will:
- ✅ Automatically load quotes from your comparison system
- ✅ Load interactions from training data
- ✅ Run appropriate training levels based on available data
- ✅ Generate comprehensive report

### Step 3: Review Results

Check the generated report:
```bash
cat kb_training_system/integrated_training_report.md
```

## 📋 Manual Usage

### Level 1: Train from Quotes

```python
from kb_training_system import Level1StaticGrounding

trainer = Level1StaticGrounding(knowledge_base_path="Files/")
result = trainer.train_from_quotes(quotes)
```

### Level 2: Train from Interactions

```python
from kb_training_system import Level2InteractionEvolution

trainer = Level2InteractionEvolution(knowledge_base_path="Files/")
result = trainer.train_from_interactions(interactions)
```

### Complete Pipeline

```python
from kb_training_system import TrainingOrchestrator

orchestrator = TrainingOrchestrator(knowledge_base_path="Files/")
result = orchestrator.run_complete_pipeline(
    quotes=quotes,
    interactions=interactions,
    social_interactions=social_data
)
```

## 🔍 Evaluate Interactions

```python
from kb_training_system import KnowledgeBaseEvaluator

evaluator = KnowledgeBaseEvaluator(knowledge_base_path="Files/")
result = evaluator.evaluate_interaction(
    query="¿Cuál es el precio de ISODEC 100mm?",
    response="El precio es $46.07 según BMC_Base_Conocimiento_GPT.json",
    sources_consulted=["BMC_Base_Conocimiento_GPT.json"]
)
```

## 🐛 Detect Leaks

```python
from kb_training_system import KnowledgeBaseLeakDetector

detector = KnowledgeBaseLeakDetector(knowledge_base_path="Files/")
leaks = detector.detect_leaks_in_interaction(
    query="¿Cuál es el precio?",
    response="No tengo esa información",
    sources_consulted=[]
)
```

## 📊 Benchmark Architecture

```python
from kb_training_system import KnowledgeBaseEvaluator

evaluator = KnowledgeBaseEvaluator(knowledge_base_path="Files/")
benchmark = evaluator.benchmark_architecture(evaluation_dataset)
```

## 📚 Full Documentation

- **README**: `kb_training_system/README.md`
- **Architecture**: `KB_TRAINING_SYSTEM_ARCHITECTURE.md`
- **Examples**: `kb_training_system/example_usage.py`

## 🎯 Next Steps

1. ✅ Run integration script to get started
2. ✅ Review generated reports
3. ✅ Address critical leaks first
4. ✅ Set up regular training schedule
5. ✅ Monitor evaluation metrics

---

**Ready to improve your KB!** 🚀
