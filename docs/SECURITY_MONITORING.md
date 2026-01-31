# Security Monitoring and Audit Guide

Comprehensive guide for monitoring security, conducting audits, and responding to vulnerabilities.

## 🎯 Overview

This document outlines processes for continuous security monitoring, scheduled audits, and vulnerability management.

---

## 📊 GitHub Security Features

### Available Security Features

GitHub provides several built-in security features that should be enabled and monitored:

#### 1. Dependabot Alerts
**Status:** ✅ Enabled (configured in `.github/dependabot.yml`)

**What it does:**
- Scans dependencies for known vulnerabilities
- Creates alerts for vulnerable packages
- Suggests version updates

**How to access:**
1. Go to: **Repository** → **Security** → **Dependabot alerts**
2. Review alerts by severity
3. Click on alert for details and remediation

**Action items:**
- Review alerts weekly
- Prioritize Critical and High severity alerts
- Update dependencies promptly

#### 2. Secret Scanning
**Status:** ⚠️ Needs manual enablement

**How to enable:**
1. Go to: **Repository** → **Settings** → **Security & analysis**
2. Enable "Secret scanning"
3. Enable "Push protection" to prevent commits with secrets

**What it does:**
- Scans repository for exposed secrets
- Alerts when API keys, tokens, or credentials are detected
- Blocks commits with secrets (if push protection enabled)

**Monitoring:**
- Check: **Repository** → **Security** → **Secret scanning**
- Respond immediately to any alerts
- Rotate compromised credentials

#### 3. Code Scanning (CodeQL)
**Status:** ✅ Configured (see `.github/workflows/codeql.yml`)

**What it does:**
- Analyzes code for security vulnerabilities
- Runs on every push and pull request
- Scans Python and JavaScript/TypeScript code

**How to access:**
1. Go to: **Repository** → **Security** → **Code scanning**
2. Review alerts by severity and category
3. Click on alert for details and fix suggestions

**Monitoring:**
- Review new alerts after each scan
- Track resolution of existing alerts
- Verify fixes before closing

#### 4. Security Advisories
**Status:** Available for use

**How to create:**
1. Go to: **Repository** → **Security** → **Advisories**
2. Click "New draft security advisory"
3. Fill in vulnerability details
4. Publish when ready

**When to use:**
- Discovered vulnerability needs coordination
- Need to notify users privately
- Want to request CVE from GitHub

---

## 🔍 Automated Security Scanning

### Weekly Security Scans

**Configured workflows:**

1. **CodeQL Analysis** (`.github/workflows/codeql.yml`)
   - Runs: Every Monday at 6:00 AM UTC
   - Scans: Python and JavaScript/TypeScript
   - Results: Security tab → Code scanning

2. **Python Security Scanning** (`.github/workflows/security-scan.yml`)
   - Runs: Every Wednesday at 3:00 AM UTC
   - Tools: Bandit, Safety, pip-audit
   - Results: Workflow artifacts and Security tab

3. **Dependency Updates** (`.github/dependabot.yml`)
   - Runs: Weekly (configurable)
   - Creates: Pull requests for updates
   - Labels: dependencies, security

### Manual Security Scans

Trigger on-demand scans when needed:

```bash
# Navigate to repository
cd /path/to/repository

# Run Bandit (Python security linter)
bandit -r . -f json -o bandit-report.json

# Run Safety (dependency vulnerability checker)
safety check --json --output safety-report.json

# Run pip-audit (PyPI vulnerability scanner)
pip-audit --format json --output pip-audit-report.json

# Review results
cat bandit-report.json | jq
cat safety-report.json | jq
cat pip-audit-report.json | jq
```

Or trigger via GitHub Actions:

1. Go to: **Actions** → **Python Security Scanning**
2. Click "Run workflow"
3. Select branch and click "Run workflow"

---

## 📅 Audit Schedule

### Daily Monitoring (Automated)

**Automated checks:**
- [ ] Dependabot alerts reviewed (if any new alerts)
- [ ] Failed security workflows investigated
- [ ] Secret scanning alerts responded to immediately

**Responsible:** Automated + On-call team member

### Weekly Reviews (Every Monday)

**Manual review tasks:**
- [ ] Review CodeQL scan results from Monday run
- [ ] Review Python security scan from Wednesday run
- [ ] Check Dependabot pull requests
- [ ] Review and merge dependency updates
- [ ] Check for new security advisories affecting dependencies
- [ ] Review access logs (if available)

**Responsible:** Security champion or designated team member

**Time estimate:** 30-60 minutes

### Monthly Audits (First Monday of Month)

**Comprehensive audit:**
- [ ] Review all open security alerts (Dependabot, CodeQL, Secret scanning)
- [ ] Verify all dependencies are up to date
- [ ] Check for outdated or deprecated packages
- [ ] Review GitHub Security advisories for used packages
- [ ] Audit user access and permissions
- [ ] Review branch protection rules
- [ ] Verify security documentation is current
- [ ] Check API key rotation schedule
- [ ] Review and update security runbook if needed

