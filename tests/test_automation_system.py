#!/usr/bin/env python3
"""
Test Automation System
======================

Tests for workflow engine, workflow monitor, and scheduler enhancements.
"""

import sys
from pathlib import Path
import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from panelin_automation import (
    WorkflowEngine,
    Workflow,
    WorkflowStep,
    WorkflowMonitor
)
from panelin_automation.workflow_engine import TriggerType


def test_workflow_engine():
    """Test workflow engine execution"""
    print("\n" + "=" * 80)
    print("Testing Workflow Engine")
    print("=" * 80)
    
    engine = WorkflowEngine()
    
    # Define test workflow steps
    def step1(context):
        context['step1_done'] = True
        return {"status": "success", "value": 42}
    
    def step2(context):
        if not context.get('step1_done'):
            raise ValueError("Step 1 not executed")
        context['step2_done'] = True
        return {"status": "success", "value": 100}
    
    def step3_conditional(context):
        return {"status": "success", "skipped": True}
    
    # Create workflow
    workflow = Workflow(
        id="test_workflow_1",
        name="Test Workflow",
        description="Test workflow with multiple steps",
        steps=[
            WorkflowStep(name="step1", function=step1),
            WorkflowStep(name="step2", function=step2),
            WorkflowStep(
                name="step3",
                function=step3_conditional,
                condition=lambda ctx: ctx.get('skip_step3', False)
            )
        ],
        trigger_type=TriggerType.MANUAL
    )
    
    # Register workflow
    engine.register_workflow(workflow)
    print("✅ Workflow registered")
    
    # Execute workflow
    result = engine.execute_workflow("test_workflow_1", context={})
    
    assert result["status"] == "completed", f"Workflow failed: {result.get('errors')}"
    assert result["steps_completed"] == 2, "Not all steps completed"
    print(f"✅ Workflow executed successfully:")
    print(f"   Status: {result['status']}")
    print(f"   Steps completed: {result['steps_completed']}/{result['steps_total']}")
    print(f"   Duration: {result['duration_seconds']:.2f}s")
    
    # Test stats
    stats = engine.get_workflow_stats()
    assert stats["total_executions"] == 1
    assert stats["successful"] == 1
    print(f"✅ Workflow stats: {stats['success_rate']}% success rate")
    
    print("\n✅ Workflow Engine tests passed")


def test_workflow_monitor():
    """Test workflow monitoring"""
    print("\n" + "=" * 80)
    print("Testing Workflow Monitor")
    print("=" * 80)
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        log_path = f.name
    
    try:
        monitor = WorkflowMonitor(log_path)
        
        # Log a successful execution
        success_result = {
            "execution_id": "exec_1",
            "workflow_id": "test_workflow",
            "status": "completed",
            "duration_seconds": 5.0,
            "steps_completed": 3,
            "steps_total": 3,
            "errors": []
        }
        
        monitor.log_execution(success_result)
        print("✅ Successful execution logged")
        
        # Log a failed execution
        failed_result = {
            "execution_id": "exec_2",
            "workflow_id": "test_workflow",
            "status": "failed",
            "duration_seconds": 2.0,
            "steps_completed": 1,
            "steps_total": 3,
            "errors": ["Step 2 failed"]
        }
        
        monitor.log_execution(failed_result)
        print("✅ Failed execution logged")
        
        # Check alerts
        alerts = monitor.get_alerts(level="error")
        assert len(alerts) > 0, "No error alerts generated"
        print(f"✅ Alerts generated: {len(alerts)} error alerts")
        
        # Get performance report
        report = monitor.get_performance_report()
        assert "test_workflow" in report["workflows"]
        print(f"✅ Performance report generated")
        print(f"   Workflows tracked: {len(report['workflows'])}")
    
    finally:
        Path(log_path).unlink()
    
    print("\n✅ Workflow Monitor tests passed")


def test_event_based_triggers():
    """Test event-based workflow triggers"""
    print("\n" + "=" * 80)
    print("Testing Event-Based Triggers")
    print("=" * 80)
    
    engine = WorkflowEngine()
    
    # Register event handler
    triggered = []
    
    def on_kb_update(event_data):
        triggered.append(event_data)
        return {"status": "handled"}
    
    engine.register_event_handler("kb_updated", on_kb_update)
    print("✅ Event handler registered")
    
    # Trigger event
    result = engine.trigger_event("kb_updated", {"file": "BMC_Base_Conocimiento_GPT-2.json"})
    
    assert len(triggered) == 1, "Event handler not triggered"
    assert result["handlers_executed"] == 1
    print(f"✅ Event triggered and handled")
    print(f"   Handlers executed: {result['handlers_executed']}")
    
    print("\n✅ Event-Based Triggers tests passed")


def main():
    """Run all automation system tests"""
    print("\n" + "=" * 80)
    print("AUTOMATION SYSTEM TEST SUITE")
    print("=" * 80)
    
    try:
        test_workflow_engine()
        test_workflow_monitor()
        test_event_based_triggers()
        
        print("\n" + "=" * 80)
        print("✅ ALL AUTOMATION TESTS PASSED")
        print("=" * 80)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
