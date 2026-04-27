---
applyTo: "**/*.py"
---

# Python-Specific Copilot Instructions

These instructions apply to all Python files in the repository.

## Critical Rules

### Financial Calculations
**ALWAYS use `Decimal` for financial calculations, NEVER `float`**

```python
from decimal import Decimal, ROUND_HALF_UP

# ✅ Correct
price = Decimal('41.88')
area = Decimal('2.3')
total = (price * area).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# ❌ Wrong - float introduces precision errors
price = 41.88  # This will cause precision issues
```

### Type Hints
Always include type hints in function signatures:

```python
from decimal import Decimal
from typing import Dict, Optional

def calculate_quote(
    price: Decimal,
    quantity: int,
    discount: Optional[Decimal] = None
) -> Dict[str, Decimal]:
    """Calculate quotation with optional discount."""
    pass
```

### Error Handling
- Use specific exception types
- Include clear error messages in Spanish for user-facing errors
- Log exceptions properly for debugging

```python
# ✅ Good
if quantity <= 0:
    raise ValueError(f"La cantidad debe ser mayor a cero, recibido: {quantity}")

# ❌ Bad
if quantity <= 0:
    raise Exception("Invalid quantity")
```

## Code Style

### PEP 8 Compliance
- Line length: 88 characters (Black formatter default)
- Use 4 spaces for indentation
- Two blank lines between top-level functions/classes
- One blank line between methods

### Naming Conventions
- Functions: `snake_case` (e.g., `calculate_panel_quote`)
- Classes: `PascalCase` (e.g., `QuotationResult`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_DISCOUNT_PERCENT`)
- Private functions/methods: prefix with `_` (e.g., `_load_knowledge_base`)
- Spanish technical terms preserved: `autoportancia`, `canalón`, etc.

### Docstrings
Use clear docstrings with Spanish technical terms when appropriate:

```python
def validate_autoportancia(
    length_m: Decimal,
    width_m: Decimal,
    thickness_mm: int
) -> bool:
    """
    Valida la autoportancia del panel según dimensiones.
    
    Args:
        length_m: Longitud del panel en metros
        width_m: Ancho del panel en metros
        thickness_mm: Espesor del panel en milímetros
    
    Returns:
        True si el panel cumple con autoportancia requerida
    """
    pass
```

## Testing

### Test Structure
- Use `pytest` framework
- Test files: `test_*.py` pattern
- Test classes: `Test*` pattern
- Test functions: `test_*` pattern

### Dependency Injection
Functions should accept optional parameters for testing:

```python
def validate_quotation(
    price: Decimal,
    bom_rules: Optional[Dict] = None
) -> bool:
    """Allow injection of test bom_rules."""
    if bom_rules is None:
        bom_rules = _load_default_bom_rules()
    # ... rest of validation
```

## Common Patterns

### Knowledge Base Loading
```python
import json
from pathlib import Path
from typing import Dict

def _load_knowledge_base(kb_path: Optional[Path] = None) -> Dict:
    """Load knowledge base with fallback paths."""
    if kb_path is None:
        # Try Level 1 Master first
        kb_path = Path("GPT_Panelin_copilotedit/01_KNOWLEDGE_BASE/Level_1_Master/panelin_truth_bmcuruguay.json")
    
    with open(kb_path, 'r', encoding='utf-8') as f:
        return json.load(f)
```

### Calculator Results
Return structured dictionaries with Decimal values:

```python
from decimal import Decimal
from typing import Dict, List

def calculate_quote(...) -> Dict:
    """Return structured quote result."""
    return {
        "quotation_id": "Q-20260208-abc123",
        "total_usd": Decimal("837.60"),
        "calculation_verified": True,
        "warnings": []
    }
```

## Security

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Validate all user inputs
- Sanitize data before displaying to users
- Use `python-dotenv` for `.env` files

## Performance

- Decimal arithmetic is slower than float but **required** for financial calculations
- Cache knowledge base loads when appropriate
- Use lazy loading for large datasets
- Consider pagination for large result sets

## When Modifying Existing Code

1. Check if file uses `Decimal` - maintain consistency
2. Look for existing error handling patterns
3. Match the existing code style and naming
4. Update tests if changing function signatures
5. Run `pytest` to verify changes don't break existing functionality
