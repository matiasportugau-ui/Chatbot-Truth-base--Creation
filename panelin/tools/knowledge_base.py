"""
Panelin Knowledge Base - Operaciones de consulta a la base de conocimiento.

Este módulo implementa herramientas para consultar la base de conocimiento
de productos BMC Uruguay de forma determinista.

Funciones:
1. lookup_product_specs() - Búsqueda exacta por SKU o nombre
2. search_products() - Búsqueda semántica/fuzzy
3. get_available_products() - Lista todos los productos disponibles
4. get_product_by_sku() - Búsqueda directa por SKU
"""

import json
import re
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from panelin.models.schemas import ProductSpec


# Default KB path
DEFAULT_KB_PATH = Path(__file__).parent.parent / "data" / "panelin_truth_bmcuruguay.json"

# Module-level cache for knowledge base
_KB_CACHE: Optional[Dict[str, Any]] = None
_KB_PATH_CACHE: Optional[Path] = None


def _get_kb_path() -> Path:
    """Find and cache the knowledge base path."""
    global _KB_PATH_CACHE
    if _KB_PATH_CACHE is not None:
        return _KB_PATH_CACHE
    
    possible_paths = [
        DEFAULT_KB_PATH,
        Path(__file__).parent.parent / "panelin_truth_bmcuruguay.json",
        Path(__file__).parent.parent.parent / "panelin_truth_bmcuruguay.json",
        Path(__file__).parent.parent / "data" / "panelin_truth_bmcuruguay.json",
    ]
    
    for p in possible_paths:
        if p.exists():
            _KB_PATH_CACHE = p
            return p
    
    raise FileNotFoundError(f"Knowledge base not found. Tried: {possible_paths}")


