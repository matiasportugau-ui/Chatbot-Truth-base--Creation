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
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, Paragraph, Spacer, Image, PageBreak
from reportlab.platypus import SimpleDocTemplate, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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
        story = []

        # Header section with logo and centered title
        story.extend(self._build_header(quotation_data))
        story.append(Spacer(1, 8))

        # Client info (simplified, no title since it's in header)
        story.extend(self._build_client_info(quotation_data))
        story.append(Spacer(1, 8))

        # Materials table (combines products, accessories, fixings)
        story.extend(self._build_materials_table(quotation_data))
        story.append(Spacer(1, 6))

        # Totals section
        story.extend(self._build_totals(quotation_data["totals"]))
        story.append(Spacer(1, 6))

        # Comments section (with per-line formatting)
        story.extend(self._build_comments(quotation_data.get("comments", [])))
        story.append(Spacer(1, 4))

        # Banking information footer box
        story.extend(self._build_banking_info())

        # Build PDF
        doc.build(story)

        return self.output_path

    def _build_header(self, data: Dict) -> List:
        """Build header section with logo and centered title (two-column layout)"""
        elements = []
        
        # Create two-column header: [Logo | Centered Title]
        header_data = []
        
        # Left column: Logo
        logo_cell = ""
        if os.path.exists(BMCStyles.LOGO_PATH):
            try:
                # Load logo with auto-width based on height (maintain aspect ratio)
                from reportlab.lib.utils import ImageReader
                img = ImageReader(BMCStyles.LOGO_PATH)
                img_width, img_height = img.getSize()
                aspect = img_width / float(img_height)
                logo_height = BMCStyles.LOGO_HEIGHT
                logo_width = logo_height * aspect
                
                logo = Image(
                    BMCStyles.LOGO_PATH,
                    width=logo_width,
                    height=logo_height
                )
                logo_cell = logo
            except Exception as e:
                # Fallback to text if logo fails
                print(f"Warning: Could not load logo: {e}")
                logo_cell = Paragraph("<b>BMC Uruguay</b>", BMCStyles.get_header_style())
        else:
            logo_cell = Paragraph("<b>BMC Uruguay</b>", BMCStyles.get_header_style())
        
        # Right column: Centered title
        # Use dynamic title or default to "COTIZACIÓN – ISODEC EPS 100 mm"
        title_text = data.get('quote_title', 'COTIZACIÓN – ISODEC EPS 100 mm')
        if data.get('quote_description'):
            title_text = f"COTIZACIÓN – {data['quote_description']}"
        
        title_style = ParagraphStyle(
            'HeaderTitle',
            parent=BMCStyles.get_title_style(),
            alignment=1,  # Center alignment
            fontSize=BMCStyles.FONT_SIZE_TITLE,
            fontName=BMCStyles.FONT_NAME_BOLD,
            textColor=BMCStyles.BMC_BLUE,
        )
        title_cell = Paragraph(title_text, title_style)
        
        # Create header table with two columns
        header_data = [[logo_cell, title_cell]]
        header_table = Table(header_data, colWidths=[60*mm, 110*mm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        elements.append(header_table)
        
        return elements

    def _build_client_info(self, data: Dict) -> List:
        """Build client information section (simplified)"""
        elements = []

        client = data.get("client", {})
        normal_style = BMCStyles.get_small_style()

        # Date and location
        elements.append(
            Paragraph(
                f"<b>Fecha:</b> {QuotationDataFormatter.format_date(data.get('date', ''))}",
                normal_style,
            )
        )
        
        # Client info
        if client.get('name'):
            elements.append(
                Paragraph(f"<b>Cliente:</b> {client.get('name', '')}", normal_style)
            )
        if client.get('address'):
            elements.append(
                Paragraph(f"<b>Dirección:</b> {client.get('address', '')}", normal_style)
            )
        if client.get('phone'):
            elements.append(
                Paragraph(f"<b>Tel/cel:</b> {client.get('phone', '')}", normal_style)
            )

        return elements

    def _build_materials_table(self, data: Dict) -> List:
        """Build combined materials table (products, accessories, fixings)"""
        elements = []
        
        # Combine all items into one table
        all_items = []
        
        # Add products
        products = data.get("products", [])
        all_items.extend(products)
        
        # Add accessories
        accessories = data.get("accessories", [])
        all_items.extend(accessories)
        
        # Add fixings
        fixings = data.get("fixings", [])
        all_items.extend(fixings)
        
        if not all_items:
            return elements
        
        # Table header
        header = [
            "Material / Descripción",
            "Unid",
            "Cant",
            "USD",
            "Total",
        ]
        
        # Table data
        table_data = [header]
        for item in all_items:
            # Ensure correct total calculation
            total_usd = item.get("total_usd")
            if total_usd is None or total_usd == 0:
                total_usd = QuotationDataFormatter.calculate_item_total(item)
            
            row = [
                item.get("name", ""),
                item.get("unit_base", "unidad")[:4],  # Abbreviate unit
                str(item.get("quantity", "")),
                QuotationDataFormatter.format_currency(
                    item.get("unit_price_usd", 0)
                ),
                QuotationDataFormatter.format_currency(total_usd),
            ]
            table_data.append(row)
        
        # Create table with optimized column widths
        table = Table(table_data, colWidths=[90*mm, 20*mm, 20*mm, 25*mm, 25*mm])
        table.setStyle(BMCStyles.get_products_table_style(num_rows=len(table_data)))
        
        elements.append(table)
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
        """Build comments section with per-line formatting (bold/red)"""
        elements = []

        # Section title
        header_style = BMCStyles.get_header_style()
        elements.append(Paragraph("<b>COMENTARIOS:</b>", header_style))
        
        # Pre-defined comments with specific formatting
        # These match the requirement specifications
        formatted_comments = [
            ("Entrega de 10 a 15 días, dependemos de producción.", "bold"),
            ("Oferta válida por 10 días a partir de la fecha.", "red"),
            ("Incluye descuentos de Pago al Contado. Seña del 60% (al confirmar). Saldo del 40 % (previo a retiro de fábrica).", "bold_red"),
        ]
        
        # Add YouTube URL as plain text
        formatted_comments.append(("https://youtu.be/Am4mZskFMgc", "normal"))
        
        # Merge with any additional comments from data
        additional_comments = comments if comments else []
        
        # Render formatted comments
        for comment_text, style_type in formatted_comments:
            if style_type == "bold":
                style = BMCStyles.get_comments_bold_style()
                text = f"• <b>{comment_text}</b>"
            elif style_type == "red":
                style = BMCStyles.get_comments_red_style()
                text = f'• <font color="#{BMCStyles.TEXT_RED.hexval()[2:]}">{comment_text}</font>'
            elif style_type == "bold_red":
                style = BMCStyles.get_comments_bold_red_style()
                text = f'• <b><font color="#{BMCStyles.TEXT_RED.hexval()[2:]}">{comment_text}</font></b>'
            else:
                style = BMCStyles.get_comments_style()
                text = f"• {comment_text}"
            
            elements.append(Paragraph(text, style))
        
        # Add any additional comments from the data (normal style)
        normal_style = BMCStyles.get_comments_style()
        for comment in additional_comments:
            # Skip if already in formatted_comments
            if not any(comment in fc[0] for fc in formatted_comments):
                elements.append(Paragraph(f"• {comment}", normal_style))

        return elements

    def _build_conditions(self, conditions: List[str]) -> List:
        """Build terms and conditions section"""
        elements = []

        conditions_style = BMCStyles.get_conditions_style()

        for condition in conditions:
            elements.append(Paragraph(condition, conditions_style))

        return elements

    def _build_banking_info(self) -> List:
        """Build banking information footer box with grid/border"""
        elements = []

        elements.append(Spacer(1, 6))
        
        # Create bank transfer footer box (matching reference image style)
        # 3 rows with grid lines, first row has gray background
        
        # Use consistent small style for all footer text
        footer_style = ParagraphStyle(
            'FooterText',
            fontName=BMCStyles.FONT_NAME,
            fontSize=BMCStyles.FONT_SIZE_FOOTER,
            textColor=BMCStyles.TEXT_BLACK,
            leading=BMCStyles.FONT_SIZE_FOOTER + 2,
        )
        
        footer_data = [
            # Row 1 (gray background)
            [
                Paragraph("<b>Depósito Bancario</b>", footer_style),
                Paragraph(f"<b>Titular:</b> {QuotationConstants.BANK_ACCOUNT_HOLDER} – RUT: {QuotationConstants.BANK_RUT}", footer_style),
            ],
            # Row 2
            [
                Paragraph(f"<b>{QuotationConstants.BANK_ACCOUNT_TYPE} - {QuotationConstants.BANK_NAME}.</b>", footer_style),
                Paragraph(f"<b>Número de Cuenta Dólares :</b> {QuotationConstants.BANK_ACCOUNT_USD}", footer_style),
            ],
            # Row 3
            [
                Paragraph(f"Por cualquier duda, consultar al {QuotationConstants.CONTACT_PHONE}.", footer_style),
                Paragraph('<u><font color="blue">Lea los Términos y Condiciones</font></u>', footer_style),
            ],
        ]
        
        # Create table with box style
        footer_table = Table(footer_data, colWidths=[90*mm, 90*mm])
        footer_table.setStyle(BMCStyles.get_footer_box_style())
        
        elements.append(footer_table)

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
