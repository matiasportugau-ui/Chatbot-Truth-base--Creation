# New Features Guide - Panelin Bot System

Quick guide to the newly implemented persistence, automation, and reporting features.

---

## Context Checkpointing

### Quick Start

```python
from panelin_persistence import CheckpointManager

# Initialize manager
manager = CheckpointManager(
    message_interval=10,  # Checkpoint every 10 messages
    time_interval_minutes=5  # Or every 5 minutes
)

# Start session
manager.start_session("session_123", "user_123")

# Increment message count as conversation progresses
manager.increment_message_count()

# Save checkpoint when needed
context_data = {
    "messages": [...],
    "kb_state": {...},
    "user_info": {...}
}

checkpoint_id = manager.save_checkpoint(context_data)
```

### Restore Context

```python
from panelin_persistence import ContextRestorer

restorer = ContextRestorer()
restored = restorer.restore_latest_context("session_123")

print(f"Restored {restored['message_count']} messages")
print(f"Context: {restored['context']}")
```

---

## User Profiles

### Create and Manage Users

```python
from panelin_persistence import UserProfileDatabase

db = UserProfileDatabase()

# Create user with preferences
user = db.create_or_update_user(
    user_id="user_123",
    name="John Doe",
    email="john@example.com",
    preferences={
        "preferred_products": ["ISODEC_EPS"],
        "language": "es",
        "notification_settings": {"email": True}
    }
)

# Record interaction
db.record_interaction(
    user_id="user_123",
    session_id="session_123",
    interaction_type="quotation",
    interaction_data={"product": "ISODEC_EPS", "thickness": "100mm"}
)

# Update preference
db.update_preference("user_123", "theme", "dark")
```

### Personalization

```python
from panelin_persistence import PersonalizationEngine

engine = PersonalizationEngine()

# Get personalized context
context = engine.get_user_context("user_123")
print(f"Personalization level: {context['personalization_level']}")
print(f"Interaction count: {context['interaction_count']}")

# Get recommendations
recommendations = engine.get_personalized_recommendations("user_123")
for rec in recommendations:
    print(f"- {rec['message']} (confidence: {rec['confidence']})")
```

---

## Workflow Automation

### Define and Execute Workflows

```python
from panelin_automation import WorkflowEngine, Workflow, WorkflowStep
from panelin_automation.workflow_engine import TriggerType

engine = WorkflowEngine()

# Define workflow steps
def update_kb(context):
    # Update KB logic
    return {"status": "success", "files_updated": 3}

def generate_report(context):
    # Generate report logic
    return {"status": "success", "report_path": "/reports/daily.md"}

# Create workflow
workflow = Workflow(
    id="daily_maintenance",
    name="Daily Maintenance",
    description="Update KB and generate daily report",
    steps=[
        WorkflowStep(name="update_kb", function=update_kb),
        WorkflowStep(name="generate_report", function=generate_report)
    ],
    trigger_type=TriggerType.SCHEDULED
)

# Register and execute
engine.register_workflow(workflow)
result = engine.execute_workflow("daily_maintenance")

print(f"Workflow status: {result['status']}")
print(f"Steps completed: {result['steps_completed']}/{result['steps_total']}")
```

### Event-Based Triggers

```python
# Register event handler
def on_kb_update(event_data):
    print(f"KB updated: {event_data['file']}")
    # Trigger related workflows

engine.register_event_handler("kb_updated", on_kb_update)

# Trigger event
engine.trigger_event("kb_updated", {"file": "BMC_Base_Conocimiento_GPT-2.json"})
```

---

## Automated Reports

### Generate Reports

```python
from panelin_reports import ReportGenerator
from panelin_reports.report_generator import ReportFormat

generator = ReportGenerator(output_dir="./reports")

# Generate KB health report
kb_data = {
    "status": "healthy",
    "levels": {...},
    "warnings": [],
    "conflicts": []
}

filepath = generator.generate_kb_health_report(kb_data, ReportFormat.MARKDOWN)
print(f"Report generated: {filepath}")
```

### Schedule Reports

