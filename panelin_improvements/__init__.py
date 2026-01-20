"""
Panelin Improvements Package
============================

P0 Implementation modules for Panelin chatbot system improvements.
"""

from .source_of_truth_validator import (
    SourceOfTruthValidator,
    SourceValidationResult,
    validate_source_of_truth
)

from .logging_setup import (
    setup_logging,
    TraceContext,
    log_source_decision,
    log_formula_application,
    log_conflict_detected,
    log_guardrail_check,
    log_price_response,
    log_quotation_generated,
    log_error,
    log_api_call,
    set_trace_id,
    get_trace_id,
    set_user_id,
    get_user_id
)

from .conflict_detector import (
    ConflictDetector,
    Conflict
)

__version__ = "0.1.0"
__all__ = [
    # Source of Truth
    "SourceOfTruthValidator",
    "SourceValidationResult",
    "validate_source_of_truth",
    # Logging
    "setup_logging",
    "TraceContext",
    "log_source_decision",
    "log_formula_application",
    "log_conflict_detected",
    "log_guardrail_check",
    "log_price_response",
    "log_quotation_generated",
    "log_error",
    "log_api_call",
    "set_trace_id",
    "get_trace_id",
    "set_user_id",
    "get_user_id",
    # Conflict Detection
    "ConflictDetector",
    "Conflict",
]
