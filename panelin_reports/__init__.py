"""
Panelin Reports Module
======================

Automated report generation, scheduling, and distribution system.

Modules:
- report_generator: Core report generation logic
- report_templates: Report templates (JSON, Markdown, PDF)
- report_scheduler: Scheduled report generation
- report_distributor: Email and file distribution
"""

from .report_generator import ReportGenerator
from .report_templates import ReportTemplate, TemplateType
from .report_scheduler import ReportScheduler
from .report_distributor import ReportDistributor

__all__ = [
    "ReportGenerator",
    "ReportTemplate",
    "TemplateType",
    "ReportScheduler",
    "ReportDistributor",
]

__version__ = "1.0.0"
