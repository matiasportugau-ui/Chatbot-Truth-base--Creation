---
applyTo: "**/*.py"
---

# Python Coding Conventions

## Purpose

These instructions guide Copilot code review for Python files in this repository.
This repository is an AI-powered chatbot system for construction panel quotations.

## Naming Conventions

- Use snake_case for variables and functions
- Use PascalCase for class names
- Use UPPERCASE for constants
- Use descriptive, intention-revealing names

```python
# Avoid
d = new_data()
x = users.filter(u: u.active)

# Prefer
calculation_data = new_data()
active_users = users.filter(user: user.is_active)
```

## Financial Calculations

- **CRITICAL**: Always use `Decimal` for financial calculations, NEVER `float`
- Use `ROUND_HALF_UP` for consistent rounding
- Convert float to Decimal via string: `Decimal(str(value))`

```python
from decimal import Decimal, ROUND_HALF_UP

# Avoid
price = 41.88  # float introduces precision errors

# Prefer
price = Decimal('41.88')
area = Decimal('2.3')
total = (price * area).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

## Code Style

- Follow PEP 8 style guidelines
- Limit line length to 88 characters (Black formatter standard)
- Use type hints for function signatures
- Write descriptive docstrings with Spanish technical terms when appropriate

```python
# Prefer
def calculate_panel_quote(
    panel_type: str,
    thickness_mm: int,
    length_m: Decimal,
    width_m: Decimal,
    quantity: int,
) -> dict:
    """Calculate panel quotation with BOM.
    
    Args:
        panel_type: Type of panel (e.g., "Isopanel", "Isodec")
        thickness_mm: Panel thickness in millimeters
        length_m: Panel length in meters
        width_m: Panel width in meters  
        quantity: Number of panels
        
    Returns:
        Dictionary containing quotation details and BOM
    """
```

## Best Practices

- Use list comprehensions for simple transformations
- Prefer f-strings for string formatting
- Use context managers (with statements) for resource management
- Use explicit `None` checks instead of implicit falsy checks

```python
# Avoid
file = open('data.txt')
content = file.read()
file.close()

# Prefer
with open('data.txt') as file:
    content = file.read()
```

## Error Handling

- Raise `ValueError` for invalid inputs with clear messages
- Use specific exception types, not bare `except:`
- Include helpful error messages in Spanish when user-facing

```python
# Avoid
try:
    process_data(data)
except:
    pass

# Prefer
try:
    process_data(data)
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    raise
```

## Testing

- Use pytest framework
- Test functions should follow `test_*` pattern
- Use dependency injection for testability (e.g., `bom_rules` parameter)
- Use descriptive test names in Spanish docstrings when explaining technical concepts

```python
def test_minimum_length_adjustment():
    """Test que paneles menores al mínimo se ajustan."""
    result = calculate_panel_quote(
        panel_type="Isopanel",
        thickness_mm=50,
        length_m=Decimal('2.0'),
        width_m=Decimal('1.0'),
        quantity=10,
    )
    assert result["calculation_verified"] is True
```

## Security

- Never hardcode credentials or API keys
- Use environment variables via `.env` files
- Use `python-dotenv` for loading environment variables
- Store Google Service Account credentials securely (not in repo)
