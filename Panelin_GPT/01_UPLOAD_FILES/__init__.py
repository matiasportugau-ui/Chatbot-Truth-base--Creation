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

# PDF generation (always available)
from .pdf_generator import BMCQuotationPDF, QuotationDataFormatter, generate_quotation_pdf
from .pdf_styles import BMCStyles, QuotationConstants

__all__ = [
    "BMCQuotationPDF",
    "QuotationDataFormatter",
    "generate_quotation_pdf",
    "BMCStyles",
    "QuotationConstants",
]

# Optional imports (require additional dependencies)
try:
    from .report_generator import ReportGenerator
    from .report_templates import ReportTemplate, TemplateType
    __all__.extend(["ReportGenerator", "ReportTemplate", "TemplateType"])
except ImportError:
    pass

try:
    from .report_scheduler import ReportScheduler
    __all__.append("ReportScheduler")
except ImportError:
    pass

try:
    from .report_distributor import ReportDistributor
    __all__.append("ReportDistributor")
except ImportError:
    pass

__version__ = "1.1.0"
