"""
Panelin Persistence Module
===========================

Provides automatic context checkpointing, user profile management,
and conversation history persistence for the Panelin chatbot system.

Modules:
- context_database: SQLite database for context storage
- checkpoint_manager: Automatic checkpointing logic
- context_restorer: Context restoration mechanism
- user_profiles: User profile persistence
- personalization_engine: Personalization based on user behavior
"""

from .context_database import ContextDatabase
from .checkpoint_manager import CheckpointManager
from .context_restorer import ContextRestorer
from .user_profiles import UserProfileDatabase, UserProfile
from .personalization_engine import PersonalizationEngine

__all__ = [
    "ContextDatabase",
    "CheckpointManager",
    "ContextRestorer",
    "UserProfileDatabase",
    "UserProfile",
    "PersonalizationEngine",
]

__version__ = "1.0.0"
