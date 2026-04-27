---
applyTo: "**/test_*.py"
---

# Test Files - Copilot Instructions

These instructions apply to all test files following the `test_*.py` pattern.

## 🧪 Testing Framework

This repository uses **pytest** for all testing.

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_quotation_calculations.py -v

# Run with detailed output
python3 -m pytest tests/test_deterministic_quote_calculator.py -xvs

# Run with coverage
python3 -m pytest tests/ --cov=panelin --cov-report=html
```

## 📋 Test Structure Standards

### File Organization
```
tests/
├── test_quotation_calculations.py
├── test_bom_generation.py
├── test_autoportancia_validation.py
└── conftest.py  # Shared fixtures
```

### Naming Conventions
- Test files: `test_*.py`
- Test classes: `Test*` (e.g., `TestQuotationCalculator`)
- Test functions: `test_*` (e.g., `test_basic_quote`)
- Fixtures: descriptive names (e.g., `sample_bom_rules`)

## ✅ Test Patterns

### Basic Test Structure
```python
import pytest
from decimal import Decimal

class TestQuotationCalculator:
    """Tests for quotation calculator functionality."""
    
    def test_basic_quote_calculation(self):
        """Test que paneles menores al mínimo se ajustan."""
        result = calculate_panel_quote(
            panel_type="Isopanel",
            thickness_mm=50,
            length_m=2.0,
            width_m=1.0,
            quantity=10,
        )
        
        assert result["total_usd"] == Decimal("837.60")
        assert result["calculation_verified"] is True
        assert len(result["warnings"]) == 0
```

### Using Fixtures
```python
import pytest
from decimal import Decimal

@pytest.fixture
def sample_bom_rules():
    """Sample BOM rules for testing."""
    return {
        "ISOPANEL_50mm": {
            "fasteners_per_m2": 6,
            "sealant_ml_per_m": 50
        }
    }

def test_with_fixture(sample_bom_rules):
    """Test using fixture data."""
    result = calculate_bom(panel_type="Isopanel", bom_rules=sample_bom_rules)
    assert "fasteners" in result
```

### Parametrized Tests
```python
import pytest
from decimal import Decimal

@pytest.mark.parametrize("thickness,expected_price", [
    (50, Decimal("41.88")),
    (80, Decimal("52.50")),
    (100, Decimal("63.12")),
])
def test_price_by_thickness(thickness, expected_price):
    """Test que precios varían correctamente por espesor."""
    result = get_price_per_m2("Isopanel", thickness)
    assert result == expected_price
```

## 🔒 Dependency Injection for Testing

Functions should accept optional parameters for test data injection:

```python
# In production code
def validate_quotation(
    price: Decimal,
    quantity: int,
    bom_rules: Optional[Dict] = None  # Allow injection
) -> bool:
    """Validate quotation with injectable rules."""
    if bom_rules is None:
        bom_rules = _load_default_bom_rules()
    # ... validation logic

# In test
def test_validation_with_custom_rules():
    """Test validation with custom BOM rules."""
    custom_rules = {"max_discount": Decimal("10.00")}
    result = validate_quotation(
        Decimal("100.00"),
        10,
        bom_rules=custom_rules
    )
    assert result is True
```

## 💰 Testing Financial Calculations

### Use Decimal, Not Float
```python
from decimal import Decimal

def test_financial_calculation():
    """Financial calculations must use Decimal."""
    # ✅ Correct
    price = Decimal('41.88')
    quantity = 10
    total = price * quantity
    assert total == Decimal('418.80')
    
    # ❌ Wrong - never compare floats for financial data
    # assert 41.88 * 10 == 418.80  # This can fail due to float precision
```

### Testing Rounding
```python
from decimal import Decimal, ROUND_HALF_UP

def test_price_rounding():
    """Test correct rounding for financial calculations."""
    price = Decimal('41.885')
    rounded = price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    assert rounded == Decimal('41.89')
```

## 🎯 Test Coverage Goals

- **Calculator functions**: 100% coverage required
- **BOM generation**: 100% coverage required
- **Validation functions**: 100% coverage required
- **Utility functions**: 90%+ coverage
- **Integration points**: Critical paths covered

## 🐛 Testing Error Conditions

```python
import pytest

def test_invalid_quantity_raises_error():
    """Test que cantidad inválida lanza ValueError."""
    with pytest.raises(ValueError, match="cantidad debe ser mayor"):
        calculate_quote(
            panel_type="Isopanel",
            thickness_mm=50,
            quantity=-5  # Invalid
        )

def test_unknown_panel_type():
    """Test que tipo de panel desconocido lanza ValueError."""
    with pytest.raises(ValueError, match="tipo de panel no reconocido"):
        calculate_quote(panel_type="UnknownPanel", thickness_mm=50, quantity=10)
```

## 📊 Testing with Mock Data

```python
from unittest.mock import Mock, patch

def test_with_mocked_kb_load():
    """Test with mocked knowledge base loading."""
    mock_kb = {
        "products": {
            "ISOPANEL_50mm": {"price_per_m2": "41.88"}
        }
    }
    
    with patch('module.load_knowledge_base', return_value=mock_kb):
        result = calculate_quote("Isopanel", 50, 2.0, 1.0, 10)
        assert result["price_per_m2"] == Decimal("41.88")
```

## ✨ Testing Best Practices

1. **Descriptive Names**: Use Spanish docstrings for technical concepts
2. **Arrange-Act-Assert**: Structure tests clearly
3. **One Concept Per Test**: Test one thing at a time
4. **Fast Tests**: Keep tests fast (<1s per test)
5. **Independent Tests**: Each test should be runnable independently
6. **Clear Assertions**: Use descriptive assertion messages

```python
def test_minimum_length_adjustment():
    """Test que longitud menor al mínimo se ajusta a 2.0m."""
    # Arrange
    panel_type = "Isopanel"
    requested_length = Decimal("1.5")
    expected_adjusted = Decimal("2.0")
    
    # Act
    result = calculate_quote(panel_type, 50, requested_length, 1.0, 10)
    
    # Assert
    assert result["adjusted_length_m"] == expected_adjusted, \
        "Panel length should be adjusted to minimum 2.0m"
```

## 🚫 What NOT to Do in Tests

- ❌ Don't use `assert True` or `assert False` without context
- ❌ Don't test implementation details, test behavior
- ❌ Don't use floating point for financial assertions
- ❌ Don't modify global state without cleanup
- ❌ Don't skip tests without a good reason and comment

## 🔄 Test Maintenance

When updating code:
1. Update existing tests first (TDD)
2. Run tests to verify they fail appropriately
3. Implement the change
4. Verify tests pass
5. Check test coverage hasn't decreased

## 📖 Related Resources

- `pytest` documentation: https://docs.pytest.org/
- Repository testing guide: `.github/copilot-instructions.md` (Testing Practices section)
- Coverage reports: Run with `--cov` flag to generate HTML reports