**Responsible:** Team lead + Security champion

**Time estimate:** 2-3 hours

**Deliverable:** Monthly security report (template below)

### Quarterly Security Reviews (First Week of Quarter)

**Deep dive assessment:**
- [ ] Full dependency audit with SBOM (Software Bill of Materials)
- [ ] Penetration testing (if applicable)
- [ ] Security policy review and update
- [ ] Incident response plan review
- [ ] Training needs assessment
- [ ] Review and update threat model
- [ ] External security scan (if budget allows)
- [ ] Compliance check (if applicable)
- [ ] Update security roadmap

**Responsible:** Leadership + Security team

**Time estimate:** 1-2 days

**Deliverable:** Quarterly security assessment report

---

## 📋 Monthly Security Report Template

```markdown
# Security Report - [Month Year]

**Report Period:** [Start Date] - [End Date]
**Prepared by:** [Name]
**Date:** [Date]

## Executive Summary

[2-3 sentence overview of security posture]

## Metrics

| Metric | Count | Change from Last Month |
|--------|-------|----------------------|
| Open Dependabot Alerts | X | +/- Y |
| Open CodeQL Alerts | X | +/- Y |
| Open Secret Scanning Alerts | X | +/- Y |
| Dependencies Updated | X | +/- Y |
| Security Patches Applied | X | +/- Y |

## Critical Issues

### High Priority
1. [Issue description] - Status: [Open/In Progress/Resolved]
2. ...

### Medium Priority
1. [Issue description] - Status: [Open/In Progress/Resolved]
2. ...

## Actions Taken

1. [Action] - [Date] - [Outcome]
2. [Action] - [Date] - [Outcome]
3. ...

## Vulnerabilities Resolved

1. [CVE-XXXX-XXXXX] - [Package] - Severity: [High/Med/Low] - Fixed: [Date]
2. ...

## Upcoming Work

1. [Planned security work]
2. [Scheduled updates]
3. ...

## Recommendations

1. [Recommendation]
2. [Recommendation]
3. ...

## Appendix

- CodeQL scan results: [Link to artifact]
- Security scan results: [Link to artifact]
- Dependabot report: [Link]
```

---

## 🚨 Vulnerability Response Process

### Severity Levels and SLAs

| Severity | Description | Response Time | Resolution Time |
|----------|-------------|---------------|----------------|
| **Critical** | Remote code execution, data breach | Immediate (< 1 hour) | 24 hours |
| **High** | Authentication bypass, SQL injection | 4 hours | 7 days |
| **Medium** | XSS, CSRF, info disclosure | 24 hours | 30 days |
| **Low** | Minor issues, best practice violations | 1 week | 90 days |

### Response Workflow

#### 1. Detection
- Alert received from Dependabot, CodeQL, or security scan
- Manual discovery during audit
- External security researcher report

#### 2. Triage (Within SLA Response Time)
- Verify the vulnerability is real
- Assess actual impact on the system
- Determine severity level
- Assign to responsible team member

#### 3. Investigation
- Understand the root cause
- Identify affected components
- Determine attack surface
- Check if actively exploited

#### 4. Remediation
- Develop fix or mitigation
- Test fix in development environment
- Create pull request with fix
- Request security review
- Merge after approval

#### 5. Verification
- Verify fix resolves vulnerability
- Run security scans to confirm
- Check for regression
- Document resolution

#### 6. Communication
- Update issue/alert with resolution
- Notify stakeholders if critical
- Document in security log
- Create post-mortem if needed

#### 7. Prevention
- Update security guidelines if needed
- Add test case to prevent regression
- Share learnings with team
- Update documentation

### Example: Responding to Dependabot Alert

```bash
# 1. Receive Dependabot alert for vulnerable package
# Example: "openai 1.0.0 has a critical vulnerability"

# 2. Review alert details
# - Check severity
# - Read vulnerability description
# - Review suggested fix version

# 3. Test the update
git checkout -b security/update-openai
pip install openai==1.12.0  # Updated version
pip freeze > requirements.txt

# 4. Run tests
pytest

# 5. Run security scans
bandit -r .
safety check

# 6. If tests pass, commit and create PR
git add requirements.txt
git commit -m "security: update openai to fix CVE-XXXX-XXXXX"
git push origin security/update-openai

# 7. Create PR with security label
# 8. After review and CI passes, merge
# 9. Verify Dependabot alert is closed
```

---

## 🔔 Alert Configuration

### Email Notifications

**Enable GitHub notifications:**
1. Go to: **Profile** → **Settings** → **Notifications**
2. Under "Dependabot alerts", select "Email"
3. Under "Security alerts", select "Email"

