import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
KEYRING_SERVICE = "PanelinWolf"

def get_secret(key_name, default=None):
    """
    Retrieves a secret from the system keyring or environment variables.
    Precedence: Keyring (if enabled) > Environment Variable > Default
    """
    use_keyring = os.getenv("USE_KEYRING", "false").lower() == "true"

    # 1. Try Keyring (lazy import to avoid keyring backend issues in containers)
    if use_keyring:
        try:
            import keyring
            from loguru import logger
            secret = keyring.get_password(KEYRING_SERVICE, key_name)
            if secret:
                return secret
        except Exception as e:
            try:
                from loguru import logger
                logger.warning(f"Failed to retrieve {key_name} from keyring: {e}")
            except Exception:
                pass

    # 2. Try Environment Variable
    secret = os.getenv(key_name)
    if secret:
        return secret

    # 3. Fallback to Default
    if default is None:
        try:
            from loguru import logger
            logger.debug(f"Secret {key_name} not found in keyring or environment.")
        except Exception:
            pass

    return default
