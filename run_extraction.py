#!/usr/bin/env python3
"""
Wrapper script to run agent extraction diagnostic
"""
import sys
import os
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gpt_simulation_agent.agent_system.utils.json_parser import JSONParser
from gpt_simulation_agent.agent_system.utils.markdown_parser import MarkdownParser
from gpt_simulation_agent.agent_system.agent_self_diagnosis import SelfDiagnosisEngine
from gpt_simulation_agent.agent_system.agent_extraction import ExtractionEngine

def main():
    """Run extraction diagnostic"""
    print("=" * 70)
    print("AGENT EXTRACTION DIAGNOSTIC")
    print("=" * 70)
    
    workspace_path = str(project_root)
    print(f"\nWorkspace: {workspace_path}\n")
    
    try:
        engine = ExtractionEngine(workspace_path)
        print("Extracting all available information...")
        
        extracted = engine.extract_all()
        
        # Save results
        output_path = project_root / "diagnostico_extraction.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extracted, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Extraction completed!")
        print(f"Results saved to: {output_path}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("EXTRACTION SUMMARY")
        print("=" * 70)
        
        print("\n📊 Confidence Scores:")
        for key, score in extracted.get("confidence_scores", {}).items():
            bar = "█" * int(score * 20)
            print(f"  {key:20s}: {bar:20s} {score:.2%}")
        
        print("\n📁 Knowledge Base Files Found:")
        kb_files = extracted.get("knowledge_base", {}).get("files", [])
        for i, file in enumerate(kb_files[:10], 1):
            print(f"  {i}. {Path(file).name}")
        if len(kb_files) > 10:
            print(f"  ... and {len(kb_files) - 10} more files")
        
        print("\n🎭 Identity:")
        identity = extracted.get("identity", {})
        if identity:
            for key, value in identity.items():
                print(f"  {key}: {value}")
        else:
            print("  ⚠️  No identity information extracted")
        
        print("\n📦 Products Found:")
        products = extracted.get("products", {})
        print(f"  Total: {len(products)} products")
        
        print("\n🧮 Formulas Found:")
        formulas = extracted.get("formulas", {})
        print(f"  Total: {len(formulas)} formulas")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
