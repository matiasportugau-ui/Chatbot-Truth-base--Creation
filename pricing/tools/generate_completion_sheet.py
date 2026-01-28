#!/usr/bin/env python3
"""
Generate Data Completion Sheet
Creates a CSV containing ONLY products with missing critical data (Length, Thickness, Type, Family).
Pre-fills with current values for context.
"""

import json
import csv
from pathlib import Path

INPUT_JSON = "pricing/out/bromyros_pricing_reference.json"
OUTPUT_CSV = "pricing/out/products_missing_data.csv"

REQUIRED_FIELDS = ["length_m", "thickness_mm", "type", "family", "unit_base"]


def generate_sheet():
    input_path = Path(INPUT_JSON)
    if not input_path.exists():
        print(f"Error: {INPUT_JSON} not found.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    products = data.get("products", [])
    missing_data_rows = []

    for p in products:
        # Check if any required field is missing (None, empty string, or 0 where 0 is invalid)
        is_missing = False
        row = {
            "sku": p.get("sku"),
            "name": p.get("name"),
            "current_status": p.get("stock_status"),
        }

        for field in REQUIRED_FIELDS:
            val = p.get(field)
            # define "missing": None, "", or 0 (for numerical fields like length/thickness)
            if val is None or val == "" or (isinstance(val, (int, float)) and val == 0):
                is_missing = True
                row[field] = ""  # Leave empty for user to fill
            else:
                row[field] = val  # Pre-fill existing

        if is_missing:
            missing_data_rows.append(row)

    # Write to CSV
    if not missing_data_rows:
        print("Great news! No missing data found.")
        return

    fieldnames = ["sku", "name", "current_status"] + REQUIRED_FIELDS

    Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(missing_data_rows)

    print(
        f"Generated {OUTPUT_CSV} with {len(missing_data_rows)} rows requiring completion."
    )
    print("Columns to fill: length_m, thickness_mm, type, family, unit_base")


if __name__ == "__main__":
    generate_sheet()
