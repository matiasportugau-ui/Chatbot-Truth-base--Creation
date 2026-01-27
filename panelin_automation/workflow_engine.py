#!/usr/bin/env python3
"""
Workflow Engine
===============

Event-based workflow execution engine with support for complex
multi-step workflows, conditional logic, and error handling.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerType(Enum):
    """Workflow trigger types"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    WEBHOOK = "webhook"


@dataclass
class WorkflowStep:
    """Represents a single workflow step"""
    name: str
    function: Callable
    args: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 3
    retry_delay_seconds: int = 5
    timeout_seconds: int = 300
    on_error: str = "fail"  # "fail", "continue", "retry"
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None


@dataclass
class Workflow:
    """Represents a complete workflow"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    trigger_type: TriggerType = TriggerType.MANUAL
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowEngine:
    """Executes workflows with error handling and monitoring"""
    
    def __init__(self):
        """Initialize workflow engine"""
        self.workflows: Dict[str, Workflow] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
    
    def register_workflow(self, workflow: Workflow):
        """Register a workflow"""
        self.workflows[workflow.id] = workflow
    
    def execute_workflow(
        self,
        workflow_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow
        
        Args:
            workflow_id: Workflow identifier
            context: Execution context (shared across steps)
        
        Returns:
            Execution result with status and outputs
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {
                "status": "error",
                "error": f"Workflow {workflow_id} not found"
            }
        
        execution_id = f"{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        execution_result = {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "workflow_name": workflow.name,
            "status": WorkflowStatus.RUNNING.value,
            "start_time": start_time.isoformat(),
            "steps_completed": 0,
            "steps_total": len(workflow.steps),
            "step_results": [],
            "context": context or {},
            "errors": []
        }
        
        try:
            for i, step in enumerate(workflow.steps, 1):
                # Check condition if present
                if step.condition and not step.condition(execution_result["context"]):
                    execution_result["step_results"].append({
                        "step_name": step.name,
                        "status": "skipped",
                        "reason": "condition_not_met"
                    })
                    continue
                
                # Execute step with retry logic
                step_result = self._execute_step(step, execution_result["context"])
                execution_result["step_results"].append(step_result)
                
                if step_result["status"] == "failed":
                    if step.on_error == "fail":
                        execution_result["status"] = WorkflowStatus.FAILED.value
                        execution_result["errors"].append(f"Step {step.name} failed: {step_result.get('error')}")
                        break
                    elif step.on_error == "continue":
                        execution_result["errors"].append(f"Step {step.name} failed (continuing): {step_result.get('error')}")
                        continue
                else:
                    execution_result["steps_completed"] += 1
                    # Update context with step output
                    if "output" in step_result:
                        execution_result["context"][f"{step.name}_output"] = step_result["output"]
            
            # Mark as completed if no failures
            if execution_result["status"] == WorkflowStatus.RUNNING.value:
                execution_result["status"] = WorkflowStatus.COMPLETED.value
        
        except Exception as e:
            execution_result["status"] = WorkflowStatus.FAILED.value
            execution_result["errors"].append(f"Workflow execution error: {str(e)}")
        
        # Finalize execution record
        end_time = datetime.now()
        execution_result["end_time"] = end_time.isoformat()
        execution_result["duration_seconds"] = (end_time - start_time).total_seconds()
        
        # Store in history
        self.execution_history.append(execution_result)
        
        return execution_result
    
    def _execute_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single workflow step with retry logic"""
        step_start = datetime.now()
        
        for attempt in range(step.retry_count):
            try:
                # Execute step function
                result = step.function(**step.args, context=context)
                
                return {
                    "step_name": step.name,
                    "status": "completed",
                    "output": result,
                    "attempts": attempt + 1,
                    "duration_seconds": (datetime.now() - step_start).total_seconds()
                }
            
            except Exception as e:
                if attempt < step.retry_count - 1 and step.on_error == "retry":
                    time.sleep(step.retry_delay_seconds)
                    continue
                else:
                    return {
                        "step_name": step.name,
                        "status": "failed",
                        "error": str(e),
                        "attempts": attempt + 1,
                        "duration_seconds": (datetime.now() - step_start).total_seconds()
                    }
        
        return {
            "step_name": step.name,
            "status": "failed",
            "error": "Max retries exceeded",
            "attempts": step.retry_count
        }
    
    def register_event_handler(self, event_name: str, handler: Callable):
        """Register an event handler"""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
    
    def trigger_event(self, event_name: str, event_data: Dict[str, Any]):
        """Trigger an event and execute registered handlers"""
        handlers = self.event_handlers.get(event_name, [])
        
        results = []
        for handler in handlers:
            try:
                result = handler(event_data)
                results.append({"handler": handler.__name__, "status": "success", "result": result})
            except Exception as e:
                results.append({"handler": handler.__name__, "status": "failed", "error": str(e)})
        
        return {
            "event": event_name,
            "timestamp": datetime.now().isoformat(),
            "handlers_executed": len(results),
            "results": results
        }
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow executions"""
        return self.execution_history[-limit:]
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow execution statistics"""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
                "average_duration_seconds": 0
            }
        
        total = len(self.execution_history)
        successful = sum(1 for ex in self.execution_history if ex["status"] == WorkflowStatus.COMPLETED.value)
        failed = sum(1 for ex in self.execution_history if ex["status"] == WorkflowStatus.FAILED.value)
        
        durations = [ex.get("duration_seconds", 0) for ex in self.execution_history if "duration_seconds" in ex]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / total * 100, 2) if total > 0 else 0,
            "average_duration_seconds": round(avg_duration, 2),
            "registered_workflows": len(self.workflows)
        }
