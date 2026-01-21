# Google Labs Gem Generation

## Overview

The GPT Simulation Agent now includes automatic **Google Labs Gem generation**! After extracting your GPT configuration, the agent can automatically create Google Labs Gems (AI mini-apps) that you can use in Gemini.

## Quick Start

### 1. Run Configuration Extraction

```bash
cd gpt_simulation_agent
python example_usage.py
```

This extracts your GPT configuration from workspace files.

### 2. Generate Gems

```bash
python example_gem_generation.py
```

This will:
- ✅ Generate a main Gem from your extracted configuration
- ✅ Generate multiple Gems for different use cases
- ✅ Generate a Gem based on training data patterns (if available)

## How It Works

### Step 1: Configuration Extraction
The agent scans your workspace and extracts:
- Identity and role information
- Knowledge base files
- System instructions
- Products and formulas
- Business rules
- Actions and capabilities

### Step 2: Gem Type Detection
The agent analyzes your configuration and determines the best Gem type:
- **Automation**: If you have actions enabled
- **Research**: If you have extensive knowledge base
- **Data Processing**: If you have products/formulas
- **Custom**: For other configurations

### Step 3: Description Generation
The agent creates a natural language description that:
- Describes what your Gem does
- Includes capabilities from your configuration
- Specifies the workflow steps

### Step 4: Workflow Design
Using the Build AI Apps agent, it designs a complete workflow with:
- Input nodes
- Processing steps
- Output nodes
- Validation

## Generated Outputs

After running gem generation, you'll find:

```
output/
└── generated_gems/
    ├── generated_gem.json          # Main Gem from config
    ├── all_generated_gems.json     # All generated Gems
    ├── training_based_gem.json     # Gem from training data
    └── generated_gems_summary.json # Summary
```

Each Gem JSON includes:
- `gem_description`: Ready to paste into Google Labs
- `workflow`: Complete workflow structure
- `instrucciones`: Step-by-step instructions
- `valido`: Validation status

## Programmatic Usage

### Generate Single Gem

```python
from agent_system.gpt_simulation_agent import GPTSimulationAgent

agent = GPTSimulationAgent(workspace_path=".")

# Extract configuration
config = agent.configure()

# Generate main Gem
gem_result = agent.generate_gems(generate_multiple=False)

gem = gem_result["gem"]
print(gem["gem_description"])  # Ready for Google Labs!
```

### Generate Multiple Gems

```python
# Generate Gems for different use cases
multiple_gems = agent.generate_gems(generate_multiple=True)

for gem_item in multiple_gems["gems"]:
    print(f"{gem_item['name']}: {gem_item['gem']['gem_description']}")
```

### Generate Gem from Training Data

```python
# Process training data first
agent.process_training_data()

# Generate Gem based on patterns
training_gem = agent.generate_gem_from_training()

print(training_gem["gem_description"])
```

## Using Generated Gems

### Step 1: Get the Description

Open the generated JSON file and copy the `gem_description` field:

```json
{
  "gem_description": "Crea un app que actúa como Panelin, un asistente de cotización..."
}
```

### Step 2: Create Gem in Google Labs

1. Go to [gemini.google.com](https://gemini.google.com)
2. Click **"Gems"** in the left sidebar
3. Click **"New Gem"** in "My Gems from Labs"
4. Paste the `gem_description` into the text box
5. Wait for Gemini to generate the workflow (may take a few minutes)

### Step 3: Test and Refine

1. Click **"Start app"** to test
2. If needed, use conversational commands to adjust
3. Or use the visual editor to modify nodes
4. Save when ready!

## Example Workflow

```python
from agent_system.gpt_simulation_agent import GPTSimulationAgent

# Initialize
agent = GPTSimulationAgent(workspace_path=".")

# 1. Extract configuration
print("Extracting configuration...")
config = agent.configure()
print(f"✓ {config['completion']:.1f}% complete")

# 2. Generate main Gem
print("\nGenerating main Gem...")
gem_result = agent.generate_gems()
gem = gem_result["gem"]

# 3. Get description for Google Labs
description = gem["gem_description"]
print("\n📝 Description for Google Labs:")
print(description)

# 4. Save to file for easy copying
with open("gem_description.txt", "w") as f:
    f.write(description)
print("\n✓ Saved to gem_description.txt")
```

## Integration with Build AI Apps Agent

The Gem generator uses the **Build AI Apps agent** (`agente_build_ai_apps.py`) to:
- Design workflows from descriptions
- Validate workflow structure
- Optimize workflows
- Generate step-by-step instructions

Make sure `agente_build_ai_apps.py` is in the parent directory for full functionality.

## Troubleshooting

### "Build AI Apps agent not available"
- Ensure `agente_build_ai_apps.py` is in the parent directory
- Check that the import path is correct

### "No extracted configuration available"
- Run `agent.configure()` first
- Check that workspace contains GPT configuration files

### Gem description is too generic
- Ensure your configuration files are complete
- Add more details to your knowledge base
- Include specific instructions in system instructions

### Generated Gem doesn't match needs
- Review the generated workflow in the JSON
- Use the remix functionality to modify
- Manually adjust the description and regenerate

## Best Practices

1. **Complete Configuration First**: Ensure your GPT configuration is as complete as possible before generating Gems

2. **Review Generated Descriptions**: Always review the `gem_description` before using in Google Labs

3. **Test Multiple Gems**: Generate multiple Gems to see different approaches

4. **Iterate**: Use the generated Gems as starting points and refine in Google Labs

5. **Combine with Training Data**: Generate Gems from both configuration and training data for best results

## Next Steps

1. ✅ Extract your configuration
2. ✅ Generate Gems
3. ✅ Copy descriptions to Google Labs
4. ✅ Test and refine
5. ✅ Share your Gems!

---

**Happy Gem Building!** 🚀
