"""
Knowledge Base Evolver
======================

Evolves knowledge base files to improve GPT performance and maintain consistency.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from loguru import logger


class KnowledgeBaseEvolver:
    """
    Evolves knowledge base files based on analysis and best practices.
    """
    
    def __init__(self, knowledge_base_path: str):
        """
        Initialize evolver
        
        Args:
            knowledge_base_path: Path to knowledge base directory
        """
        self.kb_path = Path(knowledge_base_path)
        if not self.kb_path.exists():
            raise ValueError(f"Knowledge base path does not exist: {knowledge_base_path}")
    
    def evolve(
        self,
        current_state: Dict[str, Any],
        conflicts: Optional[Dict[str, Any]] = None,
        strategy: str = "auto",
        target_improvements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evolve knowledge base based on current state and conflicts.
        
        Args:
            current_state: Current knowledge base analysis
            conflicts: Detected conflicts
            strategy: Evolution strategy (auto, conservative, aggressive)
            target_improvements: Specific improvements to target
            
        Returns:
            Evolution report with changes made
        """
        logger.info(f"Starting knowledge base evolution (strategy: {strategy})")
        
        evolution_plan = self._create_evolution_plan(
            current_state, conflicts, strategy, target_improvements
        )
        
        changes_applied = []
        changes_recommended = []
        
        for change in evolution_plan.get("changes", []):
            if change.get("auto_apply", False) and strategy != "conservative":
                result = self._apply_change(change)
                if result.get("applied"):
                    changes_applied.append(result)
            else:
                changes_recommended.append(change)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy,
            "evolution_plan": evolution_plan,
            "changes_applied": changes_applied,
            "changes_recommended": changes_recommended,
            "backup_created": self._create_backup(),
            "summary": {
                "total_changes": len(evolution_plan.get("changes", [])),
                "applied": len(changes_applied),
                "recommended": len(changes_recommended)
            }
        }
        
        logger.info(f"Evolution complete: {len(changes_applied)} changes applied, "
                   f"{len(changes_recommended)} recommended")
        return report
    
    def _create_evolution_plan(
        self,
        current_state: Dict,
        conflicts: Optional[Dict],
        strategy: str,
        target_improvements: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Create plan for knowledge base evolution"""
        plan = {
            "changes": [],
            "priority": "medium"
        }
        
        # Analyze current state
        kb_analysis = current_state.get("knowledge_base_analysis", {})
        quality_metrics = kb_analysis.get("quality_metrics", {})
        evolution_opportunities = kb_analysis.get("evolution_opportunities", [])
        
        # Add changes based on opportunities
        for opportunity in evolution_opportunities:
            change = self._opportunity_to_change(opportunity, strategy)
            if change:
                plan["changes"].append(change)
        
        # Add changes based on conflicts
        if conflicts:
            conflict_changes = self._conflicts_to_changes(conflicts, strategy)
            plan["changes"].extend(conflict_changes)
        
        # Add changes based on target improvements
        if target_improvements:
            target_changes = self._targets_to_changes(target_improvements, strategy)
            plan["changes"].extend(target_changes)
        
        # Prioritize changes
        plan["changes"] = self._prioritize_changes(plan["changes"])
        
        return plan
    
    def _opportunity_to_change(self, opportunity: str, strategy: str) -> Optional[Dict]:
        """Convert evolution opportunity to change plan"""
        change = {
            "type": "enhancement",
            "description": opportunity,
            "auto_apply": False,
            "priority": "medium"
        }
        
        if "Level 1" in opportunity:
            change["type"] = "critical"
            change["priority"] = "high"
            change["action"] = "create_level_1_file"
        
        elif "product catalog" in opportunity.lower():
            change["type"] = "enhancement"
            change["action"] = "expand_products"
            change["auto_apply"] = strategy == "aggressive"
        
        elif "formulas" in opportunity.lower():
            change["type"] = "enhancement"
            change["action"] = "add_formulas"
            change["auto_apply"] = False  # Requires manual review
        
        elif "source of truth" in opportunity.lower():
            change["type"] = "structure"
            change["action"] = "clarify_hierarchy"
            change["auto_apply"] = False
        
        return change
    
    def _conflicts_to_changes(self, conflicts: Dict, strategy: str) -> List[Dict]:
        """Convert conflicts to change plans"""
        changes = []
        
        conflict_list = conflicts.get("conflicts", [])
        for conflict in conflict_list:
            if conflict.get("severity") == "critical":
                change = {
                    "type": "fix",
                    "description": f"Fix critical conflict: {conflict.get('product_id')} - {conflict.get('field')}",
                    "action": "resolve_conflict",
                    "conflict_id": conflict.get("product_id"),
                    "priority": "high",
                    "auto_apply": strategy == "aggressive",
                    "recommendation": conflict.get("recommendation", "")
                }
                changes.append(change)
        
        return changes
    
    def _targets_to_changes(self, targets: List[str], strategy: str) -> List[Dict]:
        """Convert target improvements to change plans"""
        changes = []
        
        for target in targets:
            change = {
                "type": "enhancement",
                "description": f"Target improvement: {target}",
                "action": f"improve_{target.lower().replace(' ', '_')}",
                "priority": "medium",
                "auto_apply": strategy == "aggressive"
            }
            changes.append(change)
        
        return changes
    
    def _prioritize_changes(self, changes: List[Dict]) -> List[Dict]:
        """Prioritize changes by importance"""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            changes,
            key=lambda x: (
                priority_order.get(x.get("priority", "medium"), 1),
                x.get("type") == "critical"
            )
        )
    
    def _apply_change(self, change: Dict) -> Dict:
        """Apply a change to knowledge base"""
        result = {
            "change_id": change.get("description", "unknown"),
            "applied": False,
            "error": None,
            "backup_path": None
        }
        
        action = change.get("action")
        
        try:
            if action == "resolve_conflict":
                # Resolve conflict by updating lower-level files
                result["applied"] = self._resolve_conflict(change)
            elif action == "expand_products":
                # This would require manual input or external data
                result["applied"] = False
                result["error"] = "Product expansion requires manual input"
            elif action == "add_formulas":
                # This would require manual input
                result["applied"] = False
                result["error"] = "Formula addition requires manual input"
            elif action == "clarify_hierarchy":
                # Create hierarchy documentation
                result["applied"] = self._create_hierarchy_doc()
            else:
                result["applied"] = False
                result["error"] = f"Unknown action: {action}"
        
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error applying change: {e}")
        
        return result
    
    def _resolve_conflict(self, change: Dict) -> bool:
        """Resolve a conflict by updating files"""
        # This is a placeholder - actual conflict resolution would depend on conflict type
        logger.info(f"Resolving conflict: {change.get('conflict_id')}")
        return False  # Conservative approach - don't auto-resolve
    
    def _create_hierarchy_doc(self) -> bool:
        """Create hierarchy documentation"""
        doc_path = self.kb_path / "HIERARCHY.md"
        doc_content = """# Knowledge Base Hierarchy

## Level 1 (Master) - Source of Truth
- **Files**: BMC_Base_Conocimiento_GPT.json, BMC_Base_Conocimiento_GPT-2.json
- **Purpose**: Primary source for prices, formulas, and specifications
- **Priority**: HIGHEST - Always use first

## Level 2 (Validation)
- **Files**: BMC_Base_Unificada_v4.json
- **Purpose**: Cross-reference and validation only
- **Priority**: MEDIUM - Do not use for direct responses

## Level 3 (Dynamic)
- **Files**: panelin_truth_bmcuruguay_web_only_v2.json
- **Purpose**: Price updates and stock status
- **Priority**: LOW - Verify against Level 1

## Level 4 (Support)
- **Files**: Aleros -2.rtf, CSV files, Markdown files
- **Purpose**: Contextual support and additional information
- **Priority**: LOWEST - Supplementary only

## Conflict Resolution
When conflicts are detected, always use Level 1 (Master) as the source of truth.
"""
        try:
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            logger.info(f"Hierarchy documentation created: {doc_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating hierarchy doc: {e}")
            return False
    
    def _create_backup(self) -> Optional[str]:
        """Create backup of knowledge base before evolution"""
        backup_dir = self.kb_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"kb_backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # Copy files
        import shutil
        for file_path in self.kb_path.glob("*"):
            if file_path.is_file():
                shutil.copy2(file_path, backup_path / file_path.name)
        
        logger.info(f"Backup created: {backup_path}")
        return str(backup_path)
