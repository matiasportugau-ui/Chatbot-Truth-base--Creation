"""
Main architecture generator engine.

Combines all components to generate complete chatbot architectures.
"""

from datetime import datetime
from typing import Optional

from ..models.architecture import (
    Architecture,
    ArchitectureConfig,
    ArchitectureTier,
    CostBreakdown,
)
from ..models.channels import Channel, ChannelType
from ..models.infrastructure import (
    InfrastructureStack,
    HostingProvider,
    LLMModel,
    recommend_infrastructure,
)
from .cost_optimizer import CostOptimizer
from .channel_selector import ChannelSelector
from .roadmap_builder import RoadmapBuilder


class ArchitectureGenerator:
    """
    Main engine for generating chatbot architectures.

    Orchestrates channel selection, infrastructure recommendation,
    cost optimization, and roadmap building.
    """

    VERSION = "1.0.0"

    def __init__(self, config: ArchitectureConfig):
        self.config = config
        self.channel_selector = ChannelSelector(config)

    def determine_tier(self) -> ArchitectureTier:
        """
        Determine appropriate architecture tier based on config.

        Criteria:
        - Budget
        - Channel priorities
        - Development hours available
        """
        budget = self.config.monthly_budget_max
        dev_hours = self.config.development_hours_available

        # Check if user wants all channels
        wants_all = (
            self.config.whatsapp_priority > 0 and
            self.config.messenger_priority > 0 and
            self.config.instagram_priority > 0 and
            self.config.mercadolibre_priority > 0
        )

        if budget < 30 or dev_hours < 40:
            return ArchitectureTier.MINIMAL
        elif budget < 60 and not wants_all:
            return ArchitectureTier.STANDARD
        elif budget < 100:
            return ArchitectureTier.COMPLETE
        else:
            return ArchitectureTier.ENTERPRISE

    def generate(
        self,
        tier: Optional[ArchitectureTier] = None,
    ) -> Architecture:
        """
        Generate complete architecture definition.

        Args:
            tier: Override tier selection (auto-detected if None)

        Returns:
            Complete Architecture object
        """
        # Determine tier
        if tier is None:
            tier = self.determine_tier()

        # Select channels
        recommendations = self.channel_selector.select_channels(tier)
        channels = [r.channel for r in recommendations]
        enabled_channels = [c for c in channels if c.config.enabled]

        # Recommend infrastructure
        infrastructure = recommend_infrastructure(
            monthly_budget=self.config.monthly_budget_max - 30,  # Reserve for API fees
            latency_priority=self.config.latency_sensitive,
            volume=self.config.monthly_conversations,
        )

        # Optimize costs
        optimizer = CostOptimizer(self.config)
        cost_breakdown, optimization_result = optimizer.optimize(
            channels,
            infrastructure,
        )

        # Build roadmap
        roadmap_builder = RoadmapBuilder(self.config, infrastructure)
        phases = roadmap_builder.build_roadmap(channels, tier)

        # Calculate totals
        total_hours = sum(p.development_hours for p in phases)
        total_weeks = sum(p.duration_weeks for p in phases)
        monthly_cost = cost_breakdown.total_with_contingency
        annual_savings = (190 - monthly_cost) * 12  # vs Botmaker

        # Generate diagram
        diagram = self._generate_diagram(enabled_channels, infrastructure)

        # Generate recommendations and risks
        recommendations_list = self._generate_recommendations(
            tier, optimization_result.optimizations_applied
        )
        risks = self._generate_risks(tier, infrastructure)
        alternatives = self._generate_alternatives(tier)

        return Architecture(
            name=f"{self.config.company_name} Chatbot Architecture",
            version=self.VERSION,
            created_at=datetime.now(),
            tier=tier,
            config=self.config,
            channels=channels,
            infrastructure=infrastructure,
            cost_breakdown=cost_breakdown,
            monthly_cost_estimate=round(monthly_cost, 2),
            annual_savings_vs_botmaker=round(annual_savings, 2),
            phases=phases,
            total_development_hours=total_hours,
            estimated_completion_weeks=total_weeks,
            diagram=diagram,
            recommendations=recommendations_list,
            risks=risks,
            alternatives=alternatives,
        )

    def _generate_diagram(
        self,
        channels: list[Channel],
        infrastructure: InfrastructureStack,
    ) -> str:
        """Generate ASCII architecture diagram."""
        channel_names = [c.name for c in channels]
        channels_str = " / ".join(channel_names)

        return f"""
+------------------+     +-------------------+     +------------------+
|    CUSTOMERS     | --> |   CHANNEL APIs    | --> |  WEBHOOK SERVER  |
+------------------+     +-------------------+     +------------------+
                         | {channels_str[:40].ljust(40)} |          |
                         +-------------------+     v
                                               +------------------+
                                               |    n8n (free)    |
                                               |   Orchestrator   |
                                               +------------------+
                                                        |
                              +-------------------------+-------------------------+
                              |                         |                         |
                              v                         v                         v
                    +------------------+      +------------------+      +------------------+
                    |   {infrastructure.llm_primary.name[:14].ljust(14)} |      |  Python Backend  |      |    Database      |
                    |    (LLM API)     |      | Quotation Engine |      | ({infrastructure.database or 'SQLite'})  |
                    +------------------+      +------------------+      +------------------+
                              |                         |
                              +-------------------------+
                                        |
                                        v
                              +------------------+
                              |    RESPONSE      |
                              | --> Customer     |
                              +------------------+

HOSTING: {infrastructure.hosting.name} ({infrastructure.hosting.region})
COST: ~${infrastructure.hosting.monthly_cost:.2f}/mo hosting + API fees
"""

    def _generate_recommendations(
        self,
        tier: ArchitectureTier,
        optimizations: list[str],
    ) -> list[str]:
        """Generate architecture recommendations."""
        recs = [
            "Start with WhatsApp alone; it handles 70%+ of traffic",
            "Use GPT-4o-mini for 90%+ of queries; reserve GPT-4o for edge cases",
            "Enable OpenAI prompt caching for 50% savings on repeated prompts",
            "Maximize customer-initiated WhatsApp messages (free) vs business-initiated (paid)",
        ]

        if tier == ArchitectureTier.MINIMAL:
            recs.append("Upgrade to Standard tier once WhatsApp is stable")

        if self.config.require_human_handoff:
            recs.append(
                "Consider Chatwoot (free, self-hosted) for unified human agent inbox"
            )

        if self.config.mercadolibre_priority > 5:
            recs.append(
                "Focus Mercado Libre automation on Questions API (pre-sale) for max conversion impact"
            )

        # Add optimizations as recommendations
        recs.extend(optimizations)

        return recs

    def _generate_risks(
        self,
        tier: ArchitectureTier,
        infrastructure: InfrastructureStack,
    ) -> list[str]:
        """Generate risk analysis."""
        risks = []

        # Hosting risks
        if infrastructure.hosting.monthly_cost == 0:
            risks.append(
                "Oracle Cloud Free: ARM instance availability may delay initial setup. "
                "Have Vultr Buenos Aires as backup ($5/mo)."
            )

        # WhatsApp risks
        risks.append(
            "WhatsApp verification can take 1-3 weeks. Start process early."
        )

        # Mercado Libre risks
        if tier in [ArchitectureTier.COMPLETE, ArchitectureTier.ENTERPRISE]:
            risks.append(
                "Mercado Libre may moderate AUTOMATIC_MESSAGE responses. "
                "Design contextual, non-templated replies."
            )

        # Technical risks
        if self.config.development_hours_available < 60:
            risks.append(
                "Limited development hours may extend timeline. "
                "Prioritize WhatsApp, defer other channels."
            )

        # Maintenance
        risks.append(
            "Budget 4-8 hours/month for ongoing maintenance and improvements."
        )

        return risks

    def _generate_alternatives(self, tier: ArchitectureTier) -> list[str]:
        """Generate alternative approaches."""
        alternatives = [
            "Botmaker ($190/mo): No development needed, but 4x more expensive",
            "ManyChat ($49-79/mo): Good for Messenger/Instagram, but no WhatsApp on free tier",
            "Twilio + SendGrid: More control but higher complexity and costs",
        ]

        if tier == ArchitectureTier.MINIMAL:
            alternatives.append(
                "360dialog BSP ($25/mo): Simpler WhatsApp setup if Meta direct proves difficult"
            )

        return alternatives


def generate_architecture(
    company_name: str = "Panelin BMC",
    country: str = "Uruguay",
    monthly_conversations: int = 1500,
    budget_min: float = 20.0,
    budget_max: float = 75.0,
    tier: Optional[ArchitectureTier] = None,
) -> Architecture:
    """
    Convenience function to generate architecture with common defaults.

    Args:
        company_name: Company name for the architecture
        country: Target country
        monthly_conversations: Expected monthly conversation volume
        budget_min: Minimum monthly budget
        budget_max: Maximum monthly budget
        tier: Override tier (auto-detected if None)

    Returns:
        Complete Architecture object
    """
    config = ArchitectureConfig(
        company_name=company_name,
        country=country,
        monthly_conversations=monthly_conversations,
        monthly_budget_min=budget_min,
        monthly_budget_max=budget_max,
    )

    generator = ArchitectureGenerator(config)
    return generator.generate(tier=tier)
