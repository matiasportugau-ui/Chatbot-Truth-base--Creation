import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from kb_update_optimizer import KBUpdateOptimizer

@patch('kb_update_optimizer.OpenAI')
def test_optimizer_init(mock_openai_class):
    mock_openai_class.return_value = MagicMock()
    optimizer = KBUpdateOptimizer(api_key="test_key", assistant_id="test_asst")
    assert optimizer.assistant_id == "test_asst"

def test_calculate_file_hash(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")
    
    # We need a valid optimizer instance for this, but let's mock OpenAI again
    with patch('kb_update_optimizer.OpenAI'):
        optimizer = KBUpdateOptimizer(api_key="test_key", assistant_id="test_asst")
        file_hash = optimizer.calculate_file_hash(test_file)
        assert isinstance(file_hash, str)
        assert len(file_hash) == 32  # MD5 is 32 chars
