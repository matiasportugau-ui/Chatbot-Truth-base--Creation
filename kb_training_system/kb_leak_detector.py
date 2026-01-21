"""
Knowledge Base Leak Detector
=============================

Detects knowledge gaps and leaks in chatbot interactions.
Identifies missing information, incorrect responses, and KB coverage issues.
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import re
from collections import defaultdict
from loguru import logger


@dataclass
class KnowledgeLeak:
    """Represents a detected knowledge leak"""
    leak_id: str
    leak_type: str  # "missing_info", "incorrect_response", "source_mismatch", "coverage_gap"
    query: str
    response: str
    detected_at: str
    severity: str  # "critical", "high", "medium", "low"
    category: str  # "pricing", "specifications", "formulas", "general"
    missing_information: Optional[str] = None
    expected_source: Optional[str] = None
    actual_sources: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class LeakAnalysisReport:
    """Comprehensive leak analysis report"""
    timestamp: str
    total_leaks: int
    leaks_by_type: Dict[str, int]
    leaks_by_severity: Dict[str, int]
    leaks_by_category: Dict[str, int]
    critical_leaks: List[KnowledgeLeak]
    kb_coverage_gaps: List[str]
    recommendations: List[str]
    detailed_leaks: List[KnowledgeLeak] = field(default_factory=list)


class KnowledgeBaseLeakDetector:
    """
    Detects knowledge leaks and gaps in chatbot knowledge base.
    
    Leak Types:
    1. Missing Information: Query asks for data not in KB
    2. Incorrect Response: Response contradicts KB or ground truth
    3. Source Mismatch: Wrong source used (e.g., Level 2 instead of Level 1)
    4. Coverage Gap: KB doesn't cover common query patterns
    """
    
    def __init__(
        self,
        knowledge_base_path: Optional[str] = None,
        leak_history_path: Optional[str] = None
    ):
        """
        Initialize leak detector
        
        Args:
            knowledge_base_path: Path to knowledge base directory
            leak_history_path: Path to store leak history
        """
        self.kb_path = Path(knowledge_base_path) if knowledge_base_path else None
        self.leak_history_path = Path(leak_history_path) if leak_history_path else Path("kb_training_system/leak_history")
        self.leak_history_path.mkdir(parents=True, exist_ok=True)
        self.detected_leaks: List[KnowledgeLeak] = []
        
        # Load existing leak history
        self._load_leak_history()
    
    def detect_leaks_in_interaction(
        self,
        query: str,
        response: str,
        sources_consulted: List[str],
        ground_truth: Optional[str] = None,
        expected_sources: Optional[List[str]] = None
    ) -> List[KnowledgeLeak]:
        """
        Detect leaks in a single interaction
        
        Args:
            query: User query
            response: Chatbot response
            sources_consulted: Sources used
            ground_truth: Expected answer (optional)
            expected_sources: Expected sources (optional)
            
        Returns:
            List of detected leaks
        """
        leaks = []
        
        # 1. Missing Information Leak
        missing_leaks = self._detect_missing_information(query, response, sources_consulted)
        leaks.extend(missing_leaks)
        
        # 2. Incorrect Response Leak
        if ground_truth:
            incorrect_leaks = self._detect_incorrect_response(
                query, response, ground_truth, sources_consulted
            )
            leaks.extend(incorrect_leaks)
        
        # 3. Source Mismatch Leak
        if expected_sources:
            source_leaks = self._detect_source_mismatch(
                sources_consulted, expected_sources, query
            )
            leaks.extend(source_leaks)
        
        # 4. Coverage Gap (if no sources consulted)
        if not sources_consulted:
            coverage_leak = self._detect_coverage_gap(query, response)
            if coverage_leak:
                leaks.append(coverage_leak)
        
        # Store leaks
        self.detected_leaks.extend(leaks)
        self._save_leak_history()
        
        return leaks
    
    def _detect_missing_information(
        self,
        query: str,
        response: str,
        sources: List[str]
    ) -> List[KnowledgeLeak]:
        """Detect missing information leaks"""
        leaks = []
        
        # Patterns indicating missing information
        missing_patterns = [
            r"no tengo (esa|la) información",
            r"no (está|estan) disponible",
            r"no encuentro",
            r"no sé",
            r"no disponible en base",
            r"no (tengo|tiene) (esa|ese|esa) (información|dato|precio)"
        ]
        
        response_lower = response.lower()
        
        for pattern in missing_patterns:
            if re.search(pattern, response_lower):
                # Extract what's missing
                query_lower = query.lower()
                category = self._categorize_query(query)
                
                leak = KnowledgeLeak(
                    leak_id=f"LEAK-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{len(leaks)}",
                    leak_type="missing_info",
                    query=query,
                    response=response,
                    detected_at=datetime.now().isoformat(),
                    severity=self._assess_severity(query, category),
                    category=category,
                    missing_information=self._extract_missing_info(query, response),
                    actual_sources=sources,
                    recommendations=[
                        f"Add information about {category} to knowledge base",
                        f"Consider adding to Level 1 (Master) source for {category}"
                    ]
                )
                leaks.append(leak)
        
        # Check for vague responses to specific queries
        specific_indicators = {
            "precio": ["precio", "costo", "valor", "$"],
            "espesor": ["espesor", "thickness", "grosor"],
            "autoportancia": ["autoportancia", "luz", "span", "distancia"],
            "fórmula": ["fórmula", "cálculo", "formula", "calcular"]
        }
        
        query_lower = query.lower()
        for indicator_type, keywords in specific_indicators.items():
            if any(kw in query_lower for kw in keywords):
                # Check if response contains the specific data
                if not any(kw in response_lower for kw in keywords):
                    if not any(pattern in response_lower for pattern in missing_patterns):
                        # Vague response to specific query
                        leak = KnowledgeLeak(
                            leak_id=f"LEAK-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{len(leaks)}",
                            leak_type="missing_info",
                            query=query,
                            response=response,
                            detected_at=datetime.now().isoformat(),
                            severity="high",
                            category=indicator_type,
                            missing_information=f"Specific {indicator_type} data not provided",
                            actual_sources=sources,
                            recommendations=[
                                f"Ensure {indicator_type} information is available in KB",
                                f"Add {indicator_type} to Level 1 source if missing"
                            ]
                        )
                        leaks.append(leak)
        
        return leaks
    
    def _detect_incorrect_response(
        self,
        query: str,
        response: str,
        ground_truth: str,
        sources: List[str]
    ) -> List[KnowledgeLeak]:
        """Detect incorrect response leaks"""
        leaks = []
        
        # Simple comparison (can be enhanced with semantic similarity)
        response_lower = response.lower()
        truth_lower = ground_truth.lower()
        
        # Extract key numbers (prices, measurements)
        response_numbers = set(re.findall(r'\d+\.?\d*', response))
        truth_numbers = set(re.findall(r'\d+\.?\d*', truth_lower))
        
        # Check for significant number mismatches
        if truth_numbers:
            mismatch_rate = len(truth_numbers - response_numbers) / len(truth_numbers)
            if mismatch_rate > 0.3:  # More than 30% mismatch
                leak = KnowledgeLeak(
                    leak_id=f"LEAK-{datetime.now().strftime('%Y%m%d-%H%M%S')}-INCORRECT",
                    leak_type="incorrect_response",
                    query=query,
                    response=response,
                    detected_at=datetime.now().isoformat(),
                    severity="critical",
                    category=self._categorize_query(query),
                    missing_information=f"Response doesn't match ground truth. Expected: {ground_truth[:100]}",
                    actual_sources=sources,
                    recommendations=[
                        "Verify KB data accuracy",
                        "Check if KB needs update",
                        "Review source hierarchy compliance"
                    ]
                )
                leaks.append(leak)
        
        return leaks
    
    def _detect_source_mismatch(
        self,
        actual_sources: List[str],
        expected_sources: List[str],
        query: str
    ) -> List[KnowledgeLeak]:
        """Detect source mismatch leaks"""
        leaks = []
        
        # Check if Level 1 source expected but not used
        level_1_files = [
            "BMC_Base_Conocimiento_GPT.json",
            "BMC_Base_Conocimiento_GPT-2.json"
        ]
        
        expected_level_1 = any(
            any(level_1 in exp for level_1 in level_1_files)
            for exp in expected_sources
        )
        
        actual_level_1 = any(
            any(level_1 in act for level_1 in level_1_files)
            for act in actual_sources
        )
        
        if expected_level_1 and not actual_level_1:
            leak = KnowledgeLeak(
                leak_id=f"LEAK-{datetime.now().strftime('%Y%m%d-%H%M%S')}-SOURCE",
                leak_type="source_mismatch",
                query=query,
                response="",
                detected_at=datetime.now().isoformat(),
                severity="high",
                category="source_compliance",
                expected_source="Level 1 (Master)",
                actual_sources=actual_sources,
                recommendations=[
                    "Use Level 1 (Master) source for prices and formulas",
                    "Update instructions to enforce source hierarchy"
                ]
            )
            leaks.append(leak)
        
        return leaks
    
    def _detect_coverage_gap(
        self,
        query: str,
        response: str
    ) -> Optional[KnowledgeLeak]:
        """Detect coverage gap leaks"""
        # If no sources consulted, it's a coverage gap
        response_lower = response.lower()
        
        # Check if response is generic/hallucinated
        generic_phrases = [
            "en general", "típicamente", "usualmente",
            "puede variar", "depende"
        ]
        
        if any(phrase in response_lower for phrase in generic_phrases):
            return KnowledgeLeak(
                leak_id=f"LEAK-{datetime.now().strftime('%Y%m%d-%H%M%S')}-COVERAGE",
                leak_type="coverage_gap",
                query=query,
                response=response,
                detected_at=datetime.now().isoformat(),
                severity="medium",
                category=self._categorize_query(query),
                recommendations=[
                    "Add specific information to KB for this query type",
                    "Consider adding examples or FAQs"
                ]
            )
        
        return None
    
    def _categorize_query(self, query: str) -> str:
        """Categorize query type"""
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["precio", "costo", "valor", "$"]):
            return "pricing"
        elif any(kw in query_lower for kw in ["espesor", "thickness", "grosor"]):
            return "specifications"
        elif any(kw in query_lower for kw in ["autoportancia", "luz", "span"]):
            return "specifications"
        elif any(kw in query_lower for kw in ["fórmula", "calcular", "cálculo"]):
            return "formulas"
        else:
            return "general"
    
    def _assess_severity(self, query: str, category: str) -> str:
        """Assess leak severity"""
        # Critical categories
        if category in ["pricing", "formulas"]:
            return "critical"
        
        # High severity
        if category == "specifications":
            return "high"
        
        # Medium by default
        return "medium"
    
    def _extract_missing_info(self, query: str, response: str) -> str:
        """Extract what information is missing"""
        # Try to extract key terms from query
        query_lower = query.lower()
        
        # Extract product names, measurements, etc.
        product_keywords = ["isodec", "isoroof", "isopanel", "isowall"]
        found_products = [kw for kw in product_keywords if kw in query_lower]
        
        if found_products:
            return f"Information about {', '.join(found_products)}"
        
        # Extract measurements
        measurements = re.findall(r'\d+\s*(mm|m|cm)', query_lower)
        if measurements:
            return f"Information for {measurements[0]} specification"
        
        return "General information requested in query"
    
    def analyze_leak_patterns(
        self,
        interactions: List[Dict[str, Any]]
    ) -> LeakAnalysisReport:
        """
        Analyze leak patterns across multiple interactions
        
        Args:
            interactions: List of {query, response, sources, ground_truth}
            
        Returns:
            LeakAnalysisReport with comprehensive analysis
        """
        logger.info(f"Analyzing leak patterns in {len(interactions)} interactions")
        
        all_leaks = []
        
        for interaction in interactions:
            leaks = self.detect_leaks_in_interaction(
                query=interaction.get("query", ""),
                response=interaction.get("response", ""),
                sources_consulted=interaction.get("sources", []),
                ground_truth=interaction.get("ground_truth"),
                expected_sources=interaction.get("expected_sources")
            )
            all_leaks.extend(leaks)
        
        # Aggregate analysis
        leaks_by_type = defaultdict(int)
        leaks_by_severity = defaultdict(int)
        leaks_by_category = defaultdict(int)
        
        for leak in all_leaks:
            leaks_by_type[leak.leak_type] += 1
            leaks_by_severity[leak.severity] += 1
            leaks_by_category[leak.category] += 1
        
        critical_leaks = [l for l in all_leaks if l.severity == "critical"]
        
        # Identify coverage gaps
        coverage_gaps = self._identify_coverage_gaps(all_leaks)
        
        # Generate recommendations
        recommendations = self._generate_leak_recommendations(all_leaks)
        
        report = LeakAnalysisReport(
            timestamp=datetime.now().isoformat(),
            total_leaks=len(all_leaks),
            leaks_by_type=dict(leaks_by_type),
            leaks_by_severity=dict(leaks_by_severity),
            leaks_by_category=dict(leaks_by_category),
            critical_leaks=critical_leaks,
            kb_coverage_gaps=coverage_gaps,
            recommendations=recommendations,
            detailed_leaks=all_leaks
        )
        
        return report
    
    def _identify_coverage_gaps(self, leaks: List[KnowledgeLeak]) -> List[str]:
        """Identify KB coverage gaps from leaks"""
        gaps = []
        
        # Group by category
        category_queries = defaultdict(list)
        for leak in leaks:
            category_queries[leak.category].append(leak.query)
        
        for category, queries in category_queries.items():
            if len(queries) >= 3:  # Recurring pattern
                gaps.append(
                    f"{category}: {len(queries)} queries with missing information. "
                    f"Sample: {queries[0][:100]}"
                )
        
        return gaps
    
    def _generate_leak_recommendations(
        self,
        leaks: List[KnowledgeLeak]
    ) -> List[str]:
        """Generate recommendations from leak analysis"""
        recommendations = []
        
        # Count by type
        missing_info = [l for l in leaks if l.leak_type == "missing_info"]
        source_mismatch = [l for l in leaks if l.leak_type == "source_mismatch"]
        incorrect = [l for l in leaks if l.leak_type == "incorrect_response"]
        
        if missing_info:
            top_category = max(
                set(l.category for l in missing_info),
                key=lambda c: sum(1 for l in missing_info if l.category == c)
            )
            recommendations.append(
                f"Add {top_category} information to Level 1 (Master) KB. "
                f"{len(missing_info)} missing information leaks detected."
            )
        
        if source_mismatch:
            recommendations.append(
                f"Enforce Level 1 (Master) source usage. "
                f"{len(source_mismatch)} source mismatch leaks detected."
            )
        
        if incorrect:
            recommendations.append(
                f"Review KB accuracy. {len(incorrect)} incorrect response leaks detected."
            )
        
        # Critical leaks
        critical = [l for l in leaks if l.severity == "critical"]
        if critical:
            recommendations.append(
                f"URGENT: Address {len(critical)} critical leaks immediately."
            )
        
        return recommendations
    
    def _load_leak_history(self):
        """Load leak history from file"""
        history_file = self.leak_history_path / "leak_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert back to KnowledgeLeak objects
                    self.detected_leaks = [
                        KnowledgeLeak(**leak_data)
                        for leak_data in data.get("leaks", [])
                    ]
            except Exception as e:
                logger.warning(f"Error loading leak history: {e}")
    
    def _save_leak_history(self):
        """Save leak history to file"""
        history_file = self.leak_history_path / "leak_history.json"
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "leaks": [
                    {
                        "leak_id": leak.leak_id,
                        "leak_type": leak.leak_type,
                        "query": leak.query,
                        "response": leak.response,
                        "detected_at": leak.detected_at,
                        "severity": leak.severity,
                        "category": leak.category,
                        "missing_information": leak.missing_information,
                        "expected_source": leak.expected_source,
                        "actual_sources": leak.actual_sources,
                        "recommendations": leak.recommendations
                    }
                    for leak in self.detected_leaks
                ]
            }
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving leak history: {e}")
    
    def export_leak_report(
        self,
        report: LeakAnalysisReport,
        output_path: str
    ) -> str:
        """Export leak analysis report"""
        report_text = f"""
