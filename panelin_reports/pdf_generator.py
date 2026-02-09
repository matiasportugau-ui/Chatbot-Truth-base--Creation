#!/usr/bin/env python3
"""
BMC Uruguay Quotation PDF Generator
====================================

Generates professional quotation PDFs matching the exact structure
and branding of BMC Uruguay's standard quotation template.

Based on: Cotización 01042025 BASE - Isopanel xx mm - Isodec EPS xx mm -desc- WA.ods
"""

import io
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from xml.sax.saxutils import escape

from .pdf_styles import BMCStyles, QuotationConstants


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


OFFICIAL_BMC_LOGO_PATH = "/mnt/data/Logo_BMC- PNG.png"


class BMCQuotationPDF:
    """
    PDF quotation template focused on visual layout:
    header + materials table + comments + bank transfer footer.
    """

    COMMENT_BOLD_LINE = "Entrega de 10 a 15 días, dependemos de producción."
    COMMENT_RED_LINE = "Oferta válida por 10 días a partir de la fecha."
    COMMENT_BOLD_RED_LINE = (
        "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). "
        "Saldo del 40 % (previo a retiro de fábrica)."
    )
    DEFAULT_TEMPLATE_COMMENTS = [
        COMMENT_BOLD_LINE,
        COMMENT_RED_LINE,
        COMMENT_BOLD_RED_LINE,
        QuotationConstants.SPM_SYSTEM_VIDEO,
    ]
    COMMENT_FIT_STEPS: List[Tuple[float, float]] = [
        (8.2, 9.6),
        (8.0, 9.4),
        (7.8, 9.2),
        (7.6, 9.0),
        (7.4, 8.8),
    ]

    def __init__(self, output_path: str, logo_path: str = OFFICIAL_BMC_LOGO_PATH):
        self.output_path = output_path
        self.logo_path = logo_path or OFFICIAL_BMC_LOGO_PATH
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def generate(self, quotation_data: Dict) -> str:
        """
        Generate quotation PDF trying to keep it on one page.
        If needed, only comments typography is reduced first.
        """
        selected_pdf = b""
        for comment_font_size, comment_leading in self.COMMENT_FIT_STEPS:
            pdf_bytes, page_count = self._build_pdf_bytes(
                quotation_data=quotation_data,
                comment_font_size=comment_font_size,
                comment_leading=comment_leading,
            )
            selected_pdf = pdf_bytes
            if page_count <= 1:
                break

        Path(self.output_path).write_bytes(selected_pdf)
        return self.output_path

    def _build_pdf_bytes(
        self,
        quotation_data: Dict,
        comment_font_size: float,
        comment_leading: float,
    ) -> Tuple[bytes, int]:
        """Build a PDF in-memory and report resulting page count."""
        pdf_buffer = io.BytesIO()
        page_counter: Dict[str, int] = {}

        class _CountingCanvas(canvas.Canvas):
            def save(self_inner) -> None:
                page_counter["pages"] = self_inner.getPageNumber()
                super().save()

        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            leftMargin=12 * mm,
            rightMargin=12 * mm,
            topMargin=10 * mm,
            bottomMargin=9 * mm,
        )

        story = self._build_story(
            quotation_data=quotation_data,
            doc_width=doc.width,
            comment_font_size=comment_font_size,
            comment_leading=comment_leading,
        )
        doc.build(story, canvasmaker=_CountingCanvas)
        return pdf_buffer.getvalue(), page_counter.get("pages", 1)

    def _build_story(
        self,
        quotation_data: Dict,
        doc_width: float,
        comment_font_size: float,
        comment_leading: float,
    ) -> List:
        elements: List[Any] = []
        elements.extend(self._build_header(quotation_data, doc_width))
        elements.append(Spacer(1, 2.5 * mm))
        elements.extend(self._build_client_meta(quotation_data, doc_width))
        elements.append(Spacer(1, 2.5 * mm))
        elements.extend(self._build_materials_table(quotation_data, doc_width))
        elements.append(Spacer(1, 2.0 * mm))
        elements.extend(
            self._build_comments(
                quotation_data=quotation_data,
                comment_font_size=comment_font_size,
                comment_leading=comment_leading,
            )
        )
        elements.append(Spacer(1, 1.8 * mm))
        elements.extend(self._build_bank_transfer_footer(doc_width))
        return elements

    def _build_header(self, data: Dict, doc_width: float) -> List:
        """Build two-column header: [logo | centered title]."""
        title_style = ParagraphStyle(
            "QuoteTitle",
            fontName=BMCStyles.FONT_NAME_BOLD,
            fontSize=13.8,
            leading=15.0,
            alignment=1,
            textColor=colors.HexColor("#111111"),
            spaceAfter=0,
            spaceBefore=0,
        )

        logo_cell = self._build_logo_flowable(target_height=18 * mm, max_width=54 * mm)
        title_cell = Paragraph(escape(self._resolve_document_title(data)), title_style)

        table = Table(
            [[logo_cell, title_cell]],
            colWidths=[54 * mm, doc_width - (54 * mm)],
        )
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return [table]

    def _build_logo_flowable(self, target_height: float, max_width: float):
        """Return official logo image with preserved aspect ratio."""
        if not self.logo_path or not os.path.exists(self.logo_path):
            return Spacer(1, target_height)

        try:
            image_reader = ImageReader(self.logo_path)
            img_width_px, img_height_px = image_reader.getSize()
            if img_width_px <= 0 or img_height_px <= 0:
                return Spacer(1, target_height)

            scaled_width = target_height * (img_width_px / img_height_px)
            scaled_height = target_height
            if scaled_width > max_width:
                scaled_width = max_width
                scaled_height = scaled_width * (img_height_px / img_width_px)

            return Image(
                self.logo_path,
                width=scaled_width,
                height=scaled_height,
                hAlign="LEFT",
            )
        except Exception:
            return Spacer(1, target_height)

    def _resolve_document_title(self, data: Dict) -> str:
        description = (data.get("quote_description") or "").strip()
        if description:
            return f"COTIZACIÓN – {description}"

        quote_title = (data.get("quote_title") or "").strip()
        if quote_title and quote_title.lower() != "cotización":
            return f"COTIZACIÓN – {quote_title}"

        return "COTIZACIÓN – ISODEC EPS 100 mm"

    def _build_client_meta(self, data: Dict, doc_width: float) -> List:
        """Compact metadata row below header."""
        client = data.get("client", {})
        meta_style = ParagraphStyle(
            "MetaSmall",
            fontName=BMCStyles.FONT_NAME,
            fontSize=8.2,
            leading=9.0,
            textColor=colors.HexColor("#333333"),
        )

        cells = [
            Paragraph(f"<b>Cliente:</b> {escape(client.get('name', '') or '-')}", meta_style),
            Paragraph(
                f"<b>Tel:</b> {escape(client.get('phone', '') or '-')}",
                meta_style,
            ),
            Paragraph(
                f"<b>Fecha:</b> {escape(QuotationDataFormatter.format_date(data.get('date', '')))}",
                meta_style,
            ),
        ]
        table = Table([cells], colWidths=[doc_width * 0.50, doc_width * 0.23, doc_width * 0.27])
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return [table]

    def _build_materials_table(self, data: Dict, doc_width: float) -> List:
        """Build styled materials table with repeat header row."""
        header = ["Material", "Unid", "Cant", "USD", "Total"]
        table_rows = [header]

        for row in self._iter_material_rows(data):
            table_rows.append(row)

        if len(table_rows) == 1:
            table_rows.append(["Sin materiales", "", "", "$0.00", "$0.00"])

        table = Table(
            table_rows,
            colWidths=[
                doc_width * 0.49,
                doc_width * 0.10,
                doc_width * 0.11,
                doc_width * 0.15,
                doc_width * 0.15,
            ],
            repeatRows=1,
        )

        table_style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDEDED")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111111")),
            ("FONTNAME", (0, 0), (-1, 0), BMCStyles.FONT_NAME_BOLD),
            ("FONTSIZE", (0, 0), (-1, 0), 9.1),
            ("FONTNAME", (0, 1), (-1, -1), BMCStyles.FONT_NAME),
            ("FONTSIZE", (0, 1), (-1, -1), 8.6),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7D7D7")),
            ("TOPPADDING", (0, 0), (-1, -1), 2.0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.0),
            ("LEFTPADDING", (0, 0), (-1, -1), 3.0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3.0),
        ]

        for row_idx in range(1, len(table_rows)):
            bg_color = colors.white if row_idx % 2 else colors.HexColor("#FAFAFA")
            table_style.append(("BACKGROUND", (0, row_idx), (-1, row_idx), bg_color))

        table.setStyle(TableStyle(table_style))
        return [table]

    def _iter_material_rows(self, data: Dict) -> List[List[str]]:
        rows: List[List[str]] = []
        for section_key in ("products", "accessories", "fixings"):
            for item in data.get(section_key, []):
                total_usd = item.get("total_usd")
                if total_usd is None or total_usd == 0:
                    total_usd = QuotationDataFormatter.calculate_item_total(item)

                description = (item.get("name") or "").strip()
                specification = (item.get("specification") or "").strip()
                if specification:
                    description = f"{description} ({specification})"

                unit_price = item.get("unit_price_usd", item.get("sale_sin_iva", 0))
                quantity = item.get("quantity", "")

                rows.append(
                    [
                        description,
                        self._resolve_unit_label(item),
                        self._format_quantity(quantity),
                        QuotationDataFormatter.format_currency(float(unit_price or 0)),
                        QuotationDataFormatter.format_currency(float(total_usd or 0)),
                    ]
                )

        return rows

    def _resolve_unit_label(self, item: Dict) -> str:
        unit_base = (item.get("unit_base") or "unidad").strip().lower()
        if unit_base in ("m2", "m²"):
            return "m²"
        if unit_base == "ml":
            return "ml"
        if unit_base == "unidad":
            return "Unid"
        return unit_base

    def _format_quantity(self, quantity: Any) -> str:
        if isinstance(quantity, int):
            return str(quantity)
        if isinstance(quantity, float):
            return f"{quantity:.2f}".rstrip("0").rstrip(".")
        return str(quantity)

    def _build_comments(
        self, quotation_data: Dict, comment_font_size: float, comment_leading: float
    ) -> List:
        elements: List[Any] = []
        section_style = ParagraphStyle(
            "CommentsHeader",
            fontName=BMCStyles.FONT_NAME_BOLD,
            fontSize=8.8,
            leading=9.6,
            textColor=colors.HexColor("#111111"),
            spaceAfter=1.6,
        )
        elements.append(Paragraph("COMENTARIOS:", section_style))

        base_comment_style = ParagraphStyle(
            "CommentLine",
            fontName=BMCStyles.FONT_NAME,
            fontSize=comment_font_size,
            leading=comment_leading,
            textColor=colors.HexColor("#222222"),
            spaceAfter=0.8,
        )

        for raw_line in self._compose_comments(quotation_data):
            line = raw_line.strip()
            if not line:
                continue

            normalized = self._normalize_comment(line)
            font_name = BMCStyles.FONT_NAME
            color = "#222222"

            if normalized == self.COMMENT_BOLD_LINE:
                font_name = BMCStyles.FONT_NAME_BOLD
            elif normalized == self.COMMENT_RED_LINE:
                color = "#C92828"
            elif normalized == self.COMMENT_BOLD_RED_LINE:
                font_name = BMCStyles.FONT_NAME_BOLD
                color = "#C92828"

            bullet_text = (
                f'<font name="{font_name}" color="{color}">• {escape(line)}</font>'
            )
            elements.append(Paragraph(bullet_text, base_comment_style))

        return elements

    def _compose_comments(self, quotation_data: Dict) -> List[str]:
        comments: List[str] = []
        seen = set()

        def _push(line: str) -> None:
            cleaned = line.strip()
            if not cleaned:
                return
            normalized = self._normalize_comment(cleaned)
            if normalized in seen:
                return
            seen.add(normalized)
            comments.append(cleaned)

        for template_line in self.DEFAULT_TEMPLATE_COMMENTS:
            _push(template_line)

        for user_line in quotation_data.get("comments", []):
            _push(user_line)

        return comments

    def _normalize_comment(self, text: str) -> str:
        cleaned = text.strip().lstrip("*").lstrip("•").strip()
        return " ".join(cleaned.split())

    def _build_bank_transfer_footer(self, doc_width: float) -> List:
        """Build boxed transfer block with gray first row and inner rules."""
        small_style = ParagraphStyle(
            "BankInfoSmall",
            fontName=BMCStyles.FONT_NAME,
            fontSize=8.4,
            leading=9.2,
            textColor=colors.HexColor("#1E1E1E"),
        )

        bank_rows = [
            [
                Paragraph("<b>Depósito Bancario</b>", small_style),
                Paragraph(
                    "Titular: Metalog SAS – RUT: 120403430012",
                    small_style,
                ),
            ],
            [
                Paragraph("Caja de Ahorro - BROU.", small_style),
                Paragraph(
                    "Número de Cuenta Dólares : 110520638-00002",
                    small_style,
                ),
            ],
            [
                Paragraph("Por cualquier duda, consultar al 092 663 245.", small_style),
                Paragraph(
                    (
                        f'<link href="{escape(QuotationConstants.TERMS_CONDITIONS_URL)}">'
                        '<font color="#1D5FD0"><u>Lea los Términos y Condiciones</u></font>'
                        "</link>"
                    ),
                    small_style,
                ),
            ],
        ]

        table = Table(bank_rows, colWidths=[doc_width * 0.38, doc_width * 0.62])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDEDED")),
                    ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor("#AAAAAA")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C6C6C6")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2.0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.0),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3.0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3.0),
                ]
            )
        )
        return [table]


def build_quote_pdf(
    data: Dict,
    output_path: str,
    logo_path: str = OFFICIAL_BMC_LOGO_PATH,
) -> str:
    """
    Build quotation PDF with BMC layout template.
    Accepts either raw quotation data or pre-formatted data.
    """
    formatted_data = (
        data
        if ("client" in data and "totals" in data)
        else QuotationDataFormatter.format_for_pdf(data)
    )
    generator = BMCQuotationPDF(output_path, logo_path=logo_path)
    return generator.generate(formatted_data)


# Convenience function for backward compatibility
def generate_quotation_pdf(
    quotation_data: Dict,
    output_path: str,
    logo_path: str = OFFICIAL_BMC_LOGO_PATH,
) -> str:
    """
    Generate a BMC quotation PDF using the unified template.
    """
    return build_quote_pdf(
        data=quotation_data,
        output_path=output_path,
        logo_path=logo_path,
    )
