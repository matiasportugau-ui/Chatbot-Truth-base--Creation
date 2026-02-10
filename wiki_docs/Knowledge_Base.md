# Knowledge Base (KB)

The Knowledge Base is the **Source of Truth** for Panelin. The AI does not memorize prices; it retrieves them from these files. This ensures 100% accuracy and prevents "hallucinations" regarding costs.

## Hierarchy of Truth

The system follows a strict hierarchy when looking for information:

### 1. Level 1 - Master (The Absolute Truth) ⭐
*   **File**: `BMC_Base_Conocimiento_GPT-2.json`
*   **Content**: Validated Shopify prices, official formulas, product specifications.
*   **Rule**: **ALWAYS** check this file first. If there is a conflict, this file wins.

### 2. Level 2 - Validation
*   **File**: `BMC_Base_Unificada_v4.json`
*   **Content**: Consolidated data used for cross-referencing.
*   **Rule**: Used to validate Level 1 data, but never overrides it.

### 3. Level 3 - Dynamic (Real-Time)
*   **File**: `panelin_truth_bmcuruguay_web_only_v2.json`
*   **Content**: Web-scraped prices, stock status.
*   **Rule**: Used to check for very recent updates not yet in Master.

### 4. Level 4 - Support
*   **Files**: `Aleros.rtf`, CSV catalogs, Markdown guides.
*   **Content**: Contextual information, specific installation rules (e.g., overhangs).

## Updating the Knowledge Base

The KB is updated using the **Ingestion Agent**.

1.  **Place raw files** in the input directory (e.g., `Files/`).
2.  **Run the ingestion script**:
    ```bash
    python agente_ingestion_analisis.py
    ```
3.  **Review the output**: The agent will generate a new JSON file and a report.
4.  **Promote to Master**: If the data is correct, rename/move the file to replace `BMC_Base_Conocimiento_GPT-2.json`.

## Internal vs. Public Data

⚠️ **IMPORTANT**:
*   `BROMYROS_Base_Costos_Precios_2026.json` contains **internal costs and margins**.
*   **NEVER** upload this file to a public GPT or expose it to end-users.
*   It is reserved for internal agents (e.g., for management reporting).
