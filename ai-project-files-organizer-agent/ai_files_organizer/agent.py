"""
Main File Organizer Agent
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .core.file_scanner import FileScanner, FileMetadata
from .core.version_manager import VersionManager
from .core.outdated_detector import OutdatedDetector
from .core.folder_structure_engine import FolderStructureEngine
from .core.approval_manager import ApprovalManager
from .core.file_watcher import FileWatcher
from .core.scheduler import Scheduler
from .core.git_manager import GitManager
from .utils.logger import setup_logger
from .utils.validators import (
    validate_path,
    sanitize_filename,
    validate_write_permissions,
)
from .utils.metrics import MetricsCollector
from .utils.config_validator import ConfigValidator


class FileOrganizerAgent:
    """
    Main agent for organizing project files
    """

    def __init__(
        self,
        workspace_path: str,
        config_path: Optional[Path] = None,
        require_approval: bool = True,
    ):
        """
        Initialize File Organizer Agent.

        Args:
            workspace_path: Path to workspace to organize
            config_path: Path to configuration file
            require_approval: If True, require approval for all actions
        """
        self.workspace_path = Path(workspace_path).resolve()
        self.require_approval = require_approval

        # Validate workspace path
        is_valid, error = validate_path(str(self.workspace_path), must_exist=True)
        if not is_valid:
            raise ValueError(f"Invalid workspace path: {error}")

        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "default_config.json"
        self.config = self._load_config(config_path)

        # Setup logger
        log_file = self.workspace_path / ".files_organizer" / "logs" / "agent.log"
        self.logger = setup_logger("FileOrganizerAgent", log_file)

        # Initialize components
        self.scanner = FileScanner(str(self.workspace_path))
        self.version_manager = VersionManager(
            format_string=self.config.get("versioning", {}).get("format", "ddmm_vN"),
            auto_increment=self.config.get("versioning", {}).get("auto_increment", True),
        )
        self.outdated_detector = OutdatedDetector(
            days_threshold=self.config.get("outdated_detection", {}).get("days_threshold", 90),
            check_content=self.config.get("outdated_detection", {}).get("check_content", True),
            check_references=self.config.get("outdated_detection", {}).get("check_references", True),
        )
        
        # Load folder rules
        rules_file = Path(__file__).parent / "config" / "folder_rules.json"
        if self.config.get("folder_structure", {}).get("rules_file"):
            rules_file = self.workspace_path / self.config["folder_structure"]["rules_file"]
        
        self.folder_engine = FolderStructureEngine(rules_file=rules_file)
        
        history_file = self.workspace_path / ".files_organizer" / "approval_history.json"
        self.approval_manager = ApprovalManager(
            require_approval=self.require_approval,
            batch_mode=self.config.get("approval", {}).get("batch_mode", True),
            history_file=history_file,
        )

        self.file_watcher: Optional[FileWatcher] = None
        self.scheduler = Scheduler()

        # Initialize metrics collector
        metrics_file = (
            self.workspace_path / ".files_organizer" / "metrics.json"
        )
        self.metrics = MetricsCollector(metrics_file=metrics_file)

        # Initialize Git manager if repository
        self.git_manager: Optional[GitManager] = None
        try:
            if (self.workspace_path / ".git").exists():
                self.git_manager = GitManager(
                    str(self.workspace_path),
                    require_approval=self.require_approval,
                )
                self.logger.info("Git repository detected, GitManager initialized")
        except Exception as e:
            self.logger.warning(f"Could not initialize GitManager: {e}")

        self.logger.info(f"Initialized FileOrganizerAgent for {self.workspace_path}")

    def _load_config(self, config_path: Path) -> Dict:
        """Load and validate configuration from file"""
        if config_path.exists():
            is_valid, errors, config = ConfigValidator.validate_file(config_path)
            if is_valid:
                return config
            else:
                self.logger.warning(
                    f"Config validation errors: {', '.join(errors)}. Using defaults."
                )

        # Return default config
        default_config_path = Path(__file__).parent / "config" / "default_config.json"
        if default_config_path.exists():
            is_valid, errors, config = ConfigValidator.validate_file(
                default_config_path
            )
            if is_valid:
                return config
            else:
                self.logger.warning(
                    f"Default config validation errors: {', '.join(errors)}"
                )

        return {}

    def organize_existing_files(self, interactive: bool = True) -> Dict:
        """
        Organize all existing files in workspace.

        Args:
            interactive: If True, prompt for approvals interactively

        Returns:
            Organization results dictionary
        """
        # Start metrics tracking
        metrics = self.metrics.start_operation("organize_existing_files")
        self.logger.info("Starting organization of existing files")

        try:
            # Scan all files
            files = self.scanner.scan(recursive=True)
            self.logger.info(f"Scanned {len(files)} files")
            metrics.files_processed = len(files)

            # Generate proposals
            proposals = self.folder_engine.generate_batch_proposals(
                files, self.workspace_path
            )
            self.logger.info(f"Generated {len(proposals)} organization proposals")

            # Request batch approval
            approval_result = self.approval_manager.request_batch_approval(
                proposals, interactive=interactive
            )
            self.metrics.record_approval(
                approval_result.get("approved", False)
            )

            if not approval_result.get("approved", False):
                metrics.complete()
                return {
                    "success": False,
                    "message": "Organization not approved",
                    "proposals": proposals,
                }

            # Apply approved proposals
            approved_proposals = approval_result.get("approved_proposals", [])
            results = self._apply_proposals(approved_proposals, metrics)

            self.logger.info(
                f"Organized {len(results.get('successful', []))} files"
            )

            metrics.complete()
            self.metrics.save_metrics()

            return {
                "success": True,
                "proposals": proposals,
                "approved": approved_proposals,
                "results": results,
                "metrics": metrics.to_dict(),
            }
        except Exception as e:
            metrics.complete()
            self.logger.error(f"Error during organization: {e}", exc_info=True)
            raise

    def suggest_new_file_location(self, file_path: str) -> Dict:
        """
        Suggest location for a new file.

        Args:
            file_path: Path to new file

        Returns:
            Proposal dictionary
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            # Create temporary metadata for new file
            file_meta = FileMetadata(
                path=file_path_obj,
                name=file_path_obj.name,
                extension=file_path_obj.suffix.lower(),
                size=0,
                modified_time=datetime.now(),
                category="other",
                file_type="unknown",
            )
        else:
            # Scan the file
            file_meta = self.scanner._extract_metadata(file_path_obj)
            if not file_meta:
                return {"error": "Could not analyze file"}

        proposal = self.folder_engine.generate_proposal(file_meta, self.workspace_path)
        return proposal

    def _apply_proposals(
        self, proposals: List[Dict], metrics: Optional[object] = None
    ) -> Dict:
        """
        Apply approved proposals with backup, validation, and conflict handling.

        Args:
            proposals: List of approved proposals
            metrics: Optional metrics collector instance

        Returns:
            Dictionary with successful and failed operations
        """
        successful = []
        failed = []

        # Create backup directory
        backup_dir = (
            self.workspace_path
            / ".files_organizer"
            / "backups"
            / datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        backup_enabled = self.config.get("backup", {}).get("enabled", True)

        if backup_enabled:
            try:
                backup_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Backup directory created: {backup_dir}")
            except (OSError, PermissionError) as e:
                self.logger.warning(
                    f"Could not create backup directory: {e}. Continuing without backup."
                )
                backup_enabled = False

        for proposal in proposals:
            try:
                source_path = Path(proposal["file"])
                target_path = Path(proposal["proposed_location"])

                # Validate source path exists
                if not source_path.exists():
                    raise FileNotFoundError(f"Source file does not exist: {source_path}")

                # Validate source is readable
                if not os.access(source_path, os.R_OK):
                    raise PermissionError(f"Cannot read source file: {source_path}")

                # Validate workspace boundary
                is_valid, error = validate_path(
                    str(source_path),
                    must_exist=True,
                    workspace_root=self.workspace_path,
                )
                if not is_valid:
                    raise ValueError(f"Source path validation failed: {error}")

                # Create target directory if needed
                if self.config.get("folder_structure", {}).get(
                    "auto_create_folders", True
                ):
                    target_path.mkdir(parents=True, exist_ok=True)

                # Validate write permissions for target directory
                is_writable, write_error = validate_write_permissions(target_path)
                if not is_writable:
                    raise PermissionError(
                        f"Cannot write to target directory: {write_error}"
                    )

                # Move file
                if "move" in proposal["actions"]:
                    target_file = target_path / proposal["proposed_name"]

                    # Handle version codes if needed
                    if self.config.get("versioning", {}).get("add_to_existing", True):
                        final_name = self.version_manager.add_version_to_filename(
                            proposal["proposed_name"]
                        )
                        target_file = target_path / final_name
                    else:
                        target_file = target_path / proposal["proposed_name"]

                    # Handle name conflicts
                    if target_file.exists():
                        counter = 1
                        base_name = target_file.stem
                        extension = target_file.suffix
                        while target_file.exists():
                            target_file = (
                                target_path / f"{base_name}_{counter}{extension}"
                            )
                            counter += 1
                        self.logger.warning(
                            f"Target file exists, using alternative name: {target_file.name}"
                        )

                    # Create backup before moving
                    if backup_enabled and source_path.exists():
                        try:
                            backup_path = backup_dir / source_path.name
                            # Handle backup name conflicts too
                            backup_counter = 1
                            while backup_path.exists():
                                backup_path = (
                                    backup_dir
                                    / f"{source_path.stem}_{backup_counter}{source_path.suffix}"
                                )
                                backup_counter += 1
                            shutil.copy2(source_path, backup_path)
                            self.logger.info(
                                f"Backed up {source_path} to {backup_path}"
                            )
                        except (OSError, PermissionError) as e:
                            self.logger.warning(
                                f"Could not create backup for {source_path}: {e}"
                            )

                    # Move file
                    shutil.move(str(source_path), str(target_file))
                    successful.append(
                        {
                            "file": str(source_path),
                            "new_location": str(target_file),
                            "action": "moved",
                            "backup_location": (
                                str(backup_path) if backup_enabled else None
                            ),
                        }
                    )
                    self.logger.info(f"Moved {source_path} to {target_file}")

                    # Record metrics
                    if metrics:
                        self.metrics.record_file_operation(metrics, True)

            except (FileNotFoundError, PermissionError, OSError) as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                failed.append(
                    {
                        "file": str(proposal["file"]),
                        "error": error_msg,
                        "error_type": type(e).__name__,
                    }
                )
                self.logger.error(
                    f"Failed to apply proposal for {proposal['file']}: {error_msg}",
                    exc_info=True,
                )
                if metrics:
                    self.metrics.record_file_operation(metrics, False, error_msg)
            except ValueError as e:
                error_msg = f"Validation error: {str(e)}"
                failed.append(
                    {
                        "file": str(proposal["file"]),
                        "error": error_msg,
                        "error_type": "ValidationError",
                    }
                )
                self.logger.error(
                    f"Validation failed for {proposal['file']}: {error_msg}"
                )
                if metrics:
                    self.metrics.record_file_operation(metrics, False, error_msg)
            except Exception as e:
                # Catch-all for unexpected errors
                error_msg = f"Unexpected error: {str(e)}"
                failed.append(
                    {
                        "file": str(proposal["file"]),
                        "error": error_msg,
                        "error_type": type(e).__name__,
                    }
                )
                self.logger.critical(
                    f"Unexpected error processing {proposal['file']}: {e}",
                    exc_info=True,
                )
                if metrics:
                    self.metrics.record_file_operation(metrics, False, error_msg)

        return {"successful": successful, "failed": failed}

    def start_monitoring(self, interactive: bool = True):
        """Start real-time file monitoring"""
        if self.file_watcher:
            return

        def handle_file_event(event_type: str, file_path: str):
            """Handle file system events"""
            self.logger.info(f"File event: {event_type} - {file_path}")

            if event_type == "created":
                proposal = self.suggest_new_file_location(file_path)
                if proposal and not proposal.get("error"):
                    approval = self.approval_manager.request_approval(
                        proposal, interactive=interactive
                    )
                    if approval.get("approved"):
                        self._apply_proposals([proposal])

        self.file_watcher = FileWatcher(
            str(self.workspace_path), handle_file_event
        )
        self.file_watcher.start()

        # Setup periodic tasks
        if self.config.get("monitoring", {}).get("periodic_interval_hours"):
            interval = self.config["monitoring"]["periodic_interval_hours"]
            self.scheduler.add_task(
                "detect_outdated",
                self._periodic_outdated_detection,
                interval,
            )
            self.scheduler.start()

        self.logger.info("Started file monitoring")

    def stop_monitoring(self):
        """Stop real-time file monitoring"""
        if self.file_watcher:
            self.file_watcher.stop()
            self.file_watcher = None

        self.scheduler.stop()
        self.logger.info("Stopped file monitoring")

    def _periodic_outdated_detection(self):
        """Periodic task to detect outdated files"""
        self.logger.info("Running periodic outdated file detection")
        files = self.scanner.scan()
        outdated = self.outdated_detector.detect_outdated(files, self.workspace_path)
        
        if outdated:
            self.logger.info(f"Found {len(outdated)} outdated files")
            # Could trigger approval workflow here

    def detect_outdated_files(self) -> List[Dict]:
        """Detect outdated files"""
        files = self.scanner.scan()
        outdated = self.outdated_detector.detect_outdated(files, self.workspace_path)
        return outdated

    def stage_and_commit_changes(
        self,
        files: List[str],
        message: str,
        interactive: bool = True,
        auto_push: bool = False,
    ) -> Dict:
        """
        Stage and commit changes with approval workflow.

        Args:
            files: List of files to stage
            message: Commit message
            interactive: If True, prompt for approvals
            auto_push: If True, push after commit (requires approval)

        Returns:
            Dictionary with operation results
        """
        if not self.git_manager:
            return {
                "success": False,
                "error": "Not a Git repository or GitManager not initialized",
            }

        results = {}

        # Plan stage operation
        stage_plan = self.git_manager.plan_stage_operation(files)
        if not stage_plan.get("valid"):
            return {"success": False, "error": stage_plan.get("errors", ["Unknown error"])}

        # Request approval through ApprovalManager
        approval = self.approval_manager.request_approval(
            {
                "type": "git_stage",
                "plan": stage_plan,
                "description": f"Stage {len(files)} files for commit",
            },
            interactive=interactive,
        )

        if not approval.get("approved"):
            return {"success": False, "message": "Stage operation not approved"}

        # Execute stage
        stage_result = self.git_manager.execute_approved_plan(stage_plan)
        results["stage"] = stage_result

        if not stage_result.get("success"):
            return {"success": False, "results": results}

        # Plan commit operation
        commit_plan = self.git_manager.plan_commit_operation(message)
        if not commit_plan.get("valid"):
            return {"success": False, "error": commit_plan.get("error")}

        # Request approval for commit
        commit_approval = self.approval_manager.request_approval(
            {
                "type": "git_commit",
                "plan": commit_plan,
                "description": f"Commit with message: {message}",
            },
            interactive=interactive,
        )

        if not commit_approval.get("approved"):
            return {"success": False, "message": "Commit operation not approved"}

        # Execute commit
        commit_result = self.git_manager.execute_approved_plan(commit_plan)
        results["commit"] = commit_result

        # Optionally push
        if auto_push and commit_result.get("success"):
            push_plan = self.git_manager.plan_push_operation()
            if push_plan.get("valid"):
                push_approval = self.approval_manager.request_approval(
                    {
                        "type": "git_push",
                        "plan": push_plan,
                        "description": "Push changes to remote",
                    },
                    interactive=interactive,
                )
                if push_approval.get("approved"):
                    push_result = self.git_manager.execute_approved_plan(push_plan)
                    results["push"] = push_result

        return {"success": True, "results": results}

    def get_statistics(self) -> Dict:
        """Get operation statistics"""
        return self.metrics.get_statistics()
