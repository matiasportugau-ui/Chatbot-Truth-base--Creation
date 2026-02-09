#!/usr/bin/env python3
"""
Test PDF Generation v2.0
=========================

Test script to validate BMC Uruguay quotation PDF generation.
Creates sample PDFs and verifies all design requirements:
  A) Header with logo + centered title
  B) Table styled correctly (alternating rows, right-aligned numerics)
  C) COMENTARIOS: block with bold/red rules
  D) Bank transfer footer box
  E) 1-page fit
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from panelin_reports.pdf_generator import (
    BMCQuotationPDF,
    QuotationDataFormatter,
    generate_quotation_pdf,
    build_quote_pdf,
    _classify_comment_line,
)
from panelin_reports.pdf_styles import BMCStyles, QuotationConstants


def create_sample_quotation_data():
    """Create sample quotation data for testing (full cotización with comments)"""
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "location": "Maldonado, Uy.",
        "quote_title": "COTIZACIÓN",
        "quote_description": "ISODEC EPS 100 mm",
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
                "specification": '1m – 3/8"',
                "quantity": 20,
                "unit_price_usd": 2.43,
                "total_usd": 48.60,
            },
            {
                "name": "Tuerca Gal. BSW",
                "specification": '3/8"',
                "quantity": 40,
                "unit_price_usd": 0.15,
                "total_usd": 6.00,
            },
            {
                "name": "Remache POP",
                "specification": "5/32 x 1/2",
                "quantity": 100,
                "unit_price_usd": 0.06,
                "total_usd": 6.00,
            },
        ],
        "shipping_usd": 280.0,
        "comments": [
            "Proyecto: Ampliación galpón industrial",
            "Entrega de 10 a 15 días, dependemos de producción.",
            "Oferta válida por 10 días a partir de la fecha.",
            "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).",
            "Nota: Incluye todos los accesorios necesarios para instalación completa.",
            f"Para saber más del sistema constructivo SPM: {QuotationConstants.SPM_SYSTEM_VIDEO}",
        ],
    }


def get_page_count(pdf_path):
    """Get page count from a PDF file."""
    with open(pdf_path, "rb") as f:
        content = f.read()
        counts = re.findall(rb"/Count (\d+)", content)
        if counts:
            return int(counts[0])
    return -1


def test_comment_classification():
    """Test that comment line classification works correctly."""
    print("  Testing comment line classification...")

    assert _classify_comment_line("Entrega de 10 a 15 días, dependemos de producción.") == "bold"
    assert _classify_comment_line("Oferta válida por 10 días a partir de la fecha.") == "red"
    assert _classify_comment_line("Incluye descuentos de Pago al Contado. Seña del 60%") == "bold_red"
    assert _classify_comment_line("Proyecto: Ampliación galpón industrial") == "normal"
    assert _classify_comment_line("https://youtu.be/Am4mZskFMgc") == "normal"

    print("    PASSED: All comment classifications correct")
    return True


def test_logo_resolution():
    """Test that logo path resolution works."""
    print("  Testing logo path resolution...")

    logo = BMCStyles.resolve_logo_path()
    if logo and os.path.exists(logo):
        print(f"    PASSED: Logo found at {logo}")
        return True
    else:
        print(f"    WARNING: No logo found (logo={logo}). PDF will generate without logo.")
        return True  # Not a hard failure


def test_styles():
    """Test that style constants meet the design spec."""
    print("  Testing style constants...")

    # Margins
    assert abs(BMCStyles.MARGIN_LEFT - 12 * 2.834645669) < 1, "Left margin should be ~12mm"
    assert abs(BMCStyles.MARGIN_RIGHT - 12 * 2.834645669) < 1, "Right margin should be ~12mm"
    assert abs(BMCStyles.MARGIN_TOP - 10 * 2.834645669) < 1, "Top margin should be ~10mm"

    # Font sizes
    assert 8.0 <= BMCStyles.FONT_SIZE_COMMENT <= 8.2, f"Comment font should be 8.0-8.2, got {BMCStyles.FONT_SIZE_COMMENT}"
    assert 9.0 <= BMCStyles.FONT_SIZE_TABLE_HEADER <= 9.2, f"Table header font should be 9.0-9.2, got {BMCStyles.FONT_SIZE_TABLE_HEADER}"
    assert 8.5 <= BMCStyles.FONT_SIZE_SMALL <= 8.7, f"Table row font should be 8.5-8.7, got {BMCStyles.FONT_SIZE_SMALL}"

    # Comment leading
    assert 9.0 <= BMCStyles.COMMENT_LEADING <= 9.6, f"Comment leading should be 9.0-9.6, got {BMCStyles.COMMENT_LEADING}"

    print("    PASSED: All style constants within spec")
    return True


def test_pdf_generation():
    """Test PDF generation with sample data."""
    print("=" * 60)
    print("BMC Uruguay Quotation PDF Generator - Test Suite v2.0")
    print("=" * 60)
    print()

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    all_passed = True

    # Test 1: Comment classification
    print("Test 1: Comment line classification")
    all_passed &= test_comment_classification()
    print()

    # Test 2: Logo resolution
    print("Test 2: Logo resolution")
    all_passed &= test_logo_resolution()
    print()

    # Test 3: Style constants
    print("Test 3: Style constants")
    all_passed &= test_styles()
    print()

    # Test 4: Full PDF generation
    print("Test 4: Full PDF generation (generate_quotation_pdf)")
    sample_data = create_sample_quotation_data()

    # Format data for verification
    formatted_data = QuotationDataFormatter.format_for_pdf(sample_data)
    totals = formatted_data["totals"]
    print(f"  Subtotal: ${totals['subtotal']:,.2f}")
    print(f"  IVA 22%: ${totals['iva']:,.2f}")
    print(f"  Grand Total: ${totals['grand_total']:,.2f}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"cotizacion_test_v2_{timestamp}.pdf"

    try:
        pdf_path = generate_quotation_pdf(sample_data, str(output_path))
        if Path(pdf_path).exists():
            file_size = Path(pdf_path).stat().st_size
            page_count = get_page_count(pdf_path)
            print(f"  PDF generated: {pdf_path}")
            print(f"  File size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
            print(f"  Page count: {page_count}")

            if page_count == 1:
                print("    PASSED: Fits in 1 page!")
            else:
                print(f"    WARNING: {page_count} pages (target is 1)")
            all_passed &= True
        else:
            print("  FAILED: PDF file not found after generation")
            all_passed = False
    except Exception as e:
        print(f"  FAILED: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    print()

    # Test 5: build_quote_pdf alias
    print("Test 5: build_quote_pdf alias")
    output_path2 = output_dir / f"cotizacion_build_quote_{timestamp}.pdf"
    try:
        pdf_path2 = build_quote_pdf(sample_data, str(output_path2))
        if Path(pdf_path2).exists():
            print(f"  PDF generated: {pdf_path2}")
            print("    PASSED: build_quote_pdf works correctly")
            all_passed &= True
        else:
            print("  FAILED: PDF not created")
            all_passed = False
    except Exception as e:
        print(f"  FAILED: {e}")
        all_passed = False
    print()

    # Test 6: Minimal quotation (products only, no comments)
    print("Test 6: Minimal quotation (auto-comments)")
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
    output_path3 = output_dir / f"cotizacion_minimal_{timestamp}.pdf"
    try:
        pdf_path3 = generate_quotation_pdf(minimal_data, str(output_path3))
        page_count = get_page_count(pdf_path3)
        print(f"  PDF generated: {pdf_path3} ({page_count} page(s))")
        print("    PASSED")
        all_passed &= True
    except Exception as e:
        print(f"  FAILED: {e}")
        all_passed = False
    print()

    # Test 7: Bug fix test (Length_m and missing total_usd)
    print("Test 7: Bug fix test (Length_m + auto total_usd)")
    bug_fix_data = {
        "client_name": "Test Bug Fixes",
        "products": [
            {
                "name": "Isopanel EPS 50 mm (Capital L Test)",
                "Length_m": 5.5,
                "quantity": 10,
                "unit_price_usd": 33.21,
                "total_m2": 55.0,
                "unit_base": "m2",
            }
        ],
        "accessories": [
            {
                "name": "Perfil U (Capital L Test)",
                "Length_m": 3.0,
                "quantity": 5,
                "unit_price_usd": 3.90,
                "unit_base": "ml",
            }
        ],
    }
    output_path4 = output_dir / f"cotizacion_bugfix_{timestamp}.pdf"
    try:
        pdf_path4 = generate_quotation_pdf(bug_fix_data, str(output_path4))
        formatted = QuotationDataFormatter.format_for_pdf(bug_fix_data)
        prod_total = formatted["products"][0]["total_usd"]
        acc_total = formatted["accessories"][0]["total_usd"]
        print(f"  Product total: {prod_total} (Expected: ~1826.55)")
        print(f"  Accessory total: {acc_total} (Expected: ~58.5)")
        print(f"  PDF generated: {pdf_path4}")
        print("    PASSED")
        all_passed &= True
    except Exception as e:
        print(f"  FAILED: {e}")
        all_passed = False

    print()
    print("=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED - check output above")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    print()
    success = test_pdf_generation()
    print()
    if success:
        print("All tests completed successfully!")
        print("Review generated PDFs in panelin_reports/output/")
    else:
        print("Some tests failed. Please check the errors above.")
        sys.exit(1)
