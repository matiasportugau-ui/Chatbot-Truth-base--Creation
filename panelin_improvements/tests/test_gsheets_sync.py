import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import pytest  # noqa: E402

from panelin_improvements.cost_matrix_tools import gsheets_manager  # noqa: E402


class FakeWorksheet:
    def __init__(self, values=None):
        self.values = values or []
        self.cleared = False
        self.updated = []

    def clear(self):
        self.cleared = True

    def update(self, range_name, values=None):
        # gspread supports update(values) and update(range_name, values)
        if values is None:
            values = range_name
        self.updated.append(values)

    def get_all_values(self):
        return self.values


class FakeSheet:
    def __init__(self, worksheet):
        self._worksheet = worksheet
        self.added = False

    def worksheet(self, name):
        if name != gsheets_manager.SHEET_NAME:
            raise gsheets_manager.gspread.WorksheetNotFound("Not found")
        return self._worksheet

    def add_worksheet(self, title, rows, cols):
        self.added = True
        return self._worksheet


class FakeClient:
    def __init__(self, sheet):
        self.sheet = sheet
        self.open_called = False
        self.open_by_key_called = False

    def open(self, name):
        self.open_called = True
        return self.sheet

    def open_by_key(self, key):
        self.open_by_key_called = True
        return self.sheet


def _sample_json():
    return {
        "productos": {
            "todos": [
                {
                    "codigo": "IAGRO30",
                    "nombre": "Producto Test",
                    "categoria": "isoroof_foil",
                    "espesor_mm": "30",
                    "estado": "ACT.",
                    "costos": {
                        "fabrica_directo": {
                            "costo_base_usd_iva": 10.0,
                        }
                    },
                    "margen": {"porcentaje": "20", "ganancia_usd": 2.0},
                    "precios": {
                        "empresa": {"venta_iva_usd": 12.0},
                        "particular": {"consumidor_iva_inc_usd": 14.0},
                        "web_stock": {
                            "web_venta_iva_usd": 12.5,
                            "web_venta_iva_inc_usd": 15.0,
                        },
                    },
                    "precio_metro_lineal": {
                        "precio_base_usd": 3.2,
                        "precios_por_largo": {},
                    },
                    "metadata": {"proveedor": "BROMYROS"},
                }
            ]
        }
    }


def test_validate_json_structure_ok():
    products = gsheets_manager._validate_json_structure(_sample_json())
    assert isinstance(products, list)
    assert products[0]["codigo"] == "IAGRO30"


def test_validate_json_structure_invalid():
    with pytest.raises(ValueError):
        gsheets_manager._validate_json_structure({"productos": {"todos": {}}})


def test_sync_up_writes_rows(monkeypatch, tmp_path):
    data = _sample_json()
    json_path = tmp_path / "data.json"
    json_path.write_text(json.dumps(data), encoding="utf-8")

    ws = FakeWorksheet()
    client = FakeClient(FakeSheet(ws))

    monkeypatch.setattr(gsheets_manager, "get_client", lambda *_: client)

    gsheets_manager.sync_up(str(json_path), "creds.json", "sheet")
    assert ws.cleared is True
    assert ws.updated


def test_sync_down_writes_json(monkeypatch, tmp_path):
    headers = gsheets_manager._build_headers()
    row = [
        "BROMYROS",
        "IAGRO30",
        "Producto Test",
        "isoroof_foil",
        "30",
        "ACT.",
        "",
        "",
        "10",
        "",
        "",
        "20",
        "2",
        "12",
        "14",
        "12.5",
        "15",
        "3.2",
    ]
    values = [headers, row]
    ws = FakeWorksheet(values=values)
    client = FakeClient(FakeSheet(ws))

    monkeypatch.setattr(gsheets_manager, "get_client", lambda *_: client)

    output_path = tmp_path / "out.json"
    result = gsheets_manager.sync_down("creds.json", "sheet", str(output_path))

    assert output_path.exists()
    assert result["productos"]["todos"][0]["codigo"] == "IAGRO30"


def test_sync_down_missing_headers(monkeypatch, tmp_path):
    headers = ["codigo", "nombre"]
    values = [headers, ["IAGRO30", "Producto"]]
    ws = FakeWorksheet(values=values)
    client = FakeClient(FakeSheet(ws))

    monkeypatch.setattr(gsheets_manager, "get_client", lambda *_: client)

    with pytest.raises(ValueError):
        gsheets_manager.sync_down("creds.json", "sheet", str(tmp_path / "out.json"))
