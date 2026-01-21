# KB Update System - Setup Instructions

## Quick Setup (Recommended)

Run the automated setup script:

```bash
./setup_kb_update_system.sh
```

This script will:
1. ✅ Check if API key is set
2. ✅ Verify dependencies are installed
3. ✅ Test both optimizers
4. ✅ Optionally run first update

---

## Manual Setup

### Step 1: Set API Key

#### Option A: For Current Session
```bash
export OPENAI_API_KEY="your-api-key-here"
```

#### Option B: Permanent (Recommended)
Add to your shell config file:

**For zsh (macOS default):**
```bash
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**For bash:**
```bash
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### Option C: Using .env file
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

Then load it:
```bash
export $(cat .env | xargs)
```

---

### Step 2: Verify Dependencies

```bash
pip install openai loguru schedule
```

Or verify they're installed:
```bash
pip list | grep -E "(openai|loguru|schedule)"
```

---

### Step 3: Test the System

#### Check KB Update Status
```bash
python3 kb_update_optimizer.py --stats
```

Expected output:
```
📊 Update Statistics:
   Hash cache files: 0
   Cached queries: 0
   Changed files: 2
```

#### Check Training Data Status
```bash
python3 training_data_optimizer.py --stats
```

---

### Step 4: Run First Update

```bash
# Update all tiers (only if changed)
python3 kb_update_optimizer.py --tier all

# Or update specific tier
python3 kb_update_optimizer.py --tier level_3
```

---

### Step 5: Set Up Automated Scheduling

#### Option A: Daemon Mode (Simple)
```bash
# Run in background
nohup python3 kb_auto_scheduler.py --daemon > scheduler.log 2>&1 &

# Or use screen/tmux
screen -S kb_scheduler
python3 kb_auto_scheduler.py --daemon
# Press Ctrl+A then D to detach
```

#### Option B: System Cron (Recommended for Production)

Edit crontab:
```bash
crontab -e
```

Add these lines (adjust path as needed):
```cron
# Level 3: Daily at 2 AM
0 2 * * * cd "/Users/matias/Chatbot Truth base  Creation" && python3 kb_update_optimizer.py --tier level_3

# Training: Daily at 4 AM
0 4 * * * cd "/Users/matias/Chatbot Truth base  Creation" && python3 training_data_optimizer.py --process

# Level 2: Weekly on Sunday at 3 AM
0 3 * * 0 cd "/Users/matias/Chatbot Truth base  Creation" && python3 kb_update_optimizer.py --tier level_2

# Patterns: Weekly on Sunday at 5 AM
0 5 * * 0 cd "/Users/matias/Chatbot Truth base  Creation" && python3 training_data_optimizer.py --extract-patterns

# Level 1: Monthly on 1st at 4 AM
0 4 1 * * cd "/Users/matias/Chatbot Truth base  Creation" && python3 kb_update_optimizer.py --tier level_1
```

---

## Verification

After setup, verify everything works:

```bash
# 1. Check system status
python3 kb_update_optimizer.py --stats
python3 training_data_optimizer.py --stats

# 2. Test update (dry run)
python3 kb_update_optimizer.py --tier all

# 3. Test scheduler (one-time run)
python3 kb_auto_scheduler.py --once
```

---

## Troubleshooting

### "OPENAI_API_KEY not set"
- Make sure you've exported the variable
- Check with: `echo $OPENAI_API_KEY`
- If empty, set it using one of the methods above

### "Module not found"
- Install dependencies: `pip install openai loguru schedule`
- Or use: `pip install -r requirements.txt` (if available)

### "File not found" errors
- Check that "Files " directory exists
- Verify KB files are in the correct location
- Run `python3 kb_update_optimizer.py --stats` to see what's detected

### Scheduler not running
- Check logs: `tail -f logs/kb_scheduler_*.log`
- Verify API key is set in the environment where scheduler runs
- Test with `--once` flag first

---

## Next Steps

1. ✅ Run first update
2. ✅ Monitor for a few days
3. ✅ Adjust schedule as needed
4. ✅ Review cost savings

See `KB_UPDATE_QUICKSTART.md` for detailed usage instructions.
