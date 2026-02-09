#!/usr/bin/env python3
"""
BMC Uruguay Quotation PDF Generator
====================================

Generates professional quotation PDFs matching the exact structure
and branding of BMC Uruguay's standard quotation template.

Design update (2026-02-09):
- Two-column header: [BMC logo | centered title]
- Materials table with #EDEDED header, alternating rows, right-aligned numerics
- COMENTARIOS: section with bullet list + per-line bold/red formatting
- Bank transfer footer as boxed/ruled table
- 1-page-first: shrink comments font/leading before altering table

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
# Data formatter (NO CHANGES to BOM / pricing logic)
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


# ---------------------------------------------------------------------------
# Comment line formatting helper
# ---------------------------------------------------------------------------

def _resolve_comment_style(text: str, style_hint: Optional[str] = None):
    """
    Determine the style key for a comment line.
    Returns one of: "normal", "bold", "red", "bold_red".
    """
    if style_hint and style_hint in ("normal", "bold", "red", "bold_red"):
        return style_hint

    # Auto-detect from COMMENT_FORMAT_RULES
    for phrase, skey in QuotationConstants.COMMENT_FORMAT_RULES.items():
        if phrase in text:
            return skey
    return "normal"


def _get_style_for_key(key: str, font_size=None, leading=None):
    """Return the ParagraphStyle matching the style key."""
    mapping = {
        "normal": BMCStyles.get_comment_normal_style,
        "bold": BMCStyles.get_comment_bold_style,
        "red": BMCStyles.get_comment_red_style,
        "bold_red": BMCStyles.get_comment_bold_red_style,
    }
    fn = mapping.get(key, mapping["normal"])
    return fn(font_size=font_size, leading=leading)


# ---------------------------------------------------------------------------
# PDF Generator
# ---------------------------------------------------------------------------

class BMCQuotationPDF:
    """
    Main PDF generator for BMC Uruguay quotations.
    Replicates exact structure from ODS template with updated design.
    """

    def __init__(self, output_path: str, logo_path: Optional[str] = None):
        """
        Initialize PDF generator

        Args:
            output_path: Path where PDF will be saved
            logo_path: Explicit logo path override (optional)
        """
        self.output_path = output_path
        self.styles = BMCStyles()
        self.constants = QuotationConstants()
        self.logo_path = logo_path or BMCStyles.resolve_logo_path()

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
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=BMCStyles.PAGE_SIZE,
            topMargin=BMCStyles.MARGIN_TOP,
            bottomMargin=BMCStyles.MARGIN_BOTTOM,
            leftMargin=BMCStyles.MARGIN_LEFT,
            rightMargin=BMCStyles.MARGIN_RIGHT,
        )

        story = self._build_story(quotation_data)

        # Build with repeat-header callback for multi-page tables
        doc.build(story)

        return self.output_path

    # ------------------------------------------------------------------
    def _build_story(self, data: Dict) -> List:
        """Assemble the full document story."""
        story = []

        # A) HEADER – two-column: [logo | centred title]
        story.extend(self._build_header(data))
        story.append(Spacer(1, 6))

        # Client info
        story.extend(self._build_client_section(data))
        story.append(Spacer(1, 8))

        # C) MATERIALS TABLES (design only – no data changes)
        if data.get("products"):
            story.extend(self._build_products_table(data["products"]))
            story.append(Spacer(1, 8))

        if data.get("accessories"):
            story.extend(self._build_accessories_table(data["accessories"]))
            story.append(Spacer(1, 8))

        if data.get("fixings"):
            story.extend(self._build_fixings_table(data["fixings"]))
            story.append(Spacer(1, 8))

        # Totals
        story.extend(self._build_totals(data["totals"]))
        story.append(Spacer(1, 8))

        # D) COMENTARIOS block
        comments = data.get("comments", [])
        story.extend(self._build_comments(comments))
        story.append(Spacer(1, 6))

        # E) FOOTER – bank transfer box
        story.extend(self._build_bank_transfer_box())

        return story

    # ==================================================================
    # A) HEADER
    # ==================================================================
    def _build_header(self, data: Dict) -> List:
        """
        Build two-column header: [logo | centred title].
        Below: date, location, technical specs.
        """
        elements = []
        usable_width = BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_LEFT - BMCStyles.MARGIN_RIGHT

        # -- Build title text --
        title_text = data.get("quote_title", "COTIZACIÓN")
        desc = data.get("quote_description", "")
        if desc:
            title_text = f"{title_text} – {desc}"

        title_style = BMCStyles.get_title_style()
        title_para = Paragraph(title_text, title_style)

        # -- Build logo or placeholder --
        logo_cell = ""
        logo_col_width = 45 * mm
        if self.logo_path and os.path.isfile(self.logo_path):
            try:
                img = Image(self.logo_path)
                # Scale to height 18mm, keep aspect ratio
                iw, ih = img.drawWidth, img.drawHeight
                scale = (BMCStyles.LOGO_HEIGHT) / ih
                img.drawWidth = iw * scale
                img.drawHeight = ih * scale
                logo_col_width = img.drawWidth + 4 * mm
                logo_cell = img
            except Exception:
                logo_cell = ""

        title_col_width = usable_width - logo_col_width

        header_data = [[logo_cell, title_para]]
        header_table = Table(
            header_data,
            colWidths=[logo_col_width, title_col_width],
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

        # Sub-header: date, location, contact, specs
        contact_style = BMCStyles.get_small_style()
        elements.append(Spacer(1, 4))

        # Date / location line
        date_str = QuotationDataFormatter.format_date(data.get("date", ""))
        loc = data.get("location", "")
        elements.append(
            Paragraph(
                f"Fecha: {date_str} &nbsp;&nbsp;&nbsp; {loc}",
                contact_style,
            )
        )

        # Company contact
        elements.append(
            Paragraph(
                f"{QuotationConstants.COMPANY_EMAIL} | "
                f"{QuotationConstants.COMPANY_WEBSITE} | "
                f"Tel: {QuotationConstants.COMPANY_PHONE}",
                contact_style,
            )
        )

        # Technical specs
        specs = data.get("technical_specs", {})
        if specs:
            elements.append(
                Paragraph(
                    f"Autoportancia: {specs.get('autoportancia', 0)} m &nbsp;&nbsp; "
                    f"Apoyos: {specs.get('apoyos', 0)}",
                    contact_style,
                )
            )

        return elements

    # ==================================================================
    # Client info
    # ==================================================================
    def _build_client_section(self, data: Dict) -> List:
        """Build client information block."""
        elements = []
        client = data.get("client", {})
        ns = BMCStyles.get_normal_style()

        elements.append(
            Paragraph(f"<b>Cliente:</b> {client.get('name', '')}", ns)
        )
        if client.get("address"):
            elements.append(
                Paragraph(f"<b>Dirección:</b> {client.get('address', '')}", ns)
            )
        if client.get("phone"):
            elements.append(
                Paragraph(f"<b>Tel/cel:</b> {client.get('phone', '')}", ns)
            )

        return elements

    # ==================================================================
    # C) MATERIALS TABLES (design-only changes)
    # ==================================================================
    def _build_products_table(self, products: List[Dict]) -> List:
        """Build products table with updated styling."""
        elements = []

        header = [
            "Producto",
            "Largos (m)",
            "Cantidades",
            "Costo m² (USD)",
            "Costo Total (USD)",
        ]

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

        table = Table(data, colWidths=[180, 55, 55, 80, 100], repeatRows=1)
        table.setStyle(BMCStyles.get_products_table_style(num_data_rows=len(products)))

        elements.append(table)
        return elements

    def _build_accessories_table(self, accessories: List[Dict]) -> List:
        """Build accessories/profiles table."""
        elements = []

        header_style = BMCStyles.get_header_style()
        elements.append(Paragraph("Accesorios", header_style))

        header = [
            "Producto",
            "Largo (m)",
            "Cantidades",
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

        table = Table(data, colWidths=[180, 55, 55, 80, 100], repeatRows=1)
        table.setStyle(BMCStyles.get_products_table_style(num_data_rows=len(accessories)))

        elements.append(table)
        return elements

    def _build_fixings_table(self, fixings: List[Dict]) -> List:
        """Build fixings/fijaciones table."""
        elements = []

        header_style = BMCStyles.get_header_style()
        elements.append(Paragraph("Fijaciones", header_style))

        header = [
            "Producto",
            "Especificación",
            "Cantidades",
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

        table = Table(data, colWidths=[140, 75, 55, 80, 100], repeatRows=1)
        table.setStyle(BMCStyles.get_products_table_style(num_data_rows=len(fixings)))

        elements.append(table)
        return elements

    # ==================================================================
    # Totals
    # ==================================================================
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

    # ==================================================================
    # D) COMENTARIOS block
    # ==================================================================
    def _build_comments(
        self,
        comments: List,
        font_size: Optional[float] = None,
        leading: Optional[float] = None,
    ) -> List:
        """
        Build COMENTARIOS section with bullet list and per-line formatting.

        ``comments`` may be:
        - A list of plain strings (auto-detect formatting)
        - A list of (text, style_key) tuples
        """
        elements = []

        header_style = BMCStyles.get_header_style()
        elements.append(Paragraph("COMENTARIOS:", header_style))

        fs = font_size or BMCStyles.COMMENT_FONT_SIZE
        ld = leading or BMCStyles.COMMENT_LEADING

        for entry in comments:
            # Support both plain strings and (text, style_hint) tuples
            if isinstance(entry, (list, tuple)) and len(entry) >= 2:
                text, hint = entry[0], entry[1]
            else:
                text, hint = str(entry), None

            style_key = _resolve_comment_style(text, hint)
            style = _get_style_for_key(style_key, font_size=fs, leading=ld)
            elements.append(Paragraph(f"• {text}", style))

        # Always append the standard formatted comments
        # (these are the fixed template lines from the spec)
        for text, skey in QuotationConstants.STANDARD_COMMENTS:
            # Skip if user already provided a comment with the same beginning
            already = any(
                (isinstance(c, str) and c.startswith(text[:30]))
                or (isinstance(c, (list, tuple)) and str(c[0]).startswith(text[:30]))
                for c in comments
            )
            if not already:
                style = _get_style_for_key(skey, font_size=fs, leading=ld)
                elements.append(Paragraph(f"• {text}", style))

        return elements

    # ==================================================================
    # E) BANK TRANSFER FOOTER BOX
    # ==================================================================
    def _build_bank_transfer_box(self) -> List:
        """
        Build the bank transfer information as a boxed/ruled table.
        Exact text per specification.
        """
        elements = []
        elements.append(Spacer(1, 6))

        usable_width = BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_LEFT - BMCStyles.MARGIN_RIGHT
        col_left = usable_width * 0.42
        col_right = usable_width * 0.58

        small = ParagraphStyle(
            "BankCell",
            fontName=BMCStyles.FONT_NAME,
            fontSize=BMCStyles.BANK_FONT_SIZE,
            textColor=BMCStyles.TEXT_BLACK,
            leading=BMCStyles.BANK_FONT_SIZE + 2,
        )
        small_blue_underline = ParagraphStyle(
            "BankCellBlueU",
            fontName=BMCStyles.FONT_NAME,
            fontSize=BMCStyles.BANK_FONT_SIZE,
            textColor=BMCStyles.BMC_LIGHT_BLUE,
            leading=BMCStyles.BANK_FONT_SIZE + 2,
        )

        # Row 1
        r1_left = Paragraph("Depósito Bancario", small)
        r1_right = Paragraph(
            f"Titular: {QuotationConstants.BANK_ACCOUNT_HOLDER} – "
            f"RUT: {QuotationConstants.BANK_RUT}",
            small,
        )

        # Row 2
        r2_left = Paragraph(
            f"{QuotationConstants.BANK_ACCOUNT_TYPE} - {QuotationConstants.BANK_NAME}.",
            small,
        )
        r2_right = Paragraph(
            f"Número de Cuenta Dólares : {QuotationConstants.BANK_ACCOUNT_USD}",
            small,
        )

        # Row 3
        r3_left = Paragraph(
            f"Por cualquier duda, consultar al {QuotationConstants.CONTACT_PHONE}.",
            small,
        )
        r3_right = Paragraph(
            '<u>Lea los Términos y Condiciones</u>',
            small_blue_underline,
        )

        bank_data = [
            [r1_left, r1_right],
            [r2_left, r2_right],
            [r3_left, r3_right],
        ]

        bank_table = Table(bank_data, colWidths=[col_left, col_right])
        bank_table.setStyle(BMCStyles.get_bank_table_style())

        elements.append(bank_table)
        return elements

    # ==================================================================
    # Legacy compatibility – conditions (kept but not primary)
    # ==================================================================
    def _build_conditions(self, conditions: List[str]) -> List:
        """Build terms and conditions section (legacy fallback)."""
        elements = []
        conditions_style = BMCStyles.get_conditions_style()
        for condition in conditions:
            elements.append(Paragraph(condition, conditions_style))
        return elements

    def _build_banking_info(self) -> List:
        """Legacy banking info (now replaced by _build_bank_transfer_box)."""
        return self._build_bank_transfer_box()


# ---------------------------------------------------------------------------
# Convenience / public API
# ---------------------------------------------------------------------------

def generate_quotation_pdf(
    quotation_data: Dict,
    output_path: str,
    logo_path: Optional[str] = None,
) -> str:
    """
    Generate a BMC Uruguay quotation PDF

    Args:
        quotation_data: Raw quotation data (will be formatted automatically)
        output_path: Path where PDF should be saved
        logo_path: Optional explicit logo path (default: auto-resolve)

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
    Reusable template function per specification.
    Delegates to generate_quotation_pdf with explicit logo path.

    Args:
        data: Raw quotation data dictionary
        output_path: Destination PDF file path
        logo_path: Path to BMC logo PNG (default: /mnt/data/Logo_BMC- PNG.png)

    Returns:
        Path to generated PDF
    """
    return generate_quotation_pdf(data, output_path, logo_path=logo_path)
