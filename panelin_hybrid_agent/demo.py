#!/usr/bin/env python3
"""
Demo script for Panelin Hybrid Agent.

Shows the key features:
1. Deterministic quotation calculation
2. Validation of results
3. Product lookup
4. Agent interface (if LangGraph available)

Run: python -m panelin_hybrid_agent.demo
"""

import json
from pathlib import Path

# Ensure we can import from the package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from panelin_hybrid_agent.tools.quotation_calculator import (
    calculate_panel_quote,
    validate_quotation,
    lookup_product_specs,
    calculate_fijaciones,
    calculate_perfileria,
    get_available_products,
)
from panelin_hybrid_agent.agent import PanelinAgent


def demo_basic_quotation():
    """Demonstrate basic quotation calculation."""
    print("\n" + "=" * 60)
    print("DEMO 1: Cotización Básica de Paneles")
    print("=" * 60)
    
    print("\nSolicitud: 10 paneles Isodec EPS 100mm, 6 metros de largo")
    print("-" * 60)
    
    result = calculate_panel_quote(
        panel_type="Isodec_EPS",
        thickness_mm=100,
        length_m=6.0,
        quantity=10,
        include_fijaciones=True,
        include_perfileria=True
    )
    
    # Verify deterministic calculation
    print(f"\n✓ Cálculo verificado: {result['calculation_verified']}")
    print(f"✓ Método: {result['calculation_method']}")
    
    # Show quotation
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                 COTIZACIÓN BMC URUGUAY                        ║
╠══════════════════════════════════════════════════════════════╣
║ Producto: {result['product_id']:<48} ║
║ Cantidad: {result['quantity']} paneles x {6.0}m x 1.12m{' ' * 26}║
║ Área total: {result['area_m2']:.2f} m²{' ' * 41}║
╠══════════════════════════════════════════════════════════════╣
║ DESGLOSE                                                      ║
║ ├─ Paneles:     ${result['panels_subtotal_usd']:>10.2f}{' ' * 32}║
║ ├─ Fijaciones:  ${result['fijaciones_subtotal_usd']:>10.2f}{' ' * 32}║
║ └─ Perfilería:  ${result['perfileria_subtotal_usd']:>10.2f}{' ' * 32}║
╠══════════════════════════════════════════════════════════════╣
║ Subtotal:       ${result['subtotal_usd']:>10.2f}{' ' * 32}║
║ Descuento:      ${result['discount_usd']:>10.2f}{' ' * 32}║
║ Neto:           ${result['total_usd']:>10.2f}{' ' * 32}║
║ IVA (22%):      ${result['total_with_iva_usd'] - result['total_usd']:>10.2f}{' ' * 32}║
╠══════════════════════════════════════════════════════════════╣
║ TOTAL CON IVA:  ${result['total_with_iva_usd']:>10.2f}{' ' * 32}║
╚══════════════════════════════════════════════════════════════╝
""")
    
    return result


def demo_validation():
    """Demonstrate quotation validation."""
    print("\n" + "=" * 60)
    print("DEMO 2: Validación de Cotización")
    print("=" * 60)
    
    result = calculate_panel_quote(
        panel_type="Isopanel_EPS",
        thickness_mm=50,
        length_m=4.0,
        quantity=20,
        discount_percent=10.0
    )
    
    validation = validate_quotation(result)
    
    print(f"\nResultado validación: {'✓ VÁLIDO' if validation['is_valid'] else '✗ INVÁLIDO'}")
    
    if validation['errors']:
        print("\nErrores:")
        for error in validation['errors']:
            print(f"  ✗ {error}")
    
    print("\nVerificaciones pasadas:")
    for check in validation['verification_checks']:
        print(f"  {check}")
    
    return validation


def demo_product_lookup():
    """Demonstrate product specification lookup."""
    print("\n" + "=" * 60)
    print("DEMO 3: Consulta de Especificaciones")
    print("=" * 60)
    
    # Get all products
    products = get_available_products()
    print(f"\nProductos disponibles ({len(products)}):")
    for p in products:
        print(f"  • {p}")
    
    # Lookup specific product
    print("\n" + "-" * 60)
    print("Especificaciones Isodec PIR:")
    
    specs = lookup_product_specs(panel_type="Isodec_PIR")
    
    for product in specs['products']:
        print(f"""
  Espesor: {product['thickness_mm']}mm
  Precio: ${product['price_per_m2']}/m²
  Autoportancia: {product.get('autoportancia_m', 'N/A')}m
  R-térmico: {product.get('resistencia_termica', 'N/A')}
  Ignífugo: {product.get('ignifugo', 'N/A')}
