"""
Panelin Automation Module
==========================

Provides workflow automation, event-based triggers, and monitoring
for the Panelin chatbot system.

Modules:
- workflow_engine: Workflow execution engine
- workflow_monitor: Workflow monitoring and error handling
"""

from .workflow_engine import WorkflowEngine, Workflow, WorkflowStep
from .workflow_monitor import WorkflowMonitor

__all__ = [
    "WorkflowEngine",
    "Workflow",
    "WorkflowStep",
    "WorkflowMonitor",
]

__version__ = "1.0.0"
