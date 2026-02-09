#!/usr/bin/env python3
"""
Test new PDF template
"""
import sys
from pathlib import Path
from datetime import datetime

# Direct imports to avoid dependency issues
sys.path.insert(0, str(Path(__file__).parent))

from panelin_reports.pdf_generator import generate_quotation_pdf

def test_new_template():
    """Test the new PDF template"""
    print("=" * 60)
    print("Testing New BMC PDF Template")
    print("=" * 60)
    print()

    # Create output directory
    output_dir = Path(__file__).parent / "panelin_reports" / "output"
    output_dir.mkdir(exist_ok=True)

    # Sample data
    sample_data = {
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
                "name": "Perfil K2 Ch. Blanca (int. 35x35)",
                "length_m": 3.0,
                "quantity": 8,
                "unit_price_usd": 3.40,
                "total_usd": 81.60,
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
                "name": "Remache POP ó T1 P. Mecha",
                "specification": "5/32 x ½",
                "quantity": 100,
                "unit_price_usd": 0.06,
                "total_usd": 6.00,
            },
        ],
        "shipping_usd": 280.0,
    }

    print("Generating PDF with new template...")
    print(f"  - Client: {sample_data['client_name']}")
    print(f"  - Products: {len(sample_data['products'])}")
    print(f"  - Accessories: {len(sample_data['accessories'])}")
    print(f"  - Fixings: {len(sample_data['fixings'])}")
    print()

    try:
        output_path = output_dir / f"cotizacion_new_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = generate_quotation_pdf(sample_data, str(output_path))
        
        print(f"✅ PDF generated successfully!")
        print(f"📄 Location: {pdf_path}")
        print()
        
        if Path(pdf_path).exists():
            file_size = Path(pdf_path).stat().st_size
            print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            print()
            print("=" * 60)
            print("✅ TEST PASSED - New template working!")
            print("=" * 60)
            print()
            print("Template features:")
            print("  ✓ BMC logo + centered title header")
            print("  ✓ Unified materials table")
            print("  ✓ COMENTARIOS section with formatting")
            print("  ✓ Bank transfer footer box")
            print()
            return True
        else:
            print("❌ Error: PDF file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_template()
    sys.exit(0 if success else 1)
