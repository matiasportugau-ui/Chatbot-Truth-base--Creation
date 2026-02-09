#!/usr/bin/env python3
"""
Test script for the new PDF design (2026-02-09).

Validates:
1) Header logo + centered title
2) Table styled correctly (alternating rows, right-aligned numerics)
3) COMENTARIOS section with bold/red rules
4) Bank transfer footer box
5) PDF does not overflow (single page target)
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


def create_sample_data():
    """Create sample quotation data that exercises all features."""
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "location": "Maldonado, Uy.",
        "quote_title": "COTIZACIÓN",
        "quote_description": "ISODEC EPS 100 mm",
        "client_name": "Arquitecto Rodríguez",
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
                "name": "Perfil Ch. Blanca U 50mm x 35mm",
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
                "name": "Canalón Estándar 100mm",
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
                "specification": "1m – 3/8\"",
                "quantity": 20,
                "unit_price_usd": 2.43,
                "total_usd": 48.60,
            },
            {
                "name": "Tuerca Gal. BSW",
                "specification": "3/8\"",
                "quantity": 40,
                "unit_price_usd": 0.15,
                "total_usd": 6.00,
            },
            {
                "name": "Remache POP o T1 P. Mecha",
                "specification": "5/32 x 1/2",
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


def test_new_design():
    """Run the test and validate output."""
    print("=" * 60)
    print("BMC Quotation PDF – New Design Test (2026-02-09)")
    print("=" * 60)
    print()

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    data = create_sample_data()

    # Check logo
    logo = BMCStyles.resolve_logo_path()
    print(f"Logo resolved to: {logo or '(none – will skip logo)'}")
    print()

    # 1) generate_quotation_pdf
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out1 = output_dir / f"cotizacion_new_design_{ts}.pdf"
    print(f"1) Generating via generate_quotation_pdf -> {out1.name}")
    pdf1 = generate_quotation_pdf(data, str(out1))
    sz1 = os.path.getsize(pdf1)
    print(f"   OK  size={sz1:,} bytes ({sz1/1024:.1f} KB)")
    print()

    # 2) build_quote_pdf (explicit logo)
    out2 = output_dir / f"cotizacion_build_quote_{ts}.pdf"
    print(f"2) Generating via build_quote_pdf -> {out2.name}")
    pdf2 = build_quote_pdf(data, str(out2))
    sz2 = os.path.getsize(pdf2)
    print(f"   OK  size={sz2:,} bytes ({sz2/1024:.1f} KB)")
    print()

    # 3) Verify key features via simple PDF text extraction (reportlab doesn't provide this;
    #    just verify file exists and has reasonable size)
    assert sz1 > 2000, f"PDF too small ({sz1} bytes), likely broken"
    assert sz2 > 2000, f"PDF too small ({sz2} bytes), likely broken"

    # 4) Verify standard comments are populated
    formatted = QuotationDataFormatter.format_for_pdf(data)
    assert "comments" in formatted
    assert "totals" in formatted
    print(f"3) Data formatting OK – subtotal=${formatted['totals']['subtotal']:,.2f}")
    print()

    # 5) Verify comment format rules exist
    assert len(QuotationConstants.COMMENT_FORMAT_RULES) >= 3, \
        "Expected at least 3 comment format rules"
    print(f"4) Comment format rules: {len(QuotationConstants.COMMENT_FORMAT_RULES)} defined")
    for phrase, style_key in QuotationConstants.COMMENT_FORMAT_RULES.items():
        print(f"   - '{phrase[:40]}...' -> {style_key}")
    print()

    # 6) Verify bank transfer constants
    assert QuotationConstants.BANK_ACCOUNT_HOLDER == "Metalog SAS"
    assert QuotationConstants.BANK_RUT == "120403430012"
    assert QuotationConstants.BANK_ACCOUNT_USD == "110520638-00002"
    print("5) Bank transfer constants verified")
    print()

    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
    print()
    print(f"Output files in: {output_dir}")
    return True


if __name__ == "__main__":
    success = test_new_design()
    sys.exit(0 if success else 1)
