# 📘 How to Configure and Prompt This System

This guide provides a complete walkthrough for configuring and prompting the **Panelin - BMC Assistant Pro** chatbot system.

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Configuration](#-configuration)
   - [Environment Setup](#environment-setup)
   - [Knowledge Base Setup](#knowledge-base-setup)
   - [OpenAI GPT Configuration](#openai-gpt-configuration)
3. [Prompting](#-prompting)
   - [System Instructions](#system-instructions)
   - [Prompt Templates](#prompt-templates)
   - [Special Commands](#special-commands)
4. [Testing](#-testing)
5. [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Option 1: Local Development

```bash
# 1. Clone and navigate to repository
cd /path/to/Chatbot-Truth-base--Creation

# 2. Create environment file
cp .env.example .env

# 3. Edit .env with your configuration
# (Optional - MongoDB, Facebook, Instagram, MercadoLibre tokens)

# 4. Verify configuration
python3 verificar_configuracion.py

# 5. Run the system
python3 agente_ingestion_analisis.py --modo completo
```

### Option 2: OpenAI GPT Builder

1. Go to [chatgpt.com/gpts/editor](https://chatgpt.com/gpts/editor)
2. Create new GPT named "**Panelin - BMC Assistant Pro**"
3. Copy system instructions from `PANELIN_INSTRUCTIONS_COPY_PASTE.txt`
4. Upload knowledge base files (see below)
5. Enable **Web Browsing** and **Code Interpreter**
6. Save and test

---

## ⚙️ Configuration

### Environment Setup

Create a `.env` file in the project root:

```bash
# MongoDB (optional - for database extraction)
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/panelin
MONGODB_DATABASE_NAME=panelin

# Facebook (optional - for real APIs)
FACEBOOK_APP_ID=your_app_id
FACEBOOK_PAGE_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_page_id

# Instagram (optional - for real APIs)
INSTAGRAM_APP_ID=your_app_id
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id

# MercadoLibre (optional - for real APIs)
MERCADOLIBRE_ACCESS_TOKEN=your_token
MERCADOLIBRE_USER_ID=your_user_id
```

### Knowledge Base Setup

The knowledge base uses a **hierarchical structure** with 4 levels:

| Level | File | Purpose | Priority |
|-------|------|---------|----------|
| **Level 1 - MASTER** ⭐ | `BMC_Base_Conocimiento_GPT-2.json` | Primary source of truth for prices and formulas | **HIGHEST** |
| **Level 2 - VALIDATION** | `BMC_Base_Unificada_v4.json` | Cross-reference and validation | Medium |
| **Level 3 - DYNAMIC** | `panelin_truth_bmcuruguay_web_only_v2.json` | Real-time price verification | Low |
| **Level 4 - SUPPORT** | `Aleros.rtf`, context files, CSVs | Technical rules and context | Reference |

**Key Rule**: Always use Level 1 first. If there's a conflict, Level 1 wins.

### OpenAI GPT Configuration

#### Required Files to Upload

Upload these files to the GPT's Knowledge Base in this order:

1. ⭐ `BMC_Base_Conocimiento_GPT-2.json` (MASTER - upload first)
2. `BMC_Base_Unificada_v4.json`
3. `BMC_Catalogo_Completo_Shopify (1).json`
4. `panelin_truth_bmcuruguay_web_only_v2.json`
5. `panelin_context_consolidacion_sin_backend.md`
6. `Aleros.rtf` (or convert to .txt/.md)
7. `panelin_truth_bmcuruguay_catalog_v2_index.csv`

#### Capabilities to Enable

- ✅ **Web Browsing** - For verifying updated prices on Shopify
- ✅ **Code Interpreter** - For PDF generation and CSV processing
- ❌ **DALL-E** - Optional (not required for core functionality)

#### Recommended Model

- **GPT-4** or **GPT-4 Turbo** - Best for complex technical calculations
- **GPT-4o** - Latest version, best performance

---

## 💬 Prompting

### System Instructions

Copy the complete system instructions from:
- **File**: `PANELIN_INSTRUCTIONS_COPY_PASTE.txt`
- **Alternative**: `Instrucciones_Sistema_Panelin_CopiarPegar.txt`

The instructions include:

1. **Identity and Role** - Panelin as BMC Assistant Pro
2. **User Personalization** - Special responses for Mauro, Martin, Rami
3. **Source of Truth** - Hierarchical knowledge base rules
4. **Quotation Process** - 5-phase technical quotation workflow
5. **Business Rules** - Currency, IVA, calculations
6. **Special Commands** - SOP commands for advanced users
7. **Guardrails** - Validation rules to prevent errors

### Prompt Templates

#### Basic Quotation Request
```
Necesito cotizar ISODEC 100mm para un techo de 6m de luz, 4 paneles
```

#### Product Comparison
```
¿Qué diferencia hay entre EPS y PIR para un techo industrial de 500m²?
```

#### Technical Consultation
```
¿Cuál es la autoportancia del ISOROOF 80mm? ¿Sirve para 4m de luz?
```

#### Price Inquiry
```
¿Cuánto cuesta el ISODEC 150mm por metro cuadrado?
```

#### PDF Generation
```
Genera un PDF de la cotización anterior
```

### Special Commands

| Command | Function | Description |
|---------|----------|-------------|
| `/estado` | Status Check | Shows Ledger summary + context risk + recommendation |
| `/checkpoint` | Save Progress | Exports current state (snapshot + deltas) |
| `/consolidar` | Full Export | Exports complete pack (MD + JSONL + JSON + Patch) |
| `/evaluar_ventas` | Sales Evaluation | Evaluates sales personnel |
| `/entrenar` | Training Mode | Activates training practices |

### Conversation Starters

Suggested prompts to begin conversations:

1. `"Hola, mi nombre es [nombre]"`
2. `"Necesito cotizar ISODEC 100mm para un techo de 6m de luz"`
3. `"¿Qué diferencia hay entre EPS y PIR?"`
4. `"Genera un PDF de la cotización"`
5. `"/estado"`

---

## 🧪 Testing

### Verification Tests

Run these tests after configuration:

```python
# Test 1: Verify configuration
python3 verificar_configuracion.py

# Test 2: Run system tests
python3 test_sistema_completo.py

# Test 3: Test quotation calculator
python3 -m pytest tests/test_quotation_calculations.py -v
```

### Manual Test Cases

| Test | Input | Expected Output |
|------|-------|-----------------|
| Personalization | "Hola" | Should ask for user name |
| Basic Price | "¿Cuánto cuesta ISODEC 100mm?" | Price from Level 1 JSON: ~$46.07 |
| Technical Validation | "ISODEC 100mm para 7m de luz" | Warning: needs 150mm or more (autoportancia 5.5m < 7m) |
| Missing Data | "¿Cuánto cuesta producto inexistente?" | "No tengo esa información en mi base" |
| SOP Command | "/estado" | Ledger summary with context risk |

### Checklist

- [ ] ✅ System instructions loaded correctly
- [ ] ✅ All 7 knowledge base files uploaded
- [ ] ✅ Web Browsing enabled
- [ ] ✅ Code Interpreter enabled
- [ ] ✅ Personalization works (test with "Mauro", "Martin", "Rami")
- [ ] ✅ Source of truth works (reads correct JSON)
- [ ] ✅ Quotations calculate correctly
- [ ] ✅ Technical validation works (autoportancia)
- [ ] ✅ SOP commands work
- [ ] ✅ Guardrails prevent invented data

---

## 🔧 Troubleshooting

### Common Issues

#### GPT doesn't read the correct file
**Solution**: Ensure `BMC_Base_Conocimiento_GPT-2.json` is uploaded first. Add explicit instruction: "ALWAYS read BMC_Base_Conocimiento_GPT-2.json first"

#### GPT invents prices
**Solution**: Add stricter guardrail: "NEVER give a price without reading the JSON first"

#### Personalization doesn't work
**Solution**: Start a new conversation. Verify personalization instructions are clear.

#### Formulas are incorrect
**Solution**: Verify the GPT uses formulas from `formulas_cotizacion` in the JSON. Add examples in instructions.

#### Model Selection (AUTO only visible)
**Solution**: 
1. Check your OpenAI plan (Plus/Team required for model selection)
2. Use API directly if GPT Builder doesn't allow model selection
3. Add instruction: "This GPT should use GPT-4 for precision in technical calculations"

### Support Files

| Issue Area | Reference File |
|------------|----------------|
| Configuration | `QUICK_START_CONFIG.md` |
| Setup | `SETUP_INSTRUCTIONS.md` |
| GPT Creation | `Guia_Crear_GPT_OpenAI_Panelin.md` |
| Troubleshooting | `TROUBLESHOOTING_MODEL_SELECTION.md` |
| Architecture | `Arquitectura_Ideal_GPT_Panelin.md` |

---

## 📚 Additional Resources

- **Full Configuration Guide**: `Guia_Crear_GPT_OpenAI_Panelin.md`
- **Quick Start**: `P0_QUICK_START.md`
- **Prompt Reference**: `PANELIN_INSTRUCTIONS_COPY_PASTE.txt`
- **Features Guide**: `README_NEW_FEATURES.md`
- **Security Guide**: `SECURITY_INSTRUCTIONS.md`

---

## 📝 Summary

1. **Configure Environment**: Set up `.env` with required credentials
2. **Upload Knowledge Base**: 7 files with Level 1 as priority
3. **Apply System Instructions**: Copy from `PANELIN_INSTRUCTIONS_COPY_PASTE.txt`
4. **Enable Capabilities**: Web Browsing + Code Interpreter
5. **Test**: Verify with the test cases above
6. **Monitor**: Watch for invented data, incorrect formulas, or missing personalization

**Ready to go!** 🚀

---

*Last Updated: 2026-02-08*
*Version: 1.0*
