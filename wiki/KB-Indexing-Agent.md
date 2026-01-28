# KB Indexing Expert Agent

**Version**: 1.0.0  
**Purpose**: Expert agent specialized in Knowledge Base indexing, retrieval, and validation optimized for GPT OpenAI Actions API calls.

---

## Overview

The KB Indexing Expert Agent provides fast, accurate access to the 4-level hierarchical Knowledge Base system. It's specifically optimized for integration with GPT OpenAI Actions, providing structured function schemas and efficient indexing.

### Key Features

- ✅ **Hybrid Search**: Combines semantic, keyword, and structured search
- ✅ **Hierarchical Access**: Enforces 4-level priority system (Master → Validation → Dynamic → Support)
- ✅ **Fast Indexing**: Builds searchable indexes for quick retrieval
- ✅ **Conflict Detection**: Identifies and reports conflicts between KB levels
- ✅ **Structured Retrieval**: Direct access to products, formulas, and specifications
- ✅ **GPT Optimized**: Function schemas designed for OpenAI Actions API

---

## Architecture

### KB Hierarchy

```
Level 1 - MASTER (Highest Priority)
├── BMC_Base_Conocimiento_GPT.json
└── BMC_Base_Conocimiento_GPT-2.json

Level 2 - VALIDATION
└── BMC_Base_Unificada_v4.json

Level 3 - DYNAMIC
└── panelin_truth_bmcuruguay_web_only_v2.json

Level 4 - SUPPORT
├── Aleros -2.rtf
└── panelin_truth_bmcuruguay_catalog_v2_index.csv
```

### Indexing System

The agent builds a comprehensive index of all KB files:

- **Key Indexing**: Indexes all JSON keys for fast lookup
- **Path Indexing**: Tracks full paths (e.g., `productos.ISODEC_EPS.espesores.100`)
- **Value Indexing**: Indexes leaf values for content search
- **Metadata Caching**: Caches file metadata (size, modification date, level)

---

## Available Functions

### 1. `search_knowledge_base`

**Purpose**: Search KB using hybrid semantic + keyword + structured search

**Parameters**:
- `query` (required): Search query string
- `level_priority` (optional): Preferred KB level (1-4)
- `search_type` (optional): "hybrid" (default), "keyword", "semantic", "structured"
- `max_results` (optional): Maximum results (default: 10, max: 50)

**Returns**: Search results with scores, levels, and metadata

**Example**:
```python
result = search_knowledge_base(
    query="ISODEC 100mm price",
    level_priority=1,
    search_type="hybrid",
    max_results=10
)
```

### 2. `get_product_information`

**Purpose**: Get detailed product information from Level 1 Master KB

**Parameters**:
- `product_name` (required): Product name (e.g., "ISODEC EPS")
- `thickness` (optional): Specific thickness in mm

**Returns**: Product specifications, prices, thicknesses, autoportancia

**Example**:
```python
result = get_product_information("ISODEC EPS", thickness="100")
```

### 3. `get_formula`

**Purpose**: Get quotation or energy savings formulas from Level 1 Master KB

**Parameters**:
- `formula_name` (required): Formula name (e.g., "cantidad_paneles")

**Returns**: Formula definition and metadata

**Example**:
```python
result = get_formula("cantidad_paneles")
```

### 4. `validate_kb_health`

**Purpose**: Validate KB health, check file availability, detect conflicts

**Parameters**: None

**Returns**: Health report with status, conflicts, and warnings

**Example**:
```python
health = validate_kb_health()
print(health["status"])  # "healthy", "degraded", or "error"
```

### 5. `get_kb_metadata`

**Purpose**: Get comprehensive KB metadata (structure, file locations, sizes)

**Parameters**: None

**Returns**: Metadata about all KB files and hierarchy

**Example**:
```python
metadata = get_kb_metadata()
print(metadata["files"])
```

### 6. `build_kb_index`

**Purpose**: Build or rebuild the KB search index

**Parameters**:
- `level` (optional): Build index for specific level only

**Returns**: Index statistics and metadata

**Example**:
```python
index = build_kb_index()  # Index all levels
# or
index = build_kb_index(level=1)  # Index only Level 1
```

---

## Setup

### 1. Install Dependencies

```bash
pip install openai
```

### 2. Set OpenAI API Key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Setup OpenAI Assistant

```bash
python setup_kb_indexing_agent.py
```

This will:
- Create an OpenAI Assistant with all KB functions
- Save the assistant ID to `.kb_indexing_assistant_id`
- Generate configuration file in `gpt_configs/`

### 4. Test Functions Locally

```bash
python setup_kb_indexing_agent.py test
```

---

## Usage

### Direct Function Calls (Python)

