"""
Panelin Agent V2 - Product Lookup Tools
========================================

Deterministic product search and lookup functions.
These tools help the LLM find products based on natural language queries
while keeping all data retrieval deterministic.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import re


def _load_knowledge_base() -> dict:
    """Load the single source of truth knowledge base"""
    kb_path = Path(__file__).parent.parent / "config" / "panelin_truth_bmcuruguay.json"
    if not kb_path.exists():
        raise FileNotFoundError(f"Knowledge base not found at {kb_path}")
    
    with open(kb_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _normalize_query(query: str) -> str:
    """Normalize search query for matching"""
    return query.lower().strip()


def _extract_thickness(query: str) -> Optional[int]:
    """Extract thickness in mm from a query string"""
    patterns = [
        r'(\d+)\s*mm',
        r'(\d+)\s*milimetros',
        r'espesor\s*(\d+)',
        r'de\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            return int(match.group(1))
    
    return None


def _match_product_family(query: str) -> Optional[str]:
    """Match product family from query"""
    query_lower = query.lower()
    
    # Order matters: more specific matches first
    family_keywords = [
        ("ISOROOF", ["isoroof", "iso roof", "isoroof 3g", "isoroof foil", "foil", "3g"]),
        ("ISOWALL", ["isowall", "iso wall", "pir fachada"]),
        ("HIANSA", ["hiansa", "trapezoidal", "becam", "5g"]),
        ("ISODEC", ["isodec", "iso dec", "techo", "cubierta"]),
        ("ISOPANEL", ["isopanel", "iso panel", "panel eps", "paredes", "fachada"]),
    ]
    
    for family, keywords in family_keywords:
        for kw in keywords:
            if kw in query_lower:
                return family
    
    return None


def _match_application(query: str) -> Optional[str]:
    """Match application type from query"""
    query_lower = query.lower()
    
    app_keywords = {
        "techos": ["techo", "techos", "roof", "cubierta", "cubiertas", "tapa"],
        "paredes": ["pared", "paredes", "wall", "muro", "muros", "lateral"],
        "fachadas": ["fachada", "fachadas", "facade", "exterior", "frente"],
        "agro": ["agro", "agricola", "galpon", "galpón", "tinglado"]
    }
    
    for app, keywords in app_keywords.items():
        for kw in keywords:
            if kw in query_lower:
                return app
    
    return None


def find_product_by_query(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Find products based on a natural language query.
    
    This function performs DETERMINISTIC pattern matching - 
    no LLM inference is involved in the search logic.
    
    Args:
        query: Natural language query (e.g., "panel para techo de 100mm")
        max_results: Maximum number of results to return
        
    Returns:
        List of matching products with their details
    """
    kb = _load_knowledge_base()
    products = kb.get("products", {})
    
    query_normalized = _normalize_query(query)
    
    # Extract search criteria
    thickness = _extract_thickness(query_normalized)
    family = _match_product_family(query_normalized)
    application = _match_application(query_normalized)
    
    # Score and filter products
    scored_results = []
    
    for product_id, product in products.items():
        score = 0
        
        # Family match (high priority)
        if family and product.get("family", "").upper() == family:
            score += 50
        
        # Thickness match (high priority)
        if thickness and product.get("thickness_mm") == thickness:
            score += 40
        
        # Application match
        if application:
            product_apps = [a.lower() for a in product.get("application", [])]
            if application in product_apps:
                score += 30
        
        # Name contains query terms
        name_lower = product.get("name", "").lower()
        query_words = query_normalized.split()
        for word in query_words:
            if len(word) > 2 and word in name_lower:
                score += 10
        
        # Stock availability bonus
        if product.get("stock_status") == "available":
            score += 5
        
        if score > 0:
            scored_results.append({
                "product_id": product_id,
                "name": product.get("name"),
                "family": product.get("family"),
                "thickness_mm": product.get("thickness_mm"),
                "price_per_m2": product.get("price_per_m2"),
                "currency": product.get("currency"),
                "application": product.get("application"),
                "stock_status": product.get("stock_status"),
                "ancho_util_m": product.get("ancho_util_m"),
                "largo_min_m": product.get("largo_min_m"),
                "largo_max_m": product.get("largo_max_m"),
                "match_score": score
            })
    
    # Sort by score and return top results
    scored_results.sort(key=lambda x: x["match_score"], reverse=True)
    
    return scored_results[:max_results]


