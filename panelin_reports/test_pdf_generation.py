#!/usr/bin/env python3
"""
Test PDF Generation
===================

Test script to validate BMC Uruguay quotation PDF generation.
Creates sample PDFs with test data.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from panelin_reports.pdf_generator import (
    BMCQuotationPDF,
    QuotationDataFormatter,
    generate_quotation_pdf,
)


def create_sample_quotation_data():
    """Create sample quotation data for testing"""
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "location": "Maldonado, Uy.",
        "quote_title": "Cotización",
        "quote_description": "Isopanel 50 mm + Isodec EPS 100mm",
        "client_name": "Juan Pérez",
        "client_address": "Av. Principal 123, Maldonado",
        "client_phone": "099 123 456",
        "autoportancia": 5.5,
        "apoyos": 1,
        "products": [
            {
                "name": "Isopanel EPS 50 mm (Fachada)",
                "length_m": 6.0,
                "quantity": 33,
                "unit_price_usd": 33.21,
                "total_usd": 6600.00,
                "total_m2": 200.0,
            },
            {
                "name": "Isopanel EPS 50 mm (Fachada)",
                "length_m": 5.5,
                "quantity": 15,
                "unit_price_usd": 33.21,
                "total_usd": 2745.00,
                "total_m2": 82.5,
            },
            {
                "name": "Isodec EPS 100 mm (Cubierta)",
                "length_m": 7.0,
                "quantity": 25,
                "unit_price_usd": 36.54,
                "total_usd": 6388.50,
                "total_m2": 175.0,
            },
        ],
        "accessories": [
            {
                "name": 'Perfil Ch. Blanca "U" 50mm x 35mm',
                "length_m": 3.0,
                "quantity": 10,
                "unit_price_usd": 3.90,
                "total_usd": 117.00,
            },
            {
                "name": "Perfil Alu 5852 Anodizado (Estructural)",
                "length_m": 6.8,
                "quantity": 5,
                "unit_price_usd": 8.95,
                "total_usd": 304.30,
            },
            {
                "name": "Perfil K2 Ch. Blanca (int. 35x35)",
                "length_m": 3.0,
                "quantity": 8,
                "unit_price_usd": 3.40,
                "total_usd": 81.60,
            },
            {
                "name": "Canalón Estandar 100mm",
                "length_m": 3.03,
                "quantity": 4,
                "unit_price_usd": 22.43,
                "total_usd": 271.66,
            },
        ],
        "fixings": [
            {
                "name": "Bromplast Silicona Neutra (Salchicha)",
                "specification": "600 gr.",
                "quantity": 5,
                "unit_price_usd": 9.78,
                "total_usd": 48.90,
            },
            {
                "name": "Silicona Neutra (Pomo)",
                "specification": "280 gr.",
                "quantity": 10,
                "unit_price_usd": 6.08,
                "total_usd": 60.80,
            },
            {
                "name": "Varilla Roscada BSW",
                "specification": '1m – ⅜"',
                "quantity": 20,
                "unit_price_usd": 2.43,
                "total_usd": 48.60,
            },
            {
                "name": "Tuerca Gal. BSW",
                "specification": '⅜"',
                "quantity": 40,
                "unit_price_usd": 0.15,
                "total_usd": 6.00,
            },
            {
                "name": "Remache POP ó T1 P. Mecha",
                "specification": "5/32 x ½",
                "quantity": 100,
                "unit_price_usd": 0.06,
                "total_usd": 6.00,
            },
        ],
        "shipping_usd": 280.0,
        "comments": [
            "Proyecto: Ampliación galpón industrial",
            "Nota: Incluye todos los accesorios necesarios para instalación completa",
        ],
    }


def test_pdf_generation():
    """Test PDF generation with sample data"""
    print("=" * 60)
    print("BMC Uruguay Quotation PDF Generator - Test Script")
    print("=" * 60)
    print()

    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # Create sample data
    print("1. Creating sample quotation data...")
    sample_data = create_sample_quotation_data()
    print(f"   ✅ Client: {sample_data['client_name']}")
    print(f"   ✅ Products: {len(sample_data['products'])}")
    print(f"   ✅ Accessories: {len(sample_data['accessories'])}")
    print(f"   ✅ Fixings: {len(sample_data['fixings'])}")
    print()

    # Format data
    print("2. Formatting data for PDF...")
    formatted_data = QuotationDataFormatter.format_for_pdf(sample_data)
    totals = formatted_data["totals"]
    print(f"   ✅ Subtotal: ${totals['subtotal']:,.2f}")
    print(f"   ✅ IVA 22%: ${totals['iva']:,.2f}")
    print(f"   ✅ Total: ${totals['grand_total']:,.2f}")
    print()

    # Generate PDF
    print("3. Generating PDF...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"cotizacion_test_{timestamp}.pdf"

    try:
        pdf_path = generate_quotation_pdf(sample_data, str(output_path))
        print(f"   ✅ PDF generated successfully!")
        print(f"   📄 Location: {pdf_path}")
        print()

        # Verify file exists
        if Path(pdf_path).exists():
            file_size = Path(pdf_path).stat().st_size
            print(f"   📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            print()
            print("=" * 60)
            print("✅ TEST PASSED - PDF generation successful!")
            print("=" * 60)
            return True
        else:
            print("   ❌ Error: PDF file not found after generation")
            return False

    except Exception as e:
        print(f"   ❌ Error generating PDF: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_multiple_scenarios():
    """Test PDF generation with various data scenarios"""
    print("\n" + "=" * 60)
    print("Testing Multiple Scenarios")
    print("=" * 60)
    print()

    output_dir = Path(__file__).parent / "output"

    # Scenario 1: Minimal quotation
    print("Scenario 1: Minimal quotation (products only)...")
    minimal_data = {
        "client_name": "Cliente Mínimo",
        "products": [
            {
                "name": "Isopanel EPS 30 mm",
                "length_m": 5.0,
                "quantity": 10,
                "unit_price_usd": 30.00,
                "total_usd": 1500.00,
                "total_m2": 50.0,
            }
        ],
    }

    try:
        pdf_path = generate_quotation_pdf(
            minimal_data,
            str(
                output_dir
                / f"cotizacion_minimal_{datetime.now().strftime('%H%M%S')}.pdf"
            ),
        )
        print(f"   ✅ Generated: {Path(pdf_path).name}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    print()

    # Scenario 2: Large quotation
    print("Scenario 2: Large quotation (many items)...")
    large_data = create_sample_quotation_data()
    # Add more products
    for i in range(5):
        large_data["products"].append(
            {
                "name": f"Panel Type {i+1}",
                "length_m": 5.0 + i,
                "quantity": 10 + i,
                "unit_price_usd": 30.00 + i,
                "total_usd": (30.00 + i) * (10 + i),
                "total_m2": 50.0 + i * 10,
            }
        )

    try:
        pdf_path = generate_quotation_pdf(
            large_data,
            str(
                output_dir / f"cotizacion_large_{datetime.now().strftime('%H%M%S')}.pdf"
            ),
        )
        print(f"   ✅ Generated: {Path(pdf_path).name}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Scenario 3: Test Bug Fixes (Length_m and automatic total calculation)
    print("Scenario 3: Testing bug fixes (Length_m and missing total_usd)...")
    bug_fix_data = {
        "client_name": "Test Bug Fixes",
        "products": [
            {
                "name": "Isopanel EPS 50 mm (Capital L Test)",
                "Length_m": 5.5,  # Capital L
                "quantity": 10,
                "unit_price_usd": 33.21,
                "total_m2": 55.0,
                "unit_base": "m2",
                # total_usd is missing, should be calculated and displayed
            }
        ],
        "accessories": [
            {
                "name": "Perfil U (Capital L Test)",
                "Length_m": 3.0,  # Capital L
                "quantity": 5,
                "unit_price_usd": 3.90,
                "unit_base": "ml",
                # total_usd is missing, should be calculated and displayed
            }
        ],
    }

    try:
        pdf_path = generate_quotation_pdf(
            bug_fix_data,
            str(
                output_dir
                / f"cotizacion_bugfix_{datetime.now().strftime('%H%M%S')}.pdf"
            ),
        )
        print(f"   ✅ Generated: {Path(pdf_path).name}")
        print(f"   ✅ Verifying calculation in formatted data...")
        formatted = QuotationDataFormatter.format_for_pdf(bug_fix_data)
        prod_total = formatted["products"][0]["total_usd"]
        acc_total = formatted["accessories"][0]["total_usd"]
        print(f"      - Product total: {prod_total} (Expected: 1826.55)")
        print(f"      - Accessory total: {acc_total} (Expected: 58.5)")

        # Verify Length_m display logic doesn't crash
        # (Already verified by generate_quotation_pdf call)

    except Exception as e:
        print(f"   ❌ Failed: {e}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    print()
    success = test_pdf_generation()

    if success:
        print()
        test_multiple_scenarios()
        print()
        print("🎉 All tests completed!")
        print()
        print("Next steps:")
        print("  1. Review generated PDFs in panelin_reports/output/")
        print("  2. Add BMC Uruguay logo to panelin_reports/assets/bmc_logo.png")
        print("  3. Adjust styling in pdf_styles.py if needed")
        print("  4. Integrate with GPT Code Interpreter")
        print()
    else:
        print()
        print("❌ Tests failed. Please check the errors above.")
        sys.exit(1)
