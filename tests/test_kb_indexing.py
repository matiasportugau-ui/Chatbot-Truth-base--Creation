import pytest
from pathlib import Path
import json
from agente_kb_indexing import KBIndexingAgent

def test_kb_agent_init(temp_kb_dir):
    agent = KBIndexingAgent(kb_path=temp_kb_dir)
    assert agent.kb_path == temp_kb_dir

def test_load_json_file_missing(temp_kb_dir):
    agent = KBIndexingAgent(kb_path=temp_kb_dir)
    result = agent._load_json_file("non_existent.json", 1)
    assert result is None

def test_index_json_structure():
    agent = KBIndexingAgent()
    data = {"key1": "value1", "key2": {"subkey": 123}}
    index = agent._index_json_structure(data)
    assert len(index) > 0
    # Check if key1 is indexed
    assert any(item["key"] == "key1" for item in index)
    # Check if subkey is indexed
    assert any(item["key"] == "subkey" for item in index)
