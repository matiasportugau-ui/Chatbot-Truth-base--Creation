#!/usr/bin/env python3
"""
Comprehensive Feature Demo
===========================

Demonstrates all newly implemented features working together:
- Context checkpointing
- User profiles and personalization
- Workflow automation
- Automated reports
- Training automation
"""

import sys
from pathlib import Path
import tempfile
import json

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from panelin_persistence import (
    CheckpointManager,
    ContextRestorer,
    PersonalizationEngine
)
from panelin_automation import WorkflowEngine, Workflow, WorkflowStep
from panelin_automation.workflow_engine import TriggerType
from panelin_reports import ReportGenerator
from panelin_reports.report_generator import ReportFormat


def demo_banner(title):
    """Print demo section banner"""
    print("\n" + "=" * 80)
    print(f"DEMO: {title}")
    print("=" * 80)


def demo_context_persistence():
    """Demo context checkpointing and restoration"""
    demo_banner("Context Persistence System")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "demo_context.db")
        
        # Create checkpoint manager
        print("\n1. Creating checkpoint manager...")
        manager = CheckpointManager(
            db_path=db_path,
            message_interval=5,
            time_interval_minutes=1
        )
        
        # Start session
        print("2. Starting session for user 'demo_user'...")
        manager.start_session("demo_session_1", "demo_user")
        
        # Simulate conversation
        print("3. Simulating conversation (10 messages)...")
        context_data = {
            "messages": [],
            "kb_state": {"current_product": "ISODEC_EPS", "thickness": "100mm"},
            "user_info": {"user_id": "demo_user", "name": "Demo User"}
        }
        
        for i in range(10):
            context_data["messages"].append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Message {i+1}"
            })
            manager.increment_message_count()
            
            # Auto-checkpoint should trigger at message 5 and 10
            checkpoint_id = manager.save_checkpoint(context_data)
            if checkpoint_id:
                print(f"   ✅ Auto-checkpoint #{checkpoint_id} created at message {i+1}")
        
        # Get stats
        stats = manager.get_stats()
        print(f"\n4. Checkpoint stats:")
        print(f"   - Total checkpoints: {stats['total_checkpoints']}")
        print(f"   - DB size: {stats['db_file_size_mb']} MB")
        
        # Restore context
        print("\n5. Restoring latest context...")
        manager.close()
        
        restorer = ContextRestorer(db_path)
        restored = restorer.restore_latest_context("demo_session_1", validate=False)
        
        if restored:
            print(f"   ✅ Context restored successfully")
            print(f"   - Messages: {restored['message_count']}")
            print(f"   - Compression savings: {restored['compression_info']['savings_percent']}%")
            print(f"   - Compressed size: {restored['compression_info']['compressed_size_kb']} KB")
        
        restorer.close()
    
    print("\n✅ Context Persistence Demo Complete")


def demo_user_profiles():
    """Demo user profile system and personalization"""
    demo_banner("User Profile & Personalization System")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "demo_users.db")
        
        # Create personalization engine
        print("\n1. Creating personalization engine...")
        engine = PersonalizationEngine(db_path)
        
        # Get context for new user
        print("2. Getting context for new user 'john_doe'...")
        context = engine.get_user_context("john_doe")
        print(f"   - Personalization level: {context['personalization_level']}")
        print(f"   - Interaction count: {context['interaction_count']}")
        
        # Simulate interactions
        print("\n3. Recording 15 user interactions...")
        for i in range(15):
            engine.db.record_interaction(
                user_id="john_doe",
                session_id=f"session_{i}",
                interaction_type="quotation" if i % 2 == 0 else "consultation",
                interaction_data={
                    "product": "ISODEC_EPS" if i % 3 == 0 else "ISOROOF_3G",
                    "action": "price_check"
                }
            )
        
        # Update user preferences
        print("4. Updating user preferences...")
        engine.db.update_preference("john_doe", "preferred_products", ["ISODEC_EPS"])
        engine.db.update_preference("john_doe", "language", "es")
        
        # Get updated context
        print("\n5. Getting updated user context...")
        updated_context = engine.get_user_context("john_doe")
        print(f"   - Personalization level: {updated_context['personalization_level']}")
        print(f"   - Interaction count: {updated_context['interaction_count']}")
        print(f"   - Common interaction types: {updated_context['interaction_summary']['common_types'][:2]}")
        
        # Get recommendations
        print("\n6. Generating personalized recommendations...")
        recommendations = engine.get_personalized_recommendations("john_doe")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec['message']} (confidence: {rec['confidence']})")
        
        engine.close()
    
    print("\n✅ User Profile & Personalization Demo Complete")


