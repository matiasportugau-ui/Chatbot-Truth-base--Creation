# Security Documentation

Welcome to the security documentation for the Panelin Chatbot project.

## 📚 Documentation Overview

This directory contains comprehensive security guides and best practices for maintaining a secure development and deployment environment.

### Quick Links

| Document | Purpose | Who Should Read |
|----------|---------|----------------|
| **[Security Automation Summary](SECURITY_AUTOMATION_SUMMARY.md)** | Overview of all automated security features | Everyone (start here!) |
| **[Secrets Management](SECRETS_MANAGEMENT.md)** | Guide for handling API keys and sensitive data | All developers |
| **[Secure Coding Guidelines](SECURE_CODING_GUIDELINES.md)** | Best practices for writing secure code | All developers |
| **[Branch Protection Guide](BRANCH_PROTECTION_GUIDE.md)** | How to configure branch protection rules | Repository admins |
| **[Security Monitoring](SECURITY_MONITORING.md)** | Monitoring, auditing, and incident response | Security champions, leads |
| **[Security Cleanup](SECURITY_CLEANUP.md)** | Remove secrets from git history and rotate keys | Admins (emergency use) |

### Root Level Documents

- **[../SECURITY.md](../SECURITY.md)** - Security policy, reporting vulnerabilities, supported versions
- **[../.github/CODEOWNERS](../.github/CODEOWNERS)** - Code ownership and automatic review assignments
- **[../.github/dependabot.yml](../.github/dependabot.yml)** - Dependabot configuration for automated updates

---

## 🚀 Getting Started

### For Developers

1. **Read the basics:**
   - [Security Automation Summary](SECURITY_AUTOMATION_SUMMARY.md) - Understand what's automated
   - [Secrets Management](SECRETS_MANAGEMENT.md) - Learn how to handle API keys
   - [Secure Coding Guidelines](SECURE_CODING_GUIDELINES.md) - Follow security best practices

