# Quick Start Guide - GPT Knowledge Base Configuration Agent

## Installation

```bash
cd gpt_kb_config_agent
pip install -r requirements.txt
```

## Basic Usage

### 1. Analyze Your Knowledge Base

First, analyze your knowledge base to understand its current state:

```bash
python -m gpt_kb_config_agent.main analyze --kb-path ../Files/
```

**Output:**
- `gpt_configs/kb_analysis_report.json` - Complete analysis
- Health score (0-100)
- List of files found
- Conflicts detected
- Recommendations

### 2. Generate GPT Configuration

Generate a ready-to-use GPT configuration:

```bash
python -m gpt_kb_config_agent.main configure \
  --kb-path ../Files/ \
  --gpt-name "My Panelin GPT" \
  --use-case assistant
```

**Output:**
- `gpt_configs/My Panelin GPT_config.json` - Complete GPT configuration
- System instructions with hierarchy rules
- Knowledge base configuration
- Capabilities and actions

### 3. Validate Knowledge Base

Check for issues and conflicts:

```bash
python -m gpt_kb_config_agent.main validate --kb-path ../Files/
```

**Output:**
- `gpt_configs/validation_fix_report.json` - Validation report
- List of conflicts
- Auto-fixes applied
- Remaining issues

### 4. Evolve Knowledge Base

Improve your knowledge base:

```bash
python -m gpt_kb_config_agent.main evolve \
  --kb-path ../Files/ \
  --strategy conservative
```

**Output:**
- `gpt_configs/kb_evolution_report.json` - Evolution report
- Recommended changes
- Applied changes (if strategy allows)
- Backup created automatically

## Use Cases

### For Quotation System

```bash
python -m gpt_kb_config_agent.main configure \
  --kb-path ../Files/ \
  --gpt-name "Panelin Quotation System" \
  --use-case quotation
```

### For General Assistant

```bash
python -m gpt_kb_config_agent.main configure \
  --kb-path ../Files/ \
  --gpt-name "Panelin Assistant" \
  --use-case general
```

### For Technical Assistant

```bash
python -m gpt_kb_config_agent.main configure \
  --kb-path ../Files/ \
  --gpt-name "Panelin Technical" \
  --use-case assistant
```

## Python API

```python
from gpt_kb_config_agent import GPTKnowledgeBaseAgent

# Initialize
agent = GPTKnowledgeBaseAgent(
    knowledge_base_path="Files/",
    output_path="gpt_configs/"
)

# Analyze
report = agent.analyze_and_review()
print(f"Health Score: {report['health_score']}")

# Configure
config = agent.configure_gpt(
    gpt_name="My GPT",
    use_case="assistant"
)

# Validate
validation = agent.validate_and_fix()

# Evolve
evolution = agent.evolve_knowledge_base(
    evolution_strategy="auto"
)
```

## Understanding Health Score

- **90-100**: Excellent - Ready for production ✅
- **70-89**: Good - Minor improvements recommended ⚠️
- **50-69**: Fair - Needs attention ⚠️
- **0-49**: Poor - Critical issues need resolution ❌

## Next Steps

1. **Review Analysis Report**: Check `kb_analysis_report.json`
2. **Fix Critical Issues**: Address any validation errors
3. **Generate GPT Config**: Create your GPT configuration
4. **Test Configuration**: Use the generated config in OpenAI
5. **Evolve Periodically**: Run evolution to improve over time

## Troubleshooting

### "Knowledge base path does not exist"
- Make sure the path to your Files folder is correct
- Use absolute path if relative path doesn't work

### "Level 1 file missing"
- Ensure `BMC_Base_Conocimiento_GPT.json` or `BMC_Base_Conocimiento_GPT-2.json` exists
- These are required for GPT operation

### Low Health Score
- Check analysis report for specific issues
- Resolve conflicts
- Add missing content
- Run validation to identify problems

## Files Generated

All outputs are in `gpt_configs/` directory:

- `kb_analysis_report.json` - Complete analysis
- `{gpt_name}_config.json` - GPT configuration
- `kb_evolution_report.json` - Evolution changes
- `validation_fix_report.json` - Validation results
- `backups/` - Automatic backups before evolution

## Support

For more information, see:
- `README.md` - Full documentation
- `example_usage.py` - Code examples
- Analysis reports - Detailed insights
