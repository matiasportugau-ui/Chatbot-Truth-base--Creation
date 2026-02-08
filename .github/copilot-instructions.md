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

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Git

### Setup
```bash
# Clone the repository
git clone https://github.com/matiasportugau-ui/Chatbot-Truth-base--Creation.git
cd Chatbot-Truth-base--Creation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt        # Core dependencies
pip install -r requirements-dev.txt    # Development dependencies (includes pytest)
```

### Environment Variables
Create a `.env` file in the root directory (use `.env.example` as template):
```bash
# Required variables
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URI=mongodb://localhost:27017/panelin
GOOGLE_CREDENTIALS_PATH=path/to/service-account.json

# Optional variables
KB_PATH=./GPT_Panelin_copilotedit/01_KNOWLEDGE_BASE/
LOG_LEVEL=INFO
```

### Build & Test
```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_quotation_calculations.py -v

# Run with coverage
python3 -m pytest tests/ --cov=panelin --cov-report=html
```

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

### Calculator Decision Matrix
| Scenario | Calculator to Use | Reason |
|----------|------------------|---------|
| Customer requests quote for custom dimensions | `panelin_core.quotation_calculator` | Prices exactly what customer requested |
| Need to enforce minimum panel lengths | `panelin.tools.quotation_calculator` | Automatically adjusts to minimum viable length |
| Showing "what you'll actually pay" | `panelin.tools.quotation_calculator` | Reflects actual material costs |
| Preliminary quote / estimation | `panelin_core.quotation_calculator` | Shows requested dimensions without adjustments |
| BOM generation with real material | `panelin.tools.quotation_calculator` | Generates accurate BOM for procurement |

### Validation Rules
- Always validate `autoportancia` (self-supporting span) using safety margins
- Check product/thickness combinations exist before quoting
- Verify minimum quantities and dimensions
- Use `validate_quotation()` to verify calculation integrity

### Expected Output Examples
**Quotation Response Structure**:
```python
{
    "quotation_id": "Q-20260208-abc123",
    "panel_type": "Isopanel",
    "thickness_mm": 50,
    "dimensions": {
        "length_m": 2.0,
        "width_m": 1.0,
        "quantity": 10
    },
    "pricing": {
        "price_per_m2": Decimal("41.88"),
        "total_area_m2": Decimal("20.0"),
        "total_usd": Decimal("837.60")
    },
    "validation": {
        "autoportancia_ok": True,
        "calculation_verified": True
    },
    "bom": [
        {"item": "Panel Isopanel 50mm", "quantity": 10, "unit": "panels"},
        {"item": "Tornillos autoperforantes", "quantity": 120, "unit": "units"}
    ],
    "warnings": []
}
```

**BOM Item Structure**:
```python
{
    "sku": "ISO-050-2M",
    "item": "Panel Isopanel 50mm x 2.0m",
    "quantity": 10,
    "unit": "panels",
    "price_usd": Decimal("83.76"),
    "category": "panel"
}
```

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

### Git Workflow and PR Process
**Branch Naming**:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions/updates

**Pull Request Requirements**:
- All tests must pass
- Code must follow PEP 8 style guidelines
- Update documentation if changing APIs or behavior
- Add tests for new functionality
- CODEOWNERS approval required for sensitive files (see `.github/CODEOWNERS`)
- No secrets or credentials in code

**Review Process**:
- PRs require approval from @matiasportugau-ui for protected files
- Automated tests run via GitHub Actions
- Address all review comments before merge
- Squash commits for cleaner history when appropriate

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

## 🔧 Troubleshooting

### Common Issues

**Decimal Precision Errors**:
```python
# ❌ Problem: Mixing float and Decimal
price = Decimal('41.88')
quantity = 10  # This is an int, which is OK
area = 2.5  # ❌ float causes precision issues
total = price * Decimal(str(area)) * quantity  # ✅ Convert float to Decimal via string

# ✅ Better: Use Decimal from the start
area = Decimal('2.5')
total = price * area * quantity
```

**Knowledge Base Loading Failures**:
- Verify KB file paths exist and are accessible
- Check JSON syntax is valid (use `python -m json.tool <file>` to validate)
- Ensure file permissions allow reading
- For large KB files, increase memory limits if needed

**Test Failures with Mock Data**:
- Use dependency injection to pass test data: `function(param, bom_rules=mock_rules)`
- Ensure mock data structure matches production KB structure
- Check that Decimal values in tests are strings: `Decimal('41.88')` not `Decimal(41.88)`

**Google Sheets Authentication**:
- Use `google.oauth2.service_account.Credentials` (not oauth2client)
- Verify service account JSON file path is correct
- Ensure service account has access to the target spreadsheet
- Check required scopes: `['https://www.googleapis.com/auth/spreadsheets']`

**Calculator Choice Issues**:
- Use `panelin.tools.quotation_calculator` for adjusted minimum length pricing
- Use `panelin_core.quotation_calculator` for requested dimension pricing
- Check `adjusted_length` vs `length_m` in results to understand which was used

## 📞 Getting Help

- Check existing documentation in markdown files
- Review test files for usage examples
- Consult `PANELIN_KNOWLEDGE_BASE_GUIDE.md` for KB questions
- Review `SECURITY.md` for security concerns
- See CODEOWNERS for component ownership

---

**Last Updated**: 2026-02-08  
**Maintained by**: @matiasportugau-ui
