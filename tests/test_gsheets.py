import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from panelin_improvements.cost_matrix_tools import gsheets_manager

def test_num_conversion():
    assert gsheets_manager._num("1,234.56") == 1234.56
    assert gsheets_manager._num(None) is None
    assert gsheets_manager._num("abc") is None

def test_safe_str():
    assert gsheets_manager._safe_str(" hello ") == "hello"
    assert gsheets_manager._safe_str(None) == ""
    assert gsheets_manager._safe_str(123) == "123"

@patch('panelin_improvements.cost_matrix_tools.gsheets_manager.Credentials')
@patch('gspread.authorize')
def test_get_client(mock_authorize, mock_creds, tmp_path):
    creds_file = tmp_path / "creds.json"
    creds_file.write_text('{"type": "service_account"}')
    
    mock_creds.from_service_account_file.return_value = MagicMock()
    
    client = gsheets_manager.get_client(str(creds_file))
    assert mock_creds.from_service_account_file.called
    assert mock_authorize.called
