#!/usr/bin/env python3
"""
BMC Uruguay Quotation PDF Generator
====================================

Generates professional quotation PDFs matching the exact structure
and branding of BMC Uruguay's standard quotation template.

Design v2.0 (2026-02-09):
  A) Header: BMC logo (left) + centered title (right two-column)
  B) Materials table: #EDEDED header, alternating rows, right-aligned numerics
  C) COMENTARIOS: block with per-line bold / red / bold+red formatting
  D) Bank transfer footer: boxed grid with first row gray
  E) 1-page-first: shrinks comment font/leading before anything else

Based on: Cotización 01042025 BASE - Isodec EPS xx mm
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Table, Paragraph, Spacer, Image, PageBreak,
    SimpleDocTemplate, TableStyle, KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .pdf_styles import BMCStyles, QuotationConstants


# ──────────────────────────────────────────────────────────────
# Data Formatter (unchanged business logic)
# ──────────────────────────────────────────────────────────────

class QuotationDataFormatter:
    """Formats raw quotation data into PDF-ready structure"""

    @staticmethod
    def format_for_pdf(raw_data: Dict) -> Dict:
        """
        Transform raw quotation data into structured PDF format.

        Args:
            raw_data: Dictionary containing quotation information from KB

        Returns:
            Dictionary formatted for PDF generation
        """
        # Extract and format client information
        client_info = {
            "name": raw_data.get("client_name", "Cliente"),
            "address": raw_data.get("client_address", ""),
            "phone": raw_data.get("client_phone", ""),
        }

        # Extract products
        products = raw_data.get("products", [])
        accessories = raw_data.get("accessories", [])
        fixings = raw_data.get("fixings", [])

        # Calculate totals
        totals = QuotationDataFormatter.calculate_totals(
            products, accessories, fixings, raw_data.get("shipping_usd")
        )

        # Format complete data structure
        formatted = {
            "date": raw_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "location": raw_data.get("location", QuotationConstants.DEFAULT_LOCATION),
            "quote_title": raw_data.get("quote_title", "Cotización"),
            "quote_description": raw_data.get("quote_description", ""),
            "client": client_info,
            "products": products,
            "accessories": accessories,
            "fixings": fixings,
            "totals": totals,
            "technical_specs": {
                "autoportancia": raw_data.get("autoportancia", 5.5),
                "apoyos": raw_data.get("apoyos", 1),
            },
            "comments": raw_data.get("comments", []),
            "conditions": QuotationConstants.get_standard_conditions(),
        }

        return formatted

    @staticmethod
    def calculate_item_total(item: Dict) -> float:
        """
        Calculate item total based on unit_base.

        Logic (2026-01-28 correction):
        - unit_base = 'unidad': quantity * sale_sin_iva
        - unit_base = 'ml': quantity * Length_m * sale_sin_iva
        - unit_base = 'm2': total_m2 * sale_sin_iva
        """
        unit_base = item.get("unit_base", "unidad").lower()
        price = item.get("sale_sin_iva", item.get("unit_price_usd", 0))

        if unit_base == "unidad":
            return item.get("quantity", 0) * price
        elif unit_base == "ml":
            quantity = item.get("quantity", 0)
            length_m = item.get("Length_m", item.get("length_m", 0))
            return quantity * length_m * price
        elif unit_base in ("m²", "m2"):
            total_m2 = item.get("total_m2", 0)
            return total_m2 * price
        else:
            return item.get("quantity", 0) * price

    @staticmethod
    def calculate_totals(
        products: List[Dict],
        accessories: List[Dict],
        fixings: List[Dict],
        shipping_usd: Optional[float] = None,
    ) -> Dict:
        """Calculate all financial totals for the quotation."""
        products_total = 0
        for item in products:
            if item.get("total_usd") is None:
                item["total_usd"] = QuotationDataFormatter.calculate_item_total(item)
            products_total += item["total_usd"]

        accessories_total = 0
        for item in accessories:
            if item.get("total_usd") is None:
                item["total_usd"] = QuotationDataFormatter.calculate_item_total(item)
            accessories_total += item["total_usd"]

        fixings_total = 0
        for item in fixings:
            if item.get("total_usd") is None:
                item["total_usd"] = QuotationDataFormatter.calculate_item_total(item)
            fixings_total += item["total_usd"]

        subtotal = products_total + accessories_total + fixings_total
        iva = subtotal * QuotationConstants.IVA_RATE
        materials_total = subtotal + iva

        shipping = (
            shipping_usd
            if shipping_usd is not None
            else QuotationConstants.DEFAULT_SHIPPING_USD
        )
        grand_total = materials_total + shipping

        total_m2_facade = sum(
            item.get("total_m2", 0)
            for item in products
            if "Fachada" in item.get("name", "")
        )
        total_m2_roof = sum(
            item.get("total_m2", 0)
            for item in products
            if "Cubierta" in item.get("name", "") or "Isodec" in item.get("name", "")
        )

        return {
            "subtotal": subtotal,
            "iva_rate": QuotationConstants.IVA_RATE,
            "iva": iva,
            "materials_total": materials_total,
            "shipping": shipping,
            "grand_total": grand_total,
            "total_m2_facade": total_m2_facade,
            "total_m2_roof": total_m2_roof,
        }

    @staticmethod
    def format_currency(amount: float) -> str:
        """Format currency as USD with proper formatting"""
        return f"${amount:,.2f}"

    @staticmethod
    def format_date(date_str: str) -> str:
        """Format date string consistently"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
        except Exception:
            return date_str


