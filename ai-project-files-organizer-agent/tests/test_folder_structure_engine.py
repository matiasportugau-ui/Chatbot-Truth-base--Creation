"""
Tests for FolderStructureEngine
"""

import tempfile
from pathlib import Path

import pytest

from ai_files_organizer.core.folder_structure_engine import FolderStructureEngine
from ai_files_organizer.core.file_scanner import FileMetadata
from datetime import datetime


@pytest.fixture
def temp_workspace():
    """Create temporary workspace"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        yield workspace


def test_generate_proposal(temp_workspace):
    """Test proposal generation"""
    engine = FolderStructureEngine()
    
    # Create test metadata
    file_meta = FileMetadata(
        path=temp_workspace / "test.md",
        name="test.md",
        extension=".md",
        size=100,
        modified_time=datetime.now(),
        category="documentation",
        file_type="text/markdown",
    )
    
    proposal = engine.generate_proposal(file_meta, temp_workspace)
    
    assert "proposed_location" in proposal
    assert "justification" in proposal
    assert "confidence" in proposal
    assert proposal["confidence"] > 0
