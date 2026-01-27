#!/usr/bin/env python3
"""
KB Indexing Expert Agent
========================

Expert agent specialized in Knowledge Base indexing, retrieval, and validation
optimized for GPT OpenAI Actions API calls.

Features:
- Hierarchical KB access (4-level system)
- Optimized indexing for fast retrieval
- Semantic and keyword search
- Conflict detection and resolution
- Structured data extraction
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re

# KB Hierarchy Configuration
KB_HIERARCHY = {
    "level_1_master": [
        "BMC_Base_Conocimiento_GPT.json",
        "BMC_Base_Conocimiento_GPT-2.json"
    ],
    "level_2_validation": [
        "BMC_Base_Unificada_v4.json"
    ],
    "level_3_dynamic": [
        "panelin_truth_bmcuruguay_web_only_v2.json"
    ],
    "level_4_support": [
        "Aleros -2.rtf",
        "panelin_truth_bmcuruguay_catalog_v2_index.csv",
        # Internal cost matrix (optimized JSON with indices)
        "wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_OPTIMIZED.json",
    ]
}

# Base paths
PROJECT_ROOT = Path(__file__).parent
FILES_DIR = PROJECT_ROOT / "Files"


class KBIndexingAgent:
    """Expert agent for KB indexing and retrieval"""
    
    def __init__(self, kb_path: Optional[Path] = None):
        self.kb_path = kb_path or PROJECT_ROOT
        self.files_dir = FILES_DIR
        self._index_cache = {}
        self._metadata_cache = {}
        self._cost_matrix_cache: Optional[Dict[str, Any]] = None
        self._cost_matrix_by_code: Dict[str, Dict[str, Any]] = {}
        self._cost_matrix_by_category: Dict[str, List[Dict[str, Any]]] = {}
    
    def _load_json_file(self, filename: str, level: int) -> Optional[Dict]:
        """Load JSON file from appropriate location"""
        # Try project root first
        file_path = self.kb_path / filename
        if not file_path.exists():
            # Try Files directory
            file_path = self.files_dir / filename
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Cache metadata
                self._metadata_cache[filename] = {
                    "level": level,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
                return data
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return None
    
    def _index_json_structure(self, data: Dict, prefix: str = "", level: int = 1) -> List[Dict]:
        """Create searchable index from JSON structure"""
        index = []
        
        def traverse(obj, path: str, depth: int = 0):
            if depth > 10:  # Prevent infinite recursion
                return
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Index key
                    index.append({
                        "key": key,
                        "path": current_path,
                        "level": level,
                        "type": "key",
                        "value_type": type(value).__name__
                    })
                    
                    # Index value if it's a leaf node
                    if isinstance(value, (str, int, float, bool)):
                        index.append({
                            "key": key,
                            "path": current_path,
                            "level": level,
                            "type": "value",
                            "value": str(value),
                            "value_type": type(value).__name__
                        })
                    else:
                        traverse(value, current_path, depth + 1)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    traverse(item, current_path, depth + 1)
        
        traverse(data, prefix)
        return index
    
    def build_index(self, level: Optional[int] = None) -> Dict[str, Any]:
        """Build comprehensive index of KB files"""
        index = {
            "timestamp": datetime.now().isoformat(),
            "levels": {},
            "total_entries": 0,
            "products_indexed": 0,
            "formulas_indexed": 0
        }
        
        levels_to_index = [level] if level else [1, 2, 3, 4]
        
        for kb_level in levels_to_index:
            level_key = f"level_{kb_level}"
            files_key = f"level_{kb_level}_{['master', 'validation', 'dynamic', 'support'][kb_level-1]}"
            
            if files_key not in KB_HIERARCHY:
                continue
            
            level_index = {
                "files": {},
                "total_entries": 0
            }
            
            for filename in KB_HIERARCHY[files_key]:
                data = self._load_json_file(filename, kb_level)
                if data:
                    # Special-case: the cost matrix is already indexed; don't explode it into huge key/value entries.
                    if "BROMYROS_Costos_Ventas_2026_OPTIMIZED.json" in filename:
                        file_index = self._index_cost_matrix(data, kb_level)
                    else:
                        file_index = self._index_json_structure(data, "", kb_level)
                    level_index["files"][filename] = {
                        "entries": file_index,
                        "count": len(file_index),
                        "metadata": self._metadata_cache.get(filename, {})
                    }
                    level_index["total_entries"] += len(file_index)
                    
                    # Count products and formulas
                    if kb_level == 1:
                        if "productos" in data:
                            level_index["products_indexed"] = len(data.get("productos", {}))
                        if "formulas_cotizacion" in data:
                            level_index["formulas_indexed"] = len(data.get("formulas_cotizacion", {}))
            
            index["levels"][level_key] = level_index
            index["total_entries"] += level_index["total_entries"]
        
        self._index_cache = index
        return index

    def _index_cost_matrix(self, data: Dict[str, Any], level: int) -> List[Dict[str, Any]]:
        """
        Create a compact index for the optimized cost matrix JSON.
        We index product codes, names, categories, and a few key numeric fields to keep search fast.
        """
        entries: List[Dict[str, Any]] = []

        # index by_code
        by_code = (data.get("indices", {}) or {}).get("by_code", {}) or {}
        for code, rec in by_code.items():
            entries.append({
                "key": code,
                "path": f"indices.by_code.{code}",
                "level": level,
                "type": "cost_matrix_code",
                "value": rec.get("nombre", ""),
                "value_type": "product_code",
            })

        # index categories
        by_cat = (data.get("indices", {}) or {}).get("by_category", {}) or {}
        for cat, codes in by_cat.items():
            entries.append({
                "key": cat,
                "path": f"indices.by_category.{cat}",
                "level": level,
                "type": "cost_matrix_category",
                "value": str(len(codes)) if isinstance(codes, list) else "",
                "value_type": "category",
            })

        return entries

    # ------------------------------------------------------------------------
    # Cost Matrix Helpers (fast O(1) access)
    # ------------------------------------------------------------------------

    def _load_cost_matrix(self) -> Optional[Dict[str, Any]]:
        """Load and cache the internal cost matrix JSON."""
        if self._cost_matrix_cache is not None:
            return self._cost_matrix_cache

        cm_path = "wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_OPTIMIZED.json"
        data = self._load_json_file(cm_path, 4)
        if not data:
            self._cost_matrix_cache = None
            self._cost_matrix_by_code = {}
            self._cost_matrix_by_category = {}
            return None

        products = (data.get("productos", {}) or {}).get("todos", []) or []
        self._cost_matrix_by_code = {p.get("codigo", ""): p for p in products if p.get("codigo")}
        self._cost_matrix_by_category = (data.get("productos", {}) or {}).get("por_categoria", {}) or {}
        self._cost_matrix_cache = data
        return data

    def get_cost_matrix_product(self, code: str) -> Dict[str, Any]:
        """Get a product from the internal cost matrix by product code."""
        data = self._load_cost_matrix()
        if not data:
            return {"error": "Cost matrix not available"}

        code_norm = (code or "").strip()
        if not code_norm:
            return {"error": "Missing product code"}

        product = self._cost_matrix_by_code.get(code_norm)
        if not product and code_norm.upper() != code_norm:
            product = self._cost_matrix_by_code.get(code_norm.upper())
        if not product:
            return {"error": f"Product code not found in cost matrix: {code_norm}"}

        return {
            "source": "cost_matrix_bromyros",
            "file": "wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_OPTIMIZED.json",
            "product": product,
        }

    def get_cost_matrix_products_by_category(self, category: str) -> Dict[str, Any]:
        """Get all products from the internal cost matrix by category."""
        data = self._load_cost_matrix()
        if not data:
            return {"error": "Cost matrix not available"}

        cat = (category or "").strip()
        if not cat:
            return {"error": "Missing category"}

        products = self._cost_matrix_by_category.get(cat)
        if products is None:
            return {"error": f"Category not found in cost matrix: {cat}"}

        return {
            "source": "cost_matrix_bromyros",
            "file": "wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_OPTIMIZED.json",
            "category": cat,
            "count": len(products),
            "products": products,
        }
    
    def search_kb(
        self,
        query: str,
        level_priority: Optional[int] = None,
        search_type: str = "hybrid",
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search KB with hybrid semantic + keyword + structured search
        
        Args:
            query: Search query
            level_priority: Preferred KB level (1-4), None for all levels
            search_type: "hybrid", "keyword", "semantic", or "structured"
            max_results: Maximum results to return
        """
        # Fast path: if the query contains a known cost-matrix product code, return it immediately.
        cm = self._load_cost_matrix()
        if cm:
            # Extract candidate tokens (codes are usually short-ish alphanumerics with optional dots)
            tokens = re.findall(r"[A-Za-z0-9\\.]{3,}", query.strip())
            for tok in tokens:
                if tok in self._cost_matrix_by_code or tok.upper() in self._cost_matrix_by_code:
                    product = self._cost_matrix_by_code.get(tok) or self._cost_matrix_by_code.get(tok.upper())
                    return {
                        "query": query,
                        "search_type": "fast_cost_matrix",
                        "level_priority": level_priority,
                        "total_matches": 1,
                        "results": [{
                            "entry": {
                                "type": "cost_matrix_product",
                                "code": product.get("codigo"),
                                "name": product.get("nombre"),
                                "category": product.get("categoria"),
                                "product": product,
                            },
                            "score": 100.0,
                            "level": 4,
                            "file": "wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_OPTIMIZED.json",
                            "match_type": "cost_matrix_code",
                            "metadata": {"source": "cost_matrix_index"},
                        }]
                    }

        if not self._index_cache:
            self.build_index()
        
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Determine which levels to search
        levels_to_search = [level_priority] if level_priority else [1, 2, 3, 4]
        
        for level in levels_to_search:
            level_key = f"level_{level}"
            if level_key not in self._index_cache.get("levels", {}):
                continue
            
            level_data = self._index_cache["levels"][level_key]
            
            for filename, file_data in level_data.get("files", {}).items():
                for entry in file_data.get("entries", []):
                    score = 0.0
                    match_type = None
                    
                    # Keyword matching
                    if search_type in ["hybrid", "keyword"]:
                        key_lower = entry.get("key", "").lower()
                        path_lower = entry.get("path", "").lower()
                        value_lower = entry.get("value", "").lower() if entry.get("value") else ""
                        
                        # Exact match
                        if query_lower in key_lower or query_lower in path_lower:
                            score += 10.0
                            match_type = "exact_key"
                        elif query_lower in value_lower:
                            score += 8.0
                            match_type = "exact_value"
                        
                        # Word matching
                        key_words = set(key_lower.split("_"))
                        path_words = set(re.findall(r'\w+', path_lower))
                        value_words = set(value_lower.split()) if value_lower else set()
                        
                        common_words = query_words.intersection(key_words.union(path_words).union(value_words))
                        if common_words:
                            score += len(common_words) * 2.0
                            match_type = match_type or "word_match"
                    
                    # Structured search (path-based)
                    if search_type in ["hybrid", "structured"]:
                        path = entry.get("path", "")
                        # Boost score for product-related paths
                        if any(term in path for term in ["producto", "precio", "espesor", "autoportancia"]):
                            score += 1.0
                    
                    if score > 0:
                        results.append({
                            "entry": entry,
                            "score": score,
                            "level": level,
                            "file": filename,
                            "match_type": match_type,
                            "metadata": file_data.get("metadata", {})
                        })
        
        # Sort by score (descending) and level priority
        results.sort(key=lambda x: (x["score"], -x["level"]), reverse=True)
        
        # Limit results
        results = results[:max_results]
        
        return {
            "query": query,
            "search_type": search_type,
            "level_priority": level_priority,
            "total_matches": len(results),
            "results": results
        }
    
    def get_product_info(
        self,
        product_name: str,
        thickness: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get product information from Level 1 (Master)"""
        # Load Level 1 master file
        master_file = KB_HIERARCHY["level_1_master"][-1]  # Use latest version
        data = self._load_json_file(master_file, 1)
        
        if not data:
            return {"error": "Master KB file not found"}
        
        # Normalize product name
        product_key = None
        for key in data.get("productos", {}).keys():
            if product_name.upper() in key.upper() or key.upper() in product_name.upper():
                product_key = key
                break
        
        if not product_key:
            return {"error": f"Product {product_name} not found in KB"}
        
        product_data = data["productos"][product_key]
        
        result = {
            "product": product_key,
            "source": master_file,
            "level": 1,
            "thicknesses": {}
        }
        
        if thickness:
            # Get specific thickness
            if "espesores" in product_data and thickness in product_data["espesores"]:
                result["thicknesses"][thickness] = product_data["espesores"][thickness]
            else:
                result["error"] = f"Thickness {thickness} not found for {product_key}"
        else:
            # Get all thicknesses
            if "espesores" in product_data:
                result["thicknesses"] = product_data["espesores"]
        
        return result
    
    def get_formula(self, formula_name: str) -> Dict[str, Any]:
        """Get formula from Level 1 (Master)"""
        master_file = KB_HIERARCHY["level_1_master"][-1]
        data = self._load_json_file(master_file, 1)
        
        if not data:
            return {"error": "Master KB file not found"}
        
        # Search in formulas_cotizacion
        formulas = data.get("formulas_cotizacion", {})
        if formula_name in formulas:
            return {
                "formula": formula_name,
                "value": formulas[formula_name],
                "source": master_file,
                "level": 1
            }
        
        # Search in formulas_ahorro_energetico
        energy_formulas = data.get("formulas_ahorro_energetico", {})
        if formula_name in energy_formulas:
            return {
                "formula": formula_name,
                "value": energy_formulas[formula_name],
                "source": master_file,
                "level": 1,
                "category": "energy_savings"
            }
        
        return {"error": f"Formula {formula_name} not found"}
    
    def validate_kb_health(self) -> Dict[str, Any]:
        """Validate KB health and detect conflicts"""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "levels": {},
            "conflicts": [],
            "warnings": []
        }
        
        # Check each level
        for level in [1, 2, 3, 4]:
            level_key = f"level_{level}"
            files_key = f"level_{level}_{['master', 'validation', 'dynamic', 'support'][level-1]}"
            
            level_status = {
                "files_found": 0,
                "files_missing": [],
                "files_valid": []
            }
            
            for filename in KB_HIERARCHY.get(files_key, []):
                file_path = self.kb_path / filename
                if not file_path.exists():
                    file_path = self.files_dir / filename
                
                if file_path.exists():
                    level_status["files_found"] += 1
                    # Validate JSON
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            json.load(f)
                        level_status["files_valid"].append(filename)
                    except json.JSONDecodeError:
                        health_report["warnings"].append(f"Invalid JSON in {filename}")
                else:
                    level_status["files_missing"].append(filename)
            
            health_report["levels"][level_key] = level_status
            
            if level_status["files_missing"]:
                health_report["status"] = "degraded"
                health_report["warnings"].append(f"Level {level}: Missing files: {level_status['files_missing']}")
        
        # Detect conflicts between levels (simplified)
        if health_report["levels"].get("level_1", {}).get("files_found", 0) > 0:
            health_report["status"] = "healthy" if not health_report["warnings"] else "degraded"
        
        return health_report
    
    def get_kb_metadata(self) -> Dict[str, Any]:
        """Get comprehensive KB metadata"""
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "hierarchy": KB_HIERARCHY,
            "files": {}
        }
        
        for level in [1, 2, 3, 4]:
            files_key = f"level_{level}_{['master', 'validation', 'dynamic', 'support'][level-1]}"
            for filename in KB_HIERARCHY.get(files_key, []):
                file_path = self.kb_path / filename
                if not file_path.exists():
                    file_path = self.files_dir / filename
                
                if file_path.exists():
                    stat = file_path.stat()
                    metadata["files"][filename] = {
                        "level": level,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "exists": True
                    }
                else:
                    metadata["files"][filename] = {
                        "level": level,
                        "exists": False
                    }
        
        return metadata


# ============================================================================
# FUNCTION SCHEMAS FOR GPT OPENAI ACTIONS
# ============================================================================

def get_kb_search_function_schema() -> Dict:
    """Get KB search function schema for OpenAI Actions"""
    return {
        "name": "search_knowledge_base",
        "description": "Search the Knowledge Base using hybrid semantic + keyword + structured search. Returns indexed results from the 4-level hierarchical KB system. Use this to find product information, prices, formulas, specifications, and technical data.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'ISODEC 100mm price', 'autoportancia 150mm', 'formula cantidad paneles')"
                },
                "level_priority": {
                    "type": "integer",
                    "enum": [1, 2, 3, 4],
                    "description": "Preferred KB level: 1=Master (highest priority), 2=Validation, 3=Dynamic, 4=Support. Leave null to search all levels."
                },
                "search_type": {
                    "type": "string",
                    "enum": ["hybrid", "keyword", "semantic", "structured"],
                    "description": "Search strategy: 'hybrid' (recommended), 'keyword' for exact matches, 'semantic' for meaning-based, 'structured' for path-based",
                    "default": "hybrid"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 10)",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50
                }
            },
            "required": ["query"]
        }
    }


def get_product_info_function_schema() -> Dict:
    """Get product info function schema for OpenAI Actions"""
    return {
        "name": "get_product_information",
        "description": "Get detailed product information from Level 1 Master KB. Returns product specifications, prices, thicknesses, autoportancia, thermal coefficients, and technical data. This is the authoritative source for all product data.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "Product name (e.g., 'ISODEC EPS', 'ISOPANEL EPS', 'ISOROOF 3G', 'ISOWALL PIR')"
                },
                "thickness": {
                    "type": "string",
                    "description": "Optional: Specific thickness in mm (e.g., '100', '150', '200'). If not provided, returns all available thicknesses."
                }
            },
            "required": ["product_name"]
        }
    }


def get_formula_function_schema() -> Dict:
    """Get formula function schema for OpenAI Actions"""
    return {
        "name": "get_formula",
        "description": "Get quotation or energy savings formulas from Level 1 Master KB. Returns formula definitions used for calculations in quotations.",
        "parameters": {
            "type": "object",
            "properties": {
                "formula_name": {
                    "type": "string",
                    "description": "Formula name to retrieve (e.g., 'cantidad_paneles', 'fijaciones_por_panel', 'ahorro_climatizacion')"
                }
            },
            "required": ["formula_name"]
        }
    }


def get_kb_health_function_schema() -> Dict:
    """Get KB health validation function schema for OpenAI Actions"""
    return {
        "name": "validate_kb_health",
        "description": "Validate Knowledge Base health, check file availability, detect conflicts between levels, and generate health report. Use this to ensure KB integrity before critical operations.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }


def get_kb_metadata_function_schema() -> Dict:
    """Get KB metadata function schema for OpenAI Actions"""
    return {
        "name": "get_kb_metadata",
        "description": "Get comprehensive metadata about the Knowledge Base structure, file locations, sizes, modification dates, and hierarchy. Useful for understanding KB organization and file status.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }


def get_build_index_function_schema() -> Dict:
    """Get build index function schema for OpenAI Actions"""
    return {
        "name": "build_kb_index",
        "description": "Build or rebuild the Knowledge Base search index for optimized retrieval. Creates a comprehensive index of all KB files across all levels. Use this when KB files are updated or for initial setup.",
        "parameters": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "integer",
                    "enum": [1, 2, 3, 4],
                    "description": "Optional: Build index for specific level only. If not provided, indexes all levels."
                }
            },
            "required": []
        }
    }


def get_cost_matrix_product_function_schema() -> Dict:
    """Get cost matrix product by code function schema for OpenAI Actions"""
    return {
        "name": "get_cost_matrix_product",
        "description": "Get a product record from the internal Cost Matrix (Matriz de Costos y Ventas) by product code. Returns costs, margins, and prices. INTERNAL USE ONLY (contains sensitive cost data).",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Product code (e.g., 'IAGRO30', 'ISD150EPS', 'PU50MM')"
                }
            },
            "required": ["code"]
        }
    }


def get_cost_matrix_products_by_category_function_schema() -> Dict:
    """Get cost matrix products by category function schema for OpenAI Actions"""
    return {
        "name": "get_cost_matrix_products_by_category",
        "description": "List all products from the internal Cost Matrix by category (e.g., 'isodec_eps', 'isoroof', 'perfil'). INTERNAL USE ONLY (contains sensitive cost data).",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Category key (e.g., 'isoroof_foil', 'isodec_eps', 'anclaje', 'perfil')"
                }
            },
            "required": ["category"]
        }
    }


# ============================================================================
# FUNCTION IMPLEMENTATIONS FOR GPT
# ============================================================================

# Global agent instance
_kb_agent = KBIndexingAgent()


def search_knowledge_base(
    query: str,
    level_priority: Optional[int] = None,
    search_type: str = "hybrid",
    max_results: int = 10
) -> Dict[str, Any]:
    """Search KB - Function for GPT OpenAI Actions"""
    return _kb_agent.search_kb(query, level_priority, search_type, max_results)


def get_product_information(
    product_name: str,
    thickness: Optional[str] = None
) -> Dict[str, Any]:
    """Get product info - Function for GPT OpenAI Actions"""
    return _kb_agent.get_product_info(product_name, thickness)


def get_formula(formula_name: str) -> Dict[str, Any]:
    """Get formula - Function for GPT OpenAI Actions"""
    return _kb_agent.get_formula(formula_name)


def validate_kb_health() -> Dict[str, Any]:
    """Validate KB health - Function for GPT OpenAI Actions"""
    return _kb_agent.validate_kb_health()


def get_kb_metadata() -> Dict[str, Any]:
    """Get KB metadata - Function for GPT OpenAI Actions"""
    return _kb_agent.get_kb_metadata()


def build_kb_index(level: Optional[int] = None) -> Dict[str, Any]:
    """Build KB index - Function for GPT OpenAI Actions"""
    return _kb_agent.build_index(level)


def get_cost_matrix_product(code: str) -> Dict[str, Any]:
    """Get cost matrix product by code - Function for GPT OpenAI Actions"""
    return _kb_agent.get_cost_matrix_product(code)


def get_cost_matrix_products_by_category(category: str) -> Dict[str, Any]:
    """Get cost matrix products by category - Function for GPT OpenAI Actions"""
    return _kb_agent.get_cost_matrix_products_by_category(category)


# ============================================================================
# ALL FUNCTION SCHEMAS (for easy import)
# ============================================================================

def get_all_kb_function_schemas() -> List[Dict]:
    """Get all KB function schemas for OpenAI Actions"""
    return [
        get_kb_search_function_schema(),
        get_product_info_function_schema(),
        get_formula_function_schema(),
        get_kb_health_function_schema(),
        get_kb_metadata_function_schema(),
        get_build_index_function_schema(),
        get_cost_matrix_product_function_schema(),
        get_cost_matrix_products_by_category_function_schema(),
    ]
