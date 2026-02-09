#!/usr/bin/env python3
"""
PDF Styles Configuration
=========================

Centralized style definitions for BMC Uruguay quotation PDFs.
Ensures consistent branding and layout across all generated documents.

Updated: 2026-02-09
- New BMC logo (Logo_BMC- PNG.png)
- Revised margins (12mm L/R, 10mm top, 8-10mm bottom)
- Comments section with per-line bold/red formatting
- Bank transfer footer boxed grid
- 1-page-first rule: shrink comments font/leading before anything else
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

    # Margins (revised per design spec)
    MARGIN_TOP = 10 * mm
    MARGIN_BOTTOM = 9 * mm
    MARGIN_LEFT = 12 * mm
    MARGIN_RIGHT = 12 * mm

    # Colors - BMC Uruguay Brand
    BMC_BLUE = colors.HexColor("#003366")
    BMC_LIGHT_BLUE = colors.HexColor("#0066CC")
    TABLE_HEADER_BG = colors.HexColor("#EDEDED")
    TABLE_ALT_ROW_BG = colors.HexColor("#FAFAFA")
    TABLE_BORDER = colors.HexColor("#CCCCCC")
    TABLE_GRID_COLOR = colors.HexColor("#D0D0D0")
    TEXT_BLACK = colors.black
    TEXT_GRAY = colors.HexColor("#666666")
    TEXT_RED = colors.HexColor("#CC0000")
    HIGHLIGHT_YELLOW = colors.HexColor("#FFF9E6")
    LINK_BLUE = colors.HexColor("#0066CC")
    FOOTER_HEADER_BG = colors.HexColor("#EDEDED")

    # Fonts
    FONT_NAME = "Helvetica"
    FONT_NAME_BOLD = "Helvetica-Bold"

    FONT_SIZE_TITLE = 14
    FONT_SIZE_SUBTITLE = 12
    FONT_SIZE_HEADER = 11
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_SMALL = 9

    # Table-specific font sizes (per spec)
    FONT_SIZE_TABLE_HEADER = 9.1  # ~9.0-9.2
    FONT_SIZE_TABLE_ROW = 8.6  # ~8.5-8.7

    # Comments-specific font sizes (per spec, base target)
    FONT_SIZE_COMMENT = 8.1  # ~8.0-8.2
    COMMENT_LEADING = 9.5  # ~9.3-9.6

    # Footer bank transfer font
    FONT_SIZE_FOOTER = 8.4

    FONT_SIZE_TINY = 8

    # Logo - use official BMC logo
    LOGO_HEIGHT = 18 * mm  # ~18mm height
    # Auto-calculate width to keep aspect ratio (set at runtime)
    LOGO_WIDTH = None  # Will be calculated from aspect ratio

    # Logo path resolution: try /mnt/data first, then local assets
    @staticmethod
    def get_logo_path(custom_path=None):
        """Resolve logo path with fallback chain"""
        candidates = []
        if custom_path:
            candidates.append(custom_path)
        candidates.extend([
            "/mnt/data/Logo_BMC- PNG.png",
            os.path.join(os.path.dirname(__file__), "assets", "bmc_logo.png"),
            "panelin_reports/assets/bmc_logo.png",
            "bmc_logo.png",
        ])
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    @classmethod
    def get_title_style(cls):
        """Style for main quotation title (centered in header)"""
        return ParagraphStyle(
            "BMCTitle",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=cls.FONT_SIZE_TITLE,
            textColor=cls.BMC_BLUE,
            spaceAfter=6,
            alignment=1,  # Center aligned
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
            spaceBefore=8,
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

    @classmethod
    def get_comment_style(cls, font_size=None, leading=None):
        """
        Style for comments section text.
        Supports dynamic shrinking for 1-page-first rule.
        """
        fs = font_size or cls.FONT_SIZE_COMMENT
        ld = leading or cls.COMMENT_LEADING
        return ParagraphStyle(
            "BMCComment",
            fontName=cls.FONT_NAME,
            fontSize=fs,
            textColor=cls.TEXT_BLACK,
            spaceAfter=1.5,
            leading=ld,
            leftIndent=8,
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
            spaceAfter=1.5,
            leading=ld,
            leftIndent=8,
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
            textColor=cls.TEXT_RED,
            spaceAfter=1.5,
            leading=ld,
            leftIndent=8,
        )

    @classmethod
    def get_comment_bold_red_style(cls, font_size=None, leading=None):
        """Style for bold + red comment lines"""
        fs = font_size or cls.FONT_SIZE_COMMENT
        ld = leading or cls.COMMENT_LEADING
        return ParagraphStyle(
            "BMCCommentBoldRed",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=fs,
            textColor=cls.TEXT_RED,
            spaceAfter=1.5,
            leading=ld,
            leftIndent=8,
        )

    @classmethod
    def get_comment_title_style(cls):
        """Style for 'COMENTARIOS:' section title"""
        return ParagraphStyle(
            "BMCCommentTitle",
            fontName=cls.FONT_NAME_BOLD,
            fontSize=9,
            textColor=cls.TEXT_BLACK,
            spaceAfter=3,
            spaceBefore=6,
        )

    @classmethod
    def get_products_table_style(cls, num_data_rows=0):
        """
        Table style for products section with alternating rows.
        Thin grid lines, light gray header, alternating row backgrounds.
        """
        style_commands = [
            # Header row
            ("BACKGROUND", (0, 0), (-1, 0), cls.TABLE_HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), cls.BMC_BLUE),
            ("FONTNAME", (0, 0), (-1, 0), cls.FONT_NAME_BOLD),
            ("FONTSIZE", (0, 0), (-1, 0), cls.FONT_SIZE_TABLE_HEADER),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            # Data rows
            ("FONTNAME", (0, 1), (-1, -1), cls.FONT_NAME),
            ("FONTSIZE", (0, 1), (-1, -1), cls.FONT_SIZE_TABLE_ROW),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),  # Product name left-aligned
            # Right-align numeric columns (Unid/Cant/USD/Total)
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            # Thin grid lines
            ("GRID", (0, 0), (-1, -1), 0.4, cls.TABLE_GRID_COLOR),
            ("LINEBELOW", (0, 0), (-1, 0), 0.8, cls.BMC_BLUE),
            # Padding (tight)
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]

        # Add alternating row backgrounds
        for i in range(1, num_data_rows + 1):
            if i % 2 == 0:
                style_commands.append(
                    ("BACKGROUND", (0, i), (-1, i), cls.TABLE_ALT_ROW_BG)
                )

        return TableStyle(style_commands)

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

    @classmethod
    def get_footer_bank_table_style(cls):
        """
        Table style for bank transfer footer box.
        Grid/box lines visible, first row gray background.
        """
        return TableStyle(
            [
                # First row header background
                ("BACKGROUND", (0, 0), (-1, 0), cls.FOOTER_HEADER_BG),
                # All cells
                ("FONTNAME", (0, 0), (-1, -1), cls.FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), cls.FONT_SIZE_FOOTER),
                ("TEXTCOLOR", (0, 0), (-1, -1), cls.TEXT_BLACK),
                # Bold first column
                ("FONTNAME", (0, 0), (0, -1), cls.FONT_NAME_BOLD),
                # Grid (outer border + internal row lines)
                ("BOX", (0, 0), (-1, -1), 0.8, cls.TEXT_BLACK),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, cls.TABLE_GRID_COLOR),
                # Tight padding
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                # Alignment
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
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

    # ----- Comment lines with special formatting rules -----
    # These define which comment lines get bold, red, or bold+red treatment.
    COMMENT_FORMAT_RULES = {
        # Lines that should be BOLD
        "bold": [
            "Entrega de 10 a 15 días, dependemos de producción.",
        ],
        # Lines that should be RED
        "red": [
            "Oferta válida por 10 días a partir de la fecha.",
        ],
        # Lines that should be BOLD + RED
        "bold_red": [
            "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).",
        ],
    }

    # ----- Standard comment lines for cotización -----
    STANDARD_COMMENTS = [
        "Entrega de 10 a 15 días, dependemos de producción.",
        "Oferta válida por 10 días a partir de la fecha.",
        "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).",
        f"Ancho útil paneles de Fachada = 1.14 m de Cubierta = 1.12 m. Pendiente mínima 7%.",
        "Con tarjeta de crédito y en cuotas, sería en $ y a través de Mercado Pago con un recargo de 11,9% (comisión MP).",
        "Retiro sin cargo en Planta Industrial de Bromyros S.A. (Colonia Nicolich / CANELONES)",
        "BMC no asume responsabilidad por fallas producidas por no respetar la autoportancia sugerida.",
        "No incluye descarga del material. Se requieren 2 personas.",
        "Al aceptar esta cotización confirma haber revisado el contenido de la misma.",
        "Nuestro asesoramiento es una guía, en ningún caso sustituye el trabajo profesional de Arq. o Ing.",
        "Al momento de recibir el material corroborar el estado del mismo. Una vez recibido, no aceptamos devolución.",
        f"Para saber más del sistema constructivo SPM: https://youtu.be/Am4mZskFMgc",
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
