#!/usr/bin/env python3
"""
Export full master pricing table to CSV for review.
"""
import csv
import json
from pathlib import Path

MASTER_JSON = "gpt_consolidation_agent/deployment/knowledge_base/bromyros_pricing_master.json"
OUTPUT_CSV = "pricing/out/bromyros_pricing_master_full_table.csv"

FIELD_ORDER = [
    "id",
    "sku",
    "name",
    "description",
    "type",
    "family",
    "unit_base",
    "thickness_mm",
    "length_m",
    "production_type",
    "min_length_m",
    "max_length_m",
    "price_usd",
    "sale_price_usd_ex_iva",
    "cost_usd_ex_iva",
    "web_price_usd",
    "stock_status",
    "tipo",
    "familia",
    "default_thickness",
]


def export_table() -> None:
    master_path = Path(MASTER_JSON)
    if not master_path.exists():
        raise FileNotFoundError(f"Master file not found: {MASTER_JSON}")

    data = json.loads(master_path.read_text(encoding="utf-8"))
    products = data.get("products", [])

    output_path = Path(OUTPUT_CSV)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELD_ORDER)
        writer.writeheader()
        for p in products:
            row = {field: p.get(field) for field in FIELD_ORDER}
            writer.writerow(row)

    # Print a short summary for the console
    total = len(products)
    production_types = {}
    missing_length = 0
    missing_thickness = 0
    for p in products:
        production_types[p.get("production_type") or "none"] = (
            production_types.get(p.get("production_type") or "none", 0) + 1
        )
        if not p.get("length_m"):
            missing_length += 1
        if not p.get("thickness_mm"):
            missing_thickness += 1

    print(f"Exported {total} products to {OUTPUT_CSV}")
    print(f"Production types: {production_types}")
    print(f"Missing length_m: {missing_length}")
    print(f"Missing thickness_mm: {missing_thickness}")


if __name__ == "__main__":
    export_table()
