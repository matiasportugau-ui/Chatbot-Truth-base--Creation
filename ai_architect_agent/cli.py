#!/usr/bin/env python3
"""
CLI interface for AI Architect Agent.

Usage:
    python -m ai_architect_agent.cli [options]

Examples:
    # Generate default architecture
    python -m ai_architect_agent.cli

    # Interactive mode
    python -m ai_architect_agent.cli --interactive

    # Compare all tiers
    python -m ai_architect_agent.cli --compare

    # Custom configuration
    python -m ai_architect_agent.cli --company "MyCompany" --budget 50 --conversations 2000
"""

import argparse
import sys
from pathlib import Path

from .models.architecture import ArchitectureConfig, ArchitectureTier
from .architect_agent import AIArchitectAgent


def print_header():
    """Print CLI header."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           AI ARCHITECT AGENT - Chatbot Architecture              ║
║                                                                  ║
║   Functionalist, cost-effective multi-channel deployment        ║
║   Target: $25-75/month (vs Botmaker $190/month)                  ║
╚══════════════════════════════════════════════════════════════════╝
""")


def print_architecture_summary(arch):
    """Print architecture summary to console."""
    print(f"""
┌─────────────────────────────────────────────────────────────────┐
│ {arch.name:^63} │
├─────────────────────────────────────────────────────────────────┤
│ Tier: {arch.tier.value.upper():<57} │
│ Monthly Cost: ${arch.monthly_cost_estimate:<51.2f} │
│ Annual Savings (vs Botmaker): ${arch.annual_savings_vs_botmaker:<33,.2f} │
├─────────────────────────────────────────────────────────────────┤
│ Channels:                                                       │
""")
    for ch in arch.channels:
        status = "✓" if ch.config.enabled else "○"
        print(f"│   {status} {ch.name:<58} │")

    print(f"""├─────────────────────────────────────────────────────────────────┤
│ Infrastructure:                                                 │
│   Hosting: {arch.infrastructure.hosting.name:<52} │
│   LLM: {arch.infrastructure.llm_primary.name:<56} │
│   Orchestration: {arch.infrastructure.orchestration:<46} │
├─────────────────────────────────────────────────────────────────┤
│ Implementation: {arch.total_development_hours} hours ({arch.estimated_completion_weeks} weeks){' ' * 35}│
└─────────────────────────────────────────────────────────────────┘
""")


def print_cost_breakdown(arch):
    """Print cost breakdown table."""
    print("\n📊 Cost Breakdown:")
    print("─" * 45)
    for name, cost in arch.cost_breakdown.to_table():
        print(f"  {name:<30} ${cost:>8.2f}")
    print("─" * 45)
    print(f"  {'TOTAL (with contingency)':<30} ${arch.monthly_cost_estimate:>8.2f}")
    print()


def print_tier_comparison(comparisons):
    """Print tier comparison table."""
    print("\n📈 Tier Comparison:")
    print("─" * 80)
    print(f"{'Tier':<12} {'Monthly':<12} {'Annual Save':<14} {'Channels':<10} {'Hours':<10} {'Weeks':<8}")
    print("─" * 80)

    for tier, data in comparisons.items():
        print(
            f"{tier:<12} "
            f"${data['monthly_cost']:<10.2f} "
            f"${data['annual_savings_vs_botmaker']:<12,.2f} "
            f"{data['channels']:<10} "
            f"{data['development_hours']:<10} "
            f"{data['implementation_weeks']:<8}"
        )
    print("─" * 80)
    print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Architect Agent - Generate optimal chatbot architectures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          Generate default architecture
  %(prog)s --interactive            Interactive configuration
  %(prog)s --compare                Compare all architecture tiers
  %(prog)s --tier minimal           Generate minimal tier
  %(prog)s --budget 50 --company X  Custom budget and company
        """,
    )

    # Configuration options
    config_group = parser.add_argument_group("Configuration")
    config_group.add_argument(
        "--company", "-c",
        default="Panelin BMC Uruguay",
        help="Company name (default: Panelin BMC Uruguay)",
    )
    config_group.add_argument(
        "--conversations", "-n",
        type=int,
        default=1500,
        help="Expected monthly conversations (default: 1500)",
    )
    config_group.add_argument(
        "--budget", "-b",
        type=float,
        default=75.0,
        help="Maximum monthly budget in USD (default: 75)",
    )
    config_group.add_argument(
        "--tier", "-t",
        choices=["minimal", "standard", "complete", "enterprise"],
        help="Force specific architecture tier",
    )

    # Mode options
    mode_group = parser.add_argument_group("Mode")
    mode_group.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run interactive design session",
    )
    mode_group.add_argument(
        "--compare",
        action="store_true",
        help="Compare all architecture tiers",
    )
    mode_group.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze requirements without generating",
    )

    # Output options
    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "--output", "-o",
        default="./architectures",
        help="Output directory for generated files",
    )
    output_group.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "summary", "all"],
        default="all",
        help="Export format (default: all)",
    )
    output_group.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output",
    )
    output_group.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output with all reports",
    )

    args = parser.parse_args()

    # Print header unless quiet
    if not args.quiet:
        print_header()

    # Initialize configuration
    config = ArchitectureConfig(
        company_name=args.company,
        monthly_conversations=args.conversations,
        monthly_budget_max=args.budget,
    )

    # Initialize agent
    agent = AIArchitectAgent(
        config=config,
        output_dir=Path(args.output),
    )

    # Handle different modes
    if args.interactive:
        architecture = agent.interactive_design()

    elif args.compare:
        comparisons = agent.compare_tiers()
        print_tier_comparison(comparisons)
        return 0

    elif args.analyze:
        analysis = agent.analyze()
        print("\n📋 Requirements Analysis:")
        print("─" * 50)
        print(f"Recommended Tier: {analysis['recommended_tier'].upper()}")
        print(f"Reasoning: {analysis['tier_reasoning']}")
        print(f"\nRecommended Budget: ${analysis['estimated_budget']['recommended']:.2f}/month")
        print("\nChannel Recommendations:")
        for ch in analysis['channels']:
            status = "✓ Recommended" if ch['recommended'] else "○ Deferred"
            print(f"  {ch['name']}: {status} (score: {ch['priority_score']:.1f})")
        return 0

    else:
        # Generate architecture
        tier = ArchitectureTier(args.tier) if args.tier else None
        architecture = agent.generate_architecture(tier=tier)

    # Display results
    if not args.quiet:
        print_architecture_summary(architecture)
        print_cost_breakdown(architecture)

    # Verbose output
    if args.verbose:
        print("\n" + "=" * 70)
        print("DETAILED REPORTS")
        print("=" * 70)

        print("\n" + agent.get_cost_report(architecture))
        print("\n" + agent.get_channel_report(architecture))
        print("\n" + agent.get_roadmap_report(architecture))

    # Export files
    exported = agent.export_architecture(architecture, format=args.format)

    if not args.quiet:
        print("\n📁 Exported Files:")
        for fmt, path in exported.items():
            print(f"  {fmt}: {path}")

    # Print recommendations
    if not args.quiet and architecture.recommendations:
        print("\n💡 Key Recommendations:")
        for i, rec in enumerate(architecture.recommendations[:5], 1):
            print(f"  {i}. {rec}")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
