#!/usr/bin/env python3
"""
Shopify Catalog Export Tool
Converts Shopify CSV export to GPT-friendly catalog JSON + CSV index.
"""

import json
import csv
import argparse
from datetime import datetime
from pathlib import Path
from shopify_export_parser import ShopifyExportParser


def write_catalog_json(data: dict, output_path: Path):
    """Write catalog JSON file"""
    # Add generation timestamp
    data['meta']['generated_at'] = datetime.now().isoformat()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✅ Wrote catalog JSON: {output_path}")
    print(f"   Size: {file_size_mb:.2f} MB")


def write_catalog_index_csv(data: dict, output_path: Path):
    """Write catalog index CSV"""
    products = data['products_by_handle']
    
    rows = []
    for handle, product in products.items():
        # Collect variant SKUs
        variant_skus = [v['sku'] for v in product.get('variants', []) if v.get('sku')]
        
        # Collect option names
        option_names = []
        for opt_key in ['option1_name', 'option2_name', 'option3_name']:
            if product['options'].get(opt_key):
                option_names.append(product['options'][opt_key])
        
        # Build URL (assuming standard Shopify URL structure)
        url = f"https://bmcuruguay.com.uy/products/{handle}"
        
        row = {
            'handle': handle,
            'title': product.get('title', ''),
            'vendor': product.get('vendor', ''),
            'status': product.get('status', ''),
            'published': 'yes' if product.get('published') else 'no',
            'product_category': product.get('product_category', ''),
            'type': product.get('type', ''),
            'tags': ', '.join(product.get('tags', [])),
            'option_names': ', '.join(option_names),
            'variant_count': len(product.get('variants', [])),
            'variant_skus': ', '.join(variant_skus[:5]),  # First 5 SKUs
            'image_count': len(product.get('images', [])),
            'metafield_count': len(product.get('metafields', {})),
            'url': url
        }
        rows.append(row)
    
    # Sort by handle
    rows.sort(key=lambda x: x['handle'])
    
    fieldnames = [
        'handle', 'title', 'vendor', 'status', 'published',
        'product_category', 'type', 'tags', 'option_names',
        'variant_count', 'variant_skus', 'image_count',
        'metafield_count', 'url'
    ]
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Wrote catalog index CSV: {output_path}")
    print(f"   Products: {len(rows)}")


def write_quality_report(data: dict, output_path: Path):
    """Write optional quality report"""
    meta = data['meta']
    quality = meta['quality_flags']
    
    lines = [
        "# Shopify Catalog Quality Report",
        "",
        f"**Generated**: {meta['generated_at']}",
        f"**Source**: {meta['source_file']}",
        "",
        "## Summary",
        "",
        f"- Total rows processed: {meta['total_rows_processed']}",
        f"- Unique products: {meta['unique_products']}",
        f"- Total variants: {meta['total_variants']}",
        f"- Total images: {meta['total_images']}",
        "",
        "## Quality Flags",
        "",
        f"- Products missing title: {quality['products_missing_title']}",
        f"- Products missing body: {quality['products_missing_body']}",
        f"- Duplicate SKUs found: {quality['duplicate_skus']}",
        "",
        "### Vendor Variations Detected",
        ""
    ]
    
    for vendor in quality['vendor_variations']:
        lines.append(f"- `{vendor}`")
    
    lines.extend([
        "",
        "## Index Summary",
        "",
        f"- SKU mappings: {len(data['indexes']['sku_to_handle'])}",
        f"- Vendors: {len(data['indexes']['by_vendor'])}",
        f"- Types: {len(data['indexes']['by_type'])}",
        f"- Categories: {len(data['indexes']['by_category'])}",
        f"- Tags: {len(data['indexes']['by_tag'])}",
        ""
    ])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Wrote quality report: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert Shopify product export CSV to GPT Knowledge catalog'
    )
    parser.add_argument(
        'csv_path',
        help='Path to Shopify products_export CSV file'
    )
    parser.add_argument(
        '--output-dir',
        default='catalog/out',
        help='Output directory (default: catalog/out)'
    )
    parser.add_argument(
        '--quality-report',
        action='store_true',
        help='Generate quality report markdown'
    )
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        print(f"❌ Error: CSV file not found: {csv_path}")
        return 1
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("SHOPIFY CATALOG EXPORT")
    print("=" * 70)
    print(f"\n📄 Input: {csv_path}")
    print(f"📁 Output: {output_dir}/\n")
    
    # Parse CSV
    print("⏳ Parsing Shopify export...")
    parser_obj = ShopifyExportParser(str(csv_path))
    catalog_data = parser_obj.parse()
    
    print(f"✅ Parsed {catalog_data['meta']['unique_products']} products")
    print(f"   - {catalog_data['meta']['total_variants']} variants")
    print(f"   - {catalog_data['meta']['total_images']} images\n")
    
    # Write outputs
    json_path = output_dir / 'shopify_catalog_v1.json'
    csv_index_path = output_dir / 'shopify_catalog_index_v1.csv'
    
    write_catalog_json(catalog_data, json_path)
    write_catalog_index_csv(catalog_data, csv_index_path)
    
    if args.quality_report:
        report_path = output_dir / 'shopify_catalog_quality.md'
        write_quality_report(catalog_data, report_path)
    
    print("\n" + "=" * 70)
    print("✅ EXPORT COMPLETE")
    print("=" * 70)
    print(f"\nFiles generated:")
    print(f"  1. {json_path}")
    print(f"  2. {csv_index_path}")
    if args.quality_report:
        print(f"  3. {output_dir / 'shopify_catalog_quality.md'}")
    
    print("\n📤 Next steps:")
    print("  1. Upload shopify_catalog_v1.json to GPT Knowledge Base")
    print("  2. Reference shopify_catalog_index_v1.csv for quick lookups")
    print("  3. See catalog/README.md for integration guide\n")
    
    return 0


if __name__ == '__main__':
    exit(main())
