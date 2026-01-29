"""
Product Lookup - Búsqueda Determinista de Productos
===================================================

Este módulo proporciona funciones para buscar productos en la Knowledge Base.
Todas las búsquedas son exactas y deterministas—no hay aproximaciones.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass

KB_PATH = Path(__file__).parent.parent / "kb" / "panelin_truth_bmcuruguay.json"


def _load_kb() -> dict:
    """Carga la Knowledge Base desde JSON"""
    if not KB_PATH.exists():
        raise FileNotFoundError(f"Knowledge Base no encontrada: {KB_PATH}")
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class ProductSpec:
    """Especificaciones de producto"""
    sku: str
    name: str
    family: str
    product_type: str
    thickness_mm: Optional[int]
    price_usd: float
    sale_price_usd_ex_iva: float
    web_price_usd: float
    unit_base: str
    min_length_m: Optional[float]
    max_length_m: Optional[float]
    useful_width_m: Optional[float]
    stock_status: str
    production_type: str
    last_updated: Optional[str]


def lookup_product_specs(
    sku: str,
) -> Optional[Dict[str, Any]]:
    """
    Busca especificaciones exactas de un producto por SKU.
    
    Args:
        sku: Código SKU del producto
        
    Returns:
        Dict con especificaciones del producto o None si no existe
    """
    kb = _load_kb()
    products = kb.get("products", {})
    
    if sku in products:
        return products[sku]
    
    # Búsqueda por SKU interno
    for key, product in products.items():
        if product.get("sku") == sku or product.get("id") == sku:
            return product
    
    return None


def search_products_by_criteria(
    family: Optional[str] = None,
    product_type: Optional[str] = None,
    thickness_mm: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: bool = False,
) -> List[Dict[str, Any]]:
    """
    Busca productos que coincidan con los criterios especificados.
    
    Args:
        family: Familia de producto (ISOROOF_3G, ISODEC_EPS, etc.)
        product_type: Tipo (panel, perfil, accesorio, otro)
        thickness_mm: Espesor exacto en mm
        min_price: Precio mínimo USD
        max_price: Precio máximo USD
        in_stock_only: Solo productos en stock
        
    Returns:
        Lista de productos que coinciden con los criterios
    """
    kb = _load_kb()
    products = kb.get("products", {})
    
    results = []
    
    for key, product in products.items():
        # Filtrar por familia
        if family and not product.get("family", "").upper().startswith(family.upper()):
            continue
        
        # Filtrar por tipo
        if product_type and product.get("type") != product_type:
            continue
        
        # Filtrar por espesor
        if thickness_mm is not None and product.get("thickness_mm") != thickness_mm:
            continue
        
        # Filtrar por precio
        price = product.get("price_usd", 0)
        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue
        
        # Filtrar por stock
        if in_stock_only:
            status = product.get("stock_status", "").lower()
            if "out" in status or "agotado" in status or status == "check availability":
                continue
        
        results.append({**product, "_kb_key": key})
    
    # Ordenar por precio
    results.sort(key=lambda x: x.get("price_usd", 0))
    
    return results


def get_available_thicknesses(
    panel_type: str,
    insulation_type: Optional[str] = None,
) -> List[int]:
    """
    Obtiene los espesores disponibles para un tipo de panel.
    
    Args:
        panel_type: Tipo de panel (Isopanel, Isodec, Isoroof, etc.)
        insulation_type: Tipo de aislación (EPS, PIR) - opcional
        
    Returns:
        Lista ordenada de espesores disponibles en mm
    """
    kb = _load_kb()
    products = kb.get("products", {})
    
    thicknesses = set()
    
    for product in products.values():
        family = product.get("family", "").upper()
        
        # Verificar si coincide con el tipo de panel
        if not family.startswith(panel_type.upper()):
            continue
        
        # Verificar tipo de aislación si se especifica
        if insulation_type:
            if insulation_type.upper() == "PIR" and "PIR" not in family:
                continue
            if insulation_type.upper() == "EPS" and "PIR" in family:
                continue
        
        thickness = product.get("thickness_mm")
        if thickness:
            thicknesses.add(int(thickness))
    
    return sorted(list(thicknesses))


def get_price_for_product(
    sku: str,
    price_type: Literal["empresa", "particular", "web"] = "empresa",
) -> Optional[float]:
    """
    Obtiene el precio de un producto según el tipo de cliente.
    
    Args:
        sku: Código SKU del producto
        price_type: Tipo de precio (empresa, particular, web)
        
    Returns:
        Precio en USD o None si el producto no existe
    """
    product = lookup_product_specs(sku)
    
    if not product:
        return None
    
    if price_type == "empresa":
        return product.get("sale_price_usd_ex_iva", product.get("price_usd"))
    elif price_type == "particular":
        return product.get("price_usd")
    else:  # web
        return product.get("web_price_usd", product.get("price_usd"))


def get_panels_for_application(
    application: Literal["techo", "pared", "fachada", "camara_fria"],
) -> List[Dict[str, Any]]:
    """
    Obtiene paneles recomendados para una aplicación específica.
    
    Args:
        application: Tipo de aplicación
        
    Returns:
        Lista de productos recomendados con sus especificaciones
    """
    application_map = {
        "techo": ["ISOROOF", "ISODEC"],
        "pared": ["ISOPANEL", "ISOWALL"],
        "fachada": ["ISOWALL", "ISOPANEL"],
        "camara_fria": ["ISOFRIG"],
    }
    
    families = application_map.get(application, [])
    
    results = []
    for family in families:
        products = search_products_by_criteria(
            family=family,
            product_type="panel",
        )
        results.extend(products)
    
    return results


def get_profile_for_panel(
    panel_thickness_mm: int,
    profile_type: Literal["gotero_frontal", "gotero_lateral", "cumbrera", "babeta", "canalon"],
) -> Optional[Dict[str, Any]]:
    """
    Obtiene el perfil compatible para un espesor de panel.
    
    Args:
        panel_thickness_mm: Espesor del panel en mm
        profile_type: Tipo de perfil
        
    Returns:
        Producto de perfil compatible o None
    """
    kb = _load_kb()
    products = kb.get("products", {})
    
    # Mapeo de prefijos de SKU por tipo de perfil
    profile_prefixes = {
        "gotero_frontal": ["GFS", "GFSUP", "GFCGR"],
        "gotero_lateral": ["GL", "GLDCAM"],
        "cumbrera": ["CUMROOF", "6847"],
        "babeta": ["BBAS", "BBAL", "BBESUP"],
        "canalon": ["CD", "CAN"],
    }
    
    prefixes = profile_prefixes.get(profile_type, [])
    
    for key, product in products.items():
        # Verificar si es el tipo de perfil correcto
        if product.get("family") != profile_type.split("_")[0]:
            sku = product.get("sku", key)
            matches_prefix = any(sku.startswith(p) for p in prefixes)
            if not matches_prefix:
                continue
        
        # Verificar espesor compatible
        prod_thickness = product.get("thickness_mm")
        if prod_thickness and prod_thickness == panel_thickness_mm:
            return product
        
        # Si no tiene espesor específico, puede ser universal
        if not prod_thickness and product.get("type") == "perfil":
            continue  # Skip, buscamos específico primero
    
    # Si no encontramos específico, buscar universal
    for key, product in products.items():
        if product.get("type") == "perfil":
            sku = product.get("sku", key)
            if any(sku.startswith(p) for p in prefixes):
                if not product.get("thickness_mm"):
                    return product
    
    return None


def get_catalog_summary() -> Dict[str, Any]:
    """
    Obtiene un resumen del catálogo para el agente.
    
    Returns:
        Diccionario con estadísticas del catálogo
    """
    kb = _load_kb()
    products = kb.get("products", {})
    meta = kb.get("meta", {})
    
    # Contar por tipo
    type_counts = {}
    family_counts = {}
    
    for product in products.values():
        ptype = product.get("type", "otro")
        type_counts[ptype] = type_counts.get(ptype, 0) + 1
        
        family = product.get("family", "otros")
        family_counts[family] = family_counts.get(family, 0) + 1
    
    return {
        "total_products": len(products),
        "by_type": type_counts,
        "by_family": family_counts,
        "last_sync": meta.get("last_sync"),
        "kb_version": meta.get("version"),
    }
