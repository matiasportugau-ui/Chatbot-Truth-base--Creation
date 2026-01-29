"""
Panelin Settings - Configuración del sistema de cotización.

Este módulo centraliza toda la configuración del agente Panelin:
- Modelos LLM y fallbacks
- Paths a knowledge base
- Parámetros de validación
- Configuración de Shopify sync
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class LLMConfig:
    """Configuración de modelos LLM."""
    primary_model: str = "gpt-4o-mini"
    fallback_model: str = "gpt-4o"
    temperature: float = 0.0  # Determinismo para extracción
    max_tokens: int = 2000
    api_key: Optional[str] = None
    
    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.environ.get("OPENAI_API_KEY")


@dataclass
class KnowledgeBaseConfig:
    """Configuración de base de conocimiento."""
    kb_path: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data" / "panelin_truth_bmcuruguay.json")
    sync_log_path: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data" / "sync_history.json")
    cache_ttl_seconds: int = 3600
    auto_refresh: bool = True


@dataclass
class ShopifyConfig:
    """Configuración de Shopify sync."""
    shop_domain: str = "bmcuruguay.myshopify.com"
    api_version: str = "2024-01"
    access_token: Optional[str] = None
    webhook_secret: Optional[str] = None
    sync_enabled: bool = True
    reconciliation_schedule: str = "daily"
    
    def __post_init__(self):
        if self.access_token is None:
            self.access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN")
        if self.webhook_secret is None:
            self.webhook_secret = os.environ.get("SHOPIFY_WEBHOOK_SECRET")


@dataclass
class ValidationConfig:
    """Configuración de validación de cotizaciones."""
    require_calculation_verified: bool = True
    require_checksum: bool = True
    max_discount_percent: float = 30.0
    min_order_value: float = 100.0
    validate_on_every_quote: bool = True


@dataclass
class ObservabilityConfig:
    """Configuración de observabilidad y logging."""
    langsmith_enabled: bool = False
    langsmith_project: str = "panelin-quotation-agent"
    log_level: str = "INFO"
    log_tool_calls: bool = True
    log_validations: bool = True
    
    def __post_init__(self):
        if os.environ.get("LANGCHAIN_API_KEY"):
            self.langsmith_enabled = True


@dataclass
class PricingConfig:
    """Configuración de pricing."""
    default_currency: str = "USD"
    tax_rate_uy: float = 22.0
    delivery_cost_per_m2: float = 1.50
    minimum_delivery_charge: float = 50.0
    free_delivery_threshold: float = 1000.0
    
    # Volume discounts
    volume_discount_thresholds: List[tuple] = field(default_factory=lambda: [
        (100.0, 5.0),   # 100+ m² = 5% discount
        (200.0, 8.0),   # 200+ m² = 8% discount
        (500.0, 12.0),  # 500+ m² = 12% discount
    ])
    
    # Customer type discounts
    customer_discounts: dict = field(default_factory=lambda: {
        "retail": 0.0,
        "wholesale": 5.0,
        "contractor": 10.0,
    })


@dataclass
class PanelinConfig:
    """Configuración completa del sistema Panelin."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    kb: KnowledgeBaseConfig = field(default_factory=KnowledgeBaseConfig)
    shopify: ShopifyConfig = field(default_factory=ShopifyConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    observability: ObservabilityConfig = field(default_factory=ObservabilityConfig)
    pricing: PricingConfig = field(default_factory=PricingConfig)
    
    # Agent metadata
    agent_version: str = "2.0.0"
    agent_name: str = "Panelin Quotation Agent"
    
    @classmethod
    def from_env(cls) -> "PanelinConfig":
        """Crea configuración desde variables de entorno."""
        return cls(
            llm=LLMConfig(
                primary_model=os.environ.get("PANELIN_PRIMARY_MODEL", "gpt-4o-mini"),
                fallback_model=os.environ.get("PANELIN_FALLBACK_MODEL", "gpt-4o"),
                temperature=float(os.environ.get("PANELIN_LLM_TEMPERATURE", "0")),
            ),
            shopify=ShopifyConfig(
                shop_domain=os.environ.get("SHOPIFY_SHOP_DOMAIN", "bmcuruguay.myshopify.com"),
                sync_enabled=os.environ.get("SHOPIFY_SYNC_ENABLED", "true").lower() == "true",
            ),
            observability=ObservabilityConfig(
                langsmith_enabled=bool(os.environ.get("LANGCHAIN_API_KEY")),
                log_level=os.environ.get("PANELIN_LOG_LEVEL", "INFO"),
            ),
        )


# Default configuration instance
DEFAULT_CONFIG = PanelinConfig()


def get_config() -> PanelinConfig:
    """
    Obtiene la configuración actual.
    
    Intenta cargar desde variables de entorno,
    cae a defaults si no están disponibles.
    
    Returns:
        PanelinConfig con la configuración actual
    """
    # Check for environment-based config
    if os.environ.get("PANELIN_USE_ENV_CONFIG", "").lower() == "true":
        return PanelinConfig.from_env()
    
    return DEFAULT_CONFIG
