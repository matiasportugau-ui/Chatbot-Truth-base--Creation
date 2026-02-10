# Performance Improvements Analysis

## Summary

This document identifies slow or inefficient code patterns in the repository and provides specific recommendations for optimization. The analysis focuses on the core quotation calculator modules and supporting utilities.

---

## 1. Repeated File I/O Without Caching (HIGH PRIORITY)

### Issue
Multiple modules repeatedly load JSON files from disk without caching. Each function call triggers a new file read operation.

### Affected Files

| File | Function | Problem |
|------|----------|---------|
| `panelin/tools/knowledge_base.py:27` | `_load_knowledge_base()` | Loads KB on every function call |
| `panelin/tools/quotation_calculator.py:42` | `_load_knowledge_base()` | Loads KB on every function call |
| `panelin/tools/bom_calculator.py:58` | `_load_json()` | No caching for accessories or BOM rules |
| `panelin_core/quotation_calculator.py:22` | `_load_catalog()` | Loads catalog on every function call |

### Example of Inefficient Code

```python
# panelin/tools/knowledge_base.py
def _load_knowledge_base(kb_path: Optional[Path] = None) -> Dict[str, Any]:
    """Carga la base de conocimiento desde JSON."""
    path = kb_path or DEFAULT_KB_PATH
    
    # Try multiple possible paths
    possible_paths = [path, ...]
    
    for p in possible_paths:
        if p.exists():
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)  # Disk I/O on every call!
```

### Recommended Fix

Use module-level caching with `functools.lru_cache`:

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def _load_knowledge_base_cached() -> Dict[str, Any]:
    """Cached load of knowledge base."""
    path = DEFAULT_KB_PATH
    possible_paths = [path, ...]
    
    for p in possible_paths:
        if p.exists():
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)
    raise FileNotFoundError(f"Knowledge base not found")

