#!/usr/bin/env python3
"""
GPT Knowledge Base Configuration Agent - Main Script
=====================================================

Main entry point for the GPT Knowledge Base Configuration and Evolution Agent.
"""

import argparse
import sys
from pathlib import Path
from loguru import logger

from .kb_config_agent import GPTKnowledgeBaseAgent


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    log_level = "DEBUG" if verbose else "INFO"
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="GPT Knowledge Base Configuration and Evolution Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze and review knowledge base
  python -m gpt_kb_config_agent.main analyze --kb-path Files/

  # Generate GPT configuration
  python -m gpt_kb_config_agent.main configure --kb-path Files/ --gpt-name "Panelin Assistant" --use-case assistant

  # Evolve knowledge base
  python -m gpt_kb_config_agent.main evolve --kb-path Files/ --strategy auto

  # Validate and fix issues
  python -m gpt_kb_config_agent.main validate --kb-path Files/
        """
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze and review knowledge base")
    analyze_parser.add_argument("--kb-path", type=str, required=True, help="Path to knowledge base files (Files folder)")
    analyze_parser.add_argument("--output-path", type=str, default=None, help="Output path for generated configurations")
    
    # Configure command
    configure_parser = subparsers.add_parser("configure", help="Generate GPT configuration")
    configure_parser.add_argument("--kb-path", type=str, required=True, help="Path to knowledge base files (Files folder)")
    configure_parser.add_argument("--output-path", type=str, default=None, help="Output path for generated configurations")
    configure_parser.add_argument("--gpt-name", type=str, required=True, help="Name for the GPT")
    configure_parser.add_argument("--use-case", type=str, default="general", 
                                 choices=["general", "quotation", "assistant"],
                                 help="Use case type")
    
    # Evolve command
    evolve_parser = subparsers.add_parser("evolve", help="Evolve knowledge base")
    evolve_parser.add_argument("--kb-path", type=str, required=True, help="Path to knowledge base files (Files folder)")
    evolve_parser.add_argument("--output-path", type=str, default=None, help="Output path for generated configurations")
    evolve_parser.add_argument("--strategy", type=str, default="auto",
                               choices=["auto", "conservative", "aggressive"],
                               help="Evolution strategy")
    evolve_parser.add_argument("--targets", type=str, nargs="+",
                               help="Target improvements")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate and fix knowledge base")
    validate_parser.add_argument("--kb-path", type=str, required=True, help="Path to knowledge base files (Files folder)")
    validate_parser.add_argument("--output-path", type=str, default=None, help="Output path for generated configurations")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize agent
    try:
        agent = GPTKnowledgeBaseAgent(
            knowledge_base_path=args.kb_path,
            output_path=args.output_path
        )
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == "analyze":
            logger.info("Starting knowledge base analysis...")
            report = agent.analyze_and_review()
            logger.success(f"Analysis complete! Health score: {report.get('health_score', 0):.1f}/100")
            logger.info(f"Report saved to: {agent.output_path / 'kb_analysis_report.json'}")
        
        elif args.command == "configure":
            logger.info(f"Generating GPT configuration: {args.gpt_name}")
            config = agent.configure_gpt(
                gpt_name=args.gpt_name,
                use_case=args.use_case
            )
            logger.success(f"GPT configuration generated!")
            logger.info(f"Config saved to: {agent.output_path / f'{args.gpt_name}_config.json'}")
        
        elif args.command == "evolve":
            logger.info(f"Starting knowledge base evolution (strategy: {args.strategy})")
            result = agent.evolve_knowledge_base(
                evolution_strategy=args.strategy,
                target_improvements=args.targets
            )
            logger.success(f"Evolution complete!")
            logger.info(f"Changes applied: {result['summary']['applied']}")
            logger.info(f"Changes recommended: {result['summary']['recommended']}")
            logger.info(f"Report saved to: {agent.output_path / 'kb_evolution_report.json'}")
        
        elif args.command == "validate":
            logger.info("Starting validation and auto-fix...")
            report = agent.validate_and_fix()
            logger.success(f"Validation complete!")
            logger.info(f"Conflicts detected: {report['conflicts_detected']}")
            logger.info(f"Fixes applied: {len(report['fixes_applied'])}")
            logger.info(f"Report saved to: {agent.output_path / 'validation_fix_report.json'}")
        
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
