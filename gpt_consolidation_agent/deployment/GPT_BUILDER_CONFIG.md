# PANELIN - BMC Assistant Pro: GPT Builder Configuration Guide (v2.0)

This guide provides the exact values to copy and paste into the OpenAI GPT Builder for **Panelin - BMC Assistant Pro**.

## 1. General Settings

| Field | Value |
| :--- | :--- |
| **Name** | Panelin - BMC Assistant Pro |
| **Description** | Asistente técnico especializado en cotizaciones profesionales con generación de PDFs, evaluación de ventas y entrenamiento. Integra catálogo Shopify, pricing optimizado BROMYROS, y sistema de Knowledge Base jerárquico v6.0. |

## 2. Instructions

Copy the entire content of `gpt_consolidation_agent/deployment/instructions.md` into the **Instructions** field.

### Key Highlights for v2.2 Canonical:
- **IVA 2026**: 22% already included in prices.
- **Strict Derivation**: Never recommend external installers; always derive to BMC sales agents.
- **PDF Generation**: Full workflow for professional branded quotations.
- **5-Phase Process**: Identity -> Validation -> Data Retrieval -> Calculation -> Presentation.

## 3. Conversation Starters

Add these 6 conversation starters to help users:

1. `💡 Necesito una cotización para Isopanel EPS 50mm`
2. `📄 Genera un PDF para cotización de ISODEC 100mm`
3. `🔍 ¿Qué diferencia hay entre ISOROOF PIR y EPS?`
4. `📊 Evalúa mi conocimiento sobre sistemas de fijación`
5. `⚡ ¿Cuánto ahorro energético tiene el panel de 150mm vs 100mm?`
6. `🏗️ Necesito asesoramiento para un techo de 8 metros de luz`

## 4. Knowledge Base (Upload these files)

Upload the following files from `gpt_consolidation_agent/deployment/knowledge_base/` in this suggested order:

1. `BMC_Base_Conocimiento_GPT-2.json` (Master - v6.0)
2. `bromyros_pricing_master.json` (Master Pricing)
3. `bromyros_pricing_gpt_optimized.json` (Optimized Lookup)
4. `shopify_catalog_v1.json` (Catalog Descriptions)
5. `shopify_catalog_index_v1.csv` (Catalog Index)
6. `BMC_Base_Unificada_v4.json` (Validation)
7. `panelin_truth_bmcuruguay_web_only_v2.json` (Web Dynamic)
8. `PANELIN_KNOWLEDGE_BASE_GUIDE.md` (System Guide)
9. `PANELIN_QUOTATION_PROCESS.md` (Quotation Workflow)
10. `PANELIN_TRAINING_GUIDE.md` (Training Manual)
11. `GPT_INSTRUCTIONS_PRICING.md` (Pricing Logic)
12. `panelin_context_consolidacion_sin_backend.md` (SOP Commands)
13. `Aleros -2.rtf` (Technical Reference)

## 5. Capabilities

Configure the capabilities as follows:

| Capability | Status | Notes |
| :--- | :--- | :--- |
| **Web Browsing** | ✅ Enabled | Strictly for non-authoritative general construction info. |
| **Image Generation** | ✅ Enabled | Use ONLY for educational diagrams/infographics. |
| **Code Interpreter** | ✅ Enabled | **CRITICAL**: Required for PDF generation and CSV processing. |
| **Canvas** | ✅ Enabled | Use for long-form quotations and training reports. |

## 6. Actions

Refer to `gpt_configs/Panelin_Asistente_Integral_BMC_config_v2.0.json` for technical action definitions if you are using custom API actions. For the basic GPT setup, ensure the instructions correctly guide the agent to use the Code Interpreter for PDF generation.

---
**Last Updated**: 2026-01-28
**Version**: 2.0.0
