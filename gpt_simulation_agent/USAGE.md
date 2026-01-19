# GPT Simulation Agent - Usage Guide

## Quick Start

### 1. Installation

First, install the required dependencies:

```bash
cd gpt_simulation_agent
pip install -r requirements.txt
```

### 2. Basic Usage

The simplest way to use the agent is through the example script:

```bash
python example_usage.py
```

This will:
- Scan your workspace for GPT configuration files
- Extract configuration automatically
- Identify gaps and generate extraction guides
- Process any existing training data
- Generate analytics reports

## Programmatic Usage

### Initialize the Agent

```python
from agent_system.gpt_simulation_agent import GPTSimulationAgent

# Point to your workspace (where GPT config files are)
agent = GPTSimulationAgent(
    workspace_path="/path/to/your/workspace",
    output_dir="./output"  # Optional: where to save outputs
)
```

### Phase 1: Self-Configuration

Automatically extract and analyze your GPT configuration:

```python
# Run complete self-configuration
config = agent.configure()

# Results include:
# - diagnosis: What files were found
# - extracted: What was automatically extracted
# - gap_analysis: What's missing
# - completion: Percentage complete

print(f"Configuration {config['completion']:.1f}% complete")
print(f"Found {len(config['diagnosis']['scanned_files'])} files")
```

**Output files:**
- `output/diagnosis.json` - File scan results
- `output/extracted_configs/extracted_config.json` - Extracted configuration
- `output/gap_analysis_report.json` - Missing information analysis
- `output/manual_guides/*.md` - User guides for manual extraction

### Phase 2: Social Media Ingestion (Optional)

Ingest real interactions from Facebook and Instagram:

```python
# Setup: Add API credentials to .env file first
# FACEBOOK_APP_ID=your_app_id
# FACEBOOK_APP_SECRET=your_app_secret
# FACEBOOK_PAGE_ACCESS_TOKEN=your_token
# FACEBOOK_PAGE_ID=your_page_id
# INSTAGRAM_APP_ID=your_app_id
# INSTAGRAM_ACCESS_TOKEN=your_token
# INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id

# Ingest interactions
social_data = agent.ingest_social_media(
    platforms=['facebook', 'instagram'],
    days_back=30,  # How many days to look back
    limit=1000     # Max interactions per platform
)

print(f"Facebook: {social_data['facebook']['count']} interactions")
print(f"Instagram: {social_data['instagram']['count']} interactions")
```

**Output files:**
- `training_data/social_media/facebook/posts/*.json`
- `training_data/social_media/facebook/comments/*.json`
- `training_data/social_media/facebook/messages/*.json`
- `training_data/social_media/instagram/posts/*.json`
- `training_data/social_media/instagram/comments/*.json`

### Phase 3: Process Training Data

Process all training data and generate analytics:

```python
# Process all training data sources
results = agent.process_training_data()

print(f"Total interactions: {results['total_interactions']}")
print(f"Sources: {results['sources']}")

# Generate analytics report
analytics = agent.generate_analytics()
print(f"Question rate: {analytics.get('question_rate', 0):.1f}%")
print(f"Common queries: {analytics.get('common_queries', [])}")
```

**Output files:**
- `output/training_processing_results.json` - Processing results
- `output/analytics_reports/analytics_report.md` - Analytics report

## Advanced Usage

### Using Individual Engines

You can use individual engines directly:

```python
from agent_system.agent_self_diagnosis import SelfDiagnosisEngine
from agent_system.agent_extraction import ExtractionEngine
from agent_system.agent_gap_analysis import GapAnalysisEngine

# Self-diagnosis only
diagnosis_engine = SelfDiagnosisEngine(workspace_path=".")
diagnosis = diagnosis_engine.diagnose()

# Extraction only
extraction_engine = ExtractionEngine(workspace_path=".")
extracted = extraction_engine.extract_all()

# Gap analysis only
gap_engine = GapAnalysisEngine(workspace_path=".")
gaps = gap_engine.analyze()
```

### Custom File Processing

```python
from agent_system.utils.file_scanner import FileScanner
from agent_system.utils.json_parser import JSONParser
from agent_system.utils.markdown_parser import MarkdownParser

# Scan files
scanner = FileScanner(workspace_path=".")
files = scanner.scan()

# Parse specific files
json_parser = JSONParser()
data = json_parser.parse(Path("BMC_Base_Conocimiento_GPT.json"))
products = json_parser.extract_products(data)

md_parser = MarkdownParser()
instructions = md_parser.parse(Path("Instrucciones_Sistema_Panelin.txt"))
```

