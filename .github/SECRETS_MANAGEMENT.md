# 🔐 Secrets and Environment Variables Management Guide

## Overview

This guide provides comprehensive instructions for managing secrets, API keys, and environment variables securely in the Panelin project.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Variables](#environment-variables)
3. [GitHub Actions Secrets](#github-actions-secrets)
4. [Secret Rotation Policy](#secret-rotation-policy)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Local Development Setup

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Fill in your actual values:**
   - Open `.env` in a secure editor
   - Replace placeholder values with your actual API keys
   - **Never commit this file to version control**

3. **Verify .gitignore:**
   ```bash
   # Ensure .env is listed in .gitignore
   grep "^\.env$" .gitignore
   ```

4. **Set appropriate file permissions (Unix/Linux/macOS):**
   ```bash
   chmod 600 .env
   ```

### Verify Setup

```bash
# Check that .env exists and is not tracked
git status | grep -q ".env" && echo "WARNING: .env is tracked!" || echo "OK: .env is not tracked"
```

---

## Environment Variables

### Required Variables

| Variable | Description | Where to Get | Security Level |
|----------|-------------|--------------|----------------|
| `OPENAI_API_KEY` | OpenAI API key | [OpenAI Platform](https://platform.openai.com/api-keys) | **CRITICAL** |
| `MONGODB_CONNECTION_STRING` | MongoDB connection | MongoDB Atlas or self-hosted | **HIGH** |

### Optional Variables

| Variable | Description | Default | Security Level |
|----------|-------------|---------|----------------|
| `ANTHROPIC_API_KEY` | Claude API key | None | **HIGH** |
| `GOOGLE_API_KEY` | Gemini API key | None | **HIGH** |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Facebook integration | None | **HIGH** |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram integration | None | **HIGH** |
| `MERCADOLIBRE_ACCESS_TOKEN` | MercadoLibre integration | None | **HIGH** |

### Configuration Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ENVIRONMENT` | Runtime environment | `development` | `production` |
| `DEBUG` | Debug mode | `false` | `true` |
| `LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG` |
| `PROJECT_ROOT` | Project root path | `.` | `/app` |
| `KB_PATH` | Knowledge base path | `Files` | `knowledge_base` |

---

## GitHub Actions Secrets

### Setting Up Secrets

1. **Navigate to Repository Settings:**
   - Go to your GitHub repository
   - Click **Settings** → **Secrets and variables** → **Actions**

2. **Add Required Secrets:**

   Click **New repository secret** for each:

   | Secret Name | Description | Required For |
   |-------------|-------------|--------------|
   | `OPENAI_API_KEY` | OpenAI API key | AI features, testing |
   | `MONGODB_CONNECTION_STRING` | MongoDB connection | Integration tests |
   | `GOOGLE_SHEETS_CREDENTIALS` | Service account JSON | Sheets integration |

3. **Environment-Specific Secrets:**

   For production deployments, use GitHub Environments:
   - **Settings** → **Environments** → **New environment**
   - Create `production`, `staging`, `development`
   - Add environment-specific secrets

### Using Secrets in Workflows

```yaml
name: Example Workflow

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Use secret
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          # Secret is available as environment variable
          python script.py
```

### Secret Scanning Protection

GitHub automatically scans for exposed secrets. If detected:
1. **Immediate notification** to repository admins
2. **Push may be blocked** if push protection is enabled
3. **Alert created** in Security tab

**Enable push protection:**
- Settings → Code security and analysis → Secret scanning
- Enable **Push protection**

---

## Secret Rotation Policy

### Rotation Schedule

| Secret Type | Rotation Frequency | Priority |
|-------------|-------------------|----------|
| **OpenAI API Keys** | Every 90 days | **CRITICAL** |
| **Database Credentials** | Every 90 days | **CRITICAL** |
| **OAuth Tokens** | Every 60 days | **HIGH** |
| **Service Account Keys** | Every 180 days | **MEDIUM** |

### Rotation Process

1. **Generate new secret** in the service provider
2. **Update GitHub Actions secrets** (if applicable)
3. **Update local .env files** (notify team)
4. **Test with new secret** in staging environment
5. **Deploy to production**
6. **Revoke old secret** after 24-48 hours
7. **Document rotation** in security log

### Emergency Rotation

If a secret is compromised:
1. **Immediately revoke** the exposed secret
2. **Generate replacement** secret
3. **Update all locations** (GitHub, local, deployments)
4. **Review access logs** for unauthorized usage
5. **Report incident** to security team
6. **Update security log**

---

## Security Best Practices

### DO ✅

- ✅ **Always use `.env` files** for local development
- ✅ **Use GitHub Secrets** for CI/CD
- ✅ **Rotate secrets regularly** (follow schedule above)
- ✅ **Use environment-specific secrets** (dev/staging/prod)
- ✅ **Limit secret scope** (minimal required permissions)
- ✅ **Monitor secret usage** through service provider dashboards
- ✅ **Use secret scanning tools** (TruffleHog, GitGuardian)
- ✅ **Enable MFA** on all service accounts
- ✅ **Document secret ownership** (who manages what)
- ✅ **Audit secret access** regularly

### DON'T ❌

- ❌ **Never commit `.env` files** to version control
- ❌ **Never hardcode secrets** in source code
- ❌ **Never log secrets** (even in debug mode)
- ❌ **Never share secrets** via email or chat
- ❌ **Never use production secrets** in development
- ❌ **Never commit credentials** to public repositories
- ❌ **Never reuse secrets** across projects
- ❌ **Never store secrets in plain text** files tracked by git

### Code Examples

**❌ BAD - Hardcoded secret:**
```python
api_key = "sk-proj-abc123..."  # NEVER DO THIS
```

**✅ GOOD - Environment variable:**
```python
import os
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set")
```

**❌ BAD - Logging secrets:**
```python
logger.debug(f"Using API key: {api_key}")  # NEVER LOG SECRETS
```

**✅ GOOD - Safe logging:**
```python
logger.debug(f"API key configured: {'Yes' if api_key else 'No'}")
```

---

## Troubleshooting

### Common Issues

#### Issue: "API key not found"

**Solution:**
```bash
# Verify .env file exists
ls -la .env

# Check .env is loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

#### Issue: "Permission denied reading .env"

**Solution:**
```bash
# Fix file permissions
chmod 600 .env
```

#### Issue: ".env file is tracked by git"

**Solution:**
```bash
# Remove from tracking (keeps local file)
git rm --cached .env

# Verify it's in .gitignore
echo ".env" >> .gitignore

# Commit the change
git commit -m "Remove .env from tracking"
```

#### Issue: "GitHub Actions can't access secrets"

**Solution:**
1. Verify secret exists: Settings → Secrets → Actions
2. Check secret name matches exactly (case-sensitive)
3. Ensure workflow has correct permissions
4. For organization repos, check organization-level secrets

### Getting Help

- **Security Issues:** See [SECURITY.md](SECURITY.md)
- **General Support:** Open an issue with label `question`
- **Urgent Security Matter:** Email security contact in SECURITY.md

---

## Additional Resources

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [OpenAI API Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [12-Factor App Config](https://12factor.net/config)

---

**Last Updated:** 2026-01-31  
**Maintainer:** @matiasportugau-ui
