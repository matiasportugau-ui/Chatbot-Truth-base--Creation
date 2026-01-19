"""
Tests for MetricsCollector
"""

from datetime import datetime
import tempfile
from pathlib import Path

import pytest

from ai_files_organizer.utils.metrics import MetricsCollector, OperationMetrics


def test_metrics_collector_initialization():
    """Test metrics collector initialization"""
    collector = MetricsCollector()
    assert collector.operations == []
    assert collector.total_files_organized == 0


def test_start_operation():
    """Test starting an operation"""
    collector = MetricsCollector()
    metrics = collector.start_operation("organize")
    
    assert metrics.operation_type == "organize"
    assert metrics.start_time is not None
    assert metrics.end_time is None


def test_record_file_operation():
    """Test recording file operations"""
    collector = MetricsCollector()
    metrics = collector.start_operation("organize")
    
    collector.record_file_operation(metrics, True)
    assert metrics.files_successful == 1
    assert metrics.files_processed == 1
    
    collector.record_file_operation(metrics, False, "Error message")
    assert metrics.files_failed == 1
    assert len(metrics.errors) == 1


def test_record_approval():
    """Test recording approvals"""
    collector = MetricsCollector()
    
    collector.record_approval(True)
    assert collector.total_approvals_granted == 1
    
    collector.record_approval(False)
    assert collector.total_approvals_rejected == 1


def test_get_statistics():
    """Test getting statistics"""
    collector = MetricsCollector()
    metrics = collector.start_operation("organize")
    collector.record_file_operation(metrics, True)
    metrics.complete()
    
    stats = collector.get_statistics()
    assert stats["total_operations"] == 1
    assert stats["total_files_organized"] == 1


def test_save_and_load_metrics():
    """Test saving and loading metrics"""
    with tempfile.TemporaryDirectory() as tmpdir:
        metrics_file = Path(tmpdir) / "metrics.json"
        collector = MetricsCollector(metrics_file=metrics_file)
        
        metrics = collector.start_operation("organize")
        collector.record_file_operation(metrics, True)
        metrics.complete()
        
        collector.save_metrics()
        assert metrics_file.exists()
        
        loaded = collector.load_metrics()
        assert "statistics" in loaded
