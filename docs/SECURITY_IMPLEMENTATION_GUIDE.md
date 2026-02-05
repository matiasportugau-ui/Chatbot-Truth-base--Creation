# 🛡️ Security Implementation Guide

## Quick Start Checklist

### ✅ Automated (Already Done)
The following security measures have been automatically configured:

- ✅ Dependabot configured for Python and Node.js dependencies
- ✅ CodeQL security scanning enabled (weekly + on PR)
- ✅ Security scan workflow (Bandit, Safety, pip-audit)
- ✅ Enhanced `.gitignore` with security patterns
- ✅ `SECURITY.md` policy created
- ✅ `CODEOWNERS` configured for critical files

### 🚨 Manual Actions Required (Priority 1)

#### 1. Remove Committed Secrets
```bash
# Check if .env has real secrets
cat .env

# If yes, rotate ALL keys immediately, then:
git rm --cached .env
git commit -m "security: Remove .env from version control"
git push
```

#### 2. Enable GitHub Security Features
Go to: `https://github.com/matiasportugau-ui/Chatbot-Truth-base--Creation/settings/security_analysis`

Enable:
- ✅ Dependency graph
- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ Secret scanning
- ✅ **Push protection** (CRITICAL)

#### 3. Configure Branch Protection
Go to: `Settings → Branches → Add branch protection rule`

For branch: `main`
- ✅ Require a pull request before merging
  - Require approvals: 1
  - Dismiss stale reviews
- ✅ Require status checks to pass
  - CodeQL
  - Security Scan
- ✅ Require conversation resolution
- ✅ Include administrators
- ✅ Restrict pushes (optional but recommended)

#### 4. Add GitHub Secrets
Go to: `Settings → Secrets and variables → Actions → New repository secret`

Add these secrets:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
MONGODB_URI=mongodb+srv://...
```

#### 5. Enable 2FA
1. Go to GitHub account settings
2. Enable Two-Factor Authentication
3. Save backup codes securely

---

## 🔍 Security Workflows Explained

### Daily Security Scan
**File**: `.github/workflows/security-scan.yml`
**Runs**: Daily at 2 AM + on push/PR

**Tools**:
- **Bandit**: Finds common Python security issues
- **Safety**: Checks dependencies for known vulnerabilities
- **pip-audit**: Audits Python packages for CVEs

**Reports**: Available as workflow artifacts

### CodeQL Analysis
**File**: `.github/workflows/codeql.yml`
**Runs**: Weekly + on push/PR

**Languages**: Python, JavaScript/TypeScript
**Detects**: SQL injection, XSS, path traversal, etc.

---

## 🔐 Environment Variables Setup

### Development
Create `.env` locally (NEVER commit):
```bash
# AI API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Database
MONGODB_URI=mongodb://localhost:27017/...

# Application
DEBUG=True
ENVIRONMENT=development
```

### Production
Use GitHub Secrets or your cloud provider's secret manager.

**Example with GitHub Actions**:
```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  ENVIRONMENT: production
```

---

## 🛠️ Developer Workflow

### Before Committing
```bash
# 1. Check for secrets
git diff | grep -E "(api[_-]?key|password|secret|token)" -i

# 2. Run security scan locally
pip install bandit safety pip-audit
bandit -r . -ll
safety check
pip-audit

# 3. Check gitignore is working
git status  # .env should not appear
```

### Pre-commit Hook (Optional)
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Check for potential secrets
if git diff --cached | grep -E "(api[_-]?key|password|secret|token)" -i; then
    echo "⚠️  WARNING: Potential secret detected!"
    echo "Review changes carefully before committing."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## 📊 Monitoring Security

### Check Security Status
```bash
# View Dependabot alerts
gh api /repos/matiasportugau-ui/Chatbot-Truth-base--Creation/dependabot/alerts

# View secret scanning alerts
gh api /repos/matiasportugau-ui/Chatbot-Truth-base--Creation/secret-scanning/alerts
```

### Review Workflow Results
1. Go to `Actions` tab
2. Check `Security Scan` workflow
3. Download artifacts for detailed reports

### Security Dashboard
GitHub provides a security overview:
`https://github.com/matiasportugau-ui/Chatbot-Truth-base--Creation/security`

---

## 🚀 Deployment Security

### Pre-deployment Checklist
- [ ] All tests passing
- [ ] Security scans passing (no high/critical)
- [ ] Dependencies up to date
- [ ] Environment variables configured
- [ ] Secrets rotated (if needed)
- [ ] Rate limiting configured
- [ ] Logging configured (no PII)

### Post-deployment
- [ ] Monitor error logs
- [ ] Check API usage patterns
- [ ] Verify security headers
- [ ] Test authentication flows

---

## 🔄 Maintenance Schedule

### Weekly
- Review Dependabot PRs
- Check security scan results

### Monthly
- Review access logs
- Update dependencies
- Check for new security advisories

### Quarterly
- Rotate API keys
- Security audit
- Review and update SECURITY.md
- Test disaster recovery

---

## 🆘 Incident Response

### If Secret is Exposed
1. **Immediately** rotate the exposed credential
2. Review access logs for unauthorized usage
3. Notify affected services
4. Remove from git history: `git filter-repo` or BFG Repo-Cleaner
5. Document incident

### If Vulnerability Found
1. Assess severity (use CVSS score)
2. Check if actively exploited
3. Develop patch
4. Test thoroughly
5. Deploy fix
6. Notify users (if needed)

---

## 📚 Additional Resources

- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

## 🤝 Questions?

Review `SECURITY.md` or open a discussion (not an issue) for security questions.

**Last Updated**: 2026-01-31