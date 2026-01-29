import sys
import os

# Add the current directory to path so we can import pdf_generator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_generator import generate_quotation_pdf
from datetime import datetime

# Dummy data
quotation_data = {
    "client_name": "Test Client",
    "client_address": "Test Address 123",
    "client_phone": "099123456",
    "date": "2026-01-29",
    "valid_until": "2026-02-08",
    "quote_title": "PRESUPUESTO DE PRUEBA",
    "quote_id": "TEST-001",
    "products": [
        {
            "name": "Isopanel EPS 50mm",
            "quantity": 10,
            "unit_price_usd": 46.07,  # VAT Inc
            "total_usd": 460.70,
            "unit_base": "unidad",
            "total_m2": 10,
        }
    ],
    "accessories": [],
    "fixings": [],
    "shipping_usd": 280.0,
}

try:
    output_path = "test_quotation.pdf"
    pdf_path = generate_quotation_pdf(quotation_data, output_path)
    print(f"SUCCESS: PDF generated at {pdf_path}")

    # Check if file actually exists
    if os.path.exists(pdf_path):
        print(f"VERIFIED: File exists at {os.path.abspath(pdf_path)}")
    else:
        print("ERROR: File reported generated but not found on disk")

except Exception as e:
    print(f"FAILURE: {str(e)}")
    import traceback

    traceback.print_exc()
