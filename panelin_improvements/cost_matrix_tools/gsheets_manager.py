import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .redesign_tool import CostMatrixRedesigner

# Constants shared with excel_manager
LENGTHS_ML: List[str] = [
    "1.0", "3.5", "4.0", "4.5", "5.0", "5.5", "6.0", "6.5", "7.0", "7.5",
    "8.0", "8.5", "9.0", "9.5", "10.0", "10.5", "11.0", "11.5", "12.0", "12.5", "13.0",
]

SHEET_NAME = "PRODUCTS"
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

def _num(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s:
        return None
    s = s.replace(",", "").replace(" ", "")
    try:
        return float(s)
    except Exception:
        return None

def _safe_str(v: Any) -> str:
    if v is None:
        return ""
    s = str(v)
    return s.strip()

def get_client(creds_path: str) -> gspread.Client:
    if not Path(creds_path).exists():
        raise FileNotFoundError(f"Credentials file not found at: {creds_path}")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, SCOPE)
    return gspread.authorize(creds)

def sync_up(json_path: str, creds_path: str, sheet_key_or_name: str) -> None:
    """
    Push local JSON data to Google Sheets.
    """
    print(f"Syncing UP: {json_path} -> Google Sheet '{sheet_key_or_name}'")
    
    # 1. Load JSON
    json_path_p = Path(json_path)
    if not json_path_p.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
        
    data = json.loads(json_path_p.read_text(encoding="utf-8"))
    products: List[Dict[str, Any]] = data.get("productos", {}).get("todos", [])

    # 2. Prepare headers
    headers = [
        "proveedor",
        "codigo",
        "nombre",
        "categoria",
        "espesor_mm",
        "estado",
        "shopify_status",
        "notas",
        "costo_base_usd_iva",
        "costo_con_aumento_usd_iva",
        "costo_proximo_aumento_usd_iva",
        "margen_porcentaje",
        "ganancia_usd",
        "precio_empresa_venta_iva_usd",
        "precio_particular_consumidor_iva_inc_usd",
        "precio_web_venta_iva_usd",
        "precio_web_venta_iva_inc_usd",
        "precio_ml_base_usd",
    ] + [f"ml_{l}" for l in LENGTHS_ML]

    # 3. Prepare rows
    rows: List[List[Any]] = [headers]
    for p in products:
        meta = p.get("metadata", {}) or {}
        costos = (p.get("costos", {}) or {}).get("fabrica_directo", {}) or {}
        margen = p.get("margen", {}) or {}
        precios = p.get("precios", {}) or {}
        empresa = (precios.get("empresa", {}) or {})
        particular = (precios.get("particular", {}) or {})
        web_stock = (precios.get("web_stock", {}) or {})
        ml = p.get("precio_metro_lineal", {}) or {}
        ml_by_len = (ml.get("precios_por_largo", {}) or {})

        row = [
            _safe_str(meta.get("proveedor")),
            _safe_str(p.get("codigo")),
            _safe_str(p.get("nombre")),
            _safe_str(p.get("categoria")),
            _safe_str(p.get("espesor_mm")),
            _safe_str(p.get("estado")),
            _safe_str(meta.get("shopify_status")),
            _safe_str(meta.get("notas")),
            costos.get("costo_base_usd_iva"),
            costos.get("costo_con_aumento_usd_iva"),
            costos.get("costo_proximo_aumento_usd_iva"),
            _safe_str(margen.get("porcentaje")),
            margen.get("ganancia_usd"),
            empresa.get("venta_iva_usd"),
            particular.get("consumidor_iva_inc_usd"),
            web_stock.get("web_venta_iva_usd"),
            web_stock.get("web_venta_iva_inc_usd"),
            ml.get("precio_base_usd"),
        ]
        for l in LENGTHS_ML:
            row.append(ml_by_len.get(l))
        rows.append(row)

    # 4. Connect and Update
    client = get_client(creds_path)
    try:
        sheet = client.open(sheet_key_or_name)
    except gspread.SpreadsheetNotFound:
        # If passed name, try creating? No, safer to fail or assume ID. 
        # But instructions say "share the sheet", implying it exists.
        # Try open by key if it looks like a key, or by title.
        try:
            sheet = client.open_by_key(sheet_key_or_name)
        except Exception:
             raise ValueError(f"Could not find spreadsheet with name or key: {sheet_key_or_name}")

    try:
        ws = sheet.worksheet(SHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(title=SHEET_NAME, rows=len(rows)+100, cols=len(headers))

    ws.clear()
    ws.update(rows)
    print("Sync UP complete.")

def sync_down(creds_path: str, sheet_key_or_name: str, output_json_path: str, base_json_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Pull data from Google Sheets and update local JSON.
    """
    print(f"Syncing DOWN: Google Sheet '{sheet_key_or_name}' -> {output_json_path}")

    # 1. Connect and Fetch
    client = get_client(creds_path)
    try:
        sheet = client.open(sheet_key_or_name)
    except Exception:
        try:
            sheet = client.open_by_key(sheet_key_or_name)
        except Exception:
             raise ValueError(f"Could not find spreadsheet: {sheet_key_or_name}")

    try:
        ws = sheet.worksheet(SHEET_NAME)
    except gspread.WorksheetNotFound:
        raise ValueError(f"Sheet '{SHEET_NAME}' not found in spreadsheet")

    all_values = ws.get_all_values()
    if not all_values:
        raise ValueError("Sheet is empty")

    headers = [_safe_str(h) for h in all_values[0]]
    header_idx = {h: i for i, h in enumerate(headers) if h}

    def get(row, col, default=None):
        i = header_idx.get(col)
        if i is None or i >= len(row):
            return default
        return row[i]

    # 2. Parse rows
    products: List[Dict[str, Any]] = []
    for r in all_values[1:]:
        # Ensure row has enough columns
        if not r: continue
        
        codigo = _safe_str(get(r, "codigo"))
        nombre = _safe_str(get(r, "nombre"))
        if not codigo or not nombre:
            continue

        proveedor = _safe_str(get(r, "proveedor"))
        categoria = _safe_str(get(r, "categoria"))
        espesor_mm = _safe_str(get(r, "espesor_mm")) or None
        estado = _safe_str(get(r, "estado")) or "ACT."
        shopify_status = _safe_str(get(r, "shopify_status"))
        notas = _safe_str(get(r, "notas"))

        costos = {
            "fabrica_directo": {
                "costo_base_usd_iva": _num(get(r, "costo_base_usd_iva")),
                "costo_con_aumento_usd_iva": _num(get(r, "costo_con_aumento_usd_iva")),
                "costo_proximo_aumento_usd_iva": _num(get(r, "costo_proximo_aumento_usd_iva")),
            }
        }
        margen = {
            "porcentaje": _safe_str(get(r, "margen_porcentaje")),
            "ganancia_usd": _num(get(r, "ganancia_usd")),
        }
        precios = {
            "empresa": {
                "venta_iva_usd": _num(get(r, "precio_empresa_venta_iva_usd")),
                "nota": "Empresas descuentan IVA, usar precio + IVA",
            },
            "particular": {
                "consumidor_iva_inc_usd": _num(get(r, "precio_particular_consumidor_iva_inc_usd")),
                "nota": "Particulares no descuentan IVA, usar precio IVA incluido",
            },
            "web_stock": {
                "web_venta_iva_usd": _num(get(r, "precio_web_venta_iva_usd")),
                "web_venta_iva_inc_usd": _num(get(r, "precio_web_venta_iva_inc_usd")),
            },
        }

        ml_by_len: Dict[str, Any] = {}
        for l in LENGTHS_ML:
            v = _num(get(r, f"ml_{l}"))
            if v is not None:
                ml_by_len[l] = v

        precio_metro_lineal = {
            "precio_base_usd": _num(get(r, "precio_ml_base_usd")),
            "precios_por_largo": ml_by_len,
        }

        product = {
            "codigo": codigo,
            "nombre": nombre,
            "categoria": categoria or "otros",
            "espesor_mm": espesor_mm,
            "estado": estado,
            "costos": costos,
            "margen": margen,
            "precios": precios,
            "precio_metro_lineal": precio_metro_lineal,
            "metadata": {
                "proveedor": proveedor,
                "shopify_status": shopify_status,
                "notas": notas,
                "fecha_actualizacion": datetime.now().isoformat(),
                "source": "gsheets_import",
            },
        }
        products.append(product)

    # 3. Optimize structure
    if base_json_path and Path(base_json_path).exists():
        base = json.loads(Path(base_json_path).read_text(encoding="utf-8"))
    else:
        base = {
            "meta": {
                "nombre": "Cost Matrix (Synced from GSheets)",
                "version": "2.0.0",
                "fecha_creacion": datetime.now().isoformat(),
            },
            "reglas_precios": {},
        }

    redesigner = CostMatrixRedesigner()
    structure = redesigner.create_optimized_structure(products)

    # Preserve base meta
    structure["meta"].update({k: v for k, v in base.get("meta", {}).items() if k not in {"fecha_creacion", "total_productos", "total_categorias", "estadisticas"}})
    if base.get("reglas_precios"):
        structure["reglas_precios"] = base["reglas_precios"]

    # 4. Save
    Path(output_json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_json_path).write_text(json.dumps(structure, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Sync DOWN complete.")
    return structure

def main():
    if len(sys.argv) < 3:
        print(
            "Usage:\n"
            "  python -m panelin_improvements.cost_matrix_tools.gsheets_manager sync_up <json_path> <creds_path> <sheet_name>\n"
            "  python -m panelin_improvements.cost_matrix_tools.gsheets_manager sync_down <creds_path> <sheet_name> <output_json_path> [base_json_path]\n"
        )
        sys.exit(1)

    cmd = sys.argv[1].lower()
    
    if cmd == "sync_up":
        if len(sys.argv) < 5:
            print("Error: sync_up requires <json_path> <creds_path> <sheet_name>")
            sys.exit(1)
        sync_up(sys.argv[2], sys.argv[3], sys.argv[4])
        
    elif cmd == "sync_down":
        if len(sys.argv) < 5:
            print("Error: sync_down requires <creds_path> <sheet_name> <output_json_path> [base_json_path]")
            sys.exit(1)
        base = sys.argv[5] if len(sys.argv) >= 6 else None
        sync_down(sys.argv[2], sys.argv[3], sys.argv[4], base)
        
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
