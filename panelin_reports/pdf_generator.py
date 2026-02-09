#!/usr/bin/env python3
"""
BMC Uruguay Quotation PDF Generator
====================================

Generates professional quotation PDFs matching the exact structure
and branding of BMC Uruguay's standard quotation template.

Updated: 2026-02-09
- Official BMC logo header (two-column: logo | centered title)
- Materials table with alternating rows, thin grid, right-aligned numerics
- COMENTARIOS: section with per-line bold/red formatting
- Bank transfer footer boxed grid
- 1-page-first rule: shrink comments font/leading before altering table

Based on: Cotización 01042025 BASE - Isopanel xx mm - Isodec EPS xx mm -desc- WA.ods
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
    Table,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
    SimpleDocTemplate,
    TableStyle,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader

from .pdf_styles import BMCStyles, QuotationConstants


# ---------------------------------------------------------------------------
# Data Formatter (unchanged BOM/pricing logic)
# ---------------------------------------------------------------------------

class QuotationDataFormatter:
    """Formats raw quotation data into PDF-ready structure"""

    @staticmethod
    def format_for_pdf(raw_data: Dict) -> Dict:
        """
        Transform raw quotation data into structured PDF format

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
        Calculate item total based on unit_base

        Logic (2026-01-28 correction):
        - unit_base = 'unidad': quantity × sale_sin_iva
        - unit_base = 'ml': quantity × Length_m × sale_sin_iva
        - unit_base = 'm²': total_m2 × sale_sin_iva

        Args:
            item: Dict with quantity, unit_base, sale_sin_iva, Length_m (optional)

        Returns:
            float: Calculated total
        """
        unit_base = item.get("unit_base", "unidad").lower()

        # Use sale_sin_iva if available, fallback to unit_price_usd
        price = item.get("sale_sin_iva", item.get("unit_price_usd", 0))

        if unit_base == "unidad":
            # Direct quantity
            return item.get("quantity", 0) * price

        elif unit_base == "ml":
            # Linear meters: pieces × length per piece
            quantity = item.get("quantity", 0)
            length_m = item.get("Length_m", item.get("length_m", 0))
            return quantity * length_m * price

        elif unit_base == "m²" or unit_base == "m2":
            # Square meters: total area
            total_m2 = item.get("total_m2", 0)
            return total_m2 * price

        else:
            # Fallback to quantity × price
            return item.get("quantity", 0) * price

    @staticmethod
    def calculate_totals(
        products: List[Dict],
        accessories: List[Dict],
        fixings: List[Dict],
        shipping_usd: Optional[float] = None,
    ) -> Dict:
        """
        Calculate all financial totals for the quotation.

        LEDGER: Item totals are sin IVA (from sale_sin_iva / unit_price_usd).
        subtotal = sum of items; IVA = subtotal × rate; materials = subtotal + IVA.

        Args:
            products: List of product items
            accessories: List of accessory items
            fixings: List of fixing items
            shipping_usd: Shipping cost (defaults to standard)

        Returns:
            Dictionary with all calculated totals
        """
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

        # Total from all items (calculated without IVA)
        subtotal = products_total + accessories_total + fixings_total

        # Calculate IVA from the subtotal
        iva = subtotal * QuotationConstants.IVA_RATE

        # Materials total is subtotal + IVA
        materials_total = subtotal + iva

        # Shipping
        shipping = (
            shipping_usd
            if shipping_usd is not None
            else QuotationConstants.DEFAULT_SHIPPING_USD
        )

        # Grand total
        grand_total = materials_total + shipping

        # Calculate total m² for facade and roof
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


# ---------------------------------------------------------------------------
# Comment formatting helpers
# ---------------------------------------------------------------------------

def _classify_comment_line(line: str) -> str:
    """
    Determine the formatting rule for a comment line.

    Returns one of: 'bold', 'red', 'bold_red', 'normal'
    """
    rules = QuotationConstants.COMMENT_FORMAT_RULES
    stripped = line.strip()
    for entry in rules.get("bold_red", []):
        if stripped == entry.strip():
            return "bold_red"
    for entry in rules.get("bold", []):
        if stripped == entry.strip():
            return "bold"
    for entry in rules.get("red", []):
        if stripped == entry.strip():
            return "red"
    return "normal"


# ---------------------------------------------------------------------------
# Main PDF Generator
# ---------------------------------------------------------------------------

class BMCQuotationPDF:
    """
    Main PDF generator for BMC Uruguay quotations.
    Replicates exact structure from ODS template with new design:
    - Two-column header (logo | centered title)
    - Styled materials table
    - COMENTARIOS section with per-line formatting
    - Bank transfer footer boxed grid
    - 1-page-first rule
    """

    def __init__(self, output_path: str, logo_path: str = None):
        """
        Initialize PDF generator

        Args:
            output_path: Path where PDF will be saved
            logo_path: Optional custom logo path (defaults to BMC logo search)
        """
        self.output_path = output_path
        self.styles = BMCStyles()
        self.constants = QuotationConstants()
        self.logo_path = BMCStyles.get_logo_path(logo_path)

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def generate(self, quotation_data: Dict) -> str:
        """
        Generate complete quotation PDF

        Args:
            quotation_data: Formatted quotation data dictionary

        Returns:
            Path to generated PDF file
        """
        # Create PDF document
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=BMCStyles.PAGE_SIZE,
            topMargin=BMCStyles.MARGIN_TOP,
            bottomMargin=BMCStyles.MARGIN_BOTTOM,
            leftMargin=BMCStyles.MARGIN_LEFT,
            rightMargin=BMCStyles.MARGIN_RIGHT,
        )

        # Build document elements
        story = self._build_story(quotation_data)

        # Build PDF with repeatRows for multi-page table headers
        doc.build(story)

        return self.output_path

    def _build_story(self, data: Dict, comment_font_size=None, comment_leading=None):
        """Build the full story (list of flowables) for the PDF."""
        story = []

        # Header section (logo + centered title)
        story.extend(self._build_header(data))
        story.append(Spacer(1, 8))

        # Client info
        story.extend(self._build_client_info(data))
        story.append(Spacer(1, 8))

        # Products table
        if data.get("products"):
            story.extend(self._build_products_table(data["products"]))
            story.append(Spacer(1, 6))

        # Accessories table
        if data.get("accessories"):
            story.extend(self._build_accessories_table(data["accessories"]))
            story.append(Spacer(1, 6))

        # Fixings table
        if data.get("fixings"):
            story.extend(self._build_fixings_table(data["fixings"]))
            story.append(Spacer(1, 6))

        # Totals section
        story.extend(self._build_totals(data["totals"]))
        story.append(Spacer(1, 8))

        # COMENTARIOS section (with per-line formatting)
        comments = data.get("comments", [])
        if not comments:
            comments = QuotationConstants.STANDARD_COMMENTS
        story.extend(
            self._build_comments(comments, comment_font_size, comment_leading)
        )
        story.append(Spacer(1, 6))

        # Bank transfer footer box
        story.extend(self._build_bank_transfer_footer())

        return story

    # ------------------------------------------------------------------
    # A) HEADER / BRANDING
    # ------------------------------------------------------------------

    def _build_header(self, data: Dict) -> List:
        """
        Build header section with two-column layout:
        [Logo (left) | Centered title (right)]
        Logo height ~18mm, auto-width keeping aspect ratio.
        """
        elements = []

        # Determine available width
        avail_width = BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_LEFT - BMCStyles.MARGIN_RIGHT

        # Build title text
        title_text = data.get("quote_title", "Cotización")
        desc = data.get("quote_description", "")
        if desc:
            title_text = f"{title_text} – {desc}"

        title_style = BMCStyles.get_title_style()
        title_para = Paragraph(title_text, title_style)

        # Date line
        date_str = QuotationDataFormatter.format_date(data.get("date", ""))
        location = data.get("location", "")
        date_text = f"Fecha: {date_str}"
        if location:
            date_text += f"  |  {location}"
        date_style = BMCStyles.get_small_style()
        date_para = Paragraph(date_text, date_style)

        if self.logo_path and os.path.exists(self.logo_path):
            # Calculate logo dimensions maintaining aspect ratio
            try:
                img_reader = ImageReader(self.logo_path)
                iw, ih = img_reader.getSize()
                aspect = iw / ih
                logo_height = 18 * mm
                logo_width = logo_height * aspect
                # Cap logo width to avoid overflow
                max_logo_width = avail_width * 0.35
                if logo_width > max_logo_width:
                    logo_width = max_logo_width
                    logo_height = logo_width / aspect

                logo = Image(self.logo_path, width=logo_width, height=logo_height)
            except Exception:
                logo = None
                logo_width = 0
        else:
            logo = None
            logo_width = 0

        if logo:
            # Two-column header table: [logo | title + date]
            title_col_width = avail_width - logo_width - 10
            header_data = [
                [
                    logo,
                    [title_para, Spacer(1, 2), date_para],
                ]
            ]
            header_table = Table(
                header_data,
                colWidths=[logo_width + 5, title_col_width],
            )
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
        else:
            # Fallback: just title centered + date
            elements.append(title_para)
            elements.append(date_para)

        # Company contact line (small, below header)
        contact_style = BMCStyles.get_small_style()
        contact_text = (
            f"{QuotationConstants.COMPANY_EMAIL}  |  "
            f"{QuotationConstants.COMPANY_WEBSITE}  |  "
            f"Tel: {QuotationConstants.COMPANY_PHONE}"
        )
        elements.append(Spacer(1, 3))
        elements.append(Paragraph(contact_text, contact_style))

        return elements

    # ------------------------------------------------------------------
    # Client info
    # ------------------------------------------------------------------

    def _build_client_info(self, data: Dict) -> List:
        """Build client information section"""
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

        # Technical specs (autoportancia, apoyos) - compact
        specs = data.get("technical_specs", {})
        if specs:
            spec_style = BMCStyles.get_small_style()
            spec_text = (
                f"Autoportancia: {specs.get('autoportancia', 0)} m  |  "
                f"Apoyos: {specs.get('apoyos', 0)}"
            )
            elements.append(Paragraph(spec_text, spec_style))

        return elements

    # ------------------------------------------------------------------
    # C) MATERIALS TABLE (DESIGN ONLY - no BOM logic changes)
    # ------------------------------------------------------------------

    def _build_products_table(self, products: List[Dict]) -> List:
        """Build products table with new styling"""
        elements = []

        # Table header
        header = [
            "Producto",
            "Largos (m)",
            "Cant.",
            "Costo m² (USD)",
            "Costo Total (USD)",
        ]

        # Table data
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

        # Create table with repeating header for multi-page
        table = Table(data, colWidths=[170, 55, 40, 80, 100], repeatRows=1)
        table.setStyle(BMCStyles.get_products_table_style(num_data_rows=len(products)))

        elements.append(table)
        return elements

    def _build_accessories_table(self, accessories: List[Dict]) -> List:
        """Build accessories/profiles table"""
        elements = []

        header_style = BMCStyles.get_header_style()
        elements.append(Paragraph("Accesorios", header_style))

        header = [
            "Producto",
            "Largo (m)",
            "Cant.",
            "Costo lineal (USD)",
            "Costo Total (USD)",
        ]
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

        table = Table(data, colWidths=[170, 55, 40, 80, 100], repeatRows=1)
        table.setStyle(
            BMCStyles.get_products_table_style(num_data_rows=len(accessories))
        )

        elements.append(table)
        return elements

    def _build_fixings_table(self, fixings: List[Dict]) -> List:
        """Build fixings/fijaciones table"""
        elements = []

        header_style = BMCStyles.get_header_style()
        elements.append(Paragraph("Fijaciones", header_style))

        header = [
            "Producto",
            "Especificación",
            "Cant.",
            "Costo unit. (USD)",
            "Costo Total (USD)",
        ]
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

        table = Table(data, colWidths=[140, 70, 40, 80, 100], repeatRows=1)
        table.setStyle(
            BMCStyles.get_products_table_style(num_data_rows=len(fixings))
        )

        elements.append(table)
        return elements

    # ------------------------------------------------------------------
    # Totals (unchanged pricing logic)
    # ------------------------------------------------------------------

    def _build_totals(self, totals: Dict) -> List:
        """Build totals section"""
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

        table = Table(data, colWidths=[200, 120])
        table.setStyle(BMCStyles.get_totals_table_style())

        elements.append(table)
        return elements

    # ------------------------------------------------------------------
    # D) COMENTARIOS: BLOCK
    # ------------------------------------------------------------------

    def _build_comments(
        self,
        comments: List[str],
        font_size: float = None,
        leading: float = None,
    ) -> List:
        """
        Build COMENTARIOS section with per-line formatting:
        - Bold lines
        - Red lines
        - Bold + Red lines
        - Normal lines (small font with bullet •)
        """
        elements = []

        # Section title
        title_style = BMCStyles.get_comment_title_style()
        elements.append(Paragraph("COMENTARIOS:", title_style))

        # Prepare styles for each formatting variant
        style_normal = BMCStyles.get_comment_style(font_size, leading)
        style_bold = BMCStyles.get_comment_bold_style(font_size, leading)
        style_red = BMCStyles.get_comment_red_style(font_size, leading)
        style_bold_red = BMCStyles.get_comment_bold_red_style(font_size, leading)

        for comment in comments:
            fmt = _classify_comment_line(comment)
            bullet = "\u2022 "  # bullet character •
            text = f"{bullet}{comment}"

            if fmt == "bold":
                elements.append(Paragraph(text, style_bold))
            elif fmt == "red":
                elements.append(Paragraph(text, style_red))
            elif fmt == "bold_red":
                elements.append(Paragraph(text, style_bold_red))
            else:
                elements.append(Paragraph(text, style_normal))

        return elements

    # ------------------------------------------------------------------
    # Conditions (kept for backward compat, but comments is now primary)
    # ------------------------------------------------------------------

    def _build_conditions(self, conditions: List[str]) -> List:
        """Build terms and conditions section"""
        elements = []

        conditions_style = BMCStyles.get_conditions_style()

        for condition in conditions:
            elements.append(Paragraph(condition, conditions_style))

        return elements

    # ------------------------------------------------------------------
    # E) FOOTER: BANK TRANSFER BOX
    # ------------------------------------------------------------------

    def _build_bank_transfer_footer(self) -> List:
        """
        Build bank transfer footer as a boxed/ruled table matching
        the reference image style:
        - Grid/box lines visible (outer border + internal row lines)
        - First row background light gray
        - 3 rows with left/right content
        """
        elements = []

        # Available width for the footer table
        avail_width = (
            BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_LEFT - BMCStyles.MARGIN_RIGHT
        )
        col_left = avail_width * 0.40
        col_right = avail_width * 0.60

        # Build row data - EXACT text per spec
        footer_data = [
            # Row 1
            [
                "Depósito Bancario",
                f"Titular: {QuotationConstants.BANK_ACCOUNT_HOLDER} – RUT: {QuotationConstants.BANK_RUT}",
            ],
            # Row 2
            [
                f"{QuotationConstants.BANK_ACCOUNT_TYPE} - {QuotationConstants.BANK_NAME}.",
                f"Número de Cuenta Dólares : {QuotationConstants.BANK_ACCOUNT_USD}",
            ],
            # Row 3
            [
                f"Por cualquier duda, consultar al {QuotationConstants.CONTACT_PHONE}.",
                # Blue + underlined "Lea los Términos y Condiciones"
                '<font color="#0066CC"><u>Lea los Términos y Condiciones</u></font>',
            ],
        ]

        # Use Paragraph for last row right cell to support markup
        footer_style_normal = ParagraphStyle(
            "FooterNormal",
            fontName=BMCStyles.FONT_NAME,
            fontSize=BMCStyles.FONT_SIZE_FOOTER,
            textColor=BMCStyles.TEXT_BLACK,
            leading=BMCStyles.FONT_SIZE_FOOTER + 2,
        )
        footer_style_bold = ParagraphStyle(
            "FooterBold",
            fontName=BMCStyles.FONT_NAME_BOLD,
            fontSize=BMCStyles.FONT_SIZE_FOOTER,
            textColor=BMCStyles.TEXT_BLACK,
            leading=BMCStyles.FONT_SIZE_FOOTER + 2,
        )
        footer_style_link = ParagraphStyle(
            "FooterLink",
            fontName=BMCStyles.FONT_NAME,
            fontSize=BMCStyles.FONT_SIZE_FOOTER,
            textColor=BMCStyles.LINK_BLUE,
            leading=BMCStyles.FONT_SIZE_FOOTER + 2,
        )

        # Convert to Paragraphs for rich text support
        table_data = [
            [
                Paragraph(footer_data[0][0], footer_style_bold),
                Paragraph(footer_data[0][1], footer_style_normal),
            ],
            [
                Paragraph(footer_data[1][0], footer_style_bold),
                Paragraph(footer_data[1][1], footer_style_normal),
            ],
            [
                Paragraph(footer_data[2][0], footer_style_bold),
                Paragraph(footer_data[2][1], footer_style_link),
            ],
        ]

        footer_table = Table(
            table_data,
            colWidths=[col_left, col_right],
        )
        footer_table.setStyle(BMCStyles.get_footer_bank_table_style())

        elements.append(footer_table)
        return elements


# ---------------------------------------------------------------------------
# Convenience / entry-point functions
# ---------------------------------------------------------------------------

def generate_quotation_pdf(
    quotation_data: Dict,
    output_path: str,
    logo_path: str = "/mnt/data/Logo_BMC- PNG.png",
) -> str:
    """
    Generate a BMC Uruguay quotation PDF

    Args:
        quotation_data: Raw quotation data (will be formatted automatically)
        output_path: Path where PDF should be saved
        logo_path: Path to BMC logo file

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
    # Format data for PDF
    formatted_data = QuotationDataFormatter.format_for_pdf(quotation_data)

    # Generate PDF
    generator = BMCQuotationPDF(output_path, logo_path=logo_path)
    return generator.generate(formatted_data)


def build_quote_pdf(
    data: Dict,
    output_path: str,
    logo_path: str = "/mnt/data/Logo_BMC- PNG.png",
) -> str:
    """
    Reusable template function for building a BMC cotización PDF.
    This is the recommended entry point.

    Args:
        data: Raw quotation data dict
        output_path: Where to write the PDF
        logo_path: Path to BMC logo image

    Returns:
        Path to the generated PDF file
    """
    return generate_quotation_pdf(data, output_path, logo_path=logo_path)
