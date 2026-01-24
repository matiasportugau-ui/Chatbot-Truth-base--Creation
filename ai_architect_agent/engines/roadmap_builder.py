"""
Implementation roadmap builder.

Creates phased implementation plans for chatbot deployment.
"""

from dataclasses import dataclass
from typing import Optional

from ..models.channels import Channel, ChannelType
from ..models.infrastructure import InfrastructureStack
from ..models.architecture import (
    ArchitectureConfig,
    ArchitectureTier,
    DeploymentPhase,
    ImplementationPhase,
)


class RoadmapBuilder:
    """
    Builds implementation roadmaps for chatbot deployment.

    Phases:
    1. Core infrastructure + WhatsApp (foundation)
    2. Messenger + Instagram (social expansion)
    3. Mercado Libre (e-commerce integration)
    4. Optimization + scaling (refinement)
    """

    def __init__(
        self,
        config: ArchitectureConfig,
        infrastructure: InfrastructureStack,
    ):
        self.config = config
        self.infrastructure = infrastructure

    def build_roadmap(
        self,
        channels: list[Channel],
        tier: ArchitectureTier,
    ) -> list[ImplementationPhase]:
        """
        Build complete implementation roadmap.

        Args:
            channels: Selected channels (enabled ones)
            tier: Architecture tier

        Returns:
            List of implementation phases
        """
        phases = []
        enabled_channels = [c for c in channels if c.config.enabled]
        channel_types = {c.config.channel_type for c in enabled_channels}

        # Phase 1: Always required - core infrastructure + WhatsApp
        phases.append(self._build_phase_1(
            has_whatsapp=ChannelType.WHATSAPP in channel_types
        ))

        # Phase 2: Messenger + Instagram (if included)
        if (ChannelType.MESSENGER in channel_types or
            ChannelType.INSTAGRAM in channel_types):
            phases.append(self._build_phase_2(
                has_messenger=ChannelType.MESSENGER in channel_types,
                has_instagram=ChannelType.INSTAGRAM in channel_types,
            ))

        # Phase 3: Mercado Libre (if included)
        if ChannelType.MERCADOLIBRE in channel_types:
            phases.append(self._build_phase_3())

        # Phase 4: Optimization (always included for standard+ tiers)
        if tier in [ArchitectureTier.STANDARD, ArchitectureTier.COMPLETE,
                    ArchitectureTier.ENTERPRISE]:
            phases.append(self._build_phase_4())

        # Calculate cumulative costs at each phase
        self._calculate_phase_costs(phases)

        return phases

    def _build_phase_1(self, has_whatsapp: bool) -> ImplementationPhase:
        """Phase 1: Core infrastructure and WhatsApp."""
        channels = []
        tasks = [
            "Provision cloud hosting (Oracle Cloud or Vultr)",
            "Install and configure n8n Community Edition",
            "Set up HTTPS with Let's Encrypt SSL",
            "Configure webhook endpoints",
            "Deploy Python quotation engine",
            "Integrate LLM API (GPT-4o-mini)",
        ]
        deliverables = [
            "Running n8n instance with HTTPS",
            "Python backend deployed and accessible",
            "LLM integration tested and working",
        ]

        if has_whatsapp:
            channels.append(ChannelType.WHATSAPP)
            tasks.extend([
                "Create Meta Business Account",
                "Register at developers.facebook.com",
                "Submit business verification",
                "Configure WhatsApp webhook in n8n",
                "Set up message templates",
                "Test end-to-end WhatsApp flow",
            ])
            deliverables.extend([
                "Verified WhatsApp Business account",
                "Working WhatsApp chatbot responding to messages",
                "Template messages configured for business-initiated contact",
            ])

        return ImplementationPhase(
            phase=DeploymentPhase.PHASE_1,
            name="Phase 1: Core Infrastructure + WhatsApp",
            description=(
                "Establish the foundation: cloud hosting, n8n orchestration, "
                "Python backend, and WhatsApp Business integration. This phase "
                "delivers a working chatbot handling 70% of expected traffic."
            ),
            duration_weeks=2,
            development_hours=40,
            channels=channels,
            tasks=tasks,
            deliverables=deliverables,
            dependencies=[],
        )

    def _build_phase_2(
        self,
        has_messenger: bool,
        has_instagram: bool,
    ) -> ImplementationPhase:
        """Phase 2: Messenger and Instagram."""
        channels = []
        tasks = [
            "Create Facebook App (if not existing from WhatsApp)",
            "Configure pages_messaging permission",
            "Prepare App Review demonstration video",
            "Submit for Facebook App Review",
        ]
        deliverables = [
            "Approved Facebook App with messaging permissions",
        ]

        if has_messenger:
            channels.append(ChannelType.MESSENGER)
            tasks.extend([
                "Link Facebook Page to App",
                "Configure Messenger webhook in n8n",
                "Implement Messenger-specific message formatting",
                "Test Messenger conversation flows",
            ])
            deliverables.append("Working Messenger chatbot")

        if has_instagram:
            channels.append(ChannelType.INSTAGRAM)
            tasks.extend([
                "Connect Instagram Business account to Facebook Page",
                "Configure Instagram webhook (shared with Messenger)",
                "Handle Instagram-specific media messages",
                "Test Instagram DM flows",
            ])
            deliverables.append("Working Instagram DM chatbot")

        # Synergy note
        if has_messenger and has_instagram:
            tasks.append(
                "Consolidate Messenger/Instagram handlers (shared codebase)"
            )

        return ImplementationPhase(
            phase=DeploymentPhase.PHASE_2,
            name="Phase 2: Messenger + Instagram",
            description=(
                "Expand to Facebook Messenger and Instagram. Both channels "
                "share the same Facebook App and similar integration patterns, "
                "making this a natural second phase. Adds ~25% traffic coverage."
            ),
            duration_weeks=1,
            development_hours=24,
            channels=channels,
            tasks=tasks,
            deliverables=deliverables,
            dependencies=["Phase 1 complete", "Facebook App Review approved"],
        )

    def _build_phase_3(self) -> ImplementationPhase:
        """Phase 3: Mercado Libre integration."""
        return ImplementationPhase(
            phase=DeploymentPhase.PHASE_3,
            name="Phase 3: Mercado Libre",
            description=(
                "Integrate with Mercado Libre's Questions and Messages APIs. "
                "This is the most complex integration due to OAuth requirements, "
                "message moderation, and two separate API systems."
            ),
            duration_weeks=2,
            development_hours=60,
            channels=[ChannelType.MERCADOLIBRE],
            tasks=[
                "Create Mercado Libre application",
                "Implement OAuth 2.0 authentication flow",
                "Set up token refresh mechanism (6-hour expiry)",
                "Configure Questions API webhook",
                "Configure Messages API webhook",
                "Implement 350-character message truncation",
                "Design contextual responses (avoid AUTOMATIC_MESSAGE flags)",
                "Test pre-sale question automation",
                "Test post-sale message handling",
                "Implement human escalation for complex issues",
                "Consider pursuing official ML certification",
            ],
            deliverables=[
                "Mercado Libre app with proper OAuth flow",
                "Automated pre-sale question responses",
                "Automated post-sale message handling",
                "Human escalation workflow",
            ],
            dependencies=["Phase 1 complete", "Seller account on ML"],
        )

    def _build_phase_4(self) -> ImplementationPhase:
        """Phase 4: Optimization and scaling."""
        return ImplementationPhase(
            phase=DeploymentPhase.PHASE_4,
            name="Phase 4: Optimization",
            description=(
                "Refine the chatbot based on real usage data. Implement "
                "monitoring, optimize costs, and prepare for scaling."
            ),
            duration_weeks=1,
            development_hours=20,
            channels=[],  # Optimization across all channels
            tasks=[
                "Analyze conversation logs for improvement opportunities",
                "Implement response caching for frequent questions",
                "Enable LLM prompt caching for cost reduction",
                "Set up monitoring and alerting",
                "Configure human handoff workflows (Chatwoot optional)",
                "Document operational procedures",
                "Create runbooks for common issues",
                "Performance test under expected load",
                "Review and optimize WhatsApp template usage",
            ],
            deliverables=[
                "Monitoring dashboard",
                "Response caching system",
                "Operational documentation",
                "Performance benchmarks",
            ],
            dependencies=["Phase 1-3 complete", "Real usage data collected"],
        )

    def _calculate_phase_costs(
        self,
        phases: list[ImplementationPhase],
    ) -> None:
        """Calculate cumulative monthly costs at each phase completion."""
        # Base infrastructure cost
        base_cost = self.infrastructure.hosting.monthly_cost

        # LLM cost estimate (rough, will vary by usage)
        llm_cost = self.infrastructure.llm_primary.estimate_cost(
            self.config.monthly_conversations
        )

        cumulative = base_cost + llm_cost

        for phase in phases:
            for channel_type in phase.channels:
                if channel_type == ChannelType.WHATSAPP:
                    # Estimate WhatsApp costs
                    wa_conversations = int(
                        self.config.monthly_conversations * 0.70
                    )
                    business_initiated = wa_conversations * (
                        1 - self.config.customer_initiated_ratio
                    )
                    # Mix of marketing and utility
                    wa_cost = business_initiated * 0.03  # Average rate
                    cumulative += wa_cost
                # Messenger, Instagram, ML are free

            phase.cost_at_completion = round(cumulative, 2)

    def generate_roadmap_report(
        self,
        phases: list[ImplementationPhase],
    ) -> str:
        """Generate implementation roadmap report."""
        total_hours = sum(p.development_hours for p in phases)
        total_weeks = sum(p.duration_weeks for p in phases)

        lines = [
            "# Implementation Roadmap",
            "",
            "## Overview",
            "",
            f"- **Total Phases:** {len(phases)}",
            f"- **Total Development Hours:** {total_hours}",
            f"- **Estimated Duration:** {total_weeks} weeks",
            "",
            "---",
            "",
        ]

        for phase in phases:
            lines.extend([
                f"## {phase.name}",
                "",
                f"**Duration:** {phase.duration_weeks} week(s) | "
                f"**Hours:** {phase.development_hours}",
                "",
                phase.description,
                "",
            ])

            if phase.channels:
                lines.append("**Channels:**")
                for ch in phase.channels:
                    lines.append(f"- {ch.value.title()}")
                lines.append("")

            if phase.dependencies:
                lines.append("**Dependencies:**")
                for dep in phase.dependencies:
                    lines.append(f"- {dep}")
                lines.append("")

            lines.append("**Tasks:**")
            for i, task in enumerate(phase.tasks, 1):
                lines.append(f"{i}. {task}")
            lines.append("")

            lines.append("**Deliverables:**")
            for deliverable in phase.deliverables:
                lines.append(f"- {deliverable}")
            lines.append("")

            lines.append(
                f"**Monthly Cost at Completion:** ${phase.cost_at_completion:.2f}"
            )
            lines.extend(["", "---", ""])

        return "\n".join(lines)

    def generate_gantt_ascii(
        self,
        phases: list[ImplementationPhase],
    ) -> str:
        """Generate ASCII Gantt chart."""
        lines = [
            "# Implementation Timeline",
            "",
            "```",
            "Week:  1   2   3   4   5   6",
            "       |---|---|---|---|---|",
        ]

        week = 0
        for phase in phases:
            bar_start = week
            bar_length = phase.duration_weeks
            week += bar_length

            # Create bar visualization
            bar = " " * bar_start + "=" * bar_length
            bar = bar.ljust(6)

            # Truncate phase name for display
            name = phase.name[:30].ljust(30)
            lines.append(f"{name} [{bar}]")

        lines.extend([
            "       |---|---|---|---|---|",
            "```",
        ])

        return "\n".join(lines)
