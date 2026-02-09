#!/usr/bin/env python3
"""
BMC Uruguay Quotation PDF Generator
====================================

Generates professional quotation PDFs matching the exact structure
and branding of BMC Uruguay's standard quotation template.

Based on: Cotización 01042025 BASE - Isopanel xx mm - Isodec EPS xx mm -desc- WA.ods
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, Paragraph, Spacer, Image, PageBreak
from reportlab.platypus import SimpleDocTemplate, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader

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


class BMCQuotationPDF:
    """
    Main PDF generator for BMC Uruguay quotations.
    Replicates exact structure from ODS template.
    """

    def __init__(self, output_path: str):
        """
        Initialize PDF generator

        Args:
            output_path: Path where PDF will be saved
        """
        self.output_path = output_path
        self.styles = BMCStyles()
        self.constants = QuotationConstants()

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def generate(self, quotation_data: Dict) -> str:
        """
        Generate complete quotation PDF (NEW TEMPLATE)

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
        story = []

        # Header section (logo + centered title)
        story.extend(self._build_header(quotation_data))
        story.append(Spacer(1, 8))

        # Materials table (combined products, accessories, fixings)
        story.extend(self._build_materials_table(quotation_data))
        story.append(Spacer(1, 8))

        # Totals section
        story.extend(self._build_totals(quotation_data["totals"]))
        story.append(Spacer(1, 8))

        # COMENTARIOS section (after table, with formatting rules)
        # Start with base font size, will reduce if needed
        comments = self._get_standard_comments()
        story.extend(self._build_comments(comments, font_size=None, leading=None))
        story.append(Spacer(1, 6))

        # Bank transfer footer box
        story.extend(self._build_banking_info())

        # Build PDF
        # TODO: Implement 1-page-first logic (try build, if >1 page, reduce comments font)
        doc.build(story)

        return self.output_path

    def _build_materials_table(self, data: Dict) -> List:
        """Build unified materials table (products, accessories, fixings)"""
        elements = []

        # Table header
        header = [
            "MATERIALES",
            "Unid",
            "Cant",
            "USD",
            "Total USD",
        ]

        # Table data
        table_data = [header]
        
        # Add products
        for product in data.get("products", []):
            length = product.get("Length_m", product.get("length_m", ""))
            total_usd = product.get("total_usd")
            if total_usd is None or total_usd == 0:
                total_usd = QuotationDataFormatter.calculate_item_total(product)

            row = [
                product.get("name", ""),
                "m²" if "Fachada" in product.get("name", "") or "Cubierta" in product.get("name", "") else "unid",
                str(product.get("quantity", "")),
                QuotationDataFormatter.format_currency(product.get("unit_price_usd", 0)),
                QuotationDataFormatter.format_currency(total_usd),
            ]
            table_data.append(row)

        # Add accessories
        for item in data.get("accessories", []):
            length = item.get("Length_m", item.get("length_m", ""))
            total_usd = item.get("total_usd")
            if total_usd is None or total_usd == 0:
                total_usd = QuotationDataFormatter.calculate_item_total(item)

            row = [
                item.get("name", ""),
                "ml",
                str(item.get("quantity", "")),
                QuotationDataFormatter.format_currency(item.get("unit_price_usd", 0)),
                QuotationDataFormatter.format_currency(total_usd),
            ]
            table_data.append(row)

        # Add fixings
        for item in data.get("fixings", []):
            total_usd = item.get("total_usd")
            if total_usd is None or total_usd == 0:
                total_usd = QuotationDataFormatter.calculate_item_total(item)

            row = [
                item.get("name", ""),
                "unid",
                str(item.get("quantity", "")),
                QuotationDataFormatter.format_currency(item.get("unit_price_usd", 0)),
                QuotationDataFormatter.format_currency(total_usd),
            ]
            table_data.append(row)

        # Create table
        table = Table(table_data, colWidths=[250, 40, 40, 70, 80])
        table.setStyle(BMCStyles.get_products_table_style())
        table.hAlign = "LEFT"

        elements.append(table)
        return elements

    def _get_standard_comments(self) -> List[str]:
        """Get standard comments for quotation"""
        return [
            "Entrega de 10 a 15 días, dependemos de producción.",
            "Oferta válida por 10 días a partir de la fecha.",
            "Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).",
            "Con tarjeta de crédito y en cuotas, sería en $ y a través de Mercado Pago con un recargo de 11,9% (comisión MP).",
            "Retiro sin cargo en Planta Industrial de Bromyros S.A. (Colonia Nicolich / CANELONES)",
            "Para saber más del sistema constructivo SPM: https://youtu.be/Am4mZskFMgc",
        ]

    def _build_header(self, data: Dict) -> List:
        """Build header section with logo and centered title (NEW TEMPLATE)"""
        elements = []

        # Logo path resolution
        logo_path = BMCStyles.LOGO_PATH
        # Also check absolute path for GPT environment
        if not os.path.exists(logo_path):
            abs_logo_path = os.path.join(os.path.dirname(__file__), "assets", "bmc_logo.png")
            if os.path.exists(abs_logo_path):
                logo_path = abs_logo_path

        # Build header table: [logo | centered title]
        if os.path.exists(logo_path):
            # Load logo with auto aspect ratio
            from reportlab.lib.utils import ImageReader
            img_reader = ImageReader(logo_path)
            img_width, img_height = img_reader.getSize()
            aspect = img_width / float(img_height)
            logo_height = BMCStyles.LOGO_HEIGHT
            logo_width = logo_height * aspect
            
            logo = Image(logo_path, width=logo_width, height=logo_height)
            
            # Centered title
            title_style = ParagraphStyle(
                "HeaderTitle",
                fontName=BMCStyles.FONT_NAME_BOLD,
                fontSize=BMCStyles.FONT_SIZE_TITLE,
                textColor=BMCStyles.TEXT_BLACK,
                alignment=1,  # Center
            )
            
            # Dynamic title or default
            title_text = data.get("quote_description", "ISODEC EPS 100 mm")
            title_para = Paragraph(f"<b>COTIZACIÓN – {title_text}</b>", title_style)
            
            # Create 2-column header table
            header_table_data = [[logo, title_para]]
            header_table = Table(header_table_data, colWidths=[logo_width + 10*mm, None])
            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ]))
            elements.append(header_table)
        else:
            # Fallback: just title
            title_style = BMCStyles.get_title_style()
            title_text = data.get("quote_description", "ISODEC EPS 100 mm")
            elements.append(Paragraph(f"COTIZACIÓN – {title_text}", title_style))

        return elements

    def _build_title_section(self, data: Dict) -> List:
        """Build client information section (title now in header)"""
        elements = []

        # Client information (minimal, inline)
        client = data.get("client", {})
        small_style = BMCStyles.get_small_style()

        if client.get("name"):
            elements.append(
                Paragraph(f"<b>Cliente:</b> {client.get('name', '')}", small_style)
            )
        if client.get("address"):
            elements.append(
                Paragraph(f"<b>Dirección:</b> {client.get('address', '')}", small_style)
            )
        if client.get("phone"):
            elements.append(
                Paragraph(f"<b>Tel/cel:</b> {client.get('phone', '')}", small_style)
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

    def _build_comments(self, comments: List[str], font_size=None, leading=None) -> List:
        """Build COMENTARIOS section with per-line formatting (NEW TEMPLATE)"""
        elements = []

        # Header: "COMENTARIOS:" in bold
        header_style = ParagraphStyle(
            "CommentsHeader",
            fontName=BMCStyles.FONT_NAME_BOLD,
            fontSize=10,
            textColor=BMCStyles.TEXT_BLACK,
            spaceAfter=4,
        )
        elements.append(Paragraph("<b>COMENTARIOS:</b>", header_style))

        # Get comment style (adjustable for 1-page fit)
        comment_style = BMCStyles.get_comments_style(font_size=font_size, leading=leading)

        # Format each comment with special rules
        for comment in comments:
            formatted_comment = self._format_comment_line(comment)
            # Add bullet
            bullet_text = f"• {formatted_comment}"
            elements.append(Paragraph(bullet_text, comment_style))

        return elements

    def _format_comment_line(self, comment: str) -> str:
        """Apply per-line formatting rules for comments"""
        # Rule 1: "Entrega de 10 a 15 días..." -> BOLD
        if "Entrega de 10 a 15 días" in comment or "dependemos de producción" in comment.lower():
            return f"<b>{comment}</b>"
        
        # Rule 2: "Oferta válida por 10 días..." -> RED
        if "Oferta válida por 10 días" in comment or "oferta válida" in comment.lower():
            return f'<font color="#CC0000">{comment}</font>'
        
        # Rule 3: "Incluye descuentos de Pago al Contado..." -> BOLD + RED
        if "Incluye descuentos de Pago al Contado" in comment or ("Seña del 60%" in comment and "Saldo del 40" in comment):
            return f'<b><font color="#CC0000">{comment}</font></b>'
        
        # Default: normal
        return comment

    def _build_conditions(self, conditions: List[str]) -> List:
        """Build terms and conditions section"""
        elements = []

        conditions_style = BMCStyles.get_conditions_style()

        for condition in conditions:
            elements.append(Paragraph(condition, conditions_style))

        return elements

    def _build_banking_info(self) -> List:
        """Build bank transfer footer box (NEW TEMPLATE)"""
        elements = []

        # Small spacer before footer
        elements.append(Spacer(1, 6))

        # Build footer table with exact content from requirements
        # Row 1: Depósito Bancario | Titular info
        # Row 2: Caja de Ahorro | Número de Cuenta
        # Row 3: Consulta | Términos (blue + underlined)
        
        from reportlab.platypus import Paragraph as Para
        
        small_font = 8.4
        cell_style = ParagraphStyle(
            "BankCell",
            fontName=BMCStyles.FONT_NAME,
            fontSize=small_font,
            textColor=BMCStyles.TEXT_BLACK,
            leading=10,
        )
        
        row1_left = Para("<b>Depósito Bancario</b>", cell_style)
        row1_right = Para(f"Titular: {QuotationConstants.BANK_ACCOUNT_HOLDER} – RUT: {QuotationConstants.BANK_RUT}", cell_style)
        
        row2_left = Para(f"{QuotationConstants.BANK_ACCOUNT_TYPE} - {QuotationConstants.BANK_NAME}.", cell_style)
        row2_right = Para(f"Número de Cuenta Dólares : {QuotationConstants.BANK_ACCOUNT_USD}", cell_style)
        
        row3_left = Para(f"Por cualquier duda, consultar al {QuotationConstants.CONTACT_PHONE}.", cell_style)
        row3_right = Para('<font color="#0066CC"><u>Lea los Términos y Condiciones</u></font>', cell_style)
        
        bank_table_data = [
            [row1_left, row1_right],
            [row2_left, row2_right],
            [row3_left, row3_right],
        ]
        
        # Create table with grid/box lines
        bank_table = Table(bank_table_data, colWidths=[220, 280])
        bank_table.setStyle(BMCStyles.get_bank_transfer_table_style())
        
        elements.append(bank_table)

        return elements


# Convenience function for quick PDF generation
def generate_quotation_pdf(quotation_data: Dict, output_path: str) -> str:
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
    # Format data for PDF
    formatted_data = QuotationDataFormatter.format_for_pdf(quotation_data)

    # Generate PDF
    generator = BMCQuotationPDF(output_path)
    return generator.generate(formatted_data)
