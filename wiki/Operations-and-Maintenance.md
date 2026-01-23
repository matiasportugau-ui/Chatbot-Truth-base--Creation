# Operations and Maintenance

## Scheduling
For production-style automation, use the built-in scheduler or cron jobs.

Scheduler (one-time):
```bash
python kb_auto_scheduler.py --once
```

Scheduler (daemon):
```bash
nohup python kb_auto_scheduler.py --daemon > scheduler.log 2>&1 &
```

Cron example:
```
0 2 * * * cd /path/to/repo && python kb_update_optimizer.py --tier level_3
0 4 * * * cd /path/to/repo && python training_data_optimizer.py --process
0 3 * * 0 cd /path/to/repo && python kb_update_optimizer.py --tier level_2
0 5 * * 0 cd /path/to/repo && python training_data_optimizer.py --extract-patterns
0 4 1 * * cd /path/to/repo && python kb_update_optimizer.py --tier level_1
```

## Logs and monitoring
Track updates and training progress:
```bash
python kb_update_optimizer.py --stats
python training_data_optimizer.py --stats
```

If using the scheduler, check log output:
```
logs/kb_scheduler_YYYY-MM-DD.log
```

## Operational checks
- Verify Level 1 KB is present and updated.
- Confirm update tiers are running in the correct cadence.
- Review conflict detection outputs and resolve discrepancies.

## References
- KB_UPDATE_QUICKSTART.md
- KB_UPDATE_TRAINING_STRATEGY.md
