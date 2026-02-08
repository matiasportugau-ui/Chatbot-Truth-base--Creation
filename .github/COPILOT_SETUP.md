# GitHub Copilot Setup

This repository is configured to work with [GitHub Copilot coding agent](https://docs.github.com/en/copilot/tutorials/coding-agent) for AI-assisted development.

## 📋 What is Configured

This repository has Copilot instructions that help the AI coding agent understand:
- Project structure and components
- Coding standards and best practices
- Testing requirements
- Security boundaries
- Domain-specific terminology and business logic

## 📍 Location

Copilot instructions are stored in:
- **`.github/copilot-instructions.md`** - Main instructions file

This follows [GitHub's recommended location](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results) for repository-specific Copilot instructions.

## 🎯 What the Instructions Cover

### 1. **Quick Start & Setup**
- Python version requirements (3.10+)
- Installation steps
- Environment variables
- Build and test commands

### 2. **Coding Standards**
- **Critical**: Use `Decimal` for all financial calculations (never `float`)
- PEP 8 style guidelines
- Type hints and docstrings
- Error handling patterns

### 3. **Repository Structure**
- Key components and directories
- Calculator variants (`panelin.tools` vs `panelin_core`)
- Knowledge base hierarchy (4 levels)
- Testing structure

### 4. **Domain Knowledge**
- BMC Uruguay business context
- Panel types and technical terms
- Spanish terminology preservation
- Self-supporting span validation (`autoportancia`)

### 5. **Multi-Agent Task Distribution**
- Copilot vs Claude role assignment
- Task-specific responsibilities (code, reasoning, analysis)
- RAG configuration reference parameters
- Shared responsibilities matrix

### 6. **Development Workflow**
- Git branch naming conventions
- PR requirements and review process
- Test-driven development approach
- CODEOWNERS for sensitive files

### 7. **Troubleshooting**
- Common Decimal precision errors
- Knowledge base loading issues
- Calculator choice guidance
- Google Sheets authentication

## 🚀 Using Copilot with This Repository

When working with GitHub Copilot in this repository:

1. **Copilot will automatically read** `.github/copilot-instructions.md`
2. **Follow the coding standards** outlined in the instructions
3. **Use the examples** provided for common patterns
4. **Respect the boundaries** defined in CODEOWNERS

## 🔧 For Contributors

When contributing to this repository:

- Review `.github/copilot-instructions.md` before making changes
- Follow the coding standards for financial calculations (Decimal)
- Use the appropriate calculator variant for your use case
- Add tests following the existing patterns
- Preserve Spanish technical terminology

## 📚 Additional Resources

- [GitHub Copilot Best Practices](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results)
- [How to Write Great Agents Instructions](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/)
- Repository-specific: `PANELIN_KNOWLEDGE_BASE_GUIDE.md`
- Security policy: `SECURITY.md`

## 📝 Maintaining These Instructions

The Copilot instructions should be kept up-to-date when:
- Major architectural changes occur
- New coding standards are adopted
- Dependencies are significantly updated
- New domain concepts are introduced

**Last Updated**: 2026-02-08  
**Maintained by**: @matiasportugau-ui
