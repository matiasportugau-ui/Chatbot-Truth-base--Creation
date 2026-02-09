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

    # Margins - Updated for new template (2026-02-09)
    MARGIN_TOP = 10 * mm
    MARGIN_BOTTOM = 10 * mm
    MARGIN_LEFT = 12 * mm
    MARGIN_RIGHT = 12 * mm

    # Colors - BMC Uruguay Brand
    BMC_BLUE = colors.HexColor("#003366")
    BMC_LIGHT_BLUE = colors.HexColor("#0066CC")
    TABLE_HEADER_BG = colors.HexColor("#EDEDED")  # Updated for new template
    TABLE_ROW_ALT_BG = colors.HexColor("#FAFAFA")  # Alternating row background
    TABLE_BORDER = colors.HexColor("#CCCCCC")
    TEXT_BLACK = colors.black
    TEXT_GRAY = colors.HexColor("#666666")
    TEXT_RED = colors.red  # For special comment formatting
    HIGHLIGHT_YELLOW = colors.HexColor("#FFF9E6")

    # Fonts
    FONT_NAME = "Helvetica"
    FONT_NAME_BOLD = "Helvetica-Bold"

    # Updated font sizes for new template (2026-02-09)
    FONT_SIZE_TITLE = 14  # Centered title in header
    FONT_SIZE_SUBTITLE = 12
    FONT_SIZE_HEADER = 10
    FONT_SIZE_TABLE_HEADER = 9.2  # Materials table header
    FONT_SIZE_TABLE_ROW = 8.6  # Materials table rows
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_SMALL = 9
    FONT_SIZE_COMMENTS = 8.2  # Comments section base size (may shrink to fit page)
    FONT_SIZE_TINY = 8.4  # Bank transfer footer

    # Leading (line spacing)
    LEADING_COMMENTS = 9.5  # Comments section (may shrink to fit page)
    LEADING_TINY = 10  # Bank transfer footer

    # Logo - Official BMC logo (2026-02-09)
    LOGO_HEIGHT = 18 * mm  # Fixed height, auto width to maintain aspect ratio
    # Look for logo in multiple locations
    LOGO_PATH = (
        "/mnt/data/Logo_BMC- PNG.png"
        if os.path.exists("/mnt/data/Logo_BMC- PNG.png")
        else (
            "bmc_logo.png"
            if os.path.exists("bmc_logo.png")
            else "panelin_reports/assets/bmc_logo.png"
        )
    )

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
        """Table style for products section - Updated template (2026-02-09)"""
        style_commands = [
            # Header row - light gray background
            ("BACKGROUND", (0, 0), (-1, 0), cls.TABLE_HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), cls.TEXT_BLACK),
            ("FONTNAME", (0, 0), (-1, 0), cls.FONT_NAME_BOLD),
            ("FONTSIZE", (0, 0), (-1, 0), cls.FONT_SIZE_TABLE_HEADER),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),  # First column left
            ("ALIGN", (1, 0), (-1, 0), "RIGHT"),  # Numeric columns right
            # Data rows
            ("FONTNAME", (0, 1), (-1, -1), cls.FONT_NAME),
            ("FONTSIZE", (0, 1), (-1, -1), cls.FONT_SIZE_TABLE_ROW),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),  # Product name left-aligned
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),  # Numbers right-aligned
            # Thin grid lines
            ("GRID", (0, 0), (-1, -1), 0.5, cls.TABLE_BORDER),
            # Padding
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
        
        # Add alternating row backgrounds (white/very light gray)
        # This will be applied dynamically based on row count
        return TableStyle(style_commands)
    
    @classmethod
    def apply_alternating_rows(cls, table_style, num_rows):
        """Apply alternating row backgrounds to a table style"""
        for i in range(1, num_rows):  # Skip header row (0)
            if i % 2 == 0:  # Even rows get light gray
                table_style.add("BACKGROUND", (0, i), (-1, i), cls.TABLE_ROW_ALT_BG)
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
    def get_comments_style(cls, bold=False, red=False, font_size=None, leading=None):
        """Style for comments section with selective formatting (2026-02-09)
        
        Args:
            bold: Apply bold formatting
            red: Apply red color
            font_size: Custom font size (default: FONT_SIZE_COMMENTS)
            leading: Custom leading (default: LEADING_COMMENTS)
        """
        return ParagraphStyle(
            "BMCComments",
            fontName=cls.FONT_NAME_BOLD if bold else cls.FONT_NAME,
            fontSize=font_size if font_size else cls.FONT_SIZE_COMMENTS,
            textColor=cls.TEXT_RED if red else cls.TEXT_BLACK,
            leftIndent=15,
            spaceAfter=2,
            leading=leading if leading else cls.LEADING_COMMENTS,
            bulletFontName=cls.FONT_NAME,
            bulletFontSize=font_size if font_size else cls.FONT_SIZE_COMMENTS,
        )
    
    @classmethod
    def get_bank_transfer_table_style(cls):
        """Table style for bank transfer footer box (2026-02-09)"""
        return TableStyle(
            [
                # First row - light gray background
                ("BACKGROUND", (0, 0), (-1, 0), cls.TABLE_HEADER_BG),
                # All rows
                ("FONTNAME", (0, 0), (-1, -1), cls.FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), cls.FONT_SIZE_TINY),
                ("TEXTCOLOR", (0, 0), (-1, -1), cls.TEXT_BLACK),
                # Alignment
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                # Grid/box lines
                ("BOX", (0, 0), (-1, -1), 1, cls.TABLE_BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, cls.TABLE_BORDER),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, cls.TABLE_BORDER),
                # Padding
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
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
    
    # Formatted comments for new template (2026-02-09)
    # These lines have specific formatting rules (bold/red)
    COMMENT_DELIVERY_BOLD = "Entrega de 10 a 15 días, dependemos de producción."
    COMMENT_VALIDITY_RED = "Oferta válida por 10 días a partir de la fecha."
    COMMENT_PAYMENT_BOLD_RED = "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica)."

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
    def get_formatted_comments(cls):
        """Returns formatted comments for new PDF template (2026-02-09)
        
        Returns list of tuples: (text, bold, red, is_youtube_url)
        """
        return [
            (cls.COMMENT_DELIVERY_BOLD, True, False, False),  # BOLD
            (cls.COMMENT_VALIDITY_RED, False, True, False),  # RED
            (cls.COMMENT_PAYMENT_BOLD_RED, True, True, False),  # BOLD + RED
            (cls.SPM_SYSTEM_VIDEO, False, False, True),  # YouTube URL (plain text)
        ]
