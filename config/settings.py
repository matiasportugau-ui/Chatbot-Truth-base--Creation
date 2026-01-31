import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

from config.security_utils import get_secret

# Load environment variables from .env if it exists
load_dotenv()

class Settings:
    """Centralized configuration for Panelin"""

    # Project Paths
    PROJECT_ROOT: Path = Path(os.getenv("PROJECT_ROOT", Path(__file__).parent.parent.absolute()))

    # KB Paths
    # Note: Using "Files" as default, but checking for "Files " (with space) for backward compatibility
    KB_PATH_DEFAULT = "Files"
    KB_PATH: Path = PROJECT_ROOT / os.getenv("KB_PATH", KB_PATH_DEFAULT)

    # If the directory with space exists, use it
    if (PROJECT_ROOT / "Files ").exists() and not (PROJECT_ROOT / "Files").exists():
        KB_PATH = PROJECT_ROOT / "Files "

    FILES_DIR: Path = KB_PATH

    # API Keys (loaded via security_utils to filter placeholders)
    OPENAI_API_KEY: Optional[str] = get_secret("OPENAI_API_KEY")
    OPENAI_ASSISTANT_ID: Optional[str] = os.getenv("OPENAI_ASSISTANT_ID", "asst_7LdhJMasW5HHGZh0cgchTGkX")

    # Google Sheets
    GSHEETS_CREDS: str = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "panelin_improvements/credentials.json")
    GSHEETS_NAME: str = os.getenv("GSHEETS_NAME", "BROMYROS_Costos_Ventas_2026")

    # Persistence
    MONGODB_URI: str = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DATABASE_NAME", "panelin")

    @classmethod
    def validate(cls) -> bool:
        """Basic validation of critical settings"""
        if not cls.OPENAI_API_KEY:
            print("⚠️ Warning: OPENAI_API_KEY is not set. "
                  "Add a real key to your .env file or system keyring.")
            return False
        return True

# Singleton instance
settings = Settings()
