#!/usr/bin/env python3
import json
import sys

# Load from the deployed master file
FILE = "gpt_consolidation_agent/deployment/knowledge_base/bromyros_pricing_master.json"

try:
    with open(FILE, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    print("Master file not found.")
    sys.exit(1)

products = data.get("products", [])

print(
    f"| SKU | Product Name | Prod Type | Length (m) | Min/Max (m) | Price (Inc IVA) |"
)
print(f"|---|---|---|---|---|---|")

# Display first 25 products to give a good sample
for p in products[:25]:
    sku = p.get("sku", "N/A")
    name = p.get("name", "N/A")[:40]
    prod_type = p.get("production_type", "-")

    length = p.get("length_m")
    length_str = f"{length:.2f}" if length else "-"

    min_len = p.get("min_length_m")
    max_len = p.get("max_length_m")
    min_max = f"{min_len}/{max_len}" if min_len else "-"

    price = p.get("price_usd", 0)

    print(
        f"| {sku} | {name}... | {prod_type} | {length_str} | {min_max} | ${price:.2f} |"
    )
