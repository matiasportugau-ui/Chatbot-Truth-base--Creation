# Copilot Instructions for Panelin Chatbot Truth Base

This repository contains the Panelin/BMC chatbot system for construction panel quotations and technical assistance. Follow these guidelines when contributing code.

## 📋 Repository Overview

**Purpose**: AI-powered chatbot system for BMC Uruguay (construction panel supplier) providing:
- Panel quotation calculations (ISOPANEL, ISODEC, ISOROOF, ISOWALL)
- Bill of Materials (BOM) generation
- Technical specifications and self-supporting span validation
- Knowledge base management and training
- Multi-agent architecture for specialized tasks

**Key Components**:
- `panelin/`: Core quotation and BOM calculation tools
- `panelin_core/`: Core calculator with requested dimension pricing
- `panelin_backend/`: Backend services and APIs
- `GPT_Panelin_copilotedit/`: GPT-specific quotation tools
- `kb_training_system/`: Knowledge base training and optimization
- `tests/`: Comprehensive test suite

## 🐍 Python Coding Standards

### Financial Calculations
**CRITICAL**: Always use `Decimal` for financial calculations, NEVER `float`
```python
from decimal import Decimal, ROUND_HALF_UP

# ✅ Correct
price = Decimal('41.88')
area = Decimal('2.3')
total = (price * area).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# ❌ Wrong
price = 41.88  # float introduces precision errors
```

### Code Style
- Follow PEP 8 conventions
- Use type hints for function signatures
- Write descriptive docstrings with Spanish technical terms when appropriate
- Prefer explicit over implicit (e.g., explicit `None` checks)

### Error Handling
- Raise `ValueError` for invalid inputs with clear messages
- Use specific exception types, not bare `except:`
- Include helpful error messages in Spanish when user-facing

