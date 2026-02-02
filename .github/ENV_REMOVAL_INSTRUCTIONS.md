# 🚨 CRITICAL: .env File Removal and Secret Rotation Instructions

## ⚠️ IMMEDIATE ACTION REQUIRED

The `.env` file was previously committed to the repository. While it has been removed from tracking, it still exists in Git history. **All secrets in that file should be considered compromised.**

---

## 🔒 Step 1: Remove .env from Git Tracking (COMPLETED)

✅ **Already done** - The `.env` file has been removed from Git tracking using:
```bash
git rm --cached .env
```

The file still exists locally but won't be committed in future changes.

---

## 🔑 Step 2: Rotate ALL Exposed Secrets (REQUIRED)

### API Keys That MUST Be Rotated

Based on the committed `.env` file, the following secret was exposed:

#### OpenAI API Key
- **Status**: ⚠️ **COMPROMISED** - Was committed to repository
- **Action Required**: Immediate rotation

### Rotation Steps

#### 1. OpenAI API Key Rotation

**Generate New Key:**
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Name it clearly (e.g., "Panelin Production - 2026-01-31")
4. Copy the new key immediately (you won't see it again)

**Update Local Environment:**
```bash
# Edit your local .env file
nano .env

# Replace the old OPENAI_API_KEY with the new one
# Old: OPENAI_API_KEY=sk-your-actual-api-key-here
# New: OPENAI_API_KEY=sk-proj-new-key-here
```

**Update GitHub Actions Secrets:**
1. Go to Repository → Settings → Secrets and variables → Actions
2. Find `OPENAI_API_KEY` secret (or create if it doesn't exist)
3. Click "Update" and paste the new key
4. Click "Update secret"

**Update Production Environment:**
- If deployed to a server, update the environment variable there
- If using a cloud provider, update secrets in their console
- Restart services to pick up the new key

**Revoke Old Key:**
1. Go back to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Find the old key in the list
3. Click the trash icon to revoke it
4. Confirm revocation

**Verify:**
```bash
# Test that the new key works
python -c "from openai import OpenAI; client = OpenAI(); print('API key works!')"
```

#### 2. Other API Keys (If Configured)

If you have configured any of these services, rotate their keys too:

**Anthropic (Claude):**
- Console: https://console.anthropic.com/
- Generate new key → Update .env → Revoke old key

**Google (Gemini):**
- Console: https://makersuite.google.com/app/apikey
- Generate new key → Update .env → Revoke old key

**Facebook/Instagram:**
- Generate new access tokens in Facebook Developer Console
- Update .env and production
- Revoke old tokens

**MercadoLibre:**
- Refresh token through OAuth flow
- Update .env and production

---

## 🧹 Step 3: Clean Git History (OPTIONAL - Advanced)

⚠️ **WARNING**: This is a destructive operation that rewrites Git history. Only do this if:
- You understand Git history rewriting
- You can coordinate with all team members
- The repository is not heavily used by others

### Option A: BFG Repo-Cleaner (Recommended)

```bash
# Install BFG
# On macOS:
brew install bfg

# On Linux:
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar
alias bfg='java -jar bfg-1.14.0.jar'

# Clone a fresh copy
cd /tmp
git clone --mirror https://github.com/matiasportugau-ui/Chatbot-Truth-base--Creation.git
cd Chatbot-Truth-base--Creation.git

# Remove .env from history
bfg --delete-files .env

# Clean up
git reflog expire --expire=now --all && git gc --prune=now --aggressive

# Force push (requires admin rights and will affect all collaborators)
git push --force
```

### Option B: Git Filter-Repo

```bash
# Install git-filter-repo
pip install git-filter-repo

# Clone a fresh copy
cd /tmp
git clone https://github.com/matiasportugau-ui/Chatbot-Truth-base--Creation.git
cd Chatbot-Truth-base--Creation

# Remove .env from history
git filter-repo --path .env --invert-paths

# Force push (requires admin rights)
git push --force --all
git push --force --tags
```

### Option C: Leave History As-Is (Safest)

**Recommended approach**: Since all secrets will be rotated anyway, you can simply:
1. ✅ Remove `.env` from tracking (already done)
2. ✅ Rotate all secrets (do this now)
3. ✅ Document the incident
4. Move forward with proper security practices

The old secrets in Git history are useless after rotation.

---

## 📝 Step 4: Document the Rotation

Create a security log entry:

```bash
# Create or append to security log
cat >> .github/SECURITY_LOG.md << 'EOF'

### Security Incident - 2026-01-31

**Type**: Secret exposure  
**Severity**: High  
**Status**: Resolved

**Description**:
The `.env` file was committed to the repository, exposing the OpenAI API key.

**Actions Taken**:
1. Removed `.env` from Git tracking
2. Rotated OpenAI API key
3. Updated local and production environments
4. Revoked old API key
5. Enhanced `.env.example` with security warnings
6. Implemented automated secret scanning

**Prevention**:
- Enabled secret scanning with push protection
- Added comprehensive security documentation
- Educated team on secrets management

**Verified By**: @matiasportugau-ui  
**Date**: 2026-01-31

EOF
```

---

## ✅ Verification Checklist

After completing the rotation, verify:

```markdown
- [ ] New OpenAI API key generated
- [ ] Local .env updated with new key
- [ ] GitHub Actions secrets updated
- [ ] Production environment updated
- [ ] Old API key revoked
- [ ] New key tested and working
- [ ] All team members notified of key rotation
- [ ] Security log updated
- [ ] .env is in .gitignore (verify: `grep "^\.env$" .gitignore`)
- [ ] .env is not tracked (verify: `git status` doesn't show .env)
```

---

## 🔮 Future Prevention

These measures are now in place to prevent future exposures:

✅ **Automated Protection**:
- Secret scanning enabled (detects committed secrets)
- Push protection enabled (blocks commits with secrets)
- TruffleHog scans in CI/CD
- Pre-commit hooks recommended

✅ **Documentation**:
- [SECRETS_MANAGEMENT.md](.github/SECRETS_MANAGEMENT.md) - Best practices
- [CONTRIBUTING_SECURITY.md](.github/CONTRIBUTING_SECURITY.md) - Contributor guidelines
- Enhanced `.env.example` with warnings

✅ **Monitoring**:
- Daily security scans
- Continuous secret scanning
- Regular security audits

---

## 🆘 Need Help?

**If you're unsure about any step**:
1. **Don't panic** - We have a plan
2. **Rotate secrets first** - This is the most important step
3. **Ask for help** - Tag @matiasportugau-ui or security team
4. **Document what you did** - For security log

**If you discover the old key was used maliciously**:
1. Check OpenAI usage logs immediately
2. Review billing for unexpected charges
3. Follow incident response in [SECURITY_MONITORING.md](.github/SECURITY_MONITORING.md)
4. Consider filing a security incident report

---

## 📋 Quick Reference

**Key Rotation Schedule**:
- **Emergency rotation**: Immediately when compromised
- **Routine rotation**: Every 90 days
- **Next scheduled rotation**: 2026-04-30 (90 days from now)

**Service Provider Consoles**:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Google: https://makersuite.google.com/app/apikey
- Facebook: https://developers.facebook.com/

**Documentation**:
- [SECRETS_MANAGEMENT.md](.github/SECRETS_MANAGEMENT.md) - Full guide
- [SECURITY.md](../SECURITY.md) - Security policy
- [SECURITY_MONITORING.md](.github/SECURITY_MONITORING.md) - Incident response

---

**Last Updated**: 2026-01-31  
**Severity**: High  
**Action Required**: Immediate secret rotation
