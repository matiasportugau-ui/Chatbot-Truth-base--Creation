#!/usr/bin/env python3
print("Loading pdf_generator...")
"""
BMC Uruguay Quotation PDF Generator
====================================

Generates professional quotation PDFs matching the standardized ODS structure.
Follows the specific styling and VAT policies defined in the prompt file.

Key Features:
- VAT Handling: Items and subtotals displayed NET (excl. VAT). VAT added at the end.
- Styling: Brand colors, top bar, specific header layout.
- Content: Conditions and Bank Accounts in footer.
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
from reportlab.lib import colors

try:
    from .pdf_styles import BMCStyles, QuotationConstants
except ImportError:
    from pdf_styles import BMCStyles, QuotationConstants


class QuotationDataFormatter:
    """Formats raw quotation data into PDF-ready structure"""

    @staticmethod
    def format_for_pdf(raw_data: Dict) -> Dict:
        """
        Transform raw quotation data into structured PDF format.
        CRITICAL: Converts VAT-inclusive prices from KB to NET prices for PDF display.
        """
        # Extract client info
        client_info = {
            "name": raw_data.get("client_name", ""),
            "address": raw_data.get("client_address", ""),
            "phone": raw_data.get("client_phone", ""),
        }

        # Process products with VAT reversal for display
        products = QuotationDataFormatter._process_items(raw_data.get("products", []))
        accessories = QuotationDataFormatter._process_items(
            raw_data.get("accessories", [])
        )
        fixings = QuotationDataFormatter._process_items(raw_data.get("fixings", []))

        # Calculate totals
        totals = QuotationDataFormatter.calculate_totals(
            products, accessories, fixings, raw_data.get("shipping_usd")
        )

        formatted = {
            "quote_id": raw_data.get(
                "quote_id", f"QT-{datetime.now().strftime('%Y%m%d')}"
            ),
            "date": raw_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "valid_until": raw_data.get("valid_until", ""),
            "quote_title": raw_data.get("quote_title", "PRESUPUESTO / COTIZACIÓN"),
            "client": client_info,
            "products": products,
            "accessories": accessories,
            "fixings": fixings,
            "totals": totals,
            "conditions": QuotationConstants.get_standard_conditions(),
            "bank_accounts": raw_data.get(
                "bank_accounts", QuotationDataFormatter._get_default_bank_accounts()
            ),
            "legal_disclaimer": raw_data.get(
                "legal_disclaimer",
                "Precios en USD. Imágenes ilustrativas. Sujetos a stock.",
            ),
        }

        return formatted

    @staticmethod
    def _process_items(items: List[Dict]) -> List[Dict]:
        """
        Process items to ensure they have NET prices for display.
        Prioritizes canonical 'sale_sin_iva' (NET) field.
        Fallbacks to 'unit_price_usd' (VAT INC) / 1.22 only if necessary.
        """
        processed = []
        for item in items:
            # 1. Try canonical NET price first (already without VAT)
            price_net = item.get("sale_sin_iva", 0)

            # 2. If no NET price, derive from VAT-inclusive price
            if price_net == 0:
                price_vat_inc = item.get("unit_price_usd", 0)
                price_net = price_vat_inc / (1 + QuotationConstants.IVA_RATE)

            # Calculate total NET based on unit base
            quantity = item.get("quantity", 0)
            unit_base = item.get("unit_base", "unidad").lower()

            total_net = 0
            if unit_base == "unidad":
                total_net = quantity * price_net
            elif unit_base == "ml":
                length = item.get("Length_m", item.get("length_m", 0))
                total_net = quantity * length * price_net
            elif unit_base in ["m2", "m²"]:
                total_m2 = item.get("total_m2", 0)
                total_net = total_m2 * price_net
            else:
                total_net = quantity * price_net

            new_item = item.copy()
            new_item["unit_price_net"] = price_net
            new_item["total_net"] = total_net
            processed.append(new_item)

        return processed

    @staticmethod
    def calculate_totals(
        products: List[Dict],
        accessories: List[Dict],
        fixings: List[Dict],
        shipping_usd: Optional[float] = None,
    ) -> Dict:
        """
        Calculate totals starting from NET values.
        """
        subtotal_net = 0

        for group in [products, accessories, fixings]:
            for item in group:
                subtotal_net += item.get("total_net", 0)

        # Calculate VAT
        iva = subtotal_net * QuotationConstants.IVA_RATE

        # Materials Total (VAT Inc)
        materials_total = subtotal_net + iva

        # Shipping (Usually VAT Inc or Exempt? Assuming pure cost added to total)
        # Verify if shipping needs VAT. Usually shipping is a service with VAT.
        # For simplicity/safety matching previous logic: add shipping to final.
        shipping = (
            shipping_usd
            if shipping_usd is not None
            else QuotationConstants.DEFAULT_SHIPPING_USD
        )

        grand_total = materials_total + shipping

        return {
            "subtotal_net": subtotal_net,
            "iva_rate": QuotationConstants.IVA_RATE,
            "iva_amount": iva,
            "materials_total_inc_vat": materials_total,
            "shipping": shipping,
            "grand_total": grand_total,
        }

    @staticmethod
    def _get_default_bank_accounts() -> List[Dict]:
        return [
            {
                "bank": QuotationConstants.BANK_NAME,
                "type": QuotationConstants.BANK_ACCOUNT_TYPE,
                "currency": "USD",
                "number": QuotationConstants.BANK_ACCOUNT_USD,
                "holder": QuotationConstants.BANK_ACCOUNT_HOLDER,
            }
        ]

    @staticmethod
    def format_currency(amount: float) -> str:
        return f"${amount:,.2f}"

    @staticmethod
    def format_date(date_str: str) -> str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            return date_str


class BMCQuotationPDF:
    """PDF Generator with new standardized ODS styling"""

    def __init__(self, output_path: str):
        self.output_path = output_path
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def generate(self, data: Dict) -> str:
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=BMCStyles.PAGE_SIZE,
            topMargin=BMCStyles.MARGIN_TOP + 10 * mm,  # Extra space for custom header
            bottomMargin=BMCStyles.MARGIN_BOTTOM
            + 20 * mm,  # Extra space for custom footer
            leftMargin=BMCStyles.MARGIN_LEFT,
            rightMargin=BMCStyles.MARGIN_RIGHT,
        )

        # Custom Flowable for Header/Footer (using build's onFirstPage/onLaterPages)
        story = []

        # Spacer for header
        story.append(Spacer(1, 10 * mm))

        # Title and Meta
        story.extend(self._build_title_meta(data))
        story.append(Spacer(1, 15))

        # Tables
        if data["products"]:
            story.extend(self._build_table("Productos", data["products"]))
            story.append(Spacer(1, 10))

        if data["accessories"]:
            story.extend(self._build_table("Accesorios", data["accessories"]))
            story.append(Spacer(1, 10))

        if data["fixings"]:
            story.extend(self._build_table("Fijaciones", data["fixings"]))
            story.append(Spacer(1, 10))

        # Totals
        story.extend(self._build_totals(data["totals"]))
        story.append(Spacer(1, 20))

        # Conditions & Banking (Footer body)
        story.extend(self._build_footer_body(data))

        doc.build(
            story,
            onFirstPage=self._draw_header_footer,
            onLaterPages=self._draw_header_footer,
        )
        return self.output_path

    def _draw_header_footer(self, canvas, doc):
        """Draws static header and footer on every page"""
        canvas.saveState()

        # --- HEADER ---
        # Top Color Bar
        canvas.setFillColor(BMCStyles.BMC_BLUE)
        canvas.rect(
            0,
            BMCStyles.PAGE_HEIGHT - 8 * mm,
            BMCStyles.PAGE_WIDTH,
            8 * mm,
            fill=1,
            stroke=0,
        )

        # Logo (Left)
        if os.path.exists(BMCStyles.LOGO_PATH):
            try:
                canvas.drawImage(
                    BMCStyles.LOGO_PATH,
                    BMCStyles.MARGIN_LEFT,
                    BMCStyles.PAGE_HEIGHT - 35 * mm,
                    width=50 * mm,
                    preserveAspectRatio=True,
                    anchor="sw",
                )
            except:
                pass

        # Company Info (Right)
        text = canvas.beginText(
            BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_RIGHT - 50 * mm,
            BMCStyles.PAGE_HEIGHT - 20 * mm,
        )
        text.setFont(BMCStyles.FONT_NAME_BOLD, 10)
        text.setFillColor(BMCStyles.BMC_BLUE)
        text.textLine(QuotationConstants.COMPANY_NAME)

        text.setFont(BMCStyles.FONT_NAME, 9)
        text.setFillColor(BMCStyles.TEXT_BLACK)
        text.textLine(
            f"RUT: {QuotationConstants.BANK_RUT}"
        )  # Using RUT from Bank info as fallback
        text.textLine("Maldonado, Uruguay")  # Generic
        text.textLine(f"Tel: {QuotationConstants.COMPANY_PHONE}")
        text.textLine(QuotationConstants.COMPANY_EMAIL)
        text.textLine(QuotationConstants.COMPANY_WEBSITE)
        canvas.drawText(text)

        # --- FOOTER ---
        # Page Number
        page_num = f"Página {doc.page}"
        canvas.drawRightString(
            BMCStyles.PAGE_WIDTH - BMCStyles.MARGIN_RIGHT, 10 * mm, page_num
        )

        canvas.restoreState()

    def _build_title_meta(self, data: Dict) -> List:
        elements = []

        # Title "PRESUPUESTO / COTIZACIÓN"
        elements.append(Paragraph(data["quote_title"], BMCStyles.get_title_style()))

        # Client & Quote Data Grid
        style_label = ParagraphStyle(
            "Label",
            parent=BMCStyles.get_normal_style(),
            fontName=BMCStyles.FONT_NAME_BOLD,
        )
        style_val = BMCStyles.get_normal_style()

        client = data["client"]

        # We use a table for alignment
        t_data = [
            [
                Paragraph("Cliente:", style_label),
                Paragraph(client["name"], style_val),
                Paragraph("Fecha:", style_label),
                Paragraph(QuotationDataFormatter.format_date(data["date"]), style_val),
            ],
            [
                Paragraph("Dirección:", style_label),
                Paragraph(client["address"], style_val),
                Paragraph("Válido hasta:", style_label),
                Paragraph(
                    QuotationDataFormatter.format_date(data["valid_until"]), style_val
                ),
            ],
            [
                Paragraph("Teléfono:", style_label),
                Paragraph(client["phone"], style_val),
                Paragraph("Cotización #:", style_label),
                Paragraph(data["quote_id"], style_val),
            ],
        ]

        t = Table(t_data, colWidths=[25 * mm, 80 * mm, 25 * mm, 40 * mm])
        t.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        elements.append(t)

        return elements

    def _build_table(self, title: str, items: List[Dict]) -> List:
        elements = []
        # Section Title
        elements.append(Paragraph(title, BMCStyles.get_header_style()))

        # Header
        header = ["Descripción", "Unidad", "Cant", "P.Unit (S/IVA)", "Total (S/IVA)"]
        data = [header]

        for item in items:
            unit = item.get("unit_base", "Unid.")
            # Format length in desc or unit if needed
            desc = item.get("name", "")
            if "Length_m" in item:
                desc += f" (Largo: {item['Length_m']}m)"

            row = [
                Paragraph(desc, BMCStyles.get_small_style()),
                unit,
                str(item.get("quantity", "")),
                QuotationDataFormatter.format_currency(item.get("unit_price_net", 0)),
                QuotationDataFormatter.format_currency(item.get("total_net", 0)),
            ]
            data.append(row)

        t = Table(data, colWidths=[80 * mm, 20 * mm, 20 * mm, 30 * mm, 30 * mm])
        t.setStyle(BMCStyles.get_products_table_style())
        elements.append(t)
        return elements

    def _build_totals(self, totals: Dict) -> List:
        data = [
            [
                "Subtotal (sin IVA):",
                QuotationDataFormatter.format_currency(totals["subtotal_net"]),
            ],
            [
                f"IVA {int(totals['iva_rate']*100)}%:",
                QuotationDataFormatter.format_currency(totals["iva_amount"]),
            ],
            [
                "TOTAL FINAL (IVA Inc.):",
                QuotationDataFormatter.format_currency(
                    totals["materials_total_inc_vat"]
                ),
            ],
        ]

        if totals["shipping"] > 0:
            data.insert(
                2,
                ["Envío:", QuotationDataFormatter.format_currency(totals["shipping"])],
            )
            data[-1][1] = QuotationDataFormatter.format_currency(totals["grand_total"])

        t = Table(data, colWidths=[130 * mm, 50 * mm], hAlign="RIGHT")
        t.setStyle(BMCStyles.get_totals_table_style())
        return [t]

    def _build_footer_body(self, data: Dict) -> List:
        elements = []

        # Conditions Header
        elements.append(
            Paragraph("Condiciones / Términos", BMCStyles.get_header_style())
        )

        # Conditions List
        for cond in data["conditions"]:
            elements.append(Paragraph(f"• {cond}", BMCStyles.get_conditions_style()))

        elements.append(Spacer(1, 10))

        # Bank Accounts
        elements.append(Paragraph("Cuentas Bancarias", BMCStyles.get_header_style()))

        for acc in data["bank_accounts"]:
            txt = f"<b>{acc.get('bank')}</b> - {acc.get('type')} {acc.get('currency')} N° {acc.get('number')} - Titular: {acc.get('holder')}"
            elements.append(Paragraph(txt, BMCStyles.get_small_style()))

        return elements


def generate_quotation_pdf(quotation_data: Dict, output_path: str) -> str:
    formatted_data = QuotationDataFormatter.format_for_pdf(quotation_data)
    generator = BMCQuotationPDF(output_path)
    return generator.generate(formatted_data)
