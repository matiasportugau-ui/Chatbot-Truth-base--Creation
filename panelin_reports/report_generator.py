#!/usr/bin/env python3
"""
Report Generator
================

Core report generation logic with support for multiple formats
and data sources.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum


class ReportFormat(Enum):
    """Report output formats"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    TEXT = "text"


class ReportGenerator:
    """Generates reports from various data sources"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory for report output
        """
        if output_dir is None:
            output_dir = str(Path(__file__).parent / "output")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_kb_health_report(
        self,
        kb_data: Dict[str, Any],
        format: ReportFormat = ReportFormat.MARKDOWN
    ) -> str:
        """
        Generate Knowledge Base health report
        
        Args:
            kb_data: KB health data
            format: Output format
        
        Returns:
            Report filepath
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report_data = {
            "report_type": "kb_health",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "status": kb_data.get("status", "unknown"),
                "levels_healthy": sum(1 for level in kb_data.get("levels", {}).values() if level.get("files_found", 0) > 0),
                "total_levels": len(kb_data.get("levels", {})),
                "warnings": kb_data.get("warnings", []),
                "conflicts": kb_data.get("conflicts", [])
            },
            "details": kb_data
        }
        
        if format == ReportFormat.JSON:
            filepath = self.output_dir / f"kb_health_{timestamp}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        elif format == ReportFormat.MARKDOWN:
            filepath = self.output_dir / f"kb_health_{timestamp}.md"
            md_content = self._format_kb_health_markdown(report_data)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return str(filepath)
    
    def _format_kb_health_markdown(self, report_data: Dict[str, Any]) -> str:
        """Format KB health report as Markdown"""
        summary = report_data["summary"]
        details = report_data["details"]
        
        lines = [
            "# Knowledge Base Health Report",
            f"\n**Generated**: {report_data['generated_at']}",
            f"\n## Summary",
            f"\n- **Status**: {summary['status']}",
            f"- **Healthy Levels**: {summary['levels_healthy']}/{summary['total_levels']}",
            f"- **Warnings**: {len(summary['warnings'])}",
            f"- **Conflicts**: {len(summary['conflicts'])}",
        ]
        
        if summary['warnings']:
            lines.append("\n## Warnings")
            for warning in summary['warnings']:
                lines.append(f"- {warning}")
        
        if summary['conflicts']:
            lines.append("\n## Conflicts")
            for conflict in summary['conflicts']:
                lines.append(f"- {conflict}")
        
        lines.append("\n## Level Details")
        for level_name, level_data in details.get("levels", {}).items():
            lines.append(f"\n### {level_name}")
            lines.append(f"- Files found: {level_data.get('files_found', 0)}")
            if level_data.get('files_valid'):
                lines.append(f"- Valid files: {', '.join(level_data['files_valid'])}")
            if level_data.get('files_missing'):
                lines.append(f"- Missing files: {', '.join(level_data['files_missing'])}")
        
        return '\n'.join(lines)
    
    def generate_training_report(
        self,
        training_data: Dict[str, Any],
        format: ReportFormat = ReportFormat.MARKDOWN
    ) -> str:
        """Generate training system report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report_data = {
            "report_type": "training_system",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_interactions": training_data.get("total_interactions", 0),
                "processed": training_data.get("processed", 0),
                "success_rate": training_data.get("success_rate", 0),
                "average_quality_score": training_data.get("average_quality_score", 0)
            },
            "details": training_data
        }
        
        if format == ReportFormat.JSON:
            filepath = self.output_dir / f"training_report_{timestamp}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        elif format == ReportFormat.MARKDOWN:
            filepath = self.output_dir / f"training_report_{timestamp}.md"
            md_content = self._format_training_markdown(report_data)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
        
        return str(filepath)
    
    def _format_training_markdown(self, report_data: Dict[str, Any]) -> str:
        """Format training report as Markdown"""
        summary = report_data["summary"]
        
        lines = [
            "# Training System Report",
            f"\n**Generated**: {report_data['generated_at']}",
            f"\n## Summary",
            f"\n- **Total Interactions**: {summary['total_interactions']}",
            f"- **Processed**: {summary['processed']}",
            f"- **Success Rate**: {summary['success_rate']}%",
            f"- **Average Quality Score**: {summary['average_quality_score']:.2f}",
        ]
        
        return '\n'.join(lines)
    
    def generate_workflow_report(
        self,
        workflow_data: Dict[str, Any],
        format: ReportFormat = ReportFormat.MARKDOWN
    ) -> str:
        """Generate workflow execution report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report_data = {
            "report_type": "workflow_execution",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_workflows": workflow_data.get("total_executions", 0),
                "successful": workflow_data.get("successful", 0),
                "failed": workflow_data.get("failed", 0),
                "success_rate": workflow_data.get("success_rate", 0)
            },
            "details": workflow_data
        }
        
        if format == ReportFormat.JSON:
            filepath = self.output_dir / f"workflow_report_{timestamp}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        elif format == ReportFormat.MARKDOWN:
            filepath = self.output_dir / f"workflow_report_{timestamp}.md"
            md_content = self._format_workflow_markdown(report_data)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
        
        return str(filepath)
    
    def _format_workflow_markdown(self, report_data: Dict[str, Any]) -> str:
        """Format workflow report as Markdown"""
        summary = report_data["summary"]
        
        lines = [
            "# Workflow Execution Report",
            f"\n**Generated**: {report_data['generated_at']}",
            f"\n## Summary",
            f"\n- **Total Workflows**: {summary['total_workflows']}",
            f"- **Successful**: {summary['successful']}",
            f"- **Failed**: {summary['failed']}",
            f"- **Success Rate**: {summary['success_rate']}%",
        ]
        
        return '\n'.join(lines)