def get_product_price(product_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the exact price for a product.
    
    CRITICAL: This is a deterministic lookup - prices come from KB, not LLM.
    
    Args:
        product_id: Exact product ID
        
    Returns:
        Price information or None if not found
    """
    kb = _load_knowledge_base()
    products = kb.get("products", {})
    
    if product_id not in products:
        return None
    
    product = products[product_id]
    
    return {
        "product_id": product_id,
        "name": product.get("name"),
        "price_per_m2": product.get("price_per_m2"),
        "currency": product.get("currency"),
        "last_updated": product.get("last_updated"),
        "_source": "panelin_truth_kb_deterministic"
    }


def check_product_availability(product_id: str) -> Dict[str, Any]:
    """
    Check product availability status.
    
    Args:
        product_id: Product ID to check
        
    Returns:
        Availability information
    """
    kb = _load_knowledge_base()
    products = kb.get("products", {})
    
    if product_id not in products:
        return {
            "product_id": product_id,
            "found": False,
            "available": False,
            "message": f"Producto no encontrado: {product_id}"
        }
    
    product = products[product_id]
    stock_status = product.get("stock_status", "unknown")
    
    return {
        "product_id": product_id,
        "found": True,
        "name": product.get("name"),
        "available": stock_status == "available",
        "stock_status": stock_status,
        "inventory_quantity": product.get("inventory_quantity"),
        "last_updated": product.get("last_updated"),
        "_source": "panelin_truth_kb_deterministic"
    }


def list_all_products(family: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all available products, optionally filtered by family.
    
    Args:
        family: Optional family filter (ISOPANEL, ISODEC, etc.)
        
    Returns:
        List of all matching products
    """
    kb = _load_knowledge_base()
    products = kb.get("products", {})
    
    result = []
    for product_id, product in products.items():
        if family and product.get("family", "").upper() != family.upper():
            continue
        
        result.append({
            "product_id": product_id,
            "name": product.get("name"),
            "family": product.get("family"),
            "sub_family": product.get("sub_family"),
            "thickness_mm": product.get("thickness_mm"),
            "price_per_m2": product.get("price_per_m2"),
            "currency": product.get("currency"),
            "stock_status": product.get("stock_status")
        })
    
    return result


def get_pricing_rules() -> Dict[str, Any]:
    """
    Get current pricing rules (tax rates, delivery costs, etc.)
    
    Returns:
        Pricing rules from knowledge base
    """
    kb = _load_knowledge_base()
    return kb.get("pricing_rules", {})


# Tool definitions for LLM
TOOL_DEFINITIONS = [
    {
        "name": "find_product_by_query",
        "description": "Busca productos basándose en descripción en lenguaje natural. Útil cuando el usuario no sabe el código exacto del producto.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Descripción del producto buscado (ej: 'panel para techo de 100mm', 'isopanel económico')"
                },
                "max_results": {
                    "type": "integer",
                    "default": 5,
                    "description": "Máximo de resultados a retornar"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_product_price",
        "description": "Obtiene el precio exacto de un producto por su ID. Usar después de identificar el producto correcto.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "ID exacto del producto (ej: ISOPANEL_EPS_50mm)"
                }
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "check_product_availability",
        "description": "Verifica disponibilidad y stock de un producto.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "ID del producto a verificar"
                }
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "list_all_products",
        "description": "Lista todos los productos disponibles, opcionalmente filtrados por familia.",
        "parameters": {
            "type": "object",
            "properties": {
                "family": {
                    "type": "string",
                    "enum": ["ISOPANEL", "ISODEC", "ISOWALL", "ISOROOF", "HIANSA"],
                    "description": "Filtrar por familia de producto"
                }
            }
        }
    }
]
