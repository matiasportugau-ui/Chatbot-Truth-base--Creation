# Security Policy

## 🔒 Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 6.x     | :white_check_mark: |
| 5.x     | :white_check_mark: |
| < 5.0   | :x:                |

## 🚨 Reporting a Vulnerability

We take the security of our chatbot system seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please DO NOT:
- Open a public GitHub issue
- Disclose the vulnerability publicly before we've had a chance to address it
- Exploit the vulnerability beyond what is necessary to demonstrate it

### Please DO:
1. **Email us**: Send details to **security@panelin-project.example.com** (or create a private security advisory on GitHub)
2. **Use GitHub Security Advisories** (Preferred):
   - Go to repository → **Security** tab → **Advisories** → **New draft security advisory**
   - Fill in vulnerability details
   - This allows private discussion before public disclosure
3. **Include**:
   - Type of vulnerability
   - Full paths of source file(s) related to the vulnerability
   - Location of the affected source code (tag/branch/commit or URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the vulnerability
   - How you think it should be fixed (optional)

### What to Expect:
- **Initial Response**: Within 48 hours
- **Status Update**: Within 5 business days
- **Resolution Timeline**: Depends on severity
  - Critical: 7 days
  - High: 14 days
  - Medium: 30 days
  - Low: 60 days

## 🛡️ Security Best Practices

### For Contributors
- Never commit API keys, passwords, tokens, or secrets
- Always use environment variables for sensitive configuration
- Keep dependencies up to date
- Review code for security issues before submitting PRs
- Use `.env.example` as a template, never commit actual `.env`
- Run security scans locally before pushing

### For Deployment
- **API Keys**: Rotate regularly (every 90 days minimum)
- **Environments**: Use separate keys for dev/staging/production
- **Authentication**: Enable MFA on all service accounts
- **Monitoring**: Track API usage for anomalies
- **Access**: Follow principle of least privilege
- **Encryption**: Use TLS/SSL for all API communications

### Sensitive Data Handling
This system processes:
- Customer quotations and pricing data
- Business catalog information
- Conversation histories
- Internal knowledge bases

**Requirements:**
- Do not log sensitive customer information
- Sanitize all user inputs
- Implement rate limiting
- Use secure database connections
- Encrypt data at rest when possible

## 🔍 Security Features

### Automated Scanning
- **CodeQL**: Analyzes code for security vulnerabilities
- **Dependabot**: Monitors dependencies for known vulnerabilities
- **Secret Scanning**: Detects accidentally committed secrets
- **Security Workflow**: Daily scans with Bandit, Safety, and pip-audit

### Branch Protection
- Required PR reviews before merging
- Status checks must pass
- Conversation resolution required
- Up-to-date branches enforced

### Monitoring
- Dependency vulnerability alerts
- Security advisory notifications
- Audit logs for repository access

## 📋 Security Checklist for Deployments

- [ ] All API keys stored in environment variables or secrets manager
- [ ] `.env` file is in `.gitignore` and never committed
- [ ] Dependencies are up to date
- [ ] Security scan passes (no high/critical issues)
- [ ] Rate limiting is configured
- [ ] Input validation is implemented
- [ ] Error messages don't leak sensitive information
- [ ] Logging excludes PII and secrets
- [ ] HTTPS/TLS is enforced
- [ ] Database connections are secured

## 📚 Additional Resources

- [OpenAI Security Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Features](https://docs.github.com/en/code-security)

## 🔄 Updates to This Policy

This security policy may be updated from time to time. We will notify contributors of significant changes via:
- GitHub repository notifications
- Pull request comments for major security updates
- Issue tracking for policy changes

**Last Updated**: 2026-01-31

---

## 📖 Additional Security Documentation

For more detailed information, see:
- [Secrets Management Guide](.github/SECRETS_MANAGEMENT.md) - How to manage API keys and environment variables
- [Branch Protection Setup](.github/BRANCH_PROTECTION_SETUP.md) - Repository security configuration
- [Contributing Guidelines](CONTRIBUTING.md) - Development and contribution practices (if available)

## 🔗 Related Workflows

Our automated security includes:
- **CodeQL Analysis** - Weekly security scanning for Python and JavaScript
- **Security Scan** - Daily scans with Bandit, Safety, and pip-audit
- **Dependabot** - Automated dependency updates
- **Secret Scanning** - Continuous monitoring for exposed secrets