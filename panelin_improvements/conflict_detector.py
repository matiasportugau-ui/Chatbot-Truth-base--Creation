"""
Conflict Detection Engine
=========================

Detects conflicts between knowledge base sources and generates reports.
Part of P0.4: Conflict Detection and Reporting
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path


@dataclass
class Conflict:
    """Represents a conflict between knowledge base sources"""
    product_id: str
    field: str
    level_1_value: Any
    level_2_value: Optional[Any] = None
    level_3_value: Optional[Any] = None
    severity: str = "warning"  # "critical", "warning", "info"
    recommendation: str = ""
    detected_at: str = ""
    
    def __post_init__(self):
        if not self.detected_at:
            self.detected_at = datetime.now().isoformat()


class ConflictDetector:
    """
    Detects conflicts between knowledge base sources.
    
    Compares:
    - Level 1 (Master) vs Level 2 (Validation)
    - Level 1 (Master) vs Level 3 (Dynamic)
    - Level 2 vs Level 3
    """
    
    def __init__(self, knowledge_base_path: Optional[str] = None):
        """
        Initialize conflict detector
        
        Args:
            knowledge_base_path: Path to knowledge base directory
        """
        self.kb_path = Path(knowledge_base_path) if knowledge_base_path else None
        self.level_1_files = [
            "BMC_Base_Conocimiento_GPT.json",
            "BMC_Base_Conocimiento_GPT-2.json"
        ]
        self.level_2_files = [
            "BMC_Base_Unificada_v4.json"
        ]
        self.level_3_files = [
            "panelin_truth_bmcuruguay_web_only_v2.json"
        ]
    
    def detect_conflicts(
        self,
        level_1_data: Dict[str, Any],
        level_2_data: Optional[Dict[str, Any]] = None,
        level_3_data: Optional[Dict[str, Any]] = None
    ) -> List[Conflict]:
        """
        Detect conflicts between knowledge base levels
        
        Args:
            level_1_data: Data from Level 1 (Master) source
            level_2_data: Optional data from Level 2 (Validation) source
            level_3_data: Optional data from Level 3 (Dynamic) source
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Compare Level 1 vs Level 2
        if level_2_data:
            conflicts.extend(
                self._compare_levels(level_1_data, level_2_data, "level_2")
            )
        
        # Compare Level 1 vs Level 3
        if level_3_data:
            conflicts.extend(
                self._compare_levels(level_1_data, level_3_data, "level_3")
            )
        
        # Compare Level 2 vs Level 3 (if both exist)
        if level_2_data and level_3_data:
            conflicts.extend(
                self._compare_levels(level_2_data, level_3_data, "level_2_vs_3")
            )
        
        return conflicts
    
    def _compare_levels(
        self,
        level_1_data: Dict[str, Any],
        other_data: Dict[str, Any],
        comparison_type: str
    ) -> List[Conflict]:
        """Compare two data levels and detect conflicts"""
        conflicts = []
        
        # Compare prices
        if "price" in level_1_data or "precio" in level_1_data:
            price_conflict = self._compare_prices(
                level_1_data, other_data, comparison_type
            )
            if price_conflict:
                conflicts.append(price_conflict)
        
        # Compare product specifications
        spec_conflicts = self._compare_specifications(
            level_1_data, other_data, comparison_type
        )
        conflicts.extend(spec_conflicts)
        
        # Compare formulas
        formula_conflicts = self._compare_formulas(
            level_1_data, other_data, comparison_type
        )
        conflicts.extend(formula_conflicts)
        
        return conflicts
    
    def _compare_prices(
        self,
        level_1_data: Dict[str, Any],
        other_data: Dict[str, Any],
        comparison_type: str
    ) -> Optional[Conflict]:
        """Compare prices between levels"""
        price_1 = self._extract_price(level_1_data)
        price_other = self._extract_price(other_data)
        
        if price_1 is None or price_other is None:
            return None
        
        # Calculate difference percentage
        if price_1 > 0:
            diff_percent = abs((price_other - price_1) / price_1) * 100
        else:
            diff_percent = 100 if price_other != price_1 else 0
        
        # Determine severity
        if diff_percent > 5:  # More than 5% difference
            severity = "critical"
        elif diff_percent > 1:  # More than 1% difference
            severity = "warning"
        else:
            severity = "info"
        
        if price_1 != price_other:
            product_id = level_1_data.get("product_id") or level_1_data.get("id", "unknown")
            level_name = "Level 2" if comparison_type == "level_2" else "Level 3"
            
            return Conflict(
                product_id=product_id,
                field="price",
                level_1_value=price_1,
                level_2_value=price_other if comparison_type == "level_2" else None,
                level_3_value=price_other if comparison_type == "level_3" else None,
                severity=severity,
                recommendation=(
                    f"Use Level 1 price (${price_1:.2f}). "
                    f"{level_name} shows ${price_other:.2f} "
                    f"({diff_percent:.2f}% difference). "
                    f"Level 1 always takes precedence."
                )
            )
        
        return None
    
    def _compare_specifications(
        self,
        level_1_data: Dict[str, Any],
        other_data: Dict[str, Any],
        comparison_type: str
    ) -> List[Conflict]:
        """Compare technical specifications"""
        conflicts = []
        spec_fields = ["espesor", "thickness", "autoportancia", "span", "ancho", "width"]
        
        for field in spec_fields:
            value_1 = level_1_data.get(field)
            value_other = other_data.get(field)
            
            if value_1 is not None and value_other is not None and value_1 != value_other:
                product_id = level_1_data.get("product_id") or level_1_data.get("id", "unknown")
                level_name = "Level 2" if comparison_type == "level_2" else "Level 3"
                
                conflicts.append(Conflict(
                    product_id=product_id,
                    field=field,
                    level_1_value=value_1,
                    level_2_value=value_other if comparison_type == "level_2" else None,
                    level_3_value=value_other if comparison_type == "level_3" else None,
                    severity="warning",
                    recommendation=(
                        f"Specification conflict in {field}: "
                        f"Level 1 = {value_1}, {level_name} = {value_other}. "
                        f"Use Level 1 value."
                    )
                ))
        
        return conflicts
    
    def _compare_formulas(
        self,
        level_1_data: Dict[str, Any],
        other_data: Dict[str, Any],
        comparison_type: str
    ) -> List[Conflict]:
        """Compare formulas between levels"""
        conflicts = []
        
        formulas_1 = level_1_data.get("formulas", {})
        formulas_other = other_data.get("formulas", {})
        
        if not formulas_1 or not formulas_other:
            return conflicts
        
        for formula_name, formula_1 in formulas_1.items():
            formula_other = formulas_other.get(formula_name)
            
            if formula_other and formula_1 != formula_other:
                conflicts.append(Conflict(
                    product_id="formulas",
                    field=f"formula_{formula_name}",
                    level_1_value=formula_1,
                    level_2_value=formula_other if comparison_type == "level_2" else None,
                    level_3_value=formula_other if comparison_type == "level_3" else None,
                    severity="critical",
                    recommendation=(
                        f"Formula conflict: {formula_name}. "
                        f"Level 1 formula must be used. "
                        f"Level 1: {formula_1}, "
                        f"Other: {formula_other}"
                    )
                ))
        
        return conflicts
    
    def _extract_price(self, data: Dict[str, Any]) -> Optional[float]:
        """Extract price from data structure"""
        # Try different price field names
        price_fields = ["price", "precio", "precio_usd", "precio_dolar"]
        
        for field in price_fields:
            if field in data:
                price = data[field]
                if isinstance(price, (int, float)):
                    return float(price)
                elif isinstance(price, str):
                    # Remove currency symbols and convert
                    price_clean = price.replace("$", "").replace(",", "").strip()
                    try:
                        return float(price_clean)
                    except ValueError:
                        continue
        
        return None
    
    def generate_report(self, conflicts: List[Conflict]) -> Dict[str, Any]:
        """
        Generate conflict report
        
        Args:
            conflicts: List of detected conflicts
            
        Returns:
            Report dictionary
        """
        critical = [c for c in conflicts if c.severity == "critical"]
        warnings = [c for c in conflicts if c.severity == "warning"]
        info = [c for c in conflicts if c.severity == "info"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_conflicts": len(conflicts),
            "critical": len(critical),
            "warnings": len(warnings),
            "info": len(info),
            "conflicts": [asdict(c) for c in conflicts],
            "summary": {
                "critical_conflicts": [asdict(c) for c in critical],
                "warning_conflicts": [asdict(c) for c in warnings],
                "info_conflicts": [asdict(c) for c in info]
            },
            "recommendations": [
                "Use Level 1 (Master) source for all responses",
                "Update Level 2/3 sources to match Level 1",
                "Review critical conflicts immediately",
                "Monitor conflicts regularly"
            ]
        }
    
    def save_report(self, conflicts: List[Conflict], output_path: str, format: str = "json"):
        """
        Save conflict report to file
        
        Args:
            conflicts: List of conflicts
            output_path: Path to save report
            format: Report format ("json" or "markdown")
        """
        report = self.generate_report(conflicts)
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        elif format == "markdown":
            self._save_markdown_report(report, output_file)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _save_markdown_report(self, report: Dict[str, Any], output_file: Path):
        """Save report in Markdown format"""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Conflict Detection Report\n\n")
            f.write(f"**Generated:** {report['timestamp']}\n\n")
            f.write(f"**Total Conflicts:** {report['total_conflicts']}\n")
            f.write(f"- Critical: {report['critical']}\n")
            f.write(f"- Warnings: {report['warnings']}\n")
            f.write(f"- Info: {report['info']}\n\n")
            
            f.write("## Critical Conflicts\n\n")
            for conflict in report['summary']['critical_conflicts']:
                f.write(f"### {conflict['product_id']} - {conflict['field']}\n")
                f.write(f"- **Level 1 Value:** {conflict['level_1_value']}\n")
                if conflict['level_2_value']:
                    f.write(f"- **Level 2 Value:** {conflict['level_2_value']}\n")
                if conflict['level_3_value']:
                    f.write(f"- **Level 3 Value:** {conflict['level_3_value']}\n")
                f.write(f"- **Recommendation:** {conflict['recommendation']}\n\n")
            
            f.write("## Recommendations\n\n")
            for rec in report['recommendations']:
                f.write(f"- {rec}\n")


if __name__ == "__main__":
    # Example usage
    detector = ConflictDetector()
    
    # Example data
    level_1_data = {
        "product_id": "ISODEC_EPS_100",
        "price": 46.07,
        "espesor": 100,
        "autoportancia": 5.5
    }
    
    level_2_data = {
        "product_id": "ISODEC_EPS_100",
        "price": 46.00,  # Different price
        "espesor": 100,
        "autoportancia": 5.5
    }
    
    # Detect conflicts
    conflicts = detector.detect_conflicts(level_1_data, level_2_data)
    
    print(f"Detected {len(conflicts)} conflicts:")
    for conflict in conflicts:
        print(f"\n{conflict.severity.upper()}: {conflict.product_id} - {conflict.field}")
        print(f"  Level 1: {conflict.level_1_value}")
        print(f"  Level 2: {conflict.level_2_value}")
        print(f"  Recommendation: {conflict.recommendation}")
    
    # Generate report
    report = detector.generate_report(conflicts)
    print(f"\n\nReport Summary:")
    print(f"Total: {report['total_conflicts']}")
    print(f"Critical: {report['critical']}")
    print(f"Warnings: {report['warnings']}")
