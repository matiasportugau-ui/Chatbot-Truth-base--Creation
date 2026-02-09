#!/usr/bin/env python3
"""
BMC Uruguay Quotation PDF Generator
====================================

Generates professional quotation PDFs matching the exact structure
and branding of BMC Uruguay's standard quotation template.

Based on: Cotización 01042025 BASE - Isopanel xx mm - Isodec EPS xx mm -desc- WA.ods
"""

import os
from io import BytesIO
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Table,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
    ListFlowable,
    ListItem,
)
from reportlab.platypus import SimpleDocTemplate, TableStyle
from xml.sax.saxutils import escape as _xml_escape

from .pdf_styles import BMCStyles, QuotationConstants


DEFAULT_BMC_PDF_LOGO_PATH = "/mnt/data/Logo_BMC- PNG.png"

# Fixed template comment lines (ensures COMENTARIOS block is always present and consistent)
DEFAULT_TEMPLATE_COMMENTS: List[str] = [
    "Entrega de 10 a 15 días, dependemos de producción.",
    "Oferta válida por 10 días a partir de la fecha.",
    "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).",
    "Para saber más del sistema constructivo SPM haga click en https://youtu.be/Am4mZskFMgc",
]

COMMENT_FORMAT_RULES = {
    "Entrega de 10 a 15 días, dependemos de producción.": {"bold": True, "color": None},
    "Oferta válida por 10 días a partir de la fecha.": {"bold": False, "color": "#FF0000"},
    "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).": {
        "bold": True,
        "color": "#FF0000",
    },
}


def _compose_paragraph_markup(text: str, *, bold: bool = False, color: Optional[str] = None) -> str:
    """Escape text and apply simple ReportLab paragraph markup (bold/color)."""
    safe = _xml_escape(text or "")
    if bold:
        safe = f"<b>{safe}</b>"
    if color:
        safe = f'<font color="{color}">{safe}</font>'
    return safe


def _resolve_logo_path(logo_path: str) -> Optional[str]:
    """Resolve logo path; returns None if file is missing."""
    if logo_path and os.path.exists(logo_path):
        return logo_path
    return None


def _build_scaled_logo(logo_path: str, *, target_height_mm: float = 18.0) -> Optional[Image]:
    """Create a ReportLab Image scaled to a target height (mm), preserving aspect ratio."""
    resolved = _resolve_logo_path(logo_path)
    if not resolved:
        return None
    try:
        iw, ih = ImageReader(resolved).getSize()
        target_h = target_height_mm * mm
        target_w = (float(iw) / float(ih)) * target_h if ih else target_h
        img = Image(resolved, width=target_w, height=target_h)
        img.hAlign = "LEFT"
        return img
    except Exception:
        return None


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
        # Calculate subtotal from all items
        # If total_usd is provided, use it; otherwise calculate based on unit_base
        # We also ensure total_usd is populated in the item for display purposes

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
        except:
            return date_str


