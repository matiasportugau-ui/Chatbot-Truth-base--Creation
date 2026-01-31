# Branch Protection Setup Guide

This document provides step-by-step instructions for configuring branch protection rules to ensure code quality and security.

## 🎯 Overview

Branch protection rules prevent direct pushes to important branches and ensure that all changes go through a review process with automated checks.

## 📋 Prerequisites

- Repository admin or owner access
- At least one workflow configured (we have tests, CodeQL, and security scanning)

## 🔒 Recommended Protection Rules

### For `main` branch

#### Step 1: Access Branch Protection Settings

1. Navigate to: **Repository** → **Settings** → **Branches**
2. Under "Branch protection rules", click **Add rule** or **Edit** if a rule exists
3. In "Branch name pattern", enter: `main`

#### Step 2: Configure Protection Settings

Enable the following settings:

##### ✅ Require pull request before merging
- [x] **Require a pull request before merging**
  - [x] Require approvals: **1** (minimum, increase to 2 for critical repos)
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners (if CODEOWNERS file exists)
  - [x] Restrict who can dismiss pull request reviews
  - [x] Allow specified actors to bypass required pull requests: *(Leave empty for strict enforcement)*

##### ✅ Require status checks to pass before merging
- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging
  - **Select required status checks:**
    - `test / test` (Python tests)
    - `analyze (python) / Analyze Code with CodeQL` (CodeQL Python)
    - `analyze (javascript) / Analyze Code with CodeQL` (CodeQL JavaScript)
    - `security-scan / Python Security Analysis` (Security scanning)

##### ✅ Require conversation resolution before merging
- [x] **Require conversation resolution before merging**
  - Ensures all review comments are addressed before merge

##### ✅ Require signed commits
- [x] **Require signed commits** (Recommended for high-security environments)
  - See "Setting up Commit Signing" section below

##### ✅ Require linear history
- [x] **Require linear history** (Optional but recommended)
  - Prevents merge commits, enforces rebase or squash merging

##### ✅ Require deployments to succeed before merging
- [ ] Require deployments to succeed (Enable if you have deployment workflows)

##### ✅ Lock branch
- [ ] Lock branch (Only enable for archived/protected branches)

##### ✅ Do not allow bypassing the above settings
- [x] **Do not allow bypassing the above settings**
  - Applies rules even to repository admins

##### ✅ Restrict who can push to matching branches
- [x] **Restrict who can push to matching branches**
  - Add specific users/teams who can push (usually none for strict protection)
  - Consider adding CI/CD service accounts if needed

##### ✅ Allow force pushes
- [ ] **Allow force pushes** (Keep DISABLED for main branch)

##### ✅ Allow deletions
- [ ] **Allow deletions** (Keep DISABLED for main branch)

#### Step 3: Save Protection Rules

Click **Create** or **Save changes** at the bottom of the page.

---

## 🔐 Setting Up Commit Signing (Optional but Recommended)

Commit signing ensures commits are from verified sources.

### Using GPG Keys

#### 1. Generate GPG Key

```bash
# Generate a new GPG key
gpg --full-generate-key

# Use RSA and RSA, 4096 bits, no expiration
# Enter your name and email (must match GitHub email)
```

#### 2. Get Your GPG Key ID

```bash
# List GPG keys
gpg --list-secret-keys --keyid-format=long

# Output will look like:
# sec   rsa4096/YOUR_KEY_ID 2024-01-01 [SC]
# Copy YOUR_KEY_ID
```

#### 3. Export GPG Public Key

```bash
# Export the GPG public key
gpg --armor --export YOUR_KEY_ID
```

#### 4. Add GPG Key to GitHub

1. Go to: **GitHub** → **Settings** → **SSH and GPG keys**
2. Click **New GPG key**
3. Paste your GPG public key
4. Click **Add GPG key**

#### 5. Configure Git to Sign Commits

```bash
# Configure Git to use your GPG key
git config --global user.signingkey YOUR_KEY_ID

# Enable commit signing by default
git config --global commit.gpgsign true

# Configure GPG program (if needed)
git config --global gpg.program gpg
```

#### 6. Test Commit Signing

```bash
# Make a signed commit
git commit -S -m "Test signed commit"

# Verify the signature
git log --show-signature -1
```

### Using SSH Keys (Alternative)

GitHub also supports signing commits with SSH keys (easier setup):

```bash
# Configure Git to use SSH signing
git config --global gpg.format ssh

# Set your SSH key for signing
git config --global user.signingkey ~/.ssh/id_ed25519.pub

# Enable commit signing
git config --global commit.gpgsign true
```

---

## 📊 Verifying Branch Protection

After setting up protection rules, verify they work:

### Test 1: Direct Push (Should Fail)

```bash
# Try to push directly to main
git checkout main
echo "test" >> README.md
git add README.md
git commit -m "Test direct push"
git push

# Expected: Push rejected by remote (branch protection)
```

### Test 2: PR Without Status Checks (Should Fail)

1. Create a branch and make changes
2. Open a pull request
3. Try to merge before status checks pass
4. Expected: Merge button disabled until checks pass

### Test 3: PR Without Review (Should Fail)

1. Open a pull request
2. Wait for status checks to pass
3. Try to merge without approval
4. Expected: Merge button disabled until review approved

### Test 4: PR With Unresolved Comments (Should Fail)

1. Open a pull request
2. Add a review comment
3. Try to merge with unresolved conversation
4. Expected: Merge blocked until conversation resolved

---

## 🎛️ Branch Protection Matrix

| Branch | PR Required | Reviews | Status Checks | Signed Commits | Admins Bypass |
|--------|-------------|---------|---------------|----------------|---------------|
| `main` | ✅ Yes | 1+ | ✅ All required | ⚠️ Recommended | ❌ No |
| `develop` | ✅ Yes | 1+ | ✅ All required | ⚠️ Optional | ❌ No |
| `feature/*` | ✅ Yes | 1 | ✅ Tests only | ❌ No | ✅ Yes |
| `release/*` | ✅ Yes | 2+ | ✅ All required | ✅ Yes | ❌ No |

---

## 🔄 Recommended Workflow

1. **Create feature branch** from `main`
   ```bash
   git checkout main
   git pull
   git checkout -b feature/your-feature
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

3. **Push to remote**
   ```bash
   git push -u origin feature/your-feature
   ```

4. **Open Pull Request** on GitHub
   - Fill in PR template
   - Request reviewers
   - Add labels

5. **Wait for checks** to pass
   - Python tests
   - CodeQL analysis
   - Security scanning

6. **Address review comments**
   - Make requested changes
   - Resolve conversations
   - Push updates

7. **Merge when approved**
   - Use "Squash and merge" for clean history
   - Delete branch after merge

---

## 🚨 Troubleshooting

### Issue: Can't push to main
**Solution:** This is expected! Create a pull request instead.

### Issue: Status checks not running
**Solution:** 
- Check that workflows are enabled in repository settings
- Verify workflow files are in `.github/workflows/`
- Check Actions tab for errors

### Issue: Can't merge even with approvals
**Solution:**
- Ensure all status checks pass
- Resolve all conversations
- Update branch if "require up-to-date" is enabled

### Issue: Signed commits not working
**Solution:**
- Verify GPG key is added to GitHub
- Check `git config --global --list` for signing settings
- Ensure email matches GitHub account

---

## 📚 Additional Resources

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Configuring Protected Branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule)
- [About Commit Signature Verification](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification)
- [GitHub Status Checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)

---

**Last Updated:** 2026-01-31  
**Maintainer:** @matiasportugau-ui