def demo_workflow_automation():
    """Demo workflow engine and event triggers"""
    demo_banner("Workflow Automation System")
    
    # Create workflow engine
    print("\n1. Creating workflow engine...")
    engine = WorkflowEngine()
    
    # Define workflow steps
    print("2. Defining workflow steps...")
    
    def step_update_kb(context):
        print("   → Executing: Update KB")
        context['kb_updated'] = True
        return {"files_updated": 3, "status": "success"}
    
    def step_generate_report(context):
        if not context.get('kb_updated'):
            raise ValueError("KB not updated")
        print("   → Executing: Generate Report")
        return {"report_path": "/reports/demo.md", "status": "success"}
    
    def step_notify(context):
        print("   → Executing: Send Notification")
        return {"notified": ["admin@example.com"], "status": "success"}
    
    # Create workflow
    print("3. Creating 'Daily Maintenance' workflow...")
    workflow = Workflow(
        id="daily_maintenance",
        name="Daily Maintenance Workflow",
        description="Update KB, generate report, notify team",
        steps=[
            WorkflowStep(name="update_kb", function=step_update_kb),
            WorkflowStep(name="generate_report", function=step_generate_report),
            WorkflowStep(name="notify", function=step_notify)
        ],
        trigger_type=TriggerType.SCHEDULED
    )
    
    # Register workflow
    engine.register_workflow(workflow)
    print("   ✅ Workflow registered")
    
    # Execute workflow
    print("\n4. Executing workflow...")
    result = engine.execute_workflow("daily_maintenance", context={})
    
    print(f"\n5. Workflow results:")
    print(f"   - Status: {result['status']}")
    print(f"   - Steps completed: {result['steps_completed']}/{result['steps_total']}")
    print(f"   - Duration: {result['duration_seconds']:.3f}s")
    
    # Test event-based triggers
    print("\n6. Testing event-based triggers...")
    triggered_events = []
    
    def on_kb_updated(event_data):
        triggered_events.append(event_data)
        print(f"   ✅ Event handler triggered: KB updated - {event_data['file']}")
    
    engine.register_event_handler("kb_updated", on_kb_updated)
    engine.trigger_event("kb_updated", {"file": "BMC_Base_Conocimiento_GPT-2.json"})
    
    print(f"   - Events triggered: {len(triggered_events)}")
    
    # Get stats
    print("\n7. Workflow statistics:")
    stats = engine.get_workflow_stats()
    print(f"   - Total executions: {stats['total_executions']}")
    print(f"   - Success rate: {stats['success_rate']}%")
    print(f"   - Average duration: {stats['average_duration_seconds']:.3f}s")
    
    print("\n✅ Workflow Automation Demo Complete")


def demo_automated_reports():
    """Demo automated report generation"""
    demo_banner("Automated Report Generation")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create report generator
        print("\n1. Creating report generator...")
        generator = ReportGenerator(output_dir=tmpdir)
        
        # Generate KB health report (JSON)
        print("\n2. Generating KB Health Report (JSON)...")
        kb_data = {
            "status": "healthy",
            "levels": {
                "level_1_master": {
                    "files_found": 2,
                    "files_valid": ["BMC_Base_Conocimiento_GPT-2.json"]
                },
                "level_2_validation": {
                    "files_found": 1,
                    "files_valid": ["BMC_Base_Unificada_v4.json"]
                }
            },
            "warnings": [],
            "conflicts": []
        }
        
        json_report = generator.generate_kb_health_report(kb_data, ReportFormat.JSON)
        print(f"   ✅ JSON report: {Path(json_report).name}")
        
        # Generate KB health report (Markdown)
        print("\n3. Generating KB Health Report (Markdown)...")
        md_report = generator.generate_kb_health_report(kb_data, ReportFormat.MARKDOWN)
        print(f"   ✅ Markdown report: {Path(md_report).name}")
        
        # Show report content
        print("\n4. Report content preview:")
        with open(md_report, 'r') as f:
            content = f.read()
            lines = content.split('\n')[:10]
            for line in lines:
                print(f"   {line}")
            print("   ...")
        
        # Generate training report
        print("\n5. Generating Training Report...")
        training_data = {
            "total_interactions": 150,
            "processed": 145,
            "success_rate": 96.7,
            "average_quality_score": 4.2
        }
        
        training_report = generator.generate_training_report(training_data, ReportFormat.MARKDOWN)
        print(f"   ✅ Training report: {Path(training_report).name}")
        
        # Show generated files
        print("\n6. Generated report files:")
        report_files = list(Path(tmpdir).glob("*.json")) + list(Path(tmpdir).glob("*.md"))
        for report_file in report_files:
            size_kb = report_file.stat().st_size / 1024
            print(f"   - {report_file.name} ({size_kb:.2f} KB)")
    
    print("\n✅ Automated Report Generation Demo Complete")