def _load_knowledge_base(kb_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load knowledge base with optional custom path."""
    if kb_path is None:
        return _load_knowledge_base_cached()
    # Custom path - load directly without cache
    with open(kb_path, 'r', encoding='utf-8') as f:
        return json.load(f)
```

### Already Optimized (Good Example)
`GPT_Panelin_copilotedit/03_PYTHON_TOOLS/quotation_calculator_v3.py` correctly uses module-level caching:

```python
_ACCESSORIES_CATALOG_CACHE = None
_BOM_RULES_CACHE = None

def _load_accessories_catalog() -> dict:
    global _ACCESSORIES_CATALOG_CACHE
    if _ACCESSORIES_CATALOG_CACHE is not None:
        return _ACCESSORIES_CATALOG_CACHE
    # ... load and cache
```

---

## 2. Inefficient String Normalization in Loops (MEDIUM PRIORITY)

### Issue
The `lookup_accessory_price()` function in `bom_calculator.py` imports and calls `unicodedata` functions inside nested loops.

### Affected File
`panelin/tools/bom_calculator.py:179-262`

### Inefficient Code

```python
def lookup_accessory_price(...):
    # Strategy 5: Match by name/sku containing the tipo keyword and family compatibility
    # Normalize accents for matching
    import unicodedata  # Import inside function (lines 241-242)
    def _strip_accents(s: str) -> str:
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

    tipo_norm = _strip_accents(tipo.lower())
    for item in all_items:
        item_name_norm = _strip_accents(item.get("name", "").lower())  # Called in loop
```

### Recommended Fix

1. Move import to module level
2. Cache normalized values or pre-compute them when loading catalog:

```python
# At module level
import unicodedata

def _strip_accents(s: str) -> str:
    """Strip accents from string for fuzzy matching."""
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

# In catalog loading, pre-compute normalized names
def _load_accessories_with_index(path: Path) -> dict:
    catalog = _load_json(path)
    # Pre-compute normalized names for fast lookup
    catalog['_name_index'] = {
        _strip_accents(item.get("name", "").lower()): item
        for section in catalog.values() if isinstance(section, list)
        for item in section
    }
    return catalog
```

---

## 3. Nested Loops for Product Matching (MEDIUM PRIORITY)

### Issue
Several functions perform O(n) linear searches through products dictionary multiple times with multiple strategies. This is inefficient for large catalogs.

### Affected Files
- `panelin/tools/knowledge_base.py:47-112` (`lookup_product_specs`)
- `panelin/tools/quotation_calculator.py:565-586` (`_fuzzy_match_product`)
- `panelin/tools/bom_calculator.py:179-262` (`lookup_accessory_price`)

### Example of Inefficient Code

```python
# panelin/tools/knowledge_base.py
def lookup_product_specs(product_identifier: str, ...):
    # Strategy 1: Exact match by key - loops through all products
    for key, product in products.items():
        if key.lower() == normalized:
            return _format_product_spec(key, product)
        # ...
    
    # Strategy 2: Match by SKU - loops through all products AGAIN
    for key, product in products.items():
        if product.get("sku", "").lower() == normalized:
            return _format_product_spec(key, product)
    
    # Strategy 3: Match by name - loops through all products AGAIN
    for key, product in products.items():
        # ...
    
    # Strategy 4: Match by panel type - loops AGAIN
    for keyword, base_key in type_keywords.items():
        for key, product in products.items():
            # ...
```

### Recommended Fix

Build indices at load time:

```python
def _build_product_indices(products: Dict) -> Dict:
    """Build lookup indices for fast product matching."""
    indices = {
        'by_key_lower': {},      # key.lower() -> key
        'by_sku_lower': {},      # sku.lower() -> key
        'by_name_lower': {},     # name.lower() -> [keys]
        'by_family_thickness': {},  # (family, thickness) -> key
    }
    
    for key, product in products.items():
        indices['by_key_lower'][key.lower()] = key
        
        sku = product.get("sku", "")
        if sku:
            indices['by_sku_lower'][sku.lower()] = key
        
        name = product.get("name", "").lower()
        if name not in indices['by_name_lower']:
            indices['by_name_lower'][name] = []
        indices['by_name_lower'][name].append(key)
        
        # Build family-thickness index
        family = product.get("familia", product.get("family", "")).lower()
        thickness = product.get("thickness_mm")
        if family and thickness:
            indices['by_family_thickness'][(family, thickness)] = key
    
    return indices
```

---

## 4. Repeated Decimal Conversions (LOW PRIORITY)

### Issue
Values are repeatedly converted to Decimal type throughout calculations. While using Decimal is correct for financial precision, creating new Decimal objects is more expensive than native operations.

### Affected Files
- `panelin/tools/quotation_calculator.py` (multiple functions)
- `panelin/tools/bom_calculator.py` (multiple functions)
- `GPT_Panelin_copilotedit/03_PYTHON_TOOLS/quotation_calculator_v3.py`

### Example

```python
# Creates new Decimal object each time
discount_pct = _to_decimal(discount_percent)
discount_amount = _round_currency(subtotal * discount_pct / _to_decimal(100))  # _to_decimal(100) called repeatedly
```

### Recommended Fix

Pre-define common constants:

```python
# Module-level constants
DECIMAL_ZERO = Decimal('0')
DECIMAL_ONE = Decimal('1')
DECIMAL_100 = Decimal('100')
DECIMAL_1000 = Decimal('1000')

# In calculations
discount_amount = _round_currency(subtotal * discount_pct / DECIMAL_100)
```

---

## 5. Multiple Path Existence Checks (LOW PRIORITY)

### Issue
Knowledge base loading functions check multiple paths in sequence, calling `Path.exists()` multiple times.

### Affected Files
- `panelin/tools/knowledge_base.py:32-43`
- `panelin/tools/quotation_calculator.py:47-58`
- `panelin/tools/bom_calculator.py:65-75`

### Recommended Fix

Once the correct path is found, cache it:

```python
_KB_PATH_CACHE = None

def _get_kb_path() -> Path:
    global _KB_PATH_CACHE
    if _KB_PATH_CACHE is not None:
        return _KB_PATH_CACHE
    
    possible_paths = [DEFAULT_KB_PATH, ...]
    for p in possible_paths:
        if p.exists():
            _KB_PATH_CACHE = p
            return p
    raise FileNotFoundError(...)
```

---

## 6. Inefficient Accessory Flattening (MEDIUM PRIORITY)

### Issue
`lookup_accessory_price()` in `bom_calculator.py` rebuilds a flat list of all accessories on every call.

### Affected Code

```python
def lookup_accessory_price(...):
    acc_catalog = _load_json(accessories_path or ACCESSORIES_PATH)

    # Build a flat list of all accessories - DONE EVERY CALL
    all_items = []
    for section_key in ['perfileria_goterones', 'babetas', 'canalones', ...]:
        for item in acc_catalog.get(section_key, []):
            all_items.append(item)
```

### Recommended Fix

Pre-build the flattened list when loading:

```python
_ACCESSORIES_FLAT_CACHE = None

def _get_flat_accessories() -> List[Dict]:
    global _ACCESSORIES_FLAT_CACHE
    if _ACCESSORIES_FLAT_CACHE is not None:
        return _ACCESSORIES_FLAT_CACHE
    
    acc_catalog = _load_accessories_catalog()
    all_items = []
    for section_key in ['perfileria_goterones', 'babetas', 'canalones', ...]:
        all_items.extend(acc_catalog.get(section_key, []))
    
    _ACCESSORIES_FLAT_CACHE = all_items
    return all_items
```

---

## 7. Duplicate Import Statements (LOW PRIORITY)

### Issue
Some files have duplicate import statements.

### Affected File
`panelin_improvements/cost_matrix_tools/gsheets_manager.py:7-8, 13-16`

```python
import gspread
from google.oauth2.service_account import Credentials

import gspread  # Duplicate!
from google.oauth2.service_account import Credentials  # Duplicate!
```

### Recommended Fix

Remove duplicate imports.

---

## Implementation Priority

| Priority | Issue | Estimated Impact | Effort |
|----------|-------|------------------|--------|
| HIGH | #1 Repeated File I/O | 50-100x faster for repeated calls | Low |
| MEDIUM | #6 Accessory Flattening | 10-20x faster for accessory lookups | Low |
| MEDIUM | #3 Nested Loop Matching | 5-10x faster for product lookups | Medium |
| MEDIUM | #2 String Normalization | 2-5x faster for fuzzy matching | Low |
| LOW | #4 Decimal Constants | Minor improvement | Very Low |
| LOW | #5 Path Caching | Minor improvement | Very Low |
| LOW | #7 Duplicate Imports | Code cleanliness | Very Low |

---

## Quick Wins (Can Be Implemented Immediately)

1. **Add caching to `_load_knowledge_base()`** in `panelin/tools/knowledge_base.py`
2. **Add caching to `_load_json()`** in `panelin/tools/bom_calculator.py`
3. **Remove duplicate imports** in `panelin_improvements/cost_matrix_tools/gsheets_manager.py`
4. **Move unicodedata import** to module level in `panelin/tools/bom_calculator.py`

---

## Testing Recommendations

After implementing optimizations, verify:

1. Run existing tests to ensure no regressions:
   ```bash
   python3 -m pytest tests/ -v
   ```

2. For GPT_Panelin_copilotedit module:
   ```bash
   cd GPT_Panelin_copilotedit/03_PYTHON_TOOLS
   python3 -m pytest tests/ -v --override-ini="addopts=-v --tb=short -p no:warnings"
   ```

3. Benchmark before/after using simple timing:
   ```python
   import timeit
   from panelin.tools import knowledge_base
   
   # Before optimization
   time_before = timeit.timeit(
       lambda: knowledge_base.lookup_product_specs("Isopanel EPS", thickness_mm=100),
       number=100
   )
   
   # After optimization
   time_after = timeit.timeit(
       lambda: knowledge_base.lookup_product_specs("Isopanel EPS", thickness_mm=100),
       number=100
   )
   
   print(f"Speedup: {time_before / time_after:.1f}x")
   ```