### Social Media API Clients

```python
from agent_system.utils.facebook_api import FacebookAPIClient
from agent_system.utils.instagram_api import InstagramAPIClient

# Facebook
fb_client = FacebookAPIClient()
posts = fb_client.get_posts(limit=100)
for post in posts:
    normalized = fb_client.normalize_interaction(post, "post")
    print(normalized)

# Instagram
ig_client = InstagramAPIClient()
media = ig_client.get_media(limit=100)
for item in media:
    normalized = ig_client.normalize_interaction(item, "post")
    print(normalized)
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Workspace
WORKSPACE_PATH=/path/to/your/workspace
OUTPUT_DIR=./output

# Facebook API
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_token
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_API_VERSION=v18.0

# Instagram API
INSTAGRAM_APP_ID=your_app_id
INSTAGRAM_APP_SECRET=your_app_secret
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id
INSTAGRAM_API_VERSION=v18.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/agent.log
```

### Workspace Structure

Your workspace should contain GPT configuration files:

```
workspace/
├── BMC_Base_Conocimiento_GPT.json      # Knowledge base (Nivel 1)
├── BMC_Base_Unificada_v4.json         # Validation (Nivel 2)
├── panelin_truth_bmcuruguay_web_only_v2.json  # Dynamic (Nivel 3)
├── Instrucciones_Sistema_Panelin.txt   # System instructions
├── Guia_Crear_GPT_OpenAI_Panelin.md   # Documentation
├── Action_Shopify_Ejemplo_Simple.yaml # Actions
└── ...
```

## Output Structure

After running the agent, you'll have:

```
output/
├── diagnosis.json                      # File scan results
├── extracted_configs/
│   └── extracted_config.json          # Extracted configuration
├── gap_analysis_report.json           # Missing fields analysis
├── manual_guides/                     # User extraction guides
│   ├── identity_personality_tone.md
│   └── ...
├── analytics_reports/
│   └── analytics_report.md            # Analytics report
├── social_ingestion_results.json      # Social media ingestion results
└── training_processing_results.json  # Training data processing results
```

## Common Workflows

### Workflow 1: Initial Configuration

```python
# First time setup - extract everything
agent = GPTSimulationAgent(workspace_path=".")
config = agent.configure()

# Review gap analysis
gaps = config['gap_analysis']
print(f"Missing: {len(gaps['missing_fields'])} fields")

# Check manual guides
# Look in output/manual_guides/ for extraction instructions
```

### Workflow 2: Social Media Training Data

```python
# Ingest social media interactions
agent.ingest_social_media(
    platforms=['facebook', 'instagram'],
    days_back=90,  # Last 3 months
    limit=5000
)

# Process and analyze
results = agent.process_training_data()
analytics = agent.generate_analytics()

# Review analytics
print(analytics['common_queries'])
print(analytics['engagement_metrics'])
```

### Workflow 3: Continuous Updates

```python
# Re-run configuration after updating files
agent = GPTSimulationAgent(workspace_path=".")
config = agent.configure()

# Check if completion improved
if config['completion'] > 80:
    print("Configuration is complete!")
else:
    print(f"Still {100 - config['completion']:.1f}% incomplete")
```

## Troubleshooting

### No files found
- Check that `workspace_path` points to the correct directory
- Ensure files have recognizable names (contain "base_conocimiento", "instrucciones", etc.)

### API errors (Facebook/Instagram)
- Verify API credentials in `.env` file
- Check API permissions in Facebook/Instagram developer console
- Ensure access tokens are valid and not expired

### Extraction errors
- Check file formats (JSON should be valid, Markdown should be readable)
- Review logs in `logs/agent.log` for detailed error messages

### Low completion percentage
- Review `gap_analysis_report.json` to see what's missing
- Check `manual_guides/` for extraction instructions
- Some fields may require manual input

## Next Steps

1. **Review extracted configuration**: Check `output/extracted_configs/extracted_config.json`
2. **Fill gaps**: Use guides in `output/manual_guides/` to complete missing information
3. **Ingest training data**: Set up social media APIs and ingest real interactions
4. **Analyze patterns**: Review analytics reports to understand interaction patterns
5. **Iterate**: Re-run configuration as you add more files or data

## Support

For issues or questions:
- Check logs: `logs/agent.log`
- Review output files in `output/` directory
- Check individual engine documentation in source code
