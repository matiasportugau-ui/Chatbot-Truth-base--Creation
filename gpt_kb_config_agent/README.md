# GPT Knowledge Base Configuration and Evolution Agent

Specialized agent for configuring and evolving GPT knowledge bases. Analyzes, validates, and evolves knowledge base files for optimal GPT performance.

## Features

- **Comprehensive Analysis**: Analyzes knowledge base structure, content, and quality
- **Validation**: Validates source of truth hierarchy and detects conflicts
- **Evolution**: Evolves knowledge base based on best practices and usage patterns
- **GPT Configuration**: Generates optimal GPT configurations ready for OpenAI
- **Conflict Resolution**: Detects and helps resolve conflicts between knowledge base levels
- **Health Scoring**: Calculates knowledge base health score (0-100)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Analyze Knowledge Base

```bash
python -m gpt_kb_config_agent.main analyze --kb-path Files/
```

This will:
- Analyze all knowledge base files
- Validate hierarchy structure
- Detect conflicts
- Generate comprehensive report
- Calculate health score

### 2. Generate GPT Configuration

```bash
python -m gpt_kb_config_agent.main configure \
  --kb-path Files/ \
  --gpt-name "Panelin Assistant" \
  --use-case assistant
```

This will generate:
- Complete GPT configuration with system instructions
- Knowledge base hierarchy configuration
- Capabilities and actions
- Ready-to-use JSON file for OpenAI

### 3. Evolve Knowledge Base

```bash
python -m gpt_kb_config_agent.main evolve \
  --kb-path Files/ \
  --strategy auto
```

Strategies:
- `auto`: Automatic evolution with safety checks
- `conservative`: Only recommend changes, don't apply
- `aggressive`: Apply all safe changes automatically

### 4. Validate and Fix

```bash
python -m gpt_kb_config_agent.main validate --kb-path Files/
```

This will:
- Validate source of truth hierarchy
- Detect all conflicts
- Attempt automatic fixes where possible
- Generate fix report

## Knowledge Base Structure

The agent expects the following hierarchy:

### Level 1 (Master) - Source of Truth
- **Files**: `BMC_Base_Conocimiento_GPT.json`, `BMC_Base_Conocimiento_GPT-2.json`
- **Purpose**: Primary source for prices, formulas, and specifications
- **Priority**: HIGHEST - Always use first

### Level 2 (Validation)
- **Files**: `BMC_Base_Unificada_v4.json`
- **Purpose**: Cross-reference and validation only
- **Priority**: MEDIUM - Do not use for direct responses

### Level 3 (Dynamic)
- **Files**: `panelin_truth_bmcuruguay_web_only_v2.json`
- **Purpose**: Price updates and stock status
- **Priority**: LOW - Verify against Level 1

### Level 4 (Support)
- **Files**: `Aleros -2.rtf`, CSV files, Markdown files
- **Purpose**: Contextual support and additional information
- **Priority**: LOWEST - Supplementary only

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

## Output Files

All outputs are saved to `gpt_configs/` directory (or custom `--output-path`):

- `kb_analysis_report.json`: Complete analysis report
- `{gpt_name}_config.json`: GPT configuration file
- `kb_evolution_report.json`: Evolution changes report
- `validation_fix_report.json`: Validation and fix report

## Integration with Existing Tools

The agent integrates with:
- **panelin_improvements**: Uses `SourceOfTruthValidator` and `ConflictDetector`
- **gpt_simulation_agent**: Follows similar patterns for GPT configuration
- **Files folder**: Analyzes original knowledge base files

## API Usage

```python
from gpt_kb_config_agent import GPTKnowledgeBaseAgent

# Initialize agent
agent = GPTKnowledgeBaseAgent(
    knowledge_base_path="Files/",
    output_path="gpt_configs/"
)

# Analyze knowledge base
report = agent.analyze_and_review()

# Generate GPT configuration
config = agent.configure_gpt(
    gpt_name="My GPT",
    use_case="assistant"
)

# Evolve knowledge base
evolution = agent.evolve_knowledge_base(
    evolution_strategy="auto"
)

# Validate and fix
validation = agent.validate_and_fix()
```

## Health Score

The health score (0-100) is calculated based on:
- Presence of Level 1 (Master) files: 40 points
- Content richness (products, formulas): 30 points
- Structure clarity: 30 points
- Deductions for errors and conflicts

**Score Guidelines:**
- 90-100: Excellent - Ready for production
- 70-89: Good - Minor improvements recommended
- 50-69: Fair - Needs attention
- 0-49: Poor - Critical issues need resolution

## Best Practices

1. **Always use Level 1 first**: The agent enforces this in generated configurations
2. **Resolve conflicts**: Use the validation command to detect and fix conflicts
3. **Regular evolution**: Run evolution periodically to improve knowledge base
4. **Backup before evolution**: The agent creates backups automatically
5. **Review recommendations**: Always review evolution recommendations before applying

## Troubleshooting

### Missing Level 1 Files
If Level 1 files are missing, the agent will:
- Flag as critical error
- Recommend adding Level 1 files
- Health score will be significantly reduced

### Conflicts Detected
When conflicts are detected:
- Critical conflicts are flagged for immediate attention
- Warnings are logged for review
- Recommendations are provided for resolution

### Low Health Score
To improve health score:
1. Ensure Level 1 files exist
2. Resolve all conflicts
3. Add missing content (products, formulas)
4. Clarify hierarchy structure

## License

Part of the Panelin GPT Configuration System.
