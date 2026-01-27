#!/usr/bin/env python3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from agente_kb_indexing import (  # noqa: E402
    get_cost_matrix_product,
    sync_cost_matrix,
    update_product_price,
)


def main():
    creds_path = Path("panelin_improvements/credentials.json")
    if not creds_path.exists():
        raise FileNotFoundError(
            "Missing credentials.json. See GOOGLE_SHEETS_SETUP.md"
        )

    print("1) Test lookup by code")
    result = get_cost_matrix_product("IAGRO30")
    if "product" not in result:
        raise RuntimeError(f"Lookup failed: {result}")
    print(f"Product found: {result['product'].get('nombre')}")

    print("2) Test sync down (Google Sheets -> local JSON)")
    sync_result = sync_cost_matrix()
    if sync_result.get("error"):
        raise RuntimeError(f"sync_cost_matrix failed: {sync_result}")
    print("Sync down successful.")

    print("3) Test update product price (local -> Google Sheets)")
    update_result = update_product_price(
        "IAGRO30",
        999.0,
        field="costo_base_usd_iva",
    )
    if update_result.get("error"):
        raise RuntimeError(
            f"update_product_price failed: {update_result}"
        )
    print(f"Update status: {update_result.get('sync_status')}")

    print("Integration validation completed.")


if __name__ == "__main__":
    main()
