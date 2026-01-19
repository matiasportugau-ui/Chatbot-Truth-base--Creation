# API Reference

Complete API documentation for AI Project Files Organizer Agent.

## FileOrganizerAgent

Main agent class for organizing files.

### `__init__(workspace_path, config_path=None, require_approval=True)`

Initialize the agent.

**Parameters:**
- `workspace_path` (str): Path to workspace
- `config_path` (Path, optional): Path to config file
- `require_approval` (bool): Require approval for actions

### `organize_existing_files(interactive=True)`

Organize all existing files.

**Returns:** Dict with organization results

### `suggest_new_file_location(file_path)`

Suggest location for a new file.

**Parameters:**
- `file_path` (str): Path to file

**Returns:** Proposal dictionary

### `start_monitoring(interactive=True)`

Start real-time file monitoring.

### `stop_monitoring()`

Stop file monitoring.

### `detect_outdated_files()`

Detect outdated files.

**Returns:** List of outdated file reports

## FileScanner

Scans and categorizes files.

### `scan(recursive=True)`

Scan workspace for files.

**Returns:** List of FileMetadata objects

## VersionManager

Manages file versioning.

### `generate_version_code(date=None)`

Generate version code.

**Returns:** Version code string

### `add_version_to_filename(filename, date=None)`

Add version to filename.

**Returns:** Filename with version

## OutdatedDetector

Detects outdated files.

### `detect_outdated(files, workspace_path)`

Detect outdated files.

**Returns:** List of outdated file reports

## FolderStructureEngine

Generates organization proposals.

### `generate_proposal(file_meta, workspace_path)`

Generate proposal for a file.

**Returns:** Proposal dictionary

## ApprovalManager

Manages approval workflow.

### `request_approval(proposal, interactive=True)`

Request approval for proposal.

**Returns:** Approval result

## GitManager

Manages Git operations safely.

### `analyze_repository_state()`

Analyze repository state.

**Returns:** State dictionary

### `plan_stage_operation(files)`

Plan stage operation.

**Returns:** Plan dictionary

### `plan_commit_operation(message)`

Plan commit operation.

**Returns:** Plan dictionary

### `execute_approved_plan(plan)`

Execute approved plan.

**Returns:** Execution result
