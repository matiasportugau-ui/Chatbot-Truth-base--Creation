"""Tests for API endpoints"""

import pytest
from starlette.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

from panelin_backend.main import app


@patch("panelin_backend.main.db")
def test_health_check(mock_db):
    """Test health check endpoint"""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


@patch("panelin_backend.main.db")
def test_create_conversation(mock_db):
    """Test creating a conversation"""
    mock_db.create_conversation.return_value = {
        "id": "test-uuid-123",
        "thread_id": "thread_abc",
        "user_name": "Test User",
        "user_type": "customer",
        "status": "active",
        "created_at": datetime(2024, 1, 1, 12, 0, 0)
    }
    
    with TestClient(app) as client:
        response = client.post(
            "/api/conversations",
            json={
                "thread_id": "thread_abc",
                "assistant_id": "asst_xyz",
                "user_name": "Test User",
                "user_type": "customer"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["thread_id"] == "thread_abc"
        assert data["user_name"] == "Test User"
        assert data["user_type"] == "customer"
        assert data["status"] == "active"


@patch("panelin_backend.main.db")
def test_list_conversations(mock_db):
    """Test listing conversations"""
    mock_db.get_conversations.return_value = [
        {
            "id": "test-uuid-1",
            "thread_id": "thread_1",
            "user_name": "User 1",
            "user_type": "customer",
            "status": "active",
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "message_count": 5
        },
        {
            "id": "test-uuid-2",
            "thread_id": "thread_2",
            "user_name": "User 2",
            "user_type": "customer",
            "status": "completed",
            "created_at": datetime(2024, 1, 2, 12, 0, 0),
            "message_count": 10
        }
    ]
    
    with TestClient(app) as client:
        response = client.get("/api/conversations")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["thread_id"] == "thread_1"
        assert data[1]["thread_id"] == "thread_2"


@patch("panelin_backend.main.db")
def test_add_message(mock_db):
    """Test adding a message to a conversation"""
    mock_db.get_conversation_by_id.return_value = {
        "id": "test-uuid-123",
        "thread_id": "thread_abc"
    }
    
    mock_db.add_message.return_value = {
        "id": "msg-uuid-1",
        "role": "user",
        "content": "Hello",
        "created_at": datetime(2024, 1, 1, 12, 0, 0)
    }
    
    with TestClient(app) as client:
        response = client.post(
            "/api/conversations/test-uuid-123/messages",
            json={
                "thread_id": "thread_abc",
                "message_id": "msg_123",
                "role": "user",
                "content": "Hello",
                "created_at": "2024-01-01T12:00:00"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "user"
        assert data["content"] == "Hello"


@patch("panelin_backend.main.db")
def test_get_conversation_messages(mock_db):
    """Test getting messages for a conversation"""
    mock_db.get_conversation_by_id.return_value = {
        "id": "test-uuid-123",
        "thread_id": "thread_abc"
    }
    
    mock_db.get_conversation_messages.return_value = [
        {
            "id": "msg-1",
            "role": "user",
            "content": "Hello",
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "metadata": None
        },
        {
            "id": "msg-2",
            "role": "assistant",
            "content": "Hi there!",
            "created_at": datetime(2024, 1, 1, 12, 1, 0),
            "metadata": None
        }
    ]
    
    with TestClient(app) as client:
        response = client.get("/api/conversations/test-uuid-123/messages")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["role"] == "user"
        assert data[1]["role"] == "assistant"


@patch("panelin_backend.main.db")
def test_export_conversation(mock_db):
    """Test exporting a conversation"""
    mock_db.get_conversation_by_id.return_value = {
        "id": "test-uuid-123",
        "thread_id": "thread_abc",
        "user_name": "Test User",
        "created_at": datetime(2024, 1, 1, 12, 0, 0)
    }
    
    mock_db.get_conversation_messages.return_value = [
        {
            "id": "msg-1",
            "role": "user",
            "content": "Hello",
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "metadata": None
        }
    ]
    
    with TestClient(app) as client:
        response = client.get("/api/conversations/test-uuid-123/export?format=json")
        
        assert response.status_code == 200
        data = response.json()
        assert "conversation" in data
        assert "messages" in data
        assert data["conversation"]["thread_id"] == "thread_abc"


@patch("panelin_backend.main.db")
def test_get_analytics_summary(mock_db):
    """Test getting analytics summary"""
    mock_db.get_conversations.return_value = [
        {"id": "1", "message_count": 5},
        {"id": "2", "message_count": 10},
        {"id": "3", "message_count": 3}
    ]
    
    with TestClient(app) as client:
        response = client.get("/api/analytics/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_conversations"] == 3
        assert data["total_messages"] == 18
        assert data["avg_messages_per_conversation"] == 6.0


@patch("panelin_backend.main.db")
def test_add_message_conversation_not_found(mock_db):
    """Test adding message to non-existent conversation"""
    mock_db.get_conversation_by_id.return_value = None
    
    with TestClient(app) as client:
        response = client.post(
            "/api/conversations/nonexistent/messages",
            json={
                "thread_id": "thread_abc",
                "message_id": "msg_123",
                "role": "user",
                "content": "Hello",
                "created_at": "2024-01-01T12:00:00"
            }
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
