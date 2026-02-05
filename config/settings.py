import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
from .security_utils import get_secret

# Load environment variables from .env if it exists
load_dotenv()

class Settings:
    """Centralized configuration for Panelin"""
    
    # Project Paths
    PROJECT_ROOT: Path = Path(os.getenv("PROJECT_ROOT", Path(__file__).parent.parent.absolute()))
    
    # KB Paths
    KB_PATH_DEFAULT = "Files"
    KB_PATH: Path = PROJECT_ROOT / os.getenv("KB_PATH", KB_PATH_DEFAULT)
    
    # If the directory with space exists, use it
    if (PROJECT_ROOT / "Files ").exists() and not (PROJECT_ROOT / "Files").exists():
        KB_PATH = PROJECT_ROOT / "Files "
        
    FILES_DIR: Path = KB_PATH
    
    # API Keys & Secrets (via secure loader)
    OPENAI_API_KEY: Optional[str] = get_secret("OPENAI_API_KEY")
    OPENAI_ASSISTANT_ID: Optional[str] = get_secret("OPENAI_ASSISTANT_ID", "asst_7LdhJMasW5HHGZh0cgchTGkX")
    WOLF_API_KEY: Optional[str] = get_secret("WOLF_API_KEY")
    
    # Optional Provider Keys
    ANTHROPIC_API_KEY: Optional[str] = get_secret("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: Optional[str] = get_secret("GOOGLE_API_KEY")
    
    # Google Sheets
    GSHEETS_CREDS: str = get_secret("GOOGLE_SHEETS_CREDENTIALS", "panelin_improvements/credentials.json")
    GSHEETS_NAME: str = get_secret("GSHEETS_NAME", "BROMYROS_Costos_Ventas_2026")
    
    # Persistence
    MONGODB_URI: str = get_secret("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017")
    MONGODB_DB: str = get_secret("MONGODB_DATABASE_NAME", "panelin")

    # Facebook & Instagram
    FB_PAGE_ACCESS_TOKEN: Optional[str] = get_secret("FACEBOOK_PAGE_ACCESS_TOKEN")
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = get_secret("INSTAGRAM_ACCESS_TOKEN")

    @classmethod
    def validate(cls) -> bool:
        """Basic validation of critical settings"""
        if not cls.OPENAI_API_KEY:
            print("⚠️ Warning: OPENAI_API_KEY is not set")
            return False
        return True

# Singleton instance
settings = Settings()
