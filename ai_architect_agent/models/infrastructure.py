"""
Infrastructure specifications for chatbot deployment.

Optimized for Uruguay market with focus on:
- Minimal latency to South America
- Cost efficiency ($0-10/month hosting target)
- Production reliability for webhook servers
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class HostingTier(Enum):
    """Hosting cost tiers."""
    FREE = "free"
    BUDGET = "budget"  # $1-5/month
    STANDARD = "standard"  # $5-20/month
    PREMIUM = "premium"  # $20+/month


class HostingType(Enum):
    """Type of hosting infrastructure."""
    VPS = "vps"  # Virtual Private Server
    SERVERLESS = "serverless"
    CONTAINER = "container"
    PAAS = "paas"  # Platform as a Service


@dataclass
class HostingProvider:
    """Cloud hosting provider specification."""
    name: str
    monthly_cost: float
    tier: HostingTier
    hosting_type: HostingType
    region: str  # Closest to Uruguay
    cpu_cores: float
    ram_gb: float
    storage_gb: int
    bandwidth_gb: int  # Monthly transfer
    always_on: bool  # No cold starts / sleeping
    latency_to_uruguay_ms: int  # Estimated
    reliability_score: float  # 0-1, based on SLA and reputation
    setup_complexity: int  # 1-10
    notes: str = ""

    @property
    def value_score(self) -> float:
        """Calculate value: resources per dollar (higher is better)."""
        if self.monthly_cost == 0:
            return float('inf') if self.always_on else 0
        resources = (self.cpu_cores * 2) + self.ram_gb + (self.storage_gb / 10)
        reliability_factor = self.reliability_score * 2
        latency_factor = max(0, 1 - (self.latency_to_uruguay_ms / 500))
        return (resources * reliability_factor * latency_factor) / self.monthly_cost

    @classmethod
    def oracle_cloud_free(cls) -> "HostingProvider":
        """Oracle Cloud Always Free tier - best free option."""
        return cls(
            name="Oracle Cloud (Always Free)",
            monthly_cost=0.0,
            tier=HostingTier.FREE,
            hosting_type=HostingType.VPS,
            region="Sao Paulo",
            cpu_cores=4,  # ARM Ampere
            ram_gb=24,
            storage_gb=200,
            bandwidth_gb=10000,
            always_on=True,
            latency_to_uruguay_ms=50,
            reliability_score=0.85,
            setup_complexity=7,  # ARM instances have availability constraints
            notes="Best free value. ARM architecture may require container adjustments. "
                  "Use Sao Paulo region. Capacity constraints may delay provisioning."
        )

    @classmethod
    def vultr_buenos_aires(cls) -> "HostingProvider":
        """Vultr Buenos Aires - lowest latency to Uruguay."""
        return cls(
            name="Vultr (Buenos Aires)",
            monthly_cost=5.0,
            tier=HostingTier.BUDGET,
            hosting_type=HostingType.VPS,
            region="Buenos Aires",
            cpu_cores=1,
            ram_gb=1,
            storage_gb=25,
            bandwidth_gb=1000,
            always_on=True,
            latency_to_uruguay_ms=20,  # Closest possible
            reliability_score=0.90,
            setup_complexity=4,
            notes="Lowest latency to Uruguay. Simple setup. "
                  "Excellent for latency-sensitive webhook responses."
        )

    @classmethod
    def hetzner_budget(cls) -> "HostingProvider":
        """Hetzner CX22 - best paid value in Europe."""
        return cls(
            name="Hetzner (CX22)",
            monthly_cost=3.49,
            tier=HostingTier.BUDGET,
            hosting_type=HostingType.VPS,
            region="Germany",
            cpu_cores=2,
            ram_gb=4,
            storage_gb=40,
            bandwidth_gb=20000,
            always_on=True,
            latency_to_uruguay_ms=200,  # Europe to SA
            reliability_score=0.95,
            setup_complexity=4,
            notes="Best resources per dollar. Higher latency acceptable for "
                  "non-realtime processing. Excellent for background jobs."
        )

    @classmethod
    def linode_sao_paulo(cls) -> "HostingProvider":
        """Linode Sao Paulo - regional with good reliability."""
        return cls(
            name="Linode (Sao Paulo)",
            monthly_cost=5.0,
            tier=HostingTier.BUDGET,
            hosting_type=HostingType.VPS,
            region="Sao Paulo",
            cpu_cores=1,
            ram_gb=1,
            storage_gb=25,
            bandwidth_gb=1000,
            always_on=True,
            latency_to_uruguay_ms=50,
            reliability_score=0.92,
            setup_complexity=3,
            notes="Good balance of latency and reliability. "
                  "Simple interface, strong documentation."
        )

    @classmethod
    def render_free(cls) -> "HostingProvider":
        """Render free tier - NOT recommended for webhooks."""
        return cls(
            name="Render (Free Tier)",
            monthly_cost=0.0,
            tier=HostingTier.FREE,
            hosting_type=HostingType.PAAS,
            region="Oregon",
            cpu_cores=0.1,
            ram_gb=0.5,
            storage_gb=0,
            bandwidth_gb=100,
            always_on=False,  # Sleeps after 15 min inactivity
            latency_to_uruguay_ms=150,
            reliability_score=0.50,  # Low due to cold starts
            setup_complexity=2,
            notes="NOT RECOMMENDED for webhooks. Services sleep after 15 min, "
                  "causing 30-50 second cold starts that break real-time chat."
        )

    @classmethod
    def railway_starter(cls) -> "HostingProvider":
        """Railway starter - limited free credits."""
        return cls(
            name="Railway (Starter)",
            monthly_cost=0.0,  # $5 credit, then pay
            tier=HostingTier.FREE,
            hosting_type=HostingType.PAAS,
            region="US West",
            cpu_cores=1,
            ram_gb=0.5,
            storage_gb=1,
            bandwidth_gb=100,
            always_on=True,
            latency_to_uruguay_ms=150,
            reliability_score=0.80,
            setup_complexity=2,
            notes="$5 monthly credit exhausts quickly with 24/7 uptime. "
                  "Good for testing, not sustainable long-term free."
        )

    @classmethod
    def all_providers(cls) -> list["HostingProvider"]:
        """Get all hosting providers sorted by value score."""
        providers = [
            cls.oracle_cloud_free(),
            cls.vultr_buenos_aires(),
            cls.hetzner_budget(),
            cls.linode_sao_paulo(),
            cls.render_free(),
            cls.railway_starter(),
        ]
        # Sort by value (free always-on first, then by value score)
        return sorted(
            providers,
            key=lambda p: (
                not (p.monthly_cost == 0 and p.always_on),
                -p.value_score if p.value_score != float('inf') else 0
            )
        )


class LLMProvider(Enum):
    """LLM API providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"


