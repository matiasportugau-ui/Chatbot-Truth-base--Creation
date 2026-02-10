#!/usr/bin/env python3
"""
Test Persistence System
=======================

Comprehensive tests for context checkpointing, user profiles,
and personalization engine.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import json
import tempfile
import shutil

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from panelin_persistence import (
    ContextDatabase,
    CheckpointManager,
    ContextRestorer,
    UserProfileDatabase,
    PersonalizationEngine
)


def test_context_database():
    """Test context database operations"""
    print("\n" + "=" * 80)
    print("Testing Context Database")
    print("=" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_context.db")
        
        with ContextDatabase(db_path) as db:
            # Test save checkpoint
            test_context = {
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi!"}
                ],
                "kb_state": {"level": 1},
                "user_info": {"user_id": "test_user"}
            }
            
            checkpoint_id = db.save_checkpoint(
                session_id="test_session_1",
                user_id="test_user",
                context_data=test_context,
                message_count=2
            )
            
            print(f"✅ Checkpoint saved: ID {checkpoint_id}")
            
            # Test retrieve checkpoint
            checkpoint = db.get_latest_checkpoint("test_session_1")
            assert checkpoint is not None, "Checkpoint not found"
            assert checkpoint.session_id == "test_session_1"
            assert checkpoint.message_count == 2
            
            print(f"✅ Checkpoint retrieved: {checkpoint.message_count} messages")
            print(f"   Compression ratio: {checkpoint.compression_ratio:.2%}")
            
            # Test storage stats
            stats = db.get_storage_stats()
            print(f"✅ Storage stats:")
            print(f"   Total checkpoints: {stats['total_checkpoints']}")
            print(f"   DB size: {stats['db_file_size_mb']} MB")
            print(f"   Avg compression: {stats['avg_compression_ratio']:.2%}")
    
    print("\n✅ Context Database tests passed")


def test_checkpoint_manager():
    """Test checkpoint manager automation"""
    print("\n" + "=" * 80)
    print("Testing Checkpoint Manager")
    print("=" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_checkpoints.db")
        
        with CheckpointManager(db_path, message_interval=5, time_interval_minutes=1) as manager:
            # Start session
            manager.start_session("test_session_2", "test_user")
            print("✅ Session started")
            
            # Test message-based triggering
            test_context = {
                "messages": [],
                "kb_state": {},
                "user_info": {"user_id": "test_user"}
            }
            
            # Should not checkpoint yet
            assert not manager.should_checkpoint(), "Should not checkpoint yet"
            
            # Add messages until threshold
            for i in range(5):
                manager.increment_message_count()
            
            # Should checkpoint now
            assert manager.should_checkpoint(), "Should checkpoint after 5 messages"
            print("✅ Message-based trigger working")
            
            # Save checkpoint
            checkpoint_id = manager.save_checkpoint(test_context, force=False)
            assert checkpoint_id is not None, "Checkpoint should be saved"
            print(f"✅ Automatic checkpoint saved: ID {checkpoint_id}")
            
            # Test forced checkpoint
            manager.increment_message_count()
            forced_id = manager.save_checkpoint(test_context, force=True)
            assert forced_id is not None, "Forced checkpoint should be saved"
            print(f"✅ Forced checkpoint saved: ID {forced_id}")
            
            # Get stats
            stats = manager.get_stats()
            print(f"✅ Stats: {stats['total_checkpoints']} checkpoints")
    
    print("\n✅ Checkpoint Manager tests passed")


def test_context_restorer():
    """Test context restoration"""
    print("\n" + "=" * 80)
    print("Testing Context Restorer")
    print("=" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_restore.db")
        
        # Save a checkpoint first
        with ContextDatabase(db_path) as db:
            test_context = {
                "messages": [{"role": "user", "content": "Test"}],
                "kb_state": {"level": 1},
                "user_info": {"user_id": "test_user"}
            }
            
            db.save_checkpoint(
                session_id="test_session_3",
                user_id="test_user",
                context_data=test_context,
                message_count=1
            )
        
        # Restore the checkpoint
        with ContextRestorer(db_path) as restorer:
            restored = restorer.restore_latest_context("test_session_3", validate=True)
            
            assert restored is not None, "Context not restored"
            assert restored["session_id"] == "test_session_3"
            assert restored["message_count"] == 1
            assert len(restored["context"]["messages"]) == 1
            
            print(f"✅ Context restored:")
            print(f"   Messages: {restored['message_count']}")
            print(f"   Compression savings: {restored['compression_info']['savings_percent']}%")
            
            # Test restore options
            options = restorer.get_restore_options("test_session_3")
            assert len(options) > 0, "No restore options found"
            print(f"✅ Restore options: {len(options)} available")
    
    print("\n✅ Context Restorer tests passed")


def test_user_profiles():
    """Test user profile database"""
    print("\n" + "=" * 80)
    print("Testing User Profiles")
    print("=" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_users.db")
        
        with UserProfileDatabase(db_path) as db:
            # Create user
            user = db.create_or_update_user(
                user_id="test_user_1",
                name="Test User",
                email="test@example.com",
                preferences={"theme": "dark", "language": "es"}
            )
            
            print(f"✅ User created: {user.name}")
            print(f"   Preferences: {user.preferences}")
            
            # Record interaction
            db.record_interaction(
                user_id="test_user_1",
                session_id="session_1",
                interaction_type="quotation",
                interaction_data={"product": "ISODEC_EPS", "thickness": "100"}
            )
            
            print("✅ Interaction recorded")
            
            # Get user
            retrieved_user = db.get_user("test_user_1")
            assert retrieved_user is not None, "User not found"
            assert retrieved_user.interaction_count == 1, "Interaction count mismatch"
            
            print(f"✅ User retrieved: {retrieved_user.interaction_count} interactions")
            
            # Update preference
            db.update_preference("test_user_1", "theme", "light")
            updated_user = db.get_user("test_user_1")
            updated_prefs = json.loads(updated_user.preferences)
            assert updated_prefs["theme"] == "light", "Preference not updated"
            
            print("✅ Preference updated successfully")
            
            # Get interactions
            interactions = db.get_user_interactions("test_user_1")
            assert len(interactions) == 1, "Interaction not found"
            assert interactions[0]["interaction_type"] == "quotation"
            
            print(f"✅ Interactions retrieved: {len(interactions)}")
    
    print("\n✅ User Profiles tests passed")


def test_personalization_engine():
    """Test personalization engine"""
    print("\n" + "=" * 80)
    print("Testing Personalization Engine")
    print("=" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_personalization.db")
        
        with PersonalizationEngine(db_path) as engine:
            # Get context for new user
            context = engine.get_user_context("new_user_1")
            assert context["user_id"] == "new_user_1"
            assert context["personalization_level"] == "none"
            
            print(f"✅ New user context created")
            print(f"   Personalization level: {context['personalization_level']}")
            
            # Record some interactions
            for i in range(10):
                engine.db.record_interaction(
                    user_id="new_user_1",
                    session_id=f"session_{i}",
                    interaction_type="quotation" if i % 2 == 0 else "consultation",
                    interaction_data={"test": i}
                )
            
            # Get updated context
            context = engine.get_user_context("new_user_1")
            assert context["interaction_count"] == 10
            assert context["personalization_level"] == "moderate"
            
            print(f"✅ User context updated:")
            print(f"   Interactions: {context['interaction_count']}")
            print(f"   Personalization level: {context['personalization_level']}")
            
            # Get recommendations
            recommendations = engine.get_personalized_recommendations("new_user_1")
            print(f"✅ Recommendations generated: {len(recommendations)}")
            
            # Update learning
            engine.update_user_learning("new_user_1", {
                "preferred_products": ["ISODEC_EPS"],
                "avg_project_size": 100
            })
            
            print("✅ Learning patterns updated")
    
    print("\n✅ Personalization Engine tests passed")


def main():
    """Run all persistence system tests"""
    print("\n" + "=" * 80)
    print("PERSISTENCE SYSTEM TEST SUITE")
    print("=" * 80)
    
    try:
        test_context_database()
        test_checkpoint_manager()
        test_context_restorer()
        test_user_profiles()
        test_personalization_engine()
        
        print("\n" + "=" * 80)
        print("✅ ALL PERSISTENCE TESTS PASSED")
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
