#!/usr/bin/env python3
"""
Generate comprehensive multi-supplier cost matrix JSON optimized for GPT Analyze.
Structure: Option A (by supplier/proveedor)
Includes: All fields, GPT-friendly descriptions, keywords, searchable text
"""
import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from panelin_improvements.cost_matrix_tools.redesign_tool import CostMatrixRedesigner

# Suppliers to include
INCLUDED_SUPPLIERS = {
    'BROMYROS', 'ALAMBRESA', 'ARMCO', 'BECAM', 
    'HM RUBBER', 'R y C Tornillos'
}

def normalize_supplier(name: str) -> str:
    """Normalize supplier names to handle variations"""
    name_upper = name.upper().strip()
    # Handle variations in HTML filenames
    if 'HM RUBBER' in name_upper or 'HMRUBBER' in name_upper:
        return 'HM RUBBER'
    if 'R Y C' in name_upper or 'RYC' in name_upper or 'R y C' in name:
        return 'R y C Tornillos'
    return name.strip()

def _get_usage_context(category: str, thickness: Optional[str]) -> str:
    """Generate usage context for the product"""
    contexts = {
        'isoroof_foil': 'Ideal para techos livianos residenciales y comerciales. Excelente aislamiento térmico y acústico.',
        'isoroof': 'Panel aislante para techos livianos. Aplicación en viviendas, galpones y estructuras comerciales.',
        'isoroof_plus': 'Panel premium para techos livianos con mayor resistencia y durabilidad. Requiere mínimo 800 m².',
        'isoroof_colonial': 'Panel estilo colonial para techos. Estética tradicional con aislamiento moderno.',
        'isodec_eps': 'Panel para cubiertas pesadas. Aplicación en estructuras de hormigón. Excelente resistencia estructural.',
        'isodec_pir': 'Panel ignífugo para cubiertas pesadas. Ideal para industrias y depósitos. Alta resistencia al fuego.',
        'isopanel_eps': 'Panel para paredes y fachadas. Aplicación en construcción seca. Aislamiento térmico y acústico.',
        'isowall_pir': 'Panel ignífugo para paredes. Ideal para aplicaciones industriales y comerciales.',
        'isofrig': 'Panel especializado para cámaras frigoríficas y cuartos fríos. Control de temperatura extremo.',
        'gotero_frontal': 'Accesorio para sellado frontal de paneles. Previene filtraciones de agua.',
        'gotero_lateral': 'Accesorio para sellado lateral de paneles. Junta entre paneles.',
        'babeta': 'Accesorio para terminación inferior de paneles. Protección contra agua.',
        'canalon': 'Sistema de canalón para recolección de agua de lluvia.',
        'cumbrera': 'Accesorio para terminación superior de techos. Sellado en cumbrera.',
        'perfil': 'Perfil estructural para fijación de paneles.',
        'anclaje': 'Sistema de fijación para paneles. Varillas, tuercas, tacos y tornillos.',
        'flete': 'Servicio de transporte y entrega de productos.',
        'accesorio': 'Accesorio complementario para instalación de paneles.',
        'otros': 'Producto general para construcción.'
    }
    
    base_context = contexts.get(category, 'Producto para construcción y aislamiento.')
    
    if thickness:
        base_context += f" Espesor disponible: {thickness}mm."
    
    return base_context

