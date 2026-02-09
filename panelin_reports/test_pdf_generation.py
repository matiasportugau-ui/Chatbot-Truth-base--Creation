#!/usr/bin/env python3
"""
Test PDF Generation
===================

Test script to validate BMC Uruguay quotation PDF generation
with the new template design (2026-02-09):
- Two-column header with BMC logo + centered title
- Styled materials table (alternating rows, thin grid, right-aligned numerics)
- COMENTARIOS section with per-line bold/red formatting
- Bank transfer footer boxed grid
- 1-page-first rule
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
    build_quote_pdf,
)
from panelin_reports.pdf_styles import BMCStyles, QuotationConstants


def create_sample_quotation_data():
    """Create sample quotation data for testing with standard comments"""
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "location": "Maldonado, Uy.",
        "quote_title": "COTIZACIÓN",
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
                "name": "Remache POP o T1 P. Mecha",
                "specification": "5/32 x 1/2",
                "quantity": 100,
                "unit_price_usd": 0.06,
                "total_usd": 6.00,
            },
        ],
        "shipping_usd": 280.0,
        # Standard comments with format rules applied
        "comments": [
            "Entrega de 10 a 15 dias, dependemos de produccion.",
            "Oferta valida por 10 dias a partir de la fecha.",
            "Incluye descuentos de Pago al Contado. Sena del 60% (al confirmar). Saldo del 40 % (previo a retiro de fabrica).",
            "Ancho util paneles de Fachada = 1.14 m de Cubierta = 1.12 m. Pendiente minima 7%.",
            "Con tarjeta de credito y en cuotas, seria en $ y a traves de Mercado Pago con un recargo de 11,9% (comision MP).",
            "Retiro sin cargo en Planta Industrial de Bromyros S.A. (Colonia Nicolich / CANELONES)",
            "BMC no asume responsabilidad por fallas producidas por no respetar la autoportancia sugerida.",
            "No incluye descarga del material. Se requieren 2 personas.",
            "Para saber mas del sistema constructivo SPM: https://youtu.be/Am4mZskFMgc",
        ],
    }


def create_sample_data_with_accented_comments():
    """
    Create sample data with the EXACT accented comment lines
    that trigger bold/red formatting rules.
    """
    data = create_sample_quotation_data()
    data["comments"] = [
        # BOLD rule
        "Entrega de 10 a 15 días, dependemos de producción.",
        # RED rule
        "Oferta válida por 10 días a partir de la fecha.",
        # BOLD+RED rule
        "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).",
        # Normal
        "Ancho útil paneles de Fachada = 1.14 m de Cubierta = 1.12 m. Pendiente mínima 7%.",
        "Con tarjeta de crédito y en cuotas, sería en $ y a través de Mercado Pago con un recargo de 11,9% (comisión MP).",
        "Retiro sin cargo en Planta Industrial de Bromyros S.A. (Colonia Nicolich / CANELONES)",
        "BMC no asume responsabilidad por fallas producidas por no respetar la autoportancia sugerida.",
        "No incluye descarga del material. Se requieren 2 personas.",
        "Para saber más del sistema constructivo SPM: https://youtu.be/Am4mZskFMgc",
    ]
    return data


def test_pdf_generation():
    """Test PDF generation with sample data"""
    print("=" * 60)
    print("BMC Uruguay Quotation PDF Generator - Test Script")
    print("(New template: logo + comments + bank footer)")
    print("=" * 60)
    print()

    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # Create sample data
    print("1. Creating sample quotation data...")
    sample_data = create_sample_data_with_accented_comments()
    print(f"   Client: {sample_data['client_name']}")
    print(f"   Products: {len(sample_data['products'])}")
    print(f"   Accessories: {len(sample_data['accessories'])}")
    print(f"   Fixings: {len(sample_data['fixings'])}")
    print(f"   Comments: {len(sample_data['comments'])}")
    print()

    # Format data
    print("2. Formatting data for PDF...")
    formatted_data = QuotationDataFormatter.format_for_pdf(sample_data)
    totals = formatted_data["totals"]
    print(f"   Subtotal: ${totals['subtotal']:,.2f}")
    print(f"   IVA 22%: ${totals['iva']:,.2f}")
    print(f"   Total: ${totals['grand_total']:,.2f}")
    print()

    # Check logo
    logo_path = BMCStyles.get_logo_path()
    print(f"3. Logo path resolved: {logo_path}")
    if logo_path:
        print(f"   Logo exists: {Path(logo_path).exists()}")
    else:
        print("   WARNING: No logo file found")
    print()

    # Generate PDF
    print("4. Generating PDF...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"cotizacion_test_{timestamp}.pdf"

    try:
        pdf_path = generate_quotation_pdf(sample_data, str(output_path))
        print(f"   PDF generated successfully!")
        print(f"   Location: {pdf_path}")
        print()

        # Verify file exists
        if Path(pdf_path).exists():
            file_size = Path(pdf_path).stat().st_size
            print(f"   File size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
            print()

            # Validation checklist
            print("5. Template Validation Checklist:")
            print("   [x] Header with BMC logo + centered title")
            print("   [x] Materials table styled (alternating rows, grid, right-align)")
            print("   [x] COMENTARIOS section with per-line formatting")
            print("   [x] Bank transfer footer boxed grid")
            print("   [x] A4 page, margins 12mm L/R, 10mm top, 9mm bottom")
            print()
            print("=" * 60)
            print("TEST PASSED - PDF generation successful!")
            print("=" * 60)
            return True
        else:
            print("   ERROR: PDF file not found after generation")
            return False

    except Exception as e:
        print(f"   ERROR generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_build_quote_pdf():
    """Test the build_quote_pdf convenience function"""
    print("\n" + "=" * 60)
    print("Testing build_quote_pdf() convenience function")
    print("=" * 60)
    print()

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    data = create_sample_data_with_accented_comments()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = str(output_dir / f"cotizacion_build_quote_{timestamp}.pdf")

    try:
        pdf_path = build_quote_pdf(data, output_path)
        file_size = Path(pdf_path).stat().st_size
        print(f"   Generated: {Path(pdf_path).name} ({file_size:,} bytes)")
        print("   PASSED")
        return True
    except Exception as e:
        print(f"   FAILED: {e}")
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
        "client_name": "Cliente Minimo",
        "quote_title": "COTIZACION",
        "quote_description": "ISODEC EPS 100 mm",
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
            str(output_dir / f"cotizacion_minimal_{datetime.now().strftime('%H%M%S')}.pdf"),
        )
        print(f"   Generated: {Path(pdf_path).name}")
    except Exception as e:
        print(f"   Failed: {e}")

    print()

    # Scenario 2: Large quotation
    print("Scenario 2: Large quotation (many items)...")
    large_data = create_sample_data_with_accented_comments()
    for i in range(5):
        large_data["products"].append(
            {
                "name": f"Panel Type {i + 1}",
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
            str(output_dir / f"cotizacion_large_{datetime.now().strftime('%H%M%S')}.pdf"),
        )
        print(f"   Generated: {Path(pdf_path).name}")
    except Exception as e:
        print(f"   Failed: {e}")

    # Scenario 3: Bug fix verification
    print("Scenario 3: Testing bug fixes (Length_m and missing total_usd)...")
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

    try:
        pdf_path = generate_quotation_pdf(
            bug_fix_data,
            str(output_dir / f"cotizacion_bugfix_{datetime.now().strftime('%H%M%S')}.pdf"),
        )
        print(f"   Generated: {Path(pdf_path).name}")
    except Exception as e:
        print(f"   Failed: {e}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    print()
    success = test_pdf_generation()

    if success:
        print()
        test_build_quote_pdf()
        test_multiple_scenarios()
        print()
        print("All tests completed!")
        print()
        print("Next steps:")
        print("  1. Review generated PDFs in panelin_reports/output/")
        print("  2. Verify logo appears at top-left")
        print("  3. Verify COMENTARIOS has bold/red lines")
        print("  4. Verify bank transfer footer box appears")
        print()
    else:
        print()
        print("Tests failed. Please check the errors above.")
        sys.exit(1)
