"""
GPT Knowledge Base Configuration Agent
======================================

Main orchestrator agent that configures and evolves GPT knowledge bases.
Specialized in GPT creator workflows and knowledge base optimization.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from loguru import logger

from .kb_analyzer import KnowledgeBaseAnalyzer
from .kb_evolver import KnowledgeBaseEvolver
from .gpt_config_generator import GPTConfigGenerator

# Import validation tools from panelin_improvements
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from panelin_improvements.source_of_truth_validator import SourceOfTruthValidator
from panelin_improvements.conflict_detector import ConflictDetector


class GPTKnowledgeBaseAgent:
    """
    Main agent for configuring and evolving GPT knowledge bases.
    
    This agent specializes in:
    - Analyzing knowledge base structure and content
    - Validating knowledge base integrity
    - Detecting and resolving conflicts
    - Evolving knowledge bases based on usage patterns
    - Generating optimal GPT configurations
    """
    
    def __init__(
        self,
        knowledge_base_path: str,
        output_path: Optional[str] = None
    ):
        """
        Initialize GPT Knowledge Base Agent
        
        Args:
            knowledge_base_path: Path to knowledge base files (Files folder)
            output_path: Optional path for generated configurations
        """
        self.kb_path = Path(knowledge_base_path)
        self.output_path = Path(output_path) if output_path else self.kb_path.parent / "gpt_configs"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.analyzer = KnowledgeBaseAnalyzer(str(self.kb_path))
        self.evolver = KnowledgeBaseEvolver(str(self.kb_path))
        self.config_generator = GPTConfigGenerator(str(self.kb_path))
        self.validator = SourceOfTruthValidator(str(self.kb_path))
        self.conflict_detector = ConflictDetector(str(self.kb_path))
        
        logger.info(f"GPT Knowledge Base Agent initialized")
        logger.info(f"Knowledge Base Path: {self.kb_path}")
        logger.info(f"Output Path: {self.output_path}")
    
    def analyze_and_review(self) -> Dict[str, Any]:
        """
        Complete analysis and review of knowledge base files.
        
        Returns:
            Comprehensive analysis report
        """
        logger.info("Starting comprehensive knowledge base analysis...")
        
        # 1. Analyze knowledge base structure
        kb_analysis = self.analyzer.analyze_complete()
        
        # 2. Validate source of truth hierarchy
        validation_results = self._validate_hierarchy()
        
        # 3. Detect conflicts
        conflicts = self._detect_all_conflicts()
        
        # 4. Analyze GPT simulation agent patterns
        gpt_patterns = self._analyze_gpt_patterns()
        
        # 5. Generate recommendations
        recommendations = self._generate_recommendations(
            kb_analysis, validation_results, conflicts, gpt_patterns
        )
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "knowledge_base_analysis": kb_analysis,
            "validation_results": validation_results,
            "conflicts": conflicts,
            "gpt_patterns": gpt_patterns,
            "recommendations": recommendations,
            "health_score": self._calculate_health_score(
                kb_analysis, validation_results, conflicts
            )
        }
        
        # Save report
        report_path = self.output_path / "kb_analysis_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Analysis complete. Report saved to {report_path}")
        return report
    
    def configure_gpt(self, gpt_name: str, use_case: str = "general") -> Dict[str, Any]:
        """
        Generate complete GPT configuration.
        
        Args:
            gpt_name: Name for the GPT
            use_case: Use case type (general, quotation, assistant, etc.)
            
        Returns:
            Complete GPT configuration ready for OpenAI
        """
        logger.info(f"Generating GPT configuration: {gpt_name} ({use_case})")
        
        # Analyze knowledge base
        kb_analysis = self.analyzer.analyze_complete()
        
        # Generate configuration
        config = self.config_generator.generate_config(
            gpt_name=gpt_name,
            use_case=use_case,
            kb_analysis=kb_analysis
        )
        
        # Save configuration
        config_path = self.output_path / f"{gpt_name}_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"GPT configuration saved to {config_path}")
        return config
    
    def evolve_knowledge_base(
        self,
        evolution_strategy: str = "auto",
        target_improvements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evolve knowledge base based on analysis and best practices.
        
        Args:
            evolution_strategy: Strategy for evolution (auto, conservative, aggressive)
            target_improvements: Specific improvements to target
            
        Returns:
            Evolution report with changes made
        """
        logger.info(f"Starting knowledge base evolution ({evolution_strategy})")
        
        # Analyze current state
        current_analysis = self.analyzer.analyze_complete()
        
        # Detect issues
        conflicts = self._detect_all_conflicts()
        
        # Evolve
        evolution_result = self.evolver.evolve(
            current_state=current_analysis,
            conflicts=conflicts,
            strategy=evolution_strategy,
            target_improvements=target_improvements
        )
        
        # Save evolution report
        evolution_path = self.output_path / "kb_evolution_report.json"
        with open(evolution_path, 'w', encoding='utf-8') as f:
            json.dump(evolution_result, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Evolution complete. Report saved to {evolution_path}")
        return evolution_result
    
    def validate_and_fix(self) -> Dict[str, Any]:
        """
        Validate knowledge base and automatically fix issues where possible.
        
        Returns:
            Validation and fix report
        """
        logger.info("Starting validation and auto-fix...")
        
        # Validate hierarchy
        validation_results = self._validate_hierarchy()
        
        # Detect conflicts
        conflicts = self._detect_all_conflicts()
        
        # Attempt fixes
        fixes_applied = []
        for conflict in conflicts.get("conflicts", []):
            if conflict.get("severity") == "critical":
                fix_result = self._attempt_fix(conflict)
                if fix_result.get("fixed"):
                    fixes_applied.append(fix_result)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "validation_results": validation_results,
            "conflicts_detected": len(conflicts.get("conflicts", [])),
            "fixes_applied": fixes_applied,
            "remaining_issues": [
                c for c in conflicts.get("conflicts", [])
                if not any(f["conflict_id"] == c.get("product_id") for f in fixes_applied)
            ]
        }
        
        # Save report
        fix_report_path = self.output_path / "validation_fix_report.json"
        with open(fix_report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Validation and fix complete. Report saved to {fix_report_path}")
        return report
    
    def _validate_hierarchy(self) -> Dict[str, Any]:
        """Validate knowledge base hierarchy"""
        results = {
            "level_1_files": [],
            "level_2_files": [],
            "level_3_files": [],
            "validation_errors": [],
            "validation_warnings": []
        }
        
        # Check Level 1 files
        level_1_files = [
            "BMC_Base_Conocimiento_GPT.json",
            "BMC_Base_Conocimiento_GPT-2.json"
        ]
        for file_name in level_1_files:
            file_path = self.kb_path / file_name
            if file_path.exists():
                results["level_1_files"].append(str(file_path))
            else:
                results["validation_errors"].append(
                    f"CRITICAL: Level 1 file missing: {file_name}"
                )
        
        # Check Level 2 files
        level_2_files = ["BMC_Base_Unificada_v4.json"]
        for file_name in level_2_files:
            file_path = self.kb_path / file_name
            if file_path.exists():
                results["level_2_files"].append(str(file_path))
            else:
                results["validation_warnings"].append(
                    f"Level 2 file missing: {file_name}"
                )
        
        # Check Level 3 files
        level_3_files = ["panelin_truth_bmcuruguay_web_only_v2.json"]
        for file_name in level_3_files:
            file_path = self.kb_path / file_name
            if file_path.exists():
                results["level_3_files"].append(str(file_path))
            else:
                results["validation_warnings"].append(
                    f"Level 3 file missing: {file_name}"
                )
        
        return results
    
    def _detect_all_conflicts(self) -> Dict[str, Any]:
        """Detect all conflicts in knowledge base"""
        # Load knowledge base files
        level_1_data = self._load_level_1_data()
        level_2_data = self._load_level_2_data()
        level_3_data = self._load_level_3_data()
        
        # Detect conflicts
        conflicts = []
        if level_1_data and level_2_data:
            conflicts.extend(
                self.conflict_detector.detect_conflicts(level_1_data, level_2_data)
            )
        if level_1_data and level_3_data:
            conflicts.extend(
                self.conflict_detector.detect_conflicts(level_1_data, level_3_data)
            )
        
        # Generate report
        if conflicts:
            report = self.conflict_detector.generate_report(conflicts)
        else:
            report = {
                "timestamp": datetime.now().isoformat(),
                "total_conflicts": 0,
                "critical": 0,
                "warnings": 0,
                "info": 0,
                "conflicts": []
            }
        
        return report
    
    def _load_level_1_data(self) -> Optional[Dict]:
        """Load Level 1 (Master) data"""
        for file_name in ["BMC_Base_Conocimiento_GPT-2.json", "BMC_Base_Conocimiento_GPT.json"]:
            file_path = self.kb_path / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error loading {file_name}: {e}")
        return None
    
    def _load_level_2_data(self) -> Optional[Dict]:
        """Load Level 2 (Validation) data"""
        file_path = self.kb_path / "BMC_Base_Unificada_v4.json"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading Level 2: {e}")
        return None
    
    def _load_level_3_data(self) -> Optional[Dict]:
        """Load Level 3 (Dynamic) data"""
        file_path = self.kb_path / "panelin_truth_bmcuruguay_web_only_v2.json"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading Level 3: {e}")
        return None
    
    def _analyze_gpt_patterns(self) -> Dict[str, Any]:
        """Analyze GPT simulation agent patterns"""
        patterns = {
            "knowledge_base_hierarchy": True,
            "source_of_truth_enforcement": True,
            "conflict_resolution": "hierarchical",
            "validation_required": True,
            "recommended_structure": {
                "level_1_master": "Primary source for prices, formulas, specifications",
                "level_2_validation": "Cross-reference only",
                "level_3_dynamic": "Price updates and stock status",
                "level_4_support": "Contextual support files"
            }
        }
        return patterns
    
    def _generate_recommendations(
        self,
        kb_analysis: Dict,
        validation_results: Dict,
        conflicts: Dict,
        gpt_patterns: Dict
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Check for missing files
        if validation_results.get("validation_errors"):
            recommendations.append(
                "CRITICAL: Fix missing Level 1 files - these are required for GPT operation"
            )
        
        # Check for conflicts
        if conflicts.get("total_conflicts", 0) > 0:
            critical = conflicts.get("critical", 0)
            if critical > 0:
                recommendations.append(
                    f"URGENT: Resolve {critical} critical conflicts in knowledge base"
                )
            warnings = conflicts.get("warnings", 0)
            if warnings > 0:
                recommendations.append(
                    f"Review {warnings} warning-level conflicts"
                )
        
        # Check knowledge base structure
        kb_files = kb_analysis.get("files_found", [])
        if len(kb_files) < 3:
            recommendations.append(
                "Consider adding more knowledge base files for better coverage"
            )
        
        # Check for evolution opportunities
        if kb_analysis.get("evolution_opportunities"):
            recommendations.append(
                "Knowledge base can be evolved for better GPT performance"
            )
        
        return recommendations
    
    def _calculate_health_score(
        self,
        kb_analysis: Dict,
        validation_results: Dict,
        conflicts: Dict
    ) -> float:
        """Calculate overall health score (0-100)"""
        score = 100.0
        
        # Deduct for errors
        errors = len(validation_results.get("validation_errors", []))
        score -= errors * 20
        
        # Deduct for conflicts
        critical = conflicts.get("critical", 0)
        warnings = conflicts.get("warnings", 0)
        score -= critical * 10
        score -= warnings * 2
        
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, score))
    
    def _attempt_fix(self, conflict: Dict) -> Dict:
        """Attempt to automatically fix a conflict"""
        # This is a placeholder - actual fixes would depend on conflict type
        return {
            "conflict_id": conflict.get("product_id", "unknown"),
            "fixed": False,
            "reason": "Auto-fix not implemented for this conflict type",
            "recommendation": conflict.get("recommendation", "")
        }
