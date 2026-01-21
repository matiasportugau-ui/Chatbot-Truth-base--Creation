"""
Knowledge Base Analyzer
=======================

Analyzes knowledge base files to understand structure, content, and quality.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from loguru import logger


class KnowledgeBaseAnalyzer:
    """
    Analyzes knowledge base files for structure, content, and quality.
    """
    
    def __init__(self, knowledge_base_path: str):
        """
        Initialize analyzer
        
        Args:
            knowledge_base_path: Path to knowledge base directory
        """
        self.kb_path = Path(knowledge_base_path)
        if not self.kb_path.exists():
            raise ValueError(f"Knowledge base path does not exist: {knowledge_base_path}")
        
        # Define expected files by hierarchy
        self.level_1_files = [
            "BMC_Base_Conocimiento_GPT.json",
            "BMC_Base_Conocimiento_GPT-2.json"
        ]
        self.level_2_files = ["BMC_Base_Unificada_v4.json"]
        self.level_3_files = ["panelin_truth_bmcuruguay_web_only_v2.json"]
        self.support_files = [
            "Aleros -2.rtf",
            "panelin_truth_bmcuruguay_catalog_v2_index.csv"
        ]
    
    def analyze_complete(self) -> Dict[str, Any]:
        """
        Perform complete analysis of knowledge base.
        
        Returns:
            Comprehensive analysis report
        """
        logger.info("Starting complete knowledge base analysis...")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "knowledge_base_path": str(self.kb_path),
            "files_found": self._find_all_files(),
            "hierarchy_analysis": self._analyze_hierarchy(),
            "content_analysis": self._analyze_content(),
            "structure_analysis": self._analyze_structure(),
            "quality_metrics": self._calculate_quality_metrics(),
            "evolution_opportunities": self._identify_evolution_opportunities(),
            "gpt_readiness": self._assess_gpt_readiness()
        }
        
        logger.info("Knowledge base analysis complete")
        return analysis
    
    def _find_all_files(self) -> List[Dict[str, Any]]:
        """Find all knowledge base files"""
        files_found = []
        
        all_expected = (
            self.level_1_files +
            self.level_2_files +
            self.level_3_files +
            self.support_files
        )
        
        for file_name in all_expected:
            file_path = self.kb_path / file_name
            if file_path.exists():
                file_info = {
                    "name": file_name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "exists": True
                }
                
                # Try to determine file type and level
                if file_name in self.level_1_files:
                    file_info["level"] = 1
                    file_info["role"] = "master"
                elif file_name in self.level_2_files:
                    file_info["level"] = 2
                    file_info["role"] = "validation"
                elif file_name in self.level_3_files:
                    file_info["level"] = 3
                    file_info["role"] = "dynamic"
                else:
                    file_info["level"] = 4
                    file_info["role"] = "support"
                
                files_found.append(file_info)
            else:
                files_found.append({
                    "name": file_name,
                    "path": str(file_path),
                    "exists": False,
                    "level": self._get_level_for_file(file_name),
                    "role": self._get_role_for_file(file_name)
                })
        
        return files_found
    
    def _get_level_for_file(self, file_name: str) -> int:
        """Get hierarchy level for file"""
        if file_name in self.level_1_files:
            return 1
        elif file_name in self.level_2_files:
            return 2
        elif file_name in self.level_3_files:
            return 3
        else:
            return 4
    
    def _get_role_for_file(self, file_name: str) -> str:
        """Get role for file"""
        if file_name in self.level_1_files:
            return "master"
        elif file_name in self.level_2_files:
            return "validation"
        elif file_name in self.level_3_files:
            return "dynamic"
        else:
            return "support"
    
    def _analyze_hierarchy(self) -> Dict[str, Any]:
        """Analyze knowledge base hierarchy"""
        hierarchy = {
            "level_1_master": {
                "expected": self.level_1_files,
                "found": [],
                "complete": False
            },
            "level_2_validation": {
                "expected": self.level_2_files,
                "found": [],
                "complete": False
            },
            "level_3_dynamic": {
                "expected": self.level_3_files,
                "found": [],
                "complete": False
            },
            "level_4_support": {
                "expected": self.support_files,
                "found": [],
                "complete": False
            }
        }
        
        for level_name, level_info in hierarchy.items():
            for file_name in level_info["expected"]:
                file_path = self.kb_path / file_name
                if file_path.exists():
                    level_info["found"].append(file_name)
            
            level_info["complete"] = len(level_info["found"]) == len(level_info["expected"])
        
        return hierarchy
    
    def _analyze_content(self) -> Dict[str, Any]:
        """Analyze content of knowledge base files"""
        content_analysis = {
            "products": 0,
            "formulas": 0,
            "prices": 0,
            "specifications": 0,
            "file_types": {}
        }
        
        # Analyze JSON files
        json_files = (
            self.level_1_files +
            self.level_2_files +
            self.level_3_files
        )
        
        for file_name in json_files:
            file_path = self.kb_path / file_name
            if file_path.exists() and file_path.suffix == ".json":
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    file_analysis = self._analyze_json_content(data)
                    content_analysis["products"] += file_analysis.get("products", 0)
                    content_analysis["formulas"] += file_analysis.get("formulas", 0)
                    content_analysis["prices"] += file_analysis.get("prices", 0)
                    content_analysis["specifications"] += file_analysis.get("specifications", 0)
                    
                    content_analysis["file_types"][file_name] = file_analysis
                except Exception as e:
                    logger.warning(f"Error analyzing {file_name}: {e}")
        
        return content_analysis
    
    def _analyze_json_content(self, data: Any) -> Dict[str, Any]:
        """Analyze content of a JSON structure"""
        analysis = {
            "products": 0,
            "formulas": 0,
            "prices": 0,
            "specifications": 0
        }
        
        data_str = json.dumps(data).lower()
        
        # Count products (look for product-related keys)
        product_indicators = ["product", "producto", "item", "articulo"]
        if any(indicator in data_str for indicator in product_indicators):
            # Try to count actual products
            if isinstance(data, dict):
                if "products" in data:
                    analysis["products"] = len(data["products"]) if isinstance(data["products"], list) else 1
                elif "productos" in data:
                    analysis["products"] = len(data["productos"]) if isinstance(data["productos"], list) else 1
                else:
                    # Estimate based on structure
                    analysis["products"] = len([k for k in data.keys() if "product" in k.lower()])
        
        # Count formulas
        formula_indicators = ["formula", "formulas", "calculo", "calculation"]
        if any(indicator in data_str for indicator in formula_indicators):
            if isinstance(data, dict):
                if "formulas" in data:
                    analysis["formulas"] = len(data["formulas"]) if isinstance(data["formulas"], dict) else 1
                else:
                    analysis["formulas"] = len([k for k in data.keys() if "formula" in k.lower()])
        
        # Count prices
        price_indicators = ["price", "precio", "cost", "costo"]
        if any(indicator in data_str for indicator in price_indicators):
            analysis["prices"] = data_str.count("precio") + data_str.count("price")
        
        # Count specifications
        spec_indicators = ["espesor", "thickness", "autoportancia", "span", "ancho", "width"]
        analysis["specifications"] = sum(data_str.count(indicator) for indicator in spec_indicators)
        
        return analysis
    
    def _analyze_structure(self) -> Dict[str, Any]:
        """Analyze structure of knowledge base"""
        structure = {
            "hierarchy_defined": True,
            "source_of_truth_clear": False,
            "conflict_resolution": "hierarchical",
            "file_organization": "good"
        }
        
        # Check if Level 1 files exist (source of truth)
        level_1_exists = any(
            (self.kb_path / f).exists() for f in self.level_1_files
        )
        structure["source_of_truth_clear"] = level_1_exists
        
        return structure
    
    def _calculate_quality_metrics(self) -> Dict[str, Any]:
        """Calculate quality metrics"""
        files_found = self._find_all_files()
        existing_files = [f for f in files_found if f.get("exists")]
        
        metrics = {
            "completeness": len(existing_files) / len(files_found) if files_found else 0,
            "level_1_present": any(
                f.get("level") == 1 and f.get("exists") for f in files_found
            ),
            "level_2_present": any(
                f.get("level") == 2 and f.get("exists") for f in files_found
            ),
            "level_3_present": any(
                f.get("level") == 3 and f.get("exists") for f in files_found
            ),
            "total_files": len(existing_files),
            "total_size": sum(f.get("size", 0) for f in existing_files)
        }
        
        return metrics
    
    def _identify_evolution_opportunities(self) -> List[str]:
        """Identify opportunities for knowledge base evolution"""
        opportunities = []
        
        files_found = self._find_all_files()
        existing_files = [f for f in files_found if f.get("exists")]
        
        # Check for missing critical files
        level_1_exists = any(f.get("level") == 1 and f.get("exists") for f in files_found)
        if not level_1_exists:
            opportunities.append("Add Level 1 (Master) knowledge base file")
        
        # Check content richness
        content_analysis = self._analyze_content()
        if content_analysis.get("products", 0) < 10:
            opportunities.append("Expand product catalog for better coverage")
        
        if content_analysis.get("formulas", 0) == 0:
            opportunities.append("Add calculation formulas for technical accuracy")
        
        # Check structure
        structure = self._analyze_structure()
        if not structure.get("source_of_truth_clear"):
            opportunities.append("Clarify source of truth hierarchy")
        
        return opportunities
    
    def _assess_gpt_readiness(self) -> Dict[str, Any]:
        """Assess if knowledge base is ready for GPT configuration"""
        readiness = {
            "ready": False,
            "score": 0,
            "requirements_met": [],
            "requirements_missing": [],
            "recommendations": []
        }
        
        score = 0
        max_score = 100
        
        # Requirement 1: Level 1 file exists (40 points)
        files_found = self._find_all_files()
        level_1_exists = any(f.get("level") == 1 and f.get("exists") for f in files_found)
        if level_1_exists:
            score += 40
            readiness["requirements_met"].append("Level 1 (Master) file present")
        else:
            readiness["requirements_missing"].append("Level 1 (Master) file required")
        
        # Requirement 2: Content present (30 points)
        content_analysis = self._analyze_content()
        if content_analysis.get("products", 0) > 0:
            score += 15
            readiness["requirements_met"].append("Product data present")
        else:
            readiness["requirements_missing"].append("Product data needed")
        
        if content_analysis.get("formulas", 0) > 0:
            score += 15
            readiness["requirements_met"].append("Formulas present")
        else:
            readiness["requirements_missing"].append("Formulas recommended")
        
        # Requirement 3: Structure clear (30 points)
        structure = self._analyze_structure()
        if structure.get("source_of_truth_clear"):
            score += 30
            readiness["requirements_met"].append("Source of truth hierarchy clear")
        else:
            readiness["requirements_missing"].append("Define source of truth hierarchy")
        
        readiness["score"] = score
        readiness["ready"] = score >= 70
        
        if not readiness["ready"]:
            readiness["recommendations"].append(
                f"Knowledge base needs improvement. Current score: {score}/100. "
                f"Address missing requirements to reach 70+ score."
            )
        
        return readiness
