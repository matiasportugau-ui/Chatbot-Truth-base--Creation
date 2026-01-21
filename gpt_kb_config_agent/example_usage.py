#!/usr/bin/env python3
"""
Example Usage of GPT Knowledge Base Configuration Agent
=======================================================

Demonstrates how to use the agent to analyze, configure, and evolve GPT knowledge bases.
"""

from pathlib import Path
from gpt_kb_config_agent import GPTKnowledgeBaseAgent

# Example 1: Analyze Knowledge Base
print("=" * 70)
print("Example 1: Analyzing Knowledge Base")
print("=" * 70)

agent = GPTKnowledgeBaseAgent(
    knowledge_base_path="Files/",
    output_path="gpt_configs/"
)

# Perform comprehensive analysis
report = agent.analyze_and_review()

print(f"\n✅ Analysis Complete!")
print(f"Health Score: {report.get('health_score', 0):.1f}/100")
print(f"\nKnowledge Base Files Found: {len(report.get('knowledge_base_analysis', {}).get('files_found', []))}")
print(f"Conflicts Detected: {report.get('conflicts', {}).get('total_conflicts', 0)}")

# Show recommendations
recommendations = report.get('recommendations', [])
if recommendations:
    print(f"\n📋 Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")

# Example 2: Generate GPT Configuration
print("\n" + "=" * 70)
print("Example 2: Generating GPT Configuration")
print("=" * 70)

config = agent.configure_gpt(
    gpt_name="Panelin Technical Assistant",
    use_case="assistant"
)

print(f"\n✅ GPT Configuration Generated!")
print(f"Name: {config['name']}")
print(f"Use Case: {config['metadata']['use_case']}")
print(f"Knowledge Base Levels: {len(config['knowledge_base']['hierarchy'])}")
print(f"Capabilities: {list(config['capabilities'].keys())}")

# Example 3: Validate and Fix
print("\n" + "=" * 70)
print("Example 3: Validating Knowledge Base")
print("=" * 70)

validation = agent.validate_and_fix()

print(f"\n✅ Validation Complete!")
print(f"Conflicts Detected: {validation['conflicts_detected']}")
print(f"Fixes Applied: {len(validation['fixes_applied'])}")
print(f"Remaining Issues: {len(validation['remaining_issues'])}")

# Example 4: Evolve Knowledge Base
print("\n" + "=" * 70)
print("Example 4: Evolving Knowledge Base")
print("=" * 70)

evolution = agent.evolve_knowledge_base(
    evolution_strategy="conservative",  # Only recommend, don't apply
    target_improvements=["structure", "content"]
)

print(f"\n✅ Evolution Analysis Complete!")
print(f"Total Changes Identified: {evolution['summary']['total_changes']}")
print(f"Changes Recommended: {evolution['summary']['recommended']}")

if evolution['changes_recommended']:
    print(f"\n📋 Recommended Changes:")
    for i, change in enumerate(evolution['changes_recommended'][:5], 1):  # Show first 5
        print(f"  {i}. {change.get('description', 'N/A')}")
        print(f"     Priority: {change.get('priority', 'N/A')}")
        print(f"     Type: {change.get('type', 'N/A')}")

print("\n" + "=" * 70)
print("All examples completed! Check gpt_configs/ for output files.")
print("=" * 70)
