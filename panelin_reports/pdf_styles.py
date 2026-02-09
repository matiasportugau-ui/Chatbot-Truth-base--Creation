#!/usr/bin/env python3
"""
PDF Styles Configuration
=========================

Centralized style definitions for BMC Uruguay quotation PDFs.
Ensures consistent branding and layout across all generated documents.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import TableStyle


class BMCStyles:
    """BMC Uruguay PDF styling constants and configurations."""

    # Page layout (A4 mandatory)
    PAGE_SIZE = A4
    PAGE_WIDTH = A4[0]
    PAGE_HEIGHT = A4[1]

    # Margins (target: ~12mm sides, ~10mm top, ~8-10mm bottom)
    MARGIN_TOP = 10 * mm
    MARGIN_BOTTOM = 9 * mm
    MARGIN_LEFT = 12 * mm
    MARGIN_RIGHT = 12 * mm

    # Brand colors
    BMC_BLUE = colors.HexColor("#003366")
    BMC_LIGHT_BLUE = colors.HexColor("#0066CC")
    TEXT_BLACK = colors.black
    TEXT_GRAY = colors.HexColor("#555555")
    ALERT_RED = colors.HexColor("#C62828")

    # Table colors (requested template)
    TABLE_HEADER_BG = colors.HexColor("#EDEDED")
    TABLE_ALT_BG = colors.HexColor("#FAFAFA")
    TABLE_BORDER = colors.HexColor("#D2D2D2")
    HIGHLIGHT_YELLOW = colors.HexColor("#FFF9E6")

    # Fonts
    FONT_NAME = "Helvetica"
    FONT_NAME_BOLD = "Helvetica-Bold"

    FONT_SIZE_TITLE = 13.4
    FONT_SIZE_SECTION = 9.6
    FONT_SIZE_NORMAL = 9.0
    FONT_SIZE_SMALL = 8.4

    # Materials table sizes (requested template)
    FONT_SIZE_TABLE_HEADER = 9.1
    FONT_SIZE_TABLE_ROW = 8.6

    # Comments "1-page-first" tuning knobs
    COMMENT_FONT_SIZE_BASE = 8.2
    COMMENT_LEADING_BASE = 9.5
    COMMENT_FONT_SIZE_MIN = 7.2
    COMMENT_LEADING_MIN = 8.2
    COMMENT_STEP = 0.2

    # Logo (official path for this template)
    LOGO_PATH = "/mnt/data/Logo_BMC- PNG.png"
    LOGO_HEIGHT = 18 * mm

    @classmethod
    def get_title_style(cls):
        """Centered style for main quotation title in header."""
        return ParagraphStyle(
            "BMCTitle",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=cls.FONT_SIZE_TITLE,
            textColor=cls.TEXT_BLACK,
            alignment=1,  # centered
            leading=14.6,
            spaceAfter=0,
            spaceBefore=0,
        )

    @classmethod
    def get_header_style(cls):
        """Style for compact section titles."""
        return ParagraphStyle(
            "BMCSectionHeader",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=cls.FONT_SIZE_SECTION,
            textColor=cls.TEXT_BLACK,
            spaceAfter=2,
            spaceBefore=3,
        )

    @classmethod
    def get_normal_style(cls):
        """Style for compact body text."""
        return ParagraphStyle(
            "BMCNormal",
            fontName=cls.FONT_NAME,
            fontSize=cls.FONT_SIZE_NORMAL,
            textColor=cls.TEXT_BLACK,
            leading=10.2,
            spaceAfter=1.5,
        )

    @classmethod
    def get_small_style(cls):
        """Style for small text blocks."""
        return ParagraphStyle(
            "BMCSmall",
            fontName=cls.FONT_NAME,
            fontSize=cls.FONT_SIZE_SMALL,
            textColor=cls.TEXT_GRAY,
            leading=9.6,
            spaceAfter=1.5,
        )

    @classmethod
    def get_comment_style(
        cls, font_size: float = None, leading: float = None
    ) -> ParagraphStyle:
        """Style used for comments list, shrinkable to fit one page."""
        effective_size = (
            cls.COMMENT_FONT_SIZE_BASE if font_size is None else float(font_size)
        )
        effective_leading = (
            cls.COMMENT_LEADING_BASE if leading is None else float(leading)
        )
        return ParagraphStyle(
            "BMCComments",
            fontName=cls.FONT_NAME,
            fontSize=effective_size,
            textColor=cls.TEXT_BLACK,
            leading=effective_leading,
            leftIndent=8,
            firstLineIndent=0,
            bulletIndent=0,
            spaceAfter=1.2,
        )

    @classmethod
    def get_products_table_style(cls):
        """Default style for materials tables."""
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), cls.TABLE_HEADER_BG),
                ("FONTNAME", (0, 0), (-1, 0), cls.FONT_NAME_BOLD),
                ("FONTSIZE", (0, 0), (-1, 0), cls.FONT_SIZE_TABLE_HEADER),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 1), (-1, -1), cls.FONT_NAME),
                ("FONTSIZE", (0, 1), (-1, -1), cls.FONT_SIZE_TABLE_ROW),
                ("GRID", (0, 0), (-1, -1), 0.35, cls.TABLE_BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )

    @classmethod
    def get_totals_table_style(cls):
        """Table style for totals section."""
        return TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), cls.FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), cls.FONT_SIZE_SMALL),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, -1), (-1, -1), cls.FONT_NAME_BOLD),
                ("FONTSIZE", (0, -1), (-1, -1), cls.FONT_SIZE_NORMAL),
                ("TEXTCOLOR", (0, -1), (-1, -1), cls.BMC_BLUE),
                ("BACKGROUND", (0, -1), (-1, -1), cls.HIGHLIGHT_YELLOW),
                ("LINEABOVE", (0, 0), (-1, 0), 0.5, cls.TABLE_BORDER),
                ("LINEABOVE", (0, -1), (-1, -1), 1, cls.BMC_BLUE),
                ("TOPPADDING", (0, 0), (-1, -1), 2.2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]
        )

    @classmethod
    def get_transfer_table_style(cls):
        """Style for transfer footer boxed block."""
        return TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), cls.FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), cls.FONT_SIZE_SMALL),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.5, cls.TABLE_BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, cls.TABLE_BORDER),
                ("BACKGROUND", (0, 0), (-1, 0), cls.TABLE_HEADER_BG),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ]
        )

    @classmethod
    def get_conditions_style(cls):
        """Backward-compatible style for legacy conditions blocks."""
        return cls.get_comment_style()


class QuotationConstants:
    """Business constants for BMC Uruguay quotations."""

    # Tax rates
    IVA_RATE = 0.22  # 22% IVA for Uruguay 2026

    # Default values
    DEFAULT_SHIPPING_USD = 280.0
    DEFAULT_LOCATION = "Maldonado, Uy."

    # Company information
    COMPANY_NAME = "BMC Uruguay"
    COMPANY_EMAIL = "info@bmcuruguay.com.uy"
    COMPANY_WEBSITE = "www.bmcuruguay.com.uy"
    COMPANY_PHONE = "42224031"
    CONTACT_PHONE = "092 663 245"

    # Banking information
    BANK_NAME = "BROU"
    BANK_ACCOUNT_TYPE = "Caja de Ahorro"
    BANK_ACCOUNT_HOLDER = "Metalog SAS"
    BANK_RUT = "120403430012"
    BANK_ACCOUNT_USD = "110520638-00002"

    # Technical specifications
    PANEL_WIDTH_FACADE = 1.14  # meters
    PANEL_WIDTH_ROOF = 1.12  # meters
    MIN_SLOPE_PERCENTAGE = 7.0  # 7% minimum slope

    # Production & delivery
    PRODUCTION_DAYS_MIN = 10
    PRODUCTION_DAYS_MAX = 15
    QUOTE_VALIDITY_DAYS = 10

    # YouTube video
    SPM_SYSTEM_VIDEO = "https://youtu.be/Am4mZskFMgc"

    # Terms & Conditions link
    TERMS_CONDITIONS_URL = "https://bmcuruguay.com.uy/terminos-y-condiciones"

    @classmethod
    def get_standard_conditions(cls):
        """Returns list of standard quotation conditions."""
        return [
            f"*Ancho útil paneles de Fachada = {cls.PANEL_WIDTH_FACADE} m de Cubierta = {cls.PANEL_WIDTH_ROOF} m. Pendiente mínima {cls.MIN_SLOPE_PERCENTAGE}%.",
            cls.SPM_SYSTEM_VIDEO,
            "Entrega de 10 a 15 días, dependemos de producción.",
            "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).",
            "Oferta válida por 10 días a partir de la fecha.",
        ]

    @classmethod
    def get_default_comments(cls):
        """Default comments block for the formal PDF template."""
        return [
            f"Ancho útil paneles de Fachada = {cls.PANEL_WIDTH_FACADE} m de Cubierta = {cls.PANEL_WIDTH_ROOF} m. Pendiente mínima {cls.MIN_SLOPE_PERCENTAGE}%.",
            cls.SPM_SYSTEM_VIDEO,
            "Entrega de 10 a 15 días, dependemos de producción.",
            "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).",
            "Oferta válida por 10 días a partir de la fecha.",
        ]
