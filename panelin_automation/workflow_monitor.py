#!/usr/bin/env python3
"""
Workflow Monitor
================

Monitors workflow executions, tracks performance, and provides
alerting for failures and performance issues.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from collections import defaultdict


class WorkflowMonitor:
    """Monitors workflow execution and performance"""
    
    def __init__(self, log_path: Optional[str] = None):
        """
        Initialize workflow monitor
        
        Args:
            log_path: Path to workflow log file
        """
        if log_path is None:
            log_path = str(Path(__file__).parent / "workflow_monitor.log")
        
        self.log_path = log_path
        self.alerts: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, List[float]] = defaultdict(list)
    
    def log_execution(self, execution_result: Dict[str, Any]):
        """Log a workflow execution"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "execution_id": execution_result.get("execution_id"),
            "workflow_id": execution_result.get("workflow_id"),
            "status": execution_result.get("status"),
            "duration_seconds": execution_result.get("duration_seconds"),
            "steps_completed": execution_result.get("steps_completed"),
            "steps_total": execution_result.get("steps_total"),
            "errors": execution_result.get("errors", [])
        }
        
        # Write to log file
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        # Track performance metrics
        workflow_id = execution_result.get("workflow_id")
        duration = execution_result.get("duration_seconds", 0)
        if workflow_id and duration:
            self.performance_metrics[workflow_id].append(duration)
        
        # Check for issues
        self._check_for_issues(execution_result)
    
    def _check_for_issues(self, execution_result: Dict[str, Any]):
        """Check execution for issues and generate alerts"""
        workflow_id = execution_result.get("workflow_id")
        status = execution_result.get("status")
        duration = execution_result.get("duration_seconds", 0)
        errors = execution_result.get("errors", [])
        
        # Alert on failure
        if status == "failed":
            self.alerts.append({
                "level": "error",
                "timestamp": datetime.now().isoformat(),
                "workflow_id": workflow_id,
                "message": f"Workflow {workflow_id} failed",
                "details": errors
            })
        
        # Alert on slow execution
        if workflow_id in self.performance_metrics:
            avg_duration = sum(self.performance_metrics[workflow_id]) / len(self.performance_metrics[workflow_id])
            if duration > avg_duration * 2:  # 2x slower than average
                self.alerts.append({
                    "level": "warning",
                    "timestamp": datetime.now().isoformat(),
                    "workflow_id": workflow_id,
                    "message": f"Workflow {workflow_id} running slow",
                    "details": {
                        "duration": duration,
                        "average": avg_duration,
                        "slowdown_factor": round(duration / avg_duration, 2)
                    }
                })
        
        # Alert on partial completion
        steps_completed = execution_result.get("steps_completed", 0)
        steps_total = execution_result.get("steps_total", 0)
        if 0 < steps_completed < steps_total:
            self.alerts.append({
                "level": "warning",
                "timestamp": datetime.now().isoformat(),
                "workflow_id": workflow_id,
                "message": f"Workflow {workflow_id} partially completed",
                "details": {
                    "completed": steps_completed,
                    "total": steps_total,
                    "completion_rate": round(steps_completed / steps_total * 100, 1)
                }
            })
    
    def get_alerts(
        self,
        level: Optional[str] = None,
        since: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get alerts
        
        Args:
            level: Filter by level ("error", "warning", "info")
            since: Filter by timestamp (ISO format)
            limit: Maximum number of alerts to return
        
        Returns:
            List of alerts
        """
        filtered_alerts = self.alerts
        
        # Filter by level
        if level:
            filtered_alerts = [a for a in filtered_alerts if a["level"] == level]
        
        # Filter by timestamp
        if since:
            since_dt = datetime.fromisoformat(since)
            filtered_alerts = [
                a for a in filtered_alerts 
                if datetime.fromisoformat(a["timestamp"]) >= since_dt
            ]
        
        # Limit results
        return filtered_alerts[-limit:]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report for all workflows"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "workflows": {}
        }
        
        for workflow_id, durations in self.performance_metrics.items():
            if not durations:
                continue
            
            report["workflows"][workflow_id] = {
                "total_executions": len(durations),
                "average_duration_seconds": round(sum(durations) / len(durations), 2),
                "min_duration_seconds": round(min(durations), 2),
                "max_duration_seconds": round(max(durations), 2),
                "recent_trend": self._calculate_trend(durations[-10:]) if len(durations) >= 10 else "insufficient_data"
            }
        
        return report
    
    def _calculate_trend(self, durations: List[float]) -> str:
        """Calculate performance trend (improving/degrading/stable)"""
        if len(durations) < 2:
            return "insufficient_data"
        
        # Compare first half vs second half
        mid = len(durations) // 2
        first_half_avg = sum(durations[:mid]) / mid
        second_half_avg = sum(durations[mid:]) / (len(durations) - mid)
        
        change = (second_half_avg - first_half_avg) / first_half_avg
        
        if change < -0.1:  # 10% faster
            return "improving"
        elif change > 0.1:  # 10% slower
            return "degrading"
        else:
            return "stable"
    
    def clear_alerts(self, before: Optional[str] = None):
        """Clear alerts"""
        if before:
            before_dt = datetime.fromisoformat(before)
            self.alerts = [
                a for a in self.alerts 
                if datetime.fromisoformat(a["timestamp"]) >= before_dt
            ]
        else:
            self.alerts = []
    
    def export_metrics(self, filepath: str):
        """Export performance metrics to file"""
        metrics = {
            "exported_at": datetime.now().isoformat(),
            "performance": self.get_performance_report(),
            "alerts": self.get_alerts(limit=100),
            "raw_metrics": dict(self.performance_metrics)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
