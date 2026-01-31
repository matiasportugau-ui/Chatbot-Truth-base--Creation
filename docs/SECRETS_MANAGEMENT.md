# Secrets and Environment Management Guide

Complete guide for managing sensitive data, API keys, and environment variables securely.

## 🎯 Overview

This guide covers best practices for handling secrets, API keys, and environment configuration in both development and production environments.

---

## 🔑 Types of Secrets in This Project

### API Keys
- **OpenAI API Key** - Required for GPT/Assistant functionality
- **Anthropic API Key** - Optional, for Claude integration  
- **Google API Key** - Optional, for Gemini integration
- **Google Sheets Credentials** - For Google Sheets integration
- **Facebook/Instagram API** - Social media integration tokens
- **MercadoLibre API** - E-commerce platform integration

### Database Credentials
- **MongoDB Connection String** - Database access

### Configuration Values
- **Assistant IDs** - OpenAI Assistant identifiers
- **API Versions** - Service API version specifications
- **Project Paths** - File system paths for knowledge bases

---

## 🏠 Local Development Setup

### 1. Create Your `.env` File

```bash
# Copy the example file
cp .env.example .env

# Edit with your actual values
# NEVER commit this file!
```

### 2. Fill in Required Values

Edit `.env` with your actual credentials:

```bash
# --- Panelin Environment Variables ---

# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
OPENAI_ASSISTANT_ID=asst_xxxxxxxxxxxxxxxxxxxxx

# Anthropic Configuration (OPTIONAL)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx

# Google / Gemini Configuration (OPTIONAL)
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxx

# Google Sheets Integration
GOOGLE_SHEETS_CREDENTIALS=credentials/google_sheets_credentials.json

# MongoDB Configuration
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE_NAME=panelin

# Facebook API Configuration (OPTIONAL)
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_PAGE_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxx
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_API_VERSION=v18.0

# Instagram API Configuration (OPTIONAL)
INSTAGRAM_APP_ID=your_app_id
INSTAGRAM_APP_SECRET=your_app_secret
INSTAGRAM_ACCESS_TOKEN=IGQxxxxxxxxxxxxxxxxxxxxx
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id
INSTAGRAM_API_VERSION=v18.0

# MercadoLibre API Configuration (OPTIONAL)
MERCADOLIBRE_ACCESS_TOKEN=APP_USR-xxxxxxxxxxxxxxxxxxxxx
MERCADOLIBRE_USER_ID=your_user_id

# Project Paths
PROJECT_ROOT=.
KB_PATH=Files
```

### 3. Verify `.env` is Gitignored

```bash
# This should show that .env is ignored
git check-ignore .env

# Output should be: .env

# Verify git status doesn't show .env
git status

# .env should NOT appear in untracked files
```

### 4. Load Environment Variables

The project uses `python-dotenv` to automatically load `.env` files:

```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Access secrets
api_key = os.getenv('OPENAI_API_KEY')
```

---

## ☁️ Production / GitHub Actions Setup

### 1. Add Secrets to GitHub Repository

1. Navigate to: **Repository** → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add each secret individually

#### Required Secrets for GitHub Actions:

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |
| `OPENAI_ASSISTANT_ID` | Assistant ID | `asst_...` |
| `MONGODB_CONNECTION_STRING` | MongoDB URI | `mongodb://...` |

#### Optional Secrets (if used):

| Secret Name | Description |
|------------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic Claude API key |
| `GOOGLE_API_KEY` | Google/Gemini API key |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Facebook Page token |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram Business token |
| `MERCADOLIBRE_ACCESS_TOKEN` | MercadoLibre API token |

### 2. Use Secrets in GitHub Workflows

```yaml
# .github/workflows/example.yml
name: Example Workflow

on: [push]

jobs:
  example:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run script with secrets
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          MONGODB_CONNECTION_STRING: ${{ secrets.MONGODB_CONNECTION_STRING }}
        run: |
          python your_script.py
```

### 3. Environment-Specific Secrets

For multiple environments (dev, staging, production):

1. Go to: **Repository** → **Settings** → **Environments**
2. Create environments: `development`, `staging`, `production`
3. Add environment-specific secrets to each
4. Reference in workflows:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Uses production secrets
    steps:
      - name: Deploy
        env:
          API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: ./deploy.sh
