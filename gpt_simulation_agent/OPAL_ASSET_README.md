# Opal Asset - GPT Simulation Agent Configuration

## Overview

This Opal document format asset contains complete configuration for the **GPT Simulation Agent** with all functions, workflows, and system instructions needed to automatically construct and configure the agent in Google Labs.

## File Structure

- **`opal_gpt_simulation_agent_config.json`** - Main Opal document (upload this file)
- **`generate_opal_asset.py`** - Script to regenerate the asset
- **`OPAL_ASSET_README.md`** - This documentation

## What's Included

### 1. System Instructions
Complete system instructions that configure the GPT Simulation Agent with:
- Main agent orchestrator description
- All capabilities listed
- Complete function definitions with parameters and return types

### 2. Function Definitions
Five core functions are defined:
- **`configure`** - Self-configuration with workspace scanning
- **`ingest_social_media`** - Social media data ingestion
- **`process_training_data`** - Training data processing and analytics
- **`generate_gems`** - Gem generation from configurations
- **`generate_gem_from_training`** - Gem generation from training patterns

### 3. Workflows
Six complete workflows included:

#### Main Workflow: GPT Simulation Agent
- **6 nodes** with complete orchestration
- Self-diagnosis → Extraction → Gap Analysis → Gem Generation → Results
- Fully validated and ready to use

#### Gem Workflows (5 specialized Gems):
1. **Main Assistant Gem** - Intelligence-based assistant
2. **Quotation System Gem** - 5-phase quotation process
3. **Training & Analytics Gem** - Training data processing
4. **Architecture Analysis Gem** - System architecture analysis
5. **Capacity Assessment Gem** - Capacity evaluation

### 4. Knowledge Base Configuration
- Hierarchical knowledge base structure
- Source of truth configuration
- Conflict resolution rules

### 5. Tools Configuration
- Available tools (Google Search, Code Interpreter, File Upload)
- Tool-specific configurations
- Enable/disable settings

## How to Use

### Method 1: Direct Upload (If Supported)

1. Go to [gemini.google.com](https://gemini.google.com)
2. Click **"Gems"** in the left sidebar
3. Click **"New Gem"** in "My Gems from Labs"
4. Look for **"Import"** or **"Upload"** option
5. Upload `opal_gpt_simulation_agent_config.json`
6. The system will automatically configure all workflows

### Method 2: Manual Configuration

1. Open `opal_gpt_simulation_agent_config.json`
2. Copy the `system_instructions` section
3. Go to Google Labs and create a new Gem
4. Paste the system instructions in the "Instructions" field
5. Use the workflow descriptions to create workflows manually

### Method 3: Workflow-by-Workflow

1. For each workflow in the `workflows` array:
   - Copy the workflow description
   - Create a new Gem in Google Labs
   - Paste the description
   - Let Gemini generate the workflow
   - Configure using the node definitions provided

## Workflow Structure

Each workflow includes:

```json
{
  "workflow_id": "unique_id",
  "name": "Workflow Name",
  "description": "Complete description",
  "type": "automation|research|content|data_processing|analysis",
  "nodes": [
    {
      "id": "node_id",
      "type": "input|search|process|transform|generate|analyze|output",
      "name": "Node Name",
      "description": "What this node does",
      "configuration": {
        // Node-specific configuration
      },
      "connections": [
        {
          "target": "next_node_id",
          "type": "sequential"
        }
      ]
    }
  ],
  "validation": {
    "valid": true/false,
    "errors": [],
    "warnings": []
  }
}
```

## Node Types

- **input** - Receives user input
- **search** - Performs web search or knowledge base lookup
- **process** - Processes data using AI models
- **transform** - Transforms data format
- **generate** - Generates content
- **analyze** - Analyzes data and extracts insights
- **output** - Presents final results

## Function Definitions

All GPT Simulation Agent functions are documented with:
- Complete descriptions
- Parameter types and requirements
- Return value specifications
- Default values where applicable

## Knowledge Base

The asset includes knowledge base hierarchy:
- **Level 1 (Master)**: Primary source of truth
- **Level 2 (Validation)**: Validation data
- **Level 3 (Dynamic)**: Dynamic/real-time data
- **Level 4 (Support)**: Supporting documentation

## Tools Available

- **Google Search**: Web search capabilities
- **Code Interpreter**: Python/JavaScript execution
- **File Upload**: Support for multiple file formats
- **Knowledge Base Access**: Hierarchical knowledge retrieval

## Validation

All workflows are validated for:
- Presence of input nodes
- Presence of output nodes
- Valid connections between nodes
- Complete node configurations

## Regenerating the Asset

To regenerate the asset with updated data:

```bash
cd gpt_simulation_agent
python3 generate_opal_asset.py
```

This will:
- Load latest Codex analysis results
- Enhance workflow nodes
- Generate complete Opal document
- Save to `opal_gpt_simulation_agent_config.json`

## Troubleshooting

### Workflow Validation Errors
- If a workflow shows validation errors, check that input/output nodes are present
- The generator automatically adds missing input nodes
- Re-run `generate_opal_asset.py` to fix issues

### Import Issues
- If direct upload doesn't work, use Method 2 (Manual Configuration)
- Copy system instructions and workflow descriptions separately
- Create workflows one at a time

### Function Definitions
- All functions are documented in the `system_instructions.function_definitions` section
- Use these definitions to configure the agent in Google Labs
- Parameters and return types are clearly specified

## Next Steps

1. ✅ Upload `opal_gpt_simulation_agent_config.json` to Google Labs
2. ✅ Configure system instructions
3. ✅ Test main workflow
4. ✅ Test individual Gem workflows
5. ✅ Customize as needed

---

**Ready to configure your GPT Simulation Agent in Google Labs!** 🚀
