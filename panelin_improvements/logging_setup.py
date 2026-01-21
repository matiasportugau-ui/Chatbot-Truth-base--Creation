"""
Logging Setup for Panelin
=========================

Structured logging configuration with trace IDs and event tracking.
Part of P0.3: Detailed Logging for Debugging
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextvars import ContextVar
from datetime import datetime
from loguru import logger

# Context variable for trace ID
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


def setup_logging(
    log_dir: str = "logs",
    log_level: str = "INFO",
    json_format: bool = True,
    rotation: str = "100 MB",
    retention: str = "30 days"
):
    """
    Set up structured logging for Panelin
    
    Args:
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        json_format: Use JSON format for structured logging
        rotation: Log rotation size
        retention: Log retention period
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with colors
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Add file handler with JSON format
    if json_format:
        logger.add(
            log_path / "panelin_{time:YYYY-MM-DD}.json",
            format="{time} | {level} | {message}",
            serialize=True,  # JSON format
            rotation=rotation,
            retention=retention,
            level=log_level,
            encoding="utf-8"
        )
    else:
        logger.add(
            log_path / "panelin_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} | {message}",
            rotation=rotation,
            retention=retention,
            level=log_level,
            encoding="utf-8"
        )
    
    logger.info("Logging system initialized", extra={
        "log_dir": str(log_path),
        "log_level": log_level,
        "json_format": json_format
    })


def set_trace_id(trace_id: str):
    """Set trace ID for current context"""
    trace_id_var.set(trace_id)


def get_trace_id() -> Optional[str]:
    """Get current trace ID"""
    return trace_id_var.get()


def set_user_id(user_id: str):
    """Set user ID for current context"""
    user_id_var.set(user_id)


def get_user_id() -> Optional[str]:
    """Get current user ID"""
    return user_id_var.get()


def _get_context() -> Dict[str, Any]:
    """Get logging context (trace ID, user ID, etc.)"""
    context = {}
    trace_id = get_trace_id()
    if trace_id:
        context["trace_id"] = trace_id
    user_id = get_user_id()
    if user_id:
        context["user_id"] = user_id
    return context


def log_source_decision(
    source_level: int,
    source_file: str,
    product_id: Optional[str] = None,
    field: Optional[str] = None
):
    """Log source of truth decision"""
    context = _get_context()
    logger.info(
        "Source decision made",
        extra={
            **context,
            "event_type": "source_decision",
            "source_level": source_level,
            "source_file": source_file,
            "product_id": product_id,
            "field": field,
            "timestamp": datetime.now().isoformat()
        }
    )


def log_formula_application(
    formula_name: str,
    inputs: Dict[str, Any],
    output: Any,
    product_id: Optional[str] = None
):
    """Log formula application"""
    context = _get_context()
    logger.info(
        "Formula applied",
        extra={
            **context,
            "event_type": "formula_application",
            "formula": formula_name,
            "inputs": inputs,
            "output": output,
            "product_id": product_id,
            "timestamp": datetime.now().isoformat()
        }
    )


def log_conflict_detected(
    product_id: str,
    field: str,
    level_1_value: Any,
    level_2_value: Any,
    resolution: str
):
    """Log conflict detection"""
    context = _get_context()
    logger.warning(
        "Conflict detected",
        extra={
            **context,
            "event_type": "conflict_detection",
            "product_id": product_id,
            "field": field,
            "level_1_value": level_1_value,
            "level_2_value": level_2_value,
            "resolution": resolution,
            "timestamp": datetime.now().isoformat()
        }
    )


def log_guardrail_check(
    guardrail_name: str,
    passed: bool,
    details: Optional[Dict[str, Any]] = None
):
    """Log guardrail validation check"""
    context = _get_context()
    log_level = "info" if passed else "warning"
    logger.log(
        log_level.upper(),
        "Guardrail check",
        extra={
            **context,
            "event_type": "guardrail_check",
            "guardrail": guardrail_name,
            "passed": passed,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
    )


def log_price_response(
    product_id: str,
    price: float,
    source_file: str,
    source_level: int,
    currency: str = "USD"
):
    """Log price response"""
    context = _get_context()
    logger.info(
        "Price response generated",
        extra={
            **context,
            "event_type": "price_response",
            "product_id": product_id,
            "price": price,
            "currency": currency,
            "source_file": source_file,
            "source_level": source_level,
            "timestamp": datetime.now().isoformat()
        }
    )


def log_quotation_generated(
    quotation_id: Optional[str],
    product_id: str,
    total_amount: float,
    items_count: int,
    formulas_used: List[str]
):
    """Log quotation generation"""
    context = _get_context()
    logger.info(
        "Quotation generated",
        extra={
            **context,
            "event_type": "quotation_generated",
            "quotation_id": quotation_id,
            "product_id": product_id,
            "total_amount": total_amount,
            "items_count": items_count,
            "formulas_used": formulas_used,
            "timestamp": datetime.now().isoformat()
        }
    )


def log_error(
    error_type: str,
    error_message: str,
    error_details: Optional[Dict[str, Any]] = None,
    exception: Optional[Exception] = None
):
    """Log error with full context"""
    context = _get_context()
    logger.error(
        f"Error: {error_message}",
        extra={
            **context,
            "event_type": "error",
            "error_type": error_type,
            "error_message": error_message,
            "error_details": error_details or {},
            "exception_type": type(exception).__name__ if exception else None,
            "timestamp": datetime.now().isoformat()
        },
        exc_info=exception
    )


def log_api_call(
    api_name: str,
    endpoint: str,
    method: str,
    status_code: Optional[int] = None,
    duration_ms: Optional[float] = None
):
    """Log API call"""
    context = _get_context()
    logger.info(
        "API call",
        extra={
            **context,
            "event_type": "api_call",
            "api_name": api_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat()
        }
    )


class TraceContext:
    """Context manager for trace ID"""
    
    def __init__(self, trace_id: str, user_id: Optional[str] = None):
        self.trace_id = trace_id
        self.user_id = user_id
        self.old_trace_id = None
        self.old_user_id = None
    
    def __enter__(self):
        self.old_trace_id = get_trace_id()
        self.old_user_id = get_user_id()
        set_trace_id(self.trace_id)
        if self.user_id:
            set_user_id(self.user_id)
        logger.debug(f"Trace context started: {self.trace_id}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.old_trace_id:
            set_trace_id(self.old_trace_id)
        else:
            trace_id_var.set(None)
        if self.old_user_id:
            set_user_id(self.old_user_id)
        else:
            user_id_var.set(None)
        logger.debug(f"Trace context ended: {self.trace_id}")


if __name__ == "__main__":
    # Example usage
    import uuid
    
    # Setup logging
    setup_logging(log_dir="logs", log_level="INFO")
    
    # Create trace context
    trace_id = str(uuid.uuid4())
    with TraceContext(trace_id, user_id="test_user"):
        # Log various events
        log_source_decision(
            source_level=1,
            source_file="BMC_Base_Conocimiento_GPT.json",
            product_id="ISODEC_EPS_100",
            field="price"
        )
        
        log_formula_application(
            formula_name="calculate_paneles",
            inputs={"ancho_total": 10.5, "ancho_util": 1.12},
            output=10,
            product_id="ISODEC_EPS_100"
        )
        
        log_price_response(
            product_id="ISODEC_EPS_100",
            price=46.07,
            source_file="BMC_Base_Conocimiento_GPT.json",
            source_level=1
        )
        
        log_guardrail_check(
            guardrail_name="source_of_truth",
            passed=True,
            details={"source_level": 1}
        )
    
    print("Logging examples completed. Check logs/ directory for output.")
