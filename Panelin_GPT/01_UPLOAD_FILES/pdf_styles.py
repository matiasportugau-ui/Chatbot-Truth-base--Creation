#!/usr/bin/env python3
"""
PDF Styles Configuration
=========================

Centralized style definitions for BMC Uruguay quotation PDFs.
Ensures consistent branding and layout across all generated documents.

Design v2.0 (2026-02-09):
  - Header: two-column [logo | centered title]
  - Table: #EDEDED header, alternating rows, right-aligned numerics
  - Comments: bullet list, smaller font (8.0-8.2pt), per-line bold/red
  - Footer: bank transfer boxed grid
  - 1-page-first rule: shrink comments first to fit A4
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

    # Margins (updated for tighter 1-page fit)
    MARGIN_TOP = 10 * mm
    MARGIN_BOTTOM = 9 * mm
    MARGIN_LEFT = 12 * mm
    MARGIN_RIGHT = 12 * mm

    # Colors – BMC Uruguay Brand
    BMC_BLUE = colors.HexColor("#003366")
    BMC_LIGHT_BLUE = colors.HexColor("#0066CC")
    BMC_RED = colors.HexColor("#CC0000")
    TABLE_HEADER_BG = colors.HexColor("#EDEDED")
    TABLE_ALT_ROW_BG = colors.HexColor("#FAFAFA")
    TABLE_BORDER = colors.HexColor("#CCCCCC")
    FOOTER_HEADER_BG = colors.HexColor("#EDEDED")
    TEXT_BLACK = colors.black
    TEXT_GRAY = colors.HexColor("#666666")
    HIGHLIGHT_YELLOW = colors.HexColor("#FFF9E6")
    LINK_BLUE = colors.HexColor("#0055AA")

    # Fonts
    FONT_NAME = "Helvetica"
    FONT_NAME_BOLD = "Helvetica-Bold"

    FONT_SIZE_TITLE = 13
    FONT_SIZE_SUBTITLE = 11
    FONT_SIZE_HEADER = 9
    FONT_SIZE_NORMAL = 8.5
    FONT_SIZE_SMALL = 8.5  # table rows
    FONT_SIZE_TABLE_HEADER = 9.1  # table header row
    FONT_SIZE_COMMENT = 8.0  # comments base
    FONT_SIZE_TINY = 7.5

    COMMENT_LEADING = 9.3  # leading for comments

    # Logo
    LOGO_HEIGHT = 18 * mm
    # Auto-detect logo path: prefer official BMC logo, fallback to placeholder
    LOGO_PATH = None  # Will be resolved at runtime

    @classmethod
    def resolve_logo_path(cls, custom_path=None):
        """Resolve the logo path, trying multiple locations."""
        candidates = []
        if custom_path:
            candidates.append(custom_path)
        candidates.extend([
            "/mnt/data/Logo_BMC- PNG.png",
            os.path.join(os.path.dirname(__file__), "assets", "Logo_BMC.png"),
            "panelin_reports/assets/Logo_BMC.png",
            "Logo_BMC.png",
            "bmc_logo.png",
            os.path.join(os.path.dirname(__file__), "assets", "bmc_logo.png"),
        ])
        for p in candidates:
            if p and os.path.exists(p):
                return p
        return None

    # ──────────────── Paragraph Styles ────────────────

    @classmethod
    def get_title_style(cls):
        """Style for main quotation title (centered in header)"""
        return ParagraphStyle(
            "BMCTitle",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=cls.FONT_SIZE_TITLE,
            textColor=cls.BMC_BLUE,
            spaceAfter=4,
            alignment=1,  # Center
            leading=cls.FONT_SIZE_TITLE + 4,
        )

    @classmethod
    def get_header_style(cls):
        """Style for section headers"""
        return ParagraphStyle(
            "BMCHeader",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=cls.FONT_SIZE_HEADER,
            textColor=cls.BMC_BLUE,
            spaceAfter=2,
            spaceBefore=2,
        )

    @classmethod
    def get_normal_style(cls):
        """Style for normal text"""
        return ParagraphStyle(
            "BMCNormal",
            fontName=cls.FONT_NAME,
            fontSize=cls.FONT_SIZE_NORMAL,
            textColor=cls.TEXT_BLACK,
            spaceAfter=1,
            leading=cls.FONT_SIZE_NORMAL + 2,
        )

    @classmethod
    def get_small_style(cls):
        """Style for small text (conditions, notes)"""
        return ParagraphStyle(
            "BMCSmall",
            fontName=cls.FONT_NAME,
            fontSize=cls.FONT_SIZE_TINY,
            textColor=cls.TEXT_GRAY,
            spaceAfter=2,
            leading=10,
        )

    @classmethod
    def get_comment_style(cls, font_size=None, leading=None):
        """Style for comment text (bullet list items, normal)"""
        fs = font_size or cls.FONT_SIZE_COMMENT
        ld = leading or cls.COMMENT_LEADING
        return ParagraphStyle(
            "BMCComment",
            fontName=cls.FONT_NAME,
            fontSize=fs,
            textColor=cls.TEXT_BLACK,
            spaceAfter=1,
            leading=ld,
            leftIndent=10,
        )

    @classmethod
    def get_comment_bold_style(cls, font_size=None, leading=None):
        """Style for bold comment lines"""
        fs = font_size or cls.FONT_SIZE_COMMENT
        ld = leading or cls.COMMENT_LEADING
        return ParagraphStyle(
            "BMCCommentBold",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=fs,
            textColor=cls.TEXT_BLACK,
            spaceAfter=1,
            leading=ld,
            leftIndent=10,
        )

    @classmethod
    def get_comment_red_style(cls, font_size=None, leading=None):
        """Style for red comment lines"""
        fs = font_size or cls.FONT_SIZE_COMMENT
        ld = leading or cls.COMMENT_LEADING
        return ParagraphStyle(
            "BMCCommentRed",
            fontName=cls.FONT_NAME,
            fontSize=fs,
            textColor=cls.BMC_RED,
            spaceAfter=1,
            leading=ld,
            leftIndent=10,
        )

    @classmethod
    def get_comment_bold_red_style(cls, font_size=None, leading=None):
        """Style for bold+red comment lines"""
        fs = font_size or cls.FONT_SIZE_COMMENT
        ld = leading or cls.COMMENT_LEADING
        return ParagraphStyle(
            "BMCCommentBoldRed",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=fs,
            textColor=cls.BMC_RED,
            spaceAfter=1,
            leading=ld,
            leftIndent=10,
        )

    # ──────────────── Table Styles ────────────────

    @classmethod
    def get_products_table_style(cls, num_data_rows=0):
        """
        Table style for products/accessories/fixings tables.
        Updated: #EDEDED header, alternating rows, right-aligned numerics.
        """
        commands = [
            # Header row
            ("BACKGROUND", (0, 0), (-1, 0), cls.TABLE_HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), cls.BMC_BLUE),
            ("FONTNAME", (0, 0), (-1, 0), cls.FONT_NAME_BOLD),
            ("FONTSIZE", (0, 0), (-1, 0), cls.FONT_SIZE_TABLE_HEADER),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            # Data rows font
            ("FONTNAME", (0, 1), (-1, -1), cls.FONT_NAME),
            ("FONTSIZE", (0, 1), (-1, -1), cls.FONT_SIZE_SMALL),
            # Alignment: product name left, rest right-aligned for numerics
            ("ALIGN", (0, 1), (0, -1), "LEFT"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            # Grid
            ("GRID", (0, 0), (-1, -1), 0.5, cls.TABLE_BORDER),
            ("LINEBELOW", (0, 0), (-1, 0), 1, cls.BMC_BLUE),
            # Padding (tight for 1-page fit)
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]

        # Alternating row backgrounds
        if num_data_rows > 0:
            for i in range(1, num_data_rows + 1):
                if i % 2 == 0:
                    commands.append(
                        ("BACKGROUND", (0, i), (-1, i), cls.TABLE_ALT_ROW_BG)
                    )

        return TableStyle(commands)

    @classmethod
    def get_totals_table_style(cls):
        """Table style for totals section"""
        return TableStyle(
            [
                # All rows
                ("FONTNAME", (0, 0), (-1, -1), cls.FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), 8.0),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                # Grand total row (bold)
                ("FONTNAME", (0, -1), (-1, -1), cls.FONT_NAME_BOLD),
                ("FONTSIZE", (0, -1), (-1, -1), 9.5),
                ("TEXTCOLOR", (0, -1), (-1, -1), cls.BMC_BLUE),
                ("BACKGROUND", (0, -1), (-1, -1), cls.HIGHLIGHT_YELLOW),
                # Borders
                ("LINEABOVE", (0, 0), (-1, 0), 1, cls.TABLE_BORDER),
                ("LINEABOVE", (0, -1), (-1, -1), 2, cls.BMC_BLUE),
                # Padding
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )

    @classmethod
    def get_bank_transfer_table_style(cls):
        """Table style for the bank transfer footer box."""
        return TableStyle(
            [
                # Outer box border
                ("BOX", (0, 0), (-1, -1), 1, cls.TABLE_BORDER),
                # Internal row lines
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, cls.TABLE_BORDER),
                ("LINEBELOW", (0, 1), (-1, 1), 0.5, cls.TABLE_BORDER),
                # Internal column separator
                ("LINEAFTER", (0, 0), (0, -1), 0.5, cls.TABLE_BORDER),
                # First row background light gray
                ("BACKGROUND", (0, 0), (-1, 0), cls.FOOTER_HEADER_BG),
                # Font
                ("FONTNAME", (0, 0), (-1, -1), cls.FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), 8.4),
                ("TEXTCOLOR", (0, 0), (-1, -1), cls.TEXT_BLACK),
                # Padding
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                # Left column: left-aligned
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                # Right column: left-aligned
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ]
        )

    @classmethod
    def get_conditions_style(cls):
        """Style for terms and conditions"""
        return ParagraphStyle(
            "BMCConditions",
            fontName=cls.FONT_NAME,
            fontSize=7.0,
            textColor=cls.TEXT_GRAY,
            leftIndent=8,
            spaceAfter=0,
            leading=8.2,
            bulletFontName=cls.FONT_NAME,
            bulletFontSize=7.0,
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

    # ──────── Comment formatting rules ────────
    # Lines that match these patterns get special formatting
    COMMENT_BOLD_PATTERNS = [
        "Entrega de 10 a 15 días",
        "entrega de 10 a 15 días",
    ]
    COMMENT_RED_PATTERNS = [
        "Oferta válida por 10 días",
        "oferta válida por 10 días",
    ]
    COMMENT_BOLD_RED_PATTERNS = [
        "Incluye descuentos de Pago al Contado",
        "incluye descuentos de Pago al Contado",
    ]

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
        """Returns the standard comment lines for cotizaciones."""
        return [
            f"Entrega de {cls.PRODUCTION_DAYS_MIN} a {cls.PRODUCTION_DAYS_MAX} días, dependemos de producción.",
            f"Oferta válida por {cls.QUOTE_VALIDITY_DAYS} días a partir de la fecha.",
            "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).",
            f"Para saber más del sistema constructivo SPM: {cls.SPM_SYSTEM_VIDEO}",
        ]
