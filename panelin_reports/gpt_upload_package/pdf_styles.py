#!/usr/bin/env python3
"""
PDF Styles Configuration
=========================

Centralized style definitions for BMC Uruguay quotation PDFs.
Ensures consistent branding and layout across all generated documents.

Design update (2026-02-09):
- New BMC logo (Logo_BMC- PNG.png)
- Two-column header [logo | centered title]
- Materials table: #EDEDED header, alternating #FFF/#FAFAFA rows, right-align numerics
- COMENTARIOS block: bullet list, per-line bold/red support, 8.0-8.2pt
- Bank transfer footer: boxed/ruled table with gray first row
- 1-page-first rule: shrink comments before anything else
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

    # Colors - BMC Uruguay Brand
    BMC_BLUE = colors.HexColor("#003366")
    BMC_LIGHT_BLUE = colors.HexColor("#0066CC")
    BMC_RED = colors.HexColor("#CC0000")
    TABLE_HEADER_BG = colors.HexColor("#EDEDED")
    TABLE_ALT_ROW_BG = colors.HexColor("#FAFAFA")
    TABLE_BORDER = colors.HexColor("#CCCCCC")
    BANK_HEADER_BG = colors.HexColor("#EDEDED")
    TEXT_BLACK = colors.black
    TEXT_GRAY = colors.HexColor("#666666")
    HIGHLIGHT_YELLOW = colors.HexColor("#FFF9E6")

    # Fonts
    FONT_NAME = "Helvetica"
    FONT_NAME_BOLD = "Helvetica-Bold"

    FONT_SIZE_TITLE = 14
    FONT_SIZE_SUBTITLE = 12
    FONT_SIZE_HEADER = 10
    FONT_SIZE_NORMAL = 9
    FONT_SIZE_SMALL = 8.5
    FONT_SIZE_TINY = 8

    # Table-specific font sizes (matching spec)
    TABLE_HEADER_FONT_SIZE = 9.1  # ~9.0-9.2
    TABLE_ROW_FONT_SIZE = 8.6     # ~8.5-8.7

    # Comments font sizes (base; may be shrunk for 1-page fit)
    COMMENT_FONT_SIZE = 8.1       # ~8.0-8.2
    COMMENT_LEADING = 9.4         # ~9.3-9.6

    # Bank transfer footer font
    BANK_FONT_SIZE = 8.4

    # Logo – try multiple paths in priority order
    LOGO_HEIGHT = 18 * mm
    LOGO_CANDIDATES = [
        "/mnt/data/Logo_BMC- PNG.png",
        "Logo_BMC- PNG.png",
        "panelin_reports/assets/bmc_logo.png",
        os.path.join(os.path.dirname(__file__), "assets", "bmc_logo.png"),
    ]

    @classmethod
    def resolve_logo_path(cls):
        """Return the first logo path that exists on disk, or None."""
        for candidate in cls.LOGO_CANDIDATES:
            if os.path.isfile(candidate):
                return candidate
        return None

    # ── Title Style (centred, used inside header table) ──────────────
    @classmethod
    def get_title_style(cls):
        """Style for main quotation title (centered in header)"""
        return ParagraphStyle(
            "BMCTitle",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=cls.FONT_SIZE_TITLE,
            textColor=cls.BMC_BLUE,
            spaceAfter=0,
            spaceBefore=0,
            alignment=1,  # CENTER
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
            spaceAfter=4,
            spaceBefore=6,
        )

    @classmethod
    def get_normal_style(cls):
        """Style for normal text"""
        return ParagraphStyle(
            "BMCNormal",
            fontName=cls.FONT_NAME,
            fontSize=cls.FONT_SIZE_NORMAL,
            textColor=cls.TEXT_BLACK,
            spaceAfter=4,
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

    # ── Comment styles ───────────────────────────────────────────────
    @classmethod
    def get_comment_normal_style(cls, font_size=None, leading=None):
        """Style for a normal comment bullet line."""
        fs = font_size or cls.COMMENT_FONT_SIZE
        ld = leading or cls.COMMENT_LEADING
        return ParagraphStyle(
            "CommentNormal",
            fontName=cls.FONT_NAME,
            fontSize=fs,
            textColor=cls.TEXT_BLACK,
            spaceAfter=1,
            leading=ld,
        )

    @classmethod
    def get_comment_bold_style(cls, font_size=None, leading=None):
        """Style for a bold comment bullet line."""
        fs = font_size or cls.COMMENT_FONT_SIZE
        ld = leading or cls.COMMENT_LEADING
        return ParagraphStyle(
            "CommentBold",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=fs,
            textColor=cls.TEXT_BLACK,
            spaceAfter=1,
            leading=ld,
        )

    @classmethod
    def get_comment_red_style(cls, font_size=None, leading=None):
        """Style for a red comment bullet line."""
        fs = font_size or cls.COMMENT_FONT_SIZE
        ld = leading or cls.COMMENT_LEADING
        return ParagraphStyle(
            "CommentRed",
            fontName=cls.FONT_NAME,
            fontSize=fs,
            textColor=cls.BMC_RED,
            spaceAfter=1,
            leading=ld,
        )

    @classmethod
    def get_comment_bold_red_style(cls, font_size=None, leading=None):
        """Style for a bold + red comment bullet line."""
        fs = font_size or cls.COMMENT_FONT_SIZE
        ld = leading or cls.COMMENT_LEADING
        return ParagraphStyle(
            "CommentBoldRed",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=fs,
            textColor=cls.BMC_RED,
            spaceAfter=1,
            leading=ld,
        )

    # ── Products / Materials Table ──────────────────────────────────
    @classmethod
    def get_products_table_style(cls, num_data_rows=0):
        """
        Table style for products / accessories / fixings sections.
        Includes alternating row backgrounds and right-aligned numeric columns.
        """
        commands = [
            # Header row
            ("BACKGROUND", (0, 0), (-1, 0), cls.TABLE_HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), cls.BMC_BLUE),
            ("FONTNAME", (0, 0), (-1, 0), cls.FONT_NAME_BOLD),
            ("FONTSIZE", (0, 0), (-1, 0), cls.TABLE_HEADER_FONT_SIZE),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            # Data rows font
            ("FONTNAME", (0, 1), (-1, -1), cls.FONT_NAME),
            ("FONTSIZE", (0, 1), (-1, -1), cls.TABLE_ROW_FONT_SIZE),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),   # product name left
            # Right-align numeric columns (Unid / Cant / USD / Total — cols 1+)
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            # Thin grid lines
            ("GRID", (0, 0), (-1, -1), 0.4, cls.TABLE_BORDER),
            ("LINEBELOW", (0, 0), (-1, 0), 0.8, cls.BMC_BLUE),
            # Padding (tight for 1-page)
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]

        # Alternating row backgrounds (white / #FAFAFA)
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
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
        )

    # ── Bank Transfer Footer Table ──────────────────────────────────
    @classmethod
    def get_bank_table_style(cls):
        """Table style for the bank transfer footer box."""
        return TableStyle(
            [
                # Outer border + internal row lines
                ("BOX", (0, 0), (-1, -1), 0.8, cls.TABLE_BORDER),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, cls.TABLE_BORDER),
                ("LINEBELOW", (0, 1), (-1, 1), 0.5, cls.TABLE_BORDER),
                ("LINEBEFORE", (1, 0), (1, -1), 0.5, cls.TABLE_BORDER),
                # First row background light gray
                ("BACKGROUND", (0, 0), (-1, 0), cls.BANK_HEADER_BG),
                # Font
                ("FONTNAME", (0, 0), (-1, -1), cls.FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), cls.BANK_FONT_SIZE),
                ("TEXTCOLOR", (0, 0), (-1, -1), cls.TEXT_BLACK),
                # Padding
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
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
            spaceAfter=2,
            leading=10,
            bulletFontName=cls.FONT_NAME,
            bulletFontSize=cls.FONT_SIZE_TINY,
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

    # ── Standard comment lines with formatting hints ─────────────────
    # Format: (text, style_key)
    #   style_key ∈ {"normal", "bold", "red", "bold_red"}
    STANDARD_COMMENTS = [
        (
            f"Ancho útil paneles de Fachada = {1.14} m de Cubierta = {1.12} m. "
            f"Pendiente mínima {7.0}%.",
            "normal",
        ),
        (
            "Para saber más del sistema constructivo SPM haga click en "
            "https://youtu.be/Am4mZskFMgc",
            "normal",
        ),
        (
            "Entrega de 10 a 15 días, dependemos de producción.",
            "bold",
        ),
        (
            "Oferta válida por 10 días a partir de la fecha.",
            "red",
        ),
        (
            "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). "
            "Saldo del 40 % (previo a retiro de fábrica).",
            "bold_red",
        ),
        (
            "Con tarjeta de crédito y en cuotas, sería en $ y a través de "
            "Mercado Pago con un recargo de 11,9% (comisión MP).",
            "normal",
        ),
        (
            "Retiro sin cargo en Planta Industrial de Bromyros S.A. "
            "(Colonia Nicolich / CANELONES)",
            "normal",
        ),
        (
            "BMC no asume responsabilidad por fallas producidas por no respetar "
            "la autoportancia sugerida.",
            "normal",
        ),
        (
            "No incluye descarga del material. Se requieren 2 personas.",
            "normal",
        ),
        (
            "Opcional: Costo descarga $1500 + IVA / H. Únicamente en ciudad "
            "de Maldonado.",
            "normal",
        ),
        (
            "Al aceptar esta cotización confirma haber revisado el contenido de "
            "la misma en cuanto a medidas, cantidades, colores, valores y tipo "
            "de producto.",
            "normal",
        ),
        (
            "Paneles de cubierta engrafados. Alquiler de engrafadora U$S 30 + "
            "Iva por día.",
            "normal",
        ),
        (
            "Nuestro asesoramiento es una guía, en ningún caso sustituye el "
            "trabajo profesional de Arq. o Ing.",
            "normal",
        ),
        (
            "Al momento de recibir el material corroborar el estado del mismo. "
            "Una vez recibido, no aceptamos devolución.",
            "normal",
        ),
    ]

    # ── Per-line formatting rules for automatic matching ────────────
    # Key phrases → style_key for the COMENTARIOS section
    COMMENT_FORMAT_RULES = {
        "Entrega de 10 a 15 días": "bold",
        "Oferta válida por 10 días": "red",
        "Incluye descuentos de Pago al Contado": "bold_red",
    }

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
