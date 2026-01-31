# Security Cleanup and Remediation Guide

## ⚠️ Immediate Actions Required

### 1. Remove Sensitive Files from Git History

If `.env` files or other sensitive files were committed to the repository, they must be removed from the entire git history.

#### Option A: Using BFG Repo-Cleaner (Recommended)

```bash
# Install BFG
# On macOS: brew install bfg
# On Linux: Download from https://rephrase.net/box/bfg/

# Clone a fresh copy of the repo
git clone --mirror https://github.com/matiasportugau-ui/Chatbot-Truth-base--Creation.git

# Remove .env files from history
bfg --delete-files .env Chatbot-Truth-base--Creation.git

# Clean up and push
cd Chatbot-Truth-base--Creation.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

#### Option B: Using git-filter-repo (Alternative)

```bash
# Install git-filter-repo
pip install git-filter-repo

# Clone a fresh copy
git clone https://github.com/matiasportugau-ui/Chatbot-Truth-base--Creation.git
cd Chatbot-Truth-base--Creation

# Remove .env files from history
git filter-repo --path .env --invert-paths --force

# Push changes
git push --force --all
```

#### Option C: Using git filter-branch (Manual Method)

```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force --all
```

### 2. Rotate All Exposed API Keys

**CRITICAL**: Any API keys that were committed must be considered compromised and should be rotated immediately.

#### Services to Rotate:

1. **OpenAI API Keys**
   - Go to: https://platform.openai.com/api-keys
   - Delete old key
   - Generate new key
   - Update in GitHub Secrets and local `.env`

2. **Anthropic API Keys** (if used)
   - Go to: https://console.anthropic.com/settings/keys
   - Revoke old key
   - Create new key
   - Update securely

3. **Google/Gemini API Keys** (if used)
   - Go to: https://console.cloud.google.com/apis/credentials
   - Delete compromised credentials
   - Create new credentials
   - Update in secure locations

4. **Facebook/Instagram API Tokens**
   - Go to Facebook Developer Console
   - Regenerate Page Access Token
   - Update App Secret if exposed
   - Update in GitHub Secrets

5. **MercadoLibre Access Tokens**
   - Revoke and regenerate access tokens
   - Update in GitHub Secrets

6. **MongoDB Connection Strings**
   - If exposed, change database passwords
   - Update connection string in GitHub Secrets

7. **Google Sheets Service Account**
   - Generate new service account credentials
   - Delete old credentials file
   - Update in secure storage

### 3. Verify .gitignore is Working

After cleanup, verify sensitive files are properly ignored:

```bash
# Check git status - should show no sensitive files
git status

# Try to add .env - should be ignored
touch .env
echo "TEST_KEY=test" > .env
git add .env
# Should get: "The following paths are ignored by one of your .gitignore files"

# Clean up test
rm .env
```

### 4. Enable GitHub Security Features

#### Enable Secret Scanning
1. Go to: Repository Settings → Security & analysis
2. Enable "Secret scanning"
3. Enable "Push protection" (prevents accidental commits of secrets)

#### Enable Dependabot Alerts
1. Go to: Repository Settings → Security & analysis
2. Enable "Dependabot alerts"
3. Enable "Dependabot security updates"

#### Enable Code Scanning
1. Go to: Repository Settings → Security & analysis
2. Enable "Code scanning"
3. Set up CodeQL analysis (use the workflow in `.github/workflows/codeql.yml`)

### 5. Enforce Two-Factor Authentication (2FA)

**Organization Owners/Admins:**

1. Go to: Organization Settings → Authentication security
2. Enable "Require two-factor authentication for everyone in the organization"
3. Set a grace period (e.g., 1 week) for members to enable 2FA
4. Notify all members to set up 2FA before the deadline

**Individual Contributors:**

1. Go to: Personal Settings → Password and authentication
2. Enable two-factor authentication
3. Save recovery codes securely
4. Consider using an authenticator app (Google Authenticator, Authy, etc.)

### 6. Set Up GitHub Secrets

Add the following secrets to: Repository Settings → Secrets and variables → Actions

Required secrets:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY` (optional)
- `GOOGLE_API_KEY` (optional)
- `MONGODB_CONNECTION_STRING`
- `FACEBOOK_PAGE_ACCESS_TOKEN` (optional)
- `INSTAGRAM_ACCESS_TOKEN` (optional)
- `MERCADOLIBRE_ACCESS_TOKEN` (optional)

### 7. API Key Rotation Schedule

Establish a regular rotation schedule:

| Service | Rotation Frequency | Next Rotation |
|---------|-------------------|---------------|
| OpenAI API Key | Every 90 days | [Set date] |
| Google API Keys | Every 90 days | [Set date] |
| Facebook/Instagram Tokens | Every 60 days | [Set date] |
| MongoDB Passwords | Every 180 days | [Set date] |
| Service Account Keys | Every 90 days | [Set date] |

**Set calendar reminders** for each rotation date.

### 8. Post-Cleanup Verification

After completing cleanup:

- [ ] Confirmed .env is removed from git history
- [ ] All API keys have been rotated
- [ ] New keys stored only in GitHub Secrets (and local .env for development)
- [ ] Secret scanning enabled with push protection
- [ ] Dependabot alerts enabled
- [ ] Code scanning configured
- [ ] 2FA enforced for all maintainers
- [ ] Rotation schedule calendar reminders set
- [ ] Team notified of security updates

## Additional Security Resources

- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [GitHub Dependabot](https://docs.github.com/en/code-security/dependabot)
- [Removing Sensitive Data from Git](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [OpenAI API Key Best Practices](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)

## Emergency Contact

If you discover a security incident:
1. Immediately rotate all potentially compromised credentials
2. Contact the security team: **security@[yourdomain.com]** (Update this!)
3. Document the incident and steps taken
4. Review access logs for unauthorized usage

---

**Last Updated**: 2026-01-31
**Next Review**: 2026-02-28
