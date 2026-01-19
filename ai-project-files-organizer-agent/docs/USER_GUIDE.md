# User Guide

Complete guide to using AI Project Files Organizer Agent.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Configuration](#configuration)
4. [Advanced Features](#advanced-features)
5. [Best Practices](#best-practices)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from PyPI

```bash
pip install ai-files-organizer
```

### Install from Source

```bash
git clone https://github.com/your-username/ai-project-files-organizer-agent.git
cd ai-project-files-organizer-agent
pip install -e .
```

## Basic Usage

### Organize Existing Files

```bash
files-organizer organize /path/to/project
```

This will:
1. Scan all files in the project
2. Generate organization proposals
3. Request your approval
4. Apply approved changes

### Watch for New Files

```bash
files-organizer watch /path/to/project
```

This starts a monitoring process that:
- Watches for new files
- Suggests organization immediately
- Requests approval before moving files

### Scan Without Changes

```bash
files-organizer scan /path/to/project
```

This shows what would be organized without making any changes.

## Configuration

### Default Configuration

The agent uses a default configuration file. You can override it:

```python
from ai_files_organizer import FileOrganizerAgent

organizer = FileOrganizerAgent(
    workspace_path="/path/to/project",
    config_path="/path/to/custom_config.json"
)
```

### Configuration Options

```json
{
  "monitoring": {
    "realtime": true,
    "periodic_interval_hours": 24,
    "scan_on_startup": true
  },
  "versioning": {
    "format": "ddmm_vN",
    "auto_increment": true,
    "add_to_existing": true
  },
  "outdated_detection": {
    "days_threshold": 90,
    "check_content": true,
    "check_references": true
  },
  "folder_structure": {
    "rules_file": "folder_rules.json",
    "auto_create_folders": true
  },
  "approval": {
    "require_approval": true,
    "batch_mode": true,
    "timeout_seconds": 3600
  }
}
```

## Advanced Features

### Custom Folder Rules

Create a `folder_rules.json` file:

```json
{
  "rules": [
    {
      "category": "documentation",
      "extensions": [".md", ".txt"],
      "target_folder": "docs"
    }
  ]
}
```

### Version Management

Files are automatically versioned with format `ddmm_vN`:
- `dd`: Day (01-31)
- `mm`: Month (01-12)
- `vN`: Version number

Example: `Document_1601_v1.md`

### Outdated File Detection

The agent detects outdated files based on:
- Last modification date (>90 days by default)
- Duplicate content
- Missing references in code/docs

## Best Practices

1. **Start with a scan**: Use `scan` command first to see what would change
2. **Review proposals**: Always review proposals before approving
3. **Backup first**: Make sure you have backups before organizing
4. **Use version control**: Keep your project in Git
5. **Customize rules**: Adjust folder rules to match your project structure