```

---

## 🔒 Security Best Practices

### ✅ DO:

1. **Use environment variables for ALL secrets**
   ```python
   # ✅ Good
   api_key = os.getenv('OPENAI_API_KEY')
   
   # ❌ Bad
   api_key = 'sk-proj-abc123...'
   ```

2. **Keep `.env.example` updated** (without real values)
   ```bash
   # ✅ Good - shows structure
   OPENAI_API_KEY=your_openai_api_key_here
   
   # ❌ Bad - real secret
   OPENAI_API_KEY=sk-proj-real-key-123
   ```

3. **Use different keys for dev/staging/production**
   - Development: `sk-proj-dev-...`
   - Staging: `sk-proj-staging-...`
   - Production: `sk-proj-prod-...`

4. **Rotate secrets regularly**
   - Set calendar reminders every 90 days
   - See `docs/SECURITY_CLEANUP.md` for rotation process

5. **Validate secrets before using**
   ```python
   import os
   
   def get_required_env(key: str) -> str:
       value = os.getenv(key)
       if not value:
           raise ValueError(f"Missing required environment variable: {key}")
       return value
   
   api_key = get_required_env('OPENAI_API_KEY')
   ```

6. **Use minimal permissions**
   - Create API keys with only necessary scopes
   - Use read-only keys where possible

### ❌ DON'T:

1. **Never commit secrets to git**
   ```bash
   # ❌ Never do this
   git add .env
   git commit -m "Add config"
   ```

2. **Never log secrets**
   ```python
   # ❌ Bad
   print(f"API Key: {api_key}")
   logger.info(f"Using key: {api_key}")
   
   # ✅ Good
   logger.info("API key loaded successfully")
   ```

3. **Never hardcode secrets in code**
   ```python
   # ❌ Never do this
   OPENAI_API_KEY = "sk-proj-abc123..."
   ```

4. **Never share secrets in chat/email**
   - Use secure password managers (1Password, LastPass)
   - Use encrypted channels for key exchange

5. **Never expose secrets in error messages**
   ```python
   # ❌ Bad
   raise Exception(f"Failed to connect with key: {api_key}")
   
   # ✅ Good
   raise Exception("Failed to connect to API")
   ```

6. **Never store secrets in databases unencrypted**
   - Use encryption at rest
   - Consider using secret management services

---

## 🛠️ Secret Validation

### Pre-commit Hook to Prevent Secret Commits

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Pre-commit hook to prevent committing secrets

# Check for common secret patterns
if git diff --cached | grep -E "(sk-[a-zA-Z0-9]{20,}|AIza[a-zA-Z0-9_-]{35}|EAA[a-zA-Z0-9]+)"; then
    echo "❌ ERROR: Potential secret detected in commit!"
    echo "Please remove secrets and use environment variables instead."
    exit 1
fi

# Check if .env is being committed
if git diff --cached --name-only | grep -E "^\.env$"; then
    echo "❌ ERROR: .env file should not be committed!"
    echo "Only .env.example should be in version control."
    exit 1
fi

exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Runtime Secret Validation

```python
# validate_secrets.py
import os
import sys
from typing import List

def validate_secrets() -> bool:
    """Validate all required secrets are present."""
    
    required_secrets = [
        'OPENAI_API_KEY',
        'MONGODB_CONNECTION_STRING',
    ]
    
    optional_secrets = [
        'ANTHROPIC_API_KEY',
        'GOOGLE_API_KEY',
        'FACEBOOK_PAGE_ACCESS_TOKEN',
    ]
    
    missing_required = []
    missing_optional = []
    
    # Check required secrets
    for secret in required_secrets:
        if not os.getenv(secret):
            missing_required.append(secret)
    
    # Check optional secrets
    for secret in optional_secrets:
        if not os.getenv(secret):
            missing_optional.append(secret)
    
    # Report results
    if missing_required:
        print("❌ Missing required secrets:")
        for secret in missing_required:
            print(f"  - {secret}")
        return False
    
    if missing_optional:
        print("⚠️  Missing optional secrets (features may be limited):")
        for secret in missing_optional:
            print(f"  - {secret}")
    
    print("✅ All required secrets are configured")
    return True

if __name__ == '__main__':
    if not validate_secrets():
        sys.exit(1)
```

Use in your application:
```python
from dotenv import load_dotenv
from validate_secrets import validate_secrets

# Load and validate
load_dotenv()
if not validate_secrets():
    raise RuntimeError("Configuration error: missing required secrets")
```

---

## 📦 Alternative Secret Management Solutions

For production deployments, consider these enterprise solutions:

### 1. AWS Secrets Manager
```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']
```

### 2. Azure Key Vault
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def get_secret(vault_url, secret_name):
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    return client.get_secret(secret_name).value
```

### 3. HashiCorp Vault
```python
import hvac

def get_secret(vault_addr, vault_token, path):
    client = hvac.Client(url=vault_addr, token=vault_token)
    return client.secrets.kv.v2.read_secret_version(path=path)
```

### 4. Google Cloud Secret Manager
```python
from google.cloud import secretmanager

def get_secret(project_id, secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')
```

---

## 🔍 Auditing and Monitoring

### Track Secret Usage

```python
import logging
from functools import wraps

def track_secret_access(secret_name):
    """Decorator to log secret access."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logging.info(f"Accessing secret: {secret_name}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@track_secret_access('OPENAI_API_KEY')
def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    return OpenAI(api_key=api_key)
```

### Monitor API Key Usage

- Check provider dashboards regularly
- Set up usage alerts
- Review access logs for anomalies
- Track API call patterns

---

## 📋 Secrets Checklist

Before deploying or committing:

- [ ] All secrets in `.env` (local dev) or GitHub Secrets (CI/CD)
- [ ] No secrets hardcoded in source code
- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` is updated with new variables (no real values)
- [ ] Secrets validated before use
- [ ] Different keys for dev/staging/production
- [ ] Logging doesn't expose secrets
- [ ] Error messages don't leak secrets
- [ ] Pre-commit hooks configured
- [ ] Team members know how to access secrets securely

---

## 🆘 Emergency Procedures

### If a Secret is Accidentally Committed:

1. **Immediately rotate the compromised secret**
   - Generate a new API key
   - Update in all environments
   - Delete the old key

2. **Remove from git history**
   - See `docs/SECURITY_CLEANUP.md` for detailed instructions
   - Use BFG Repo-Cleaner or git filter-repo

3. **Verify the secret is no longer in history**
   ```bash
   git log --all --full-history --source --all -- .env
   ```

4. **Check for unauthorized usage**
   - Review provider dashboards
   - Check for suspicious API calls
   - Monitor costs/usage

5. **Document the incident**
   - What was exposed
   - When it was discovered
   - Actions taken
   - Preventive measures

---

## 📚 Additional Resources

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [OpenAI API Key Safety](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)
- [12 Factor App - Config](https://12factor.net/config)

---

**Last Updated:** 2026-01-31  
**Next Review:** 2026-02-28  
**Maintainer:** @matiasportugau-ui
