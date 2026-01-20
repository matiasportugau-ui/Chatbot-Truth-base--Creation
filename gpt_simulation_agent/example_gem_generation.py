#!/usr/bin/env python3
"""
Example: Generate Google Labs Gems from GPT Configuration

This script demonstrates how to use the GPT Simulation Agent
to automatically generate Google Labs Gems from extracted configurations.
"""

import sys
from pathlib import Path

# Add agent_system to path
sys.path.insert(0, str(Path(__file__).parent))

from agent_system.gpt_simulation_agent import GPTSimulationAgent


def main():
    """Main example function"""
    # Get workspace path (parent directory)
    workspace_path = Path(__file__).parent.parent
    
    print("=" * 70)
    print("GPT Simulation Agent - Gem Generation Example")
    print("=" * 70)
    print(f"\nWorkspace: {workspace_path}")
    
    # Initialize agent
    print("\n[1/5] Initializing agent...")
    agent = GPTSimulationAgent(workspace_path=str(workspace_path))
    print("✓ Agent initialized")
    
    # Self-configure (extract configuration)
    print("\n[2/5] Running self-configuration...")
    try:
        config = agent.configure()
        print(f"✓ Configuration complete")
        print(f"  - Completion: {config.get('completion', 0):.1f}%")
        print(f"  - Files scanned: {len(config.get('diagnosis', {}).get('scanned_files', []))}")
    except Exception as e:
        print(f"⚠ Configuration error: {e}")
        return
    
    # Generate main Gem
    print("\n[3/5] Generating main Google Labs Gem...")
    try:
        gem_result = agent.generate_gems(generate_multiple=False)
        
        if "error" in gem_result:
            print(f"⚠ Error: {gem_result['error']}")
        else:
            gem = gem_result.get("gem", {})
            print(f"✓ Gem generated successfully")
            print(f"  - Type: {gem.get('gem_type', 'N/A')}")
            print(f"  - Valid: {gem.get('valido', False)}")
            
            if gem.get("gem_description"):
                print(f"\n📝 Gem Description for Google Labs:")
                print("-" * 70)
                print(gem["gem_description"][:500] + "..." if len(gem["gem_description"]) > 500 else gem["gem_description"])
    except Exception as e:
        print(f"⚠ Gem generation error: {e}")
        import traceback
        traceback.print_exc()
    
    # Generate multiple Gems
    print("\n[4/5] Generating multiple Gems for different use cases...")
    try:
        multiple_gems = agent.generate_gems(generate_multiple=True)
        
        if "error" in multiple_gems:
            print(f"⚠ Error: {multiple_gems['error']}")
        else:
            gems = multiple_gems.get("gems", [])
            print(f"✓ Generated {len(gems)} Gems")
            for i, gem_item in enumerate(gems, 1):
                print(f"  {i}. {gem_item.get('name', 'Unnamed Gem')}")
    except Exception as e:
        print(f"⚠ Multiple Gems generation error: {e}")
    
    # Generate Gem from training data (if available)
    print("\n[5/5] Generating Gem from training data patterns...")
    try:
        training_gem = agent.generate_gem_from_training()
        
        if "error" in training_gem:
            print(f"⚠ {training_gem['error']}")
            print("  (This is normal if no training data is available)")
        else:
            print(f"✓ Training-based Gem generated")
            if training_gem.get("gem_description"):
                print(f"\n📝 Training-based Gem Description:")
                print("-" * 70)
                print(training_gem["gem_description"][:500] + "..." if len(training_gem.get("gem_description", "")) > 500 else training_gem.get("gem_description", ""))
    except Exception as e:
        print(f"⚠ Training Gem generation error: {e}")
    
    print("\n" + "=" * 70)
    print("Gem Generation Example Completed!")
    print("=" * 70)
    print("\n📁 Check the 'output/generated_gems' directory for:")
    print("  - generated_gem.json - Main Gem from configuration")
    print("  - all_generated_gems.json - All generated Gems")
    print("  - training_based_gem.json - Gem from training data")
    print("\n💡 Next steps:")
    print("  1. Copy the 'gem_description' from the JSON files")
    print("  2. Go to gemini.google.com and click 'Gems'")
    print("  3. Click 'New Gem' and paste the description")
    print("  4. Review and test your Gem!")


if __name__ == "__main__":
    main()
