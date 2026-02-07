# 🚀 Deployment Guide - Manual Steps

**Date**: 2026-02-07  
**Status**: Steps 1-4 COMPLETE ✅  
**Next**: Follow steps 5-12 to deploy

---

## ✅ Completed Steps (Automated)

- [x] **Step 1**: Pre-Deployment Audit - All files ready (119 KB)
- [x] **Step 2**: Updated Instructions - V3.1 section added
- [x] **Step 3**: Backup preparation - Rollback plan ready
- [x] **Step 4**: Upload Package - 4 core files ready

---

## 📦 Upload Package Ready

Location: `gpt_deployment_20260207/upload_package/`

**Files to Upload** (4 core files, 124 KB total):

1. ✅ `quotation_calculator_v3.py` (35 KB)
2. ✅ `BMC_Base_Conocimiento_GPT-2.json` (16 KB)
3. ✅ `accessories_catalog.json` (48 KB)
4. ✅ `bom_rules.json` (20 KB)

**Upload Order**: Upload in the order listed above (JSONs first, then calculator)

---

## 🔧 Manual Steps (YOU need to do these)

### Step 5: Backup Current GPT (5 min) 🔴 CRITICAL

**Before making ANY changes**:

1. Open GPT Builder: https://chat.openai.com/gpts/editor/
2. Select your "Panelin" GPT
3. Click **Configure** tab
4. Copy **ALL current instructions** → Save to a file `gpt_backup_current_instructions.txt`
5. Note which files are currently uploaded in Knowledge section
6. Save this backup somewhere safe!

**Why**: If something goes wrong, you can restore instantly.

---

### Step 6: Upload Files to GPT Builder (5 min)

**Instructions**:

1. Stay in GPT Builder → Configure tab
2. Scroll down to **Knowledge** section
3. Click **Upload files** button
4. Upload files IN THIS ORDER:
   - `bom_rules.json` (first - required by calculator)
   - `accessories_catalog.json` (second - required by calculator)
   - `BMC_Base_Conocimiento_GPT-2.json` (third - required by calculator)
   - `quotation_calculator_v3.py` (last - depends on JSONs)

5. Wait for each upload to complete before uploading next
6. Verify all 4 files appear in the Knowledge list

**Expected result**: All 4 files visible in Knowledge section, no upload errors

---

### Step 7: Update GPT Instructions (3 min)

**Instructions**:

1. Stay in GPT Builder → Configure tab
2. Scroll to top → **Instructions** textbox
3. **DELETE ALL** current instructions
4. Open file: `gpt_deployment_20260207/STEP_2_UPDATED_INSTRUCTIONS.md`
5. **COPY ALL** content from that file
6. **PASTE** into Instructions textbox
7. Verify paste was complete (scroll to bottom, should end with "v3.1 Canonical")
8. Click **Save** (top right)

**Expected result**: Instructions updated, save successful

---

### Step 8: Enable Code Interpreter (2 min) 🔴 CRITICAL

**Instructions**:

1. Stay in GPT Builder → Configure tab
2. Scroll to **Capabilities** section
3. Find **Code Interpreter** checkbox
4. ✅ **CHECK** the box (enable it)
5. Click **Save** (top right)

**Why critical**: Calculator V3.1 REQUIRES Code Interpreter to execute Python. Without it, validation won't work!

**Expected result**: Code Interpreter checkbox is checked and saved

---

### Step 9: Test Basic Quotation (5 min)

**Instructions**:

1. Click **Preview** button (top right in GPT Builder)
2. In the preview chat, type:

```
Cotiza 45m² Isopanel EPS 50mm para techo, estructura metálica, luz 3 metros
```

3. Wait for response
4. **Verify**:
   - ✅ Calculator executed (no Python errors)
   - ✅ Shows panel price: ~$1,494 (45 × $33.21)
   - ✅ Shows accessories (perfilería, fijaciones, selladores)
   - ✅ Shows total with IVA included
   - ✅ Complete BOM table

**If it fails**: Check error message, verify Code Interpreter is enabled, verify files uploaded

**Expected result**: Complete quotation with all accessories, no errors

---

### Step 10: Test Autoportancia Validation (5 min)

**Test Case A - Valid Span**:

```
Cotiza techo 50m² ISODEC EPS 100mm, luz 4 metros, estructura metálica
```

**Expected**:
- ✅ Validation message: "Espesor 100mm soporta luz de 4m con margen de seguridad"
- Mentions max safe span: 4.675m
- Quotation proceeds normally

---

**Test Case B - Excessive Span**:

```
Cotiza techo 50m² ISODEC EPS 100mm, luz 8 metros, estructura metálica
```

