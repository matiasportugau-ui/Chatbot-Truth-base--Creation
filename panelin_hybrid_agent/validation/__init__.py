"""
Validation Module
=================

Comprehensive validation for quotations and KB integrity.
Ensures 100% calculation accuracy through deterministic verification.
"""

from .validators import (
    validate_quotation,
    validate_kb_integrity,
    validate_tool_result,
    ValidationResult,
)
from .monitoring import (
    QuotationMonitor,
    log_quotation_event,
    get_metrics_summary,
)

__all__ = [
    "validate_quotation",
    "validate_kb_integrity",
    "validate_tool_result",
    "ValidationResult",
    "QuotationMonitor",
    "log_quotation_event",
    "get_metrics_summary",
]
