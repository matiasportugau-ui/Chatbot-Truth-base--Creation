# Security Recommendations for Panelin

To maintain the security of this project, please follow these guidelines:

## 1. Secrets Management
- All secrets (API keys, tokens, etc.) should ideally be stored in the **Windows Credential Manager** for security.
- Use `python scripts/manage_secrets.py` to set up your keys securely.
- For local development, secrets can be stored in a `.env` file (which is ignored by Git), but this is less secure than using the system keyring.
- Never commit the `.env` file or any `credentials.json` files.
- If an API key is accidentally committed, revoke it immediately in the provider's dashboard.

## 2. Preventing Leaks with Pre-commit Hooks
We recommend installing `pre-commit` and `detect-secrets` to prevent accidental commits of sensitive information.

### Installation:
```bash
pip install pre-commit detect-secrets
```

### Setup:
1. Create a `.pre-commit-config.yaml` file in the root:
```yaml
repos:
-   repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
    -   id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```
2. Run `detect-secrets scan > .secrets.baseline` to initialize.
3. Run `pre-commit install` to activate the hook.

## 3. Safe Execution
- Use `subprocess.run` with a list of arguments instead of a single string to avoid shell injection.
- Prefer `sys.executable` when running other Python scripts from within a script.

## 4. Git Repository Scope
- Ensure the Git repository is initialized only within the `Chatbot-Truth-base--Creation` folder, not in your user home directory.
