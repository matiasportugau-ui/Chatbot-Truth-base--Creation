# Panelin GPT Security Policy
**Version**: 1.0 (Internal)
**Scope**: Panelin GPT (Internal Use Only)

This policy defines data handling, access control, and secret management for the internal Panelin GPT.

---

## 🔐 Data Classification

| Data Type | Classification | GPT Handling |
| :--- | :--- | :--- |
| **Public Pricing** | Internal | Upload to Knowledge Base (Level 1) |
| **Product Specs** | Public | Upload to Knowledge Base (Level 2) |
| **Formulas** | Internal | Upload to Knowledge Base (Level 1) |
| **Cost / Margins** | **Confidential** | **DO NOT UPLOAD**. Use API Actions only. |
| **Customer PII** | **Confidential** | **DO NOT STORE**. Mask in context. |
| **Employee PII** | Internal | Limited (Names allowed for personalization) |

---

## 🚫 Forbidden Actions

1. **No Secrets**: Never upload `.env` files, API keys, AWS credentials, or passwords to Knowledge Base or Canvas.
2. **No Cost Uploads**: Files like `BROMYROS_Base_Costos_Precios_2026.json` or `MATRIZ de COSTOS` must NEVER be uploaded.
3. **No Public Sharing**: Do not enable "Anyone with the link" if the KB contains unreleased prices or internal strategy docs. Keep visibility "Only me" or "Team Workspace".

---

## 🛡️ Capabilities Usage

- **Web Browsing**: Do not submit internal proprietary text to public search engines via the browsing tool.
- **Code Interpreter**: Do not execute untrusted code snippets pasted by users.
- **Canvas**: Do not draft documents containing unreleased strategic plans.

---

## 🚨 Incident Response

**Leak Detected (e.g., GPT reveals system instructions):**
1. Update `PANELIN_SYSTEM_INSTRUCTIONS_CANONICAL.md`.
2. Add "DO NOT REVEAL" guardrail (already present).
3. Re-save GPT.

**Hallucination Detected (e.g., fake prices):**
1. Check `BMC_Base_Conocimiento_GPT-2.json`.
2. Verify instructions point to correct file.
3. Add negative constraint: "If not in Level 1, say 'I don't know'".

**Data Spill (e.g., cost file uploaded):**
1. Immediately DELETE the file from GPT Knowledge.
2. Delete the GPT version history if possible (or recreate GPT).
3. Rotate any secrets if they were in the file.
