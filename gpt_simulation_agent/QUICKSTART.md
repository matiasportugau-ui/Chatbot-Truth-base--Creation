# Quick Start Guide

## 3-Step Setup

### Step 1: Install Dependencies

```bash
cd gpt_simulation_agent
pip install -r requirements.txt
```

### Step 2: Run the Agent

```bash
python example_usage.py
```

This will automatically:
- ✅ Scan your workspace
- ✅ Extract configuration
- ✅ Identify gaps
- ✅ Generate reports

### Step 3: Review Results

Check the `output/` directory:
- `extracted_configs/extracted_config.json` - What was extracted
- `gap_analysis_report.json` - What's missing
- `manual_guides/` - How to fill gaps

## That's It!

The agent will automatically:
1. Find all GPT configuration files
2. Extract information from JSON, Markdown, YAML files
3. Identify what's missing
4. Generate guides for manual extraction

## Optional: Social Media Ingestion

To ingest real interactions from Facebook/Instagram:

1. **Get API credentials** from Facebook/Instagram Developer Console
2. **Create `.env` file**:
   ```bash
   FACEBOOK_PAGE_ACCESS_TOKEN=your_token
   FACEBOOK_PAGE_ID=your_page_id
   INSTAGRAM_ACCESS_TOKEN=your_token
   INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id
   ```
3. **Run ingestion**:
   ```python
   from agent_system.gpt_simulation_agent import GPTSimulationAgent
   
   agent = GPTSimulationAgent(workspace_path=".")
   agent.ingest_social_media(platforms=['facebook', 'instagram'])
   ```

## Need More Details?

See `USAGE.md` for complete documentation.
