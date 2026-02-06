# Panelin GPT Builder Configuration
**Version**: 1.1 (Full Capabilities)
**Last Updated**: 2026-02-06

Use these exact values when configuring the GPT in the [OpenAI GPT Builder](https://chatgpt.com/gpts/editor).

---

## 1. Configure Tab

### Name
`Panelin — Internal BMC Assistant Pro`

### Description
`Internal assistant for BMC Uruguay quotations and technical-sales guidance. Uses a strict Source-of-Truth KB (Level 1 master), validates autoportancia, applies IVA rules, supports training/evaluation + SOP commands, and can browse, analyze files, generate PDFs, and create diagrams when helpful.`

### Instructions
**Source**: Copy the content from [`docs/gpt/PANELIN_SYSTEM_INSTRUCTIONS_CANONICAL.md`](PANELIN_SYSTEM_INSTRUCTIONS_CANONICAL.md)

*(Ensure it includes the Capability Policy Addendum at the end)*

### Conversation Starters
1. `Hola, mi nombre es [nombre]`
2. `Necesito cotizar ISODEC EPS 100mm para 10m x 5m con luz 4.5m, fijación a hormigón.`
3. `¿Qué diferencia hay entre EPS y PIR en aislamiento y seguridad contra fuego?`
4. `/evaluar_ventas`
5. `/estado`
6. `Genera un PDF de esta cotización.`
7. `Te subo un CSV del catálogo: encontrá el producto correcto por código/keywords.`
8. `Crea un diagrama simple explicando autoportancia y “luz”.`

### Knowledge
**Upload in this exact order** (see [`PANELIN_KNOWLEDGE_MANIFEST.md`](PANELIN_KNOWLEDGE_MANIFEST.md) for file paths):

1. `BMC_Base_Conocimiento_GPT-2.json`
2. `accessories_catalog.json` (new, BOM accessories pricing)
3. `bom_rules.json` (new, parametric BOM rules)
4. `catalog/out/shopify_catalog_v1.json`
5. `Files /BMC_Base_Unificada_v4.json`
6. `panelin_truth_bmcuruguay_web_only_v2.json` (Root version)
7. `PANELIN_KNOWLEDGE_BASE_GUIDE.md`
8. `PANELIN_QUOTATION_PROCESS.md`
9. `PANELIN_TRAINING_GUIDE.md`
10. `panelin_context_consolidacion_sin_backend.md`
11. `Files /Aleros -2.rtf`
12. `catalog/out/shopify_catalog_index_v1.csv`
13. `BMC_Catalogo_Completo_Shopify (1).json` (Optional)

### Capabilities
- ✅ **Web Browsing**: ON
- ✅ **DALL·E Image Generation**: ON
- ✅ **Code Interpreter**: ON
- ✅ **Canvas**: ON

### Actions
*None for initial setup.* (See `PANELIN_ACTIONS_SPEC.md` if implementing later; ensure
`calculate_quote` returns valued `line_items` using `accessories_catalog.json` + `bom_rules.json`.)

---

## 2. Additional Settings

- **Uncheck**: "Use conversation data in your GPT to improve our models" (Recommended for internal data)
- **Visibility**: "Only me" (initially) or "Anyone with link" (for internal team)
