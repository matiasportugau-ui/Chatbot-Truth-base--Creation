import json
import gspread
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .redesign_tool import CostMatrixRedesigner

# Preferred auth (matches tests + modern google-auth)
try:
    from google.oauth2.service_account import Credentials  # type: ignore
except Exception:  # pragma: no cover
    Credentials = None  # type: ignore

# Re-use ML lengths from excel_manager context
LENGTHS_ML: List[str] = [
    "1.0",
    "3.5",
    "4.0",
    "4.5",
    "5.0",
    "5.5",
    "6.0",
    "6.5",
    "7.0",
    "7.5",
    "8.0",
    "8.5",
    "9.0",
    "9.5",
    "10.0",
    "10.5",
    "11.0",
    "11.5",
    "12.0",
    "12.5",
    "13.0",
]

def get_client(credentials_path: str):
    """Public wrapper for Google Sheets client authentication.

    Args:
        credentials_path: Path to the Google credentials JSON file.

    Returns:
        Authenticated gspread client.
    """
    return _get_client(credentials_path)


def _get_client(credentials_path: str):
    """Authenticate and return gspread client."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    if Credentials is None:
        raise ImportError("google-auth is required for get_client()")
    creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
    return gspread.authorize(creds)


def _safe_str(v: Any) -> str:
    return str(v).strip() if v is not None else ""


def _num(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "").replace(" ", "")
    try:
        return float(s)
    except ValueError:
        return None


def _build_headers() -> List[str]:
    """Return canonical headers for Google Sheets."""
    return [
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


def sync_up(json_path: str, credentials_path: str, spreadsheet_name: str):
    """Push local JSON Cost Matrix to Google Sheets."""
    client = get_client(credentials_path)
    

    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    products = data.get("productos", {}).get("todos", [])

    # Open spreadsheet
    try:
        sh = client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        print(
            f"Spreadsheet '{spreadsheet_name}' not found. Please create it and share with service account."
        )
        raise

    # Get or create PRODUCTS worksheet
    try:
        ws = sh.worksheet("PRODUCTS")
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title="PRODUCTS", rows="1000", cols="50")

    # Build rows
    headers = _build_headers()
    rows = [headers]

    for p in products:
        meta = p.get("metadata", {}) or {}
        costos = (p.get("costos", {}) or {}).get("fabrica_directo", {}) or {}
        margen = p.get("margen", {}) or {}
        precios = p.get("precios", {}) or {}
        empresa = precios.get("empresa", {}) or {}
        particular = precios.get("particular", {}) or {}
        web_stock = precios.get("web_stock", {}) or {}
        ml = p.get("precio_metro_lineal", {}) or {}
        ml_by_len = ml.get("precios_por_largo", {}) or {}

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

    # Clear and update
    ws.clear()
    ws.update(rows)
    print(f"Successfully pushed {len(products)} products to Google Sheets.")


def sync_down(
    credentials_path: str,
    spreadsheet_name: str,
    output_json_path: str,
    base_json_path: Optional[str] = None,
):
    """Pull Google Sheets Cost Matrix to local JSON."""
    client = get_client(credentials_path)
    sh = client.open(spreadsheet_name)
    ws = sh.worksheet("PRODUCTS")

    rows = ws.get_all_values()
    if not rows:
        raise ValueError("Spreadsheet is empty.")

    headers = rows[0]
    header_idx = {h: i for i, h in enumerate(headers)}

    def get_val(row, col):
        idx = header_idx.get(col)
        return row[idx] if idx is not None and idx < len(row) else ""

    products = []
    for r in rows[1:]:
        codigo = _safe_str(get_val(r, "codigo"))
        nombre = _safe_str(get_val(r, "nombre"))
        if not codigo or not nombre:
            continue

        ml_by_len = {}
        for l in LENGTHS_ML:
            v = _num(get_val(r, f"ml_{l}"))
            if v is not None:
                ml_by_len[l] = v

        p = {
            "codigo": codigo,
            "nombre": nombre,
            "categoria": _safe_str(get_val(r, "categoria")) or "otros",
            "espesor_mm": _safe_str(get_val(r, "espesor_mm")) or None,
            "estado": _safe_str(get_val(r, "estado")) or "ACT.",
            "costos": {
                "fabrica_directo": {
                    "costo_base_usd_iva": _num(get_val(r, "costo_base_usd_iva")),
                    "costo_con_aumento_usd_iva": _num(
                        get_val(r, "costo_con_aumento_usd_iva")
                    ),
                    "costo_proximo_aumento_usd_iva": _num(
                        get_val(r, "costo_proximo_aumento_usd_iva")
                    ),
                }
            },
            "margen": {
                "porcentaje": _safe_str(get_val(r, "margen_porcentaje")),
                "ganancia_usd": _num(get_val(r, "ganancia_usd")),
            },
            "precios": {
                "empresa": {
                    "venta_iva_usd": _num(get_val(r, "precio_empresa_venta_iva_usd")),
                    "nota": "Empresas descuentan IVA, usar precio + IVA",
                },
                "particular": {
                    "consumidor_iva_inc_usd": _num(
                        get_val(r, "precio_particular_consumidor_iva_inc_usd")
                    ),
                    "nota": "Particulares no descuentan IVA, usar precio IVA incluido",
                },
                "web_stock": {
                    "web_venta_iva_usd": _num(get_val(r, "precio_web_venta_iva_usd")),
                    "web_venta_iva_inc_usd": _num(
                        get_val(r, "precio_web_venta_iva_inc_usd")
                    ),
                },
            },
            "precio_metro_lineal": {
                "precio_base_usd": _num(get_val(r, "precio_ml_base_usd")),
                "precios_por_largo": ml_by_len,
            },
            "metadata": {
                "proveedor": _safe_str(get_val(r, "proveedor")),
                "shopify_status": _safe_str(get_val(r, "shopify_status")),
                "notas": _safe_str(get_val(r, "notas")),
                "fecha_actualizacion": datetime.now().isoformat(),
                "source": "gsheets_sync",
            },
        }
        products.append(p)

    # Rebuild optimized structure
    redesigner = CostMatrixRedesigner()
    structure = redesigner.create_optimized_structure(products)

    # Preserve base meta if provided
    if base_json_path and Path(base_json_path).exists():
        with open(base_json_path, "r", encoding="utf-8") as f:
            base = json.load(f)
        structure["meta"].update(
            {
                k: v
                for k, v in base.get("meta", {}).items()
                if k
                not in [
                    "fecha_creacion",
                    "total_productos",
                    "total_categorias",
                    "estadisticas",
                ]
            }
        )

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)

    print(
        f"Successfully pulled {len(products)} products from Google Sheets to {output_json_path}."
    )


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m ...gsheets_manager sync_up|sync_down ...")
        return

    cmd = sys.argv[1]
    if cmd == "sync_up":
        # sync_up json_path creds_path sheet_name
        sync_up(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "sync_down":
        # sync_down creds_path sheet_name output_json [base_json]
        base = sys.argv[5] if len(sys.argv) > 5 else None
        sync_down(sys.argv[2], sys.argv[3], sys.argv[4], base)


if __name__ == "__main__":
    main()
