#!/usr/bin/env python3
"""
BMC Uruguay Quotation PDF Generator
====================================

Generates quotation PDFs with the BMC formal template:
- Two-column header with official logo + centered title
- Styled materials tables
- COMENTARIOS block with per-line formatting rules
- Bank transfer boxed footer
"""

import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table
from reportlab.platypus import TableStyle

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
        client_info = {
            "name": raw_data.get("client_name", "Cliente"),
            "address": raw_data.get("client_address", ""),
            "phone": raw_data.get("client_phone", ""),
        }

        products = raw_data.get("products", [])
        accessories = raw_data.get("accessories", [])
        fixings = raw_data.get("fixings", [])

        totals = QuotationDataFormatter.calculate_totals(
            products, accessories, fixings, raw_data.get("shipping_usd")
        )

        return {
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

    @staticmethod
    def calculate_item_total(item: Dict) -> float:
        """
        Calculate item total based on unit_base.

        Logic (2026-01-28 correction):
        - unit_base = 'unidad': quantity x sale_sin_iva
        - unit_base = 'ml': quantity x Length_m x sale_sin_iva
        - unit_base = 'm²': total_m2 x sale_sin_iva
        """
        unit_base = str(item.get("unit_base", "unidad")).lower()
        price = item.get("sale_sin_iva", item.get("unit_price_usd", 0))

        if unit_base == "unidad":
            return item.get("quantity", 0) * price
        if unit_base == "ml":
            quantity = item.get("quantity", 0)
            length_m = item.get("Length_m", item.get("length_m", 0))
            return quantity * length_m * price
        if unit_base in ("m²", "m2"):
            total_m2 = item.get("total_m2", 0)
            return total_m2 * price
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

        NOTE: Existing pricing/BOM logic is intentionally preserved.
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


class _PageCountCanvas(canvas.Canvas):
    """Small canvas helper to capture generated page count."""

    latest_page_count = 0

    def save(self):
        _PageCountCanvas.latest_page_count = max(1, self._pageNumber)
        super().save()


class BMCQuotationPDF:
    """
    Main PDF generator for BMC Uruguay quotations.

    Applies the BMC layout template while preserving quotation calculations.
    """

    COMMENT_BOLD_LINE = "Entrega de 10 a 15 días, dependemos de producción."
    COMMENT_RED_LINE = "Oferta válida por 10 días a partir de la fecha."
    COMMENT_BOLD_RED_LINE = (
        "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). "
        "Saldo del 40 % (previo a retiro de fábrica)."
    )

    COMMENT_SIZE_VARIANTS = (
        (8.2, 9.5),
        (8.0, 9.3),
        (7.8, 9.1),
        (7.6, 8.9),
    )

    def __init__(self, output_path: str, logo_path: Optional[str] = None):
        self.output_path = output_path
        self.logo_path = BMCStyles.resolve_logo_path(logo_path)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    @property
    def _usable_width(self) -> float:
        return BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_LEFT - BMCStyles.MARGIN_RIGHT

    def _create_document(self, target) -> SimpleDocTemplate:
        return SimpleDocTemplate(
            target,
            pagesize=BMCStyles.PAGE_SIZE,
            topMargin=BMCStyles.MARGIN_TOP,
            bottomMargin=BMCStyles.MARGIN_BOTTOM,
            leftMargin=BMCStyles.MARGIN_LEFT,
            rightMargin=BMCStyles.MARGIN_RIGHT,
        )

    def _build_document(
        self, target, quotation_data: Dict, comment_font_size: float, comment_leading: float
    ) -> int:
        _PageCountCanvas.latest_page_count = 0
        doc = self._create_document(target)
        story = self._build_story(quotation_data, comment_font_size, comment_leading)
        doc.build(story, canvasmaker=_PageCountCanvas)
        return _PageCountCanvas.latest_page_count

    def generate(self, quotation_data: Dict) -> str:
        """
        Generate complete quotation PDF.

        1-page-first strategy:
        - Try to fit content into one page by reducing comment font and leading first.
        - Keep tables unchanged while trying to fit.
        """
        selected_size, selected_leading = self.COMMENT_SIZE_VARIANTS[0]

        for font_size, leading in self.COMMENT_SIZE_VARIANTS:
            temp_buffer = BytesIO()
            page_count = self._build_document(
                temp_buffer, quotation_data, font_size, leading
            )
            selected_size, selected_leading = font_size, leading
            if page_count <= 1:
                break

        self._build_document(
            self.output_path, quotation_data, selected_size, selected_leading
        )
        return self.output_path

    def _build_story(
        self, data: Dict, comment_font_size: float, comment_leading: float
    ) -> List:
        story = []

        story.extend(self._build_header(data))
        story.append(Spacer(1, 4))

        story.extend(self._build_title_section(data))
        story.append(Spacer(1, 4))

        if data.get("products"):
            story.extend(self._build_products_table(data["products"]))
            story.append(Spacer(1, 4))

        if data.get("accessories"):
            story.extend(self._build_accessories_table(data["accessories"]))
            story.append(Spacer(1, 4))

        if data.get("fixings"):
            story.extend(self._build_fixings_table(data["fixings"]))
            story.append(Spacer(1, 4))

        story.extend(self._build_totals(data["totals"]))
        story.append(Spacer(1, 4))

        story.extend(
            self._build_comments(data.get("comments", []), comment_font_size, comment_leading)
        )
        story.append(Spacer(1, 3))

        story.extend(self._build_banking_info())
        return story

    def _compose_header_title(self, data: Dict) -> str:
        quote_title = str(data.get("quote_title", "Cotización")).upper()
        quote_description = str(data.get("quote_description", "")).strip()
        if quote_description:
            return f"{quote_title} – {quote_description}"
        return quote_title

    def _build_header(self, data: Dict) -> List:
        """Build two-column header [logo | centered title]."""
        elements = []

        logo_flowable = ""
        logo_column_width = 30 * mm
        if self.logo_path:
            try:
                img_width_px, img_height_px = ImageReader(self.logo_path).getSize()
                logo_width = BMCStyles.LOGO_HEIGHT * (img_width_px / float(img_height_px))
                logo_flowable = Image(
                    self.logo_path, width=logo_width, height=BMCStyles.LOGO_HEIGHT
                )
                logo_flowable.hAlign = "LEFT"
                logo_column_width = max(24 * mm, min(55 * mm, logo_width + 1 * mm))
            except Exception:
                logo_flowable = ""

        title_text = escape(self._compose_header_title(data))
        title = Paragraph(title_text, BMCStyles.get_header_title_style())

        header_table = Table(
            [[logo_flowable, title]],
            colWidths=[logo_column_width, self._usable_width - logo_column_width],
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

        metadata_parts = [
            f"Fecha: {QuotationDataFormatter.format_date(data.get('date', ''))}",
            data.get("location", ""),
        ]
        metadata_text = " | ".join([part for part in metadata_parts if part])
        if metadata_text:
            elements.append(Spacer(1, 1))
            elements.append(Paragraph(escape(metadata_text), BMCStyles.get_small_style()))

        return elements

    def _build_title_section(self, data: Dict) -> List:
        """Build client and technical info section."""
        elements = []
        client = data.get("client", {})
        specs = data.get("technical_specs", {})
        normal_style = BMCStyles.get_normal_style()

        elements.append(
            Paragraph(
                f"<b>Cliente:</b> {escape(str(client.get('name', '')))}",
                normal_style,
            )
        )
        if client.get("address"):
            elements.append(
                Paragraph(
                    f"<b>Dirección:</b> {escape(str(client.get('address', '')))}",
                    normal_style,
                )
            )
        if client.get("phone"):
            elements.append(
                Paragraph(
                    f"<b>Tel/cel:</b> {escape(str(client.get('phone', '')))}",
                    normal_style,
                )
            )

        if specs:
            specs_text = (
                f"<b>Autoportancia:</b> {escape(str(specs.get('autoportancia', '')))} m"
                f" &nbsp; | &nbsp; <b>Apoyos:</b> {escape(str(specs.get('apoyos', '')))}"
            )
            elements.append(Paragraph(specs_text, normal_style))

        return elements

    def _build_materials_table(
        self,
        title: Optional[str],
        header: List[str],
        rows: List[List[str]],
        col_widths: List[float],
        numeric_columns: List[int],
    ) -> List:
        elements = []
        if title:
            elements.append(Paragraph(escape(title), BMCStyles.get_section_label_style()))

        table_data = [header] + rows
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            BMCStyles.get_materials_table_style(
                numeric_columns=numeric_columns, total_rows=len(table_data)
            )
        )
        elements.append(table)
        return elements

    def _build_products_table(self, products: List[Dict]) -> List:
        """Build primary materials table."""
        header = ["Material", "Largo (m)", "Cant.", "USD", "Total USD"]
        rows = []
        for product in products:
            length = product.get("Length_m", product.get("length_m", ""))
            total_usd = product.get("total_usd")
            if total_usd in (None, 0):
                total_usd = QuotationDataFormatter.calculate_item_total(product)

            unit_price = product.get("unit_price_usd", product.get("sale_sin_iva", 0))
            rows.append(
                [
                    str(product.get("name", "")),
                    str(length),
                    str(product.get("quantity", "")),
                    QuotationDataFormatter.format_currency(unit_price),
                    QuotationDataFormatter.format_currency(total_usd),
                ]
            )

        w = self._usable_width
        col_widths = [0.44 * w, 0.14 * w, 0.10 * w, 0.14 * w, 0.18 * w]
        return self._build_materials_table(
            title=None,
            header=header,
            rows=rows,
            col_widths=col_widths,
            numeric_columns=[1, 2, 3, 4],
        )

    def _build_accessories_table(self, accessories: List[Dict]) -> List:
        """Build accessories table."""
        header = ["Accesorio", "Largo (m)", "Cant.", "USD", "Total USD"]
        rows = []
        for item in accessories:
            length = item.get("Length_m", item.get("length_m", ""))
            total_usd = item.get("total_usd")
            if total_usd in (None, 0):
                total_usd = QuotationDataFormatter.calculate_item_total(item)

            unit_price = item.get("unit_price_usd", item.get("sale_sin_iva", 0))
            rows.append(
                [
                    str(item.get("name", "")),
                    str(length),
                    str(item.get("quantity", "")),
                    QuotationDataFormatter.format_currency(unit_price),
                    QuotationDataFormatter.format_currency(total_usd),
                ]
            )

        w = self._usable_width
        col_widths = [0.44 * w, 0.14 * w, 0.10 * w, 0.14 * w, 0.18 * w]
        return self._build_materials_table(
            title="ACCESORIOS",
            header=header,
            rows=rows,
            col_widths=col_widths,
            numeric_columns=[1, 2, 3, 4],
        )

    def _build_fixings_table(self, fixings: List[Dict]) -> List:
        """Build fixings/fijaciones table."""
        header = ["Fijación", "Especificación", "Cant.", "USD", "Total USD"]
        rows = []
        for item in fixings:
            total_usd = item.get("total_usd")
            if total_usd in (None, 0):
                total_usd = QuotationDataFormatter.calculate_item_total(item)

            unit_price = item.get("unit_price_usd", item.get("sale_sin_iva", 0))
            rows.append(
                [
                    str(item.get("name", "")),
                    str(item.get("specification", "")),
                    str(item.get("quantity", "")),
                    QuotationDataFormatter.format_currency(unit_price),
                    QuotationDataFormatter.format_currency(total_usd),
                ]
            )

        w = self._usable_width
        col_widths = [0.35 * w, 0.23 * w, 0.10 * w, 0.14 * w, 0.18 * w]
        return self._build_materials_table(
            title="FIJACIONES",
            header=header,
            rows=rows,
            col_widths=col_widths,
            numeric_columns=[2, 3, 4],
        )

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

        w = self._usable_width
        table = Table(data, colWidths=[0.68 * w, 0.32 * w])
        table.setStyle(BMCStyles.get_totals_table_style())
        return [table]

    @staticmethod
    def _normalize_comment(text: str) -> str:
        cleaned = str(text or "").strip()
        cleaned = re.sub(r"^[\*\-\u2022]\s*", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip().lower()

    def _collect_comments(self, comments: List[str]) -> List[str]:
        """Collect comments while ensuring required template text remains available."""
        source_comments = comments or QuotationConstants.get_standard_conditions()
        cleaned_comments = []
        seen = set()

        for line in source_comments:
            clean_line = str(line or "").strip()
            if not clean_line:
                continue
            clean_line = re.sub(r"^[\*\-\u2022]\s*", "", clean_line).strip()
            normalized = self._normalize_comment(clean_line)
            if normalized in seen:
                continue
            seen.add(normalized)
            cleaned_comments.append(clean_line)

        if not any(
            QuotationConstants.SPM_SYSTEM_VIDEO in line for line in cleaned_comments
        ):
            cleaned_comments.append(QuotationConstants.SPM_SYSTEM_VIDEO)

        return cleaned_comments

    def _comment_style_for(
        self, comment: str, font_size: float, leading: float
    ) -> ParagraphStyle:
        normalized = self._normalize_comment(comment)

        bold = False
        text_color = BMCStyles.TEXT_BLACK

        if normalized == self._normalize_comment(self.COMMENT_BOLD_RED_LINE):
            bold = True
            text_color = BMCStyles.EMPHASIS_RED
        elif normalized == self._normalize_comment(self.COMMENT_BOLD_LINE):
            bold = True
        elif normalized == self._normalize_comment(self.COMMENT_RED_LINE):
            text_color = BMCStyles.EMPHASIS_RED

        return BMCStyles.get_comment_style(
            font_size=font_size,
            leading=leading,
            bold=bold,
            text_color=text_color,
        )

    def _build_comments(
        self, comments: List[str], comment_font_size: float, comment_leading: float
    ) -> List:
        """Build COMENTARIOS block with bullet lines and selective formatting."""
        elements = [Paragraph("COMENTARIOS:", BMCStyles.get_section_label_style())]

        for comment in self._collect_comments(comments):
            style = self._comment_style_for(comment, comment_font_size, comment_leading)
            elements.append(Paragraph(f"&bull; {escape(comment)}", style))

        return elements

    def _build_banking_info(self) -> List:
        """Build boxed transfer footer block after comments."""
        base_footer_style = ParagraphStyle(
            "BankFooterBase",
            fontName=BMCStyles.FONT_NAME,
            fontSize=BMCStyles.FONT_SIZE_FOOTER,
            leading=9.4,
            textColor=BMCStyles.TEXT_BLACK,
            spaceAfter=0,
            spaceBefore=0,
        )
        bold_footer_style = ParagraphStyle(
            "BankFooterBold",
            parent=base_footer_style,
            fontName=BMCStyles.FONT_NAME_BOLD,
        )
        link_footer_style = ParagraphStyle(
            "BankFooterLink",
            parent=base_footer_style,
            textColor=BMCStyles.LINK_BLUE,
        )

        rows = [
            [
                Paragraph("Depósito Bancario", bold_footer_style),
                Paragraph(
                    "Titular: Metalog SAS – RUT: 120403430012",
                    base_footer_style,
                ),
            ],
            [
                Paragraph("Caja de Ahorro - BROU.", base_footer_style),
                Paragraph(
                    "Número de Cuenta Dólares : 110520638-00002",
                    base_footer_style,
                ),
            ],
            [
                Paragraph(
                    "Por cualquier duda, consultar al 092 663 245.",
                    base_footer_style,
                ),
                Paragraph(
                    "<u>Lea los Términos y Condiciones</u>",
                    link_footer_style,
                ),
            ],
        ]

        w = self._usable_width
        table = Table(rows, colWidths=[0.42 * w, 0.58 * w])
        table.setStyle(BMCStyles.get_transfer_footer_table_style())
        return [table]


def build_quote_pdf(
    data: Dict,
    output_path: str,
    logo_path: str = "/mnt/data/Logo_BMC- PNG.png",
) -> str:
    """
    Build a quotation PDF using the BMC layout template.

    Args:
        data: Raw quotation payload
        output_path: PDF output path
        logo_path: Preferred BMC logo path (official default)
    """
    formatted_data = QuotationDataFormatter.format_for_pdf(data)
    generator = BMCQuotationPDF(output_path, logo_path=logo_path)
    return generator.generate(formatted_data)


def generate_quotation_pdf(
    quotation_data: Dict,
    output_path: str,
    logo_path: str = "/mnt/data/Logo_BMC- PNG.png",
) -> str:
    """
    Backward-compatible API to generate quotation PDFs.
    """
    return build_quote_pdf(quotation_data, output_path, logo_path=logo_path)