```python
from agente_kb_indexing import (
    search_knowledge_base,
    get_product_information,
    get_formula
)

# Search KB
results = search_knowledge_base("ISODEC 100mm price", level_priority=1)

# Get product info
product = get_product_information("ISODEC EPS", "100")

# Get formula
formula = get_formula("cantidad_paneles")
```

### OpenAI Assistant Integration

```python
from openai import OpenAI
from agente_kb_indexing import get_all_kb_function_schemas

client = OpenAI(api_key="your-api-key")

# Create assistant with KB functions
assistant = client.beta.assistants.create(
    name="KB Indexing Expert",
    instructions="You are a KB indexing expert...",
    model="gpt-4",
    tools=[{"type": "function", "function": schema} for schema in get_all_kb_function_schemas()]
)

# Use assistant
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="What's the price of ISODEC 100mm?"
)
```

### GPT Builder Integration

1. Open GPT Builder
2. Go to "Actions" section
3. Import function schemas from `agente_kb_indexing.py`
4. Configure authentication (if needed)
5. Test each function

---

## Search Strategies

### Hybrid Search (Recommended)

Combines keyword, semantic, and structured search:

```python
results = search_knowledge_base(
    query="autoportancia 150mm",
    search_type="hybrid"
)
```

**Best for**: General queries, exploratory searches

### Keyword Search

Exact and word matching:

```python
results = search_knowledge_base(
    query="ISODEC EPS 100",
    search_type="keyword"
)
```

**Best for**: Known product names, exact matches

### Structured Search

Path-based search:

```python
results = search_knowledge_base(
    query="productos.ISODEC_EPS.espesores",
    search_type="structured"
)
```

**Best for**: Known JSON paths, structured queries

---

## Performance Optimization

### 1. Use Direct Functions for Known Data

Instead of searching, use direct functions:

```python
# Fast - Direct access
product = get_product_information("ISODEC EPS", "100")

# Slower - Search
results = search_knowledge_base("ISODEC EPS 100mm")
```

### 2. Build Index Once

Build index at startup or after KB updates:

```python
from agente_kb_indexing import build_kb_index

# Build index once
index = build_kb_index()
```

### 3. Prioritize Level 1

Always search Level 1 first:

```python
results = search_knowledge_base(
    query="price",
    level_priority=1  # Search Level 1 first
)
```

### 4. Limit Results

Use `max_results` to limit response size:

```python
results = search_knowledge_base(
    query="ISODEC",
    max_results=5  # Only top 5 results
)
```

---

## Error Handling

### Product Not Found

```python
result = get_product_information("UNKNOWN_PRODUCT")
if "error" in result:
    print(f"Error: {result['error']}")
    # Suggest similar products or search
```

### KB File Missing

```python
health = validate_kb_health()
if health["status"] != "healthy":
    print("Warning: KB health issues detected")
    for warning in health["warnings"]:
        print(f"  - {warning}")
```

### Search Returns No Results

```python
results = search_knowledge_base("rare query")
if results["total_matches"] == 0:
    # Try broader search
    results = search_knowledge_base("broader query", max_results=20)
```

---

## Best Practices

1. **Always Check Level 1 First**: Level 1 Master is the source of truth
2. **Use Direct Functions When Possible**: Faster than search for known data
3. **Validate KB Health**: Check health before critical operations
4. **Handle Conflicts**: Report conflicts, use Level 1 as authoritative
5. **Cache Results**: Cache frequently accessed data
6. **Build Index After Updates**: Rebuild index when KB files change
7. **Use Appropriate Search Type**: Choose search type based on query type
8. **Limit Results**: Use `max_results` to control response size

---

## Troubleshooting

### Index Not Found

**Problem**: Search returns no results

**Solution**: Build index first
```python
build_kb_index()
```

### KB Files Not Found

**Problem**: Functions return "file not found" errors

**Solution**: Check file locations
```python
metadata = get_kb_metadata()
print(metadata["files"])
```

### Slow Performance

**Problem**: Search is slow

**Solution**: 
- Build index once at startup
- Use direct functions instead of search
- Limit results with `max_results`
- Search specific level with `level_priority`

---

## Related Documentation

- [[Knowledge-Base]] - KB structure and hierarchy
- [[Agents-Overview]] - Other agents using KB
- [[API-Reference]] - API documentation

---

## Configuration Files

- `gpt_configs/KB_Indexing_Expert_Agent_config.json` - Full agent configuration
- `gpt_configs/KB_Indexing_Expert_Agent_setup.json` - Setup output (after running setup script)
- `.kb_indexing_assistant_id` - OpenAI Assistant ID

---

<p align="center">
  <a href="[[Knowledge-Base]]">← Knowledge Base</a> |
  <a href="[[Agents-Overview]]">Agents Overview →</a>
</p>
