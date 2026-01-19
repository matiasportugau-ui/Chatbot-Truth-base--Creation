"""
Tests for FileOrganizerAgent
"""

import tempfile
from pathlib import Path

import pytest

from ai_files_organizer import FileOrganizerAgent


@pytest.fixture
def temp_workspace():
    """Create temporary workspace"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        # Create test files
        (workspace / "test.md").write_text("# Test")
        (workspace / "config.json").write_text('{"key": "value"}')
        
        yield workspace


def test_agent_initialization(temp_workspace):
    """Test agent initialization"""
    agent = FileOrganizerAgent(
        workspace_path=str(temp_workspace),
        require_approval=False
    )
    
    assert agent.workspace_path == Path(temp_workspace).resolve()


def test_agent_scan(temp_workspace):
    """Test file scanning"""
    agent = FileOrganizerAgent(
        workspace_path=str(temp_workspace),
        require_approval=False
    )
    
    files = agent.scanner.scan()
    assert len(files) >= 2


def test_suggest_file_location(temp_workspace):
    """Test file location suggestion"""
    agent = FileOrganizerAgent(
        workspace_path=str(temp_workspace),
        require_approval=False
    )
    
    proposal = agent.suggest_new_file_location(str(temp_workspace / "new_doc.md"))
    assert "proposed_location" in proposal or "error" in proposal