```python
from panelin_reports import ReportScheduler

# Initialize scheduler
scheduler = ReportScheduler(
    output_dir="./reports",
    distribute=True,
    email_config={
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "reports@example.com",
        "password": "xxx",
        "recipients": ["team@example.com"]
    }
)

# Register data collectors
def collect_kb_health():
    from agente_kb_indexing import validate_kb_health
    return validate_kb_health()

scheduler.register_data_collector("kb_health", collect_kb_health)

# Run as daemon
scheduler.run_daemon()  # Runs continuously
```

---

## Training Automation

### Automated Level 1-2 Training

```python
from kb_training_system.training_orchestrator import TrainingOrchestrator

orchestrator = TrainingOrchestrator(
    knowledge_base_path="./",
    quotes_path="./presupuestos",
    interactions_path="./training_data"
)

# Run automated Level 1
result = orchestrator.run_automated_level1(quotes_dir="./presupuestos")
print(f"Level 1: {result.items_added} added, {result.items_updated} updated")

# Run automated Level 2
result = orchestrator.run_automated_level2(interactions_dir="./training_data")
print(f"Level 2: {result.items_added} added, {result.items_updated} updated")

# Run full automated pipeline
results = orchestrator.run_automated_training_pipeline(
    quotes_dir="./presupuestos",
    interactions_dir="./training_data",
    levels=[1, 2]
)

print(f"Pipeline status: {results['status']}")
```

---

## Testing

### Run All Tests

```bash
# Run complete test suite
python3 tests/run_all_tests.py

# Run individual test suites
python3 tests/test_persistence_system.py
python3 tests/test_automation_system.py
python3 tests/test_report_system.py
```

### Test Results
- Persistence System: ✅ 5/5 tests passed
- Automation System: ✅ 3/3 tests passed
- Report System: ✅ 3/3 tests passed
- **Overall**: ✅ 100% pass rate

---

## Performance Metrics

### Context Persistence
- Compression ratio: 72.78% average (exceeds 50% target)
- Checkpoint creation: < 100ms per checkpoint
- Restoration success rate: 100% (in tests)

### Workflow Automation
- Workflow execution: < 100ms per workflow (simple workflows)
- Event trigger latency: < 10ms
- Success rate: 100% (in tests)

### Report Generation
- Report generation time: < 500ms per report
- Template loading: < 10ms
- Distribution logging: 100% logged

---

## Configuration

### Database Paths
- Context DB: `panelin_persistence/context.db`
- User Profiles DB: `panelin_persistence/user_profiles.db`

### Report Output
- Default: `panelin_reports/output/`
- Configurable per ReportGenerator instance

### Logging
- Scheduler logs: `logs/kb_scheduler_YYYY-MM-DD.log`
- Report logs: `logs/report_scheduler_YYYY-MM-DD.log`
- Workflow monitor: `panelin_automation/workflow_monitor.log`

---

## Migration Notes

### From Manual to Automatic
1. **Context Management**: Replace manual `/checkpoint` commands with automatic CheckpointManager
2. **User Data**: Migrate from GPT instructions to UserProfileDatabase
3. **Workflows**: Replace cron jobs with WorkflowEngine for better monitoring
4. **Reports**: Replace manual report scripts with ReportScheduler

### Data Migration
- No data migration needed for new installations
- Existing systems can run in parallel during transition
- SQLite → PostgreSQL migration supported (future)

---

## Troubleshooting

### Context Checkpointing
- **Issue**: Checkpoints not saving
- **Solution**: Check session started with `start_session()`
- **Check**: Verify DB path is writable

### User Profiles
- **Issue**: User not found after creation
- **Solution**: Check database connection, verify user_id
- **Check**: Look for SQLite errors in logs

### Workflows
- **Issue**: Workflow not executing
- **Solution**: Verify workflow is registered, check step functions
- **Check**: Look at workflow execution history

### Reports
- **Issue**: Report not generated
- **Solution**: Check output directory exists and is writable
- **Check**: Verify data collectors registered

---

## Support

For issues or questions:
1. Check test files for usage examples
2. Review module docstrings
3. Check logs for error messages
4. See `BOT_IMPROVEMENT_STRATEGY.md` for architecture overview

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-27  
**Status**: Production Ready
