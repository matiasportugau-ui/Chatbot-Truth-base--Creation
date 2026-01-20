#!/usr/bin/env python3
"""
Quick script to run the File Organizer Agent
"""

import sys
from pathlib import Path

# Add the package to path
package_path = Path(__file__).parent
sys.path.insert(0, str(package_path))

from ai_files_organizer import FileOrganizerAgent

def main():
    # Get workspace path from command line or use parent directory
    if len(sys.argv) > 1:
        workspace_path = sys.argv[1]
    else:
        # Default to parent directory
        workspace_path = str(Path(__file__).parent.parent)
    
    print(f"🚀 Initializing File Organizer Agent for: {workspace_path}")
    print("=" * 60)
    
    try:
        # Initialize agent
        agent = FileOrganizerAgent(
            workspace_path=workspace_path,
            require_approval=True
        )
        print("✅ Agent initialized successfully\n")
        
        # Scan files
        print("📊 Scanning files...")
        files = agent.scanner.scan(recursive=True)
        print(f"   Found {len(files)} files\n")
        
        # Detect outdated files
        print("🔍 Detecting outdated files...")
        outdated = agent.detect_outdated_files()
        if outdated:
            print(f"   ⚠️  Found {len(outdated)} outdated files:")
            for item in outdated[:5]:  # Show first 5
                print(f"      - {Path(item['file']).name}")
            if len(outdated) > 5:
                print(f"      ... and {len(outdated) - 5} more")
        else:
            print("   ✅ No outdated files detected")
        print()
        
        # Show statistics
        print("📈 Statistics:")
        stats = agent.get_statistics()
        print(f"   Total operations: {stats.get('total_operations', 0)}")
        print(f"   Files organized: {stats.get('total_files_organized', 0)}")
        print(f"   Approvals requested: {stats.get('total_approvals_requested', 0)}")
        print()
        
        # Ask if user wants to organize
        print("=" * 60)
        response = input("Would you like to organize files? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            print("\n🔄 Starting organization...")
            result = agent.organize_existing_files(interactive=True)
            
            if result.get("success"):
                successful = len(result.get("results", {}).get("successful", []))
                failed = len(result.get("results", {}).get("failed", []))
                print(f"\n✅ Organization complete!")
                print(f"   Successful: {successful}")
                print(f"   Failed: {failed}")
            else:
                print("\n❌ Organization was not completed")
        else:
            print("\n👋 Exiting without organizing")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