**Expected**:
- ⚠️ Warning message: "Luz de 8m excede capacidad de 100mm"
- Recommendation: "Sugerimos espesor 150mm o viga intermedia"
- Mentions limits: max safe 4.675m, absolute 5.5m

---

**If validation doesn't trigger**:
- Check Code Interpreter is enabled
- Check quotation_calculator_v3.py uploaded successfully
- Check bom_rules.json uploaded (contains autoportancia tables)

**Expected result**: Both test cases show validation working correctly

---

### Step 11: Final Check (3 min)

**Instructions**:

Run one complete test with data collection:

```
Hola, necesito cotización para un techo
```

GPT should ask for: name, phone, address, then specifications.

Provide:
```
Lucía, 099 123 456, Montevideo
180m² ISODEC EPS 100mm, luz 5 metros, estructura metálica
```

**Expected**:
1. ⚠️ Validation warning (luz 5m is at limit of 4.675m safe)
2. Recommendation for 120mm or support
3. Complete quotation with all line items
4. Professional table format
5. Total with IVA included

**If everything works**: You're ready to go live!

---

### Step 12: Go Live (2 min)

**Instructions**:

1. In GPT Builder, verify everything is saved
2. Change GPT visibility if needed:
   - Private: Only you
   - Anyone with link: Share URL
   - Public: Listed in GPT store
3. Click **Save** final time
4. Test the public/shared link works
5. Announce to your team!

**Announcement Template**:

```
📢 Panelin GPT V3.1 está en producción!

Nuevas características:
✅ Validación automática de autoportancia (luz/espesor)
✅ Margen de seguridad 15% aplicado automáticamente
✅ Cotizaciones completas con todos los accesorios
✅ Cálculos verificados (91% pass rate en 111 tests)

Link: [Your GPT URL]

Pruébenlo y compartan feedback!
```

**Expected result**: GPT is live and accessible to your team/customers

---

## 🔍 Troubleshooting

### Problem: "Python execution failed"
**Solution**: 
1. Check Code Interpreter is enabled
2. Re-upload quotation_calculator_v3.py
3. Try test in preview again

### Problem: "File not found" error
**Solution**:
1. Verify all 4 files uploaded successfully
2. Check file names match exactly
3. Re-upload missing file

### Problem: Validation doesn't trigger
**Solution**:
1. Check bom_rules.json uploaded (contains autoportancia tables)
2. Verify Code Interpreter enabled
3. Try explicitly: `/autoportancia product=ISODEC_EPS espesor=100 luz=5.0`

### Problem: Prices are wrong
**Solution**:
1. Verify BMC_Base_Conocimiento_GPT-2.json uploaded
2. Verify accessories_catalog.json uploaded
3. Check instructions mention correct KB hierarchy

---

## 📊 Success Checklist

Before considering deployment complete:

- [ ] Backup of current GPT created
- [ ] All 4 files uploaded successfully
- [ ] Instructions updated with V3.1 section
- [ ] Code Interpreter enabled
- [ ] Basic quotation test passed
- [ ] Validation test (valid span) passed
- [ ] Validation test (excessive span) passed
- [ ] Complete workflow test passed
- [ ] GPT is live and accessible
- [ ] Team has been notified

---

## 🚨 If Something Goes Wrong

**Immediate Rollback** (< 5 min):

1. Open GPT Builder
2. Restore instructions from backup file
3. Remove newly uploaded files (or re-upload old ones)
4. Disable Code Interpreter if it's causing issues
5. Save
6. Test basic functionality
7. Notify team

**Then**:
- Document what went wrong
- Test fix locally
- Plan re-deployment when ready

---

## 📁 Files Reference

All deployment files are in: `gpt_deployment_20260207/`

- `STEP_1_AUDIT_REPORT.md` - Audit results
- `STEP_2_UPDATED_INSTRUCTIONS.md` - New instructions to paste
- `DEPLOYMENT_GUIDE_MANUAL_STEPS.md` - This file
- `upload_package/` - 4 files ready to upload

---

## ⏱️ Estimated Time

- Steps 5-8 (Upload & Configure): 15 minutes
- Steps 9-11 (Testing): 13 minutes
- Step 12 (Go Live): 2 minutes

**Total**: ~30 minutes of hands-on work

---

## 📞 Next Steps

1. **NOW**: Follow Step 5 - Backup your current GPT
2. **Then**: Follow Steps 6-8 - Upload files and configure
3. **Then**: Follow Steps 9-11 - Test thoroughly
4. **Finally**: Follow Step 12 - Go live!

**Good luck! 🚀**

