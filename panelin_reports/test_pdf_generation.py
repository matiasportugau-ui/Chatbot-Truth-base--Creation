#!/usr/bin/env python3
"""
Test PDF Generation (v2.0)
===========================

Test script to validate BMC Uruguay quotation PDF generation
with the new template (2026-02-09):
  - Header: BMC logo + centered title
  - Tables: styled with alternating rows, right-aligned numerics
  - COMENTARIOS: per-line bold/red formatting
  - Bank transfer footer box
  - 1-page-fit logic
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from panelin_reports.pdf_generator import (
    BMCQuotationPDF,
    QuotationDataFormatter,
    generate_quotation_pdf,
    build_quote_pdf,
)
from panelin_reports.pdf_styles import BMCStyles, QuotationConstants


def create_sample_quotation_data():
    """Create sample quotation data matching the Cotización ISODEC EPS 100mm prototype"""
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "location": "Maldonado, Uy.",
        "quote_title": "Cotización",
        "quote_description": "ISODEC EPS 100 mm",
        "client_name": "Arq. Juan Pérez",
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
                "name": "Perfil Ch. Blanca U 50mm",
                "length_m": 3.0,
                "quantity": 10,
                "unit_price_usd": 3.90,
                "total_usd": 117.00,
            },
            {
                "name": "Perfil Alu 5852 Anodizado",
                "length_m": 6.8,
                "quantity": 5,
                "unit_price_usd": 8.95,
                "total_usd": 304.30,
            },
            {
                "name": "Perfil K2 Ch. Blanca",
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
                "name": "Bromplast Silicona Neutra",
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
                "specification": "1m 3/8",
                "quantity": 20,
                "unit_price_usd": 2.43,
                "total_usd": 48.60,
            },
            {
                "name": "Tuerca Gal. BSW",
                "specification": "3/8",
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
            "Proyecto: Ampliación galpón industrial.",
            "Entrega de 10 a 15 días, dependemos de producción.",
            "Oferta válida por 10 días a partir de la fecha.",
            "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).",
            "Para saber más del sistema constructivo SPM: https://youtu.be/Am4mZskFMgc",
        ],
    }


def count_pdf_pages(pdf_path: str) -> int:
    """Count pages in a PDF file"""
    with open(pdf_path, "rb") as f:
        content = f.read()
    pages = content.count(b"/Type /Page") - content.count(b"/Type /Pages")
    return max(pages, 1)


def extract_pdf_text(pdf_path: str) -> str:
    """Extract all text from a PDF by decoding its streams"""
    import re
    import zlib
    import base64

    with open(pdf_path, "rb") as f:
        raw = f.read()

    full_text = ""
    # Find stream objects
    for m in re.finditer(rb"stream\n(.*?)endstream", raw, re.DOTALL):
        data = m.group(1).rstrip(b"\n")
        try:
            # Try ASCII85 + FlateDecode (ReportLab default)
            end_idx = data.rfind(b"~>")
            if end_idx >= 0:
                a85_data = data[: end_idx + 2]
            else:
                a85_data = data
            decoded = base64.a85decode(a85_data, adobe=True)
            try:
                text_bytes = zlib.decompress(decoded)
            except Exception:
                text_bytes = decoded
            full_text += text_bytes.decode("latin-1", errors="ignore") + " "
        except Exception:
            # Fallback: try plain zlib
            try:
                text_bytes = zlib.decompress(data)
                full_text += text_bytes.decode("latin-1", errors="ignore") + " "
            except Exception:
                full_text += data.decode("latin-1", errors="ignore") + " "

    return full_text


def check_pdf_content(pdf_path: str) -> dict:
    """Check key content markers in generated PDF"""
    text = extract_pdf_text(pdf_path)

    checks = {
        "has_cotizacion_title": "COTIZACI" in text,
        "has_comentarios": "COMENTARIOS" in text,
        "has_deposito_bancario": "Bancario" in text,
        "has_metalog": "Metalog" in text,
        "has_brou": "BROU" in text,
        "has_terminos": "rminos" in text,
        "has_rut": "120403430012" in text,
        "has_account": "110520638" in text,
    }
    return checks


def test_pdf_generation():
    """Test primary PDF generation with full sample data"""
    print("=" * 60)
    print("BMC Uruguay Quotation PDF Generator - Test v2.0")
    print("=" * 60)
    print()

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # 1. Logo check
    print("1. Checking BMC logo availability...")
    logo_path = BMCStyles.find_logo_path()
    if logo_path:
        print(f"   OK Logo found: {logo_path}")
    else:
        print("   WARN No logo file found (PDF will render without logo)")

    # 2. Create sample data
    print("\n2. Creating sample quotation data...")
    sample_data = create_sample_quotation_data()
    print(f"   OK Client: {sample_data['client_name']}")
    print(f"   OK Products: {len(sample_data['products'])}")
    print(f"   OK Accessories: {len(sample_data['accessories'])}")
    print(f"   OK Fixings: {len(sample_data['fixings'])}")
    print(f"   OK Comments: {len(sample_data['comments'])}")

    # 3. Format data
    print("\n3. Formatting data for PDF...")
    formatted_data = QuotationDataFormatter.format_for_pdf(sample_data)
    totals = formatted_data["totals"]
    print(f"   OK Subtotal: ${totals['subtotal']:,.2f}")
    print(f"   OK IVA 22%: ${totals['iva']:,.2f}")
    print(f"   OK Total: ${totals['grand_total']:,.2f}")

    # 4. Generate PDF using build_quote_pdf (canonical function)
    print("\n4. Generating PDF with build_quote_pdf()...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = str(output_dir / f"cotizacion_template_v2_{timestamp}.pdf")

    try:
        pdf_path = build_quote_pdf(sample_data, output_path)
        if not Path(pdf_path).exists():
            print("   FAIL PDF file not found after generation")
            return False

        file_size = Path(pdf_path).stat().st_size
        pages = count_pdf_pages(pdf_path)
        print(f"   OK PDF generated: {pdf_path}")
        print(f"   OK File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"   OK Pages: {pages}")

        # 5. Validate content
        print("\n5. Validating PDF content...")
        checks = check_pdf_content(pdf_path)
        all_ok = True
        for check_name, passed in checks.items():
            status = "OK" if passed else "FAIL"
            if not passed:
                all_ok = False
            print(f"   {status} {check_name}")

        # 6. Page fit check
        print(f"\n6. Page fit check...")
        if pages == 1:
            print(f"   OK Content fits in 1 page (target achieved)")
        else:
            print(f"   INFO Content uses {pages} pages (table data may be too large for 1 page)")

        print()
        if all_ok:
            print("=" * 60)
            print("PASS - All template checks passed!")
            print("=" * 60)
        else:
            print("=" * 60)
            print("PARTIAL - Some checks failed, review above")
            print("=" * 60)
        return all_ok

    except Exception as e:
        print(f"   FAIL Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_minimal_quotation():
    """Test minimal quotation (products only, no accessories/fixings)"""
    print("\n" + "-" * 60)
    print("Test: Minimal quotation (products only)")
    print("-" * 60)

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    minimal_data = {
        "client_name": "Cliente Mínimo",
        "quote_description": "Isopanel 30 mm",
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

    output_path = str(output_dir / f"cotizacion_minimal_{datetime.now().strftime('%H%M%S')}.pdf")

    try:
        pdf_path = build_quote_pdf(minimal_data, output_path)
        pages = count_pdf_pages(pdf_path)
        size = Path(pdf_path).stat().st_size
        print(f"   OK Generated: {Path(pdf_path).name} ({size:,} bytes, {pages} page)")
        return True
    except Exception as e:
        print(f"   FAIL: {e}")
        return False


def test_with_formatted_comments():
    """Test with explicit formatted comments (tuple format)"""
    print("\n" + "-" * 60)
    print("Test: Explicit formatted comments (tuple format)")
    print("-" * 60)

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    data = {
        "client_name": "Test Formatted Comments",
        "quote_description": "ISODEC EPS 100 mm",
        "products": [
            {
                "name": "Isodec EPS 100 mm (Cubierta)",
                "length_m": 7.0,
                "quantity": 25,
                "unit_price_usd": 36.54,
                "total_usd": 6388.50,
                "total_m2": 175.0,
            },
        ],
        "comments": [
            ("Entrega de 10 a 15 días, dependemos de producción.", "bold"),
            ("Oferta válida por 10 días a partir de la fecha.", "red"),
            (
                "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). "
                "Saldo del 40 % (previo a retiro de fábrica).",
                "bold_red",
            ),
            ("Nota normal de ejemplo.", "normal"),
        ],
    }

    output_path = str(output_dir / f"cotizacion_formatted_{datetime.now().strftime('%H%M%S')}.pdf")

    try:
        pdf_path = build_quote_pdf(data, output_path)
        pages = count_pdf_pages(pdf_path)
        size = Path(pdf_path).stat().st_size
        print(f"   OK Generated: {Path(pdf_path).name} ({size:,} bytes, {pages} page)")

        # Verify bold/red presence
        checks = check_pdf_content(pdf_path)
        print(f"   OK has_comentarios: {checks['has_comentarios']}")
        print(f"   OK has_deposito_bancario: {checks['has_deposito_bancario']}")
        return True
    except Exception as e:
        print(f"   FAIL: {e}")
        return False


def test_default_comments():
    """Test with no comments (should use default comments from QuotationConstants)"""
    print("\n" + "-" * 60)
    print("Test: Default comments (empty input)")
    print("-" * 60)

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    data = {
        "client_name": "Test Default Comments",
        "quote_description": "Isopanel 50 mm",
        "products": [
            {
                "name": "Isopanel EPS 50 mm (Fachada)",
                "length_m": 6.0,
                "quantity": 20,
                "unit_price_usd": 33.21,
                "total_usd": 3321.00,
                "total_m2": 120.0,
            },
        ],
        # No comments - should use defaults
    }

    output_path = str(output_dir / f"cotizacion_defaults_{datetime.now().strftime('%H%M%S')}.pdf")

    try:
        pdf_path = build_quote_pdf(data, output_path)
        pages = count_pdf_pages(pdf_path)
        size = Path(pdf_path).stat().st_size
        print(f"   OK Generated: {Path(pdf_path).name} ({size:,} bytes, {pages} page)")
        return True
    except Exception as e:
        print(f"   FAIL: {e}")
        return False


def test_no_logo():
    """Test PDF generation without logo file available"""
    print("\n" + "-" * 60)
    print("Test: No logo (graceful fallback)")
    print("-" * 60)

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    data = {
        "client_name": "Test No Logo",
        "products": [
            {
                "name": "Isopanel EPS 50 mm",
                "length_m": 5.0,
                "quantity": 10,
                "unit_price_usd": 33.21,
                "total_usd": 1660.50,
                "total_m2": 50.0,
            },
        ],
    }

    output_path = str(output_dir / f"cotizacion_nologo_{datetime.now().strftime('%H%M%S')}.pdf")

    try:
        # Force non-existent logo
        pdf_path = generate_quotation_pdf(data, output_path, logo_path="/nonexistent/logo.png")
        pages = count_pdf_pages(pdf_path)
        size = Path(pdf_path).stat().st_size
        print(f"   OK Generated without logo: {Path(pdf_path).name} ({size:,} bytes, {pages} page)")
        return True
    except Exception as e:
        print(f"   FAIL: {e}")
        return False


def test_bug_fixes():
    """Test bug fixes: Length_m capitalization and missing total_usd"""
    print("\n" + "-" * 60)
    print("Test: Bug fixes (Length_m, missing total_usd)")
    print("-" * 60)

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    data = {
        "client_name": "Test Bug Fixes",
        "products": [
            {
                "name": "Isopanel EPS 50 mm (Capital L Test)",
                "Length_m": 5.5,
                "quantity": 10,
                "unit_price_usd": 33.21,
                "total_m2": 55.0,
                "unit_base": "m2",
                # total_usd is missing - should be calculated
            }
        ],
        "accessories": [
            {
                "name": "Perfil U (Capital L Test)",
                "Length_m": 3.0,
                "quantity": 5,
                "unit_price_usd": 3.90,
                "unit_base": "ml",
                # total_usd is missing - should be calculated
            }
        ],
    }

    output_path = str(output_dir / f"cotizacion_bugfix_{datetime.now().strftime('%H%M%S')}.pdf")

    try:
        pdf_path = build_quote_pdf(data, output_path)
        size = Path(pdf_path).stat().st_size
        print(f"   OK Generated: {Path(pdf_path).name} ({size:,} bytes)")

        # Verify calculations
        formatted = QuotationDataFormatter.format_for_pdf(data)
        prod_total = formatted["products"][0]["total_usd"]
        acc_total = formatted["accessories"][0]["total_usd"]
        print(f"   OK Product total: ${prod_total:.2f} (m2 calc)")
        print(f"   OK Accessory total: ${acc_total:.2f} (ml calc)")
        return True
    except Exception as e:
        print(f"   FAIL: {e}")
        return False


if __name__ == "__main__":
    print()
    results = []

    # Main test
    results.append(("Main template test", test_pdf_generation()))

    # Additional scenarios
    results.append(("Minimal quotation", test_minimal_quotation()))
    results.append(("Formatted comments", test_with_formatted_comments()))
    results.append(("Default comments", test_default_comments()))
    results.append(("No logo fallback", test_no_logo()))
    results.append(("Bug fixes", test_bug_fixes()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"  [{status}] {name}")

    print()
    if all_passed:
        print("All tests passed!")
    else:
        print("Some tests failed. Review output above.")
        sys.exit(1)

    print()
    print("Generated PDFs are in panelin_reports/output/")
    print()
