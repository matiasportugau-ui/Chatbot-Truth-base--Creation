#!/usr/bin/env python3
"""
User Profiles
=============

User profile persistence and management system with
preferences, interaction history, and learning patterns.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class UserProfile:
    """Represents a user profile"""
    user_id: str
    name: str = ""
    email: str = ""
    preferences: str = "{}"  # JSON string
    interaction_count: int = 0
    first_interaction: str = ""
    last_interaction: str = ""
    learning_patterns: str = "{}"  # JSON string
    metadata: str = "{}"  # JSON string
    created_at: str = ""
    updated_at: str = ""


class UserProfileDatabase:
    """Database for user profile persistence"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize user profile database
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            db_path = str(Path(__file__).parent / "user_profiles.db")
        
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database schema"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                preferences TEXT,
                interaction_count INTEGER DEFAULT 0,
                first_interaction TEXT,
                last_interaction TEXT,
                learning_patterns TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                interaction_data TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Create preferences history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preference_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                changed_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_interactions_user_id 
            ON interactions(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_interactions_timestamp 
            ON interactions(timestamp DESC)
        """)
        
        self.conn.commit()
    
    def create_or_update_user(
        self,
        user_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UserProfile:
        """Create or update a user profile"""
        cursor = self.conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        existing_user = cursor.fetchone()
        
        timestamp = datetime.now().isoformat()
        
        if existing_user:
            # Update existing user
            update_fields = []
            update_values = []
            
            if name is not None:
                update_fields.append("name = ?")
                update_values.append(name)
            
            if email is not None:
                update_fields.append("email = ?")
                update_values.append(email)
            
            if preferences is not None:
                update_fields.append("preferences = ?")
                update_values.append(json.dumps(preferences, ensure_ascii=False))
            
            if metadata is not None:
                update_fields.append("metadata = ?")
                update_values.append(json.dumps(metadata, ensure_ascii=False))
            
            update_fields.append("updated_at = ?")
            update_values.append(timestamp)
            
            update_values.append(user_id)
            
            if update_fields:
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?"
                cursor.execute(query, update_values)
        
        else:
            # Create new user
            cursor.execute("""
                INSERT INTO users 
                (user_id, name, email, preferences, first_interaction, 
                 last_interaction, learning_patterns, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                name or "",
                email or "",
                json.dumps(preferences or {}, ensure_ascii=False),
                timestamp,
                timestamp,
                json.dumps({}, ensure_ascii=False),
                json.dumps(metadata or {}, ensure_ascii=False)
            ))
        
        self.conn.commit()
        
        # Return updated profile
        return self.get_user(user_id)
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return UserProfile(
            user_id=row['user_id'],
            name=row['name'],
            email=row['email'],
            preferences=row['preferences'],
            interaction_count=row['interaction_count'],
            first_interaction=row['first_interaction'],
            last_interaction=row['last_interaction'],
            learning_patterns=row['learning_patterns'],
            metadata=row['metadata'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def record_interaction(
        self,
        user_id: str,
        session_id: str,
        interaction_type: str,
        interaction_data: Dict[str, Any]
    ):
        """Record a user interaction"""
        cursor = self.conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO interactions 
            (user_id, session_id, interaction_type, interaction_data, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            session_id,
            interaction_type,
            json.dumps(interaction_data, ensure_ascii=False),
            timestamp
        ))
        
        # Update user's interaction count and last interaction time
        cursor.execute("""
            UPDATE users 
            SET interaction_count = interaction_count + 1,
                last_interaction = ?
            WHERE user_id = ?
        """, (timestamp, user_id))
        
        self.conn.commit()
    
    def get_user_interactions(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get user's interaction history"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM interactions 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_id, limit))
        
        interactions = []
        for row in cursor.fetchall():
            interactions.append({
                "id": row['id'],
                "session_id": row['session_id'],
                "interaction_type": row['interaction_type'],
                "interaction_data": json.loads(row['interaction_data']),
                "timestamp": row['timestamp']
            })
        
        return interactions
    
    def update_preference(
        self,
        user_id: str,
        preference_key: str,
        preference_value: Any
    ):
        """Update a user preference"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Get current preferences
        current_prefs = json.loads(user.preferences)
        old_value = current_prefs.get(preference_key)
        
        # Update preference
        current_prefs[preference_key] = preference_value
        
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET preferences = ?, updated_at = ?
            WHERE user_id = ?
        """, (
            json.dumps(current_prefs, ensure_ascii=False),
            datetime.now().isoformat(),
            user_id
        ))
        
        # Log preference change
        cursor.execute("""
            INSERT INTO preference_history
            (user_id, preference_key, old_value, new_value, changed_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            preference_key,
            json.dumps(old_value, ensure_ascii=False) if old_value is not None else None,
            json.dumps(preference_value, ensure_ascii=False),
            datetime.now().isoformat()
        ))
        
        self.conn.commit()
    
    def get_all_users(self, limit: int = 100) -> List[UserProfile]:
        """Get all users"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM users 
            ORDER BY last_interaction DESC 
            LIMIT ?
        """, (limit,))
        
        users = []
        for row in cursor.fetchall():
            users.append(UserProfile(
                user_id=row['user_id'],
                name=row['name'],
                email=row['email'],
                preferences=row['preferences'],
                interaction_count=row['interaction_count'],
                first_interaction=row['first_interaction'],
                last_interaction=row['last_interaction'],
                learning_patterns=row['learning_patterns'],
                metadata=row['metadata'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ))
        
        return users
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
