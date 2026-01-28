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
from reportlab.lib.units import mm
from reportlab.platypus import TableStyle


class BMCStyles:
    """BMC Uruguay PDF styling constants and configurations"""
    
    # Page Layout
    PAGE_SIZE = A4
    PAGE_WIDTH = A4[0]
    PAGE_HEIGHT = A4[1]
    
    # Margins
    MARGIN_TOP = 15 * mm
    MARGIN_BOTTOM = 15 * mm
    MARGIN_LEFT = 15 * mm
    MARGIN_RIGHT = 15 * mm
    
    # Colors - BMC Uruguay Brand
    BMC_BLUE = colors.HexColor('#003366')
    BMC_LIGHT_BLUE = colors.HexColor('#0066CC')
    TABLE_HEADER_BG = colors.HexColor('#E8E8E8')
    TABLE_BORDER = colors.HexColor('#CCCCCC')
    TEXT_BLACK = colors.black
    TEXT_GRAY = colors.HexColor('#666666')
    HIGHLIGHT_YELLOW = colors.HexColor('#FFF9E6')
    
    # Fonts
    FONT_NAME = 'Helvetica'
    FONT_NAME_BOLD = 'Helvetica-Bold'
    
    FONT_SIZE_TITLE = 18
    FONT_SIZE_SUBTITLE = 14
    FONT_SIZE_HEADER = 12
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_SMALL = 9
    FONT_SIZE_TINY = 8
    
    # Logo
    LOGO_WIDTH = 80 * mm
    LOGO_HEIGHT = 30 * mm
    LOGO_PATH = 'panelin_reports/assets/bmc_logo.png'  # To be provided
    
    @classmethod
    def get_title_style(cls):
        """Style for main quotation title"""
        return ParagraphStyle(
            'BMCTitle',
            fontName=cls.FONT_NAME_BOLD,
            fontSize=cls.FONT_SIZE_TITLE,
            textColor=cls.BMC_BLUE,
            spaceAfter=12,
            alignment=0  # Left aligned
        )
    
    @classmethod
    def get_header_style(cls):
        """Style for section headers"""
        return ParagraphStyle(
            'BMCHeader',
            fontName=cls.FONT_NAME_BOLD,
            fontSize=cls.FONT_SIZE_HEADER,
            textColor=cls.BMC_BLUE,
            spaceAfter=6,
            spaceBefore=12
        )
    
    @classmethod
    def get_normal_style(cls):
        """Style for normal text"""
        return ParagraphStyle(
            'BMCNormal',
            fontName=cls.FONT_NAME,
            fontSize=cls.FONT_SIZE_NORMAL,
            textColor=cls.TEXT_BLACK,
            spaceAfter=6
        )
    
    @classmethod
    def get_small_style(cls):
        """Style for small text (conditions, notes)"""
        return ParagraphStyle(
            'BMCSmall',
            fontName=cls.FONT_NAME,
            fontSize=cls.FONT_SIZE_TINY,
            textColor=cls.TEXT_GRAY,
            spaceAfter=3,
            leading=10
        )
    
    @classmethod
    def get_products_table_style(cls):
        """Table style for products section"""
        return TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), cls.TABLE_HEADER_BG),
            ('TEXTCOLOR', (0, 0), (-1, 0), cls.BMC_BLUE),
            ('FONTNAME', (0, 0), (-1, 0), cls.FONT_NAME_BOLD),
            ('FONTSIZE', (0, 0), (-1, 0), cls.FONT_SIZE_SMALL),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), cls.FONT_NAME),
            ('FONTSIZE', (0, 1), (-1, -1), cls.FONT_SIZE_SMALL),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Product name left-aligned
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Numbers center-aligned
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, cls.TABLE_BORDER),
            ('LINEBELOW', (0, 0), (-1, 0), 1, cls.BMC_BLUE),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ])
    
    @classmethod
    def get_totals_table_style(cls):
        """Table style for totals section"""
        return TableStyle([
            # All rows
            ('FONTNAME', (0, 0), (-1, -1), cls.FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), cls.FONT_SIZE_NORMAL),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            
            # Grand total row (bold)
            ('FONTNAME', (0, -1), (-1, -1), cls.FONT_NAME_BOLD),
            ('FONTSIZE', (0, -1), (-1, -1), cls.FONT_SIZE_HEADER),
            ('TEXTCOLOR', (0, -1), (-1, -1), cls.BMC_BLUE),
            ('BACKGROUND', (0, -1), (-1, -1), cls.HIGHLIGHT_YELLOW),
            
            # Borders
            ('LINEABOVE', (0, 0), (-1, 0), 1, cls.TABLE_BORDER),
            ('LINEABOVE', (0, -1), (-1, -1), 2, cls.BMC_BLUE),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ])
    
    @classmethod
    def get_conditions_style(cls):
        """Style for terms and conditions"""
        return ParagraphStyle(
            'BMCConditions',
            fontName=cls.FONT_NAME,
            fontSize=cls.FONT_SIZE_TINY,
            textColor=cls.TEXT_GRAY,
            leftIndent=10,
            spaceAfter=3,
            leading=11,
            bulletFontName=cls.FONT_NAME,
            bulletFontSize=cls.FONT_SIZE_TINY
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
            f"Por cualquier duda, consultar al {cls.CONTACT_PHONE}. Lea los Términos y Condiciones"
        ]
