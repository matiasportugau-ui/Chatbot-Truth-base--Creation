#!/usr/bin/env python3
"""
Context Database
================

SQLite database for storing conversation context, checkpoints, and session data.
Supports automatic compression, versioning, and efficient retrieval.
"""

import sqlite3
import json
import zlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ContextCheckpoint:
    """Represents a context checkpoint"""
    id: Optional[int] = None
    session_id: str = ""
    user_id: str = ""
    timestamp: str = ""
    message_count: int = 0
    context_data: str = ""  # JSON string
    compressed_size: int = 0
    original_size: int = 0
    compression_ratio: float = 0.0
    metadata: str = "{}"  # JSON string


class ContextDatabase:
    """SQLite database for context persistence"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize context database
        
        Args:
            db_path: Path to SQLite database file. Defaults to panelin_persistence/context.db
        """
        if db_path is None:
            db_path = str(Path(__file__).parent / "context.db")
        
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database schema if it doesn't exist"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Create checkpoints table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                message_count INTEGER NOT NULL,
                context_data BLOB NOT NULL,
                compressed_size INTEGER NOT NULL,
                original_size INTEGER NOT NULL,
                compression_ratio REAL NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id 
            ON checkpoints(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id 
            ON checkpoints(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON checkpoints(timestamp DESC)
        """)
        
        # Create sessions table for session metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                start_time TEXT NOT NULL,
                last_checkpoint_time TEXT,
                total_messages INTEGER DEFAULT 0,
                total_checkpoints INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def save_checkpoint(
        self,
        session_id: str,
        user_id: str,
        context_data: Dict[str, Any],
        message_count: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Save a context checkpoint
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier
            context_data: Context data to save
            message_count: Number of messages in this checkpoint
            metadata: Additional metadata
        
        Returns:
            Checkpoint ID
        """
        # Serialize and compress context data
        context_json = json.dumps(context_data, ensure_ascii=False)
        context_bytes = context_json.encode('utf-8')
        original_size = len(context_bytes)
        
        compressed_data = zlib.compress(context_bytes, level=9)
        compressed_size = len(compressed_data)
        compression_ratio = compressed_size / original_size if original_size > 0 else 0.0
        
        timestamp = datetime.now().isoformat()
        metadata_json = json.dumps(metadata or {}, ensure_ascii=False)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO checkpoints 
            (session_id, user_id, timestamp, message_count, context_data, 
             compressed_size, original_size, compression_ratio, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            user_id,
            timestamp,
            message_count,
            compressed_data,
            compressed_size,
            original_size,
            compression_ratio,
            metadata_json
        ))
        
        self.conn.commit()
        
        # Update session metadata
        self._update_session_metadata(session_id, user_id, timestamp, message_count)
        
        return cursor.lastrowid
    
    def _update_session_metadata(
        self,
        session_id: str,
        user_id: str,
        checkpoint_time: str,
        message_count: int
    ):
        """Update session metadata"""
        cursor = self.conn.cursor()
        
        # Check if session exists
        cursor.execute("""
            SELECT session_id FROM sessions WHERE session_id = ?
        """, (session_id,))
        
        if cursor.fetchone():
            # Update existing session
            cursor.execute("""
                UPDATE sessions 
                SET last_checkpoint_time = ?,
                    total_messages = ?,
                    total_checkpoints = total_checkpoints + 1
                WHERE session_id = ?
            """, (checkpoint_time, message_count, session_id))
        else:
            # Create new session
            cursor.execute("""
                INSERT INTO sessions 
                (session_id, user_id, start_time, last_checkpoint_time, 
                 total_messages, total_checkpoints)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (session_id, user_id, checkpoint_time, checkpoint_time, message_count))
        
        self.conn.commit()
    
    def get_latest_checkpoint(self, session_id: str) -> Optional[ContextCheckpoint]:
        """Get the most recent checkpoint for a session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM checkpoints 
            WHERE session_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (session_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Decompress context data
        compressed_data = row['context_data']
        decompressed_data = zlib.decompress(compressed_data)
        context_json = decompressed_data.decode('utf-8')
        
        return ContextCheckpoint(
            id=row['id'],
            session_id=row['session_id'],
            user_id=row['user_id'],
            timestamp=row['timestamp'],
            message_count=row['message_count'],
            context_data=context_json,
            compressed_size=row['compressed_size'],
            original_size=row['original_size'],
            compression_ratio=row['compression_ratio'],
            metadata=row['metadata']
        )
    
    def get_checkpoints_for_session(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[ContextCheckpoint]:
        """Get recent checkpoints for a session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM checkpoints 
            WHERE session_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (session_id, limit))
        
        checkpoints = []
        for row in cursor.fetchall():
            compressed_data = row['context_data']
            decompressed_data = zlib.decompress(compressed_data)
            context_json = decompressed_data.decode('utf-8')
            
            checkpoints.append(ContextCheckpoint(
                id=row['id'],
                session_id=row['session_id'],
                user_id=row['user_id'],
                timestamp=row['timestamp'],
                message_count=row['message_count'],
                context_data=context_json,
                compressed_size=row['compressed_size'],
                original_size=row['original_size'],
                compression_ratio=row['compression_ratio'],
                metadata=row['metadata']
            ))
        
        return checkpoints
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session metadata"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM sessions WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return dict(row)
    
    def cleanup_old_checkpoints(self, days_to_keep: int = 30) -> int:
        """
        Delete checkpoints older than specified days
        
        Args:
            days_to_keep: Number of days to keep checkpoints
        
        Returns:
            Number of checkpoints deleted
        """
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        cutoff_iso = datetime.fromtimestamp(cutoff_date).isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM checkpoints 
            WHERE timestamp < ?
        """, (cutoff_iso,))
        
        deleted_count = cursor.rowcount
        self.conn.commit()
        
        return deleted_count
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get database storage statistics"""
        cursor = self.conn.cursor()
        
        # Total checkpoints
        cursor.execute("SELECT COUNT(*) as count FROM checkpoints")
        total_checkpoints = cursor.fetchone()['count']
        
        # Total sessions
        cursor.execute("SELECT COUNT(*) as count FROM sessions")
        total_sessions = cursor.fetchone()['count']
        
        # Storage size
        cursor.execute("""
            SELECT 
                SUM(compressed_size) as total_compressed,
                SUM(original_size) as total_original,
                AVG(compression_ratio) as avg_compression
            FROM checkpoints
        """)
        storage_row = cursor.fetchone()
        
        db_file_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
        
        return {
            "total_checkpoints": total_checkpoints,
            "total_sessions": total_sessions,
            "total_compressed_bytes": storage_row['total_compressed'] or 0,
            "total_original_bytes": storage_row['total_original'] or 0,
            "avg_compression_ratio": storage_row['avg_compression'] or 0.0,
            "db_file_size_bytes": db_file_size,
            "db_file_size_mb": round(db_file_size / (1024 * 1024), 2)
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
