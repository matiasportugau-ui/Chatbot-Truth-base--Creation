"""
AI Architect Agent - Main orchestrator.

Generates optimal chatbot architectures using a functionalist,
cost-effective approach for multi-channel deployment.
"""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models.architecture import (
    Architecture,
    ArchitectureConfig,
    ArchitectureTier,
)
from .models.channels import Channel, ChannelType
from .models.infrastructure import (
    HostingProvider,
    LLMModel,
    InfrastructureStack,
)
from .engines.architecture_generator import ArchitectureGenerator
from .engines.cost_optimizer import CostOptimizer
from .engines.channel_selector import ChannelSelector
from .engines.roadmap_builder import RoadmapBuilder


class AIArchitectAgent:
    """
    AI Architect Agent for multi-channel chatbot deployment.

    This agent applies functionalist design principles to create
    cost-effective, production-ready chatbot architectures.

    Principles:
    1. Function over form - every component serves a purpose
    2. Cost efficiency - maximize value per dollar
    3. Incremental deployment - start simple, scale as needed
    4. Production reliability - no sleeping services, proper error handling
    """

    def __init__(
        self,
        config: Optional[ArchitectureConfig] = None,
        output_dir: Optional[Path] = None,
    ):
        """
        Initialize the AI Architect Agent.

        Args:
            config: Architecture configuration (uses defaults if None)
            output_dir: Directory for generated files (uses ./architectures if None)
        """
        self.config = config or self._default_config()
        self.output_dir = output_dir or Path("./architectures")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize engines
        self.generator = ArchitectureGenerator(self.config)
        self.optimizer = CostOptimizer(self.config)
        self.channel_selector = ChannelSelector(self.config)

    def _default_config(self) -> ArchitectureConfig:
        """Create default configuration for Uruguay construction e-commerce."""
        return ArchitectureConfig(
            company_name="Panelin BMC Uruguay",
            country="Uruguay",
            industry="construction_materials",
            monthly_conversations=1500,
            peak_conversations_per_hour=50,
            customer_initiated_ratio=0.70,
            whatsapp_priority=10,
            messenger_priority=6,
            instagram_priority=5,
            mercadolibre_priority=7,
            monthly_budget_min=25.0,
            monthly_budget_max=75.0,
            development_hours_available=80,
            prefer_free_hosting=True,
            latency_sensitive=True,
            require_human_handoff=True,
            has_existing_backend=True,
            backend_language="python",
        )

    def analyze(self) -> dict:
        """
        Analyze requirements and return insights.

        Returns:
            Dict with analysis results
        """
        tier = self.generator.determine_tier()
        recommendations = self.channel_selector.select_channels(tier)

        return {
            "recommended_tier": tier.value,
            "tier_reasoning": self._tier_reasoning(tier),
            "channels": [
                {
                    "name": r.channel.name,
                    "recommended": r.recommended,
                    "priority_score": r.priority_score,
                    "reasoning": r.reasoning,
                }
                for r in recommendations
            ],
            "estimated_budget": {
                "minimum": self.config.monthly_budget_min,
                "maximum": self.config.monthly_budget_max,
                "recommended": self._recommended_budget(tier),
            },
        }

    def _tier_reasoning(self, tier: ArchitectureTier) -> str:
        """Get reasoning for tier selection."""
        reasons = {
            ArchitectureTier.MINIMAL: (
                "Minimal tier selected due to budget constraints or limited "
                "development capacity. Focus on WhatsApp alone for 70% coverage."
            ),
            ArchitectureTier.STANDARD: (
                "Standard tier provides good balance of coverage (95% of traffic) "
                "and implementation effort. WhatsApp + Messenger + Instagram."
            ),
            ArchitectureTier.COMPLETE: (
                "Complete tier adds Mercado Libre for full e-commerce integration. "
                "Requires significant development investment but captures all channels."
            ),
            ArchitectureTier.ENTERPRISE: (
                "Enterprise tier includes redundancy, advanced monitoring, and "
                "scaling capabilities for high-volume deployments."
            ),
        }
        return reasons.get(tier, "")

    def _recommended_budget(self, tier: ArchitectureTier) -> float:
        """Get recommended monthly budget for tier."""
        budgets = {
            ArchitectureTier.MINIMAL: 25.0,
            ArchitectureTier.STANDARD: 45.0,
            ArchitectureTier.COMPLETE: 65.0,
            ArchitectureTier.ENTERPRISE: 100.0,
        }
        return budgets.get(tier, 50.0)

    def generate_architecture(
        self,
        tier: Optional[ArchitectureTier] = None,
    ) -> Architecture:
        """
        Generate complete architecture.

        Args:
            tier: Override tier (auto-detected if None)

        Returns:
            Complete Architecture object
        """
        return self.generator.generate(tier=tier)

    def compare_tiers(self) -> dict:
        """
        Compare all architecture tiers.

        Returns:
            Dict with tier comparisons
        """
        comparisons = {}

        for tier in ArchitectureTier:
            arch = self.generator.generate(tier=tier)
            comparisons[tier.value] = {
                "monthly_cost": arch.monthly_cost_estimate,
                "annual_cost": arch.monthly_cost_estimate * 12,
                "annual_savings_vs_botmaker": arch.annual_savings_vs_botmaker,
                "channels": len([c for c in arch.channels if c.config.enabled]),
                "development_hours": arch.total_development_hours,
                "implementation_weeks": arch.estimated_completion_weeks,
            }

        return comparisons

    def export_architecture(
        self,
        architecture: Architecture,
        format: str = "all",
    ) -> dict:
        """
        Export architecture to files.

        Args:
            architecture: Architecture to export
            format: Export format - "json", "markdown", "all"

        Returns:
            Dict with paths to exported files
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"architecture_{architecture.tier.value}_{timestamp}"
        exported = {}

        if format in ["json", "all"]:
            json_path = self.output_dir / f"{base_name}.json"
            with open(json_path, "w") as f:
                json.dump(architecture.to_dict(), f, indent=2, default=str)
            exported["json"] = str(json_path)

        if format in ["markdown", "all"]:
            md_path = self.output_dir / f"{base_name}.md"
            with open(md_path, "w") as f:
                f.write(architecture.to_markdown())
            exported["markdown"] = str(md_path)

        if format in ["summary", "all"]:
            summary_path = self.output_dir / f"{base_name}_summary.txt"
            with open(summary_path, "w") as f:
                f.write(architecture.generate_summary())
            exported["summary"] = str(summary_path)

        return exported

    def interactive_design(self) -> Architecture:
        """
        Interactive architecture design session.

        Guides user through configuration options and generates
        optimal architecture based on responses.

        Returns:
            Generated Architecture
        """
        print("\n" + "=" * 60)
        print("  AI ARCHITECT AGENT - Interactive Design Session")
        print("=" * 60)
        print("\nI'll help you design a cost-effective chatbot architecture.")
        print("Press Enter to use default values shown in [brackets].\n")

        # Company info
        company = input(f"Company name [{self.config.company_name}]: ").strip()
        if company:
            self.config.company_name = company

        # Volume
        try:
            volume = input(
                f"Expected monthly conversations [{self.config.monthly_conversations}]: "
            ).strip()
            if volume:
                self.config.monthly_conversations = int(volume)
        except ValueError:
            pass

        # Budget
        try:
            budget = input(
                f"Maximum monthly budget USD [{self.config.monthly_budget_max}]: "
            ).strip()
            if budget:
                self.config.monthly_budget_max = float(budget)
        except ValueError:
            pass

        # Channel priorities
        print("\nRate channel importance (1-10, 0 to disable):")
        for channel, attr in [
            ("WhatsApp", "whatsapp_priority"),
            ("Messenger", "messenger_priority"),
            ("Instagram", "instagram_priority"),
            ("Mercado Libre", "mercadolibre_priority"),
        ]:
            current = getattr(self.config, attr)
            try:
                priority = input(f"  {channel} [{current}]: ").strip()
                if priority:
                    setattr(self.config, attr, int(priority))
            except ValueError:
                pass

        # Generate
        print("\n" + "-" * 60)
        print("Generating optimal architecture...")
        print("-" * 60 + "\n")

        # Recreate generator with updated config
        self.generator = ArchitectureGenerator(self.config)
        architecture = self.generator.generate()

        # Display summary
        print(architecture.generate_summary())

        return architecture

    def quick_generate(
        self,
        company: str = "Panelin BMC",
        conversations: int = 1500,
        budget: float = 75.0,
    ) -> Architecture:
        """
        Quick architecture generation with minimal parameters.

        Args:
            company: Company name
            conversations: Monthly conversation volume
            budget: Maximum monthly budget

        Returns:
            Generated Architecture
        """
        self.config.company_name = company
        self.config.monthly_conversations = conversations
        self.config.monthly_budget_max = budget

        self.generator = ArchitectureGenerator(self.config)
        return self.generator.generate()

    def get_cost_report(self, architecture: Architecture) -> str:
        """Generate detailed cost analysis report."""
        # Get optimization result
        recommendations = self.channel_selector.select_channels(architecture.tier)
        channels = [r.channel for r in recommendations]
        _, optimization_result = self.optimizer.optimize(
            channels,
            architecture.infrastructure,
        )

        return self.optimizer.generate_cost_report(
            architecture.cost_breakdown,
            optimization_result,
        )

    def get_channel_report(self, architecture: Architecture) -> str:
        """Generate channel selection report."""
        recommendations = self.channel_selector.select_channels(architecture.tier)
        return self.channel_selector.generate_selection_report(recommendations)

    def get_roadmap_report(self, architecture: Architecture) -> str:
        """Generate implementation roadmap report."""
        roadmap_builder = RoadmapBuilder(
            self.config,
            architecture.infrastructure,
        )
        recommendations = self.channel_selector.select_channels(architecture.tier)
        channels = [r.channel for r in recommendations]
        phases = roadmap_builder.build_roadmap(channels, architecture.tier)
        return roadmap_builder.generate_roadmap_report(phases)


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Architect Agent - Generate chatbot architectures"
    )
    parser.add_argument(
        "--company",
        default="Panelin BMC",
        help="Company name",
    )
    parser.add_argument(
        "--conversations",
        type=int,
        default=1500,
        help="Expected monthly conversations",
    )
    parser.add_argument(
        "--budget",
        type=float,
        default=75.0,
        help="Maximum monthly budget (USD)",
    )
    parser.add_argument(
        "--tier",
        choices=["minimal", "standard", "complete", "enterprise"],
        help="Force specific architecture tier",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run interactive design session",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare all architecture tiers",
    )
    parser.add_argument(
        "--output",
        default="./architectures",
        help="Output directory for generated files",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "summary", "all"],
        default="all",
        help="Export format",
    )

    args = parser.parse_args()

    # Initialize agent
    config = ArchitectureConfig(
        company_name=args.company,
        monthly_conversations=args.conversations,
        monthly_budget_max=args.budget,
    )
    agent = AIArchitectAgent(
        config=config,
        output_dir=Path(args.output),
    )

    if args.interactive:
        architecture = agent.interactive_design()
    elif args.compare:
        comparisons = agent.compare_tiers()
        print("\nTier Comparison:")
        print("-" * 80)
        for tier, data in comparisons.items():
            print(f"\n{tier.upper()}:")
            print(f"  Monthly Cost: ${data['monthly_cost']:.2f}")
            print(f"  Annual Savings vs Botmaker: ${data['annual_savings_vs_botmaker']:.2f}")
            print(f"  Channels: {data['channels']}")
            print(f"  Development Hours: {data['development_hours']}")
            print(f"  Implementation Weeks: {data['implementation_weeks']}")
        return
    else:
        tier = ArchitectureTier(args.tier) if args.tier else None
        architecture = agent.generate_architecture(tier=tier)

    # Export
    exported = agent.export_architecture(architecture, format=args.format)

    print("\nArchitecture generated successfully!")
    print(f"\nExported files:")
    for fmt, path in exported.items():
        print(f"  {fmt}: {path}")

    # Print summary
    print("\n" + "=" * 60)
    print(architecture.generate_summary())


if __name__ == "__main__":
    main()
