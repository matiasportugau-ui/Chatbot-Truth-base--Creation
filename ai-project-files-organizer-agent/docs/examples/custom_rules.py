"""
Custom rules examples
"""

from pathlib import Path
import json

# Example: Create custom folder rules
def create_custom_rules():
    """Create custom folder organization rules"""
    custom_rules = {
        "rules": [
            {
                "category": "documentation",
                "extensions": [".md", ".txt", ".rst"],
                "patterns": ["README", "GUIDE", "MANUAL"],
                "target_folder": "docs",
                "subfolders": {
                    "api": ["API", "REFERENCE"],
                    "guides": ["GUIDE", "TUTORIAL"],
                }
            },
            {
                "category": "tests",
                "extensions": [".py"],
                "patterns": ["test_", "_test"],
                "target_folder": "tests",
                "subfolders": {}
            }
        ],
        "default_folder": "misc"
    }
    
    rules_file = Path("custom_folder_rules.json")
    with open(rules_file, "w") as f:
        json.dump(custom_rules, f, indent=2)
    
    print(f"Created custom rules file: {rules_file}")
