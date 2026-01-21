# KB Update System - Quick Reference

## 🔑 Essential Commands

### Setup
```bash
# Set API key (current session)
export OPENAI_API_KEY="your-api-key-here"

# Run automated setup
./setup_kb_update_system.sh
```

### Check Status
```bash
# KB update status
python3 kb_update_optimizer.py --stats

# Training data status
python3 training_data_optimizer.py --stats
```

### Run Updates
```bash
# Update all tiers (only if changed)
python3 kb_update_optimizer.py --tier all

# Update specific tier
python3 kb_update_optimizer.py --tier level_1
python3 kb_update_optimizer.py --tier level_2
python3 kb_update_optimizer.py --tier level_3

# Force update (even if unchanged)
python3 kb_update_optimizer.py --tier all --force
```

### Training Data
```bash
# Process new training data
python3 training_data_optimizer.py --process

# Extract patterns (weekly)
python3 training_data_optimizer.py --extract-patterns

# Process specific source
python3 training_data_optimizer.py --process --source social_media
```

### Automated Scheduler
```bash
# Run once (testing)
python3 kb_auto_scheduler.py --once

# Run as daemon
python3 kb_auto_scheduler.py --daemon

# Test schedule configuration
python3 kb_auto_scheduler.py --test
```

---

## 📅 Recommended Schedule

| Task | Frequency | Time | Command |
|------|-----------|------|---------|
| Level 3 Update | Daily | 2 AM | `kb_update_optimizer.py --tier level_3` |
| Training Process | Daily | 4 AM | `training_data_optimizer.py --process` |
| Level 2 Update | Weekly (Sun) | 3 AM | `kb_update_optimizer.py --tier level_2` |
| Pattern Extraction | Weekly (Sun) | 5 AM | `training_data_optimizer.py --extract-patterns` |
| Level 1 Update | Monthly (1st) | 4 AM | `kb_update_optimizer.py --tier level_1` |

---

## 🔍 Monitoring

```bash
# View scheduler logs
tail -f logs/kb_scheduler_$(date +%Y-%m-%d).log

# Check cache directory
ls -la .kb_update_cache/
ls -la .training_cache/
```

---

## 💡 Tips

1. **First Run:** Always test with `--stats` before running updates
2. **API Key:** Set it permanently in `~/.zshrc` or `~/.bashrc`
3. **Cron:** Use cron for production (more reliable than daemon)
4. **Monitoring:** Check logs daily for the first week
5. **Costs:** Monitor API usage to verify savings

---

## 📚 Full Documentation

- **Quick Start:** `KB_UPDATE_QUICKSTART.md`
- **Setup Guide:** `SETUP_INSTRUCTIONS.md`
- **Full Strategy:** `KB_UPDATE_TRAINING_STRATEGY.md`
- **Summary:** `KB_UPDATE_SUMMARY.md`
