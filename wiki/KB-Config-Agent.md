# KB Config Agent

The KB Config Agent (`gpt_kb_config_agent/`) is a specialized agent for configuring and evolving GPT knowledge bases.

---

## Overview

The KB Config Agent provides:
- Comprehensive KB analysis
- Hierarchy validation
- Conflict detection and resolution
- GPT configuration generation
- KB evolution based on usage patterns
- Health scoring (0-100)

---

## Quick Start

### Command Line

```bash
# Analyze knowledge base
python -m gpt_kb_config_agent.main analyze --kb-path "Files/"

# Generate GPT configuration
python -m gpt_kb_config_agent.main configure \
  --kb-path "Files/" \
  --gpt-name "Panelin Assistant" \
  --use-case quotation

# Evolve knowledge base
python -m gpt_kb_config_agent.main evolve \
  --kb-path "Files/" \
  --strategy auto

# Validate and fix
python -m gpt_kb_config_agent.main validate --kb-path "Files/"
```

### Python API

```python
from gpt_kb_config_agent import GPTKnowledgeBaseAgent

agent = GPTKnowledgeBaseAgent(
    knowledge_base_path="Files/",
    output_path="gpt_configs/"
)

# Analyze
report = agent.analyze_and_review()
print(f"Health Score: {report['health_score']}/100")

# Configure
config = agent.configure_gpt(
    gpt_name="Panelin Assistant",
    use_case="quotation"
)

# Evolve
evolution = agent.evolve_knowledge_base(strategy="auto")

# Validate
validation = agent.validate_and_fix()
```

---

## Components

### KB Analyzer

Analyzes knowledge base structure:

```python
from gpt_kb_config_agent.kb_analyzer import KBAnalyzer

analyzer = KBAnalyzer(kb_path="Files/")
analysis = analyzer.analyze()

print(f"Total files: {analysis['total_files']}")
print(f"Products: {analysis['products_count']}")
print(f"Formulas: {analysis['formulas_count']}")
print(f"Conflicts: {len(analysis['conflicts'])}")
```

### GPT Config Generator

Generates optimal GPT configurations:

```python
from gpt_kb_config_agent.gpt_config_generator import GPTConfigGenerator

generator = GPTConfigGenerator(kb_path="Files/")
config = generator.generate(
    gpt_name="Panelin",
    use_case="quotation",
    model="gpt-4-turbo"
)

# Save to file
generator.save_config(config, "gpt_configs/panelin_config.json")
```

### KB Evolver

Evolves knowledge base based on usage:

```python
from gpt_kb_config_agent.kb_evolver import KBEvolver

evolver = KBEvolver(kb_path="Files/")

# Preview changes (conservative)
preview = evolver.evolve(strategy="conservative")
print(f"Recommended changes: {len(preview['recommendations'])}")

# Apply changes (auto)
result = evolver.evolve(strategy="auto")
print(f"Applied: {result['applied_count']}")
```

---

## KB Hierarchy

The agent enforces this hierarchy:

```
Level 1 (Master) - HIGHEST PRIORITY
├── BMC_Base_Conocimiento_GPT-2.json
└── Purpose: Source of Truth for prices/formulas

Level 2 (Validation) - MEDIUM PRIORITY
├── BMC_Base_Unificada_v4.json
└── Purpose: Cross-reference only

Level 3 (Dynamic) - LOW PRIORITY
├── panelin_truth_bmcuruguay_web_only_v2.json
└── Purpose: Price updates, stock status

Level 4 (Support) - LOWEST PRIORITY
├── Aleros -2.rtf
├── *.csv
└── Purpose: Contextual information
```

---

## Health Score

The health score (0-100) is calculated based on:

| Component | Points | Description |
|-----------|--------|-------------|
| Level 1 Present | 40 | Master file exists |
| Content Richness | 30 | Products, formulas count |
| Structure Clarity | 30 | Clear hierarchy |
| Conflicts | -10 each | Deduction for conflicts |
| Errors | -5 each | Deduction for errors |

### Score Guidelines

| Score | Status | Action |
|-------|--------|--------|
| 90-100 | Excellent | Ready for production |
| 70-89 | Good | Minor improvements |
| 50-69 | Fair | Needs attention |
| 0-49 | Poor | Critical issues |

---

## Evolution Strategies

### Conservative

Only recommends changes, doesn't apply:

```python
evolver.evolve(strategy="conservative")
# Returns recommendations only
```

### Auto

Applies safe changes automatically:

```python
evolver.evolve(strategy="auto")
# Applies low-risk changes
# Reports medium/high-risk for review
```

### Aggressive

Applies all changes (with backup):

```python
evolver.evolve(strategy="aggressive")
# Applies all recommended changes
# Creates automatic backup
```

---

## Use Cases

### General Assistant

```bash
python -m gpt_kb_config_agent.main configure \
  --kb-path Files/ \
  --gpt-name "General Assistant" \
  --use-case general
```

### Quotation System

```bash
python -m gpt_kb_config_agent.main configure \
  --kb-path Files/ \
  --gpt-name "Quotation System" \
  --use-case quotation
```

### Technical Assistant

```bash
python -m gpt_kb_config_agent.main configure \
  --kb-path Files/ \
  --gpt-name "Technical Assistant" \
  --use-case assistant
```

---

## Output Files

| File | Description |
|------|-------------|
| `gpt_configs/kb_analysis_report.json` | Analysis report |
| `gpt_configs/{name}_config.json` | GPT configuration |
| `gpt_configs/kb_evolution_report.json` | Evolution changes |
| `gpt_configs/validation_fix_report.json` | Validation results |

---

## Integration

### With Source Validator

```python
from gpt_kb_config_agent import GPTKnowledgeBaseAgent
from panelin_improvements.source_of_truth_validator import SourceOfTruthValidator

agent = GPTKnowledgeBaseAgent(kb_path="Files/")
validator = SourceOfTruthValidator(kb_path="Files/")

# Validate before evolving
validation = validator.validate_all()
if validation['is_valid']:
    agent.evolve_knowledge_base(strategy="auto")
```

### With Conflict Detector

```python
from panelin_improvements.conflict_detector import ConflictDetector

detector = ConflictDetector(kb_path="Files/")
conflicts = detector.detect_all_conflicts()

if conflicts:
    print(f"Found {len(conflicts)} conflicts")
    for c in conflicts:
        print(f"  - {c.type}: {c.description}")
```

---

## Best Practices

1. **Always analyze before configuring**
2. **Use conservative strategy first**
3. **Review recommendations before applying**
4. **Backup before evolution**
5. **Run validation after changes**

---

## Related

- [[Agents-Overview]] - All agents
- [[Knowledge-Base]] - KB documentation
- [[Training-System]] - Training integration

---

<p align="center">
  <a href="[[GPT-Simulation-Agent]]">← GPT Simulation Agent</a> |
  <a href="[[Files-Organizer-Agent]]">Files Organizer Agent →</a>
</p>
