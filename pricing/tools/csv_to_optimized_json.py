#!/usr/bin/env python3
"""
CSV to Optimized JSON Converter for GPT Knowledge Base
=======================================================

Converts BROMYROS pricing CSV into an optimized JSON format with:
- Multi-level indexing (SKU, familia, sub_familia, tipo)
- Familia groups with metadata
- Clean, normalized data
- Fast lookup structures for GPT

Usage:
    python pricing/tools/csv_to_optimized_json.py
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from collections import defaultdict

# Configuration
SOURCE_CSV = "wiki/matriz de costos adaptacion /mat design/Copy of MATRIZ de COSTOS y VENTAS 2026 update .xlsx - BROMYROS.csv"
OUTPUT_JSON = "pricing/out/bromyros_pricing_gpt_optimized.json"
IVA_RATE = 0.22

class PricingDataConverter:
    """Converts CSV pricing data to optimized JSON format"""
    
    def __init__(self, source_csv: str):
        self.source_csv = Path(source_csv)
        self.products: List[Dict[str, Any]] = []
        self.indices: Dict[str, Dict] = {
            "by_sku": {},
            "by_familia": defaultdict(list),
            "by_sub_familia": defaultdict(list),
            "by_tipo": defaultdict(list)
        }
        self.familia_groups: Dict[str, Dict] = {}
        self.stats = {
            "total_rows": 0,
            "valid_products": 0,
            "skipped_rows": 0,
            "duplicate_skus": 0,
            "familias": set(),
            "sub_familias": set(),
            "tipos": set()
        }
    
    def clean_price(self, value: str) -> Optional[float]:
        """Parse price string to float, handling commas and spaces"""
        if not value or value.strip() == "":
            return None
        try:
            clean = value.replace(' ', '').replace(',', '.')
            return round(float(clean), 2)
        except (ValueError, AttributeError):
            return None
    
    def extract_thickness_mm(self, sku: str, name: str) -> Optional[float]:
        """Extract thickness in mm from SKU or name"""
        # Try SKU first (e.g., IROOF50, ISD100EPS)
        if sku:
            match = re.search(r'(?:IROOF|IAGRO|ISD|IW|IF|GL|GF|GFS|GFSUP)(\d+)', sku.upper())
            if match:
                return float(match.group(1))
        
        # Try name (e.g., "50 mm", "100mm")
        if name:
            match = re.search(r'(\d+)\s*mm', name.lower())
            if match:
                return float(match.group(1))
        
        return None
    
    def normalize_familia(self, familia: str) -> str:
        """Normalize familia name for consistency"""
        if not familia:
            return "ESTANDAR"
        
        # Strip whitespace
        familia = familia.strip()
        
        # Handle common variations
        if not familia or familia == "":
            return "ESTANDAR"
        
        return familia
    
    def normalize_sub_familia(self, sub_familia: str) -> str:
        """Normalize sub_familia name"""
        if not sub_familia:
            return "ESTANDAR"
        
        sub_familia = sub_familia.strip()
        
        if not sub_familia or sub_familia == "":
            return "ESTANDAR"
        
        return sub_familia
    
    def normalize_tipo(self, tipo: str) -> str:
        """Normalize tipo (product type)"""
        if not tipo:
            return "Accesorio"
        
        tipo = tipo.strip()
        
        if not tipo or tipo == "":
            return "Accesorio"
        
        return tipo
    
    def parse_csv(self) -> None:
        """Parse CSV and extract products"""
        print(f"📄 Reading CSV: {self.source_csv}")
        
        if not self.source_csv.exists():
            raise FileNotFoundError(f"Source CSV not found: {self.source_csv}")
        
        with open(self.source_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        print(f"📊 Total rows in CSV: {len(rows)}")
        
        # Header row
        header = rows[0] if rows else []
        
        for i, row in enumerate(rows[1:], start=2):  # Skip header
            self.stats["total_rows"] += 1
            
            # Skip empty rows
            if len(row) < 14 or not any(row):
                self.stats["skipped_rows"] += 1
                continue
            
            # Extract fields
            sku = row[0].strip() if len(row) > 0 else ""
            name = row[1].strip() if len(row) > 1 else ""
            thickness_str = row[2].strip() if len(row) > 2 else ""
            length_str = row[3].strip() if len(row) > 3 else ""
            tipo = row[4].strip() if len(row) > 4 else ""
            familia = row[5].strip() if len(row) > 5 else ""
            sub_familia = row[6].strip() if len(row) > 6 else ""
            unit_base = row[7].strip() if len(row) > 7 else ""
            largo_min_max = row[8].strip() if len(row) > 8 else ""
            
            # Pricing fields
            cost_sin_iva = self.clean_price(row[9]) if len(row) > 9 else None
            sale_sin_iva = self.clean_price(row[10]) if len(row) > 10 else None
            sale_iva_inc = self.clean_price(row[11]) if len(row) > 11 else None
            web_sin_iva = self.clean_price(row[12]) if len(row) > 12 else None
            web_iva_inc = self.clean_price(row[13]) if len(row) > 13 else None
            
            # Skip if no SKU or if it's a header/separator row
            if not sku or not name:
                self.stats["skipped_rows"] += 1
                continue
            
            # Skip if name looks like a header
            if "ISOROOF" in name and "/" in name and not sku:
                self.stats["skipped_rows"] += 1
                continue
            
            # Normalize categorical fields
            familia_norm = self.normalize_familia(familia)
            sub_familia_norm = self.normalize_sub_familia(sub_familia)
            tipo_norm = self.normalize_tipo(tipo)
            
            # Extract thickness
            thickness_mm = self.extract_thickness_mm(sku, name)
            if not thickness_mm and thickness_str:
                try:
                    thickness_mm = float(thickness_str.replace(',', '.'))
                except:
                    pass
            
            # Build product entry
            product = {
                "sku": sku,
                "name": name,
                "familia": familia_norm,
                "sub_familia": sub_familia_norm,
                "tipo": tipo_norm,
                "specifications": {
                    "thickness_mm": thickness_mm,
                    "length_m": length_str if length_str else None,
                    "unit_base": unit_base if unit_base else "m2",
                    "largo_min_max": largo_min_max if largo_min_max else None
                },
                "pricing": {
                    "cost_sin_iva": cost_sin_iva,
                    "sale_sin_iva": sale_sin_iva,
                    "sale_iva_inc": sale_iva_inc,
                    "web_sin_iva": web_sin_iva,
                    "web_iva_inc": web_iva_inc
                }
            }
            
            # Track stats
            self.stats["familias"].add(familia_norm)
            self.stats["sub_familias"].add(sub_familia_norm)
            self.stats["tipos"].add(tipo_norm)
            
            # Handle duplicate SKUs - check against existing products
            existing_skus = {p["sku"] for p in self.products}
            if sku in existing_skus:
                self.stats["duplicate_skus"] += 1
                print(f"⚠️  Duplicate SKU found: {sku} (row {i}) - {name[:50]}")
                # Append suffix for duplicates
                count = 1
                new_sku = f"{sku}_{count}"
                while new_sku in existing_skus:
                    count += 1
                    new_sku = f"{sku}_{count}"
                product["sku"] = new_sku
                product["original_sku"] = sku
            
            self.products.append(product)
            self.stats["valid_products"] += 1
        
        print(f"✅ Parsed {self.stats['valid_products']} valid products")
        print(f"⏭️  Skipped {self.stats['skipped_rows']} rows")
        if self.stats["duplicate_skus"] > 0:
            print(f"⚠️  Found {self.stats['duplicate_skus']} duplicate SKUs (renamed)")
    
    def build_indices(self) -> None:
        """Build multi-level indices"""
        print("\n🔍 Building indices...")
        
        for product in self.products:
            sku = product["sku"]
            familia = product["familia"]
            sub_familia = product["sub_familia"]
            tipo = product["tipo"]
            
            # SKU index (direct reference)
            self.indices["by_sku"][sku] = product
            
            # Familia index (list of SKUs)
            self.indices["by_familia"][familia].append(sku)
            
            # Sub_familia index
            self.indices["by_sub_familia"][sub_familia].append(sku)
            
            # Tipo index
            self.indices["by_tipo"][tipo].append(sku)
        
        # Convert defaultdicts to regular dicts
        self.indices["by_familia"] = dict(self.indices["by_familia"])
        self.indices["by_sub_familia"] = dict(self.indices["by_sub_familia"])
        self.indices["by_tipo"] = dict(self.indices["by_tipo"])
        
        print(f"   • SKU index: {len(self.indices['by_sku'])} entries")
        print(f"   • Familia index: {len(self.indices['by_familia'])} groups")
        print(f"   • Sub_familia index: {len(self.indices['by_sub_familia'])} groups")
        print(f"   • Tipo index: {len(self.indices['by_tipo'])} groups")
    
    def build_familia_groups(self) -> None:
        """Build familia groups with metadata and product lists"""
        print("\n👥 Building familia groups...")
        
        for familia, skus in self.indices["by_familia"].items():
            # Get all products in this familia
            familia_products = [self.indices["by_sku"][sku] for sku in skus]
            
            # Calculate metadata
            thicknesses = [p["specifications"]["thickness_mm"] 
                          for p in familia_products 
                          if p["specifications"]["thickness_mm"] is not None]
            
            thickness_range = None
            if thicknesses:
                min_thick = min(thicknesses)
                max_thick = max(thicknesses)
                thickness_range = f"{int(min_thick)}-{int(max_thick)}mm" if min_thick != max_thick else f"{int(min_thick)}mm"
            
            # Get predominant sub_familia and tipo
            sub_familias = [p["sub_familia"] for p in familia_products]
            tipos = [p["tipo"] for p in familia_products]
            
            predominant_sub_familia = max(set(sub_familias), key=sub_familias.count) if sub_familias else "N/A"
            predominant_tipo = max(set(tipos), key=tipos.count) if tipos else "N/A"
            
            # Build description
            description = self._generate_familia_description(familia, predominant_tipo, predominant_sub_familia)
            
            self.familia_groups[familia] = {
                "description": description,
                "sub_familia": predominant_sub_familia,
                "tipo": predominant_tipo,
                "thickness_range": thickness_range,
                "product_count": len(skus),
                "products": familia_products
            }
        
        print(f"   • Created {len(self.familia_groups)} familia groups")
    
    def _generate_familia_description(self, familia: str, tipo: str, sub_familia: str) -> str:
        """Generate human-readable description for familia group"""
        descriptions = {
            "ISOROOF / FOIL": "Isoroof panels with foil coating for enhanced thermal performance",
            "ISOROOF": "Standard Isoroof panels for roofing applications",
            "ISOROOF Colonial": "Isoroof Colonial panels with tile-like appearance",
            "ISODEC": "ISODEC panels for heavy-duty roofing and wall applications",
            "ISOWALL": "Isowall panels for facade and wall insulation",
            "ISOFRIG": "IsoFrig panels for refrigeration and clean rooms",
            "ISOPANEL": "ISOPANEL EPS panels for general construction",
            "ESTANDAR": "Standard accessories and consumables applicable to all product families",
        }
        
        # Return predefined description or generate one
        if familia in descriptions:
            return descriptions[familia]
        
        # Generate description from tipo and sub_familia
        return f"{tipo} products in {familia} family ({sub_familia} material)"
    
    def generate_json(self, output_path: str) -> None:
        """Generate final optimized JSON"""
        print(f"\n💾 Generating JSON: {output_path}")
        
        output = {
            "metadata": {
                "source": "MATRIZ de COSTOS y VENTAS 2026",
                "source_file": str(self.source_csv),
                "generated_at": datetime.now().isoformat(),
                "total_products": len(self.products),
                "total_familias": len(self.indices["by_familia"]),
                "total_sub_familias": len(self.indices["by_sub_familia"]),
                "currency": "USD",
                "iva_rate": IVA_RATE,
                "version": "1.0.0"
            },
            "indices": {
                "by_sku": {sku: {"familia": p["familia"], "sub_familia": p["sub_familia"], "tipo": p["tipo"]} 
                          for sku, p in self.indices["by_sku"].items()},
                "by_familia": self.indices["by_familia"],
                "by_sub_familia": self.indices["by_sub_familia"],
                "by_tipo": self.indices["by_tipo"]
            },
            "familia_groups": self.familia_groups,
            "products": self.products
        }
        
        # Write JSON
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        file_size = output_file.stat().st_size
        print(f"✅ Generated: {output_file}")
        print(f"   • File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"   • Products: {len(self.products)}")
        print(f"   • Familias: {len(self.familia_groups)}")
    
    def print_summary(self) -> None:
        """Print conversion summary"""
        print("\n" + "="*60)
        print("📊 CONVERSION SUMMARY")
        print("="*60)
        print(f"Total rows processed:     {self.stats['total_rows']}")
        print(f"Valid products:           {self.stats['valid_products']}")
        print(f"Skipped rows:             {self.stats['skipped_rows']}")
        print(f"Duplicate SKUs:           {self.stats['duplicate_skus']}")
        print(f"\nUnique familias:          {len(self.stats['familias'])}")
        print(f"Unique sub_familias:      {len(self.stats['sub_familias'])}")
        print(f"Unique tipos:             {len(self.stats['tipos'])}")
        print("="*60)

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🚀 BROMYROS PRICING CSV → OPTIMIZED JSON CONVERTER")
    print("="*60)
    
    converter = PricingDataConverter(SOURCE_CSV)
    
    try:
        # Step 1: Parse CSV
        converter.parse_csv()
        
        # Step 2: Build indices
        converter.build_indices()
        
        # Step 3: Build familia groups
        converter.build_familia_groups()
        
        # Step 4: Generate JSON
        converter.generate_json(OUTPUT_JSON)
        
        # Step 5: Print summary
        converter.print_summary()
        
        print("\n✅ Conversion complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