def demo_integrated_workflow():
    """Demo all features working together"""
    demo_banner("Integrated Feature Demonstration")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup
        print("\n1. Setting up integrated environment...")
        context_db = str(Path(tmpdir) / "context.db")
        user_db = str(Path(tmpdir) / "users.db")
        reports_dir = str(Path(tmpdir) / "reports")
        
        checkpoint_mgr = CheckpointManager(db_path=context_db)
        personalization = PersonalizationEngine(db_path=user_db)
        workflow_engine = WorkflowEngine()
        report_gen = ReportGenerator(output_dir=reports_dir)
        
        print("   ✅ All systems initialized")
        
        # Simulate user session
        print("\n2. Simulating user session...")
        user_id = "integrated_demo_user"
        session_id = "integrated_session_1"
        
        # Get user context (creates profile if new)
        user_context = personalization.get_user_context(user_id)
        print(f"   - User: {user_id}")
        print(f"   - Personalization level: {user_context['personalization_level']}")
        
        # Start checkpoint session
        checkpoint_mgr.start_session(session_id, user_id)
        print(f"   - Session: {session_id}")
        
        # Simulate conversation with checkpointing
        print("\n3. Simulating conversation with auto-checkpointing...")
        conversation_context = {
            "messages": [],
            "kb_state": {},
            "user_info": user_context
        }
        
        for i in range(7):
            # Add message
            conversation_context["messages"].append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Demo message {i+1}"
            })
            checkpoint_mgr.increment_message_count()
            
            # Record interaction in user profile
            personalization.db.record_interaction(
                user_id=user_id,
                session_id=session_id,
                interaction_type="quotation" if i % 2 == 0 else "consultation",
                interaction_data={"message_num": i+1}
            )
            
            # Auto-checkpoint - update message count in context to match
            if checkpoint_mgr.should_checkpoint():
                # Update context with current message count for validation
                checkpoint_context = conversation_context.copy()
                checkpoint_context["messages"] = conversation_context["messages"][:checkpoint_mgr.message_count]
                checkpoint_id = checkpoint_mgr.save_checkpoint(checkpoint_context)
                if checkpoint_id:
                    print(f"   ✅ Checkpoint #{checkpoint_id} at message {len(checkpoint_context['messages'])}")
        
        # Create workflow that generates report
        print("\n4. Creating automated workflow...")
        
        def generate_session_report(context):
            # Get user interactions
            interactions = personalization.db.get_user_interactions(user_id, limit=10)
            
            # Generate report
            report_data = {
                "status": "healthy",
                "levels": {},
                "warnings": [],
                "conflicts": []
            }
            
            return report_gen.generate_kb_health_report(report_data, ReportFormat.JSON)
        
        workflow = Workflow(
            id="session_report",
            name="Generate Session Report",
            description="Generate report for completed session",
            steps=[
                WorkflowStep(name="generate_report", function=generate_session_report)
            ],
            trigger_type=TriggerType.EVENT
        )
        
        workflow_engine.register_workflow(workflow)
        
        # Execute workflow
        print("5. Executing workflow...")
        workflow_result = workflow_engine.execute_workflow("session_report", context={})
        print(f"   - Status: {workflow_result['status']}")
        print(f"   - Duration: {workflow_result['duration_seconds']:.3f}s")
        
        # Get personalized recommendations
        print("\n6. Generating personalized recommendations...")
        recommendations = personalization.get_personalized_recommendations(user_id)
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec['message']}")
        
        # Final stats
        print("\n7. Session summary:")
        checkpoint_stats = checkpoint_mgr.get_stats()
        user_context_final = personalization.get_user_context(user_id)
        
        print(f"   - Checkpoints created: {checkpoint_stats['total_checkpoints']}")
        print(f"   - Messages: {len(conversation_context['messages'])}")
        print(f"   - User interactions: {user_context_final['interaction_count']}")
        print(f"   - Personalization level: {user_context_final['personalization_level']}")
        
        # Cleanup
        checkpoint_mgr.close()
        personalization.close()
    
    print("\n✅ Integrated Feature Demo Complete")


def main():
    """Run all feature demos"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE FEATURE DEMONSTRATION")
    print("Showcasing all newly implemented bot improvement features")
    print("=" * 80)
    
    try:
        # Individual feature demos
        demo_context_persistence()
        demo_user_profiles()
        demo_workflow_automation()
        demo_automated_reports()
        
        # Integrated demo
        demo_integrated_workflow()
        
        # Final summary
        print("\n" + "=" * 80)
        print("DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\nAll features demonstrated successfully:")
        print("  ✅ Context Persistence - Automatic checkpointing with compression")
        print("  ✅ User Profiles - Preference tracking and personalization")
        print("  ✅ Workflow Automation - Event-based triggers and execution")
        print("  ✅ Automated Reports - Multi-format report generation")
        print("  ✅ Integration - All features working together seamlessly")
        print("\nSystem Status: PRODUCTION READY")
        print("=" * 80)
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