""")


def demo_fijaciones():
    """Demonstrate fixing kit calculation."""
    print("\n" + "=" * 60)
    print("DEMO 4: Cálculo de Kit de Fijación")
    print("=" * 60)
    
    # Metal structure
    print("\nPara estructura metálica:")
    metal = calculate_fijaciones(
        panel_type="Isodec_EPS",
        largo_m=6.0,
        cantidad=10,
        autoportancia_m=5.5,
        base_type="metal"
    )
    
    print(f"  Puntos de fijación: {metal['puntos_fijacion']}")
    print(f"  Varillas: {metal['varillas_qty']}")
    print(f"  Tuercas: {metal['tuercas_qty']}")
    print(f"  Subtotal: ${metal['subtotal_usd']:.2f}")
    
    # Concrete structure
    print("\nPara hormigón:")
    hormigon = calculate_fijaciones(
        panel_type="Isodec_EPS",
        largo_m=6.0,
        cantidad=10,
        autoportancia_m=5.5,
        base_type="hormigon"
    )
    
    print(f"  Puntos de fijación: {hormigon['puntos_fijacion']}")
    print(f"  Varillas: {hormigon['varillas_qty']}")
    print(f"  Tuercas: {hormigon['tuercas_qty']}")
    print(f"  Tacos: {hormigon['tacos_qty']}")
    print(f"  Subtotal: ${hormigon['subtotal_usd']:.2f}")


def demo_agent():
    """Demonstrate agent interface."""
    print("\n" + "=" * 60)
    print("DEMO 5: Interfaz del Agente")
    print("=" * 60)
    
    agent = PanelinAgent()
    
    # Direct quotation (no LLM)
    print("\nCotización directa (sin LLM):")
    result = agent.quote_direct(
        panel_type="Isoroof_3G",
        thickness_mm=30,
        length_m=5.0,
        quantity=8,
        base_type="madera"
    )
    
    if result['success']:
        q = result['quotation']
        print(f"  Producto: {q['product_id']}")
        print(f"  Área: {q['area_m2']:.2f} m²")
        print(f"  Total: ${q['total_with_iva_usd']:.2f}")
        print(f"  Verificado: {q['calculation_verified']}")
    else:
        print(f"  Error: {result['error']}")
    
    # Chat interface (fallback mode)
    print("\nChat interface (modo fallback):")
    response = agent.chat("¿Qué productos tienen disponibles?")
    print(f"  Respuesta: {response['response'][:100]}...")


def demo_comparison():
    """Compare different panel options."""
    print("\n" + "=" * 60)
    print("DEMO 6: Comparativa de Opciones")
    print("=" * 60)
    
    options = [
        ("Isodec_EPS", 100, "Económica"),
        ("Isodec_EPS", 150, "Mejor aislamiento"),
        ("Isodec_PIR", 80, "Ignífuga"),
    ]
    
    print("\nPara 10 paneles de 6m (techo):")
    print("-" * 60)
    
    results = []
    for panel_type, thickness, label in options:
        result = calculate_panel_quote(
            panel_type=panel_type,
            thickness_mm=thickness,
            length_m=6.0,
            quantity=10,
            include_fijaciones=False,
            include_perfileria=False
        )
        results.append((label, result))
    
    print(f"{'Opción':<20} {'Área':<10} {'$/m²':<10} {'Total':<12}")
    print("-" * 60)
    
    for label, r in results:
        price_per_m2 = r['panels_subtotal_usd'] / r['area_m2']
        print(f"{label:<20} {r['area_m2']:.1f} m²   ${price_per_m2:.2f}    ${r['total_with_iva_usd']:.2f}")


def main():
    """Run all demos."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║         PANELIN HYBRID AGENT v2.0 - DEMO                      ║
║         Arquitectura: LLM orquesta, código calcula            ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    try:
        demo_basic_quotation()
        demo_validation()
        demo_product_lookup()
        demo_fijaciones()
        demo_agent()
        demo_comparison()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print("\nTodos los cálculos fueron verificados como deterministas.")
        print("El LLM nunca realizó aritmética directamente.")
        
    except Exception as e:
        print(f"\n❌ Error durante demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
