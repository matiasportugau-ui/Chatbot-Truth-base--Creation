"""
Cost optimization engine for chatbot architecture.

Applies functionalist principles: maximize value per dollar spent.
"""

from dataclasses import dataclass
from typing import Optional

from ..models.channels import Channel, ChannelType, estimate_channel_costs
from ..models.infrastructure import (
    HostingProvider,
    LLMModel,
    InfrastructureStack,
)
from ..models.architecture import ArchitectureConfig, CostBreakdown


@dataclass
class OptimizationResult:
    """Result of cost optimization."""
    original_cost: float
    optimized_cost: float
    savings: float
    savings_percentage: float
    optimizations_applied: list[str]
    trade_offs: list[str]


class CostOptimizer:
    """
    Optimizes architecture costs while maintaining functionality.

    Principles:
    1. Free tiers first (Oracle Cloud, Gemini free tier)
    2. Pay only for what you use (WhatsApp service conversations)
    3. Cache aggressively (LLM prompt caching)
    4. Consolidate where possible (same FB app for Messenger/Instagram)
    """

    # Botmaker reference price for comparison
    BOTMAKER_MONTHLY = 190.0

    def __init__(self, config: ArchitectureConfig):
        self.config = config

    def calculate_channel_costs(
        self,
        channels: list[Channel],
    ) -> dict[ChannelType, float]:
        """Calculate monthly costs per channel."""
        costs = {}
        for channel in channels:
            if not channel.config.enabled:
                costs[channel.config.channel_type] = 0.0
                continue

            # Estimate traffic for this channel
            channel_conversations = int(
                self.config.monthly_conversations * channel.typical_traffic_share
            )

            cost_data = estimate_channel_costs(
                channel,
                channel_conversations,
                self.config.customer_initiated_ratio,
            )
            costs[channel.config.channel_type] = cost_data["total_monthly"]

        return costs

    def calculate_llm_costs(
        self,
        model: LLMModel,
        fallback: Optional[LLMModel] = None,
    ) -> float:
        """
        Calculate monthly LLM API costs.

        Assumes:
        - Average 500 input tokens per conversation
        - Average 300 output tokens per conversation
        - 30% cache hit ratio
        - 10% fallback usage if fallback model specified
        """
        primary_conversations = self.config.monthly_conversations
        if fallback:
            primary_conversations = int(primary_conversations * 0.90)
            fallback_conversations = int(self.config.monthly_conversations * 0.10)
            fallback_cost = fallback.estimate_cost(fallback_conversations)
        else:
            fallback_cost = 0.0

        primary_cost = model.estimate_cost(primary_conversations)
        return round(primary_cost + fallback_cost, 2)

    def calculate_hosting_costs(
        self,
        provider: HostingProvider,
    ) -> float:
        """Calculate monthly hosting costs."""
        return provider.monthly_cost

    def build_cost_breakdown(
        self,
        channels: list[Channel],
        infrastructure: InfrastructureStack,
    ) -> CostBreakdown:
        """Build complete cost breakdown."""
        channel_costs = self.calculate_channel_costs(channels)
        llm_cost = self.calculate_llm_costs(
            infrastructure.llm_primary,
            infrastructure.llm_fallback,
        )
        hosting_cost = self.calculate_hosting_costs(infrastructure.hosting)

        breakdown = CostBreakdown(
            hosting=hosting_cost,
            whatsapp_fees=channel_costs.get(ChannelType.WHATSAPP, 0.0),
            messenger_fees=channel_costs.get(ChannelType.MESSENGER, 0.0),
            instagram_fees=channel_costs.get(ChannelType.INSTAGRAM, 0.0),
            mercadolibre_fees=channel_costs.get(ChannelType.MERCADOLIBRE, 0.0),
            llm_api=llm_cost,
            ssl_certificate=0.0,  # Let's Encrypt is free
        )

        # Add 10% contingency
        breakdown.contingency = round(breakdown.total * 0.10, 2)

        return breakdown

    def optimize(
        self,
        channels: list[Channel],
        infrastructure: InfrastructureStack,
    ) -> tuple[CostBreakdown, OptimizationResult]:
        """
        Apply cost optimizations to architecture.

        Returns:
            Tuple of (optimized CostBreakdown, OptimizationResult)
        """
        # Calculate original costs
        original_breakdown = self.build_cost_breakdown(channels, infrastructure)
        original_cost = original_breakdown.total_with_contingency

        optimizations = []
        trade_offs = []

        # Optimization 1: Use free hosting if budget allows setup complexity
        if (infrastructure.hosting.monthly_cost > 0 and
            self.config.prefer_free_hosting):
            oracle = HostingProvider.oracle_cloud_free()
            if oracle.always_on:
                infrastructure.hosting = oracle
                optimizations.append(
                    f"Switched to Oracle Cloud Free tier (saves ${original_breakdown.hosting:.2f}/mo)"
                )
                trade_offs.append(
                    "ARM architecture may require container adjustments"
                )

        # Optimization 2: Use GPT-4o-mini instead of GPT-4o
        if infrastructure.llm_primary.model_id == "gpt-4o":
            old_cost = self.calculate_llm_costs(infrastructure.llm_primary)
            infrastructure.llm_primary = LLMModel.gpt4o_mini()
            new_cost = self.calculate_llm_costs(infrastructure.llm_primary)
            savings = old_cost - new_cost
            optimizations.append(
                f"Switched to GPT-4o-mini (saves ${savings:.2f}/mo)"
            )
            trade_offs.append(
                "Slightly lower reasoning capability for complex edge cases"
            )

        # Optimization 3: Leverage Gemini free tier for fallback
        if infrastructure.llm_fallback is None:
            infrastructure.llm_fallback = LLMModel.gemini_flash()
            optimizations.append(
                "Added Gemini Flash as fallback (has free tier of 1,500 req/day)"
            )

        # Optimization 4: Maximize customer-initiated WhatsApp conversations
        for channel in channels:
            if channel.config.channel_type == ChannelType.WHATSAPP:
                if self.config.customer_initiated_ratio < 0.70:
                    optimizations.append(
                        "Recommend designing flows to maximize customer-initiated "
                        "messages (free) vs business-initiated (paid)"
                    )

        # Optimization 5: Consolidate Messenger/Instagram under single app
        has_messenger = any(
            c.config.channel_type == ChannelType.MESSENGER and c.config.enabled
            for c in channels
        )
        has_instagram = any(
            c.config.channel_type == ChannelType.INSTAGRAM and c.config.enabled
            for c in channels
        )
        if has_messenger and has_instagram:
            optimizations.append(
                "Messenger and Instagram share single Facebook App (no extra setup)"
            )

        # Optimization 6: Use SQLite instead of MongoDB for low volume
        if (self.config.monthly_conversations < 5000 and
            infrastructure.database == "MongoDB"):
            infrastructure.database = "SQLite"
            optimizations.append(
                "Using SQLite instead of MongoDB (simpler, no extra cost)"
            )
            trade_offs.append(
                "Will need migration to MongoDB if volume exceeds 5,000/month"
            )

        # Recalculate optimized costs
        optimized_breakdown = self.build_cost_breakdown(channels, infrastructure)
        optimized_cost = optimized_breakdown.total_with_contingency

        savings = original_cost - optimized_cost
        savings_pct = (savings / original_cost * 100) if original_cost > 0 else 0

        result = OptimizationResult(
            original_cost=round(original_cost, 2),
            optimized_cost=round(optimized_cost, 2),
            savings=round(savings, 2),
            savings_percentage=round(savings_pct, 1),
            optimizations_applied=optimizations,
            trade_offs=trade_offs,
        )

        return optimized_breakdown, result

    def compare_to_botmaker(self, monthly_cost: float) -> dict:
        """Compare DIY cost to Botmaker's $190/month."""
        monthly_savings = self.BOTMAKER_MONTHLY - monthly_cost
        annual_savings = monthly_savings * 12

        # Calculate break-even on development time
        dev_hours = 60  # Conservative estimate for basic setup
        hourly_rate = 50  # Assumed developer rate
        dev_cost = dev_hours * hourly_rate
        break_even_months = dev_cost / monthly_savings if monthly_savings > 0 else float('inf')

        return {
            "botmaker_monthly": self.BOTMAKER_MONTHLY,
            "diy_monthly": monthly_cost,
            "monthly_savings": round(monthly_savings, 2),
            "annual_savings": round(annual_savings, 2),
            "break_even_months": round(break_even_months, 1),
            "five_year_savings": round(annual_savings * 5 - dev_cost, 2),
        }

    def generate_cost_report(
        self,
        breakdown: CostBreakdown,
        optimization_result: OptimizationResult,
    ) -> str:
        """Generate human-readable cost analysis report."""
        comparison = self.compare_to_botmaker(breakdown.total_with_contingency)

        lines = [
            "# Cost Analysis Report",
            "",
            "## Monthly Cost Breakdown",
            "",
            "| Component | Cost |",
            "|-----------|------|",
        ]

        for name, cost in breakdown.to_table():
            lines.append(f"| {name} | ${cost:.2f} |")

        lines.extend([
            f"| **Total (with 10% contingency)** | **${breakdown.total_with_contingency:.2f}** |",
            "",
            "## vs Botmaker Comparison",
            "",
            f"- Botmaker: ${comparison['botmaker_monthly']:.2f}/month",
            f"- This Architecture: ${comparison['diy_monthly']:.2f}/month",
            f"- **Monthly Savings: ${comparison['monthly_savings']:.2f}**",
            f"- **Annual Savings: ${comparison['annual_savings']:.2f}**",
            f"- Break-even: {comparison['break_even_months']:.1f} months",
            f"- 5-Year Net Savings: ${comparison['five_year_savings']:.2f}",
            "",
            "## Optimizations Applied",
            "",
        ])

        for opt in optimization_result.optimizations_applied:
            lines.append(f"- {opt}")

        if optimization_result.trade_offs:
            lines.extend([
                "",
                "## Trade-offs",
                "",
            ])
            for trade in optimization_result.trade_offs:
                lines.append(f"- {trade}")

        return "\n".join(lines)
