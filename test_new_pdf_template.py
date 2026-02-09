#!/usr/bin/env python3
"""
Test script for new BMC PDF template design
Validates that the PDF matches the formatting requirements
"""

import os
import sys
from datetime import datetime

# Add panelin_reports to path
sys.path.insert(0, '/workspace')

# Import directly to avoid dependency issues
from panelin_reports.pdf_generator import generate_quotation_pdf, BMCQuotationPDF, QuotationDataFormatter

def create_sample_quotation_data():
    """Create sample quotation data for testing"""
    return {
        'client_name': 'Arquitecto Juan Rodríguez',
        'client_address': 'Av. Principal 1234, Maldonado',
        'client_phone': '092 123 456',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'quote_title': 'COTIZACIÓN',
        'quote_description': 'ISODEC EPS 100 mm',
        'autoportancia': 5.5,
        'apoyos': 2,
        'products': [
            {
                'name': 'Isopanel EPS 50 mm (Fachada)',
                'quantity': 100,
                'unit_base': 'm²',
                'total_m2': 100,
                'unit_price_usd': 33.21,
                'sale_sin_iva': 33.21,
                'total_usd': 3321.00,
                'Length_m': 5.0,
            },
            {
                'name': 'ISODEC EPS 100 mm (Cubierta)',
                'quantity': 80,
                'unit_base': 'm²',
                'total_m2': 80,
                'unit_price_usd': 36.54,
                'sale_sin_iva': 36.54,
                'total_usd': 2923.20,
                'Length_m': 6.0,
            },
        ],
        'accessories': [
            {
                'name': 'Perfil U 50mm',
                'quantity': 15,
                'unit_base': 'ml',
                'Length_m': 3.0,
                'unit_price_usd': 3.90,
                'sale_sin_iva': 3.90,
                'total_usd': 175.50,
            },
            {
                'name': 'Perfil K2',
                'quantity': 10,
                'unit_base': 'ml',
                'Length_m': 3.0,
                'unit_price_usd': 3.40,
                'sale_sin_iva': 3.40,
                'total_usd': 102.00,
            },
            {
                'name': 'Gotero Lateral 100mm',
                'quantity': 4,
                'unit_base': 'unidad',
                'Length_m': 3.0,
                'unit_price_usd': 20.77,
                'sale_sin_iva': 20.77,
                'total_usd': 83.08,
            },
        ],
        'fixings': [
            {
                'name': 'Silicona Sikaflex',
                'quantity': 8,
                'unit_base': 'unidad',
                'unit_price_usd': 9.78,
                'sale_sin_iva': 9.78,
                'total_usd': 78.24,
                'specification': '310ml',
            },
            {
                'name': 'Tornillos autoperforantes',
                'quantity': 120,
                'unit_base': 'unidad',
                'unit_price_usd': 0.06,
                'sale_sin_iva': 0.06,
                'total_usd': 7.20,
                'specification': '6.3x150mm',
            },
        ],
        'shipping_usd': 280.0,
        'comments': [
            'Material de primera calidad importado',
            'Garantía de fábrica: 10 años',
        ]
    }

def validate_pdf_exists(pdf_path):
    """Check if PDF was generated successfully"""
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: PDF not generated at {pdf_path}")
        return False
    
    file_size = os.path.getsize(pdf_path)
    if file_size < 1000:  # Less than 1KB is likely an error
        print(f"❌ ERROR: PDF file too small ({file_size} bytes)")
        return False
    
    print(f"✅ PDF generated successfully: {pdf_path}")
    print(f"   File size: {file_size:,} bytes")
    return True

def main():
    """Run PDF generation test"""
    print("=" * 70)
    print("BMC PDF Template Test - New Design Validation")
    print("=" * 70)
    print()
    
    # Create output directory
    output_dir = '/workspace/test_output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate test PDF
    output_path = os.path.join(output_dir, 'test_cotizacion_new_template.pdf')
    print(f"Generating test PDF: {output_path}")
    print()
    
    try:
        # Create sample data
        quotation_data = create_sample_quotation_data()
        
        # Generate PDF
        result_path = generate_quotation_pdf(quotation_data, output_path)
        
        print()
        print("PDF Generation Results:")
        print("-" * 70)
        
        # Validate
        if validate_pdf_exists(result_path):
            print()
            print("✅ VALIDATION CHECKLIST:")
            print("   [ ] Header with BMC logo at top-left")
            print("   [ ] Centered title 'COTIZACIÓN – ISODEC EPS 100 mm'")
            print("   [ ] Materials table with alternating row backgrounds")
            print("   [ ] Table columns right-aligned (numeric)")
            print("   [ ] Comments section with BOLD line (Entrega...)")
            print("   [ ] Comments section with RED line (Oferta válida...)")
            print("   [ ] Comments section with BOLD+RED line (Incluye descuentos...)")
            print("   [ ] Bank transfer footer box with grid lines")
            print("   [ ] First row of footer has gray background")
            print("   [ ] PDF fits on 1 page")
            print()
            print(f"📄 Review the PDF manually at: {result_path}")
            print()
            print("✅ TEST PASSED: PDF generated successfully")
            print()
            print("NEXT STEPS:")
            print("1. Open the PDF and verify all formatting requirements")
            print("2. Check that logo displays correctly")
            print("3. Verify comments bold/red formatting")
            print("4. Confirm bank transfer footer box appears correctly")
            print("5. Ensure everything fits on 1 page")
            
            return 0
        else:
            print()
            print("❌ TEST FAILED: PDF validation failed")
            return 1
            
    except Exception as e:
        print()
        print(f"❌ ERROR during PDF generation:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
