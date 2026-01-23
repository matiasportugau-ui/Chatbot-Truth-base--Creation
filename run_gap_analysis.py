#!/usr/bin/env python3
"""
Wrapper script to run gap analysis diagnostic
"""
import sys
import os
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gpt_simulation_agent.agent_system.agent_gap_analysis import GapAnalysisEngine

def main():
    """Run gap analysis diagnostic"""
    print("=" * 70)
    print("GAP ANALYSIS DIAGNOSTIC")
    print("=" * 70)
    
    workspace_path = str(project_root)
    print(f"\nWorkspace: {workspace_path}\n")
    
    try:
        engine = GapAnalysisEngine(workspace_path)
        print("Analyzing gaps in knowledge base configuration...")
        
        analysis = engine.analyze()
        
        # Save results
        output_path = project_root / "diagnostico_gap_analysis.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Gap analysis completed!")
        print(f"Results saved to: {output_path}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("GAP ANALYSIS SUMMARY")
        print("=" * 70)
        
        completion = analysis.get("completion_percentage", 0)
        bar = "█" * int(completion / 5)
        print(f"\n📊 Completion: {bar:20s} {completion:.1f}%")
        
        print("\n✅ Extracted Fields:")
        extracted_fields = analysis.get("extracted_fields", [])
        for i, field in enumerate(extracted_fields[:15], 1):
            print(f"  {i}. {field}")
        if len(extracted_fields) > 15:
            print(f"  ... and {len(extracted_fields) - 15} more fields")
        
        print("\n❌ Missing Fields:")
        missing_fields = analysis.get("missing_fields", [])
        for i, gap in enumerate(missing_fields[:15], 1):
            print(f"  {i}. {gap.get('path', 'unknown')}")
        if len(missing_fields) > 15:
            print(f"  ... and {len(missing_fields) - 15} more fields")
        
        print("\n🔧 Extraction Requests:")
        requests = analysis.get("extraction_requests", {})
        
        auto = requests.get("auto_extractable", [])
        print(f"\n  🤖 Auto-extractable: {len(auto)}")
        for i, req in enumerate(auto[:5], 1):
            print(f"     {i}. {req.get('field', 'unknown')}")
        
        semi = requests.get("semi_automatic", [])
        print(f"\n  ⚙️  Semi-automatic: {len(semi)}")
        for i, req in enumerate(semi[:5], 1):
            print(f"     {i}. {req.get('field', 'unknown')}")
        
        manual = requests.get("manual_required", [])
        print(f"\n  ✋ Manual required: {len(manual)}")
        for i, req in enumerate(manual[:5], 1):
            print(f"     {i}. {req.get('field', 'unknown')}")
        
        print("\n📖 Manual Extraction Guides:")
        guides = analysis.get("manual_guides", [])
        print(f"  Total: {len(guides)} guides available")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error during gap analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