**Configure watching:**
1. Go to repository
2. Click "Watch" → "Custom"
3. Select "Security alerts"

### Slack/Discord Integration (Optional)

Set up webhooks for security alerts:

```yaml
# .github/workflows/security-alert-notify.yml
name: Security Alert Notification

on:
  # Trigger on Dependabot alerts
  repository_vulnerability_alert:
    types: [create]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Send Slack notification
        uses: slackapi/slack-github-action@v1
        with:
          webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
          payload: |
            {
              "text": "🚨 New security alert in repository",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Security Alert*\nA new vulnerability has been detected."
                  }
                }
              ]
            }
```

---

## 📈 Security Metrics to Track

### Key Performance Indicators (KPIs)

1. **Mean Time to Detect (MTTD)**
   - Average time to discover vulnerability
   - Target: < 24 hours for critical

2. **Mean Time to Respond (MTTR)**
   - Average time to respond to alert
   - Target: Within SLA times

3. **Mean Time to Remediate (MTTR)**
   - Average time to fix vulnerability
   - Target: Within SLA resolution times

4. **Vulnerability Backlog**
   - Number of open security alerts
   - Target: < 5 open high/critical alerts

5. **Dependency Freshness**
   - Percentage of dependencies on latest stable version
   - Target: > 80%

6. **Security Scan Coverage**
   - Percentage of code covered by security scans
   - Target: 100%

### Tracking Dashboard

Create a simple tracking spreadsheet:

| Date | Critical | High | Medium | Low | MTTD | MTTR | Notes |
|------|----------|------|--------|-----|------|------|-------|
| 2026-01 | 0 | 2 | 5 | 8 | 12h | 3d | ... |
| 2026-02 | 0 | 1 | 3 | 6 | 8h | 2d | ... |

---

## 🔐 Access Audit

### Repository Access Review

**Monthly task:**
```bash
# List repository collaborators
gh api repos/matiasportugau-ui/Chatbot-Truth-base--Creation/collaborators

# Review:
# - Does each person still need access?
# - Are permission levels appropriate?
# - Any inactive accounts to remove?
```

**Questions to ask:**
- [ ] Do all collaborators still require access?
- [ ] Are permission levels correct (read/write/admin)?
- [ ] Any external collaborators that should be removed?
- [ ] Any accounts inactive for > 90 days?

---

## 📝 Audit Checklist

### Pre-Deployment Security Checklist

Before deploying to production:

- [ ] All security scans pass (CodeQL, Bandit, Safety)
- [ ] No critical or high Dependabot alerts
- [ ] Dependencies up to date
- [ ] No secrets in code or config files
- [ ] Environment variables properly configured
- [ ] HTTPS/TLS enforced
- [ ] Rate limiting configured
- [ ] Error handling doesn't leak sensitive info
- [ ] Logging configured (no PII or secrets logged)
- [ ] Input validation implemented
- [ ] Authentication and authorization working
- [ ] Security headers configured
- [ ] Database connections secured
- [ ] Backups configured and tested

---

## 📚 Resources and Tools

### Security Tools

- **GitHub Security Features** - Built-in security scanning
- **Bandit** - Python security linter
- **Safety** - Python dependency vulnerability scanner
- **pip-audit** - PyPI vulnerability scanner
- **CodeQL** - Semantic code analysis
- **Dependabot** - Automated dependency updates
- **OWASP ZAP** - Web app security testing
- **Snyk** - Dependency vulnerability scanning

### Learning Resources

- [GitHub Security Lab](https://securitylab.github.com/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Python Security](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [OpenAI Safety](https://platform.openai.com/docs/guides/safety-best-practices)

---

## 🆘 Escalation Contacts

### Security Incident Escalation

| Level | Contact | Response Time |
|-------|---------|---------------|
| L1 - Informational | Team Lead | 1 business day |
| L2 - Medium | Security Champion | 4 hours |
| L3 - High | Repository Owner | 1 hour |
| L4 - Critical | Emergency Contact | Immediate |

**Emergency Security Contact:**
- Email: matiasportugau@gmail.com
- Create: [Private Security Advisory](https://github.com/matiasportugau-ui/Chatbot-Truth-base--Creation/security/advisories/new)

---

## 🔄 Continuous Improvement

### Review and Update This Guide

- **Frequency:** Quarterly
- **Next Review:** 2026-04-30
- **Owner:** @matiasportugau-ui

**Review checklist:**
- [ ] Are SLAs still appropriate?
- [ ] Are tools and processes effective?
- [ ] Are contact details current?
- [ ] New security features to add?
- [ ] Lessons learned from incidents?
- [ ] Team feedback incorporated?

---

**Last Updated:** 2026-01-31  
**Next Review:** 2026-04-30  
**Version:** 1.0  
**Maintainer:** @matiasportugau-ui
