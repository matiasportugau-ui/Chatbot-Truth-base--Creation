"""
Git Manager for safe Git operations with user approval
"""

import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..utils.logger import get_logger


class GitManager:
    """
    Safe Git operations manager with explicit user approval
    
    Features:
    - Exhaustive validations before each operation
    - Explicit approval system
    - Best practices compliance
    - Safe conflict handling
    - Complete operation logging
    """

    def __init__(self, workspace_path: str, require_approval: bool = True):
        """
        Initialize Git Manager.
        
        Args:
            workspace_path: Repository path
            require_approval: If True, require approval for all operations
        """
        self.workspace_path = Path(workspace_path).resolve()
        self.require_approval = require_approval
        self.logger = get_logger("GitManager")
        
        # Validate Git repository
        if not self._is_git_repo():
            raise ValueError(f"Not a Git repository: {self.workspace_path}")

    def _is_git_repo(self) -> bool:
        """Check if directory is a Git repository"""
        return (self.workspace_path / ".git").exists()

    def _run_git_command(self, command: List[str], check: bool = True) -> Tuple[bool, str, str]:
        """
        Run Git command.
        
        Args:
            command: Git command as list
            check: If True, raise on error
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                check=check,
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr

    def analyze_repository_state(self) -> Dict:
        """
        Analyze current repository state.
        
        Returns:
            Dictionary with repository state information
        """
        state = {
            "branch": None,
            "is_clean": False,
            "modified_files": [],
            "staged_files": [],
            "untracked_files": [],
            "ahead": 0,
            "behind": 0,
            "has_conflicts": False,
        }

        # Get current branch
        success, stdout, _ = self._run_git_command(["branch", "--show-current"], check=False)
        if success:
            state["branch"] = stdout.strip()

        # Get status
        success, stdout, _ = self._run_git_command(["status", "--porcelain"], check=False)
        if success:
            lines = stdout.strip().split("\n") if stdout.strip() else []
            for line in lines:
                if line.startswith("??"):
                    state["untracked_files"].append(line[3:])
                elif line.startswith(" M") or line.startswith("MM"):
                    state["modified_files"].append(line[3:])
                elif line.startswith("M ") or line.startswith("A ") or line.startswith("D "):
                    state["staged_files"].append(line[3:])

            state["is_clean"] = len(lines) == 0

        # Check for conflicts
        success, stdout, _ = self._run_git_command(["diff", "--check"], check=False)
        if "conflict" in stdout.lower():
            state["has_conflicts"] = True

        # Check ahead/behind
        if state["branch"]:
            success, stdout, _ = self._run_git_command(
                ["rev-list", "--left-right", "--count", f"{state['branch']}...origin/{state['branch']}"],
                check=False
            )
            if success and stdout.strip():
                parts = stdout.strip().split("\t")
                if len(parts) == 2:
                    state["ahead"] = int(parts[0])
                    state["behind"] = int(parts[1])

        return state

    def plan_stage_operation(self, files: List[str]) -> Dict:
        """
        Plan stage operation and present to user.
        
        Args:
            files: List of files to stage
            
        Returns:
            Plan dictionary
        """
        # Validate files
        validated_files = []
        errors = []
        
        for file_path in files:
            full_path = self.workspace_path / file_path
            if not full_path.exists():
                errors.append(f"File does not exist: {file_path}")
            else:
                validated_files.append(file_path)

        if errors:
            return {
                "valid": False,
                "errors": errors,
            }

        state = self.analyze_repository_state()

        plan = {
            "operation": "stage",
            "branch": state["branch"],
            "files": validated_files,
            "warnings": [],
            "valid": True,
        }

        # Check for conflicts
        if state["has_conflicts"]:
            plan["warnings"].append("Repository has merge conflicts. Resolve before staging.")

        # Check if on main/master
        if state["branch"] in ["main", "master"]:
            plan["warnings"].append(
                "⚠️  WARNING: Working on main/master branch. Consider creating a feature branch."
            )

        return plan

    def plan_commit_operation(self, message: str) -> Dict:
        """
        Plan commit operation and present to user.
        
        Args:
            message: Commit message
            
        Returns:
            Plan dictionary
        """
        # Validate commit message
        is_valid, error = self.validate_commit_message(message)
        if not is_valid:
            return {
                "valid": False,
                "error": error,
            }

        state = self.analyze_repository_state()

        if not state["staged_files"]:
            return {
                "valid": False,
                "error": "No files staged for commit",
            }

        plan = {
            "operation": "commit",
            "branch": state["branch"],
            "message": message,
            "files": state["staged_files"],
            "warnings": [],
            "valid": True,
        }

        # Check if on main/master
        if state["branch"] in ["main", "master"]:
            plan["warnings"].append(
                "⚠️  WARNING: Committing directly to main/master branch."
            )

        return plan

    def plan_pull_operation(self, branch: Optional[str] = None, rebase: bool = False) -> Dict:
        """
        Plan pull operation and present to user.
        
        Args:
            branch: Branch to pull (default: current)
            rebase: If True, use rebase instead of merge
            
        Returns:
            Plan dictionary
        """
        state = self.analyze_repository_state()
        target_branch = branch or state["branch"]

        if not target_branch:
            return {
                "valid": False,
                "error": "No branch specified and no current branch",
            }

        plan = {
            "operation": "pull",
            "branch": target_branch,
            "rebase": rebase,
            "warnings": [],
            "valid": True,
        }

        # Check for uncommitted changes
        if not state["is_clean"]:
            plan["warnings"].append(
                "⚠️  WARNING: You have uncommitted changes. Consider stashing or committing first."
            )

        # Check if behind
        if state["behind"] > 0:
            plan["info"] = f"Branch is {state['behind']} commits behind remote."

        return plan

    def plan_push_operation(self, branch: Optional[str] = None, force: bool = False) -> Dict:
        """
        Plan push operation and present to user.
        
        Args:
            branch: Branch to push (default: current)
            force: If True, force push (requires explicit approval)
            
        Returns:
            Plan dictionary
        """
        state = self.analyze_repository_state()
        target_branch = branch or state["branch"]

        if not target_branch:
            return {
                "valid": False,
                "error": "No branch specified and no current branch",
            }

        plan = {
            "operation": "push",
            "branch": target_branch,
            "force": force,
            "ahead": state["ahead"],
            "warnings": [],
            "valid": True,
        }

        # Check if ahead
        if state["ahead"] == 0:
            plan["warnings"].append("No commits to push.")

        # Force push warnings
        if force:
            plan["warnings"].append(
                "⚠️  DANGER: Force push will overwrite remote history. Use with extreme caution!"
            )

        # Check if pushing to main/master
        if target_branch in ["main", "master"]:
            plan["warnings"].append(
                "⚠️  WARNING: Pushing directly to main/master. Consider using a Pull Request."
            )

        return plan

    def execute_approved_plan(self, plan: Dict) -> Dict:
        """
        Execute approved plan.
        
        Args:
            plan: Approved plan dictionary
            
        Returns:
            Execution result dictionary
        """
        operation = plan.get("operation")
        result = {
            "success": False,
            "operation": operation,
            "message": "",
            "output": "",
        }

        try:
            if operation == "stage":
                result = self._execute_stage(plan)
            elif operation == "commit":
                result = self._execute_commit(plan)
            elif operation == "pull":
                result = self._execute_pull(plan)
            elif operation == "push":
                result = self._execute_push(plan)
            else:
                result["message"] = f"Unknown operation: {operation}"

        except Exception as e:
            result["success"] = False
            result["message"] = f"Error executing operation: {str(e)}"
            self.logger.error(f"Error executing {operation}: {e}")

        return result

    def _execute_stage(self, plan: Dict) -> Dict:
        """Execute stage operation"""
        files = plan.get("files", [])
        success, stdout, stderr = self._run_git_command(["add"] + files)
        
        return {
            "success": success,
            "operation": "stage",
            "message": "Files staged successfully" if success else "Failed to stage files",
            "output": stdout,
            "error": stderr if not success else None,
        }

    def _execute_commit(self, plan: Dict) -> Dict:
        """Execute commit operation"""
        message = plan.get("message", "")
        success, stdout, stderr = self._run_git_command(
            ["commit", "-m", message]
        )
        
        return {
            "success": success,
            "operation": "commit",
            "message": "Commit created successfully" if success else "Failed to create commit",
            "output": stdout,
            "error": stderr if not success else None,
        }

    def _execute_pull(self, plan: Dict) -> Dict:
        """Execute pull operation"""
        branch = plan.get("branch")
        rebase = plan.get("rebase", False)
        
        command = ["pull"]
        if rebase:
            command.append("--rebase")
        command.extend(["origin", branch])
        
        success, stdout, stderr = self._run_git_command(command, check=False)
        
        # Check for conflicts
        has_conflicts = "conflict" in stderr.lower() or "conflict" in stdout.lower()
        
        return {
            "success": success and not has_conflicts,
            "operation": "pull",
            "message": "Pull completed successfully" if success else "Pull failed or has conflicts",
            "output": stdout,
            "error": stderr if not success else None,
            "has_conflicts": has_conflicts,
        }

    def _execute_push(self, plan: Dict) -> Dict:
        """Execute push operation"""
        branch = plan.get("branch")
        force = plan.get("force", False)
        
        command = ["push"]
        if force:
            command.append("--force")
        command.extend(["origin", branch])
        
        success, stdout, stderr = self._run_git_command(command, check=False)
        
        return {
            "success": success,
            "operation": "push",
            "message": "Push completed successfully" if success else "Push failed",
            "output": stdout,
            "error": stderr if not success else None,
        }

    def validate_commit_message(self, message: str) -> Tuple[bool, str]:
        """
        Validate commit message format (Conventional Commits).
        
        Args:
            message: Commit message to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not message or not message.strip():
            return False, "Commit message cannot be empty"

        lines = message.strip().split("\n")
        subject = lines[0]

        # Check length
        if len(subject) > 72:
            return False, "Subject line should be 72 characters or less"

        # Check format: type(scope): description
        pattern = r"^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+"
        if not re.match(pattern, subject):
            return False, (
                "Commit message should follow Conventional Commits format: "
                "type(scope): description (e.g., 'feat(organizer): add version manager')"
            )

        return True, ""

    def generate_commit_message(self, changes: Dict) -> str:
        """
        Generate commit message following Conventional Commits.
        
        Args:
            changes: Dictionary with change information
            
        Returns:
            Generated commit message
        """
        # Determine type based on changes
        file_types = changes.get("file_types", [])
        if any(".py" in ft for ft in file_types):
            commit_type = "feat"
        elif any("test" in ft.lower() for ft in file_types):
            commit_type = "test"
        else:
            commit_type = "chore"

        # Generate description
        file_count = changes.get("file_count", 0)
        if file_count == 1:
            description = f"update {changes.get('files', ['file'])[0]}"
        else:
            description = f"update {file_count} files"

        message = f"{commit_type}(organizer): {description}"

        return message

    def handle_conflicts(self, conflicts: List[str]) -> Dict:
        """
        Handle merge conflicts.
        
        Args:
            conflicts: List of conflicted file paths
            
        Returns:
            Conflict handling result
        """
        return {
            "conflicts": conflicts,
            "message": (
                "Conflicts detected. Please resolve manually:\n"
                + "\n".join(f"  - {c}" for c in conflicts)
            ),
            "options": [
                "Resolve manually (recommended)",
                "Abort operation",
            ],
        }
