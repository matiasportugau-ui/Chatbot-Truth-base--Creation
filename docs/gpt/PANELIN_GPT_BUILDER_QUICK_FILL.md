# Panelin GPT Builder — Copy/Paste Quick Fill Guide

**Version**: 1.0 (Full Capabilities)
**Date**: 2026-01-25
**Estimated Time**: 15-20 minutes

---

## Before You Start

1. Open the GPT Builder: [https://chatgpt.com/gpts/editor](https://chatgpt.com/gpts/editor)
2. Have this repo open
3. Enable **Code Interpreter** (currently OFF in your screenshot)

---

## STEP 1: Configure Tab → Nombre (Name)

**Copy/paste this**:

```
Panelin — Internal BMC Assistant Pro
```

---

## STEP 2: Configure Tab → Descripción (Description)

**Copy/paste this**:

```
Internal assistant for BMC Uruguay quotations and technical-sales guidance. Uses a strict Source-of-Truth KB (Level 1 master), validates autoportancia, applies IVA rules, supports training/evaluation + SOP commands, and can browse, analyze files, generate PDFs, and create diagrams when helpful.
```

---

## STEP 3: Configure Tab → Instrucciones (Instructions)

**Source file**: `docs/gpt/PANELIN_SYSTEM_INSTRUCTIONS_CANONICAL.md`

**How to copy**:

1. Open the file in your editor
2. Copy from line 9 (`# IDENTIDAD Y ROL`) to the end (line ~220)
3. Paste into the "Instrucciones" field
4. Verify the capability policy addendum is at the bottom

**Quick verification**:

- Search for: `BMC_Base_Conocimiento_GPT-2.json` (should appear multiple times)
- Search for: `CAPABILITIES POLICY` (should be near the end)
- Search for: `RECOLECCIÓN DE DATOS DEL CLIENTE` (production mode data collection)

---

## STEP 4: Configure Tab → Frases para iniciar una conversación (Starters)

**Copy/paste these 8 starters** (one per field):

1. `Hola, mi nombre es [nombre]`
2. `Necesito cotizar ISODEC EPS 100mm para 10m x 5m con luz 4.5m, fijación a hormigón.`
3. `¿Qué diferencia hay entre EPS y PIR en aislamiento y seguridad contra fuego?`
4. `/evaluar_ventas`
5. `/estado`
6. `Genera un PDF de esta cotización.`
7. `Te subo un CSV del catálogo: encontrá el producto correcto por código/keywords.`
8. `Crea un diagrama simple explicando autoportancia y "luz".`

---

## STEP 5: Configure Tab → Conocimientos (Knowledge)

**Click "Cargar archivos" and upload IN THIS EXACT ORDER**:

### Upload Sequence (11 files)

**Priority 1 — Level 1 Master (FIRST)**

1. ✅ `BMC_Base_Conocimiento_GPT-2.json`

**Priority 2 — Catalog (NEW)**
2. ✅ `catalog/out/shopify_catalog_v1.json`

**Priority 3 — Validation/Dynamic**
3. ✅ `Files /BMC_Base_Unificada_v4.json`
4. ✅ `panelin_truth_bmcuruguay_web_only_v2.json` (Root version ONLY, not `Files /`)

**Priority 4 — Process Anchors**
5. ✅ `PANELIN_KNOWLEDGE_BASE_GUIDE.md`
6. ✅ `PANELIN_QUOTATION_PROCESS.md`
7. ✅ `PANELIN_TRAINING_GUIDE.md`
8. ✅ `panelin_context_consolidacion_sin_backend.md`

**Priority 5 — Support/Indexes**
9. ✅ `Files /Aleros -2.rtf` (if Builder rejects: convert to `.md` first)
10. ✅ `catalog/out/shopify_catalog_index_v1.csv`
11. ⚠️ `BMC_Catalogo_Completo_Shopify (1).json` (Optional, legacy)

**Wait 2-3 minutes after upload** for GPT to reindex files.

---

## STEP 6: Configure Tab → Modelo recomendado (Model)

**Click the dropdown** and select:

- **GPT-4** (recommended)
- **GPT-4 Turbo** (faster, also good)
- **GPT-4o** (if available)

**Do NOT use**:

- ❌ GPT-3.5 (not precise enough for technical calculations)
- ❌ AUTO (unpredictable model selection)

---

## STEP 7: Configure Tab → Funcionalidades (Capabilities)

**Enable ALL of these** (your screenshot shows Code Interpreter OFF — fix this):

- ✅ **Búsqueda en la web** (Web Browsing)
- ✅ **Lienzo** (Canvas)
- ✅ **Generación de imagen** (Image Generation)
- ✅ **Intérprete de código y análisis de datos** (Code Interpreter) ← **TURN THIS ON**

---

## STEP 8: Configure Tab → Acciones (Actions)

**Leave empty for now** (Actions are optional).

If you implement the backend API later, refer to `docs/gpt/PANELIN_ACTIONS_SPEC.md`.

---

## STEP 9: Save & Test

### Save

1. Click **"Guardar"** (top right)
2. Choose **"Only me"** (recommended for internal GPT with sensitive data)

### Test in Preview

Open the **Preview** pane and run these quick smoke tests:

**Test 1**: Source of Truth

```
¿Cuánto cuesta ISODEC 100mm?
```

**Expected**: Asks for nombre, teléfono, dirección obra. Then cites KB and gives exact price ($46.07).

**Test 2**: Catalog Lookup

```
 Busca el producto con handle "isoroof-3g-gris-rojo-blanco-bromyros"
```

**Expected**: Returns description from catalog.

**Test 3**: Code Interpreter

```
Genera un PDF de esta cotización.
```

**Expected**: Writes Python code, executes, provides download link.

**Test 4**: Image Generation

```
Crea un diagrama explicando "luz" y autoportancia.
```

**Expected**: Generates diagram, disclaims it's not a real photo.

**Test 5**: Web Conflict

```
     Busca en la web el precio de ISODEC 100mm y compáralo con tu base.
```

**Expected**: Uses Level 1 KB as authority, mentions web is secondary.

For full test suite, see: `docs/gpt/PANELIN_GPT_TEST_PLAN.md`

---

## STEP 10: Production Checklist

Before marking as "ready for production":

- [ ] All Knowledge files uploaded in correct order
- [ ] Code Interpreter enabled
- [ ] All 5 test suites pass (see `PANELIN_GPT_TEST_PLAN.md`)
- [ ] Client data collection activates for quotes
- [ ] Phone validation works (09X format)
- [ ] No hallucinated prices
- [ ] Capabilities stay within policy boundaries

---

## Troubleshooting

### "Panelin invents prices"

- **Cause**: Level 1 file not uploaded first, or instructions don't enforce it
- **Fix**: Re-upload `BMC_Base_Conocimiento_GPT-2.json` FIRST, wait 3 min, retest

### "Code Interpreter disabled error"

- **Cause**: Toggle is OFF
- **Fix**: Go to Configure → Funcionalidades → Enable "Intérprete de código"

### "Cannot find catalog product"

- **Cause**: `shopify_catalog_v1.json` not uploaded or reindex incomplete
- **Fix**: Verify file uploaded, wait 2-3 min, retry

### "Phone validation too strict"

- **Cause**: Instructions block non-Uruguay formats
- **Fix**: Update canonical instructions to accept international formats if needed

---

**Ready to configure!** 🚀

Follow steps 1–10 above, checking each field carefully. The entire setup should take 15–20 minutes.