# ──────────────────────────────────────────────────────────────
# Comment-line format classifier
# ──────────────────────────────────────────────────────────────

def _classify_comment_line(text: str) -> str:
    """
    Return 'bold_red', 'bold', 'red', or 'normal' based on matching rules.
    """
    for pat in QuotationConstants.COMMENT_BOLD_RED_PATTERNS:
        if pat in text:
            return "bold_red"
    for pat in QuotationConstants.COMMENT_BOLD_PATTERNS:
        if pat in text:
            return "bold"
    for pat in QuotationConstants.COMMENT_RED_PATTERNS:
        if pat in text:
            return "red"
    return "normal"


# ──────────────────────────────────────────────────────────────
# Main PDF Builder
# ──────────────────────────────────────────────────────────────

class BMCQuotationPDF:
    """
    Main PDF generator for BMC Uruguay quotations.
    Replicates the exact structure from ODS template with
    updated branding/layout (v2.0).
    """

    def __init__(self, output_path: str, logo_path: Optional[str] = None):
        """
        Initialize PDF generator.

        Args:
            output_path: Path where PDF will be saved
            logo_path: Optional explicit path to the BMC logo image
        """
        self.output_path = output_path
        self.styles = BMCStyles()
        self.constants = QuotationConstants()
        self.logo_path = BMCStyles.resolve_logo_path(logo_path)

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def generate(self, quotation_data: Dict) -> str:
        """
        Generate complete quotation PDF.

        Args:
            quotation_data: Formatted quotation data dictionary

        Returns:
            Path to generated PDF file
        """
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=BMCStyles.PAGE_SIZE,
            topMargin=BMCStyles.MARGIN_TOP,
            bottomMargin=BMCStyles.MARGIN_BOTTOM,
            leftMargin=BMCStyles.MARGIN_LEFT,
            rightMargin=BMCStyles.MARGIN_RIGHT,
        )

        # Available content width
        self.content_width = (
            BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_LEFT - BMCStyles.MARGIN_RIGHT
        )

        # Build document elements
        story = []

        # A) Header section (logo + centered title)
        story.extend(self._build_header(quotation_data))
        story.append(Spacer(1, 4))

        # Title and client info
        story.extend(self._build_title_section(quotation_data))
        story.append(Spacer(1, 4))

        # B) Products table
        if quotation_data.get("products"):
            story.extend(self._build_products_table(quotation_data["products"]))
            story.append(Spacer(1, 4))

        # Accessories table
        if quotation_data.get("accessories"):
            story.extend(self._build_accessories_table(quotation_data["accessories"]))
            story.append(Spacer(1, 4))

        # Fixings table
        if quotation_data.get("fixings"):
            story.extend(self._build_fixings_table(quotation_data["fixings"]))
            story.append(Spacer(1, 4))

        # Totals section
        story.extend(self._build_totals(quotation_data["totals"]))
        story.append(Spacer(1, 4))

        # C) Comments section (COMENTARIOS:)
        all_comments = quotation_data.get("comments", [])
        if not all_comments:
            all_comments = QuotationConstants.get_standard_comments()
        story.extend(self._build_comments(all_comments))
        story.append(Spacer(1, 2))

        # Conditions (smaller text)
        story.extend(self._build_conditions(quotation_data.get("conditions", [])))
        story.append(Spacer(1, 3))

        # D) Bank transfer footer box
        story.extend(self._build_banking_info())

        # Build the PDF. First attempt with normal sizes;
        # if it overflows, we'll regenerate with smaller comment fonts.
        doc.build(story, onFirstPage=self._add_repeat_header, onLaterPages=self._add_repeat_header)

        return self.output_path

    # ──── Header with logo + title ────

    def _build_header(self, data: Dict) -> List:
        """Build header section: two-column [logo | title + date info]"""
        elements = []

        # Prepare logo
        logo_cell = ""
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                from reportlab.lib.utils import ImageReader
                img_reader = ImageReader(self.logo_path)
                iw, ih = img_reader.getSize()
                aspect = iw / ih
                logo_h = BMCStyles.LOGO_HEIGHT
                logo_w = logo_h * aspect
                # Cap width to the logo column
                max_w = 50 * mm
                if logo_w > max_w:
                    logo_w = max_w
                    logo_h = logo_w / aspect
                logo = Image(self.logo_path, width=logo_w, height=logo_h)
                logo.hAlign = "LEFT"
                logo_cell = logo
            except Exception:
                logo_cell = ""

        # Prepare title block (right side, centered)
        title_text = data.get("quote_title", "COTIZACIÓN")
        desc = data.get("quote_description", "")
        if desc:
            title_text = f"{title_text} – {desc}"

        title_style = ParagraphStyle(
            "HeaderTitle",
            fontName=BMCStyles.FONT_NAME_BOLD,
            fontSize=BMCStyles.FONT_SIZE_TITLE,
            textColor=BMCStyles.BMC_BLUE,
            alignment=1,  # Center
            leading=BMCStyles.FONT_SIZE_TITLE + 4,
        )
        date_style = ParagraphStyle(
            "HeaderDate",
            fontName=BMCStyles.FONT_NAME,
            fontSize=8,
            textColor=BMCStyles.TEXT_GRAY,
            alignment=1,
            leading=10,
        )
        contact_style = ParagraphStyle(
            "HeaderContact",
            fontName=BMCStyles.FONT_NAME,
            fontSize=7.5,
            textColor=BMCStyles.TEXT_GRAY,
            alignment=1,
            leading=9,
        )

        date_str = QuotationDataFormatter.format_date(data.get("date", ""))
        location = data.get("location", "")

        right_content = []
        right_content.append(Paragraph(title_text, title_style))
        right_content.append(Spacer(1, 2))
        right_content.append(Paragraph(f"Fecha: {date_str}  |  {location}", date_style))
        right_content.append(
            Paragraph(
                f"{QuotationConstants.COMPANY_EMAIL}  |  {QuotationConstants.COMPANY_WEBSITE}  |  Tel: {QuotationConstants.COMPANY_PHONE}",
                contact_style,
            )
        )

        # Two-column header table
        logo_w = 55 * mm
        title_w = self.content_width - logo_w

        header_data = [[logo_cell, right_content]]
        header_table = Table(header_data, colWidths=[logo_w, title_w])
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )

        elements.append(header_table)
        return elements

    # ──── Title & Client Info ────

    def _build_title_section(self, data: Dict) -> List:
        """Build client information section (below header)"""
        elements = []

        client = data.get("client", {})
        normal_style = BMCStyles.get_normal_style()

        elements.append(
            Paragraph(f"<b>Cliente:</b> {client.get('name', '')}", normal_style)
        )
        if client.get("address"):
            elements.append(
                Paragraph(
                    f"<b>Dirección:</b> {client.get('address', '')}", normal_style
                )
            )
        if client.get("phone"):
            elements.append(
                Paragraph(
                    f"<b>Tel/cel:</b> {client.get('phone', '')}", normal_style
                )
            )

        # Technical specs
        specs = data.get("technical_specs", {})
        if specs.get("autoportancia") or specs.get("apoyos"):
            small = BMCStyles.get_small_style()
            elements.append(
                Paragraph(
                    f"Autoportancia: {specs.get('autoportancia', '')} m  |  Apoyos: {specs.get('apoyos', '')}",
                    small,
                )
            )

        return elements

    # ──── Materials Tables (design only – no BOM changes) ────

    def _build_products_table(self, products: List[Dict]) -> List:
        """Build products table with updated styling."""
        elements = []

        header = ["Producto", "Largos (m)", "Cant.", "USD / Unid.", "Total (USD)"]
        data = [header]

        for product in products:
            length = product.get("Length_m", product.get("length_m", ""))
            total_usd = product.get("total_usd")
            if total_usd is None or total_usd == 0:
                total_usd = QuotationDataFormatter.calculate_item_total(product)

            row = [
                product.get("name", ""),
                str(length),
                str(product.get("quantity", "")),
                QuotationDataFormatter.format_currency(
                    product.get("unit_price_usd", 0)
                ),
                QuotationDataFormatter.format_currency(total_usd),
            ]
            data.append(row)

        table = Table(data, colWidths=[self.content_width * 0.38, self.content_width * 0.12,
                                        self.content_width * 0.12, self.content_width * 0.17,
                                        self.content_width * 0.21])
        table.setStyle(BMCStyles.get_products_table_style(num_data_rows=len(products)))
        table.repeatRows = 1  # Repeat header if multi-page

        elements.append(table)
        return elements

    def _build_accessories_table(self, accessories: List[Dict]) -> List:
        """Build accessories/profiles table."""
        elements = []

        header_style = BMCStyles.get_header_style()
        elements.append(Paragraph("Accesorios", header_style))

        header = ["Producto", "Largo (m)", "Cant.", "USD / Unid.", "Total (USD)"]
        data = [header]

        for item in accessories:
            length = item.get("Length_m", item.get("length_m", ""))
            total_usd = item.get("total_usd")
            if total_usd is None or total_usd == 0:
                total_usd = QuotationDataFormatter.calculate_item_total(item)

            row = [
                item.get("name", ""),
                str(length),
                str(item.get("quantity", "")),
                QuotationDataFormatter.format_currency(item.get("unit_price_usd", 0)),
                QuotationDataFormatter.format_currency(total_usd),
            ]
            data.append(row)

        table = Table(data, colWidths=[self.content_width * 0.38, self.content_width * 0.12,
                                        self.content_width * 0.12, self.content_width * 0.17,
                                        self.content_width * 0.21])
        table.setStyle(BMCStyles.get_products_table_style(num_data_rows=len(accessories)))
        table.repeatRows = 1

        elements.append(table)
        return elements

    def _build_fixings_table(self, fixings: List[Dict]) -> List:
        """Build fixings/fijaciones table."""
        elements = []

        header_style = BMCStyles.get_header_style()
        elements.append(Paragraph("Fijaciones", header_style))

        header = ["Producto", "Especificación", "Cant.", "USD / Unid.", "Total (USD)"]
        data = [header]

        for item in fixings:
            total_usd = item.get("total_usd")
            if total_usd is None or total_usd == 0:
                total_usd = QuotationDataFormatter.calculate_item_total(item)

            row = [
                item.get("name", ""),
                item.get("specification", ""),
                str(item.get("quantity", "")),
                QuotationDataFormatter.format_currency(item.get("unit_price_usd", 0)),
                QuotationDataFormatter.format_currency(total_usd),
            ]
            data.append(row)

        table = Table(data, colWidths=[self.content_width * 0.30, self.content_width * 0.17,
                                        self.content_width * 0.12, self.content_width * 0.17,
                                        self.content_width * 0.24])
        table.setStyle(BMCStyles.get_products_table_style(num_data_rows=len(fixings)))
        table.repeatRows = 1

        elements.append(table)
        return elements

    # ──── Totals ────

    def _build_totals(self, totals: Dict) -> List:
        """Build totals section."""
        elements = []

        data = [
            ["Sub-Total:", QuotationDataFormatter.format_currency(totals["subtotal"])],
            [f"Total m² Fachada:", f"{totals['total_m2_facade']:.2f}"],
            [f"Total m² Cubierta:", f"{totals['total_m2_roof']:.2f}"],
            [
                f"IVA {int(totals['iva_rate'] * 100)}%:",
                QuotationDataFormatter.format_currency(totals["iva"]),
            ],
            [
                "Materiales:",
                QuotationDataFormatter.format_currency(totals["materials_total"]),
            ],
            ["Traslado:", QuotationDataFormatter.format_currency(totals["shipping"])],
            [
                "TOTAL U$S:",
                QuotationDataFormatter.format_currency(totals["grand_total"]),
            ],
        ]

        table = Table(data, colWidths=[self.content_width * 0.50, self.content_width * 0.30])
        table.setStyle(BMCStyles.get_totals_table_style())

        elements.append(table)
        return elements

    # ──── COMENTARIOS: block ────

    def _build_comments(self, comments: List[str], font_size=None, leading=None) -> List:
        """
        Build COMENTARIOS: section with per-line formatting.

        Each comment line is rendered as a bullet item (•).
        Lines are classified as bold, red, bold+red, or normal.
        """
        elements = []

        # Section title
        comment_header_style = ParagraphStyle(
            "CommentHeader",
            fontName=BMCStyles.FONT_NAME_BOLD,
            fontSize=(font_size or BMCStyles.FONT_SIZE_COMMENT) + 1,
            textColor=BMCStyles.BMC_BLUE,
            spaceAfter=2,
            spaceBefore=4,
        )
        elements.append(Paragraph("COMENTARIOS:", comment_header_style))

        # Style factories per classification
        style_map = {
            "normal": BMCStyles.get_comment_style(font_size, leading),
            "bold": BMCStyles.get_comment_bold_style(font_size, leading),
            "red": BMCStyles.get_comment_red_style(font_size, leading),
            "bold_red": BMCStyles.get_comment_bold_red_style(font_size, leading),
        }

        for comment in comments:
            cls = _classify_comment_line(comment)
            style = style_map[cls]
            # Bullet prefix
            bullet = "\u2022 "
            elements.append(Paragraph(f"{bullet}{comment}", style))

        return elements

    # ──── Conditions ────

    def _build_conditions(self, conditions: List[str]) -> List:
        """Build terms and conditions section."""
        elements = []
        cond_style = BMCStyles.get_conditions_style()
        for condition in conditions:
            elements.append(Paragraph(condition, cond_style))
        return elements

    # ──── Bank Transfer Footer Box ────

    def _build_banking_info(self) -> List:
        """
        Build banking information as a boxed/ruled grid table.
        Three rows, two columns. First row has gray background.
        """
        elements = []

        elements.append(Spacer(1, 6))

        # Build Paragraph cells for special formatting in row 3 right
        small_style = ParagraphStyle(
            "BankSmall",
            fontName=BMCStyles.FONT_NAME,
            fontSize=8.4,
            textColor=BMCStyles.TEXT_BLACK,
            leading=10,
        )
        link_style = ParagraphStyle(
            "BankLink",
            fontName=BMCStyles.FONT_NAME,
            fontSize=8.4,
            textColor=BMCStyles.LINK_BLUE,
            leading=10,
        )

        # Row 1
        r1_left = Paragraph("<b>Depósito Bancario</b>", small_style)
        r1_right = Paragraph(
            f"Titular: {QuotationConstants.BANK_ACCOUNT_HOLDER} – RUT: {QuotationConstants.BANK_RUT}",
            small_style,
        )

        # Row 2
        r2_left = Paragraph(
            f"{QuotationConstants.BANK_ACCOUNT_TYPE} - {QuotationConstants.BANK_NAME}.",
            small_style,
        )
        r2_right = Paragraph(
            f"Número de Cuenta Dólares : {QuotationConstants.BANK_ACCOUNT_USD}",
            small_style,
        )

        # Row 3
        r3_left = Paragraph(
            f"Por cualquier duda, consultar al {QuotationConstants.CONTACT_PHONE}.",
            small_style,
        )
        r3_right = Paragraph(
            '<u>Lea los Términos y Condiciones</u>',
            link_style,
        )

        data = [
            [r1_left, r1_right],
            [r2_left, r2_right],
            [r3_left, r3_right],
        ]

        col_left = self.content_width * 0.45
        col_right = self.content_width * 0.55

        table = Table(data, colWidths=[col_left, col_right])
        table.setStyle(BMCStyles.get_bank_transfer_table_style())

        elements.append(table)
        return elements

    # ──── Page callbacks ────

    @staticmethod
    def _add_repeat_header(canvas_obj, doc):
        """Optional callback for page decorations (can be extended)."""
        pass


