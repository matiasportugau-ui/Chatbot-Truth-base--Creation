#!/usr/bin/env python3
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from panelin_improvements.cost_matrix_tools import gsheets_manager  # noqa: E402


def main():
    creds_path = Path("panelin_improvements/credentials.json")
    json_path = Path(
        "wiki/matriz de costos adaptacion /redesigned/"
        "BROMYROS_Costos_Ventas_2026_OPTIMIZED.json"
    )
    sheet_name = "BROMYROS_Costos_Ventas_2026"

    if not creds_path.exists():
        raise FileNotFoundError(f"Missing credentials at {creds_path}")

    if not json_path.exists():
        raise FileNotFoundError(f"Missing JSON at {json_path}")

    print("Starting manual sync test...")
    print(f"Using sheet: {sheet_name}")

    print("1) Sync UP (local -> sheet)")
    gsheets_manager.sync_up(str(json_path), str(creds_path), sheet_name)

    print("2) Sync DOWN (sheet -> local temp)")
    temp_out = Path("panelin_improvements/scripts/_sync_test_output.json")
    result = gsheets_manager.sync_down(
        str(creds_path),
        sheet_name,
        str(temp_out),
        str(json_path),
    )

    count = len(result.get("productos", {}).get("todos", []))
    print(f"Downloaded products: {count}")

    try:
        original = json.loads(json_path.read_text(encoding="utf-8"))
        original_count = len(original.get("productos", {}).get("todos", []))
        print(f"Original products: {original_count}")
    except (OSError, json.JSONDecodeError):
        print("Could not read original JSON for comparison.")

    print(f"Temp output saved to: {temp_out}")
    print("Manual sync test completed.")


if __name__ == "__main__":
    main()