class BMCQuotationPDF:
    """
    Main PDF generator for BMC Uruguay quotations.
    Replicates exact structure from ODS template.
    """

    def __init__(self, output_path: str, logo_path: str = DEFAULT_BMC_PDF_LOGO_PATH):
        """
        Initialize PDF generator

        Args:
            output_path: Path where PDF will be saved
        """
        self.output_path = output_path
        self.logo_path = logo_path
        self.styles = BMCStyles()
        self.constants = QuotationConstants()

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def generate(self, quotation_data: Dict) -> str:
        """
        Generate the "Cotización" PDF using the fixed BMC template:
        header (logo + centered title), materials table, COMENTARIOS, bank transfer box.

        IMPORTANT: This method is design/layout only. It does NOT alter any BOM/pricing logic.
        """
        pdf_bytes = self._render_one_page_first(quotation_data)
        Path(self.output_path).write_bytes(pdf_bytes)
        return self.output_path

    def _render_one_page_first(self, quotation_data: Dict) -> bytes:
        """
        1-page-first rule:
        - Build as 1 page whenever possible
        - If content spills to page 2, shrink ONLY the comments font/leading first.
        """
        comment_font = float(getattr(BMCStyles, "FONT_SIZE_COMMENTS", 8.1))
        comment_leading = float(getattr(BMCStyles, "LEADING_COMMENTS", 9.45))

        min_comment_font = 6.8
        max_attempts = 10

        last_pdf = b""
        for _ in range(max_attempts):
            pdf, page_count = self._render_to_bytes(
                quotation_data,
                comment_font=comment_font,
                comment_leading=comment_leading,
            )
            last_pdf = pdf
            if page_count <= 1:
                return pdf

            # Shrink comments only (table unchanged)
            comment_font = max(min_comment_font, comment_font - 0.2)
            comment_leading = max(comment_font + 0.9, comment_leading - 0.25)

        return last_pdf

    def _render_to_bytes(
        self, quotation_data: Dict, *, comment_font: float, comment_leading: float
    ) -> tuple[bytes, int]:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=BMCStyles.MARGIN_TOP,
            bottomMargin=BMCStyles.MARGIN_BOTTOM,
            leftMargin=BMCStyles.MARGIN_LEFT,
            rightMargin=BMCStyles.MARGIN_RIGHT,
        )

        story = self._build_bmc_template_story(
            quotation_data,
            doc_width=doc.width,
            comment_font=comment_font,
            comment_leading=comment_leading,
        )

        counting_canvas = None

        class _CountingCanvas(canvas.Canvas):
            pass

        def _canvasmaker(*args, **kwargs):
            nonlocal counting_canvas
            counting_canvas = _CountingCanvas(*args, **kwargs)
            return counting_canvas

        doc.build(story, canvasmaker=_canvasmaker)
        page_count = int(counting_canvas.getPageNumber() if counting_canvas else 1)
        return buffer.getvalue(), page_count

    def _build_bmc_template_story(
        self,
        quotation_data: Dict,
        *,
        doc_width: float,
        comment_font: float,
        comment_leading: float,
    ) -> List:
        story: List[Any] = []

        # HEADER (two columns: logo | centered title)
        header = self._build_header_logo_title(quotation_data, doc_width=doc_width)
        story.append(header)
        story.append(Spacer(1, 2.0 * mm))

        # MATERIALS TABLE
        materials_table = self._build_materials_table(quotation_data, doc_width=doc_width)
        story.append(materials_table)
        story.append(Spacer(1, 2.0 * mm))

        # COMENTARIOS
        story.extend(
            self._build_comentarios_block(
                quotation_data,
                doc_width=doc_width,
                comment_font=comment_font,
                comment_leading=comment_leading,
            )
        )
        story.append(Spacer(1, 2.0 * mm))

        # BANK TRANSFER BOX
        story.append(self._build_bank_transfer_box(doc_width=doc_width))

        return story

    def _get_title_text(self, data: Dict) -> str:
        desc = (data.get("quote_description") or "").strip()
        if desc:
            return f"COTIZACIÓN – {desc}"
        title = (data.get("quote_title") or "COTIZACIÓN").strip()
        return title.upper() if title else "COTIZACIÓN"

    def _build_header_logo_title(self, data: Dict, *, doc_width: float) -> Table:
        logo = _build_scaled_logo(self.logo_path, target_height_mm=18.0)
        title_style = ParagraphStyle(
            "BMCQuoteHeaderTitle",
            fontName=BMCStyles.FONT_NAME_BOLD,
            fontSize=12.5,
            leading=13.8,
            alignment=1,  # centered
            textColor=colors.black,
            spaceBefore=0,
            spaceAfter=0,
        )
        title = Paragraph(_compose_paragraph_markup(self._get_title_text(data)), title_style)

        logo_cell = logo if logo is not None else Spacer(1, 18.0 * mm)
        logo_w = float(getattr(logo_cell, "drawWidth", 30.0 * mm))
        logo_col_w = min(max(logo_w, 28.0 * mm), 60.0 * mm)

        tbl = Table(
            [[logo_cell, title]],
            colWidths=[logo_col_w, max(1.0, doc_width - logo_col_w)],
            hAlign="LEFT",
        )
        tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "CENTER"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return tbl

    def _flatten_items_for_materials_table(self, data: Dict) -> List[Dict]:
        items: List[Dict] = []
        for group_key in ("products", "accessories", "fixings"):
            group = data.get(group_key) or []
            if isinstance(group, list):
                items.extend(group)
        return items

    def _build_materials_table(self, data: Dict, *, doc_width: float) -> Table:
        header = ["Descripción", "Unid", "Cant", "USD", "Total"]
        rows: List[List[Any]] = [header]

        body_style = ParagraphStyle(
            "BMCMaterialsBody",
            fontName=BMCStyles.FONT_NAME,
            fontSize=BMCStyles.FONT_SIZE_TABLE_BODY,
            leading=BMCStyles.FONT_SIZE_TABLE_BODY + 1.2,
        )

        for item in self._flatten_items_for_materials_table(data):
            name = (item.get("name") or "").strip()
            spec = (item.get("specification") or "").strip()
            length = item.get("Length_m", item.get("length_m", None))
            if spec:
                name = f"{name} – {spec}"
            if length not in (None, "", 0):
                # Include length as plain text (keeps fixed table columns)
                name = f"{name} (L: {length} m)"

            unit = item.get("unit_base", "Unid")
            qty = item.get("quantity", "")

            unit_price = item.get("sale_sin_iva", item.get("unit_price_usd", 0))
            total_usd = item.get("total_usd")
            if total_usd is None:
                total_usd = QuotationDataFormatter.calculate_item_total(item)

            rows.append(
                [
                    Paragraph(_compose_paragraph_markup(name), body_style),
                    str(unit),
                    str(qty),
                    QuotationDataFormatter.format_currency(float(unit_price or 0)),
                    QuotationDataFormatter.format_currency(float(total_usd or 0)),
                ]
            )

        col_widths = [
            doc_width * 0.54,
            doc_width * 0.10,
            doc_width * 0.10,
            doc_width * 0.13,
            doc_width * 0.13,
        ]
        tbl = Table(rows, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
        tbl.setStyle(BMCStyles.get_products_table_style())
        return tbl

    def _get_comment_lines(self, data: Dict) -> List[str]:
        provided = data.get("comments") or []
        lines: List[str] = [str(x) for x in provided if str(x).strip()]

        # Enforce fixed template lines (avoid duplicates)
        existing = set(l.strip() for l in lines)
        for line in DEFAULT_TEMPLATE_COMMENTS:
            if line.strip() not in existing:
                lines.append(line)
        return lines

    def _build_comentarios_block(
        self,
        data: Dict,
        *,
        doc_width: float,
        comment_font: float,
        comment_leading: float,
    ) -> List[Any]:
        elements: List[Any] = []

        title_style = ParagraphStyle(
            "BMCCommentsTitle",
            fontName=BMCStyles.FONT_NAME_BOLD,
            fontSize=9.2,
            leading=10.2,
            textColor=colors.black,
            spaceBefore=0,
            spaceAfter=2,
        )
        elements.append(Paragraph("<b>COMENTARIOS:</b>", title_style))

        comment_style = ParagraphStyle(
            "BMCCommentLine",
            fontName=BMCStyles.FONT_NAME,
            fontSize=float(comment_font),
            leading=float(comment_leading),
            textColor=colors.black,
            spaceBefore=0,
            spaceAfter=0,
        )

        list_items: List[ListItem] = []
        for line in self._get_comment_lines(data):
            raw = str(line).strip()
            rule = COMMENT_FORMAT_RULES.get(raw, {})
            markup = _compose_paragraph_markup(
                raw,
                bold=bool(rule.get("bold", False)),
                color=rule.get("color"),
            )
            p = Paragraph(markup, comment_style)
            list_items.append(ListItem(p, leftIndent=8, bulletText="•"))

        elements.append(
            ListFlowable(
                list_items,
                bulletType="bullet",
                start="•",
                leftIndent=0,
                bulletFontName=BMCStyles.FONT_NAME,
                bulletFontSize=float(comment_font),
                bulletDedent=0,
            )
        )
        return elements

    def _build_bank_transfer_box(self, *, doc_width: float) -> Table:
        footer_style = ParagraphStyle(
            "BMCFooterSmall",
            fontName=BMCStyles.FONT_NAME,
            fontSize=float(getattr(BMCStyles, "FONT_SIZE_FOOTER", 8.4)),
            leading=float(getattr(BMCStyles, "FONT_SIZE_FOOTER", 8.4)) + 1.1,
            textColor=colors.black,
        )

        link_style = ParagraphStyle(
            "BMCFooterLink",
            parent=footer_style,
            textColor=colors.HexColor("#0000FF"),
        )

        data = [
            [
                Paragraph(_compose_paragraph_markup("Depósito Bancario", bold=True), footer_style),
                Paragraph(
                    _compose_paragraph_markup(
                        "Titular: Metalog SAS – RUT: 120403430012"
                    ),
                    footer_style,
                ),
            ],
            [
                Paragraph(_compose_paragraph_markup("Caja de Ahorro - BROU."), footer_style),
                Paragraph(
                    _compose_paragraph_markup(
                        "Número de Cuenta Dólares : 110520638-00002"
                    ),
                    footer_style,
                ),
            ],
            [
                Paragraph(
                    _compose_paragraph_markup(
                        "Por cualquier duda, consultar al 092 663 245."
                    ),
                    footer_style,
                ),
                Paragraph(
                    '<font color="#0000FF"><u>Lea los Términos y Condiciones</u></font>',
                    link_style,
                ),
            ],
        ]

        tbl = Table(data, colWidths=[doc_width * 0.50, doc_width * 0.50], hAlign="LEFT")
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), BMCStyles.TABLE_HEADER_BG),
                    ("BOX", (0, 0), (-1, -1), 0.4, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        return tbl

    def _build_header(self, data: Dict) -> List:
        """Build header section with logo and company info"""
        elements = []

        # TODO: Add logo when available
        # if os.path.exists(BMCStyles.LOGO_PATH):
        #     logo = Image(BMCStyles.LOGO_PATH, width=BMCStyles.LOGO_WIDTH, height=BMCStyles.LOGO_HEIGHT)
        #     elements.append(logo)

        # Company contact information
        styles = getSampleStyleSheet()
        contact_style = BMCStyles.get_small_style()

        elements.append(Paragraph(QuotationConstants.COMPANY_EMAIL, contact_style))
        elements.append(Paragraph(QuotationConstants.COMPANY_WEBSITE, contact_style))
        elements.append(Paragraph(QuotationConstants.COMPANY_PHONE, contact_style))

        # Date and location
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(
                f"Fecha: {QuotationDataFormatter.format_date(data.get('date', ''))}",
                contact_style,
            )
        )
        elements.append(Paragraph(data.get("location", ""), contact_style))

        # Technical specs (autoportancia, apoyos)
        specs = data.get("technical_specs", {})
        if specs:
            elements.append(
                Paragraph(
                    f"Autoportancia: {specs.get('autoportancia', 0)} m", contact_style
                )
            )
            elements.append(
                Paragraph(f"Apoyos: {specs.get('apoyos', 0)}", contact_style)
            )

        return elements

    def _build_title_section(self, data: Dict) -> List:
        """Build title and client information section"""
        elements = []

        # Main title
        title_style = BMCStyles.get_title_style()
        title_text = f"{data.get('quote_title', 'Cotización')}: {data.get('quote_description', '')}"
        elements.append(Paragraph(title_text, title_style))

        # Client information
        client = data.get("client", {})
        normal_style = BMCStyles.get_normal_style()

        elements.append(Spacer(1, 12))
        elements.append(
            Paragraph(f"<b>Cliente:</b> {client.get('name', '')}", normal_style)
        )
        elements.append(
            Paragraph(f"<b>Dirección:</b> {client.get('address', '')}", normal_style)
        )
        elements.append(
            Paragraph(f"<b>Tel/cel:</b> {client.get('phone', '')}", normal_style)
        )

        return elements

    def _build_products_table(self, products: List[Dict]) -> List:
        """Build products table"""
        elements = []

        # Table header
        header = [
            "Producto",
            "Largos (m)",
            "Cantidades",
            "Costo m² (USD)",
            "Costo Total (USD)",
        ]

        # Table data
        data = [header]
        for product in products:
            # Ensure correct Length_m and total_usd calculation
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

        # Create table
        table = Table(data, colWidths=[180, 60, 60, 80, 100])
        table.setStyle(BMCStyles.get_products_table_style())

        elements.append(table)
        return elements

    def _build_accessories_table(self, accessories: List[Dict]) -> List:
        """Build accessories/profiles table"""
        elements = []

        # Section header
        header_style = BMCStyles.get_header_style()
        elements.append(Paragraph("Accesorios", header_style))

        # Table structure (similar to products)
        header = [
            "Producto",
            "Largo (m)",
            "Cantidades",
            "Costo lineal (USD)",
            "Costo Total (USD)",
        ]
        data = [header]

        for item in accessories:
            # Ensure correct Length_m and total_usd calculation
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

        table = Table(data, colWidths=[180, 60, 60, 80, 100])
        table.setStyle(BMCStyles.get_products_table_style())

        elements.append(table)
        return elements

    def _build_fixings_table(self, fixings: List[Dict]) -> List:
        """Build fixings/fijaciones table"""
        elements = []

        # Section header
        header_style = BMCStyles.get_header_style()
        elements.append(Paragraph("Fijaciones", header_style))

        # Table structure
        header = [
            "Producto",
            "Especificación",
            "Cantidades",
            "Costo unit. (USD)",
            "Costo Total (USD)",
        ]
        data = [header]

        for item in fixings:
            # Bug 2 Fix: Ensure total_usd is calculated if missing
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

        table = Table(data, colWidths=[140, 80, 60, 80, 100])
        table.setStyle(BMCStyles.get_products_table_style())

        elements.append(table)
        return elements

    def _build_totals(self, totals: Dict) -> List:
        """Build totals section"""
        elements = []

        # Format totals data
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

        # Create table
        table = Table(data, colWidths=[200, 120])
        table.setStyle(BMCStyles.get_totals_table_style())

        elements.append(table)
        return elements

    def _build_comments(self, comments: List[str]) -> List:
        """Build comments section"""
        elements = []

        header_style = BMCStyles.get_header_style()
        elements.append(Paragraph("Comentarios", header_style))

        small_style = BMCStyles.get_small_style()
        for comment in comments:
            elements.append(Paragraph(comment, small_style))

        return elements

    def _build_conditions(self, conditions: List[str]) -> List:
        """Build terms and conditions section"""
        elements = []

        conditions_style = BMCStyles.get_conditions_style()

        for condition in conditions:
            elements.append(Paragraph(condition, conditions_style))

        return elements

    def _build_banking_info(self) -> List:
        """Build banking information section"""
        elements = []

        small_style = BMCStyles.get_small_style()

        elements.append(Spacer(1, 12))
        elements.append(Paragraph("<b>Depósito Bancario</b>", small_style))
        elements.append(
            Paragraph(
                f"Titular: {QuotationConstants.BANK_ACCOUNT_HOLDER} - RUT: {QuotationConstants.BANK_RUT}",
                small_style,
            )
        )
        elements.append(
            Paragraph(
                f"{QuotationConstants.BANK_ACCOUNT_TYPE} - {QuotationConstants.BANK_NAME}",
                small_style,
            )
        )
        elements.append(
            Paragraph(
                f"Número de Cuenta Dólares: {QuotationConstants.BANK_ACCOUNT_USD}",
                small_style,
            )
        )

        return elements


def build_quote_pdf(
    data: Dict,
    output_path: str,
    logo_path: str = DEFAULT_BMC_PDF_LOGO_PATH,
) -> str:
    """
    Build a "Cotización" PDF using the BMC template (design/format only).

    Args:
        data: Raw quotation data OR already formatted data (from QuotationDataFormatter).
        output_path: Target PDF path.
        logo_path: Official logo path (default: /mnt/data/Logo_BMC- PNG.png)
    """
    formatted_data = (
        data
        if isinstance(data, dict) and "client" in data and "totals" in data
        else QuotationDataFormatter.format_for_pdf(data)
    )
    generator = BMCQuotationPDF(output_path, logo_path=logo_path)
    return generator.generate(formatted_data)


# Convenience function for quick PDF generation (keeps backward-compatible name)
def generate_quotation_pdf(
    quotation_data: Dict,
    output_path: str,
    logo_path: str = DEFAULT_BMC_PDF_LOGO_PATH,
) -> str:
    """
    Generate a BMC Uruguay quotation PDF

    Args:
        quotation_data: Raw quotation data (will be formatted automatically)
        output_path: Path where PDF should be saved

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
    return build_quote_pdf(quotation_data, output_path, logo_path=logo_path)