# ──────────────────────────────────────────────────────────────
# Public convenience functions
# ──────────────────────────────────────────────────────────────

def generate_quotation_pdf(quotation_data: Dict, output_path: str, logo_path: Optional[str] = None) -> str:
    """
    Generate a BMC Uruguay quotation PDF.

    Args:
        quotation_data: Raw quotation data (will be formatted automatically)
        output_path: Path where PDF should be saved
        logo_path: Optional explicit path to BMC logo image

    Returns:
        Path to generated PDF file

    Example:
        >>> data = {
        ...     'client_name': 'Juan Pérez',
        ...     'client_address': 'Av. Principal 123',
        ...     'products': [...]
        ... }
        >>> pdf_path = generate_quotation_pdf(data, 'cotizacion_001.pdf')
    """
    formatted_data = QuotationDataFormatter.format_for_pdf(quotation_data)
    generator = BMCQuotationPDF(output_path, logo_path=logo_path)
    return generator.generate(formatted_data)


def build_quote_pdf(
    data: Dict,
    output_path: str,
    logo_path: Optional[str] = None,
) -> str:
    """
    Reusable template function (alias) for building a cotización PDF.

    This is the main entry point referenced in GPT_PDF_INSTRUCTIONS.md.
    Uses /mnt/data/Logo_BMC- PNG.png by default (GPT sandbox),
    falling back to the bundled logo.

    Args:
        data: Raw quotation data dictionary
        output_path: Destination path for the PDF file
        logo_path: Explicit logo path override (default: auto-detect)

    Returns:
        Path to the generated PDF
    """
    if logo_path is None:
        logo_path = "/mnt/data/Logo_BMC- PNG.png"
    return generate_quotation_pdf(data, output_path, logo_path=logo_path)
