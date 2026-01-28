# Knowledge Base System

The Panelin Knowledge Base (KB) is a hierarchical system designed to provide accurate, consistent information for quotations and technical assistance.

---

## Table of Contents

1. [Overview](#overview)
2. [4-Level Hierarchy](#4-level-hierarchy)
3. [File Reference](#file-reference)
4. [Validation Rules](#validation-rules)
5. [Conflict Detection](#conflict-detection)
6. [KB Management](#kb-management)
7. [Best Practices](#best-practices)

---

## Overview

The Knowledge Base is the **Source of Truth** for all pricing, specifications, and technical data. It follows a strict 4-level hierarchy where Level 1 (Master) always takes precedence.

### Key Principles

1. **Single Source of Truth**: Level 1 is the authoritative source
2. **Never Invent Data**: If data isn't in KB, say "I don't have that information"
3. **Hierarchy Enforcement**: Always consult levels in order (1 → 2 → 3 → 4)
4. **Conflict Reporting**: Report any conflicts between levels

---

## 4-Level Hierarchy

```
┌─────────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE BASE HIERARCHY                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ⭐ LEVEL 1: MASTER                                        Priority │
│  ───────────────────────────────────────────────────────    ★★★★★  │
│  File: BMC_Base_Conocimiento_GPT-2.json                             │
│                                                                      │
│  The ABSOLUTE Source of Truth. Contains:                            │
│  • Product specifications (ISODEC, ISOPANEL, ISOROOF, ISOWALL)     │
│  • Validated Shopify prices                                         │
│  • Quotation formulas (formulas_cotizacion)                        │
│  • Autoportancia (load-bearing) data                               │
│  • Thermal coefficients                                             │
│  • Business rules (reglas_negocio)                                 │
│  • Uruguay reference data                                           │
│                                                                      │
│  RULE: ALWAYS read this file FIRST before giving any price         │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  📚 LEVEL 2: VALIDATION                                   Priority │
│  ───────────────────────────────────────────────────────    ★★★☆☆  │
│  File: BMC_Base_Unificada_v4.json                                   │
│                                                                      │
│  For cross-reference ONLY. NOT for direct responses.               │
│  • Validates Level 1 data                                          │
│  • Detects inconsistencies                                         │
│  • Contains additional product details                             │
│                                                                      │
│  RULE: Only use for validation, NEVER as primary source            │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  🔄 LEVEL 3: DYNAMIC                                      Priority │
│  ───────────────────────────────────────────────────────    ★★☆☆☆  │
│  File: panelin_truth_bmcuruguay_web_only_v2.json                   │
│                                                                      │
│  Updated prices and stock status.                                  │
│  • Current web prices                                               │
│  • Stock availability                                               │
│  • Price updates                                                    │
│                                                                      │
│  RULE: Verify against Level 1 before using                         │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  📎 LEVEL 4: SUPPORT                                      Priority │
│  ───────────────────────────────────────────────────────    ★☆☆☆☆  │
│  Files: Aleros.rtf, CSV files, Markdown guides                     │
│                                                                      │
│  Contextual and supplementary information.                         │
│  • Technical guides (aleros, overhangs)                            │
│  • Product indexes (CSV)                                           │
│  • Context documents                                                │
│                                                                      │
│  RULE: Use only for additional context                             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## File Reference

### Level 1: Master Files

#### `BMC_Base_Conocimiento_GPT-2.json`

**Location:** Project root  
**Priority:** MAXIMUM  
**Purpose:** Primary source for prices, formulas, specifications

**Structure:**

```json
{
  "metadata": {
    "version": "2.0",
    "last_updated": "2026-01-21",
    "source": "BMC Knowledge Base"
  },
  "productos": {
    "ISODEC_EPS": {
      "espesores": {
        "100": {
          "precio_shopify": 46.07,
          "ancho_util": 0.95,
          "autoportancia": 5.5,
          "coeficiente_termico": 2.5
        },
        "150": {
          "precio_shopify": 62.35,
          "ancho_util": 0.95,
          "autoportancia": 7.5,
          "coeficiente_termico": 3.75
        }
      }
    }
  },
  "formulas_cotizacion": {
    "cantidad_paneles": "ceil(area_total / (largo_panel * ancho_util))",
    "fijaciones_por_panel": 2,
    "varillas_por_fijacion": 1
  },
  "reglas_negocio": {
    "iva": 0.22,
    "pendiente_minima_techo": 0.07,
    "moneda": "USD"
  },
  "formulas_ahorro_energetico": {
    "ahorro_climatizacion": "delta_R * coeficiente * area * horas_uso"
  },
  "datos_referencia_uruguay": {
    "costo_kwh": 0.15,
    "horas_climatizacion_anual": 2000
  }
}
```

### Level 2: Validation Files

#### `BMC_Base_Unificada_v4.json`

**Location:** `Files/BMC_Base_Unificada_v4.json`  
**Priority:** High  
**Purpose:** Cross-reference and validation only

### Level 3: Dynamic Files

#### `panelin_truth_bmcuruguay_web_only_v2.json`

**Location:** `Files/` or root  
**Priority:** Medium  
**Purpose:** Current web prices and stock status

### Level 4: Support Files

| File | Purpose |
|------|---------|
| `Aleros.rtf` or `Aleros -2.rtf` | Technical rules for overhangs |
| `*.csv` | Product indexes |
| `*.md` | Context documents |

---

## Validation Rules

### Mandatory Rules

1. **BEFORE giving any price**: READ `BMC_Base_Conocimiento_GPT-2.json`
2. **NEVER invent** prices or specifications not in the JSON
3. **If not found**: Say "No tengo esa información en mi base de conocimiento"
4. **If conflict**: Use Level 1 and report the difference
5. **NEVER calculate** prices from cost × margin. Use Shopify price from JSON

### Guardrails Checklist

Before responding, verify:

| Check | Action if Failed |
|-------|------------------|
| ✓ Info in KB? | "No tengo esa información" |
| ✓ Source is Level 1? | Use Level 1 and report difference |
| ✓ Any conflicts? | Report and use Level 1 |
| ✓ Business rules applied? | Validate IVA, minimum slope |
| ✓ Correct formulas? | Only use formulas from JSON |
| ✓ Energy analysis included? | Include in ALL panel comparisons |
| ✓ Estimated costs clear? | Explain if estimated |
| ✓ Long-term value? | Combine initial cost + future value |

---

## Conflict Detection

### Types of Conflicts

| Type | Description | Severity |
|------|-------------|----------|
| **Price Mismatch** | Different prices between levels | Critical |
| **Spec Mismatch** | Different specifications | High |
| **Missing Data** | Data in one level, not another | Medium |
| **Format Conflict** | Structural differences | Low |

### Conflict Detection Code

```python
from panelin_improvements.conflict_detector import ConflictDetector

detector = ConflictDetector(kb_path="Files/")

# Detect all conflicts
conflicts = detector.detect_all_conflicts()

for conflict in conflicts:
    print(f"Type: {conflict.type}")
    print(f"Severity: {conflict.severity}")
    print(f"Level 1 Value: {conflict.level1_value}")
    print(f"Other Value: {conflict.other_value}")
    print(f"Recommendation: {conflict.recommendation}")
```

### Conflict Resolution

1. **Always trust Level 1** for prices and formulas
2. **Report conflicts** to knowledge base maintainers
3. **Log discrepancies** for future analysis
4. **Update lower levels** to match Level 1 when appropriate

---

## KB Management

### Health Check

```bash
# Run KB analysis
python -m gpt_kb_config_agent.main analyze --kb-path "Files/"
```

**Output:**

```
Knowledge Base Analysis Report
==============================

Health Score: 87/100 ✅

Level 1 (Master):
  ✅ BMC_Base_Conocimiento_GPT-2.json - Present
  Products: 24
  Formulas: 9
  Business Rules: 6

Level 2 (Validation):
  ✅ BMC_Base_Unificada_v4.json - Present
  Products: 28 (4 more than Level 1)

Level 3 (Dynamic):
  ✅ panelin_truth_bmcuruguay_web_only_v2.json - Present
  Last Updated: 2026-01-20

Level 4 (Support):
  ✅ Aleros -2.rtf - Present
  ✅ CSV index - Present

Conflicts Detected: 2
  - Price mismatch: ISODEC 100mm ($46.07 vs $45.99) [MEDIUM]
  - Missing: ISOWALL 80mm not in Level 3 [LOW]
```

### Update Process

```python
from gpt_kb_config_agent import GPTKnowledgeBaseAgent

agent = GPTKnowledgeBaseAgent(
    knowledge_base_path="Files/",
    output_path="gpt_configs/"
)

# Validate and fix
result = agent.validate_and_fix()

print(f"Conflicts resolved: {result['resolved']}")
print(f"Conflicts remaining: {result['remaining']}")
```

### Evolution

```python
# Evolve knowledge base based on usage patterns
evolution = agent.evolve_knowledge_base(strategy="auto")

print(f"Items added: {evolution['items_added']}")
print(f"Items updated: {evolution['items_updated']}")
print(f"Recommendations: {evolution['recommendations']}")
```

---

## Best Practices

### 1. Always Verify Level 1 First

```python
def get_price(product, thickness):
    # ALWAYS check Level 1 first
    level1_price = read_level1_price(product, thickness)
    
    if level1_price is None:
        return {"error": "No tengo esa información en mi base de conocimiento"}
    
    return {"price": level1_price, "source": "Level 1 Master"}
```

### 2. Log All KB Access

```python
import logging

logger = logging.getLogger("kb_access")

def access_kb(level, file, key):
    logger.info(f"KB Access: Level {level}, File: {file}, Key: {key}")
    # ... access logic
```

### 3. Regular Validation

Schedule regular KB validation:

```python
from kb_auto_scheduler import KBAutoScheduler

scheduler = KBAutoScheduler()
scheduler.schedule_validation(
    interval="daily",
    time="02:00",
    notify_on_conflict=True
)
```

### 4. Backup Before Updates

```python
from gpt_kb_config_agent import GPTKnowledgeBaseAgent

agent = GPTKnowledgeBaseAgent(knowledge_base_path="Files/")

# Automatic backup before evolution
agent.evolve_knowledge_base(
    strategy="auto",
    create_backup=True  # Creates timestamped backup
)
```

### 5. Document Changes

Maintain a changelog for KB updates:

```markdown
# KB Changelog

## 2026-01-21
- Updated ISODEC 100mm price to $46.07
- Added ISOWALL 80mm specifications
- Fixed autoportancia data for ISOPANEL 150mm

## 2026-01-15
- Initial Level 1 Master file creation
- Migrated from legacy system
```

---

## Internal Knowledge Base (Sensitive)

### BROMYROS Cost/Price Data

**Files:**
- `BROMYROS_Base_Costos_Precios_2026.json`
- `MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv`

**Purpose:** Internal cost and margin data

**WARNING:** 
- Contains sensitive financial information
- NOT for public GPT
- Only for internal agents

**Usage:**

```python
# For internal agents only
from create_bromyros_kb import load_bromyros_kb

kb = load_bromyros_kb()
# Contains: costs, margins, enterprise prices, retail prices
```

---

## Related Documentation

- [[KB-Indexing-Agent]] - Expert agent for KB indexing and retrieval (optimized for GPT OpenAI Actions)
- [[Agents-Overview]] - Agents that use the KB
- [[Training-System]] - How training updates the KB
- [[Troubleshooting]] - Common KB issues

---

<p align="center">
  <a href="[[Agents-Overview]]">← Agents Overview</a> |
  <a href="[[Training-System]]">Training System →</a>
</p>
