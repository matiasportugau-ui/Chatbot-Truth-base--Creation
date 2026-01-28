#!/usr/bin/env python3
"""
Context Restorer
================

Restores conversation context from checkpoints with validation
and integrity checking.
"""

import json
from datetime import datetime
from typing import Dict, Optional, Any, List

from .context_database import ContextDatabase


class ContextRestorer:
    """Restores context from saved checkpoints"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize context restorer
        
        Args:
            db_path: Path to database file
        """
        self.db = ContextDatabase(db_path)
    
    def restore_latest_context(
        self,
        session_id: str,
        validate: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Restore the latest context for a session
        
        Args:
            session_id: Session identifier
            validate: Validate context integrity
        
        Returns:
            Restored context data or None if not found
        """
        checkpoint = self.db.get_latest_checkpoint(session_id)
        if not checkpoint:
            return None
        
        # Decompress and parse context
        try:
            context_data = json.loads(checkpoint.context_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse checkpoint context: {e}")
        
        # Validate if requested
        if validate:
            validation_result = self._validate_context(context_data, checkpoint)
            if not validation_result['valid']:
                raise ValueError(f"Context validation failed: {validation_result['errors']}")
        
        # Build restoration result
        return {
            "checkpoint_id": checkpoint.id,
            "session_id": checkpoint.session_id,
            "user_id": checkpoint.user_id,
            "timestamp": checkpoint.timestamp,
            "message_count": checkpoint.message_count,
            "context": context_data,
            "metadata": json.loads(checkpoint.metadata),
            "restored_at": datetime.now().isoformat(),
            "compression_info": {
                "ratio": checkpoint.compression_ratio,
                "compressed_size_kb": round(checkpoint.compressed_size / 1024, 2),
                "original_size_kb": round(checkpoint.original_size / 1024, 2),
                "savings_percent": round((1 - checkpoint.compression_ratio) * 100, 1)
            }
        }
    
    def _validate_context(
        self,
        context_data: Dict[str, Any],
        checkpoint: Any
    ) -> Dict[str, Any]:
        """
        Validate context integrity
        
        Args:
            context_data: Context data to validate
            checkpoint: Checkpoint metadata
        
        Returns:
            Validation result with valid flag and errors list
        """
        errors = []
        
        # Check required fields
        required_fields = ["messages", "kb_state", "user_info"]
        for field in required_fields:
            if field not in context_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate messages structure
        if "messages" in context_data:
            if not isinstance(context_data["messages"], list):
                errors.append("messages must be a list")
            elif len(context_data["messages"]) != checkpoint.message_count:
                errors.append(f"Message count mismatch: expected {checkpoint.message_count}, got {len(context_data['messages'])}")
        
        # Validate KB state
        if "kb_state" in context_data and not isinstance(context_data["kb_state"], dict):
            errors.append("kb_state must be a dict")
        
        # Validate user info
        if "user_info" in context_data:
            if not isinstance(context_data["user_info"], dict):
                errors.append("user_info must be a dict")
            elif context_data["user_info"].get("user_id") != checkpoint.user_id:
                errors.append(f"User ID mismatch: expected {checkpoint.user_id}, got {context_data['user_info'].get('user_id')}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "checkpoint_id": checkpoint.id,
            "validated_at": datetime.now().isoformat()
        }
    
    def restore_context_at_time(
        self,
        session_id: str,
        timestamp: str
    ) -> Optional[Dict[str, Any]]:
        """Restore context from a specific time"""
        checkpoints = self.db.get_checkpoints_for_session(session_id, limit=100)
        
        # Find closest checkpoint at or before timestamp
        target_time = datetime.fromisoformat(timestamp)
        best_checkpoint = None
        
        for cp in checkpoints:
            cp_time = datetime.fromisoformat(cp.timestamp)
            if cp_time <= target_time:
                if best_checkpoint is None or cp_time > datetime.fromisoformat(best_checkpoint.timestamp):
                    best_checkpoint = cp
        
        if not best_checkpoint:
            return None
        
        context_data = json.loads(best_checkpoint.context_data)
        
        return {
            "checkpoint_id": best_checkpoint.id,
            "session_id": best_checkpoint.session_id,
            "user_id": best_checkpoint.user_id,
            "timestamp": best_checkpoint.timestamp,
            "context": context_data,
            "metadata": json.loads(best_checkpoint.metadata),
            "restored_at": datetime.now().isoformat()
        }
    
    def get_restore_options(self, session_id: str) -> List[Dict[str, Any]]:
        """Get available restore points for a session"""
        checkpoints = self.db.get_checkpoints_for_session(session_id, limit=20)
        
        return [
            {
                "checkpoint_id": cp.id,
                "timestamp": cp.timestamp,
                "message_count": cp.message_count,
                "age_minutes": round((datetime.now() - datetime.fromisoformat(cp.timestamp)).total_seconds() / 60, 1),
                "size_kb": round(cp.compressed_size / 1024, 2)
            }
            for cp in checkpoints
        ]
    
    def close(self):
        """Close database connection"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
