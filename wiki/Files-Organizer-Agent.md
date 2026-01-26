# Files Organizer Agent

The Files Organizer Agent (`ai-project-files-organizer-agent/`) is an intelligent agent that automatically organizes project files with version management and Git integration.

---

## Overview

Located in `ai-project-files-organizer-agent/`, this agent provides:
- Automatic file organization into best-practice structures
- Version management with date-based naming (ddmm_vN)
- Outdated file detection
- Real-time monitoring for new files
- Approval workflow before changes
- Git integration (stage, commit, push)
- Automatic backups

---

## Features

| Feature | Description |
|---------|-------------|
| **Auto Organization** | Organizes files into standard folders |
| **Version Management** | Adds version codes to filenames |
| **Outdated Detection** | Identifies old/obsolete files |
| **Real-time Monitoring** | Watches for new files |
| **Approval Workflow** | Requests approval before changes |
| **Git Integration** | Safe Git operations |
| **Smart Categorization** | Auto-categorizes by type/content |
| **Backups** | Creates backups before moving |

---

## Installation

```bash
# From repository
cd ai-project-files-organizer-agent
pip install -e .

# Or from PyPI (when published)
pip install ai-files-organizer
```

---

## Quick Start

### CLI

```bash
# Organize existing files
files-organizer organize /path/to/project

# Watch for new files
files-organizer watch /path/to/project

# Scan without making changes
files-organizer scan /path/to/project
```

### Python API

```python
from ai_files_organizer import FileOrganizerAgent

# Initialize
organizer = FileOrganizerAgent(workspace_path="/path/to/project")

# Organize existing files
organizer.organize_existing_files()

# Start monitoring
organizer.start_monitoring()
```

---

## Target Structure

The agent organizes projects into this structure:

```
project_root/
├── docs/
│   ├── architecture/      # Architecture docs
│   ├── guides/            # User guides
│   ├── configuration/     # Config docs
│   └── knowledge_base/    # KB documentation
├── src/ or code/
│   ├── agents/            # Agent code
│   ├── validators/        # Validation code
│   └── utils/             # Utilities
├── data/
│   ├── training/          # Training data
│   ├── bundles/           # Data bundles
│   └── knowledge/         # KB files
├── config/                # Configuration files
├── output/                # Generated outputs
├── logs/                  # Log files
└── archived/              # Archived files
```

---

## Version Management

### Naming Format

Files are versioned with `ddmm_vN` format:

```
Original:     report.pdf
Versioned:    report_2301_v1.pdf
Next version: report_2301_v2.pdf
```

### Version Detection

```python
from ai_files_organizer.utils.validators import is_versioned, get_version

filename = "report_2301_v2.pdf"

print(is_versioned(filename))  # True
print(get_version(filename))   # 2
```

---

## Outdated Detection

The agent identifies outdated files based on:

| Criterion | Description |
|-----------|-------------|
| **Date** | Files older than threshold |
| **Content** | Superseded by newer versions |
| **References** | No longer referenced |
| **Naming** | Old naming conventions |

```python
from ai_files_organizer import OutdatedDetector

detector = OutdatedDetector(workspace_path=".")
outdated = detector.scan()

for file in outdated:
    print(f"{file['path']}: {file['reason']}")
```

---

## Git Integration

### Safe Operations

The agent performs Git operations with approval:

```python
from ai_files_organizer import FileOrganizerAgent

organizer = FileOrganizerAgent(
    workspace_path=".",
    git_enabled=True
)

# Organize and commit
organizer.organize_and_commit(
    message="chore: organize project files"
)
```

### Approval Workflow

```python
# With approval
organizer.organize_existing_files(require_approval=True)
# Shows preview, waits for confirmation

# Without approval (auto)
organizer.organize_existing_files(require_approval=False)
```

---

## Configuration

### Config File

Create `.files-organizer.yml`:

```yaml
workspace_path: .
output_path: organized/

rules:
  # File type mappings
  documentation:
    patterns:
      - "*.md"
      - "*.txt"
      - "*.pdf"
    target: docs/
  
  code:
    patterns:
      - "*.py"
      - "*.ts"
      - "*.js"
    target: src/
  
  data:
    patterns:
      - "*.json"
      - "*.csv"
      - "*.xml"
    target: data/

settings:
  versioning: true
  version_format: "ddmm_vN"
  backup: true
  backup_path: .backup/
  git_integration: true
  require_approval: true
```

### Custom Rules

```python
from ai_files_organizer import FileOrganizerAgent

organizer = FileOrganizerAgent(
    workspace_path=".",
    custom_rules={
        "kb_files": {
            "patterns": ["*_Base_*.json"],
            "target": "Files/knowledge/"
        },
        "training": {
            "patterns": ["*training*.json", "*training*.csv"],
            "target": "training_data/"
        }
    }
)
```

---

## Monitoring

### Real-time Watching

```python
from ai_files_organizer import FileOrganizerAgent

organizer = FileOrganizerAgent(workspace_path=".")

# Start monitoring (blocks)
organizer.start_monitoring()

# Or in background
import threading
monitor_thread = threading.Thread(target=organizer.start_monitoring)
monitor_thread.daemon = True
monitor_thread.start()
```

### Event Handlers

```python
def on_new_file(filepath, suggested_action):
    print(f"New file: {filepath}")
    print(f"Suggested: Move to {suggested_action['target']}")
    return True  # Approve

organizer.on_new_file = on_new_file
organizer.start_monitoring()
```

---

## Metrics

The agent tracks:

```python
from ai_files_organizer.utils.metrics import get_metrics

metrics = get_metrics()

print(f"Files organized: {metrics['files_organized']}")
print(f"Versions created: {metrics['versions_created']}")
print(f"Backups created: {metrics['backups_created']}")
print(f"Git commits: {metrics['git_commits']}")
```

---

## Components

| Component | File | Purpose |
|-----------|------|---------|
| Main Agent | `ai_files_organizer/` | Core agent |
| CLI | `cli.py` | Command-line interface |
| Validators | `utils/validators.py` | Validation utilities |
| Config Validator | `utils/config_validator.py` | Config validation |
| Metrics | `utils/metrics.py` | Usage tracking |
| Logger | `utils/logger.py` | Logging setup |

---

## Examples

### Basic Organization

```python
from ai_files_organizer import FileOrganizerAgent

organizer = FileOrganizerAgent(workspace_path=".")

# Scan first
scan_result = organizer.scan()
print(f"Files to organize: {len(scan_result['files'])}")

# Organize
organizer.organize_existing_files()
```

### With Custom Rules

See `docs/examples/custom_rules.py`:

```python
from ai_files_organizer import FileOrganizerAgent

organizer = FileOrganizerAgent(
    workspace_path=".",
    custom_rules={
        "panelin_configs": {
            "patterns": ["PANELIN_*.md", "PANELIN_*.txt"],
            "target": "docs/panelin/"
        }
    }
)

organizer.organize_existing_files()
```

---

## Related

- [[Agents-Overview]] - All agents
- [[Architecture]] - System architecture
- [[Contributing]] - How to contribute

---

<p align="center">
  <a href="[[KB-Config-Agent]]">← KB Config Agent</a> |
  <a href="[[Agents-Overview]]">Agents Overview →</a>
</p>