@dataclass
class LLMModel:
    """LLM model specification with costs."""
    provider: LLMProvider
    model_id: str
    name: str
    input_cost_per_million: float  # $ per 1M tokens
    output_cost_per_million: float  # $ per 1M tokens
    context_window: int  # tokens
    supports_caching: bool
    cache_discount: float  # 0-1, percentage off for cached
    quality_score: float  # 0-1, relative capability
    speed_score: float  # 0-1, relative speed
    notes: str = ""

    def estimate_cost(
        self,
        conversations: int,
        avg_input_tokens: int = 500,
        avg_output_tokens: int = 300,
        cache_hit_ratio: float = 0.3,
    ) -> float:
        """Estimate monthly cost for given conversation volume."""
        total_input = conversations * avg_input_tokens
        total_output = conversations * avg_output_tokens

        # Apply caching discount
        if self.supports_caching:
            cached_input = total_input * cache_hit_ratio
            uncached_input = total_input * (1 - cache_hit_ratio)
            input_cost = (
                (uncached_input / 1_000_000) * self.input_cost_per_million +
                (cached_input / 1_000_000) * self.input_cost_per_million * (1 - self.cache_discount)
            )
        else:
            input_cost = (total_input / 1_000_000) * self.input_cost_per_million

        output_cost = (total_output / 1_000_000) * self.output_cost_per_million

        return round(input_cost + output_cost, 2)

    @classmethod
    def gpt4o_mini(cls) -> "LLMModel":
        """GPT-4o-mini - optimal cost/performance for quotation chatbots."""
        return cls(
            provider=LLMProvider.OPENAI,
            model_id="gpt-4o-mini",
            name="GPT-4o Mini",
            input_cost_per_million=0.15,
            output_cost_per_million=0.60,
            context_window=128000,
            supports_caching=True,
            cache_discount=0.50,
            quality_score=0.85,
            speed_score=0.95,
            notes="RECOMMENDED. Handles 90%+ of queries effectively at 16x less "
                  "than GPT-4o. Best cost/performance ratio for quotation bots."
        )

    @classmethod
    def gpt4o(cls) -> "LLMModel":
        """GPT-4o - premium option for complex reasoning."""
        return cls(
            provider=LLMProvider.OPENAI,
            model_id="gpt-4o",
            name="GPT-4o",
            input_cost_per_million=2.50,
            output_cost_per_million=10.00,
            context_window=128000,
            supports_caching=True,
            cache_discount=0.50,
            quality_score=0.98,
            speed_score=0.80,
            notes="Premium option. Reserve for complex edge cases requiring "
                  "advanced reasoning. 16x more expensive than mini."
        )

    @classmethod
    def gemini_flash(cls) -> "LLMModel":
        """Gemini 2.5 Flash - competitive alternative with free tier."""
        return cls(
            provider=LLMProvider.GOOGLE,
            model_id="gemini-2.5-flash",
            name="Gemini 2.5 Flash",
            input_cost_per_million=0.15,
            output_cost_per_million=0.60,
            context_window=1000000,
            supports_caching=True,
            cache_discount=0.75,
            quality_score=0.85,
            speed_score=0.95,
            notes="Identical pricing to GPT-4o-mini. Has FREE tier of "
                  "1,500 requests/day - may eliminate LLM costs entirely."
        )

    @classmethod
    def claude_haiku(cls) -> "LLMModel":
        """Claude 3.5 Haiku - fast and affordable."""
        return cls(
            provider=LLMProvider.ANTHROPIC,
            model_id="claude-3-5-haiku-20241022",
            name="Claude 3.5 Haiku",
            input_cost_per_million=0.80,
            output_cost_per_million=4.00,
            context_window=200000,
            supports_caching=True,
            cache_discount=0.90,
            quality_score=0.82,
            speed_score=0.98,
            notes="Very fast responses. Excellent for simple Q&A. "
                  "90% prompt caching discount is industry-leading."
        )

    @classmethod
    def groq_llama(cls) -> "LLMModel":
        """Groq Llama - ultra-fast, ultra-cheap."""
        return cls(
            provider=LLMProvider.GROQ,
            model_id="llama-3.3-70b-versatile",
            name="Llama 3.3 70B (Groq)",
            input_cost_per_million=0.59,
            output_cost_per_million=0.79,
            context_window=128000,
            supports_caching=False,
            cache_discount=0,
            quality_score=0.80,
            speed_score=1.00,
            notes="Fastest inference. Free tier with rate limits. "
                  "Good for high-volume, simple queries."
        )

    @classmethod
    def recommended_models(cls) -> list["LLMModel"]:
        """Get recommended models in order of preference."""
        return [
            cls.gpt4o_mini(),  # Primary recommendation
            cls.gemini_flash(),  # Alternative with free tier
            cls.claude_haiku(),  # Fast alternative
            cls.groq_llama(),  # Budget option
            cls.gpt4o(),  # Premium fallback
        ]


