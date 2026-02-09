"""
Panelin Reports Module
======================

Automated report generation, scheduling, and distribution system.

Modules:
- report_generator: Core report generation logic
- report_templates: Report templates (JSON, Markdown, PDF)
- report_scheduler: Scheduled report generation
- report_distributor: Email and file distribution
- pdf_generator: BMC Uruguay quotation PDF generation
- pdf_styles: PDF styling and branding configuration
"""

from .report_generator import ReportGenerator
from .report_templates import ReportTemplate, TemplateType
from .report_scheduler import ReportScheduler
from .report_distributor import ReportDistributor
from .pdf_generator import (
    BMCQuotationPDF,
    QuotationDataFormatter,
    generate_quotation_pdf,
    build_quote_pdf,
)
from .pdf_styles import BMCStyles, QuotationConstants

__all__ = [
    "ReportGenerator",
    "ReportTemplate",
    "TemplateType",
    "ReportScheduler",
    "ReportDistributor",
    "BMCQuotationPDF",
    "QuotationDataFormatter",
    "generate_quotation_pdf",
    "build_quote_pdf",
    "BMCStyles",
    "QuotationConstants",
]

__version__ = "1.1.0"