def _load_knowledge_base(kb_path: Optional[Path] = None) -> Dict[str, Any]:
    """Carga la base de conocimiento desde JSON con caching."""
    global _KB_CACHE
    
    # Use cache for default path
    if kb_path is None:
        if _KB_CACHE is not None:
            return _KB_CACHE
        path = _get_kb_path()
        with open(path, 'r', encoding='utf-8') as f:
            _KB_CACHE = json.load(f)
        return _KB_CACHE
    
    # Custom path - load directly without cache
    if kb_path.exists():
        with open(kb_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    raise FileNotFoundError(f"Knowledge base not found at: {kb_path}")


def lookup_product_specs(
    product_identifier: str,
    thickness_mm: Optional[int] = None,
    kb_path: Optional[Path] = None,
) -> Optional[ProductSpec]:
    """
    Busca especificaciones exactas de un producto en la base de conocimiento.
    
    Args:
        product_identifier: SKU, nombre de producto, o tipo de panel
        thickness_mm: Espesor específico (opcional)
        kb_path: Path a la KB (para testing)
    
    Returns:
        ProductSpec si se encuentra, None si no
    
    Example:
        >>> specs = lookup_product_specs("Isopanel EPS", thickness_mm=100)
        >>> print(specs["price_per_m2"])
        41.88
    """
    catalog = _load_knowledge_base(kb_path)
    products = catalog.get("products", {})
    
    # Normalize identifier
    normalized = product_identifier.lower().strip()
    
    # Strategy 1: Exact match by key
    for key, product in products.items():
        if key.lower() == normalized:
            return _format_product_spec(key, product)
        if thickness_mm and f"{thickness_mm}mm" in key:
            if normalized.replace(" ", "_") in key.lower():
                return _format_product_spec(key, product)
    
    # Strategy 2: Match by SKU
    for key, product in products.items():
        if product.get("sku", "").lower() == normalized:
            return _format_product_spec(key, product)
    
    # Strategy 3: Match by name (fuzzy)
    for key, product in products.items():
        product_name = product.get("name", "").lower()
        if normalized in product_name or product_name in normalized:
            # Check thickness if specified
            if thickness_mm is None or f"{thickness_mm}" in key:
                return _format_product_spec(key, product)
    
    # Strategy 4: Match by panel type keywords
    type_keywords = {
        "isopanel": "isopanel_eps",
        "isodec": "isodec_eps",
        "isowall": "isowall_pir",
        "isoroof": "isoroof_3g",
        "hiansa": "hiansa_panel_5g",
    }
    
    for keyword, base_key in type_keywords.items():
        if keyword in normalized:
            # Find matching product
            for key, product in products.items():
                if base_key in key.lower():
                    if thickness_mm is None or f"{thickness_mm}mm" in key:
                        return _format_product_spec(key, product)
    
    return None


def search_products(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 5,
    kb_path: Optional[Path] = None,
) -> List[ProductSpec]:
    """
    Búsqueda semántica/fuzzy de productos.
    
    Args:
        query: Descripción del producto o uso buscado
        filters: Filtros opcionales (familia, min_price, max_price, in_stock_only)
        limit: Número máximo de resultados
        kb_path: Path a KB
    
    Returns:
        Lista de ProductSpec ordenados por relevancia
    
    Example:
        >>> results = search_products("paneles económicos para techos")
        >>> for r in results:
        ...     print(r["name"], r["price_per_m2"])
    """
    catalog = _load_knowledge_base(kb_path)
    products = catalog.get("products", {})
    filters = filters or {}
    
    # Parse query for keywords
    query_lower = query.lower()
    keywords = set(re.findall(r'\w+', query_lower))
    
    # Score and filter products
    scored_products = []
    
    for key, product in products.items():
        score = 0
        
        # Skip if doesn't match filters
        if filters.get("familia"):
            if product.get("familia", "").lower() != filters["familia"].lower():
                continue
        
        if filters.get("min_price"):
            if product.get("price_per_m2", 0) < filters["min_price"]:
                continue
        
        if filters.get("max_price"):
            if product.get("price_per_m2", float("inf")) > filters["max_price"]:
                continue
        
        if filters.get("in_stock_only"):
            if product.get("stock_status") == "out_of_stock":
                continue
        
        # Score based on keyword matches
        product_text = f"{key} {product.get('name', '')} {product.get('familia', '')} {product.get('description', '')}".lower()
        
        for keyword in keywords:
            if keyword in product_text:
                score += 1
                # Boost for exact matches in name
                if keyword in product.get("name", "").lower():
                    score += 2
        
        # Boost for application keywords
        application_keywords = {
            "techo": ["isodec", "isoroof"],
            "cubierta": ["isodec", "isoroof"],
            "pared": ["isopanel", "isowall"],
            "fachada": ["isopanel", "isowall"],
            "económico": ["isopanel_eps", "isoroof_foil"],
            "premium": ["isowall_pir", "isoroof_plus"],
            "aislamiento": ["pir", "150mm", "200mm"],
            "galpón": ["isodec", "hiansa"],
        }
        
        for app_keyword, product_types in application_keywords.items():
            if app_keyword in keywords:
                for pt in product_types:
                    if pt in key.lower():
                        score += 3
        
        if score > 0:
            scored_products.append((score, key, product))
    
    # Sort by score descending
    scored_products.sort(key=lambda x: x[0], reverse=True)
    
    # Return top results
    results = []
    for _, key, product in scored_products[:limit]:
        results.append(_format_product_spec(key, product))
    
    return results


def get_available_products(
    familia: Optional[str] = None,
    in_stock_only: bool = False,
    kb_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Lista todos los productos disponibles.
    
    Args:
        familia: Filtrar por familia (ISOPANEL, ISODEC, ISOROOF, etc.)
        in_stock_only: Solo productos en stock
        kb_path: Path a KB
    
    Returns:
        Lista simplificada de productos con nombre, precio, y disponibilidad
    """
    catalog = _load_knowledge_base(kb_path)
    products = catalog.get("products", {})
    
    result = []
    for key, product in products.items():
        # Apply filters
        if familia:
            if product.get("familia", "").lower() != familia.lower():
                continue
        
        if in_stock_only:
            if product.get("stock_status") == "out_of_stock":
                continue
        
        result.append({
            "product_id": key,
            "name": product.get("name", key),
            "familia": product.get("familia", ""),
            "price_per_m2": product.get("price_per_m2"),
            "currency": product.get("currency", "USD"),
            "available_thicknesses": product.get("available_thicknesses", []),
            "stock_status": product.get("stock_status", "unknown"),
        })
    
    return sorted(result, key=lambda x: x["name"])


def get_product_by_sku(
    sku: str,
    kb_path: Optional[Path] = None,
) -> Optional[ProductSpec]:
    """
    Búsqueda directa por SKU.
    
    Args:
        sku: SKU del producto (ej: "IROOF50", "IDEC100")
        kb_path: Path a KB
    
    Returns:
        ProductSpec si se encuentra, None si no
    """
    catalog = _load_knowledge_base(kb_path)
    products = catalog.get("products", {})
    sku_index = catalog.get("indices", {}).get("by_sku", {})
    
    # Check SKU index first
    if sku.upper() in sku_index:
        sku_info = sku_index[sku.upper()]
        # Find corresponding product
        for key, product in products.items():
            if product.get("sku", "").upper() == sku.upper():
                return _format_product_spec(key, product)
    
    # Fallback: search in products
    for key, product in products.items():
        if product.get("sku", "").upper() == sku.upper():
            return _format_product_spec(key, product)
    
    return None


def get_pricing_rules(kb_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Obtiene las reglas generales de pricing.
    
    Returns:
        Diccionario con tax_rate_uy, delivery costs, thresholds, etc.
    """
    catalog = _load_knowledge_base(kb_path)
    return catalog.get("pricing_rules", {})


def get_kb_metadata(kb_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Obtiene metadata de la base de conocimiento.
    
    Returns:
        Version, last_sync, source info, etc.
    """
    catalog = _load_knowledge_base(kb_path)
    return {
        "version": catalog.get("version", "unknown"),
        "last_sync": catalog.get("last_sync"),
        "shopify_store": catalog.get("shopify_store"),
        "total_products": len(catalog.get("products", {})),
        "schema_version": catalog.get("meta", {}).get("schema_version"),
    }


def _format_product_spec(key: str, product: Dict[str, Any]) -> ProductSpec:
    """Formatea un producto de la KB como ProductSpec."""
    return ProductSpec(
        shopify_id=product.get("shopify_id"),
        sku=product.get("sku", key),
        name=product.get("name", key),
        familia=product.get("familia", ""),
        sub_familia=product.get("sub_familia", ""),
        tipo=product.get("tipo", "Panel"),
        price_per_m2=product.get("price_per_m2", 0),
        price_per_unit=product.get("price_per_unit"),
        currency=product.get("currency", "USD"),
        available_thicknesses=product.get("available_thicknesses"),
        ancho_util_m=product.get("ancho_util_m", 1.0),
        largo_min_m=product.get("largo_min_m", 2.0),
        largo_max_m=product.get("largo_max_m", 14.0),
        calculation_rules=product.get("calculation_rules", {
            "minimum_order_m2": 10,
            "bulk_discount_threshold_m2": 100,
            "bulk_discount_percent": 5,
            "max_discount_percent": 30,
        }),
        inventory_quantity=product.get("inventory_quantity"),
        stock_status=product.get("stock_status", "unknown"),
        last_updated=product.get("last_updated", datetime.utcnow().isoformat()),
        sync_source=product.get("sync_source", "manual"),
    )
