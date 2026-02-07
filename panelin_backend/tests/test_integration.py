"""Integration tests for chat_with_panelin.py logging"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions from chat_with_panelin
from chat_with_panelin import log_conversation_create, log_message


@patch("chat_with_panelin.requests")
def test_log_conversation_create_success(mock_requests):
    """Test successful conversation logging"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test-uuid",
        "thread_id": "thread_abc",
        "user_name": "Test User"
    }
    mock_requests.post.return_value = mock_response
    
    result = log_conversation_create(
        thread_id="thread_abc",
        assistant_id="asst_xyz",
        user_name="Test User"
    )
    
    assert result is not None
    assert result["id"] == "test-uuid"
    assert result["thread_id"] == "thread_abc"
    mock_requests.post.assert_called_once()


@patch("chat_with_panelin.requests")
def test_log_conversation_create_failure(mock_requests):
    """Test conversation logging failure handling"""
    mock_requests.post.side_effect = Exception("Connection error")
    
    result = log_conversation_create(
        thread_id="thread_abc",
        assistant_id="asst_xyz",
        user_name="Test User"
    )
    
    # Should return None on error but not crash
    assert result is None


@patch("chat_with_panelin.requests")
def test_log_message_success(mock_requests):
    """Test successful message logging"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_requests.post.return_value = mock_response
    
    # Should not raise exception
    log_message(
        conversation_id="test-uuid",
        message_id="msg_123",
        thread_id="thread_abc",
        role="user",
        content="Hello",
        created_at=datetime.now()
    )
    
    mock_requests.post.assert_called_once()


@patch("chat_with_panelin.requests")
def test_log_message_failure(mock_requests):
    """Test message logging failure handling"""
    mock_requests.post.side_effect = Exception("Connection error")
    
    # Should not raise exception, just print warning
    log_message(
        conversation_id="test-uuid",
        message_id="msg_123",
        thread_id="thread_abc",
        role="user",
        content="Hello",
        created_at=datetime.now()
    )
    
    # Test passes if no exception is raised


@patch("chat_with_panelin.requests")
def test_log_conversation_without_user_name(mock_requests):
    """Test conversation logging without user name"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test-uuid",
        "thread_id": "thread_abc",
        "user_name": None
    }
    mock_requests.post.return_value = mock_response
    
    result = log_conversation_create(
        thread_id="thread_abc",
        assistant_id="asst_xyz",
        user_name=None
    )
    
    assert result is not None
    assert result["user_name"] is None
    
    # Verify the request was made with correct data
    call_args = mock_requests.post.call_args
    assert call_args[1]["json"]["user_name"] is None
    assert call_args[1]["json"]["user_type"] == "customer"


@patch("chat_with_panelin.requests")
def test_backend_url_configuration(mock_requests):
    """Test that backend URL is correctly configured"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "test"}
    mock_requests.post.return_value = mock_response
    
    log_conversation_create(
        thread_id="thread_abc",
        assistant_id="asst_xyz"
    )
    
    # Verify URL includes the correct endpoint
    call_args = mock_requests.post.call_args
    url = call_args[0][0]
    assert "/api/conversations" in url