def add_gpt_analyze_optimizations(product: Dict[str, Any]) -> Dict[str, Any]:
    """Add GPT Analyze-friendly fields: descriptions, keywords, searchable text"""
    code = product.get('codigo', '')
    name = product.get('nombre', '')
    category = product.get('categoria', '')
    thickness = product.get('espesor_mm', '')
    supplier = product.get('metadata', {}).get('proveedor', '')
    
    # Generate searchable description
    description_parts = []
    if name:
        description_parts.append(name)
    if thickness:
        description_parts.append(f"Espesor: {thickness}mm")
    if category:
        cat_names = {
            'isoroof_foil': 'Panel aislante techo liviano con lámina',
            'isoroof': 'Panel aislante techo liviano',
            'isoroof_plus': 'Panel aislante techo liviano premium',
            'isoroof_colonial': 'Panel aislante techo estilo colonial',
            'isodec_eps': 'Panel aislante cubierta pesada EPS',
            'isodec_pir': 'Panel aislante cubierta pesada PIR',
            'isopanel_eps': 'Panel aislante pared EPS',
            'isowall_pir': 'Panel aislante pared PIR',
            'isofrig': 'Panel aislante cámaras frigoríficas',
            'gotero_frontal': 'Gotero frontal para paneles',
            'gotero_lateral': 'Gotero lateral para paneles',
            'babeta': 'Babeta para paneles',
            'canalon': 'Canalón para paneles',
            'cumbrera': 'Cumbrera para paneles',
            'perfil': 'Perfil para paneles',
            'anclaje': 'Sistema de anclaje',
            'flete': 'Servicio de flete',
            'accesorio': 'Accesorio para paneles',
            'otros': 'Producto general'
        }
        description_parts.append(cat_names.get(category, category))
    if supplier:
        description_parts.append(f"Proveedor: {supplier}")
    
    description = ". ".join(description_parts) + "."
    
    # Generate keywords
    keywords = []
    keywords.append(code.lower())
    keywords.append(name.lower())
    if thickness:
        keywords.append(f"{thickness}mm")
        keywords.append(f"espesor {thickness}")
    keywords.append(category)
    if supplier:
        keywords.append(supplier.lower())
    
    # Extract additional keywords from name
    name_lower = name.lower()
    if 'panel' in name_lower:
        keywords.append('panel')
    if 'aislante' in name_lower:
        keywords.append('aislante')
    if 'techo' in name_lower or 'cubierta' in name_lower:
        keywords.append('techo')
    if 'pared' in name_lower or 'fachada' in name_lower:
        keywords.append('pared')
    if 'frigorifico' in name_lower or 'frigorifica' in name_lower:
        keywords.append('frigorifico')
    
    # Generate searchable text (concatenated for GPT search)
    searchable_text = f"{code} {name} {category} {thickness}mm {supplier}".lower()
    
    # Add GPT Analyze fields to metadata
    if 'metadata' not in product:
        product['metadata'] = {}
    
    product['metadata']['gpt_analyze'] = {
        'description': description,
        'keywords': list(set(keywords)),  # Remove duplicates
        'searchable_text': searchable_text,
        'category_display': category.replace('_', ' ').title(),
        'usage_context': _get_usage_context(category, thickness)
    }
    
    return product

