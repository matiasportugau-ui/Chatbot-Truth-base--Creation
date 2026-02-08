#!/usr/bin/env python3
"""
Perfilería Pricing Index Builder
=================================

Creates a fast lookup index for perfilería (profiles) pricing by ML (metro lineal).

Output: 04_DATA/indices/perfileria_index.json
"""

import json
from pathlib import Path
from decimal import Decimal
import unicodedata

def _normalize_token(value: str) -> str:
    """Normalize text to ASCII lowercase for reliable matching."""
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()

def build_perfileria_index():
    """Build perfilería pricing index from accessories catalog"""
    print("=" * 70)
    print("PERFILERÍA PRICING INDEX BUILDER")
    print("=" * 70)
    
    # Load accessories catalog
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    catalog_path = project_root / "01_KNOWLEDGE_BASE" / "Level_1_2_Accessories" / "accessories_catalog.json"
    
    print(f"\n📂 Loading accessories catalog...")
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    accesorios = catalog.get('accesorios', [])
    print(f"   - Total accessories: {len(accesorios)}")
    
    # Filter perfileria items (normalize types to avoid accent mismatches)
    perfileria_types = {
        "perfil",
        "gotero_frontal",
        "gotero_lateral",
        "gotero_superior",
        "babeta_adosar",
        "babeta_empotrar",
        "canalon",
        "cumbrera",
    }
    perfileria_types_norm = {_normalize_token(tipo) for tipo in perfileria_types}
    perfileria_items = [
        acc for acc in accesorios
        if _normalize_token(acc.get("tipo", "")) in perfileria_types_norm
    ]
    
    print(f"   - Perfilería items found: {len(perfileria_items)}")
    
    # Build index
    index = {
        "meta": {
            "version": "1.0",
            "fecha": "2026-02-07",
            "descripcion": "Índice de precios por metro lineal para perfilería",
            "total_items": len(perfileria_items)
        },
        "items": {},
        "by_tipo": {}
    }
    
    for acc in perfileria_items:
        sku = acc['sku']
        tipo = acc.get("tipo", "")
        tipo_norm = _normalize_token(tipo)
        name = acc.get("name") or acc.get("nombre") or ""
        
        # Calculate price per ML
        precio_unit = acc.get('precio_unit_iva_inc', 0)
        largo_std = acc.get('largo_std_m')
        
        if largo_std and largo_std > 0:
            precio_por_ml = float(Decimal(str(precio_unit)) / Decimal(str(largo_std)))
        else:
            precio_por_ml = float(precio_unit)  # Already per ML or unit price
        
        item_data = {
            "sku": sku,
            "name": name,
            "tipo": tipo,
            "tipo_norm": tipo_norm,
            "precio_unit_iva_inc": precio_unit,
            "largo_std_m": largo_std,
            "precio_por_ml": round(precio_por_ml, 4),
            "unidad": acc.get('unidad', 'unid'),
            "espesor_mm": acc.get('espesor_mm'),
            "compatibilidad": acc.get('compatibilidad', [])
        }
        
        index["items"][sku] = item_data
        
        # Index by tipo
        for tipo_key in {tipo_norm, tipo}:
            if not tipo_key:
                continue
            if tipo_key not in index["by_tipo"]:
                index["by_tipo"][tipo_key] = []
            index["by_tipo"][tipo_key].append(sku)
    
    # Save index
    output_path = project_root / "04_DATA" / "indices" / "perfileria_index.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n💾 Saving index to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Index saved")
    
    # Summary
    print("\n" + "=" * 70)
    print("INDEX SUMMARY")
    print("=" * 70)
    for tipo, skus in sorted(index["by_tipo"].items()):
        print(f"  - {tipo}: {len(skus)} items")
    
    print(f"\nTotal perfilería items indexed: {len(index['items'])}")
    print()

if __name__ == "__main__":
    build_perfileria_index()
