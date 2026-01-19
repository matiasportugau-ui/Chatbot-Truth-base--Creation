"""
Metrics and monitoring utilities for AI Files Organizer Agent
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json


@dataclass
class OperationMetrics:
    """Metrics for a single operation"""

    operation_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    files_processed: int = 0
    files_successful: int = 0
    files_failed: int = 0
    duration_seconds: Optional[float] = None
    errors: List[str] = field(default_factory=list)

    def complete(self):
        """Mark operation as complete and calculate duration"""
        self.end_time = datetime.now()
        if self.start_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = delta.total_seconds()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "operation_type": self.operation_type,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "files_processed": self.files_processed,
            "files_successful": self.files_successful,
            "files_failed": self.files_failed,
            "duration_seconds": self.duration_seconds,
            "errors": self.errors,
        }


class MetricsCollector:
    """Collects and stores metrics for operations"""

    def __init__(self, metrics_file: Optional[Path] = None):
        """
        Initialize metrics collector.

        Args:
            metrics_file: Optional path to store metrics JSON file
        """
        self.metrics_file = metrics_file
        self.operations: List[OperationMetrics] = []
        self.total_files_organized = 0
        self.total_approvals_requested = 0
        self.total_approvals_granted = 0
        self.total_approvals_rejected = 0

    def start_operation(self, operation_type: str) -> OperationMetrics:
        """
        Start tracking an operation.

        Args:
            operation_type: Type of operation (e.g., "organize", "scan", "watch")

        Returns:
            OperationMetrics instance
        """
        metrics = OperationMetrics(
            operation_type=operation_type, start_time=datetime.now()
        )
        self.operations.append(metrics)
        return metrics

    def record_file_operation(
        self, metrics: OperationMetrics, success: bool, error: Optional[str] = None
    ):
        """
        Record a file operation result.

        Args:
            metrics: OperationMetrics instance
            success: Whether operation was successful
            error: Optional error message
        """
        metrics.files_processed += 1
        if success:
            metrics.files_successful += 1
            self.total_files_organized += 1
        else:
            metrics.files_failed += 1
            if error:
                metrics.errors.append(error)

    def record_approval(self, granted: bool):
        """Record an approval decision"""
        self.total_approvals_requested += 1
        if granted:
            self.total_approvals_granted += 1
        else:
            self.total_approvals_rejected += 1

    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        total_operations = len(self.operations)
        completed_operations = [
            op for op in self.operations if op.end_time is not None
        ]
        total_duration = sum(
            op.duration_seconds or 0 for op in completed_operations
        )

        return {
            "total_operations": total_operations,
            "completed_operations": len(completed_operations),
            "total_files_organized": self.total_files_organized,
            "total_approvals_requested": self.total_approvals_requested,
            "total_approvals_granted": self.total_approvals_granted,
            "total_approvals_rejected": self.total_approvals_rejected,
            "approval_rate": (
                self.total_approvals_granted / self.total_approvals_requested
                if self.total_approvals_requested > 0
                else 0.0
            ),
            "total_duration_seconds": total_duration,
            "average_duration_seconds": (
                total_duration / len(completed_operations)
                if completed_operations
                else 0.0
            ),
        }

    def save_metrics(self):
        """Save metrics to file"""
        if self.metrics_file:
            try:
                self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
                data = {
                    "statistics": self.get_statistics(),
                    "operations": [op.to_dict() for op in self.operations],
                }
                with open(self.metrics_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

    def load_metrics(self) -> Dict:
        """Load metrics from file"""
        if self.metrics_file and self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