### Naming Conventions
- Functions: `snake_case` (e.g., `calculate_panel_quote`)
- Classes: `PascalCase` (e.g., `QuotationResult`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_KB_PATH`)
- Private functions: prefix with `_` (e.g., `_load_knowledge_base`)

## 📊 Knowledge Base Hierarchy

**CRITICAL**: Always respect the knowledge base hierarchy when accessing data

### Priority Order:
1. **LEVEL 1 - MASTER** (⭐ Primary Source):
   - `BMC_Base_Conocimiento_GPT-2.json` - Authoritative source for prices, formulas, specifications
   - `accessories_catalog.json` - Accessories catalog with pricing
   - `bom_rules.json` - Parametric BOM rules by system

2. **LEVEL 2 - VALIDATION**:
   - `BMC_Base_Unificada_v4.json` - For cross-reference only

3. **LEVEL 3 - DYNAMIC**:
   - `panelin_truth_bmcuruguay_web_only_v2.json` - Web-scraped updated prices

4. **LEVEL 4 - SUPPORT**:
   - Various documentation and context files

**Rule**: In case of conflicts, LEVEL 1 always wins.

## 🧪 Testing Practices

### Running Tests
```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_quotation_calculations.py -v

# Run with detailed output
python3 -m pytest tests/test_deterministic_quote_calculator.py -xvs
```

### Test Structure
- Use `pytest` framework
- Test files: `test_*.py` pattern
- Test classes: `Test*` pattern (e.g., `TestDeterministicQuoteCalculator`)
- Test functions: `test_*` pattern
- Use descriptive test names in Spanish docstrings when explaining technical concepts

### Test Patterns
```python
import pytest

class TestQuotationCalculator:
    def test_basic_quote(self):
        """Test que paneles menores al mínimo se ajustan."""
        result = calculate_panel_quote(
            panel_type="Isopanel",
            thickness_mm=50,
            length_m=2.0,
            width_m=1.0,
            quantity=10,
        )
        assert result["total_usd"] == 963.20
        assert result["calculation_verified"] is True
```

### Dependency Injection for Testing
- Functions accept optional parameters for dependency injection (e.g., `bom_rules` parameter)
- Use this pattern to inject test data without modifying global state
- Example: `validate_autoportancia(length_m, width_m, thickness_mm, bom_rules=test_rules)`

## 🏗️ Calculator Conventions

### Two Calculator Variants
Be aware of two different quotation calculators with different behaviors:

1. **`panelin.tools.quotation_calculator`**: Adjusts to minimum length for pricing
   - Uses `adjusted_length` (enforces minimum panel length)
   - Quotes based on actual material needed

2. **`panelin_core.quotation_calculator`**: Prices based on requested dimensions
   - Uses `length_m` (requested length)
   - Shows warnings but prices as requested

Choose the appropriate calculator based on requirements.

### Validation Rules
- Always validate `autoportancia` (self-supporting span) using safety margins
- Check product/thickness combinations exist before quoting
- Verify minimum quantities and dimensions
- Use `validate_quotation()` to verify calculation integrity

## 🔒 Security and Sensitive Data

### Credentials and Secrets
- NEVER commit secrets, API keys, or credentials to code
- Use environment variables via `.env` (never commit `.env`, only `.env.example`)
- Use `python-dotenv` for loading environment variables
- Store Google Service Account credentials securely (not in repo)

### Google Sheets Authentication
```python
from google.oauth2.service_account import Credentials

# ✅ Correct - use Credentials from google.oauth2.service_account
creds = Credentials.from_service_account_file(
    'path/to/credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
```

### Knowledge Base Data
- JSON knowledge base files contain business-sensitive pricing data
- Code owners required for changes to:
  - `*.json` files (pricing catalogs)
  - `/config/` directory
  - `/gpt_configs/` directory
  - Core system files in `/panelin_core/`

## 📦 Dependencies and Packages

### Installing Dependencies
```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies (includes pytest)
pip install -r requirements-dev.txt

# Cloud Run deployment
pip install -r requirements-cloudrun.txt
```

### Key Dependencies
- `openai>=1.0.0` - OpenAI API integration
- `pymongo>=4.0.0` - MongoDB for persistence
- `gspread>=5.12.0` - Google Sheets integration
- `pandas>=2.0.0` - Data processing
- `reportlab>=4.0.0` - PDF generation
- `pytest` - Testing framework

### Adding New Dependencies
- Add to appropriate `requirements*.txt` file
- Pin major versions (e.g., `>=1.0.0`)
- Update all environment-specific requirement files if needed

## 🔍 Code Search and Navigation

### Finding Components
```bash
# Find quotation-related code
grep -r "calculate.*quote" --include="*.py"

# Find test files for a module
find . -name "test_*calculator*.py"

# Search for Decimal usage
grep -r "from decimal import" --include="*.py"
```

## 🎯 BMC Business Logic

### Core Principles
1. **BMC Uruguay does NOT manufacture** - they supply/commercialize products
2. **Value proposition**: "Optimized technical solutions for comfort, budget savings, structure optimization, reduced construction time, and future problem prevention"
3. **LLM NEVER calculates** - only extracts parameters, all arithmetic in deterministic functions

### Product Families
- **ISOPANEL**: EPS insulated panels
- **ISODEC**: Deck/roof panels  
- **ISOROOF**: Roof-specific panels
- **ISOWALL**: Wall panels
- **HM_RUBBER**: EPDM waterproofing membrane
- **Accessories**: Profiles, fasteners, sealants, finishes

### Technical Terms (Spanish)
- `autoportancia` - self-supporting span
- `canalón` - gutter (note: no accent in catalog)
- `solape` - overlap
- `desperdicio` - waste/scrap
- `fijación` - fastening/fixing
- `terminación` - finishing/trim

## 🚀 Development Workflow

### Before Making Changes
1. Understand the knowledge base hierarchy
2. Check existing tests for the module
3. Review related documentation in `/docs/` or markdown files
4. Check CODEOWNERS for sensitive files

### Making Changes
1. Write or update tests FIRST (TDD approach)
2. Implement minimal changes to pass tests
3. Use `Decimal` for all financial calculations
4. Run tests locally before committing
5. Update documentation if changing APIs or behavior

### Commit Messages
- Use clear, descriptive messages
- Reference issue numbers when applicable
- Use imperative mood ("Add feature" not "Added feature")

## 📚 Documentation

### Key Documentation Files
- `PANELIN_KNOWLEDGE_BASE_GUIDE.md` - Knowledge base structure and usage
- `PANELIN_INSTRUCTIONS_FINAL.txt` - GPT system instructions
- `SECURITY.md` - Security policy and vulnerability reporting
- `KNOWLEDGE_ANALYSIS_PLAN_MERGED.md` - Knowledge analysis and planning

### Updating Documentation
- Update markdown docs when changing APIs
- Keep knowledge base guide in sync with JSON structure changes
- Document business logic changes in relevant guides

## ⚡ Performance Considerations

### Large Files
- Knowledge base JSON files can be large (>1MB)
- Use lazy loading for knowledge bases
- Cache loaded data when appropriate
- Consider pagination for large catalog displays

### Calculation Performance
- Decimal arithmetic is slower than float but necessary for precision
- Cache repeated calculations when safe to do so
- Use efficient data structures for lookup tables

## 🧩 Multi-Agent Architecture

This repository uses specialized agents for different tasks:
- Quotation agents (GPT-based calculation parameter extraction)
- Analysis agents (knowledge base analysis)
- Training agents (KB optimization and training)
- Ingestion agents (social media and data ingestion)

When working with agents:
- Keep agent prompts in separate configuration files
- Use dependency injection for testability
- Log agent interactions for debugging
- Maintain clear boundaries between agent responsibilities

## 🔄 Continuous Integration

### GitHub Actions
- `.github/workflows/tests.yml` - Automated test execution
- `.github/workflows/auto-approve.yml` - PR auto-approval workflow

### Running CI Locally
```bash
# Replicate CI test run
python3 -m pytest tests/ -v --tb=short
```

## 💡 Tips for Contributors

1. **Read the Knowledge Base Guide first**: Understanding the KB hierarchy is crucial
2. **Use Decimal everywhere for money**: Float precision errors are unacceptable in financial calculations
3. **Respect the calculator variants**: Know which calculator variant to use for your use case
4. **Test with real data**: Use actual product specs from knowledge base in tests
5. **Spanish technical terms**: Preserve Spanish terminology for domain-specific concepts
6. **Security first**: Never commit credentials or sensitive business data
7. **Minimal changes**: Make surgical, targeted changes rather than broad refactors

## 📞 Getting Help

- Check existing documentation in markdown files
- Review test files for usage examples
- Consult `PANELIN_KNOWLEDGE_BASE_GUIDE.md` for KB questions
- Review `SECURITY.md` for security concerns
- See CODEOWNERS for component ownership

---

**Last Updated**: 2026-02-08  
**Maintained by**: @matiasportugau-ui
