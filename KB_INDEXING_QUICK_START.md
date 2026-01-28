# KB Indexing Expert Agent - Quick Start

Quick reference guide for the KB Indexing Expert Agent optimized for GPT OpenAI Actions.

## 🚀 Quick Setup

```bash
# 1. Install dependencies
pip install openai

# 2. Set API key
export OPENAI_API_KEY="your-api-key"

# 3. Setup agent
python setup_kb_indexing_agent.py

# 4. Test functions
python setup_kb_indexing_agent.py test
```

## 📋 Function Reference

### Search KB
```python
from agente_kb_indexing import search_knowledge_base

results = search_knowledge_base(
    query="ISODEC 100mm price",
    level_priority=1,
    search_type="hybrid",
    max_results=10
)
```

### Get Product Info
```python
from agente_kb_indexing import get_product_information

product = get_product_information("ISODEC EPS", thickness="100")
```

### Get Formula
```python
from agente_kb_indexing import get_formula

formula = get_formula("cantidad_paneles")
```

### Validate Health
```python
from agente_kb_indexing import validate_kb_health

health = validate_kb_health()
print(health["status"])  # "healthy", "degraded", or "error"
```

### Build Index
```python
from agente_kb_indexing import build_kb_index

index = build_kb_index()  # All levels
# or
index = build_kb_index(level=1)  # Specific level
```

## 🎯 Common Use Cases

### 1. Get Product Price
```python
product = get_product_information("ISODEC EPS", "100")
price = product["thicknesses"]["100"]["precio_shopify"]
```

### 2. Search for Autoportancia
```python
results = search_knowledge_base("autoportancia 150mm", level_priority=1)
```

### 3. Get Quotation Formula
```python
formula = get_formula("cantidad_paneles")
```

### 4. Health Check Before Operation
```python
health = validate_kb_health()
if health["status"] == "healthy":
    # Proceed with operation
    pass
```

## 📊 KB Hierarchy Priority

1. **Level 1 - MASTER** (Always use first)
   - `BMC_Base_Conocimiento_GPT-2.json`
   - Source of truth for prices, formulas

2. **Level 2 - VALIDATION**
   - `BMC_Base_Unificada_v4.json`
   - Cross-reference only

3. **Level 3 - DYNAMIC**
   - `panelin_truth_bmcuruguay_web_only_v2.json`
   - Updated prices, stock

4. **Level 4 - SUPPORT**
   - `Aleros -2.rtf`, CSV files
   - Contextual info

## ⚡ Performance Tips

- ✅ Use `get_product_information()` for known products (faster)
- ✅ Use `search_knowledge_base()` for exploratory queries
- ✅ Build index once at startup: `build_kb_index()`
- ✅ Always prioritize Level 1: `level_priority=1`
- ✅ Limit results: `max_results=10` (default)

## 🔧 OpenAI Assistant Integration

```python
from openai import OpenAI
from agente_kb_indexing import get_all_kb_function_schemas

client = OpenAI(api_key="your-key")

assistant = client.beta.assistants.create(
    name="KB Indexing Expert",
    instructions="You are a KB indexing expert...",
    model="gpt-4",
    tools=[{"type": "function", "function": schema} 
           for schema in get_all_kb_function_schemas()]
)
```

## 📚 Full Documentation

See `wiki/KB-Indexing-Agent.md` for complete documentation.
