"""
Centralized secret management for Panelin.

Loads secrets from environment variables (including .env via python-dotenv).
Optionally uses the `keyring` library if installed.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from loguru import logger

# Ensure .env is loaded before any secret lookups
load_dotenv()

# Placeholder patterns that should NOT be treated as real values
_PLACEHOLDER_PATTERNS = (
    "your_",
    "sk-your-",
    "_here",
    "CHANGE_ME",
    "placeholder",
    "xxx",
)


def _is_placeholder(value: str) -> bool:
    """Return True if the value looks like a placeholder, not a real secret."""
    lower = value.strip().lower()
    return any(p.lower() in lower for p in _PLACEHOLDER_PATTERNS)


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieve a secret by name.

    Lookup order:
      1. OS environment variable (includes .env values loaded by dotenv)
      2. System keyring (if the `keyring` package is installed)
      3. The provided default

    Placeholder values (e.g. 'your_openai_api_key_here') are ignored.
    """
    # 1. Environment / .env
    value = os.environ.get(name)
    if value and not _is_placeholder(value):
        return value

    # 2. Keyring (optional dependency)
    try:
        import keyring as kr

        stored = kr.get_password("panelin", name)
        if stored and not _is_placeholder(stored):
            return stored
    except Exception:
        pass  # keyring not installed or backend unavailable

    if default is not None:
        return default

    logger.debug(f"Secret {name} not found in environment or keyring.")
    return None
