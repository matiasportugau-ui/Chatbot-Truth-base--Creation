"""Database layer for Panelin conversation logging"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from typing import Dict, List, Optional
from datetime import datetime
import uuid

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://panelin:changeme@localhost:5432/panelin_conversations")


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def create_conversation(
    thread_id: str, 
    assistant_id: str, 
    user_id: Optional[str] = None, 
    user_name: Optional[str] = None, 
    user_type: str = "customer"
) -> Dict:
    """Create a new conversation record"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO conversations (thread_id, assistant_id, user_id, user_name, user_type)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, thread_id, user_name, user_type, status, created_at
            """, (thread_id, assistant_id, user_id, user_name, user_type))
            return dict(cur.fetchone())


def add_message(
    conversation_id: str, 
    message_id: str, 
    thread_id: str, 
    role: str, 
    content: str, 
    created_at: datetime
) -> Dict:
    """Add a message to a conversation"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Insert message
            cur.execute("""
                INSERT INTO messages (conversation_id, message_id, thread_id, role, content, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, role, content, created_at
            """, (conversation_id, message_id, thread_id, role, content, created_at))
            
            result = dict(cur.fetchone())
            
            # Update conversation updated_at
            cur.execute("""
                UPDATE conversations 
                SET updated_at = %s 
                WHERE id = %s
            """, (datetime.now(), conversation_id))
            
            return result


def get_conversation_by_thread_id(thread_id: str) -> Optional[Dict]:
    """Get conversation by thread_id"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, thread_id, assistant_id, user_name, user_type, status, created_at, updated_at
                FROM conversations
                WHERE thread_id = %s
            """, (thread_id,))
            result = cur.fetchone()
            return dict(result) if result else None


def get_conversations(
    user_type: Optional[str] = None, 
    status: Optional[str] = None, 
    limit: int = 50, 
    offset: int = 0
) -> List[Dict]:
    """Get list of conversations with filters"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT 
                    c.id, c.thread_id, c.user_name, c.user_type, c.status, c.created_at,
                    COUNT(m.id) as message_count
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE 1=1
            """
            params = []
            
            if user_type:
                query += " AND c.user_type = %s"
                params.append(user_type)
            
            if status:
                query += " AND c.status = %s"
                params.append(status)
            
            query += " GROUP BY c.id ORDER BY c.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]


def get_conversation_messages(conversation_id: str) -> List[Dict]:
    """Get all messages for a conversation"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, role, content, created_at, metadata
                FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at ASC
            """, (conversation_id,))
            return [dict(row) for row in cur.fetchall()]


def get_conversation_by_id(conversation_id: str) -> Optional[Dict]:
    """Get conversation by ID"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, thread_id, assistant_id, user_name, user_type, status, created_at, updated_at
                FROM conversations
                WHERE id = %s
            """, (conversation_id,))
            result = cur.fetchone()
            return dict(result) if result else None
