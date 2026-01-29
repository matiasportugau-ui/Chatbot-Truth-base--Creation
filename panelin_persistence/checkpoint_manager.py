#!/usr/bin/env python3
"""
Checkpoint Manager
==================

Automatic checkpointing logic with configurable intervals,
message-based and time-based triggers.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Callable

from .context_database import ContextDatabase


class CheckpointManager:
    """Manages automatic context checkpointing"""

    def __init__(
        self,
        db_path: Optional[str] = None,
        message_interval: int = 10,
        time_interval_minutes: int = 5,
        auto_cleanup_days: int = 30,
    ):
        """
        Initialize checkpoint manager

        Args:
            db_path: Path to database file
            message_interval: Checkpoint every N messages (default: 10)
            time_interval_minutes: Checkpoint every N minutes (default: 5)
            auto_cleanup_days: Auto-cleanup checkpoints older than N days
                (default: 30)
        """
        self.db = ContextDatabase(db_path)
        self.message_interval = message_interval
        self.time_interval = timedelta(minutes=time_interval_minutes)
        self.auto_cleanup_days = auto_cleanup_days

        # Session tracking
        self.current_session_id: Optional[str] = None
        self.current_user_id: Optional[str] = None
        self.message_count = 0
        self.last_checkpoint_time: Optional[datetime] = None

        # Callbacks
        self.on_checkpoint_saved: Optional[
            Callable[[int, Dict[str, Any]], None]
        ] = None

    def start_session(self, session_id: str, user_id: str):
        """Start a new session or resume existing"""
        self.current_session_id = session_id
        self.current_user_id = user_id
        self.message_count = 0
        self.last_checkpoint_time = datetime.now()

    def should_checkpoint(self) -> bool:
        """Check if a checkpoint should be created"""
        if not self.current_session_id:
            return False

        # Message-based trigger
        if self.message_count >= self.message_interval:
            return True

        # Time-based trigger
        if self.last_checkpoint_time:
            time_since_last = datetime.now() - self.last_checkpoint_time
            if time_since_last >= self.time_interval:
                return True

        return False

    def increment_message_count(self):
        """Increment message counter"""
        self.message_count += 1

    def save_checkpoint(
        self,
        context_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        force: bool = False,
    ) -> Optional[int]:
        """
        Save a checkpoint if conditions are met

        Args:
            context_data: Context data to save
            metadata: Additional metadata
            force: Force checkpoint regardless of conditions

        Returns:
            Checkpoint ID if saved, None if skipped
        """
        if not force and not self.should_checkpoint():
            return None

        if not self.current_session_id or not self.current_user_id:
            raise ValueError(
                "Session not started. Call start_session() first."
            )

        # Add automatic metadata
        checkpoint_metadata = {
            "checkpoint_reason": "forced" if force else "automatic",
            "message_trigger": self.message_count >= self.message_interval,
            "time_trigger": (
                (datetime.now() - self.last_checkpoint_time) >= self.time_interval
                if self.last_checkpoint_time
                else False
            ),
            **(metadata or {}),
        }

        checkpoint_id = self.db.save_checkpoint(
            session_id=self.current_session_id,
            user_id=self.current_user_id,
            context_data=context_data,
            message_count=self.message_count,
            metadata=checkpoint_metadata,
        )

        # Reset counters
        self.message_count = 0
        self.last_checkpoint_time = datetime.now()

        # Callback
        if callable(self.on_checkpoint_saved):
            self.on_checkpoint_saved(checkpoint_id, checkpoint_metadata)

        # Auto-cleanup
        self._auto_cleanup()

        return checkpoint_id

    def _auto_cleanup(self):
        """Automatically cleanup old checkpoints"""
        if self.auto_cleanup_days > 0:
            self.db.cleanup_old_checkpoints(self.auto_cleanup_days)

    def get_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Get the latest checkpoint for current session"""
        if not self.current_session_id:
            return None

        checkpoint = self.db.get_latest_checkpoint(self.current_session_id)
        if not checkpoint:
            return None

        return {
            "id": checkpoint.id,
            "session_id": checkpoint.session_id,
            "user_id": checkpoint.user_id,
            "timestamp": checkpoint.timestamp,
            "message_count": checkpoint.message_count,
            "context": json.loads(checkpoint.context_data),
            "metadata": json.loads(checkpoint.metadata),
            "compression_ratio": checkpoint.compression_ratio,
            "compressed_size_mb": round(
                checkpoint.compressed_size / (1024 * 1024), 3
            ),
            "original_size_mb": round(
                checkpoint.original_size / (1024 * 1024), 3
            ),
        }

    def get_session_history(self, limit: int = 10) -> list[Dict[str, Any]]:
        """Get checkpoint history for current session"""
        if not self.current_session_id:
            return []

        checkpoints = self.db.get_checkpoints_for_session(
            self.current_session_id, limit
        )

        return [
            {
                "id": cp.id,
                "timestamp": cp.timestamp,
                "message_count": cp.message_count,
                "compressed_size_kb": round(cp.compressed_size / 1024, 2),
                "compression_ratio": round(cp.compression_ratio, 3),
                "metadata": json.loads(cp.metadata),
            }
            for cp in checkpoints
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get checkpoint statistics"""
        return self.db.get_storage_stats()

    def close(self):
        """Close database connection"""
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
