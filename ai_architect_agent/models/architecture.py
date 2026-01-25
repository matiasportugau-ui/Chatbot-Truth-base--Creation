"""
Architecture definitions for multi-channel chatbot deployment.

Functionalist approach: Every component serves a clear purpose.
Cost-effective design: Minimize expenses while maximizing reliability.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from .channels import Channel, ChannelType, estimate_channel_costs
from .infrastructure import (
    InfrastructureStack,
    HostingProvider,
    LLMModel,
    recommend_infrastructure,
)


class ArchitectureTier(Enum):
    """Architecture complexity/cost tiers."""
    MINIMAL = "minimal"  # $20-30/month, WhatsApp only
    STANDARD = "standard"  # $40-60/month, WhatsApp + Messenger/Instagram
    COMPLETE = "complete"  # $60-80/month, All channels
    ENTERPRISE = "enterprise"  # $100+/month, High volume, redundancy


class DeploymentPhase(Enum):
    """Implementation phases."""
    PHASE_1 = "phase_1"  # Core infrastructure + WhatsApp
    PHASE_2 = "phase_2"  # Add Messenger + Instagram
    PHASE_3 = "phase_3"  # Add Mercado Libre
    PHASE_4 = "phase_4"  # Optimization + scaling


@dataclass
class ArchitectureConfig:
    """Configuration inputs for architecture generation."""
    # Business requirements
    company_name: str
    country: str = "Uruguay"
    industry: str = "construction_materials"

    # Volume expectations
    monthly_conversations: int = 1500
    peak_conversations_per_hour: int = 50
    customer_initiated_ratio: float = 0.70

    # Channel priorities (1-10, higher = more important)
    whatsapp_priority: int = 10
    messenger_priority: int = 6
    instagram_priority: int = 5
    mercadolibre_priority: int = 7

    # Budget constraints
    monthly_budget_min: float = 20.0
    monthly_budget_max: float = 75.0
    development_hours_available: int = 80

    # Technical preferences
    prefer_free_hosting: bool = True
    latency_sensitive: bool = True
    require_human_handoff: bool = True

    # Existing infrastructure
    has_existing_backend: bool = True  # Python quotation engine
    backend_language: str = "python"


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for architecture."""
    hosting: float = 0.0
    whatsapp_fees: float = 0.0
    messenger_fees: float = 0.0
    instagram_fees: float = 0.0
    mercadolibre_fees: float = 0.0
    llm_api: float = 0.0
    ssl_certificate: float = 0.0  # Let's Encrypt = free
    domain: float = 0.0  # Optional
    monitoring: float = 0.0  # Optional
    contingency: float = 0.0  # 10% buffer

    @property
    def total(self) -> float:
        return (
            self.hosting +
            self.whatsapp_fees +
            self.messenger_fees +
            self.instagram_fees +
            self.mercadolibre_fees +
            self.llm_api +
            self.ssl_certificate +
            self.domain +
            self.monitoring +
            self.contingency
        )

    @property
    def total_with_contingency(self) -> float:
        base = self.total - self.contingency
        return base * 1.10  # 10% contingency

    def to_table(self) -> list[tuple[str, float]]:
        """Return as list of (component, cost) tuples."""
        items = [
            ("Cloud Hosting", self.hosting),
            ("WhatsApp Business API", self.whatsapp_fees),
            ("Facebook Messenger", self.messenger_fees),
            ("Instagram DMs", self.instagram_fees),
            ("Mercado Libre", self.mercadolibre_fees),
            ("LLM API (OpenAI)", self.llm_api),
            ("SSL Certificate", self.ssl_certificate),
            ("Domain (optional)", self.domain),
            ("Monitoring (optional)", self.monitoring),
            ("Contingency (10%)", self.contingency),
        ]
        return [(name, cost) for name, cost in items if cost > 0 or name in [
            "Cloud Hosting", "WhatsApp Business API", "LLM API (OpenAI)"
        ]]


