#!/usr/bin/env python3
"""
BMC Uruguay Quotation PDF Generator
====================================

Generates professional quotation PDFs matching BMC Uruguay's formal template.
"""

import os
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .pdf_styles import BMCStyles, QuotationConstants


class QuotationDataFormatter:
    """Formats raw quotation data into PDF-ready structure."""

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
        - unit_base = 'unidad': quantity × sale_sin_iva
        - unit_base = 'ml': quantity × Length_m × sale_sin_iva
        - unit_base = 'm²': total_m2 × sale_sin_iva
        """
        unit_base = item.get("unit_base", "unidad").lower()

        # Use sale_sin_iva if available, fallback to unit_price_usd
        price = item.get("sale_sin_iva", item.get("unit_price_usd", 0))

        if unit_base == "unidad":
            return item.get("quantity", 0) * price

        if unit_base == "ml":
            quantity = item.get("quantity", 0)
            length_m = item.get("Length_m", item.get("length_m", 0))
            return quantity * length_m * price

        if unit_base in {"m²", "m2"}:
            total_m2 = item.get("total_m2", 0)
            return total_m2 * price

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
        """Format currency as USD with proper formatting."""
        return f"${amount:,.2f}"

    @staticmethod
    def format_date(date_str: str) -> str:
        """Format date string consistently."""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
        except Exception:
            return date_str


class BMCQuotationPDF:
    """
    Main PDF generator for BMC Uruguay quotations.

    The generator prioritizes one-page fit by reducing comment typography
    before altering any table content or sizing.
    """

    COMMENT_BOLD_LINE = "Entrega de 10 a 15 días, dependemos de producción."
    COMMENT_RED_LINE = "Oferta válida por 10 días a partir de la fecha."
    COMMENT_BOLD_RED_LINE = (
        "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). "
        "Saldo del 40 % (previo a retiro de fábrica)."
    )

    def __init__(self, output_path: str, logo_path: Optional[str] = None):
        """
        Initialize PDF generator.

        Args:
            output_path: Path where PDF will be saved
            logo_path: Optional override for official logo path
        """
        self.output_path = output_path
        self.styles = BMCStyles()
        self.constants = QuotationConstants()
        self.logo_path = logo_path or BMCStyles.LOGO_PATH
        self.usable_width = (
            BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_LEFT - BMCStyles.MARGIN_RIGHT
        )

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def generate(self, quotation_data: Dict) -> str:
        """
        Generate complete quotation PDF with 1-page-first fitting strategy.

        Args:
            quotation_data: Formatted quotation data dictionary

        Returns:
            Path to generated PDF file
        """
        comments_font_size, comments_leading = self._resolve_comments_typography(
            quotation_data
        )
        story = self._build_story(
            quotation_data,
            comments_font_size=comments_font_size,
            comments_leading=comments_leading,
        )

        doc = self._create_document(self.output_path)
        doc.build(story)
        return self.output_path

    def _create_document(self, destination) -> SimpleDocTemplate:
        """Create a document with required A4 size and margins."""
        return SimpleDocTemplate(
            destination,
            pagesize=BMCStyles.PAGE_SIZE,
            topMargin=BMCStyles.MARGIN_TOP,
            bottomMargin=BMCStyles.MARGIN_BOTTOM,
            leftMargin=BMCStyles.MARGIN_LEFT,
            rightMargin=BMCStyles.MARGIN_RIGHT,
        )

    def _resolve_comments_typography(self, quotation_data: Dict) -> Tuple[float, float]:
        """
        Shrink comments font/leading first to maximize one-page fit.

        Table sizing and structure remain unchanged.
        """
        font_size = BMCStyles.COMMENT_FONT_SIZE_BASE
        leading = BMCStyles.COMMENT_LEADING_BASE

        while True:
            pages = self._estimate_pages(quotation_data, font_size, leading)
            if pages <= 1:
                return font_size, leading

            next_font = max(
                BMCStyles.COMMENT_FONT_SIZE_MIN,
                round(font_size - BMCStyles.COMMENT_STEP, 2),
            )
            next_leading = max(
                BMCStyles.COMMENT_LEADING_MIN,
                round(leading - BMCStyles.COMMENT_STEP, 2),
            )
            if next_font == font_size and next_leading == leading:
                return font_size, leading

            font_size, leading = next_font, next_leading

    def _estimate_pages(
        self, quotation_data: Dict, comments_font_size: float, comments_leading: float
    ) -> int:
        """Render to memory and count generated pages."""
        buffer = BytesIO()
        story = self._build_story(
            quotation_data,
            comments_font_size=comments_font_size,
            comments_leading=comments_leading,
        )

        class _PageCounterCanvas(canvas.Canvas):
            page_count = 1

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._local_page_count = 1

            def showPage(self):
                self._local_page_count += 1
                super().showPage()

            def save(self):
                _PageCounterCanvas.page_count = self._local_page_count
                super().save()

        doc = self._create_document(buffer)
        doc.build(story, canvasmaker=_PageCounterCanvas)
        return _PageCounterCanvas.page_count

    def _build_story(
        self, data: Dict, comments_font_size: float, comments_leading: float
    ) -> List:
        """Build all PDF sections in final order."""
        story: List = []
        story.extend(self._build_header(data))
        story.append(Spacer(1, 3 * mm))

        story.extend(self._build_title_section(data))
        story.append(Spacer(1, 2 * mm))

        if data.get("products"):
            story.extend(self._build_products_table(data["products"]))
            story.append(Spacer(1, 1.5 * mm))

        if data.get("accessories"):
            story.extend(self._build_accessories_table(data["accessories"]))
            story.append(Spacer(1, 1.5 * mm))

        if data.get("fixings"):
            story.extend(self._build_fixings_table(data["fixings"]))
            story.append(Spacer(1, 1.5 * mm))

        story.extend(self._build_totals(data["totals"]))
        story.append(Spacer(1, 2 * mm))

        comments = self._compose_comments(data.get("comments", []))
        story.extend(
            self._build_comments(
                comments,
                comments_font_size=comments_font_size,
                comments_leading=comments_leading,
            )
        )
        story.append(Spacer(1, 1.5 * mm))
        story.extend(self._build_transfer_footer())
        return story

    def _build_header(self, data: Dict) -> List:
        """Build two-column header: [logo | centered title]."""
        logo_cell = self._build_logo_flowable()
        title = self._resolve_header_title(data)
        title_paragraph = Paragraph(escape(title), BMCStyles.get_title_style())

        logo_col = min(76 * mm, self.usable_width * 0.34)
        title_col = self.usable_width - logo_col
        header_table = Table(
            [[logo_cell, title_paragraph]],
            colWidths=[logo_col, title_col],
            hAlign="LEFT",
        )
        header_table.setStyle(
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
        return [header_table]

    def _build_logo_flowable(self):
        """Load official logo with fixed height and preserved aspect ratio."""
        if not self.logo_path or not os.path.exists(self.logo_path):
            return Spacer(1, BMCStyles.LOGO_HEIGHT)

        try:
            img_reader = ImageReader(self.logo_path)
            img_width, img_height = img_reader.getSize()
            if not img_width or not img_height:
                return Spacer(1, BMCStyles.LOGO_HEIGHT)

            target_height = BMCStyles.LOGO_HEIGHT
            target_width = target_height * (img_width / img_height)
            return Image(self.logo_path, width=target_width, height=target_height)
        except Exception:
            return Spacer(1, BMCStyles.LOGO_HEIGHT)

    def _resolve_header_title(self, data: Dict) -> str:
        """Build header title text preserving dynamic quote context."""
        quote_description = str(data.get("quote_description", "") or "").strip()
        if quote_description:
            return f"COTIZACIÓN – {quote_description}"

        quote_title = str(data.get("quote_title", "") or "").strip()
        if quote_title and quote_title.lower() != "cotización":
            return f"COTIZACIÓN – {quote_title}"

        return "COTIZACIÓN – ISODEC EPS 100 mm"

    def _build_title_section(self, data: Dict) -> List:
        """Build compact metadata and client lines below header."""
        elements = []
        client = data.get("client", {})
        specs = data.get("technical_specs", {})

        meta_parts = [f"Fecha: {QuotationDataFormatter.format_date(data.get('date', ''))}"]
        location = str(data.get("location", "") or "").strip()
        if location:
            meta_parts.append(location)
        if specs:
            meta_parts.append(f"Autoportancia: {specs.get('autoportancia', 0)} m")
            meta_parts.append(f"Apoyos: {specs.get('apoyos', 0)}")

        elements.append(Paragraph(" | ".join(meta_parts), BMCStyles.get_small_style()))

        client_name = escape(str(client.get("name", "") or ""))
        elements.append(
            Paragraph(f"<b>Cliente:</b> {client_name}", BMCStyles.get_normal_style())
        )

        address = str(client.get("address", "") or "").strip()
        if address:
            elements.append(
                Paragraph(f"<b>Dirección:</b> {escape(address)}", BMCStyles.get_normal_style())
            )

        phone = str(client.get("phone", "") or "").strip()
        if phone:
            elements.append(
                Paragraph(f"<b>Tel/cel:</b> {escape(phone)}", BMCStyles.get_normal_style())
            )

        return elements

    def _build_products_table(self, products: List[Dict]) -> List:
        """Build products/materials table."""
        header = [
            "Producto",
            "Largos (m)",
            "Cantidades",
            "Costo m² (USD)",
            "Costo Total (USD)",
        ]
        rows = []
        for product in products:
            length = product.get("Length_m", product.get("length_m", ""))
            total_usd = product.get("total_usd")
            if total_usd is None or total_usd == 0:
                total_usd = QuotationDataFormatter.calculate_item_total(product)

            rows.append(
                [
                    str(product.get("name", "")),
                    str(length),
                    str(product.get("quantity", "")),
                    QuotationDataFormatter.format_currency(product.get("unit_price_usd", 0)),
                    QuotationDataFormatter.format_currency(total_usd),
                ]
            )

        return self._build_material_table(
            title="Materiales",
            header=header,
            rows=rows,
            col_widths=[230, 55, 55, 85, 90],
            numeric_cols=[1, 2, 3, 4],
        )

    def _build_accessories_table(self, accessories: List[Dict]) -> List:
        """Build accessories/profiles table."""
        header = [
            "Producto",
            "Largo (m)",
            "Cantidades",
            "Costo lineal (USD)",
            "Costo Total (USD)",
        ]
        rows = []
        for item in accessories:
            length = item.get("Length_m", item.get("length_m", ""))
            total_usd = item.get("total_usd")
            if total_usd is None or total_usd == 0:
                total_usd = QuotationDataFormatter.calculate_item_total(item)

            rows.append(
                [
                    str(item.get("name", "")),
                    str(length),
                    str(item.get("quantity", "")),
                    QuotationDataFormatter.format_currency(item.get("unit_price_usd", 0)),
                    QuotationDataFormatter.format_currency(total_usd),
                ]
            )

        return self._build_material_table(
            title="Accesorios",
            header=header,
            rows=rows,
            col_widths=[230, 55, 55, 85, 90],
            numeric_cols=[1, 2, 3, 4],
        )

    def _build_fixings_table(self, fixings: List[Dict]) -> List:
        """Build fixings/fijaciones table."""
        header = [
            "Producto",
            "Especificación",
            "Cantidades",
            "Costo unit. (USD)",
            "Costo Total (USD)",
        ]
        rows = []
        for item in fixings:
            total_usd = item.get("total_usd")
            if total_usd is None or total_usd == 0:
                total_usd = QuotationDataFormatter.calculate_item_total(item)

            rows.append(
                [
                    str(item.get("name", "")),
                    str(item.get("specification", "")),
                    str(item.get("quantity", "")),
                    QuotationDataFormatter.format_currency(item.get("unit_price_usd", 0)),
                    QuotationDataFormatter.format_currency(total_usd),
                ]
            )

        return self._build_material_table(
            title="Fijaciones",
            header=header,
            rows=rows,
            col_widths=[195, 95, 50, 80, 95],
            numeric_cols=[2, 3, 4],
        )

    def _build_material_table(
        self,
        title: str,
        header: Sequence[str],
        rows: Sequence[Sequence[str]],
        col_widths: Sequence[float],
        numeric_cols: Sequence[int],
    ) -> List:
        """Build a styled materials table block with repeat header."""
        elements = [Paragraph(title, BMCStyles.get_header_style())]
        table_data = [list(header)] + [list(row) for row in rows]
        table = Table(table_data, colWidths=list(col_widths), repeatRows=1, hAlign="LEFT")
        table.setStyle(self._build_material_table_style(len(table_data), numeric_cols))
        elements.append(table)
        return elements

    def _build_material_table_style(
        self, row_count: int, numeric_cols: Sequence[int]
    ) -> TableStyle:
        """Table style matching requested gray header + zebra rows + right numeric."""
        style_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), BMCStyles.TABLE_HEADER_BG),
            ("FONTNAME", (0, 0), (-1, 0), BMCStyles.FONT_NAME_BOLD),
            ("FONTSIZE", (0, 0), (-1, 0), BMCStyles.FONT_SIZE_TABLE_HEADER),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTNAME", (0, 1), (-1, -1), BMCStyles.FONT_NAME),
            ("FONTSIZE", (0, 1), (-1, -1), BMCStyles.FONT_SIZE_TABLE_ROW),
            ("TEXTCOLOR", (0, 0), (-1, -1), BMCStyles.TEXT_BLACK),
            ("GRID", (0, 0), (-1, -1), 0.35, BMCStyles.TABLE_BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ]

        for row_idx in range(1, row_count):
            bg = colors.white if row_idx % 2 else BMCStyles.TABLE_ALT_BG
            style_commands.append(("BACKGROUND", (0, row_idx), (-1, row_idx), bg))

        for col_idx in numeric_cols:
            style_commands.append(("ALIGN", (col_idx, 1), (col_idx, -1), "RIGHT"))

        return TableStyle(style_commands)

    def _build_totals(self, totals: Dict) -> List:
        """Build totals section."""
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
        table = Table(data, colWidths=[self.usable_width * 0.62, self.usable_width * 0.38])
        table.setStyle(BMCStyles.get_totals_table_style())
        return [table]

    def _compose_comments(self, raw_comments: Sequence[str]) -> List[str]:
        """Build comments list while enforcing required template lines."""
        comments = [
            str(comment).strip()
            for comment in (raw_comments or [])
            if str(comment).strip()
        ]
        if not comments:
            comments = QuotationConstants.get_default_comments()

        required = [
            self.COMMENT_BOLD_LINE,
            self.COMMENT_RED_LINE,
            self.COMMENT_BOLD_RED_LINE,
            QuotationConstants.SPM_SYSTEM_VIDEO,
        ]

        normalized_existing = {self._normalize_comment_line(line) for line in comments}
        for line in required:
            normalized = self._normalize_comment_line(line)
            if normalized not in normalized_existing:
                comments.append(line)
                normalized_existing.add(normalized)

        # Deduplicate while preserving order.
        deduped: List[str] = []
        seen = set()
        for line in comments:
            normalized = self._normalize_comment_line(line)
            if normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(line)
        return deduped

    def _build_comments(
        self, comments: List[str], comments_font_size: float, comments_leading: float
    ) -> List:
        """Build COMENTARIOS section as bullet list with selective line styling."""
        elements = [Paragraph("COMENTARIOS:", BMCStyles.get_header_style())]
        comment_style = BMCStyles.get_comment_style(
            font_size=comments_font_size, leading=comments_leading
        )

        for comment in comments:
            text = self._render_comment_markup(comment)
            elements.append(Paragraph(text, comment_style, bulletText="•"))

        return elements

    def _render_comment_markup(self, comment: str) -> str:
        """Apply bold/red rules to specific lines and keep URL plain text."""
        normalized = self._normalize_comment_line(comment)
        escaped_comment = escape(comment)

        if normalized == self._normalize_comment_line(self.COMMENT_BOLD_RED_LINE):
            return f'<font color="#C62828"><b>{escaped_comment}</b></font>'
        if normalized == self._normalize_comment_line(self.COMMENT_BOLD_LINE):
            return f"<b>{escaped_comment}</b>"
        if normalized == self._normalize_comment_line(self.COMMENT_RED_LINE):
            return f'<font color="#C62828">{escaped_comment}</font>'
        return escaped_comment

    def _normalize_comment_line(self, line: str) -> str:
        """Normalize line for robust comparisons."""
        cleaned = re.sub(r"^[\s\-\*\u2022]+", "", str(line).strip())
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    def _build_transfer_footer(self) -> List:
        """Build bank transfer boxed footer directly after comments."""
        small_style = BMCStyles.get_small_style()
        small_style.textColor = BMCStyles.TEXT_BLACK
        terms_link = Paragraph(
            '<font color="#1F5EAF"><u>Lea los Términos y Condiciones</u></font>',
            small_style,
        )
        table_data = [
            [
                Paragraph("<b>Depósito Bancario</b>", small_style),
                Paragraph("Titular: Metalog SAS – RUT: 120403430012", small_style),
            ],
            [
                Paragraph("Caja de Ahorro - BROU.", small_style),
                Paragraph("Número de Cuenta Dólares : 110520638-00002", small_style),
            ],
            [
                Paragraph("Por cualquier duda, consultar al 092 663 245.", small_style),
                terms_link,
            ],
        ]
        table = Table(
            table_data,
            colWidths=[self.usable_width * 0.42, self.usable_width * 0.58],
            hAlign="LEFT",
        )
        table.setStyle(BMCStyles.get_transfer_table_style())
        return [table]


def build_quote_pdf(
    data: Dict,
    output_path: str,
    logo_path: str = "/mnt/data/Logo_BMC- PNG.png",
) -> str:
    """
    Build quotation PDF using BMC formal template.

    Args:
        data: Raw quotation data
        output_path: Path where PDF should be saved
        logo_path: Official BMC logo path for this template
    """
    formatted_data = QuotationDataFormatter.format_for_pdf(data)
    generator = BMCQuotationPDF(output_path=output_path, logo_path=logo_path)
    return generator.generate(formatted_data)


def generate_quotation_pdf(
    quotation_data: Dict, output_path: str, logo_path: Optional[str] = None
) -> str:
    """
    Backward-compatible helper for quotation PDF generation.

    Args:
        quotation_data: Raw quotation data (formatted automatically)
        output_path: Path where PDF should be saved
        logo_path: Optional logo override; defaults to official BMC path
    """
    return build_quote_pdf(
        data=quotation_data,
        output_path=output_path,
        logo_path=logo_path or BMCStyles.LOGO_PATH,
    )
