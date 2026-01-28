import pytest
from unittest.mock import MagicMock
import os
from pathlib import Path

@pytest.fixture
def mock_openai():
    mock = MagicMock()
    return mock

@pytest.fixture
def temp_kb_dir(tmp_path):
    kb_dir = tmp_path / "Files"
    kb_dir.mkdir()
    return kb_dir

@pytest.fixture
def mock_gsheets():
    mock = MagicMock()
    return mock