@dataclass
class ImplementationPhase:
    """A phase of the implementation roadmap."""
    phase: DeploymentPhase
    name: str
    description: str
    duration_weeks: int
    development_hours: int
    channels: list[ChannelType]
    tasks: list[str]
    deliverables: list[str]
    dependencies: list[str] = field(default_factory=list)
    cost_at_completion: float = 0.0


@dataclass
class Architecture:
    """
    Complete architecture definition for multi-channel chatbot.

    This is the primary output of the AI Architect Agent.
    """
    # Metadata
    name: str
    version: str
    created_at: datetime
    tier: ArchitectureTier
    config: ArchitectureConfig

    # Components
    channels: list[Channel]
    infrastructure: InfrastructureStack

    # Costs
    cost_breakdown: CostBreakdown
    monthly_cost_estimate: float
    annual_savings_vs_botmaker: float

    # Implementation
    phases: list[ImplementationPhase]
    total_development_hours: int
    estimated_completion_weeks: int

    # Architecture diagram (ASCII)
    diagram: str

    # Recommendations
    recommendations: list[str]
    risks: list[str]
    alternatives: list[str]

    def to_dict(self) -> dict:
        """Export architecture as dictionary."""
        return {
            "metadata": {
                "name": self.name,
                "version": self.version,
                "created_at": self.created_at.isoformat(),
                "tier": self.tier.value,
            },
            "config": {
                "company": self.config.company_name,
                "country": self.config.country,
                "monthly_conversations": self.config.monthly_conversations,
                "budget_range": f"${self.config.monthly_budget_min}-${self.config.monthly_budget_max}",
            },
            "channels": [
                {
                    "name": ch.name,
                    "enabled": ch.config.enabled,
                    "priority": ch.config.priority,
                    "traffic_share": f"{ch.typical_traffic_share * 100:.0f}%",
                }
                for ch in self.channels
            ],
            "infrastructure": self.infrastructure.to_dict(),
            "costs": {
                "monthly_estimate": self.monthly_cost_estimate,
                "annual_estimate": self.monthly_cost_estimate * 12,
                "botmaker_monthly": 190,
                "annual_savings": self.annual_savings_vs_botmaker,
                "breakdown": [
                    {"component": name, "cost": cost}
                    for name, cost in self.cost_breakdown.to_table()
                ],
            },
            "implementation": {
                "total_hours": self.total_development_hours,
                "weeks": self.estimated_completion_weeks,
                "phases": [
                    {
                        "name": p.name,
                        "duration_weeks": p.duration_weeks,
                        "hours": p.development_hours,
                        "channels": [c.value for c in p.channels],
                    }
                    for p in self.phases
                ],
            },
            "recommendations": self.recommendations,
            "risks": self.risks,
        }

    def generate_summary(self) -> str:
        """Generate human-readable architecture summary."""
        lines = [
            f"# {self.name}",
            f"Version: {self.version} | Tier: {self.tier.value.title()}",
            "",
            "## Cost Summary",
            f"- Monthly estimate: ${self.monthly_cost_estimate:.2f}",
            f"- Annual cost: ${self.monthly_cost_estimate * 12:.2f}",
            f"- vs Botmaker ($190/mo): Save ${self.annual_savings_vs_botmaker:.2f}/year",
            "",
            "## Channels",
        ]

        for ch in self.channels:
            status = "Enabled" if ch.config.enabled else "Disabled"
            lines.append(f"- {ch.name}: {status} (Priority {ch.config.priority})")

        lines.extend([
            "",
            "## Infrastructure",
            f"- Hosting: {self.infrastructure.hosting.name}",
            f"- Primary LLM: {self.infrastructure.llm_primary.name}",
            f"- Orchestration: {self.infrastructure.orchestration}",
            "",
            "## Implementation",
            f"- Total hours: {self.total_development_hours}",
            f"- Timeline: {self.estimated_completion_weeks} weeks",
            "",
            "## Architecture Diagram",
            self.diagram,
        ])

        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Export as detailed Markdown document."""
        md = [
            f"# {self.name}",
            "",
            f"**Version:** {self.version}  ",
            f"**Created:** {self.created_at.strftime('%Y-%m-%d')}  ",
            f"**Tier:** {self.tier.value.title()}  ",
            f"**Target:** {self.config.company_name} ({self.config.country})",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"This architecture deploys a multi-channel AI chatbot for "
            f"**{self.config.monthly_conversations:,} monthly conversations** "
            f"at approximately **${self.monthly_cost_estimate:.2f}/month**, "
            f"saving **${self.annual_savings_vs_botmaker:,.2f} annually** "
            f"compared to Botmaker ($190/month).",
            "",
            "---",
            "",
            "## Architecture Diagram",
            "",
            "```",
            self.diagram,
            "```",
            "",
            "---",
            "",
            "## Cost Breakdown",
            "",
            "| Component | Monthly Cost |",
            "|-----------|-------------|",
        ]

        for name, cost in self.cost_breakdown.to_table():
            md.append(f"| {name} | ${cost:.2f} |")

        md.extend([
            f"| **TOTAL** | **${self.monthly_cost_estimate:.2f}** |",
            "",
            "---",
            "",
            "## Channel Configuration",
            "",
        ])

        for ch in self.channels:
            md.extend([
                f"### {ch.name}",
                "",
                f"- **Status:** {'Enabled' if ch.config.enabled else 'Disabled'}",
                f"- **Priority:** {ch.config.priority}/10",
                f"- **Traffic Share:** {ch.typical_traffic_share * 100:.0f}%",
                f"- **Implementation Hours:** {ch.implementation_hours}",
                f"- **Notes:** {ch.config.cost.notes}",
                "",
            ])

        md.extend([
            "---",
            "",
            "## Infrastructure Stack",
            "",
            f"### Hosting: {self.infrastructure.hosting.name}",
            "",
            f"- **Region:** {self.infrastructure.hosting.region}",
            f"- **Cost:** ${self.infrastructure.hosting.monthly_cost:.2f}/month",
            f"- **Specs:** {self.infrastructure.hosting.cpu_cores} CPU, "
            f"{self.infrastructure.hosting.ram_gb}GB RAM, "
            f"{self.infrastructure.hosting.storage_gb}GB storage",
            f"- **Latency:** ~{self.infrastructure.hosting.latency_to_uruguay_ms}ms to Uruguay",
            f"- **Notes:** {self.infrastructure.hosting.notes}",
            "",
            f"### LLM: {self.infrastructure.llm_primary.name}",
            "",
            f"- **Model ID:** `{self.infrastructure.llm_primary.model_id}`",
            f"- **Input Cost:** ${self.infrastructure.llm_primary.input_cost_per_million}/1M tokens",
            f"- **Output Cost:** ${self.infrastructure.llm_primary.output_cost_per_million}/1M tokens",
            f"- **Caching:** {'Yes (' + str(int(self.infrastructure.llm_primary.cache_discount * 100)) + '% discount)' if self.infrastructure.llm_primary.supports_caching else 'No'}",
            f"- **Notes:** {self.infrastructure.llm_primary.notes}",
            "",
            f"### Orchestration: {self.infrastructure.orchestration}",
            "",
            "---",
            "",
            "## Implementation Roadmap",
            "",
        ])

        for phase in self.phases:
            md.extend([
                f"### {phase.name}",
                "",
                f"**Duration:** {phase.duration_weeks} week(s) | "
                f"**Hours:** {phase.development_hours}",
                "",
                f"{phase.description}",
                "",
                "**Tasks:**",
            ])
            for task in phase.tasks:
                md.append(f"- {task}")
            md.extend([
                "",
                "**Deliverables:**",
            ])
            for deliverable in phase.deliverables:
                md.append(f"- {deliverable}")
            md.append("")

        md.extend([
            "---",
            "",
            "## Recommendations",
            "",
        ])
        for rec in self.recommendations:
            md.append(f"1. {rec}")

        md.extend([
            "",
            "## Risks & Mitigations",
            "",
        ])
        for risk in self.risks:
            md.append(f"- {risk}")

        md.extend([
            "",
            "---",
            "",
            f"*Generated by AI Architect Agent v{self.version}*",
        ])

        return "\n".join(md)
