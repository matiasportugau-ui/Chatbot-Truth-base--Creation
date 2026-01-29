"""
Monitoring and Observability
============================

Tracks quotation events, errors, and performance metrics.
Designed for integration with LangSmith, Langfuse, or custom logging.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("panelin.monitoring")

# Metrics storage (in production, use proper metrics system)
METRICS_PATH = Path(__file__).parent.parent / "logs" / "metrics.json"


@dataclass
class QuotationEvent:
    """Represents a quotation event for logging"""
    event_type: str  # "request", "tool_call", "response", "error"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    user_message: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None
    response: Optional[str] = None
    error: Optional[str] = None
    latency_ms: Optional[float] = None
    calculation_verified: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "user_message": self.user_message,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "tool_result": self.tool_result,
            "response": self.response,
            "error": self.error,
            "latency_ms": self.latency_ms,
            "calculation_verified": self.calculation_verified,
        }


@dataclass
class QuotationMonitor:
    """
    Monitors quotation operations for observability.
    
    Tracks:
    - Request/response events
    - Tool call usage
    - Errors and their types
    - Latency metrics
    - calculation_verified status (critical)
    """
    
    events: List[QuotationEvent] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=lambda: defaultdict(int))
    
    def log_request(self, user_message: str) -> None:
        """Log an incoming request"""
        event = QuotationEvent(
            event_type="request",
            user_message=user_message,
        )
        self.events.append(event)
        self.metrics["total_requests"] += 1
        logger.info(f"Request received: {user_message[:100]}...")
    
    def log_tool_call(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        tool_result: Dict[str, Any],
        latency_ms: float,
    ) -> None:
        """Log a tool call and its result"""
        calculation_verified = tool_result.get("calculation_verified", False)
        
        event = QuotationEvent(
            event_type="tool_call",
            tool_name=tool_name,
            tool_args=tool_args,
            tool_result=tool_result,
            latency_ms=latency_ms,
            calculation_verified=calculation_verified,
        )
        self.events.append(event)
        
        self.metrics["total_tool_calls"] += 1
        self.metrics[f"tool_calls_{tool_name}"] += 1
        
        if not calculation_verified:
            # CRITICAL: This should never happen
            self.metrics["calculation_not_verified"] += 1
            logger.critical(
                f"CALCULATION_NOT_VERIFIED: {tool_name} returned without verification!"
            )
        
        logger.info(f"Tool call: {tool_name} ({latency_ms:.2f}ms)")
    
    def log_response(self, response: str, total_latency_ms: float) -> None:
        """Log the final response"""
        event = QuotationEvent(
            event_type="response",
            response=response[:500],  # Truncate for storage
            latency_ms=total_latency_ms,
        )
        self.events.append(event)
        
        self.metrics["total_responses"] += 1
        self.metrics["total_latency_ms"] += total_latency_ms
        
        logger.info(f"Response sent ({total_latency_ms:.2f}ms)")
    
    def log_error(self, error: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log an error"""
        event = QuotationEvent(
            event_type="error",
            error=error,
            tool_args=context,
        )
        self.events.append(event)
        
        self.metrics["total_errors"] += 1
        logger.error(f"Error: {error}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        total_requests = self.metrics.get("total_requests", 0)
        total_latency = self.metrics.get("total_latency_ms", 0)
        
        return {
            "total_requests": total_requests,
            "total_responses": self.metrics.get("total_responses", 0),
            "total_tool_calls": self.metrics.get("total_tool_calls", 0),
            "total_errors": self.metrics.get("total_errors", 0),
            "calculation_not_verified": self.metrics.get("calculation_not_verified", 0),
            "average_latency_ms": total_latency / total_requests if total_requests > 0 else 0,
            "tool_usage": {
                k: v for k, v in self.metrics.items() if k.startswith("tool_calls_")
            },
        }
    
    def check_health(self) -> Dict[str, Any]:
        """Check monitoring health and critical metrics"""
        summary = self.get_summary()
        
        health = {
            "status": "healthy",
            "alerts": [],
        }
        
        # CRITICAL: Check for non-verified calculations
        if summary["calculation_not_verified"] > 0:
            health["status"] = "critical"
            health["alerts"].append({
                "level": "critical",
                "message": f"LLM calculated directly {summary['calculation_not_verified']} times!",
                "metric": "calculation_not_verified",
            })
        
        # Check error rate
        if summary["total_requests"] > 0:
            error_rate = summary["total_errors"] / summary["total_requests"]
            if error_rate > 0.1:
                health["status"] = "warning" if health["status"] == "healthy" else health["status"]
                health["alerts"].append({
                    "level": "warning",
                    "message": f"High error rate: {error_rate:.1%}",
                    "metric": "error_rate",
                })
        
        # Check latency
        if summary["average_latency_ms"] > 3000:
            health["status"] = "warning" if health["status"] == "healthy" else health["status"]
            health["alerts"].append({
                "level": "warning",
                "message": f"High latency: {summary['average_latency_ms']:.0f}ms",
                "metric": "latency",
            })
        
        return health


# Global monitor instance
_monitor: Optional[QuotationMonitor] = None


def get_monitor() -> QuotationMonitor:
    """Get or create the global monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = QuotationMonitor()
    return _monitor


def log_quotation_event(
    event_type: str,
    **kwargs,
) -> None:
    """
    Log a quotation event to the global monitor.
    
    Args:
        event_type: Type of event (request, tool_call, response, error)
        **kwargs: Event-specific parameters
    """
    monitor = get_monitor()
    
    if event_type == "request":
        monitor.log_request(kwargs.get("user_message", ""))
    elif event_type == "tool_call":
        monitor.log_tool_call(
            tool_name=kwargs.get("tool_name", ""),
            tool_args=kwargs.get("tool_args", {}),
            tool_result=kwargs.get("tool_result", {}),
            latency_ms=kwargs.get("latency_ms", 0),
        )
    elif event_type == "response":
        monitor.log_response(
            response=kwargs.get("response", ""),
            total_latency_ms=kwargs.get("latency_ms", 0),
        )
    elif event_type == "error":
        monitor.log_error(
            error=kwargs.get("error", ""),
            context=kwargs.get("context"),
        )


def get_metrics_summary() -> Dict[str, Any]:
    """Get current metrics summary from global monitor"""
    return get_monitor().get_summary()


def check_monitoring_health() -> Dict[str, Any]:
    """Check health of the monitoring system"""
    return get_monitor().check_health()


def export_events_to_json(filepath: Optional[Path] = None) -> str:
    """Export all events to JSON file"""
    monitor = get_monitor()
    filepath = filepath or METRICS_PATH
    
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "summary": monitor.get_summary(),
        "health": monitor.check_health(),
        "events": [e.to_dict() for e in monitor.events],
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return str(filepath)