# Knowledge Base Leak Analysis Report
Generated: {report.timestamp}

## Executive Summary
- Total Leaks Detected: {report.total_leaks}
- Critical Leaks: {len(report.critical_leaks)}
- Coverage Gaps Identified: {len(report.kb_coverage_gaps)}

## Leak Distribution

### By Type
{self._format_dict(report.leaks_by_type)}

### By Severity
{self._format_dict(report.leaks_by_severity)}

### By Category
{self._format_dict(report.leaks_by_category)}

## Critical Leaks
"""
        for leak in report.critical_leaks[:10]:  # Top 10
            report_text += f"""
### {leak.leak_id}
- **Type**: {leak.leak_type}
- **Category**: {leak.category}
- **Query**: {leak.query[:200]}
- **Missing**: {leak.missing_information}
- **Recommendations**: {', '.join(leak.recommendations)}
"""
        
        report_text += f"""
## Coverage Gaps
"""
        for gap in report.kb_coverage_gaps:
            report_text += f"- {gap}\n"
        
        report_text += f"""
## Recommendations
"""
        for rec in report.recommendations:
            report_text += f"- {rec}\n"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report_text, encoding="utf-8")
        
        logger.info(f"Leak report exported to {output_path}")
        return report_text
    
    def _format_dict(self, d: Dict) -> str:
        """Format dictionary for report"""
        return "\n".join(f"- {k}: {v}" for k, v in d.items())
