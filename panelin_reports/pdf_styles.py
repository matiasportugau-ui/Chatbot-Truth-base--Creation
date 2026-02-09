#!/usr/bin/env python3
"""
PDF Styles Configuration
=========================

Centralized style definitions for BMC Uruguay quotation PDFs.
Ensures consistent branding and layout across all generated documents.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
from reportlab.lib.units import mm
from reportlab.platypus import TableStyle


class BMCStyles:
    """BMC Uruguay PDF styling constants and configurations"""

    # Page Layout
    PAGE_SIZE = A4
    PAGE_WIDTH = A4[0]
    PAGE_HEIGHT = A4[1]

    # Margins (NEW: Tighter margins for 1-page fit)
    MARGIN_TOP = 10 * mm
    MARGIN_BOTTOM = 8 * mm
    MARGIN_LEFT = 12 * mm
    MARGIN_RIGHT = 12 * mm

    # Colors - BMC Uruguay Brand (NEW: Updated for template)
    BMC_BLUE = colors.HexColor("#003366")
    BMC_LIGHT_BLUE = colors.HexColor("#0066CC")
    TABLE_HEADER_BG = colors.HexColor("#EDEDED")  # Light gray for header
    TABLE_ALT_ROW_BG = colors.HexColor("#FAFAFA")  # Very light gray for alternating rows
    TABLE_BORDER = colors.HexColor("#CCCCCC")
    TEXT_BLACK = colors.black
    TEXT_GRAY = colors.HexColor("#666666")
    TEXT_RED = colors.HexColor("#CC0000")  # For special comment lines
    HIGHLIGHT_YELLOW = colors.HexColor("#FFF9E6")
    FOOTER_BOX_BG = colors.HexColor("#EDEDED")  # For bank transfer box header

    # Fonts (NEW: Adjusted for 1-page fit)
    FONT_NAME = "Helvetica"
    FONT_NAME_BOLD = "Helvetica-Bold"

    FONT_SIZE_TITLE = 14  # Centered title next to logo
    FONT_SIZE_SUBTITLE = 12
    FONT_SIZE_HEADER = 12
    FONT_SIZE_TABLE_HEADER = 9.2  # Table header
    FONT_SIZE_TABLE_ROW = 8.6  # Table data rows
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_SMALL = 9
    FONT_SIZE_COMMENTS = 8.1  # Base comment font (can be reduced dynamically)
    FONT_SIZE_TINY = 8

    # Logo (NEW: Official BMC logo path)
    LOGO_HEIGHT = 18 * mm  # Fixed height, width auto-scaled
    # Check multiple possible locations for the logo
    LOGO_PATH = (
        "/mnt/data/Logo_BMC- PNG.png"
        if os.path.exists("/mnt/data/Logo_BMC- PNG.png")
        else (
            "bmc_logo.png"
            if os.path.exists("bmc_logo.png")
            else "panelin_reports/assets/bmc_logo.png"
        )
    )
    
    # Comments section (NEW: For 1-page fitting)
    COMMENTS_FONT_BASE = 8.1
    COMMENTS_LEADING_BASE = 9.4
    COMMENTS_FONT_MIN = 7.5  # Minimum before it's unreadable
    COMMENTS_LEADING_MIN = 8.5

    @classmethod
    def get_title_style(cls):
        """Style for main quotation title"""
        return ParagraphStyle(
            "BMCTitle",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=cls.FONT_SIZE_TITLE,
            textColor=cls.BMC_BLUE,
            spaceAfter=12,
            alignment=0,  # Left aligned
        )

    @classmethod
    def get_header_style(cls):
        """Style for section headers"""
        return ParagraphStyle(
            "BMCHeader",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=cls.FONT_SIZE_HEADER,
            textColor=cls.BMC_BLUE,
            spaceAfter=6,
            spaceBefore=12,
        )

    @classmethod
    def get_normal_style(cls):
        """Style for normal text"""
        return ParagraphStyle(
            "BMCNormal",
            fontName=cls.FONT_NAME,
            fontSize=cls.FONT_SIZE_NORMAL,
            textColor=cls.TEXT_BLACK,
            spaceAfter=6,
        )

    @classmethod
    def get_small_style(cls):
        """Style for small text (conditions, notes)"""
        return ParagraphStyle(
            "BMCSmall",
            fontName=cls.FONT_NAME,
            fontSize=cls.FONT_SIZE_TINY,
            textColor=cls.TEXT_GRAY,
            spaceAfter=3,
            leading=10,
        )

    @classmethod
    def get_products_table_style(cls):
        """Table style for products section (NEW: With alternating rows and right-aligned numbers)"""
        return TableStyle(
            [
                # Header row
                ("BACKGROUND", (0, 0), (-1, 0), cls.TABLE_HEADER_BG),
                ("TEXTCOLOR", (0, 0), (-1, 0), cls.TEXT_BLACK),
                ("FONTNAME", (0, 0), (-1, 0), cls.FONT_NAME_BOLD),
                ("FONTSIZE", (0, 0), (-1, 0), cls.FONT_SIZE_TABLE_HEADER),
                ("ALIGN", (0, 0), (0, 0), "LEFT"),  # Product name left
                ("ALIGN", (1, 0), (-1, 0), "RIGHT"),  # Numbers right
                # Data rows
                ("FONTNAME", (0, 1), (-1, -1), cls.FONT_NAME),
                ("FONTSIZE", (0, 1), (-1, -1), cls.FONT_SIZE_TABLE_ROW),
                ("ALIGN", (0, 1), (0, -1), "LEFT"),  # Product name left-aligned
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),  # Numbers right-aligned
                # Borders (thin grid lines)
                ("GRID", (0, 0), (-1, -1), 0.5, cls.TABLE_BORDER),
                ("LINEBELOW", (0, 0), (-1, 0), 1, cls.TABLE_BORDER),
                # Padding (tighter for 1-page fit)
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                # Repeat header on multi-page (even though we target 1 page)
                ("REPEATROWS", (0, 0), (-1, 0)),
            ]
        )
    
    @classmethod
    def apply_alternating_row_colors(cls, table_style, num_rows):
        """Apply alternating row background colors to a table style"""
        # Start from row 1 (skip header row 0)
        for row_idx in range(1, num_rows):
            if row_idx % 2 == 0:  # Even rows (0-indexed, so actually odd visual rows)
                table_style.add("BACKGROUND", (0, row_idx), (-1, row_idx), cls.TABLE_ALT_ROW_BG)
        return table_style

    @classmethod
    def get_totals_table_style(cls):
        """Table style for totals section"""
        return TableStyle(
            [
                # All rows
                ("FONTNAME", (0, 0), (-1, -1), cls.FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), cls.FONT_SIZE_NORMAL),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                # Grand total row (bold)
                ("FONTNAME", (0, -1), (-1, -1), cls.FONT_NAME_BOLD),
                ("FONTSIZE", (0, -1), (-1, -1), cls.FONT_SIZE_HEADER),
                ("TEXTCOLOR", (0, -1), (-1, -1), cls.BMC_BLUE),
                ("BACKGROUND", (0, -1), (-1, -1), cls.HIGHLIGHT_YELLOW),
                # Borders
                ("LINEABOVE", (0, 0), (-1, 0), 1, cls.TABLE_BORDER),
                ("LINEABOVE", (0, -1), (-1, -1), 2, cls.BMC_BLUE),
                # Padding
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]
        )

    @classmethod
    def get_conditions_style(cls):
        """Style for terms and conditions"""
        return ParagraphStyle(
            "BMCConditions",
            fontName=cls.FONT_NAME,
            fontSize=cls.FONT_SIZE_TINY,
            textColor=cls.TEXT_GRAY,
            leftIndent=10,
            spaceAfter=3,
            leading=11,
            bulletFontName=cls.FONT_NAME,
            bulletFontSize=cls.FONT_SIZE_TINY,
        )
    
    @classmethod
    def get_comments_style(cls, font_size=None, leading=None):
        """Style for comments section (NEW: Supports dynamic sizing for 1-page fit)"""
        fs = font_size if font_size is not None else cls.COMMENTS_FONT_BASE
        ld = leading if leading is not None else cls.COMMENTS_LEADING_BASE
        return ParagraphStyle(
            "BMCComments",
            fontName=cls.FONT_NAME,
            fontSize=fs,
            textColor=cls.TEXT_BLACK,
            leftIndent=15,
            spaceAfter=2,
            leading=ld,
            bulletFontName=cls.FONT_NAME,
            bulletFontSize=fs,
        )
    
    @classmethod
    def get_bank_transfer_table_style(cls):
        """Table style for bank transfer footer box (NEW)"""
        return TableStyle(
            [
                # First row (header with gray background)
                ("BACKGROUND", (0, 0), (-1, 0), cls.FOOTER_BOX_BG),
                ("FONTNAME", (0, 0), (-1, 0), cls.FONT_NAME_BOLD),
                ("FONTSIZE", (0, 0), (-1, 0), 8.4),
                ("TEXTCOLOR", (0, 0), (-1, 0), cls.TEXT_BLACK),
                # All other rows
                ("FONTNAME", (0, 1), (-1, -1), cls.FONT_NAME),
                ("FONTSIZE", (0, 1), (-1, -1), 8.4),
                ("TEXTCOLOR", (0, 1), (-1, -1), cls.TEXT_BLACK),
                # Alignment
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                # Grid lines (box + internal lines)
                ("GRID", (0, 0), (-1, -1), 1, cls.TABLE_BORDER),
                ("BOX", (0, 0), (-1, -1), 1.5, cls.TEXT_BLACK),
                # Padding (tight)
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )


class QuotationConstants:
    """Business constants for BMC Uruguay quotations"""

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
        """Returns list of standard quotation conditions"""
        return [
            f"*Ancho útil paneles de Fachada = {cls.PANEL_WIDTH_FACADE} m de Cubierta = {cls.PANEL_WIDTH_ROOF} m. Pendiente mínima {cls.MIN_SLOPE_PERCENTAGE}%.",
            f"*Para saber más del sistema constructivo SPM haga click en {cls.SPM_SYSTEM_VIDEO}",
            f"*Fabricación y entrega de {cls.PRODUCTION_DAYS_MIN} a {cls.PRODUCTION_DAYS_MAX} días. Dependiendo de Producción. *Sujeto a cambios según fábrica.",
            "*Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).",
            "*Con tarjeta de crédito y en cuotas, sería en $ y a través de Mercado Pago con un recargo de 11,9% (comisión MP).",
            "*Retiro sin cargo en Planta Industrial de Bromyros S.A. (Colonia Nicolich / CANELONES)",
            "*BMC no asume responsabilidad por fallas producidas por no respetar la autoportancia sugerida.",
            "*No incluye descarga del material. Se requieren 2 personas. *Oferta válida por 10 días a partir de la fecha.",
            "*Opcional: Costo descarga $1500 + IVA / H. Únicamente en ciudad de Maldonado.",
            "*Al aceptar esta cotización confirma haber revisado el contenido de la misma *Paneles de cubierta engrafados.",
            "en cuanto a medidas, cantidades, colores, valores y tipo de producto. Alquiler de engrafadora U$S 30 + Iva por día.",
            "*Nuestro asesoramiento es una guía, en ningún caso sustituye el trabajo profesional de Arq. o Ing.",
            "*Al momento de recibir el material corroborar el estado del mismo. Una vez recibido, no aceptamos devolución",
            f"Por cualquier duda, consultar al {cls.CONTACT_PHONE}. Lea los Términos y Condiciones",
        ]
    
    @classmethod
    def get_standard_comments(cls):
        """Returns list of standard quotation comments (NEW: For COMENTARIOS section)"""
        return [
            "Entrega de 10 a 15 días, dependemos de producción.",
            "Oferta válida por 10 días a partir de la fecha.",
            "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).",
            f"Para saber más del sistema constructivo SPM: {cls.SPM_SYSTEM_VIDEO}",
        ]
