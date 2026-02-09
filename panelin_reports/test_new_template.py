#!/usr/bin/env python3
"""
Test Script for New BMC PDF Template (2026-02-09)
==================================================

Validates the new PDF design with:
- Logo header with centered title
- Materials table with alternating rows
- COMENTARIOS section with per-line formatting
- Bank transfer footer box

Run: python3 panelin_reports/test_new_template.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from panelin_reports.pdf_generator import generate_quotation_pdf


def create_test_quotation_data():
    """Create sample quotation data for testing"""
    return {
        'client_name': 'Arquitecto Rodríguez',
        'client_address': 'Av. Italia 2525, Montevideo',
        'client_phone': '099 123 456',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'location': 'Montevideo, Uy.',
        'quote_description': 'ISODEC EPS 100 mm',
        'autoportancia': 5.5,
        'apoyos': 1,
        'products': [
            {
                'name': 'ISODEC EPS 100 mm (Cubierta)',
                'Thickness_mm': 100,
                'Length_m': 6.0,
                'quantity': 30,
                'unit_price_usd': 36.54,
                'total_usd': 6577.20,
                'total_m2': 180.0,
                'unit_base': 'm²',
            },
            {
                'name': 'Isopanel EPS 50 mm (Fachada)',
                'Thickness_mm': 50,
                'Length_m': 3.0,
                'quantity': 50,
                'unit_price_usd': 33.21,
                'total_usd': 4981.50,
                'total_m2': 150.0,
                'unit_base': 'm²',
            },
        ],
        'accessories': [
            {
                'name': 'Perfil U 100mm',
                'Length_m': 3.0,
                'quantity': 20,
                'unit_price_usd': 4.50,
                'total_usd': 270.00,
                'unit_base': 'ml',
            },
            {
                'name': 'Babeta Lateral 100mm',
                'Length_m': 3.0,
                'quantity': 15,
                'unit_price_usd': 5.20,
                'total_usd': 234.00,
                'unit_base': 'ml',
            },
            {
                'name': 'Gotero Lateral 100mm',
                'Length_m': 3.0,
                'quantity': 10,
                'unit_price_usd': 20.77,
                'total_usd': 207.70,
                'unit_base': 'unidad',
            },
        ],
        'fixings': [
            {
                'name': 'Silicona BMC',
                'specification': '280ml cartucho',
                'quantity': 12,
                'unit_price_usd': 9.78,
                'total_usd': 117.36,
                'unit_base': 'unidad',
            },
            {
                'name': 'Tornillos autoperforantes',
                'specification': '6.3 x 150mm',
                'quantity': 200,
                'unit_price_usd': 0.06,
                'total_usd': 12.00,
                'unit_base': 'unidad',
            },
            {
                'name': 'Arandelas EPDM',
                'specification': '19mm',
                'quantity': 200,
                'unit_price_usd': 0.04,
                'total_usd': 8.00,
                'unit_base': 'unidad',
            },
        ],
        'shipping_usd': 280.0,
        'comments': [
            'Custom comment 1',
            'Custom comment 2',
        ]
    }


def test_pdf_generation():
    """Test PDF generation with new template"""
    print("=" * 60)
    print("BMC PDF Template Test (2026-02-09)")
    print("=" * 60)
    print()
    
    # Create output directory
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    # Generate test data
    print("1. Creating test quotation data...")
    test_data = create_test_quotation_data()
    print(f"   ✓ Client: {test_data['client_name']}")
    print(f"   ✓ Products: {len(test_data['products'])}")
    print(f"   ✓ Accessories: {len(test_data['accessories'])}")
    print(f"   ✓ Fixings: {len(test_data['fixings'])}")
    print()
    
    # Generate PDF
    output_path = output_dir / f"test_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    print(f"2. Generating PDF: {output_path.name}")
    
    try:
        pdf_path = generate_quotation_pdf(test_data, str(output_path))
        print(f"   ✓ PDF generated successfully!")
        print()
        
        # Check file size
        file_size = os.path.getsize(pdf_path)
        print(f"3. PDF Details:")
        print(f"   ✓ Path: {pdf_path}")
        print(f"   ✓ Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
        print()
        
        # Validation checklist
        print("4. Validation Checklist:")
        print("   Please manually verify the PDF includes:")
        print("   [ ] Header with BMC logo (left) + centered title (right)")
        print("   [ ] Materials table with alternating row backgrounds")
        print("   [ ] Numeric columns right-aligned")
        print("   [ ] COMENTARIOS: section after table")
        print("   [ ] Comments with bullet points (•)")
        print("   [ ] Specific lines formatted:")
        print("       - 'Entrega de 10 a 15 días...' in BOLD")
        print("       - 'Oferta válida por 10 días...' in RED")
        print("       - 'Incluye descuentos de Pago al Contado...' in BOLD + RED")
        print("   [ ] YouTube URL in plain text")
        print("   [ ] Bank transfer footer box with grid lines")
        print("   [ ] First row of footer has gray background")
        print("   [ ] 'Lea los Términos y Condiciones' in blue + underlined")
        print("   [ ] PDF fits on 1 page")
        print()
        
        print("=" * 60)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()
        print(f"Open the PDF to verify: {pdf_path}")
        print()
        
        return True
        
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        return False


if __name__ == '__main__':
    success = test_pdf_generation()
    sys.exit(0 if success else 1)
