#!/usr/bin/env python3
"""
Shopify Product Export Parser
Parses Shopify CSV exports and normalizes into structured catalog data.
"""

import csv
import re
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from html.parser import HTMLParser


class HTMLStripper(HTMLParser):
    """Strip HTML tags to get plain text"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    
    def handle_data(self, data):
        self.text.append(data)
    
    def get_text(self):
        return ''.join(self.text)


def strip_html(html: str) -> str:
    """Convert HTML to plain text"""
    if not html:
        return ""
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_text().strip()


class ShopifyExportParser:
    """Parses Shopify product export CSV"""
    
    # Columns to skip (prices/costs)
    SKIP_COLUMNS = {
        'Variant Price',
        'Variant Compare At Price',
        'Cost per item',
        'Unit Price Total Measure',
        'Unit Price Total Measure Unit',
        'Unit Price Base Measure',
        'Unit Price Base Measure Unit'
    }
    
    # Metafield column pattern
    METAFIELD_PATTERN = re.compile(r'\(product\.metafields\.(.*?)\)')
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.products_by_handle: Dict[str, Dict[str, Any]] = {}
        self.sku_to_handle: Dict[str, str] = {}
        self.stats = {
            'total_rows': 0,
            'unique_handles': 0,
            'total_variants': 0,
            'total_images': 0,
            'missing_title': [],
            'missing_body': [],
            'duplicate_skus': [],
            'vendor_variations': set()
        }
    
    def parse(self) -> Dict[str, Any]:
        """Parse the CSV and return structured data"""
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                self.stats['total_rows'] += 1
                self._process_row(row)
        
        # Finalize stats
        self.stats['unique_handles'] = len(self.products_by_handle)
        self.stats['vendor_variations'] = list(self.stats['vendor_variations'])
        
        return {
            'meta': self._generate_meta(),
            'products_by_handle': self.products_by_handle,
            'indexes': self._generate_indexes()
        }
    
    def _process_row(self, row: Dict[str, str]):
        """Process a single CSV row"""
        handle = row.get('Handle', '').strip()
        if not handle:
            return
        
        # Initialize product if first time seeing this handle
        if handle not in self.products_by_handle:
            self.products_by_handle[handle] = self._init_product(row)
        
        product = self.products_by_handle[handle]
        
        # Merge title/body if present (first occurrence wins)
        if row.get('Title') and not product.get('title'):
            product['title'] = row['Title'].strip()
        
        if row.get('Body (HTML)') and not product.get('body_html'):
            body_html = row['Body (HTML)'].strip()
            product['body_html'] = body_html
            product['body_text'] = strip_html(body_html)
        
        # Merge SEO if present
        if row.get('SEO Title') and not product.get('seo_title'):
            product['seo_title'] = row['SEO Title'].strip()
        
        if row.get('SEO Description') and not product.get('seo_description'):
            product['seo_description'] = row['SEO Description'].strip()
        
        # Merge option names (from first variant row)
        if row.get('Option1 Name') and not product['options'].get('option1_name'):
            product['options']['option1_name'] = row['Option1 Name'].strip()
        if row.get('Option2 Name') and not product['options'].get('option2_name'):
            product['options']['option2_name'] = row['Option2 Name'].strip()
        if row.get('Option3 Name') and not product['options'].get('option3_name'):
            product['options']['option3_name'] = row['Option3 Name'].strip()
        
        # Add variant if has option values or SKU
        if any([row.get('Option1 Value'), row.get('Option2 Value'), row.get('Option3 Value'), row.get('Variant SKU')]):
            variant = self._extract_variant(row)
            # Deduplicate by unique key
            variant_key = (
                variant.get('option1_value', ''),
                variant.get('option2_value', ''),
                variant.get('option3_value', ''),
                variant.get('sku', ''),
                variant.get('barcode', '')
            )
            if variant_key not in product['_variant_keys']:
                product['variants'].append(variant)
                product['_variant_keys'].add(variant_key)
                self.stats['total_variants'] += 1
                
                # Track SKU mapping
                if variant.get('sku'):
                    if variant['sku'] in self.sku_to_handle:
                        self.stats['duplicate_skus'].append(variant['sku'])
                    else:
                        self.sku_to_handle[variant['sku']] = handle
        
        # Add image if present
        if row.get('Image Src'):
            image = self._extract_image(row)
            image_key = (image['src'], image['position'])
            if image_key not in product['_image_keys']:
                product['images'].append(image)
                product['_image_keys'].add(image_key)
                self.stats['total_images'] += 1
        
        # Merge metafields (accumulate)
        metafields = self._extract_metafields(row)
        for key, value in metafields.items():
            if value and key not in product['metafields']:
                product['metafields'][key] = value
        
        # Merge Google Shopping fields
        google = self._extract_google_fields(row)
        for key, value in google.items():
            if value and key not in product['google_shopping']:
                product['google_shopping'][key] = value
        
        # Track vendor variations
        if product.get('vendor'):
            self.stats['vendor_variations'].add(product['vendor'])
    
    def _init_product(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Initialize a new product structure"""
        handle = row['Handle'].strip()
        return {
            'handle': handle,
            'title': row.get('Title', '').strip() if row.get('Title') else None,
            'body_html': None,
            'body_text': None,
            'vendor': row.get('Vendor', '').strip() if row.get('Vendor') else None,
            'product_category': row.get('Product Category', '').strip() if row.get('Product Category') else None,
            'type': row.get('Type', '').strip() if row.get('Type') else None,
            'tags': self._parse_tags(row.get('Tags', '')),
            'published': row.get('Published', '').strip().lower() == 'true',
            'status': row.get('Status', '').strip() if row.get('Status') else None,
            'seo_title': None,
            'seo_description': None,
            'options': {
                'option1_name': None,
                'option2_name': None,
                'option3_name': None
            },
            'variants': [],
            'images': [],
            'metafields': {},
            'google_shopping': {},
            'search_document': '',  # Will be generated later
            '_variant_keys': set(),  # Internal dedup tracking
            '_image_keys': set()  # Internal dedup tracking
        }
    
    def _parse_tags(self, tags_str: str) -> List[str]:
        """Parse comma-separated tags"""
        if not tags_str:
            return []
        return [t.strip() for t in tags_str.split(',') if t.strip()]
    
    def _extract_variant(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract variant data from row"""
        variant = {
            'option1_value': row.get('Option1 Value', '').strip() if row.get('Option1 Value') else None,
            'option2_value': row.get('Option2 Value', '').strip() if row.get('Option2 Value') else None,
            'option3_value': row.get('Option3 Value', '').strip() if row.get('Option3 Value') else None,
            'sku': row.get('Variant SKU', '').strip() if row.get('Variant SKU') else None,
            'barcode': row.get('Variant Barcode', '').strip() if row.get('Variant Barcode') else None,
            'grams': self._safe_int(row.get('Variant Grams')),
            'requires_shipping': row.get('Variant Requires Shipping', '').strip().lower() == 'true',
            'taxable': row.get('Variant Taxable', '').strip().lower() == 'true',
            'weight_unit': row.get('Variant Weight Unit', '').strip() if row.get('Variant Weight Unit') else None,
            'tax_code': row.get('Variant Tax Code', '').strip() if row.get('Variant Tax Code') else None,
            'variant_image': row.get('Variant Image', '').strip() if row.get('Variant Image') else None,
            'inventory_tracker': row.get('Variant Inventory Tracker', '').strip() if row.get('Variant Inventory Tracker') else None,
            'inventory_policy': row.get('Variant Inventory Policy', '').strip() if row.get('Variant Inventory Policy') else None,
            'fulfillment_service': row.get('Variant Fulfillment Service', '').strip() if row.get('Variant Fulfillment Service') else None
        }
        return variant
    
    def _extract_image(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract image data from row"""
        return {
            'src': row.get('Image Src', '').strip(),
            'position': self._safe_int(row.get('Image Position', '1')),
            'alt': row.get('Image Alt Text', '').strip() if row.get('Image Alt Text') else None
        }
    
    def _extract_metafields(self, row: Dict[str, str]) -> Dict[str, str]:
        """Extract metafield columns"""
        metafields = {}
        for col_name, value in row.items():
            match = self.METAFIELD_PATTERN.search(col_name)
            if match:
                key = match.group(1)
                if value and value.strip():
                    metafields[key] = value.strip()
        return metafields
    
    def _extract_google_fields(self, row: Dict[str, str]) -> Dict[str, str]:
        """Extract Google Shopping fields"""
        google = {}
        google_prefix = 'Google Shopping / '
        for col_name, value in row.items():
            if col_name.startswith(google_prefix):
                key = col_name[len(google_prefix):].lower().replace(' ', '_')
                if value and value.strip():
                    google[key] = value.strip()
        return google
    
    def _safe_int(self, value: str) -> Optional[int]:
        """Safely convert to int"""
        if not value or not value.strip():
            return None
        try:
            return int(float(value.strip()))
        except (ValueError, TypeError):
            return None
    
    def _generate_search_documents(self):
        """Generate search documents for each product"""
        for handle, product in self.products_by_handle.items():
            parts = []
            
            # Core identity
            if product.get('title'):
                parts.append(f"Title: {product['title']}")
            if product.get('vendor'):
                parts.append(f"Vendor: {product['vendor']}")
            if product.get('type'):
                parts.append(f"Type: {product['type']}")
            if product.get('product_category'):
                parts.append(f"Category: {product['product_category']}")
            
            # Tags
            if product.get('tags'):
                parts.append(f"Tags: {', '.join(product['tags'])}")
            
            # Options
            option_names = []
            for opt_key in ['option1_name', 'option2_name', 'option3_name']:
                if product['options'].get(opt_key):
                    option_names.append(product['options'][opt_key])
            if option_names:
                parts.append(f"Options: {', '.join(option_names)}")
            
            # Variant values (unique)
            all_opt_values = set()
            for variant in product.get('variants', []):
                for opt_key in ['option1_value', 'option2_value', 'option3_value']:
                    if variant.get(opt_key):
                        all_opt_values.add(variant[opt_key])
            if all_opt_values:
                parts.append(f"Variants: {', '.join(sorted(all_opt_values))}")
            
            # SKUs
            skus = [v['sku'] for v in product.get('variants', []) if v.get('sku')]
            if skus:
                parts.append(f"SKUs: {', '.join(skus)}")
            
            # Body text (first 500 chars)
            if product.get('body_text'):
                body_snippet = product['body_text'][:500]
                if len(product['body_text']) > 500:
                    body_snippet += '...'
                parts.append(f"Description: {body_snippet}")
            
            # Metafields summary
            if product.get('metafields'):
                meta_summary = ', '.join(product['metafields'].keys())
                parts.append(f"Attributes: {meta_summary}")
            
            product['search_document'] = '\n'.join(parts)
    
    def _generate_meta(self) -> Dict[str, Any]:
        """Generate metadata section"""
        # Check quality issues
        for handle, product in self.products_by_handle.items():
            if not product.get('title'):
                self.stats['missing_title'].append(handle)
            if not product.get('body_html'):
                self.stats['missing_body'].append(handle)
        
        # Generate search documents
        self._generate_search_documents()
        
        # Clean up internal tracking keys
        for product in self.products_by_handle.values():
            del product['_variant_keys']
            del product['_image_keys']
        
        return {
            'generated_at': None,  # Will be set when writing
            'source_file': self.csv_path,
            'total_rows_processed': self.stats['total_rows'],
            'unique_products': self.stats['unique_handles'],
            'total_variants': self.stats['total_variants'],
            'total_images': self.stats['total_images'],
            'quality_flags': {
                'products_missing_title': len(self.stats['missing_title']),
                'products_missing_body': len(self.stats['missing_body']),
                'duplicate_skus': len(set(self.stats['duplicate_skus'])),
                'vendor_variations': self.stats['vendor_variations']
            }
        }
    
    def _generate_indexes(self) -> Dict[str, Any]:
        """Generate lookup indexes"""
        by_vendor = defaultdict(list)
        by_type = defaultdict(list)
        by_category = defaultdict(list)
        by_tag = defaultdict(list)
        
        for handle, product in self.products_by_handle.items():
            if product.get('vendor'):
                by_vendor[product['vendor']].append(handle)
            if product.get('type'):
                by_type[product['type']].append(handle)
            if product.get('product_category'):
                by_category[product['product_category']].append(handle)
            for tag in product.get('tags', []):
                by_tag[tag].append(handle)
        
        return {
            'sku_to_handle': self.sku_to_handle,
            'by_vendor': dict(by_vendor),
            'by_type': dict(by_type),
            'by_category': dict(by_category),
            'by_tag': dict(by_tag)
        }
