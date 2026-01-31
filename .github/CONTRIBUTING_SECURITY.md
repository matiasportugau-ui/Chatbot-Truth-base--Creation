# 🤝 Contributing to Panelin - Security Guidelines

## Welcome Contributors!

Thank you for your interest in contributing to Panelin! This guide outlines security best practices to follow when contributing to the project.

---

## Table of Contents

1. [Before You Start](#before-you-start)
2. [Security Requirements](#security-requirements)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Pull Request Process](#pull-request-process)
6. [Security Checklist](#security-checklist)

---

## Before You Start

### Read the Documentation

- **SECURITY.md**: Our security policy and vulnerability reporting
- **SECRETS_MANAGEMENT.md**: How to handle API keys and secrets
- **README.md**: Project overview and setup instructions

### Required Skills

- Basic understanding of Python and/or JavaScript/TypeScript
- Familiarity with Git and GitHub workflows
- Understanding of API security best practices
- Knowledge of environment variables and secrets management

---

## Security Requirements

### ✅ Must-Follow Security Rules

1. **Never commit secrets**
   - No API keys, passwords, tokens in code
   - Use environment variables instead
   - Verify `.env` is in `.gitignore`

2. **Keep dependencies secure**
   - Use exact versions in requirements (avoid `>=` where possible for security)
   - Run security scans before submitting PR
   - Check for known vulnerabilities

3. **Follow secure coding practices**
   - Validate all user inputs
   - Use parameterized queries (prevent SQL injection)
   - Sanitize data before logging
   - Implement proper error handling

4. **Enable 2FA on your GitHub account**
   - Required for all contributors
   - Protects your account and the project

### ❌ Security Anti-Patterns to Avoid

```python
# ❌ BAD: Hardcoded API key
api_key = "sk-proj-abc123..."

# ❌ BAD: Logging sensitive data
logger.info(f"User password: {password}")

# ❌ BAD: SQL injection risk
query = f"SELECT * FROM users WHERE id = {user_id}"

# ❌ BAD: Insecure file access
with open(user_provided_path, 'r') as f:
    data = f.read()
```

```python
# ✅ GOOD: Environment variable
api_key = os.getenv("OPENAI_API_KEY")

# ✅ GOOD: Safe logging
logger.info(f"User authenticated: {user_id}")

# ✅ GOOD: Parameterized query
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))

# ✅ GOOD: Path validation
if not os.path.abspath(path).startswith(allowed_dir):
    raise ValueError("Invalid path")
```

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/Chatbot-Truth-base--Creation.git
cd Chatbot-Truth-base--Creation
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your development API keys
# IMPORTANT: Use development/test keys, not production keys!
nano .env

# Verify .env is not tracked
git status | grep ".env" && echo "WARNING!" || echo "OK"
```

### 3. Install Dependencies

```bash
# Python dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Node.js dependencies (if working on TypeScript SDK)
npm install
```

### 4. Run Security Checks

```bash
# Run security scans locally
bandit -r . -f txt
safety check
pip-audit
```

### 5. Set Up Pre-commit Hooks (Optional but Recommended)

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install
```

---

## Making Changes

### Branch Naming

Use descriptive branch names:
```
feature/add-user-authentication
fix/sql-injection-vulnerability
security/update-openai-dependency
docs/improve-security-guide
```

### Commit Messages

Follow conventional commit format:
```
feat: add input validation for user queries
fix: prevent SQL injection in search endpoint
security: update dependencies with known vulnerabilities
docs: improve secrets management guide
```

### Code Review Checklist (Self-Review)

Before submitting a PR, review your own code:

```markdown
- [ ] No secrets or API keys committed
- [ ] All new dependencies are necessary and vetted
- [ ] Input validation implemented for all user inputs
- [ ] Error messages don't expose sensitive information
- [ ] Logging doesn't include PII or secrets
- [ ] Tests added or updated for new functionality
- [ ] Documentation updated if needed
- [ ] Security scan passes (bandit, safety, pip-audit)
- [ ] No new security warnings in code editor
```

---

## Pull Request Process

### 1. Keep PRs Focused

- One feature or fix per PR
- Keep changes minimal and reviewable
- Large refactors should be discussed in an issue first

### 2. Write a Good Description

```markdown
## Description
Brief summary of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Security fix
- [ ] Documentation update

## Testing
Describe how you tested your changes.

## Security Considerations
- [ ] No new secrets or credentials added
- [ ] Input validation implemented
- [ ] No new security warnings
- [ ] Dependencies checked for vulnerabilities
- [ ] Follows least privilege principle

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where needed
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally
```

### 3. Required Checks

All PRs must pass:
- ✅ **CodeQL Analysis** - Security scanning
- ✅ **Python Security Scan** - Bandit, Safety, pip-audit
- ✅ **Pytest Tests** - Unit tests
- ✅ **Code Review** - At least 1 approval from maintainer

### 4. Respond to Reviews

- Be responsive to reviewer comments
- Ask questions if feedback is unclear
- Make requested changes promptly
- Re-request review after making changes

### 5. Merge Requirements

- All status checks must pass
- At least 1 approval from code owner
- All conversations must be resolved
- Branch must be up-to-date with base branch

---

## Security Checklist

### For Every Contribution

```markdown
**Before Committing:**
- [ ] I have not committed any secrets, API keys, or passwords
- [ ] I have not committed any `.env` file
- [ ] I have not hardcoded any sensitive values
- [ ] I checked that my changes don't introduce security vulnerabilities

**Before Submitting PR:**
- [ ] I ran local security scans (bandit, safety, pip-audit)
- [ ] I checked for vulnerable dependencies
- [ ] I validated all user inputs in my code
- [ ] I sanitized any data that gets logged
- [ ] I followed secure coding practices
- [ ] I updated documentation if I changed any security-related code

**Before Merging:**
- [ ] All CI checks pass
- [ ] Code review approved
- [ ] No new security alerts introduced
- [ ] Documentation is up to date
```

### For Security-Related Changes

If your PR touches security-sensitive code:

```markdown
- [ ] I consulted SECURITY.md before making changes
- [ ] I discussed the approach in an issue or discussion
- [ ] I considered the security implications thoroughly
- [ ] I added extra tests for security edge cases
- [ ] I updated security documentation
- [ ] I requested review from security team member
```

---

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. **DO** follow the process in [SECURITY.md](../SECURITY.md)
3. Use GitHub Security Advisories for private reporting
4. We'll work with you to fix it before public disclosure

---

## Getting Help

### Questions?

- **General questions**: Open a GitHub Discussion
- **Bug reports**: Open a GitHub Issue
- **Security concerns**: Follow [SECURITY.md](../SECURITY.md)

### Resources

- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OpenAI Safety Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)

---

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the project
- Show empathy towards other contributors

### Security-Specific Standards

- Never publicly disclose security vulnerabilities
- Respect responsible disclosure timelines
- Don't abuse your access to security information
- Report security issues you discover

---

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

**Thank you for helping make Panelin more secure!** 🔒

For questions about these guidelines, please open a discussion or contact the maintainers.

**Last Updated:** 2026-01-31  
**Maintainer:** @matiasportugau-ui