@dataclass
class InfrastructureComponent:
    """A component of the infrastructure stack."""
    name: str
    category: str  # hosting, llm, database, orchestration, etc.
    monthly_cost: float
    is_required: bool
    alternatives: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class InfrastructureStack:
    """Complete infrastructure stack specification."""
    hosting: HostingProvider
    llm_primary: LLMModel
    llm_fallback: Optional[LLMModel]
    orchestration: str  # n8n, custom, etc.
    database: Optional[str]  # MongoDB, SQLite, etc.
    additional_components: list[InfrastructureComponent] = field(default_factory=list)

    @property
    def total_monthly_cost(self) -> float:
        """Calculate total monthly infrastructure cost."""
        cost = self.hosting.monthly_cost
        # LLM costs estimated separately based on usage
        for component in self.additional_components:
            cost += component.monthly_cost
        return cost

    @property
    def complexity_score(self) -> int:
        """Overall setup complexity (1-10)."""
        base = self.hosting.setup_complexity
        if self.database:
            base += 1
        if self.llm_fallback:
            base += 1
        return min(10, base)

    def to_dict(self) -> dict:
        """Export stack as dictionary."""
        return {
            "hosting": {
                "provider": self.hosting.name,
                "region": self.hosting.region,
                "monthly_cost": self.hosting.monthly_cost,
                "specs": f"{self.hosting.cpu_cores} CPU, {self.hosting.ram_gb}GB RAM",
            },
            "llm": {
                "primary": self.llm_primary.name,
                "fallback": self.llm_fallback.name if self.llm_fallback else None,
            },
            "orchestration": self.orchestration,
            "database": self.database,
            "total_base_cost": self.total_monthly_cost,
            "complexity": self.complexity_score,
        }


def recommend_infrastructure(
    monthly_budget: float,
    latency_priority: bool = True,
    volume: int = 1500,
) -> InfrastructureStack:
    """
    Recommend infrastructure based on budget and requirements.

    Args:
        monthly_budget: Maximum monthly spend for infrastructure
        latency_priority: Whether low latency is critical
        volume: Expected monthly conversation volume

    Returns:
        Recommended InfrastructureStack
    """
    # Select hosting
    if monthly_budget == 0:
        hosting = HostingProvider.oracle_cloud_free()
    elif latency_priority and monthly_budget >= 5:
        hosting = HostingProvider.vultr_buenos_aires()
    elif monthly_budget >= 3.49:
        hosting = HostingProvider.hetzner_budget()
    else:
        hosting = HostingProvider.oracle_cloud_free()

    # Select LLM
    primary = LLMModel.gpt4o_mini()
    fallback = LLMModel.gemini_flash() if volume > 1000 else None

    return InfrastructureStack(
        hosting=hosting,
        llm_primary=primary,
        llm_fallback=fallback,
        orchestration="n8n (self-hosted, free)",
        database="SQLite" if volume < 5000 else "MongoDB",
    )
