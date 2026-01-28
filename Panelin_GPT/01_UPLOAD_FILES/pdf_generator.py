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
from reportlab.lib.styles import getSampleStyleSheet

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
        Calculate all financial totals for the quotation

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
            if "total_usd" not in item:
                item["total_usd"] = QuotationDataFormatter.calculate_item_total(item)
            products_total += item["total_usd"]

        accessories_total = 0
        for item in accessories:
            if "total_usd" not in item:
                item["total_usd"] = QuotationDataFormatter.calculate_item_total(item)
            accessories_total += item["total_usd"]

        fixings_total = 0
        for item in fixings:
            if "total_usd" not in item:
                item["total_usd"] = QuotationDataFormatter.calculate_item_total(item)
            fixings_total += item["total_usd"]

        # Total from all items (which already includes IVA)
        grand_total_items = products_total + accessories_total + fixings_total

        # Calculate subtotal (net) and IVA from the total that already includes it
        # subtotal_net = grand_total_items / 1.22
        subtotal = grand_total_items / (1 + QuotationConstants.IVA_RATE)
        iva = grand_total_items - subtotal

        # Materials total is the original sum (IVA included)
        materials_total = grand_total_items

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

        # Header section
        story.extend(self._build_header(quotation_data))
        story.append(Spacer(1, 12))

        # Title and client info
        story.extend(self._build_title_section(quotation_data))
        story.append(Spacer(1, 12))

        # Products table
        if quotation_data.get("products"):
            story.extend(self._build_products_table(quotation_data["products"]))
            story.append(Spacer(1, 12))

        # Accessories table
        if quotation_data.get("accessories"):
            story.extend(self._build_accessories_table(quotation_data["accessories"]))
            story.append(Spacer(1, 12))

        # Fixings table
        if quotation_data.get("fixings"):
            story.extend(self._build_fixings_table(quotation_data["fixings"]))
            story.append(Spacer(1, 12))

        # Totals section
        story.extend(self._build_totals(quotation_data["totals"]))
        story.append(Spacer(1, 12))

        # Comments section
        if quotation_data.get("comments"):
            story.extend(self._build_comments(quotation_data["comments"]))
            story.append(Spacer(1, 6))

        # Conditions section
        story.extend(self._build_conditions(quotation_data["conditions"]))
        story.append(Spacer(1, 12))

        # Banking information
        story.extend(self._build_banking_info())

        # Build PDF
        doc.build(story)

        return self.output_path

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
            # Bug 1 & 2 Fix: Use both Length_m and length_m, and ensure total_usd is calculated
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
            # Bug 1 & 2 Fix: Use both Length_m and length_m, and ensure total_usd is calculated
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
