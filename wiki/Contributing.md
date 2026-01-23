# Contributing Guide

Thank you for your interest in contributing to the Panelin AI System! This document provides guidelines and instructions for contributing.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Pull Request Process](#pull-request-process)
6. [Coding Standards](#coding-standards)
7. [Documentation](#documentation)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be patient with newcomers
- Focus on constructive feedback
- Accept criticism gracefully

---

## Getting Started

### Types of Contributions

We welcome:

- **Bug fixes**: Fix issues in the codebase
- **Features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Knowledge Base**: Improve KB content and structure
- **Translations**: Translate documentation (Spanish/English)

### Finding Issues

1. Check [open issues](https://github.com/your-org/panelin/issues)
2. Look for `good first issue` label for beginners
3. Check `help wanted` label for priority items

---

## Development Setup

### Prerequisites

- Python 3.8+
- Node.js 16+ (for TypeScript SDK)
- Git
- An OpenAI API key

### Setup Steps

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/panelin.git
cd panelin

# 3. Add upstream remote
git remote add upstream https://github.com/your-org/panelin.git

# 4. Create virtual environment
python -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# 6. Install Node dependencies (optional)
npm install

# 7. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 8. Verify setup
python verificar_configuracion.py
```

---

## Making Changes

### Branch Naming

Use descriptive branch names:

```
feature/add-new-agent
fix/quotation-calculation-error
docs/improve-api-reference
test/add-training-tests
```

### Workflow

```bash
# 1. Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes
# ... edit files ...

# 4. Run tests
python -m pytest tests/

# 5. Run linting
python -m flake8 .

# 6. Commit changes
git add .
git commit -m "feat: add new feature description"

# 7. Push to your fork
git push origin feature/your-feature-name

# 8. Create Pull Request on GitHub
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding/updating tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance tasks

**Examples:**
```
feat(quotation): add support for ISOWALL PIR panels
fix(kb): correct autoportancia values for ISODEC 150mm
docs(wiki): add training system documentation
test(agents): add unit tests for orchestrator
```

---

## Pull Request Process

### Before Submitting

1. **Test your changes:**
   ```bash
   python -m pytest tests/
   ```

2. **Run linting:**
   ```bash
   python -m flake8 .
   ```

3. **Update documentation** if needed

4. **Add tests** for new functionality

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated existing tests

## Documentation
- [ ] Updated relevant documentation
- [ ] Added code comments

## Related Issues
Fixes #123
```

### Review Process

1. Maintainer reviews code
2. Automated tests run
3. Address feedback
4. Approval and merge

---

## Coding Standards

### Python Style

Follow PEP 8 with these additions:

```python
# Good
def calculate_quotation(
    product: str,
    thickness: str,
    length: float,
    width: float
) -> Dict[str, Any]:
    """
    Calculate a complete quotation.
    
    Args:
        product: Product type (e.g., "ISODEC EPS")
        thickness: Thickness in mm
        length: Length in meters
        width: Width in meters
    
    Returns:
        Dictionary with quotation details
    
    Raises:
        ValueError: If product not found
    """
    pass
```

### Type Hints

Use type hints for all public functions:

```python
from typing import Dict, List, Optional, Any

def process_data(
    items: List[Dict[str, Any]],
    filter_by: Optional[str] = None
) -> List[Dict[str, Any]]:
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Short description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is empty
    
    Example:
        >>> example_function("test", 42)
        True
    """
    pass
```

### File Organization

```
module/
├── __init__.py          # Public exports
├── main.py              # Main entry point
├── core.py              # Core functionality
├── utils.py             # Utility functions
├── exceptions.py        # Custom exceptions
└── types.py             # Type definitions
```

---

## Documentation

### Wiki Contributions

Wiki pages use Markdown:

```markdown
# Page Title

Brief introduction.

---

## Table of Contents

1. [Section 1](#section-1)
2. [Section 2](#section-2)

---

## Section 1

Content here.

### Subsection

More content.

```python
# Code example
print("Hello")
```

---

## Section 2

More content.

---

<p align="center">
  <a href="[[Previous-Page]]">← Previous</a> |
  <a href="[[Next-Page]]">Next →</a>
</p>
```

### Code Documentation

Document all public APIs:

```python
class QuotationAgent:
    """
    Agent for calculating construction panel quotations.
    
    This agent handles quotation calculations for various panel types
    including ISODEC, ISOPANEL, ISOROOF, and ISOWALL.
    
    Attributes:
        kb_path: Path to knowledge base files
        motor: Quotation calculation engine
    
    Example:
        >>> agent = QuotationAgent(kb_path="Files/")
        >>> result = agent.calculate(product="ISODEC EPS", ...)
    """
    pass
```

---

## Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Fixtures
├── test_quotation.py     # Quotation tests
├── test_agents.py        # Agent tests
├── test_kb.py            # KB tests
└── test_training.py      # Training tests
```

### Writing Tests

```python
import pytest
from agente_cotizacion_panelin import calcular_cotizacion_agente

class TestQuotationAgent:
    """Tests for quotation agent."""
    
    def test_basic_quotation(self):
        """Test basic quotation calculation."""
        result = calcular_cotizacion_agente(
            producto="ISODEC EPS",
            espesor="100",
            largo=10.0,
            ancho=5.0,
            luz=4.5,
            tipo_fijacion="hormigon"
        )
        
        assert result['success'] is True
        assert result['cotizacion']['costos']['total'] > 0
    
    def test_autoportancia_validation(self):
        """Test that autoportancia is validated."""
        result = calcular_cotizacion_agente(
            producto="ISODEC EPS",
            espesor="100",
            largo=10.0,
            ancho=5.0,
            luz=6.0,  # Exceeds 5.5m limit
            tipo_fijacion="hormigon"
        )
        
        assert result['cotizacion']['validacion']['cumple_autoportancia'] is False
```

### Running Tests

```bash
# All tests
python -m pytest tests/

# Specific test file
python -m pytest tests/test_quotation.py

# With coverage
python -m pytest tests/ --cov=. --cov-report=html
```

---

## Questions?

- Open an issue for questions
- Join discussions on GitHub
- Tag maintainers for urgent matters

---

## Thank You!

Thank you for contributing to Panelin! Your contributions help make this project better for everyone.

---

<p align="center">
  <a href="[[Troubleshooting]]">← Troubleshooting</a> |
  <a href="[[Changelog]]">Changelog →</a>
</p>
