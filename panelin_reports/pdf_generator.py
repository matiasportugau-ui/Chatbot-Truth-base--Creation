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
import unicodedata
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .pdf_styles import BMCStyles, QuotationConstants

OFFICIAL_BMC_LOGO_PATH = "/mnt/data/Logo_BMC- PNG.png"

TABLE_HEADER_BG = colors.HexColor("#EDEDED")
TABLE_ALT_ROW_BG = colors.HexColor("#FAFAFA")
TABLE_GRID_COLOR = colors.HexColor("#D2D2D2")
COMMENT_RED = colors.HexColor("#C62828")
CONTENT_WIDTH = A4[0] - (24 * mm)  # 12mm left + 12mm right margins


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
        except Exception:
            return date_str


class _PageCounterCanvas(canvas.Canvas):
    """Captures rendered page count for 1-page-first strategy."""

    last_page_count = 1

    def save(self) -> None:
        type(self).last_page_count = self.getPageNumber()
        super().save()


class BMCQuotationPDF:
    """
    Main PDF generator for BMC Uruguay quotations.
    PDF template focused on formal one-page quotation layout.
    """

    def __init__(self, output_path: str, logo_path: str = OFFICIAL_BMC_LOGO_PATH):
        """
        Initialize PDF generator

        Args:
            output_path: Path where PDF will be saved
            logo_path: Preferred logo path (official BMC logo by default)
        """
        self.output_path = output_path
        self.logo_path = logo_path

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def generate(self, quotation_data: Dict) -> str:
        """
        Generate complete quotation PDF.
        Tries to fit in one page by reducing only comments font/leading first.
        """
        comments_profiles: Sequence[Tuple[float, float]] = (
            (8.2, 9.6),
            (8.0, 9.4),
            (7.8, 9.2),
            (7.6, 9.0),
            (7.4, 8.8),
        )

        selected_profile = comments_profiles[-1]
        for profile in comments_profiles:
            pages = self._build_pdf(
                quotation_data,
                comment_font_size=profile[0],
                comment_leading=profile[1],
                destination=io.BytesIO(),
            )
            selected_profile = profile
            if pages <= 1:
                break

        self._build_pdf(
            quotation_data,
            comment_font_size=selected_profile[0],
            comment_leading=selected_profile[1],
            destination=self.output_path,
        )
        return self.output_path

    def _build_pdf(
        self,
        data: Dict,
        comment_font_size: float,
        comment_leading: float,
        destination,
    ) -> int:
        doc = SimpleDocTemplate(
            destination,
            pagesize=A4,
            topMargin=10 * mm,
            bottomMargin=9 * mm,
            leftMargin=12 * mm,
            rightMargin=12 * mm,
        )
        story = self._build_story(data, comment_font_size, comment_leading)
        _PageCounterCanvas.last_page_count = 1
        doc.build(story, canvasmaker=_PageCounterCanvas)
        return _PageCounterCanvas.last_page_count

    def _build_story(
        self, data: Dict, comment_font_size: float, comment_leading: float
    ) -> List:
        story: List = []
        story.extend(self._build_header(data))
        story.append(Spacer(1, 2 * mm))

        story.extend(self._build_meta_row(data))
        story.append(Spacer(1, 2 * mm))

        story.extend(self._build_materials_table(data))
        story.append(Spacer(1, 2 * mm))

        story.extend(self._build_comments(data, comment_font_size, comment_leading))
        story.append(Spacer(1, 1.5 * mm))

        story.extend(self._build_bank_transfer_footer())
        return story

    def _build_header(self, data: Dict) -> List:
        """Build two-column header [logo | centered title]."""
        logo = self._build_logo_flowable()
        title_style = ParagraphStyle(
            "BMCHeaderTitle",
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=16.5,
            alignment=1,  # centered
            textColor=colors.black,
        )
        title = Paragraph(escape(self._build_title_text(data)), title_style)

        table = Table(
            [[logo, title]],
            colWidths=[42 * mm, CONTENT_WIDTH - (42 * mm)],
        )
        table.setStyle(
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
        return [table]

    def _build_meta_row(self, data: Dict) -> List:
        """Compact quotation metadata row."""
        client = data.get("client", {})
        client_name = escape(str(client.get("name", "")))
        date_value = QuotationDataFormatter.format_date(data.get("date", ""))

        meta_style = ParagraphStyle(
            "BMCMeta",
            fontName="Helvetica",
            fontSize=8.5,
            leading=9.4,
            textColor=colors.black,
        )
        left_text = f"<b>Cliente:</b> {client_name}"
        right_text = f"<b>Fecha:</b> {escape(date_value)}"

        table = Table(
            [[Paragraph(left_text, meta_style), Paragraph(right_text, meta_style)]],
            colWidths=[CONTENT_WIDTH * 0.68, CONTENT_WIDTH * 0.32],
        )
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return [table]

    def _build_materials_table(self, data: Dict) -> List:
        """Build materials table with required styling."""
        rows: List[List[str]] = [["Material", "Unid", "Cant", "USD", "Total"]]

        for item in self._collect_material_items(data):
            unit_price = item.get("unit_price_usd", item.get("sale_sin_iva", 0))
            total_usd = item.get("total_usd")
            if total_usd is None:
                total_usd = QuotationDataFormatter.calculate_item_total(item)

            rows.append(
                [
                    str(item.get("name", "")),
                    str(item.get("unit_base", "Unid")),
                    self._format_quantity(item.get("quantity", "")),
                    QuotationDataFormatter.format_currency(unit_price),
                    QuotationDataFormatter.format_currency(total_usd),
                ]
            )

        if len(rows) == 1:
            rows.append(["Sin materiales", "", "", "", ""])

        totals = data.get("totals", {})
        totals_start_index = len(rows)
        if totals:
            rows.extend(
                [
                    [
                        "Sub-Total",
                        "",
                        "",
                        "",
                        QuotationDataFormatter.format_currency(totals.get("subtotal", 0)),
                    ],
                    [
                        f"IVA {int(totals.get('iva_rate', QuotationConstants.IVA_RATE) * 100)}%",
                        "",
                        "",
                        "",
                        QuotationDataFormatter.format_currency(totals.get("iva", 0)),
                    ],
                    [
                        "Materiales",
                        "",
                        "",
                        "",
                        QuotationDataFormatter.format_currency(
                            totals.get("materials_total", 0)
                        ),
                    ],
                    [
                        "Traslado",
                        "",
                        "",
                        "",
                        QuotationDataFormatter.format_currency(totals.get("shipping", 0)),
                    ],
                    [
                        "TOTAL U$S",
                        "",
                        "",
                        "",
                        QuotationDataFormatter.format_currency(
                            totals.get("grand_total", 0)
                        ),
                    ],
                ]
            )

        table = Table(
            rows,
            colWidths=[106 * mm, 14 * mm, 14 * mm, 26 * mm, 26 * mm],
            repeatRows=1,
        )

        styles = [
            ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BG),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9.1),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8.6),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.35, TABLE_GRID_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, TABLE_ALT_ROW_BG]),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 2.2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ]

        if totals:
            styles.extend(
                [
                    ("FONTNAME", (0, totals_start_index), (-1, -1), "Helvetica-Bold"),
                    (
                        "BACKGROUND",
                        (0, len(rows) - 1),
                        (-1, len(rows) - 1),
                        colors.HexColor("#F2F2F2"),
                    ),
                ]
            )

        table.setStyle(TableStyle(styles))
        return [table]

    def _build_comments(
        self, data: Dict, comment_font_size: float, comment_leading: float
    ) -> List:
        """Build COMENTARIOS block with per-line style rules."""
        elements: List = []

        title_style = ParagraphStyle(
            "CommentsTitle",
            fontName="Helvetica-Bold",
            fontSize=9.4,
            leading=10.4,
            textColor=colors.black,
            spaceAfter=1.2 * mm,
        )
        elements.append(Paragraph("COMENTARIOS:", title_style))

        base_style = ParagraphStyle(
            "CommentsBase",
            fontName="Helvetica",
            fontSize=comment_font_size,
            leading=comment_leading,
            textColor=colors.black,
            spaceAfter=0.4 * mm,
        )

        for idx, comment in enumerate(self._collect_comment_lines(data)):
            style = self._comment_line_style(base_style, comment, idx)
            elements.append(Paragraph(f"&#8226; {escape(comment)}", style))

        return elements

    def _build_bank_transfer_footer(self) -> List:
        """Build transfer footer boxed grid exactly as requested."""
        cell_style = ParagraphStyle(
            "BankCell",
            fontName="Helvetica",
            fontSize=8.4,
            leading=9.4,
            textColor=colors.black,
        )
        rows = [
            [
                Paragraph("<b>Depósito Bancario</b>", cell_style),
                Paragraph("Titular: Metalog SAS – RUT: 120403430012", cell_style),
            ],
            [
                Paragraph("Caja de Ahorro - BROU.", cell_style),
                Paragraph("Número de Cuenta Dólares : 110520638-00002", cell_style),
            ],
            [
                Paragraph("Por cualquier duda, consultar al 092 663 245.", cell_style),
                Paragraph(
                    '<font color="#1F5FBF"><u>Lea los Términos y Condiciones</u></font>',
                    cell_style,
                ),
            ],
        ]

        table = Table(rows, colWidths=[69 * mm, CONTENT_WIDTH - (69 * mm)])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BG),
                    ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#B8B8B8")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2.6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2.6),
                    ("TOPPADDING", (0, 0), (-1, -1), 1.8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
                ]
            )
        )
        return [table]

    def _build_logo_flowable(self):
        logo_path = self._resolve_logo_path()
        if not logo_path:
            return Spacer(1, 18 * mm)
        return Image(logo_path, width=42 * mm, height=18 * mm, kind="proportional")

    def _resolve_logo_path(self) -> Optional[str]:
        # Use official logo first; fallback to legacy logo path only if needed.
        candidates = [self.logo_path, OFFICIAL_BMC_LOGO_PATH, BMCStyles.LOGO_PATH]
        for candidate in candidates:
            if candidate and os.path.exists(candidate):
                return candidate
        return None

    def _build_title_text(self, data: Dict) -> str:
        title = str(data.get("quote_title", "COTIZACIÓN")).strip() or "COTIZACIÓN"
        description = str(data.get("quote_description", "")).strip()
        if description:
            return f"{title.upper()} – {description}"
        return title.upper()

    def _collect_material_items(self, data: Dict) -> List[Dict]:
        items: List[Dict] = []
        items.extend(data.get("products", []))
        items.extend(data.get("accessories", []))
        items.extend(data.get("fixings", []))
        return items

    def _collect_comment_lines(self, data: Dict) -> List[str]:
        source: List[str] = []
        source.extend(data.get("comments") or [])
        source.extend(data.get("conditions") or [])
        lines: List[str] = []

        for line in source:
            if not isinstance(line, str):
                continue
            for piece in line.split("*"):
                clean = " ".join(piece.strip().split())
                if clean:
                    lines.append(clean)

        if not any("youtu" in line.lower() for line in lines):
            lines.append(QuotationConstants.SPM_SYSTEM_VIDEO)

        required_lines = [
            "Entrega de 10 a 15 días, dependemos de producción.",
            "Oferta válida por 10 días a partir de la fecha.",
            (
                "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). "
                "Saldo del 40 % (previo a retiro de fábrica)."
            ),
        ]
        folded_lines = {self._fold_text(line) for line in lines}
        for line in required_lines:
            if self._fold_text(line) not in folded_lines:
                lines.append(line)
                folded_lines.add(self._fold_text(line))

        seen = set()
        deduplicated = []
        for line in lines:
            key = self._fold_text(line)
            if key in seen:
                continue
            seen.add(key)
            deduplicated.append(line)
        return deduplicated

    def _comment_line_style(
        self, base_style: ParagraphStyle, line: str, index: int
    ) -> ParagraphStyle:
        style = ParagraphStyle(f"CommentLine{index}", parent=base_style)
        normalized = self._fold_text(line)

        delivery_line = self._fold_text(
            "Entrega de 10 a 15 días, dependemos de producción."
        )
        offer_line = self._fold_text("Oferta válida por 10 días a partir de la fecha.")
        discount_line = self._fold_text(
            "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). "
            "Saldo del 40 % (previo a retiro de fábrica)."
        )

        if delivery_line in normalized:
            style.fontName = "Helvetica-Bold"
        if offer_line in normalized:
            style.textColor = COMMENT_RED
        if discount_line in normalized:
            style.fontName = "Helvetica-Bold"
            style.textColor = COMMENT_RED
        return style

    @staticmethod
    def _fold_text(text: str) -> str:
        compact = " ".join(text.strip().lower().split())
        normalized = unicodedata.normalize("NFD", compact)
        return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")

    @staticmethod
    def _format_quantity(quantity) -> str:
        if isinstance(quantity, (int, float)):
            if isinstance(quantity, float) and not quantity.is_integer():
                return f"{quantity:.2f}"
            return str(int(quantity))
        return str(quantity)


def build_quote_pdf(
    data: Dict,
    output_path: str,
    logo_path: str = OFFICIAL_BMC_LOGO_PATH,
) -> str:
    """
    Build quotation PDF with BMC branded layout.

    Args:
        data: Raw quotation data or pre-formatted quotation data
        output_path: Path where PDF should be saved
        logo_path: Preferred logo path (defaults to official BMC logo)
    """
    formatted_data = (
        data
        if "totals" in data and "client" in data
        else QuotationDataFormatter.format_for_pdf(data)
    )
    generator = BMCQuotationPDF(output_path=output_path, logo_path=logo_path)
    return generator.generate(formatted_data)


# Convenience function for backward compatibility
def generate_quotation_pdf(quotation_data: Dict, output_path: str) -> str:
    """
    Generate a BMC Uruguay quotation PDF.
    """
    return build_quote_pdf(
        quotation_data,
        output_path,
        logo_path=OFFICIAL_BMC_LOGO_PATH,
    )
