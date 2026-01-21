# 📤 Upload Instructions - Opal Asset for Google Labs

## ✅ Asset Ready

**File**: `opal_gpt_simulation_agent_config.json` (14,142 bytes)

This file contains complete configuration for GPT Simulation Agent with:
- ✅ 6 complete workflows
- ✅ 5 function definitions
- ✅ System instructions
- ✅ Knowledge base configuration
- ✅ Tools configuration

## 🚀 Upload Methods

### Method 1: Direct JSON Upload (Recommended)

1. **Open Google Labs**
   - Go to [gemini.google.com](https://gemini.google.com)
   - Click **"Gems"** in left sidebar
   - Click **"New Gem"** in "My Gems from Labs"

2. **Upload File**
   - Look for **"Import"**, **"Upload"**, or **"Load from file"** option
   - Select `opal_gpt_simulation_agent_config.json`
   - Wait for import to complete

3. **Verify Configuration**
   - Check that system instructions are loaded
   - Verify workflows are available
   - Test main workflow

### Method 2: Copy System Instructions

If direct upload is not available:

1. **Open the JSON file**
   ```bash
   cat gpt_simulation_agent/opal_gpt_simulation_agent_config.json
   ```

2. **Copy System Instructions**
   - Find the `system_instructions` section
   - Copy the `main_agent` description
   - Copy all `function_definitions`

3. **Paste in Google Labs**
   - Create new Gem
   - Paste in "Instructions" field
   - Configure functions using the definitions

### Method 3: Workflow-by-Workflow

For each workflow in the asset:

1. **Extract Workflow Description**
   - Open JSON file
   - Find workflow in `workflows` array
   - Copy the `description` field

2. **Create Gem in Google Labs**
   - New Gem → Paste description
   - Let Gemini generate workflow
   - Configure nodes using provided definitions

## 📋 What Gets Configured

### System Instructions
- Main agent orchestrator description
- All capabilities listed
- Function definitions with parameters

### Workflows Available
1. **GPT Simulation Agent - Main** (6 nodes)
2. **Main Assistant Gem** (2 nodes)
3. **Quotation System Gem** (2 nodes)
4. **Training & Analytics Gem** (2 nodes)
5. **Architecture Analysis Gem** (2 nodes)
6. **Capacity Assessment Gem** (2 nodes)

### Functions Configured
- `configure()` - Self-configuration
- `ingest_social_media()` - Social media ingestion
- `process_training_data()` - Training processing
- `generate_gems()` - Gem generation
- `generate_gem_from_training()` - Training-based Gems

## 🔍 File Location

```
gpt_simulation_agent/
└── opal_gpt_simulation_agent_config.json  ← Upload this file
```

## ✅ Verification

After upload, verify:
- [ ] System instructions are loaded
- [ ] All 5 functions are available
- [ ] Main workflow is accessible
- [ ] Gem workflows are listed
- [ ] Knowledge base configuration is set
- [ ] Tools are enabled

## 🎯 Quick Start

1. **Upload**: `opal_gpt_simulation_agent_config.json`
2. **Test**: Run main workflow with a workspace path
3. **Verify**: Check that configuration extraction works
4. **Generate**: Test Gem generation function
5. **Customize**: Adjust as needed

---

**Ready to upload and start working!** 🚀
