import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from config.settings import settings
from config.security_utils import KEYRING_SERVICE
import os

def mask(s):
    if not s:
        return "MISSING"
    if len(s) <= 8:
        return "****"
    return f"{s[:4]}...{s[-4:]}"

def check_source(key):
    # This is a bit of a hack to check where it came from since settings loads it once
    # We re-check manually for the diagnostic
    import keyring
    use_keyring = os.getenv("USE_KEYRING", "false").lower() == "true"
    
    if use_keyring:
        try:
            if keyring.get_password(KEYRING_SERVICE, key):
                return "Keyring"
        except:
            pass
            
    if os.getenv(key):
        return ".env / Environment"
        
    return "Not Found"

def main():
    print("=" * 60)
    print("🛡️  PANELIN SECURITY DIAGNOSTIC 🛡️")
    print("=" * 60)
    
    use_keyring = os.getenv("USE_KEYRING", "false").lower() == "true"
    print(f"USE_KEYRING: {use_keyring}")
    print(f"KEYRING_SERVICE: {KEYRING_SERVICE}")
    print("-" * 60)
    
    keys_to_check = [
        "OPENAI_API_KEY",
        "OPENAI_ASSISTANT_ID",
        "WOLF_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "MONGODB_CONNECTION_STRING"
    ]
    
    print(f"{'Secret Key':<25} | {'Source':<20} | {'Value (Masked)':<15}")
    print("-" * 60)
    
    for key in keys_to_check:
        val = getattr(settings, key, None)
        # Handle special mapping for MONGODB_URI in settings
        if key == "MONGODB_CONNECTION_STRING":
            val = settings.MONGODB_URI
            
        source = check_source(key)
        print(f"{key:<25} | {source:<20} | {mask(val):<15}")
        
    print("-" * 60)
    print("\n💡 Recommendation:")
    if not use_keyring:
        print("   Keyring is DISABLED. Set USE_KEYRING=true in .env to enable system-level security.")
    else:
        print("   Keyring is ENABLED. Run 'python scripts/manage_secrets.py' to add more keys.")
    
    print("\n✅ Verification complete.")

if __name__ == "__main__":
    main()