2. **Set up your environment:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Fill in your API keys (never commit .env!)
   nano .env
   
   # Verify .env is gitignored
   git check-ignore .env  # Should output: .env
   ```

3. **Enable security notifications:**
   - Go to repository page
   - Click "Watch" → "Custom"
   - Enable "Security alerts"

### For Repository Admins

1. **Complete one-time setup:**
   - Follow [Branch Protection Guide](BRANCH_PROTECTION_GUIDE.md) to configure branch rules
   - Follow [Security Cleanup](SECURITY_CLEANUP.md) if secrets were committed
   - Add GitHub Secrets as per [Secrets Management](SECRETS_MANAGEMENT.md)

2. **Enable GitHub security features:**
   ```
   Repository Settings → Security & analysis
   ├── Enable: Secret scanning
   ├── Enable: Push protection  
   ├── Enable: Dependabot alerts
   └── Enable: Dependabot security updates
   ```

3. **Set up monitoring:**
   - Follow [Security Monitoring](SECURITY_MONITORING.md) guide
   - Schedule weekly security reviews
   - Configure alert notifications

---

## 🔒 Security Features

### Automated Security Scanning

| Feature | Schedule | Documentation |
|---------|----------|--------------|
| **CodeQL Analysis** | Weekly (Mon 6AM UTC) + on push | [codeql.yml](../.github/workflows/codeql.yml) |
| **Python Security Scan** | Weekly (Wed 3AM UTC) + on push | [security-scan.yml](../.github/workflows/security-scan.yml) |
| **Dependabot Updates** | Weekly + daily for security | [dependabot.yml](../.github/dependabot.yml) |

### Protection Mechanisms

- **.gitignore** - Prevents committing secrets
- **CODEOWNERS** - Requires review for sensitive files
- **Branch Protection** - Enforces reviews and status checks
- **Secret Scanning** - Detects accidentally committed secrets
- **Auto-Approve** - Speeds up trusted dependency updates

---

## 📋 Common Tasks

### I need to add a new API key

→ See [Secrets Management](SECRETS_MANAGEMENT.md#local-development-setup)

1. Add to `.env.example` (without real value)
2. Add to your local `.env` (with real value)
3. Add to GitHub Secrets for CI/CD

### I accidentally committed a secret

→ See [Security Cleanup](SECURITY_CLEANUP.md)

1. **Immediately** rotate the compromised key
2. Remove from git history using BFG or git-filter-repo
3. Verify removal and push changes

### I want to review security issues

→ See [Security Monitoring](SECURITY_MONITORING.md#github-security-features)

1. Go to **Security** tab in repository
2. Review **Dependabot alerts**
3. Review **Code scanning** alerts
4. Check **Secret scanning** alerts

### I need to set up branch protection

→ See [Branch Protection Guide](BRANCH_PROTECTION_GUIDE.md)

1. Go to Settings → Branches
2. Add protection rule for `main` branch
3. Enable required checks and reviews
4. Configure as per guide

### I want to write secure code

→ See [Secure Coding Guidelines](SECURE_CODING_GUIDELINES.md)

Key principles:
- Validate all user input
- Use parameterized queries
- Never hardcode secrets
- Sanitize output
- Handle errors securely

---

## 🚨 Security Incident Response

If you discover a security vulnerability:

### DO:
1. **Email:** matiasportugau@gmail.com
2. **Create:** [Private Security Advisory](https://github.com/matiasportugau-ui/Chatbot-Truth-base--Creation/security/advisories/new)
3. **Include:** Detailed description, reproduction steps, impact assessment

### DON'T:
- Don't open a public GitHub issue
- Don't disclose publicly before fix
- Don't exploit beyond demonstration

**Full details:** [../SECURITY.md](../SECURITY.md#reporting-a-vulnerability)

---

## 📊 Security Metrics

Track these metrics weekly/monthly:

- Open Dependabot alerts (Target: < 5 high/critical)
- Open CodeQL alerts (Target: 0 critical)
- Dependency freshness (Target: > 80%)
- Mean time to remediate (Target: < 7 days for high)

**Full details:** [Security Monitoring](SECURITY_MONITORING.md#security-metrics-to-track)

---

## 🔄 Regular Maintenance

### Weekly (30-60 minutes)
- Review CodeQL scan results
- Review security scan results  
- Check and merge Dependabot PRs
- Address new security alerts

### Monthly (2-3 hours)
- Comprehensive security audit
- Review user access and permissions
- Check API key rotation schedule
- Update security documentation

### Quarterly (1-2 days)
- Full dependency audit
- Security policy review
- Threat model update
- Team security training

**Full schedule:** [Security Monitoring](SECURITY_MONITORING.md#audit-schedule)

---

## 🛠️ Tools and Technologies

### Automated Security Tools

- **CodeQL** - Semantic code analysis
- **Bandit** - Python security linter
- **Safety** - Dependency vulnerability scanner
- **pip-audit** - PyPI package auditing
- **Dependabot** - Automated dependency updates

### GitHub Features

- Secret Scanning
- Code Scanning
- Dependabot Alerts
- Security Advisories
- Branch Protection
- CODEOWNERS

---

## 📖 Additional Resources

### External Documentation

- [GitHub Security Documentation](https://docs.github.com/en/code-security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OpenAI Security Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- [Python Security](https://python.readthedocs.io/en/stable/library/security_warnings.html)

### Internal Resources

- Project README: [../README.md](../README.md)
- Contributing Guidelines: (if exists)
- Code of Conduct: (if exists)

---

## ❓ FAQ

### Q: Where should I store my API keys?

**A:** Use environment variables! Add to `.env` locally, and GitHub Secrets for CI/CD. Never commit keys to git. See [Secrets Management](SECRETS_MANAGEMENT.md).

### Q: How do I know if my code is secure?

**A:** Follow [Secure Coding Guidelines](SECURE_CODING_GUIDELINES.md), run security scans locally, and automated scans will catch issues in CI/CD.

### Q: What should I do if a security scan finds issues?

**A:** Review the finding, verify it's a real issue, fix the code or update the dependency, then re-run scans to verify.

### Q: Can I bypass security checks in an emergency?

**A:** Branch protection should not allow bypassing, even for admins. In true emergencies, contact repository owner.

### Q: How often should I rotate API keys?

**A:** Every 90 days minimum. See rotation schedule in [Security Cleanup](SECURITY_CLEANUP.md#api-key-rotation-schedule).

---

## 📞 Support

**Security Issues:**
- Email: matiasportugau@gmail.com
- GitHub: [Security Advisories](https://github.com/matiasportugau-ui/Chatbot-Truth-base--Creation/security/advisories)

**General Questions:**
- Repository Owner: @matiasportugau-ui
- Documentation Issues: Open an issue or PR

---

## 🔄 Document Maintenance

**Last Updated:** 2026-01-31  
**Version:** 1.0  
**Next Review:** 2026-02-28  
**Maintainer:** @matiasportugau-ui

**To update this documentation:**
1. Make changes in `docs/` directory
2. Update "Last Updated" date
3. Create PR with "documentation" label
4. Request review from CODEOWNERS