def create_multi_supplier_structure(products_by_supplier: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """Create Option A structure: grouped by supplier"""
    
    # Calculate totals
    total_products = sum(len(products) for products in products_by_supplier.values())
    all_products = []
    for products in products_by_supplier.values():
        all_products.extend(products)
    
    # Build supplier statistics
    supplier_stats = {}
    for supplier, products in products_by_supplier.items():
        supplier_stats[supplier] = {
            'total_productos': len(products),
            'productos_activos': len([p for p in products if p.get('estado') == 'ACT.']),
            'productos_con_costo': len([p for p in products if p.get('costos', {}).get('fabrica_directo', {}).get('costo_base_usd_iva')]),
            'productos_con_precio_web': len([p for p in products if p.get('precios', {}).get('web_stock', {}).get('web_venta_iva_usd')]),
            'categorias': sorted(list(set(p.get('categoria', 'otros') for p in products)))
        }
    
    # Build indexes across all suppliers
    indexes = {
        'by_code': {},
        'by_supplier': {},
        'by_category': {},
        'by_thickness': {}
    }
    
    for supplier, products in products_by_supplier.items():
        indexes['by_supplier'][supplier] = [p.get('codigo') for p in products]
        
        for idx, product in enumerate(products):
            code = product.get('codigo', '')
            category = product.get('categoria', 'otros')
            thickness = product.get('espesor_mm')
            
            # Index by code
            indexes['by_code'][code] = {
                'codigo': code,
                'nombre': product.get('nombre', ''),
                'categoria': category,
                'proveedor': supplier,
                'path': f'proveedores.{supplier}.productos.todos[{idx}]'
            }
            
            # Index by category
            if category not in indexes['by_category']:
                indexes['by_category'][category] = []
            indexes['by_category'][category].append({
                'codigo': code,
                'proveedor': supplier
            })
            
            # Index by thickness
            if thickness:
                if thickness not in indexes['by_thickness']:
                    indexes['by_thickness'][thickness] = []
                indexes['by_thickness'][thickness].append({
                    'codigo': code,
                    'proveedor': supplier
                })
    
    # Structure by supplier (Option A)
    proveedores = {}
    for supplier, products in products_by_supplier.items():
        # Organize products by category within supplier
        products_by_cat = {}
        for product in products:
            category = product.get('categoria', 'otros')
            if category not in products_by_cat:
                products_by_cat[category] = []
            products_by_cat[category].append(product)
        
        proveedores[supplier] = {
            'nombre': supplier,
            'total_productos': len(products),
            'estadisticas': supplier_stats[supplier],
            'productos': {
                'por_categoria': products_by_cat,
                'todos': products
            }
        }
    
    # Create final structure
    structure = {
        'meta': {
            'nombre': 'Matriz de Costos y Ventas 2026 - Multi-Proveedor',
            'version': '3.0.0',
            'fecha_creacion': datetime.now().isoformat(),
            'optimizado_para': 'GPT Analyze - File Upload',
            'estructura': 'Option A - Agrupado por Proveedor',
            'total_proveedores': len(products_by_supplier),
            'total_productos': total_products,
            'proveedores_incluidos': sorted(list(products_by_supplier.keys())),
            'estadisticas_globales': {
                'productos_activos': len([p for p in all_products if p.get('estado') == 'ACT.']),
                'productos_con_costo': len([p for p in all_products if p.get('costos', {}).get('fabrica_directo', {}).get('costo_base_usd_iva')]),
                'productos_con_precio_web': len([p for p in all_products if p.get('precios', {}).get('web_stock', {}).get('web_venta_iva_usd')]),
                'categorias_unicas': sorted(list(set(p.get('categoria', 'otros') for p in all_products)))
            }
        },
        'reglas_precios': {
            'empresa': {
                'descripcion': 'Empresas descuentan IVA (22%)',
                'precio_a_usar': 'precios.empresa.venta_iva_usd',
                'nota': 'Para empresas: usar precio + IVA, luego descontar IVA al final'
            },
            'particular': {
                'descripcion': 'Particulares no descuentan IVA',
                'precio_a_usar': 'precios.particular.consumidor_iva_inc_usd',
                'nota': 'Para particulares: usar precio con IVA incluido directamente'
            },
            'cotizacion': {
                'descripcion': 'SIEMPRE usar precio + IVA y agregar IVA al final',
                'precio_base': 'precios.empresa.venta_iva_usd',
                'iva': 0.22,
                'nota': 'En cotizaciones, mostrar precio unitario con IVA incluido'
            }
        },
        'indices': indexes,
        'proveedores': proveedores
    }
    
    return structure

def main():
    # Paths
    html_dir = Path('wiki/matriz de costos adaptacion /MATRIZ de COSTOS y VENTAS 2026 2.xlsx')
    output_path = Path('wiki/matriz de costos adaptacion /redesigned/COST_MATRIX_ALL_SUPPLIERS_GPT_ANALYZE.json')
    
    if not html_dir.exists():
        print(f'Error: Directory not found: {html_dir}')
        return
    
    print('=' * 60)
    print('Generating Multi-Supplier Cost Matrix for GPT Analyze')
    print('=' * 60)
    
    redesigner = CostMatrixRedesigner()
    all_products_by_supplier: Dict[str, List[Dict]] = {}
    
    # Process HTML files
    print('\n1. Processing suppliers...')
    for html_file in sorted(html_dir.glob('*.html')):
        supplier_name = normalize_supplier(html_file.stem)
        
        if supplier_name not in INCLUDED_SUPPLIERS:
            print(f'   ⏭️  Skipping: {supplier_name}')
            continue
        
        print(f'   ✅ Processing: {supplier_name}')
        products = redesigner._parse_html_file(str(html_file))
        
        # Add supplier metadata and GPT optimizations
        optimized_products = []
        for product in products:
            product.setdefault('metadata', {})['proveedor'] = supplier_name
            optimized_product = add_gpt_analyze_optimizations(product)
            optimized_products.append(optimized_product)
        
        all_products_by_supplier[supplier_name] = optimized_products
        print(f'      Found {len(optimized_products)} products')
    
    print(f'\n2. Total suppliers: {len(all_products_by_supplier)}')
    print(f'   Total products: {sum(len(p) for p in all_products_by_supplier.values())}')
    
    # Create structure
    print('\n3. Creating optimized structure...')
    structure = create_multi_supplier_structure(all_products_by_supplier)
    
    # Save
    print(f'\n4. Saving to: {output_path}')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print('\n' + '=' * 60)
    print('✅ Generation Complete!')
    print('=' * 60)
    print(f'File: {output_path}')
    print(f'Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB')
    print(f'Suppliers: {len(all_products_by_supplier)}')
    print(f'Products: {structure["meta"]["total_productos"]}')
    print(f'Categories: {len(structure["meta"]["estadisticas_globales"]["categorias_unicas"])}')
    print('\n📋 GPT Analyze Optimizations:')
    print('   ✅ Searchable descriptions')
    print('   ✅ Keywords for each product')
    print('   ✅ Usage context')
    print('   ✅ Category tags')
    print('   ✅ Cross-supplier indexes')
    print('=' * 60)

if __name__ == '__main__':
    main()
