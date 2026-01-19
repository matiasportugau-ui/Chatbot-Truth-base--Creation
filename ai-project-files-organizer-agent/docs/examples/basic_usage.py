"""
Basic usage examples for AI Files Organizer Agent
"""

from ai_files_organizer import FileOrganizerAgent

# Example 1: Organize existing files
def organize_example():
    """Organize all files in a workspace"""
    organizer = FileOrganizerAgent(workspace_path="/path/to/project")
    result = organizer.organize_existing_files()
    print(f"Organized {len(result.get('results', {}).get('successful', []))} files")


# Example 2: Suggest location for new file
def suggest_location_example():
    """Suggest location for a new file"""
    organizer = FileOrganizerAgent(workspace_path="/path/to/project")
    proposal = organizer.suggest_new_file_location("new_document.md")
    print(f"Suggested location: {proposal['proposed_location']}")


# Example 3: Detect outdated files
def detect_outdated_example():
    """Detect outdated files"""
    organizer = FileOrganizerAgent(workspace_path="/path/to/project")
    outdated = organizer.detect_outdated_files()
    print(f"Found {len(outdated)} outdated files")


if __name__ == "__main__":
    organize_example()
