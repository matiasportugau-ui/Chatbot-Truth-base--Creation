# 🛡️ Branch Protection and Repository Security Configuration Guide

## Overview

This document provides step-by-step instructions for repository administrators to configure comprehensive security settings for the Panelin project.

> **Note:** Most of these settings require **repository administrator** or **organization owner** permissions.

---

## Table of Contents

1. [Branch Protection Rules](#branch-protection-rules)
2. [Required Status Checks](#required-status-checks)
3. [Code Security Features](#code-security-features)
4. [Access Control](#access-control)
5. [Verification Steps](#verification-steps)

---

## Branch Protection Rules

### Protecting the Main Branch

1. **Navigate to Branch Settings:**
   - Repository → **Settings** → **Branches**
   - Under "Branch protection rules", click **Add rule**

2. **Configure Branch Name Pattern:**
   ```
   Branch name pattern: main
   ```
   (Also create rules for `master` if you use that branch)

3. **Enable Required Settings:**

   #### ✅ Protect matching branches:
   - ☑️ **Require a pull request before merging**
     - ☑️ Require approvals: **1** (minimum)
     - ☑️ Dismiss stale pull request approvals when new commits are pushed
     - ☑️ Require review from Code Owners
   
   - ☑️ **Require status checks to pass before merging**
     - ☑️ Require branches to be up to date before merging
     - Add status checks:
       - `Analyze (python)` (CodeQL)
       - `Analyze (javascript)` (CodeQL)
       - `Python Security Scan`
       - `test` (pytest)
   
   - ☑️ **Require conversation resolution before merging**
   
   - ☑️ **Require signed commits** (recommended)
   
   - ☑️ **Require linear history** (optional, prevents merge commits)
   
   - ☑️ **Include administrators** (enforce rules for admins too)
   
   - ☑️ **Restrict who can push to matching branches**
     - Add: `matiasportugau-ui` and other trusted maintainers
   
   - ☑️ **Allow force pushes** → **Nobody** (recommended)
   
   - ☑️ **Allow deletions** → **Disabled** (recommended)

4. **Click "Create" or "Save changes"**

### Additional Protected Branches

Consider protecting these branches too:
- `develop` or `dev`
- `staging`
- `production`
- Release branches: `release/*`

---

## Required Status Checks

### Configuring Status Checks

The following CI/CD workflows should be required to pass:

| Workflow | Check Name | Purpose |
|----------|------------|---------|
| CodeQL Analysis | `Analyze (python)` | Python security scanning |
| CodeQL Analysis | `Analyze (javascript)` | JavaScript/TypeScript security scanning |
| Security Scan | `Python Security Scan` | Bandit, Safety, pip-audit |
| Tests | `test` | pytest unit tests |
| Dependency Review | `Dependency Review` | Review new dependencies in PRs |

### Setup Instructions:

1. **Run workflows at least once** to make them selectable
2. **Go to branch protection settings**
3. **Under "Require status checks":**
   - Search and add each check listed above
   - ✅ Check "Require branches to be up to date"

---

## Code Security Features

### Enable All Security Features

Navigate to **Settings** → **Code security and analysis**

#### 1. Dependency Graph
- ✅ **Enable** (should be on by default)
- Automatically enabled for public repos
- Shows project dependencies

#### 2. Dependabot
- ✅ **Dependabot alerts** → Enable
  - Get alerts for vulnerable dependencies
  - Configure notification preferences

- ✅ **Dependabot security updates** → Enable
  - Automatically create PRs to update vulnerable dependencies
  - Review and merge Dependabot PRs regularly

- ✅ **Dependabot version updates** → Enable
  - Already configured via `.github/dependabot.yml`
  - Weekly checks for Python and npm packages

#### 3. Code Scanning
- ✅ **CodeQL analysis** → Configure
  - Select "Advanced" if you want to customize
  - Use the provided `.github/workflows/codeql-analysis.yml`
  - Or click "Set up this workflow" and merge the PR

#### 4. Secret Scanning
- ✅ **Secret scanning** → Enable
  - Scans for accidentally committed secrets
  - Automatically enabled for public repositories

- ✅ **Push protection** → Enable
  - **Highly recommended!**
  - Prevents pushing commits with detected secrets
  - Contributors get warning before push completes

#### 5. Private Vulnerability Reporting
- ✅ **Enable** (if available)
- Allows security researchers to privately report vulnerabilities
- Alternative to public issue reporting

---

## Access Control

### Two-Factor Authentication (2FA)

**Require 2FA for all organization members:**

1. **For Organizations:**
   - Navigate to **Organization Settings** → **Authentication security**
   - Enable **Require two-factor authentication**
   - Set deadline for members to enable 2FA

2. **For Personal Repos:**
   - Enable 2FA on your personal account
   - Settings → Password and authentication → Two-factor authentication

### Team and Collaborator Permissions

1. **Review Access:**
   - Settings → **Collaborators** (or **Manage access**)
   - Verify each collaborator's permission level

2. **Follow Least Privilege Principle:**
   - **Read**: For external contributors, auditors
   - **Triage**: For support team members
   - **Write**: For regular contributors
   - **Maintain**: For trusted team members
   - **Admin**: Only for project leads (minimum necessary)

3. **Use Teams (for Organizations):**
   - Create teams: `core-maintainers`, `contributors`, `security-team`
   - Assign team-based permissions
   - Easier to manage at scale

---

## Verification Steps

### ✅ Security Checklist

Use this checklist to verify your configuration:

#### Branch Protection
- [ ] Main branch protection enabled
- [ ] Require PR reviews (minimum 1 approval)
- [ ] Require status checks before merge
- [ ] Require branches up-to-date
- [ ] Require conversation resolution
- [ ] Enforce rules for administrators
- [ ] Signed commits required (recommended)
- [ ] Force push blocked
- [ ] Branch deletion blocked

#### Code Security
- [ ] Dependabot alerts enabled
- [ ] Dependabot security updates enabled
- [ ] CodeQL analysis configured and running
- [ ] Secret scanning enabled
- [ ] Secret scanning push protection enabled
- [ ] Security workflow (Bandit, Safety, pip-audit) running

#### Access Control
- [ ] 2FA required for all maintainers
- [ ] Collaborator permissions reviewed
- [ ] CODEOWNERS file configured
- [ ] Team permissions set (if using organization)

#### Monitoring
- [ ] Security alerts email notifications configured
- [ ] Workflow failure notifications enabled
- [ ] Dependabot notifications configured

### Testing Your Configuration

#### 1. Test Branch Protection:
```bash
# Try to push directly to main (should fail)
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "Test direct push"
git push origin main
# Expected: Push should be rejected
```

#### 2. Test PR Workflow:
```bash
# Create a feature branch
git checkout -b test-branch-protection
echo "test" >> test.txt
git add test.txt
git commit -m "Test PR workflow"
git push origin test-branch-protection
# Go to GitHub and create PR - status checks should be required
```

#### 3. Test Secret Scanning:
```bash
# Try to commit a fake secret (with push protection enabled)
git checkout -b test-secret-scan
echo "OPENAI_API_KEY=sk-proj-fake1234567890" >> test.txt
git add test.txt
git commit -m "Test secret scan"
git push origin test-secret-scan
# Expected: Push should be blocked with secret detected warning
```

---

## Automation and Monitoring

### Automated Security Reviews

The repository includes automated workflows that run:
- **On every push**: Tests, CodeQL
- **On every PR**: Dependency review, security scans
- **Daily**: Security scans (3 AM UTC)
- **Weekly**: Dependency updates check (Monday 9 AM UTC)

### Review Schedule

Establish a regular review cadence:

| Task | Frequency | Responsible |
|------|-----------|-------------|
| Review Dependabot PRs | Weekly | All maintainers |
| Review security alerts | Daily | Security lead |
| Audit access permissions | Monthly | Admin |
| Review CODEOWNERS | Quarterly | Admin |
| Rotate secrets | 90 days | Security lead |
| Full security audit | Annually | Security team |

---

## Troubleshooting

### Issue: "Status checks not appearing"

**Solution:**
1. Ensure workflows have run at least once
2. Check workflow files are in `.github/workflows/`
3. Verify workflows are enabled in Actions tab
4. Re-run workflows manually if needed

### Issue: "Can't merge PR even though checks pass"

**Solution:**
1. Check if branch is up-to-date with base branch
2. Verify all required reviewers have approved
3. Ensure all conversations are resolved
4. Check if signed commits are required

### Issue: "Dependabot PRs aren't being created"

**Solution:**
1. Verify `dependabot.yml` is in `.github/` directory
2. Check Insights → Dependency graph → Dependabot
3. Review Dependabot logs for errors
4. Ensure repository isn't archived or disabled

---

## Additional Resources

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [GitHub Security Features](https://docs.github.com/en/code-security)
- [Dependabot Configuration](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [Required Status Checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging)

---

**Last Updated:** 2026-01-31  
**Maintainer:** @matiasportugau-ui
