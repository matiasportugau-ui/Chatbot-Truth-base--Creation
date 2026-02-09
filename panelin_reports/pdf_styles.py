#!/usr/bin/env python3
"""
PDF Styles Configuration
=========================

Centralized style definitions for BMC Uruguay quotation PDFs.
Ensures consistent branding and layout across all generated documents.
"""

import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import TableStyle


class BMCStyles:
    """BMC Uruguay PDF styling constants and configurations."""

    # Page Layout (A4 required)
    PAGE_SIZE = A4
    PAGE_WIDTH = A4[0]
    PAGE_HEIGHT = A4[1]

    # Margins (requested approx: 12mm LR, 10mm top, 8-10mm bottom)
    MARGIN_TOP = 10 * mm
    MARGIN_BOTTOM = 9 * mm
    MARGIN_LEFT = 12 * mm
    MARGIN_RIGHT = 12 * mm

    # Colors
    BMC_BLUE = colors.HexColor("#003366")
    LINK_BLUE = colors.HexColor("#1E4FA5")
    TABLE_HEADER_BG = colors.HexColor("#EDEDED")
    TABLE_ALT_ROW_BG = colors.HexColor("#FAFAFA")
    TABLE_BORDER = colors.HexColor("#CFCFCF")
    TEXT_BLACK = colors.black
    TEXT_GRAY = colors.HexColor("#4D4D4D")
    EMPHASIS_RED = colors.HexColor("#C62828")
    HIGHLIGHT_YELLOW = colors.HexColor("#FFF9E6")

    # Fonts
    FONT_NAME = "Helvetica"
    FONT_NAME_BOLD = "Helvetica-Bold"

    # Typography scale
    FONT_SIZE_TITLE = 13.2
    FONT_SIZE_SECTION = 9.4
    FONT_SIZE_NORMAL = 8.8
    FONT_SIZE_TABLE_HEADER = 9.1
    FONT_SIZE_TABLE_BODY = 8.6
    FONT_SIZE_COMMENTS = 8.2
    FONT_SIZE_FOOTER = 8.4
    COMMENTS_LEADING = 9.5

    # Logo
    PRIMARY_LOGO_PATH = "/mnt/data/Logo_BMC- PNG.png"
    FALLBACK_LOGO_PATHS = (
        "panelin_reports/assets/bmc_logo.png",
        "bmc_logo.png",
    )
    LOGO_HEIGHT = 18 * mm

    @classmethod
    def resolve_logo_path(cls, preferred_path=None):
        """
        Resolve logo path, prioritizing the official BMC logo.
        """
        candidates = [preferred_path, cls.PRIMARY_LOGO_PATH, *cls.FALLBACK_LOGO_PATHS]
        for candidate in candidates:
            if candidate and os.path.exists(candidate):
                return candidate
        return None

    @classmethod
    def get_header_title_style(cls):
        """Centered title beside the logo in the header."""
        return ParagraphStyle(
            "BMCTitleHeader",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=cls.FONT_SIZE_TITLE,
            textColor=cls.BMC_BLUE,
            alignment=1,  # Center
            leading=15,
            spaceAfter=0,
            spaceBefore=0,
        )

    @classmethod
    def get_section_label_style(cls):
        """Style for section labels like COMENTARIOS."""
        return ParagraphStyle(
            "BMCSectionLabel",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=cls.FONT_SIZE_SECTION,
            textColor=cls.TEXT_BLACK,
            leading=11,
            spaceAfter=2,
            spaceBefore=0,
        )

    @classmethod
    def get_normal_style(cls):
        """Style for normal text."""
        return ParagraphStyle(
            "BMCNormal",
            fontName=cls.FONT_NAME,
            fontSize=cls.FONT_SIZE_NORMAL,
            textColor=cls.TEXT_BLACK,
            leading=10.4,
            spaceAfter=2,
        )

    @classmethod
    def get_small_style(cls):
        """Style for compact metadata text."""
        return ParagraphStyle(
            "BMCSmall",
            fontName=cls.FONT_NAME,
            fontSize=8.0,
            textColor=cls.TEXT_GRAY,
            leading=9.3,
            spaceAfter=1,
        )

    @classmethod
    def get_comment_style(cls, font_size=None, leading=None, bold=False, text_color=None):
        """Comment line style with dynamic size/leading for one-page fit strategy."""
        return ParagraphStyle(
            "BMCComment",
            fontName=cls.FONT_NAME_BOLD if bold else cls.FONT_NAME,
            fontSize=font_size or cls.FONT_SIZE_COMMENTS,
            textColor=text_color or cls.TEXT_BLACK,
            leading=leading or cls.COMMENTS_LEADING,
            leftIndent=0,
            spaceAfter=1,
            spaceBefore=0,
            wordWrap="CJK",
        )

    @classmethod
    def get_materials_table_style(cls, numeric_columns, total_rows):
        """
        Table style for materials tables.
        - Header gray
        - Thin grid
        - Alternating row backgrounds
        - Numeric columns right-aligned
        """
        commands = [
            ("BACKGROUND", (0, 0), (-1, 0), cls.TABLE_HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), cls.TEXT_BLACK),
            ("FONTNAME", (0, 0), (-1, 0), cls.FONT_NAME_BOLD),
            ("FONTSIZE", (0, 0), (-1, 0), cls.FONT_SIZE_TABLE_HEADER),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTNAME", (0, 1), (-1, -1), cls.FONT_NAME),
            ("FONTSIZE", (0, 1), (-1, -1), cls.FONT_SIZE_TABLE_BODY),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.35, cls.TABLE_BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]

        for row_idx in range(1, total_rows):
            row_color = colors.white if row_idx % 2 == 1 else cls.TABLE_ALT_ROW_BG
            commands.append(("BACKGROUND", (0, row_idx), (-1, row_idx), row_color))

        for col_idx in numeric_columns:
            commands.append(("ALIGN", (col_idx, 1), (col_idx, -1), "RIGHT"))

        return TableStyle(commands)

    @classmethod
    def get_totals_table_style(cls):
        """Compact totals table style."""
        return TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), cls.FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), cls.FONT_SIZE_NORMAL),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, -1), (-1, -1), cls.FONT_NAME_BOLD),
                ("FONTSIZE", (0, -1), (-1, -1), cls.FONT_SIZE_SECTION),
                ("BACKGROUND", (0, -1), (-1, -1), cls.HIGHLIGHT_YELLOW),
                ("LINEABOVE", (0, 0), (-1, 0), 0.4, cls.TABLE_BORDER),
                ("LINEABOVE", (0, -1), (-1, -1), 0.7, cls.TABLE_BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )

    @classmethod
    def get_transfer_footer_table_style(cls):
        """Transfer footer box style with ruled rows and gray first row."""
        return TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, cls.TABLE_BORDER),
                ("BACKGROUND", (0, 0), (-1, 0), cls.TABLE_HEADER_BG),
                ("FONTNAME", (0, 0), (-1, -1), cls.FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), cls.FONT_SIZE_FOOTER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )

    @classmethod
    def get_conditions_style(cls):
        """Backward-compatible style for legacy conditions rendering."""
        return ParagraphStyle(
            "BMCConditions",
            fontName=cls.FONT_NAME,
            fontSize=8.0,
            textColor=cls.TEXT_GRAY,
            leftIndent=10,
            spaceAfter=2,
            leading=9.4,
        )


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
        """Returns standard comments for the quotation PDF."""
        return [
            f"Ancho útil paneles de Fachada = {cls.PANEL_WIDTH_FACADE} m; Cubierta = {cls.PANEL_WIDTH_ROOF} m. Pendiente mínima {cls.MIN_SLOPE_PERCENTAGE}%.",
            cls.SPM_SYSTEM_VIDEO,
            "Entrega de 10 a 15 días, dependemos de producción.",
            "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).",
            "Con tarjeta de crédito y en cuotas, sería en $ y a través de Mercado Pago con un recargo de 11,9% (comisión MP).",
            "Retiro sin cargo en Planta Industrial de Bromyros S.A. (Colonia Nicolich / CANELONES).",
            "BMC no asume responsabilidad por fallas producidas por no respetar la autoportancia sugerida.",
            "No incluye descarga del material. Se requieren 2 personas.",
            "Oferta válida por 10 días a partir de la fecha.",
            "Opcional: Costo descarga $1500 + IVA / H. Únicamente en ciudad de Maldonado.",
            "Nuestro asesoramiento es una guía y no sustituye el trabajo profesional de Arq. o Ing.",
            "Al recibir el material corroborar el estado del mismo. Una vez recibido, no aceptamos devolución.",
        ]
