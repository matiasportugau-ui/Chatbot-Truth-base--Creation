"""Tests for database layer"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import uuid

from panelin_backend.database import db


@patch("panelin_backend.database.db.psycopg2")
def test_create_conversation(mock_psycopg2):
    """Test creating a conversation in database"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    mock_psycopg2.connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    test_uuid = str(uuid.uuid4())
    mock_cursor.fetchone.return_value = {
        "id": test_uuid,
        "thread_id": "thread_abc",
        "user_name": "Test User",
        "user_type": "customer",
        "status": "active",
        "created_at": datetime.now()
    }
    
    result = db.create_conversation(
        thread_id="thread_abc",
        assistant_id="asst_xyz",
        user_name="Test User"
    )
    
    assert result["thread_id"] == "thread_abc"
    assert result["user_name"] == "Test User"
    assert mock_cursor.execute.called


@patch("panelin_backend.database.db.psycopg2")
def test_add_message(mock_psycopg2):
    """Test adding a message to database"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    mock_psycopg2.connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    test_uuid = str(uuid.uuid4())
    mock_cursor.fetchone.return_value = {
        "id": test_uuid,
        "role": "user",
        "content": "Hello",
        "created_at": datetime.now()
    }
    
    result = db.add_message(
        conversation_id=str(uuid.uuid4()),
        message_id="msg_123",
        thread_id="thread_abc",
        role="user",
        content="Hello",
        created_at=datetime.now()
    )
    
    assert result["role"] == "user"
    assert result["content"] == "Hello"
    assert mock_cursor.execute.call_count == 2  # Insert + Update


@patch("panelin_backend.database.db.psycopg2")
def test_get_conversations(mock_psycopg2):
    """Test getting conversations from database"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    mock_psycopg2.connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    mock_cursor.fetchall.return_value = [
        {
            "id": str(uuid.uuid4()),
            "thread_id": "thread_1",
            "user_name": "User 1",
            "user_type": "customer",
            "status": "active",
            "created_at": datetime.now(),
            "message_count": 5
        }
    ]
    
    result = db.get_conversations()
    
    assert len(result) == 1
    assert result[0]["thread_id"] == "thread_1"
    assert mock_cursor.execute.called


@patch("panelin_backend.database.db.psycopg2")
def test_get_conversation_messages(mock_psycopg2):
    """Test getting messages for a conversation"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    mock_psycopg2.connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    mock_cursor.fetchall.return_value = [
        {
            "id": str(uuid.uuid4()),
            "role": "user",
            "content": "Hello",
            "created_at": datetime.now(),
            "metadata": None
        },
        {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": "Hi!",
            "created_at": datetime.now(),
            "metadata": None
        }
    ]
    
    result = db.get_conversation_messages(str(uuid.uuid4()))
    
    assert len(result) == 2
    assert result[0]["role"] == "user"
    assert result[1]["role"] == "assistant"
    assert mock_cursor.execute.called


@patch("panelin_backend.database.db.psycopg2")
def test_get_conversation_by_thread_id(mock_psycopg2):
    """Test getting conversation by thread_id"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    mock_psycopg2.connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    test_uuid = str(uuid.uuid4())
    mock_cursor.fetchone.return_value = {
        "id": test_uuid,
        "thread_id": "thread_abc",
        "assistant_id": "asst_xyz",
        "user_name": "Test User",
        "user_type": "customer",
        "status": "active",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    result = db.get_conversation_by_thread_id("thread_abc")
    
    assert result is not None
    assert result["thread_id"] == "thread_abc"
    assert mock_cursor.execute.called


@patch("panelin_backend.database.db.psycopg2")
def test_get_conversation_by_thread_id_not_found(mock_psycopg2):
    """Test getting non-existent conversation by thread_id"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    mock_psycopg2.connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    mock_cursor.fetchone.return_value = None
    
    result = db.get_conversation_by_thread_id("nonexistent")
    
    assert result is None
