"""
Settings and Configuration for Panelin Hybrid Agent.

Supports environment variables and configuration files.
"""

import os
from pathlib import Path
from typing import Optional, Literal
from dataclasses import dataclass, field
import json


@dataclass
class LLMSettings:
    """LLM configuration."""
    primary_model: str = "gpt-4o-mini"
    fallback_model: str = "claude-3-5-haiku-20241022"
    temperature: float = 0.0  # Deterministic for parameter extraction
    max_tokens: int = 4096
    
    # API Keys (from environment)
    openai_api_key: Optional[str] = field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY"))
    google_api_key: Optional[str] = field(default_factory=lambda: os.environ.get("GOOGLE_API_KEY"))


@dataclass
class ShopifySettings:
    """Shopify integration configuration."""
    store_url: str = "bmcuruguay.myshopify.com"
    api_version: str = "2024-01"
    access_token: Optional[str] = field(default_factory=lambda: os.environ.get("SHOPIFY_ACCESS_TOKEN"))
    webhook_secret: Optional[str] = field(default_factory=lambda: os.environ.get("SHOPIFY_WEBHOOK_SECRET"))


@dataclass
class KnowledgeBaseSettings:
    """Knowledge base configuration."""
    kb_path: Path = Path(__file__).parent.parent / "knowledge_base" / "panelin_truth_bmcuruguay.json"
    inventory_cache_path: Path = Path(__file__).parent.parent / "knowledge_base" / "inventory_cache.json"
    enable_vector_search: bool = False
    qdrant_url: Optional[str] = field(default_factory=lambda: os.environ.get("QDRANT_URL"))


@dataclass
class ObservabilitySettings:
    """Observability and logging configuration."""
    enable_langsmith: bool = False
    langsmith_api_key: Optional[str] = field(default_factory=lambda: os.environ.get("LANGSMITH_API_KEY"))
    langsmith_project: str = "panelin-hybrid-agent"
    log_level: str = "INFO"
    enable_tracing: bool = True


@dataclass
class BusinessRules:
    """Business rules configuration."""
    iva_rate: float = 0.22  # Uruguay IVA
    currency: str = "USD"
    bulk_discount_threshold_m2: float = 100.0
    bulk_discount_percent: float = 5.0
    minimum_order_m2: float = 10.0
    delivery_cost_per_m2: float = 1.50
    minimum_delivery_charge: float = 50.0


@dataclass
class Settings:
    """Main settings container."""
    llm: LLMSettings = field(default_factory=LLMSettings)
    shopify: ShopifySettings = field(default_factory=ShopifySettings)
    kb: KnowledgeBaseSettings = field(default_factory=KnowledgeBaseSettings)
    observability: ObservabilitySettings = field(default_factory=ObservabilitySettings)
    business: BusinessRules = field(default_factory=BusinessRules)
    
    # Environment
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables."""
        return cls(
            environment=os.environ.get("ENVIRONMENT", "development"),
            debug=os.environ.get("DEBUG", "true").lower() == "true",
        )
    
    @classmethod
    def from_file(cls, path: Path) -> "Settings":
        """Load settings from JSON file."""
        if path.exists():
            with open(path, 'r') as f:
                data = json.load(f)
            # For now, just return defaults
            # In production, would parse and apply overrides
            return cls.from_env()
        return cls.from_env()
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary (safe, no secrets)."""
        return {
            "environment": self.environment,
            "debug": self.debug,
            "llm": {
                "primary_model": self.llm.primary_model,
                "fallback_model": self.llm.fallback_model,
                "temperature": self.llm.temperature,
            },
            "shopify": {
                "store_url": self.shopify.store_url,
                "api_version": self.shopify.api_version,
                "has_access_token": self.shopify.access_token is not None,
            },
            "kb": {
                "kb_path": str(self.kb.kb_path),
                "enable_vector_search": self.kb.enable_vector_search,
            },
            "business": {
                "iva_rate": self.business.iva_rate,
                "currency": self.business.currency,
            }
        }


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings
