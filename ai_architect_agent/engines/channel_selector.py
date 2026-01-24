"""
Channel selection engine.

Selects and prioritizes channels based on business requirements.
"""

from dataclasses import dataclass
from typing import Optional

from ..models.channels import Channel, ChannelType
from ..models.architecture import ArchitectureConfig, ArchitectureTier


@dataclass
class ChannelRecommendation:
    """Recommendation for a specific channel."""
    channel: Channel
    recommended: bool
    priority_score: float  # 0-100
    reasoning: str
    implementation_order: int  # 1 = first to implement


class ChannelSelector:
    """
    Selects and prioritizes communication channels.

    Selection criteria:
    1. Business priority (user-specified)
    2. Cost effectiveness
    3. Implementation complexity
    4. Expected traffic share
    5. Integration synergies (Messenger + Instagram share codebase)
    """

    def __init__(self, config: ArchitectureConfig):
        self.config = config

    def _calculate_priority_score(self, channel: Channel) -> float:
        """
        Calculate normalized priority score (0-100).

        Factors:
        - User-specified priority (40%)
        - Traffic share (25%)
        - Cost effectiveness (20%)
        - Implementation effort (15%)
        """
        channel_type = channel.config.channel_type

        # Get user-specified priority
        priority_map = {
            ChannelType.WHATSAPP: self.config.whatsapp_priority,
            ChannelType.MESSENGER: self.config.messenger_priority,
            ChannelType.INSTAGRAM: self.config.instagram_priority,
            ChannelType.MERCADOLIBRE: self.config.mercadolibre_priority,
        }
        user_priority = priority_map.get(channel_type, 5) * 10  # Scale to 0-100

        # Traffic share score (higher share = higher score)
        traffic_score = channel.typical_traffic_share * 100

        # Cost effectiveness (lower cost = higher score)
        # Free channels get 100, paid channels scaled by cost
        base_cost = channel.config.cost.monthly_base
        per_msg = channel.config.cost.per_message_outbound
        if base_cost == 0 and per_msg == 0:
            cost_score = 100
        else:
            # Assume 1000 messages, normalize to 0-100
            estimated_cost = base_cost + (per_msg * 1000)
            cost_score = max(0, 100 - (estimated_cost * 2))

        # Implementation effort (lower hours = higher score)
        effort_score = max(0, 100 - channel.implementation_hours)

        # Weighted average
        score = (
            user_priority * 0.40 +
            traffic_score * 0.25 +
            cost_score * 0.20 +
            effort_score * 0.15
        )

        return round(score, 1)

    def select_channels(
        self,
        tier: ArchitectureTier,
    ) -> list[ChannelRecommendation]:
        """
        Select and prioritize channels based on tier.

        Tiers:
        - MINIMAL: WhatsApp only
        - STANDARD: WhatsApp + Messenger + Instagram
        - COMPLETE: All channels
        - ENTERPRISE: All channels with redundancy
        """
        all_channels = Channel.all_channels()
        recommendations = []

        for channel in all_channels:
            score = self._calculate_priority_score(channel)
            channel_type = channel.config.channel_type

            # Determine if channel is recommended for this tier
            if tier == ArchitectureTier.MINIMAL:
                recommended = channel_type == ChannelType.WHATSAPP
                reasoning = self._get_minimal_reasoning(channel)
            elif tier == ArchitectureTier.STANDARD:
                recommended = channel_type in [
                    ChannelType.WHATSAPP,
                    ChannelType.MESSENGER,
                    ChannelType.INSTAGRAM,
                ]
                reasoning = self._get_standard_reasoning(channel)
            else:  # COMPLETE or ENTERPRISE
                recommended = True
                reasoning = self._get_complete_reasoning(channel)

            # Set enabled status
            channel.config.enabled = recommended

            recommendations.append(ChannelRecommendation(
                channel=channel,
                recommended=recommended,
                priority_score=score,
                reasoning=reasoning,
                implementation_order=0,  # Set below
            ))

        # Sort by score and assign implementation order
        recommendations.sort(key=lambda r: r.priority_score, reverse=True)
        order = 1
        for rec in recommendations:
            if rec.recommended:
                rec.implementation_order = order
                order += 1

        return recommendations

    def _get_minimal_reasoning(self, channel: Channel) -> str:
        """Get reasoning for minimal tier."""
        if channel.config.channel_type == ChannelType.WHATSAPP:
            return (
                "WhatsApp handles 70%+ of customer communications in Uruguay. "
                "Service conversations are FREE since Nov 2024. Essential channel."
            )
        return (
            f"{channel.name} excluded in minimal tier. "
            "Add when WhatsApp foundation is stable."
        )

    def _get_standard_reasoning(self, channel: Channel) -> str:
        """Get reasoning for standard tier."""
        channel_type = channel.config.channel_type

        if channel_type == ChannelType.WHATSAPP:
            return (
                "Primary channel. 70% traffic share. "
                "Free service conversations make it highly cost-effective."
            )
        elif channel_type == ChannelType.MESSENGER:
            return (
                "Secondary channel. 15% traffic share. "
                "FREE via Graph API. Shares Facebook App with Instagram."
            )
        elif channel_type == ChannelType.INSTAGRAM:
            return (
                "Tertiary channel. 10% traffic share. "
                "FREE. Minimal additional effort since Messenger shares codebase."
            )
        else:
            return (
                f"{channel.name} excluded in standard tier. "
                "E-commerce integration adds complexity; defer to Phase 3."
            )

    def _get_complete_reasoning(self, channel: Channel) -> str:
        """Get reasoning for complete tier."""
        channel_type = channel.config.channel_type

        if channel_type == ChannelType.WHATSAPP:
            return "Primary channel. Essential for all tiers."
        elif channel_type == ChannelType.MESSENGER:
            return "FREE channel. Captures Facebook-originated inquiries."
        elif channel_type == ChannelType.INSTAGRAM:
            return "FREE channel. Visual-first for product discovery."
        else:
            return (
                "E-commerce integration. Critical for Mercado Libre sellers. "
                "Pre-sale questions automation drives conversion."
            )

    def get_implementation_order(
        self,
        recommendations: list[ChannelRecommendation],
    ) -> list[tuple[int, Channel, str]]:
        """
        Get channels in implementation order with reasoning.

        Returns:
            List of (order, channel, reasoning) tuples
        """
        ordered = [
            (rec.implementation_order, rec.channel, rec.reasoning)
            for rec in recommendations
            if rec.recommended
        ]
        return sorted(ordered, key=lambda x: x[0])

    def estimate_total_implementation(
        self,
        recommendations: list[ChannelRecommendation],
    ) -> dict:
        """
        Estimate total implementation effort.

        Returns:
            Dict with hours, weeks, and breakdown by channel
        """
        total_hours = 0
        breakdown = []

        for rec in recommendations:
            if rec.recommended:
                hours = rec.channel.implementation_hours
                total_hours += hours
                breakdown.append({
                    "channel": rec.channel.name,
                    "hours": hours,
                    "order": rec.implementation_order,
                })

        # Assume 20 hours/week development capacity
        weeks = (total_hours + 19) // 20

        return {
            "total_hours": total_hours,
            "estimated_weeks": weeks,
            "breakdown": sorted(breakdown, key=lambda x: x["order"]),
        }

    def generate_selection_report(
        self,
        recommendations: list[ChannelRecommendation],
    ) -> str:
        """Generate channel selection report."""
        lines = [
            "# Channel Selection Report",
            "",
            "## Selected Channels",
            "",
            "| Channel | Score | Order | Status |",
            "|---------|-------|-------|--------|",
        ]

        for rec in sorted(recommendations, key=lambda r: -r.priority_score):
            status = "Selected" if rec.recommended else "Deferred"
            order = str(rec.implementation_order) if rec.recommended else "-"
            lines.append(
                f"| {rec.channel.name} | {rec.priority_score:.1f} | "
                f"{order} | {status} |"
            )

        lines.extend([
            "",
            "## Detailed Analysis",
            "",
        ])

        for rec in sorted(recommendations, key=lambda r: -r.priority_score):
            lines.extend([
                f"### {rec.channel.name}",
                "",
                f"- **Priority Score:** {rec.priority_score:.1f}/100",
                f"- **Recommended:** {'Yes' if rec.recommended else 'No'}",
                f"- **Implementation Hours:** {rec.channel.implementation_hours}",
                f"- **Traffic Share:** {rec.channel.typical_traffic_share * 100:.0f}%",
                "",
                f"**Reasoning:** {rec.reasoning}",
                "",
            ])

        # Add implementation estimate
        estimate = self.estimate_total_implementation(recommendations)
        lines.extend([
            "## Implementation Estimate",
            "",
            f"- **Total Hours:** {estimate['total_hours']}",
            f"- **Estimated Weeks:** {estimate['estimated_weeks']}",
            "",
        ])

        return "\n".join(lines)
