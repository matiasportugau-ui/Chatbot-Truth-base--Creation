"""
Advanced usage examples
"""

from pathlib import Path
from ai_files_organizer import FileOrganizerAgent
from ai_files_organizer.core.git_manager import GitManager

# Example 1: Custom configuration
def custom_config_example():
    """Use custom configuration"""
    config_path = Path("/path/to/custom_config.json")
    organizer = FileOrganizerAgent(
        workspace_path="/path/to/project",
        config_path=config_path,
        require_approval=True
    )
    organizer.organize_existing_files()


# Example 2: Git integration
def git_integration_example():
    """Integrate with Git operations"""
    organizer = FileOrganizerAgent(workspace_path="/path/to/project")
    
    # Organize files
    result = organizer.organize_existing_files(interactive=False)
    
    if result.get("success"):
        # Initialize Git manager
        git_manager = GitManager(
            workspace_path="/path/to/project",
            require_approval=True
        )
        
        # Plan stage operation
        files = [r["new_location"] for r in result.get("results", {}).get("successful", [])]
        plan = git_manager.plan_stage_operation(files)
        
        if plan.get("valid"):
            # Execute if approved
            result = git_manager.execute_approved_plan(plan)
            print(f"Git operation: {result['message']}")


# Example 3: Monitoring mode
def monitoring_example():
    """Start monitoring for new files"""
    organizer = FileOrganizerAgent(workspace_path="/path/to/project")
    
    try:
        organizer.start_monitoring(interactive=True)
        # Keep running...
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        organizer.stop_monitoring()
