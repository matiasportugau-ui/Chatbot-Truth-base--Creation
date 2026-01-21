# Training Data Guide

## 📊 Data Sources

The KB Training System can learn from three main data sources:

1. **Quotes** - Historical quotations and pricing data
2. **Interactions** - Customer support conversations
3. **Social Media** - Facebook and Instagram interactions

## 🚀 Quick Setup

### Step 1: Prepare Data Structure

```bash
python3 prepare_training_data.py
```

This will:
- ✅ Create training data directory structure
- ✅ Generate sample data files
- ✅ Load quotes from comparison system (if available)

### Step 2: Add Your Data

Add your own data files following the formats below.

## 📋 Data Formats

### Quotes Format

**File**: `training_data/quotes/your_quotes.json`

```json
[
  {
    "product_code": "ISODEC_EPS_100",
    "product_name": "ISODEC EPS 100mm",
    "price": 46.07,
    "currency": "USD",
    "thickness": "100mm",
    "quantity": 10,
    "total": 460.70,
    "timestamp": "2026-01-20T10:00:00"
  }
]
```

### Interactions Format

**File**: `training_data/interactions/your_interactions.json`

```json
[
  {
    "query": "¿Cuál es el precio de ISODEC 100mm?",
    "response": "El precio es $46.07 según BMC_Base_Conocimiento_GPT.json",
    "sources": ["BMC_Base_Conocimiento_GPT.json"],
    "timestamp": "2026-01-20T10:00:00",
    "metadata": {
      "is_question": true,
      "platform": "chat",
      "category": "pricing"
    }
  }
]
```

### Social Media Format

**Facebook**: `training_data/social_media/facebook/your_data.json`

**Instagram**: `training_data/social_media/instagram/your_data.json`

```json
[
  {
    "platform": "facebook",
    "content": "Consulta sobre precio de paneles",
    "timestamp": "2026-01-20T10:00:00",
    "engagement": {
      "likes": 5,
      "replies": 2
    },
    "metadata": {
      "is_question": true,
      "category": "pricing"
    }
  }
]
```

## 🔄 Loading from Existing Systems

### From Quote Comparison System

The system automatically loads quotes from `comparacion_vendedoras_sistema.json` if it exists.

To generate this file:
```bash
python3 comparar_cotizaciones_vendedoras.py
```

### From Social Media APIs

Use the GPT Simulation Agent to ingest social media data:
```python
from gpt_simulation_agent.agent_system.agent_social_ingestion import SocialIngestionEngine

engine = SocialIngestionEngine()
data = engine.ingest_all()
```

## 📁 Directory Structure

```
training_data/
├── interactions/
│   ├── sample_interactions.json
│   └── your_interactions.json
├── quotes/
│   ├── sample_quotes.json
│   ├── from_comparison.json
│   └── your_quotes.json
└── social_media/
    ├── facebook/
    │   └── sample_facebook.json
    └── instagram/
        └── sample_instagram.json
```

## ✅ Verification

Check your data is ready:

```bash
python3 integrate_training_system.py
```

If data is found, you'll see:
```
✅ Loaded X quotes
✅ Loaded X interactions
✅ X social interactions
```

## 💡 Tips

1. **Start Small**: Use sample data first to test the system
2. **Add Gradually**: Add your real data incrementally
3. **Format Matters**: Follow the JSON formats exactly
4. **Metadata Helps**: Include metadata for better analysis
5. **Timestamps**: Always include timestamps for temporal analysis

## 🎯 Next Steps

1. ✅ Run `prepare_training_data.py` to create structure
2. ✅ Add your data files
3. ✅ Run `integrate_training_system.py` to train KB
4. ✅ Review generated reports
5. ✅ Iterate and improve

---

**Ready to train your KB!** 🚀
