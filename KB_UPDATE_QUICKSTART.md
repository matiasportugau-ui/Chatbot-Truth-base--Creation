# Knowledge Base Update & Training - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install openai loguru schedule
```

### Step 2: Set Environment Variables

```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_ASSISTANT_ID="asst_7LdhJMasW5HHGZh0cgchTGkX"  # Optional, has default
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
OPENAI_ASSISTANT_ID=asst_7LdhJMasW5HHGZh0cgchTGkX
```

### Step 3: Test the System

#### Test KB Updates
```bash
# Check which files need updating
python kb_update_optimizer.py --stats

# Update all tiers (only if changed)
python kb_update_optimizer.py --tier all

# Force update specific tier
python kb_update_optimizer.py --tier level_3 --force
```

#### Test Training Data Processing
```bash
# Check training data statistics
python training_data_optimizer.py --stats

# Process new training data only
python training_data_optimizer.py --process

# Extract patterns (weekly operation)
python training_data_optimizer.py --extract-patterns
```

### Step 4: Run Automated Scheduler

#### Option A: Run Once (Testing)
```bash
python kb_auto_scheduler.py --once
```

#### Option B: Run as Daemon (Production)
```bash
# Run in background
nohup python kb_auto_scheduler.py --daemon > scheduler.log 2>&1 &

# Or use screen/tmux
screen -S kb_scheduler
python kb_auto_scheduler.py --daemon
# Press Ctrl+A then D to detach
```

#### Option C: Use System Cron (Recommended for Production)
```bash
# Edit crontab
crontab -e

# Add these lines:
# Level 3: Daily at 2 AM
0 2 * * * cd /path/to/project && python kb_update_optimizer.py --tier level_3

# Training: Daily at 4 AM
0 4 * * * cd /path/to/project && python training_data_optimizer.py --process

# Level 2: Weekly on Sunday at 3 AM
0 3 * * 0 cd /path/to/project && python kb_update_optimizer.py --tier level_2

# Patterns: Weekly on Sunday at 5 AM
0 5 * * 0 cd /path/to/project && python training_data_optimizer.py --extract-patterns

# Level 1: Monthly on 1st at 4 AM
0 4 1 * * cd /path/to/project && python kb_update_optimizer.py --tier level_1
```

---

## 📊 Expected Results

### Cost Savings
- **Before:** $380-790/month
- **After:** $169-338/month
- **Savings:** 55-57% ($211-452/month)

### Update Efficiency
- **Level 1:** Only uploads when file hash changes (95% savings)
- **Level 2:** Only uploads when conflicts detected (85% savings)
- **Level 3:** Incremental updates, only changed products (70-90% savings)

### Training Efficiency
- **Processing:** Only processes new data (80-95% savings)
- **Patterns:** Local processing first, API only when needed (70% savings)

---

## 🔍 Monitoring

### Check Update Statistics
```bash
python kb_update_optimizer.py --stats
```

Output:
```
📊 Update Statistics:
   Hash cache files: 4
   Cached queries: 150
   Changed files: 1
      - panelin_truth_bmcuruguay_web_only_v2.json (level_3_dynamic)
```

### Check Training Statistics
```bash
python training_data_optimizer.py --stats
```

Output:
```
📊 Training Data Processing Statistics:
   Training data dir: training_data
   Cached patterns: True
   
   Last processed:
      social_media: 2026-01-20T10:30:00
      quotes: 2026-01-20T10:30:00
   
   Interaction counts:
      social_media: 1250
      social_media_new: 0
      social_media_processed: 1250
```

### View Logs
```bash
# View latest scheduler log
tail -f logs/kb_scheduler_$(date +%Y-%m-%d).log

# View all logs
ls -lh logs/
```

---

## 🛠️ Troubleshooting

### Issue: "OPENAI_API_KEY not set"
**Solution:** Set environment variable or create `.env` file

### Issue: "File not found"
**Solution:** Check that `Files/` directory exists with KB files

### Issue: "No new data" (but you know there is)
**Solution:** Check timestamps in interactions match expected format

### Issue: Scheduler not running
**Solution:** 
- Check logs in `logs/` directory
- Verify schedule times are correct
- Test with `--once` flag first

---

## 📈 Next Steps

1. **Week 1:** Run manually to verify everything works
2. **Week 2:** Set up cron jobs or daemon
3. **Week 3:** Monitor cost savings and adjust schedule as needed

---

## 💡 Tips

1. **Start with manual runs** to understand the system
2. **Monitor the first week** to see actual savings
3. **Adjust schedule** based on your update frequency needs
4. **Use `--force` sparingly** - only when you need to override hash checking
5. **Check logs regularly** to ensure everything is working

---

## 📚 Full Documentation

See `KB_UPDATE_TRAINING_STRATEGY.md` for complete strategy and implementation details.
