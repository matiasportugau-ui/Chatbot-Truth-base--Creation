#!/usr/bin/env python3
"""
BMC Uruguay Quotation PDF Generator
====================================

Generates professional quotation PDFs matching the exact structure
and branding of BMC Uruguay's standard quotation template.

Updated 2026-02-09: New Cotización template with:
  A) Header: BMC logo (left) + centered title
  B) Materials table: #EDEDED header, alternating rows, right-aligned numerics
  C) COMENTARIOS section: per-line bold/red formatting
  D) Bank-transfer footer: boxed/ruled grid
  E) 1-page-first logic: shrink comments font/leading before anything else

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
    SimpleDocTemplate,
    TableStyle,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .pdf_styles import BMCStyles, QuotationConstants


# ---------------------------------------------------------------------------
# Comment formatting rules: map substrings -> format type
# ---------------------------------------------------------------------------
# If a comment line contains any of these substrings, apply the given format.
# Order matters: first match wins; "bold_red" is checked before "bold"/"red".
COMMENT_FORMAT_RULES = [
    # bold + red
    (
        "Incluye descuentos de Pago al Contado",
        "bold_red",
    ),
    # bold only
    (
        "Entrega de 10 a 15 días",
        "bold",
    ),
    (
        "dependemos de producción",
        "bold",
    ),
    # red only
    (
        "Oferta válida por 10 días",
        "red",
    ),
]


def _determine_comment_format(text: str) -> str:
    """Return format type for a comment line based on COMMENT_FORMAT_RULES."""
    for substring, fmt in COMMENT_FORMAT_RULES:
        if substring in text:
            return fmt
    return "normal"


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
        - unit_base = 'unidad': quantity * sale_sin_iva
        - unit_base = 'ml': quantity * Length_m * sale_sin_iva
        - unit_base = 'm2': total_m2 * sale_sin_iva

        Args:
            item: Dict with quantity, unit_base, sale_sin_iva, Length_m (optional)

        Returns:
            float: Calculated total
        """
        unit_base = item.get("unit_base", "unidad").lower()

        # Use sale_sin_iva if available, fallback to unit_price_usd
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
        """
        Calculate all financial totals for the quotation.

        LEDGER: Item totals are sin IVA (from sale_sin_iva / unit_price_usd).
        subtotal = sum of items; IVA = subtotal * rate; materials = subtotal + IVA.
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


# ===========================================================================
# BMCQuotationPDF – new template (2026-02-09)
# ===========================================================================

class BMCQuotationPDF:
    """
    Main PDF generator for BMC Uruguay quotations.
    Replicates exact structure from ODS template with new branding.
    """

    def __init__(self, output_path: str, logo_path: Optional[str] = None):
        """
        Initialize PDF generator

        Args:
            output_path: Path where PDF will be saved
            logo_path: Optional explicit logo file path
        """
        self.output_path = output_path
        self.styles = BMCStyles()
        self.constants = QuotationConstants()
        self.logo_path = logo_path or BMCStyles.find_logo_path()

        # Comment font parameters (may be reduced for 1-page fit)
        self._comment_font_size = BMCStyles.FONT_SIZE_COMMENT
        self._comment_leading = BMCStyles.COMMENT_LEADING

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # ── public entry point ──────────────────────────────────────

    def generate(self, quotation_data: Dict) -> str:
        """
        Generate complete quotation PDF.

        Implements 1-page-first rule: if the first attempt overflows,
        progressively shrink comment font/leading and retry
        (up to 4 attempts) before giving up.

        Args:
            quotation_data: Formatted quotation data dictionary

        Returns:
            Path to generated PDF file
        """
        # Try progressively smaller comment font/leading to fit 1 page
        attempts = [
            (BMCStyles.FONT_SIZE_COMMENT, BMCStyles.COMMENT_LEADING),  # 8.1, 9.5
            (7.6, 8.8),
            (7.2, 8.3),
            (6.8, 7.8),
        ]

        for font_size, leading in attempts:
            self._comment_font_size = font_size
            self._comment_leading = leading
            page_count = self._build_pdf(quotation_data)
            if page_count <= 1:
                break

        return self.output_path

    # ── internal build ──────────────────────────────────────────

    def _build_pdf(self, quotation_data: Dict) -> int:
        """Build the PDF and return the number of pages."""

        page_counter = _PageCounter()

        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=BMCStyles.PAGE_SIZE,
            topMargin=BMCStyles.MARGIN_TOP,
            bottomMargin=BMCStyles.MARGIN_BOTTOM,
            leftMargin=BMCStyles.MARGIN_LEFT,
            rightMargin=BMCStyles.MARGIN_RIGHT,
        )

        story = []

        # A) HEADER – logo + title
        story.extend(self._build_header(quotation_data))
        story.append(Spacer(1, 4))

        # Date / location / client info
        story.extend(self._build_title_section(quotation_data))
        story.append(Spacer(1, 4))

        # B/C) MATERIALS TABLE(S)
        if quotation_data.get("products"):
            story.extend(self._build_products_table(quotation_data["products"]))
            story.append(Spacer(1, 3))

        if quotation_data.get("accessories"):
            story.extend(self._build_accessories_table(quotation_data["accessories"]))
            story.append(Spacer(1, 3))

        if quotation_data.get("fixings"):
            story.extend(self._build_fixings_table(quotation_data["fixings"]))
            story.append(Spacer(1, 3))

        # TOTALS
        story.extend(self._build_totals(quotation_data["totals"]))
        story.append(Spacer(1, 5))

        # D) COMENTARIOS
        comments_input = quotation_data.get("comments", [])
        story.extend(self._build_comments(comments_input))
        story.append(Spacer(1, 4))

        # E) BANK TRANSFER FOOTER BOX
        story.extend(self._build_banking_info())

        # Build
        doc.build(story, onFirstPage=page_counter, onLaterPages=page_counter)
        return page_counter.page_count

    # ── A) HEADER ───────────────────────────────────────────────

    def _build_header(self, data: Dict) -> List:
        """
        Build header section: two-column layout [logo | centered title].
        Logo height ~18mm, auto width keeping aspect ratio.
        """
        elements = []

        title_text = data.get("quote_title", "COTIZACIÓN")
        desc = data.get("quote_description", "")
        if desc:
            title_text = f"{title_text} – {desc}"

        title_style = BMCStyles.get_title_style()
        title_para = Paragraph(title_text.upper(), title_style)

        usable_width = BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_LEFT - BMCStyles.MARGIN_RIGHT

        logo_img = None
        logo_col_width = 0

        if self.logo_path and os.path.exists(self.logo_path):
            try:
                from reportlab.lib.utils import ImageReader

                ir = ImageReader(self.logo_path)
                iw, ih = ir.getSize()
                aspect = iw / ih
                logo_h = BMCStyles.LOGO_HEIGHT
                logo_w = logo_h * aspect
                if logo_w > BMCStyles.LOGO_MAX_WIDTH:
                    logo_w = BMCStyles.LOGO_MAX_WIDTH
                    logo_h = logo_w / aspect
                logo_img = Image(self.logo_path, width=logo_w, height=logo_h)
                logo_col_width = logo_w + 6
            except Exception:
                logo_img = None

        if logo_img is not None:
            title_col_width = usable_width - logo_col_width
            header_data = [[logo_img, title_para]]
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
        else:
            # No logo available – just centered title
            elements.append(title_para)

        return elements

    # ── Title / Client section ──────────────────────────────────

    def _build_title_section(self, data: Dict) -> List:
        """Build date, location, and client info."""
        elements = []

        contact_style = BMCStyles.get_small_style()
        normal_style = BMCStyles.get_normal_style()

        # Company contact
        elements.append(
            Paragraph(QuotationConstants.COMPANY_EMAIL, contact_style)
        )
        elements.append(
            Paragraph(QuotationConstants.COMPANY_WEBSITE, contact_style)
        )
        elements.append(
            Paragraph(QuotationConstants.COMPANY_PHONE, contact_style)
        )

        # Date and location
        elements.append(Spacer(1, 2))
        elements.append(
            Paragraph(
                f"Fecha: {QuotationDataFormatter.format_date(data.get('date', ''))}",
                contact_style,
            )
        )
        elements.append(
            Paragraph(data.get("location", ""), contact_style)
        )

        # Technical specs
        specs = data.get("technical_specs", {})
        if specs:
            elements.append(
                Paragraph(
                    f"Autoportancia: {specs.get('autoportancia', 0)} m",
                    contact_style,
                )
            )
            elements.append(
                Paragraph(f"Apoyos: {specs.get('apoyos', 0)}", contact_style)
            )

        # Client
        client = data.get("client", {})
        elements.append(Spacer(1, 3))
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

        return elements

    # ── C) MATERIALS TABLES ─────────────────────────────────────

    def _build_products_table(self, products: List[Dict]) -> List:
        """Build products table with new styling."""
        elements = []
        header = ["Producto", "Largos (m)", "Cantidades", "Costo m² (USD)", "Costo Total (USD)"]
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

        usable_w = BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_LEFT - BMCStyles.MARGIN_RIGHT
        col_ratios = [0.34, 0.13, 0.13, 0.18, 0.22]
        col_widths = [usable_w * r for r in col_ratios]

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(BMCStyles.get_products_table_style(num_data_rows=len(products)))
        elements.append(table)
        return elements

    def _build_accessories_table(self, accessories: List[Dict]) -> List:
        """Build accessories/profiles table"""
        elements = []
        header_style = BMCStyles.get_header_style()
        elements.append(Paragraph("Accesorios", header_style))

        header = ["Producto", "Largo (m)", "Cantidades", "Costo lineal (USD)", "Costo Total (USD)"]
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

        usable_w = BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_LEFT - BMCStyles.MARGIN_RIGHT
        col_ratios = [0.34, 0.13, 0.13, 0.18, 0.22]
        col_widths = [usable_w * r for r in col_ratios]

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(BMCStyles.get_products_table_style(num_data_rows=len(accessories)))
        elements.append(table)
        return elements

    def _build_fixings_table(self, fixings: List[Dict]) -> List:
        """Build fixings/fijaciones table"""
        elements = []
        header_style = BMCStyles.get_header_style()
        elements.append(Paragraph("Fijaciones", header_style))

        header = ["Producto", "Especificación", "Cantidades", "Costo unit. (USD)", "Costo Total (USD)"]
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

        usable_w = BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_LEFT - BMCStyles.MARGIN_RIGHT
        col_ratios = [0.28, 0.18, 0.13, 0.18, 0.23]
        col_widths = [usable_w * r for r in col_ratios]

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(BMCStyles.get_products_table_style(num_data_rows=len(fixings)))
        elements.append(table)
        return elements

    # ── TOTALS ──────────────────────────────────────────────────

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

    # ── D) COMENTARIOS ──────────────────────────────────────────

    def _build_comments(self, comments_input) -> List:
        """
        Build COMENTARIOS section after the table.

        ``comments_input`` may be:
        - A list of strings (legacy) – formatting is auto-detected
        - A list of (text, format) tuples – format is one of
          "normal", "bold", "red", "bold_red"
        - An empty list – default comments from QuotationConstants are used

        Per-line formatting rules:
        - "Entrega de 10 a 15 días, dependemos de producción." -> BOLD
        - "Oferta válida por 10 días a partir de la fecha." -> RED
        - "Incluye descuentos de Pago al Contado. ..." -> BOLD + RED
        """
        elements = []

        # Section title
        header_style = ParagraphStyle(
            "ComentariosHeader",
            fontName=BMCStyles.FONT_NAME_BOLD,
            fontSize=self._comment_font_size + 1.5,
            textColor=BMCStyles.TEXT_BLACK,
            spaceAfter=3,
            spaceBefore=2,
        )
        elements.append(Paragraph("COMENTARIOS:", header_style))

        # Resolve comment lines
        if not comments_input:
            comment_lines = QuotationConstants.DEFAULT_COMMENTS
        else:
            comment_lines = []
            for entry in comments_input:
                if isinstance(entry, (list, tuple)) and len(entry) == 2:
                    comment_lines.append((str(entry[0]), str(entry[1])))
                else:
                    text = str(entry)
                    fmt = _determine_comment_format(text)
                    comment_lines.append((text, fmt))

        # Style factories
        fs = self._comment_font_size
        ld = self._comment_leading
        style_map = {
            "normal": BMCStyles.get_comment_style(fs, ld),
            "bold": BMCStyles.get_comment_bold_style(fs, ld),
            "red": BMCStyles.get_comment_red_style(fs, ld),
            "bold_red": BMCStyles.get_comment_bold_red_style(fs, ld),
        }

        for text, fmt in comment_lines:
            style = style_map.get(fmt, style_map["normal"])
            bullet_char = "\u2022 "  # •
            elements.append(Paragraph(f"{bullet_char}{text}", style))

        return elements

    # ── E) BANK TRANSFER FOOTER BOX ────────────────────────────

    def _build_banking_info(self) -> List:
        """
        Build bank transfer footer as a boxed/ruled grid table.
        Matches the reference image: outer border + internal row lines,
        first row gray background.
        """
        elements = []

        elements.append(Spacer(1, 6))

        # Blue underlined "Lea los Términos y Condiciones"
        terms_text = (
            '<font color="#1155CC"><u>Lea los Términos y Condiciones</u></font>'
        )

        data = [
            # Row 1
            [
                "Depósito Bancario",
                f"Titular: {QuotationConstants.BANK_ACCOUNT_HOLDER} – "
                f"RUT: {QuotationConstants.BANK_RUT}",
            ],
            # Row 2
            [
                f"{QuotationConstants.BANK_ACCOUNT_TYPE} - {QuotationConstants.BANK_NAME}.",
                f"Número de Cuenta Dólares : {QuotationConstants.BANK_ACCOUNT_USD}",
            ],
            # Row 3
            [
                f"Por cualquier duda, consultar al {QuotationConstants.CONTACT_PHONE}.",
                "",  # placeholder – will use Paragraph for blue link
            ],
        ]

        # Use Paragraphs for row 3 right cell (blue+underlined)
        small_style = ParagraphStyle(
            "TransferSmall",
            fontName=BMCStyles.FONT_NAME,
            fontSize=BMCStyles.FONT_SIZE_SMALL,
            textColor=BMCStyles.TEXT_BLACK,
            leading=BMCStyles.FONT_SIZE_SMALL + 2,
        )
        link_style = ParagraphStyle(
            "TransferLink",
            fontName=BMCStyles.FONT_NAME,
            fontSize=BMCStyles.FONT_SIZE_SMALL,
            textColor=BMCStyles.BMC_LINK_BLUE,
            leading=BMCStyles.FONT_SIZE_SMALL + 2,
        )

        # Replace row 3 right cell with Paragraph
        data[2][1] = Paragraph(terms_text, link_style)

        usable_w = BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_LEFT - BMCStyles.MARGIN_RIGHT
        col_widths = [usable_w * 0.42, usable_w * 0.58]

        table = Table(data, colWidths=col_widths)
        table.setStyle(BMCStyles.get_transfer_table_style())

        elements.append(table)
        return elements

    # ── Legacy: build_conditions (kept for backward compat) ────

    def _build_conditions(self, conditions: List[str]) -> List:
        """Build terms and conditions section (legacy)"""
        elements = []
        conditions_style = BMCStyles.get_conditions_style()
        for condition in conditions:
            elements.append(Paragraph(condition, conditions_style))
        return elements


# ===========================================================================
# Page counter helper (for 1-page-fit detection)
# ===========================================================================

class _PageCounter:
    """Callback that counts pages during doc.build()"""

    def __init__(self):
        self.page_count = 0

    def __call__(self, canvas_obj, doc):
        self.page_count = max(self.page_count, doc.page)


# ===========================================================================
# Public convenience functions
# ===========================================================================

def generate_quotation_pdf(
    quotation_data: Dict,
    output_path: str,
    logo_path: Optional[str] = None,
) -> str:
    """
    Generate a BMC Uruguay quotation PDF.

    Args:
        quotation_data: Raw quotation data (will be formatted automatically)
        output_path: Path where PDF should be saved
        logo_path: Optional explicit path to logo image

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
    logo_path: str = "/mnt/data/Logo_BMC- PNG.png",
) -> str:
    """
    Build a complete BMC quotation PDF using the new template.

    This is the canonical entry point referenced by GPT_PDF_INSTRUCTIONS.md.
    It resolves the logo automatically and delegates to generate_quotation_pdf.

    Args:
        data: Raw quotation data dictionary
        output_path: Output file path for the PDF
        logo_path: Path to BMC logo image file

    Returns:
        Path to the generated PDF
    """
    # Resolve logo: try explicit path, then fallback
    resolved_logo = logo_path if os.path.exists(logo_path) else BMCStyles.find_logo_path()
    return generate_quotation_pdf(data, output_path, logo_path=resolved_logo)
