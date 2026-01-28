import csv
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from .schema import Product, CostInfo, MarginInfo, PriceInfo

class CostMatrixRedesigner:
    """Redesigns cost matrix for optimal GPT indexing"""
    
    def __init__(self):
        self.indexes = {
            "by_code": {},
            "by_name": {},
            "by_category": {},
            "by_thickness": {},
            "by_status": {},
            "by_searchable_text": {}
        }

    def parse_input(self, input_path: str) -> List[Dict]:
        """
        Parse an input source and extract products.

        Supported:
        - .csv / .tsv (delimited files)
        - .html (Excel "Save as Web Page" tab export)
        - directory (parses every .html file inside and concatenates results; adds `proveedor` metadata)
        """
        path = Path(input_path)

        if path.is_dir():
            products: List[Dict] = []
            for html_path in sorted(path.glob("*.html")):
                proveedor = html_path.stem.strip()
                for p in self._parse_html_file(str(html_path)):
                    p.setdefault("metadata", {})["proveedor"] = proveedor
                    products.append(p)
            return products

        if path.suffix.lower() == ".html":
            return self._parse_html_file(input_path)

        return self.parse_csv(input_path)

    def parse_csv(self, csv_path: str) -> List[Dict]:
        """Parse CSV/TSV and extract products."""
        try:
            suffix = Path(csv_path).suffix.lower()
            with open(csv_path, "r", encoding="utf-8", newline="") as f:
                if suffix == ".tsv":
                    reader = csv.reader(f, delimiter="\t")
                else:
                    sample = f.read(2048)
                    f.seek(0)
                    try:
                        dialect = csv.Sniffer().sniff(sample)
                        reader = csv.reader(f, dialect)
                    except csv.Error:
                        reader = csv.reader(f)

                rows = list(reader)
        except FileNotFoundError:
            print(f"Error: File not found at {csv_path}")
            return []

        return self._parse_rows(rows, source_label=str(csv_path))

    def _parse_html_file(self, html_path: str) -> List[Dict]:
        """Parse an Excel-exported HTML sheet into the same row-shape as the CSV parser."""
        import pandas as pd

        dfs = pd.read_html(html_path)
        if not dfs:
            return []
        df = dfs[0]

        linear_cols = [
            "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF", "AG",
            "AH", "AI", "AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR",
        ]

        def cell(r, col) -> str:
            if col not in df.columns:
                return ""
            v = r[col]
            if pd.isna(v):
                return ""
            return str(v).strip()

        rows: List[List[str]] = []
        for _, r in df.iterrows():
            # Create a sparse row matching the legacy CSV column positions used downstream.
            row = [""] * 64
            row[0] = cell(r, "A")   # Shopify
            row[1] = cell(r, "B")   # Notes
            row[2] = cell(r, "C")   # Status
            row[3] = cell(r, "D")   # Code
            row[4] = cell(r, "E")   # Product name / header text
            row[5] = cell(r, "F")   # Cost base
            row[11] = cell(r, "L")  # Venta + IVA
            row[12] = cell(r, "M")  # Consumidor IVA inc.
            row[16] = cell(r, "T")  # Web Venta + IVA
            row[17] = cell(r, "U")  # Web Venta IVA inc.
            row[19] = cell(r, "V")  # Precio ML

            for i, col in enumerate(linear_cols):
                row[23 + i] = cell(r, col)

            rows.append(row)

        return self._parse_rows(rows, source_label=str(html_path))

    def _parse_rows(self, rows: List[List[str]], source_label: str) -> List[Dict]:
        """Parse already-tokenized rows (CSV/TSV/HTML) into product dicts."""
        products: List[Dict] = []
        current_category: Optional[str] = None
        seen_codes: set[str] = set()

        for row in rows:
            if not row or len(row) < 5:
                continue

            # Normalize row values to strings
            row = ["" if v is None else str(v) for v in row]

            name = row[4].strip() if len(row) > 4 else ""
            if not name:
                continue

            # Skip header row(s)
            if name.strip().lower() in {"producto"}:
                continue

            # Section/category headers update `current_category` but are not products
            if self._is_category_header_row(row):
                current_category = self._extract_category(name)
                continue

            product_dict = self._parse_product_row(row, current_category)
            if not product_dict:
                # Debug print for failed parse (kept, per user preference)
                print(f"Failed to parse row: {row[:5]}")
                continue

            # Ensure unique codes (generated codes can collide)
            code = product_dict.get("codigo", "").strip()
            if not code:
                continue
            if code in seen_codes:
                suffix = 2
                while f"{code}_{suffix}" in seen_codes:
                    suffix += 1
                new_code = f"{code}_{suffix}"
                product_dict.setdefault("metadata", {})["codigo_original"] = code
                product_dict["codigo"] = new_code
                code = new_code

            product_dict.setdefault("metadata", {})["source"] = source_label

            seen_codes.add(code)
            products.append(product_dict)

        return products

    def _is_category_header_row(self, row: List[str]) -> bool:
        """
        Heuristic: a category header is a text row (often uppercase) that sets context,
        not a priced/coded product.
        """
        name = row[4].strip() if len(row) > 4 else ""
        if not name:
            return False

        code = row[3].strip() if len(row) > 3 else ""
        status = row[2].strip() if len(row) > 2 else ""

        # If it looks like a product row, it's not a header
        if code:
            return False
        if status:
            return False

        # If it has numeric values in typical price/cost columns, treat as product
        numeric_cols = [5, 6, 7, 10, 11, 12, 16, 17, 19]
        for idx in numeric_cols:
            if idx < len(row) and self._parse_number(row[idx]) is not None:
                return False

        upper = name.upper()
        keywords = [
            "ISOROOF", "ISODEC", "ISOPANEL", "ISOWALL", "ISOFRIG",
            "GOTERO", "BABETA", "CANALÓN", "CANALON", "CUMBRERA",
            "PERFIL", "ANCLAJE", "ACCESORIO", "ACCESORIOS", "FLETE",
        ]
        return any(k in upper for k in keywords)
    
    def _extract_category(self, text: str) -> str:
        """Extract category from text"""
        text_upper = text.upper()
        
        category_map = {
            "ISOROOF FOIL": "isoroof_foil",
            "ISOROOF PLUS": "isoroof_plus",
            "ISOROOF COLONIAL": "isoroof_colonial",
            "ISOROOF": "isoroof", # Order matters, specific first
            "ISODEC EPS": "isodec_eps",
            "ISODEC PIR": "isodec_pir",
            "ISOPANEL EPS": "isopanel_eps",
            "ISOWALL PIR": "isowall_pir",
            "ISOWALL": "isowall",
            "ISOFRIG": "isofrig",
            "GOTERO FRONTAL": "gotero_frontal",
            "GOTERO LATERAL": "gotero_lateral",
            "GOTERO": "gotero",
            "BABETA": "babeta",
            "CANALÓN": "canalon",
            "CUMBRERA": "cumbrera",
            "PERFIL": "perfil",
            "ANCLAJE": "anclaje",
            "ACCESORIO": "accesorio",
            "FLETE": "flete"
        }
        
        for key, value in category_map.items():
            if key in text_upper:
                return value
        
        return "otros"
    
    def _parse_product_row(self, row: List[str], category: Optional[str]) -> Optional[Dict]:
        """Parse a product row from CSV"""
        try:
            # Extract basic info
            shopify_status = row[0].strip() if len(row) > 0 else ""
            notes = row[1].strip() if len(row) > 1 else ""
            status = row[2].strip() if len(row) > 2 else ""
            code = row[3].strip() if len(row) > 3 else ""
            name = row[4].strip() if len(row) > 4 else ""
            
            if not name:
                # print(f"Missing name: {row[:5]}")
                return None
            
            # Generate code if missing
            if not code:
                # Create a slug from name
                slug = re.sub(r'[^a-zA-Z0-9]+', '_', name).upper().strip('_')
                if len(slug) > 20:
                    slug = slug[:20]
                code = f"GEN_{slug}"
            
            # Extract costs
            costo_base = self._parse_number(row[5]) if len(row) > 5 else None
            costo_aumento = self._parse_number(row[6]) if len(row) > 6 else None
            costo_proximo = self._parse_number(row[7]) if len(row) > 7 else None
            
            # Extract margin and profit
            margen = row[8].strip() if len(row) > 8 else ""
            ganancia = self._parse_number(row[10]) if len(row) > 10 else None
            
            # Extract prices
            venta_iva = self._parse_number(row[11]) if len(row) > 11 else None
            consumidor_iva_inc = self._parse_number(row[12]) if len(row) > 12 else None
            web_venta_iva = self._parse_number(row[16]) if len(row) > 16 else None
            web_venta_iva_inc = self._parse_number(row[17]) if len(row) > 17 else None
            
            # Extract thickness
            thickness = self._extract_thickness(name)
            
            # Extract linear meter prices (if available)
            precio_ml = self._parse_number(row[19]) if len(row) > 19 else None
            linear_prices = self._extract_linear_prices(row, 23) if len(row) > 23 else {}
            
            # Create Product object
            inferred_category = self._infer_product_category(code=code, name=name, fallback=category)
            product = Product(
                codigo=code,
                nombre=name,
                categoria=inferred_category,
                espesor_mm=thickness,
                estado=status if status else "ACT.",
                costos=CostInfo(
                    costo_base_usd_iva=costo_base,
                    costo_con_aumento_usd_iva=costo_aumento,
                    costo_proximo_aumento_usd_iva=costo_proximo
                ),
                margen=MarginInfo(
                    porcentaje=margen,
                    ganancia_usd=ganancia
                ),
                precios=PriceInfo(
                    venta_iva_usd=venta_iva,
                    consumidor_iva_inc_usd=consumidor_iva_inc,
                    web_venta_iva_usd=web_venta_iva,
                    web_venta_iva_inc_usd=web_venta_iva_inc
                ),
                precio_metro_lineal={
                    "precio_base_usd": precio_ml,
                    "precios_por_largo": linear_prices
                },
                metadata={
                    "shopify_status": shopify_status,
                    "notas": notes,
                    "fecha_actualizacion": datetime.now().isoformat()
                }
            )
            
            return product.to_dict()
            
        except Exception as e:
            print(f"Error parsing row {row[:5]}...: {e}")
            return None

    def _infer_product_category(self, code: str, name: str, fallback: Optional[str]) -> str:
        """Infer a more accurate category from code/name, falling back to section context."""
        n = (name or "").upper()
        c = (code or "").upper()

        # Panels / systems
        if "ISOROOF" in n or c.startswith(("IAGRO", "IROOF")):
            if "COLONIAL" in n:
                return "isoroof_colonial"
            if "FOIL" in n:
                return "isoroof_foil"
            if "PLUS" in n:
                return "isoroof_plus"
            return "isoroof"

        if "ISODEC" in n or c.startswith("ISD"):
            if "PIR" in n:
                return "isodec_pir"
            if "EPS" in n:
                return "isodec_eps"
            # If not specified, keep fallback or default to EPS
            return fallback or "isodec_eps"

        if "ISOPANEL" in n:
            return "isopanel_eps"

        if "ISOWALL" in n or c.startswith("IW"):
            if "PIR" in n:
                return "isowall_pir"
            return "isowall"

        if "ISOFRIG" in n or c.startswith("IF"):
            return "isofrig"

        # Profiles / accessories
        if c.startswith(("GFS", "GF")) or "GOTERO FRONTAL" in n:
            return "gotero_frontal"
        if c.startswith("GL") or "GOTERO LATERAL" in n:
            return "gotero_lateral"
        if c.startswith("BB") or "BABETA" in n:
            return "babeta"
        if c.startswith(("CD", "CAN.")) or "CANAL" in n:
            return "canalon"
        if c.startswith("CUM") or "CUMBRERA" in n:
            return "cumbrera"
        if c.startswith("PU") or "PERFIL" in n or "PLEGADO" in n:
            return "perfil"
        if c.startswith("FLETE") or "FLETE" in n:
            return "flete"

        # Anchors / fixings
        if any(term in n for term in ["VARILLA", "TUERCA", "ARANDELA", "TACO", "TORNILLO", "EXPANSIVO"]):
            return "anclaje"

        # Default
        return fallback or "otros"
    
    def _parse_number(self, value: str) -> Optional[float]:
        """Parse number from string, handling commas and errors"""
        if not value or str(value).strip() == "":
            return None
        
        try:
            # Remove commas and spaces
            cleaned = str(value).replace(",", "").replace(" ", "").strip()
            if cleaned == "" or cleaned.upper() == "#VALUE!":
                return None
            return float(cleaned)
        except:
            return None
    
    def _extract_thickness(self, name: str) -> Optional[str]:
        """Extract thickness in mm from product name"""
        patterns = [
            r'(\d+)\s*mm',
            r'(\d+)\s*m[^a-z]',
            r'espesor[:\s]+(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_linear_prices(self, row: List[str], start_col: int) -> Dict[str, float]:
        """Extract linear meter prices for different lengths"""
        linear_prices = {}
        lengths = [1.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0]
        
        for i, length in enumerate(lengths):
            if start_col + i < len(row):
                price = self._parse_number(row[start_col + i])
                if price:
                    linear_prices[str(length)] = price
        
        return linear_prices
    
    def build_indexes(self, products: List[Dict]):
        """Build search indexes for fast retrieval"""
        for idx, product in enumerate(products):
            code = product["codigo"]
            name = product["nombre"]
            category = product["categoria"]
            thickness = product.get("espesor_mm")
            status = product.get("estado", "ACT.")
            
            # Index by code
            self.indexes["by_code"][code] = {
                "codigo": code,
                "nombre": name, 
                "categoria": category,
                "path": f"productos.todos[{idx}]"  # stable path
            }
            
            # Index by name (normalized)
            name_normalized = name.lower().strip()
            if name_normalized not in self.indexes["by_name"]:
                self.indexes["by_name"][name_normalized] = []
            self.indexes["by_name"][name_normalized].append(code)
            
            # Index by category
            if category not in self.indexes["by_category"]:
                self.indexes["by_category"][category] = []
            self.indexes["by_category"][category].append(code)
            
            # Index by thickness
            if thickness:
                if thickness not in self.indexes["by_thickness"]:
                    self.indexes["by_thickness"][thickness] = []
                self.indexes["by_thickness"][thickness].append(code)
            
            # Index by status
            if status not in self.indexes["by_status"]:
                self.indexes["by_status"][status] = []
            self.indexes["by_status"][status].append(code)
    
    def create_optimized_structure(self, products: List[Dict]) -> Dict[str, Any]:
        """Create optimized JSON structure for GPT indexing"""
        
        # Build indexes
        self.build_indexes(products)
        
        # Organize by category
        products_by_category = {}
        for product in products:
            category = product["categoria"]
            if category not in products_by_category:
                products_by_category[category] = []
            products_by_category[category].append(product)
        
        # Create optimized structure
        structure = {
            "meta": {
                "nombre": "BROMYROS - Matriz de Costos y Ventas 2026 (Redesigned)",
                "version": "2.0.0",
                "fecha_creacion": datetime.now().isoformat(),
                "optimizado_para": "GPT OpenAI Actions - KB Indexing",
                "total_productos": len(products),
                "total_categorias": len(products_by_category),
                "estadisticas": {
                    "productos_activos": len([p for p in products if p.get("estado") == "ACT."]),
                    "productos_con_costo": len([p for p in products if p.get("costos", {}).get("fabrica_directo", {}).get("costo_base_usd_iva")]),
                    "productos_con_precio_web": len([p for p in products if p.get("precios", {}).get("web_stock", {}).get("web_venta_iva_usd")])
                }
            },
            "reglas_precios": {
                "empresa": {
                    "descripcion": "Empresas descuentan IVA",
                    "precio_a_usar": "precios.empresa.venta_iva_usd"
                },
                "particular": {
                    "descripcion": "Particulares no descuentan IVA",
                    "precio_a_usar": "precios.particular.consumidor_iva_inc_usd"
                },
                "cotizacion": {
                    "descripcion": "SIEMPRE usar precio + IVA y agregar IVA al final",
                    "precio_base": "precios.empresa.venta_iva_usd",
                    "iva": 0.22
                }
            },
            "indices": self.indexes,
            "productos": {
                "por_categoria": products_by_category,
                "todos": products
            }
        }
        
        return structure

def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python -m panelin_improvements.cost_matrix_tools.redesign_tool <input_path(.csv|.tsv|.html|dir)> <output_json_path>")
        return

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    redesigner = CostMatrixRedesigner()
    print(f"Parsing input from: {input_path}")
    products = redesigner.parse_input(input_path)
    
    print(f"Found {len(products)} products. Creating optimized structure...")
    structure = redesigner.create_optimized_structure(products)
    
    print(f"Saving to: {output_path}")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    print("Done!")

if __name__ == "__main__":
    main()
