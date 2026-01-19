# AI Project Files Organizer Agent

[![CI](https://github.com/your-username/ai-project-files-organizer-agent/workflows/CI/badge.svg)](https://github.com/your-username/ai-project-files-organizer-agent/actions)
[![Codecov](https://codecov.io/gh/your-username/ai-project-files-organizer-agent/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/ai-project-files-organizer-agent)
[![PyPI version](https://badge.fury.io/py/ai-files-organizer.svg)](https://badge.fury.io/py/ai-files-organizer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent AI agent that automatically organizes project files into best-practice folder structures with version management, outdated file detection, and intelligent categorization.

## Features

- 🗂️ **Automatic Organization**: Organizes files into best-practice folder structures
- 📅 **Version Management**: Adds version codes (ddmm_vN format) to filenames
- 🔍 **Outdated Detection**: Identifies outdated files based on date, content, and references
- 👁️ **Real-time Monitoring**: Watches for new files and suggests organization
- ✅ **Approval Workflow**: Requests approval before making changes
- 🔄 **Git Integration**: Safe Git operations (stage, commit, pull, push) with approval
- 📊 **Smart Categorization**: Automatically categorizes files by type and content
- ⚙️ **Configurable**: Customizable rules and folder structures
- 💾 **Automatic Backup**: Creates backups before moving files
- 🔒 **Security**: Path validation, permission checks, and workspace boundary enforcement
- 📈 **Metrics & Monitoring**: Tracks operations, approvals, and performance
- 🛡️ **Error Handling**: Specific exception handling with detailed error reporting
- ⚡ **Conflict Resolution**: Handles file name conflicts automatically

## Installation

### From PyPI (when published)

```bash
pip install ai-files-organizer
```

### From GitHub

```bash
pip install git+https://github.com/your-username/ai-project-files-organizer-agent.git
```

### Development Installation

```bash
git clone https://github.com/your-username/ai-project-files-organizer-agent.git
cd ai-project-files-organizer-agent
pip install -e .
```

## Quick Start

### CLI Usage

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

# Initialize agent
organizer = FileOrganizerAgent(workspace_path="/path/to/project")

# Organize existing files
organizer.organize_existing_files()

# Start monitoring for new files
organizer.start_monitoring()
```

## Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Complete usage guide
- **[API Reference](docs/API_REFERENCE.md)** - API documentation
- **[Contributing](CONTRIBUTING.md)** - How to contribute
- **[Examples](docs/examples/)** - Code examples

## Project Structure

The agent organizes projects into this structure:

```
project_root/
├── docs/
│   ├── architecture/
│   ├── guides/
│   ├── configuration/
│   └── knowledge_base/
├── src/ or code/
│   ├── agents/
│   ├── validators/
│   └── utils/
├── data/
│   ├── training/
│   ├── bundles/
│   └── knowledge/
├── config/
├── output/
├── logs/
└── archived/
```

## Requirements

- Python 3.8+
- See [requirements.txt](requirements.txt) for dependencies

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Roadmap

- [ ] Enhanced Git integration
- [ ] Custom rule engine
- [ ] Plugin system
- [ ] Web UI
- [ ] Integration with IDEs

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/your-username/ai-project-files-organizer-agent/issues)
- 💬 [Discussions](https://github.com/your-username/ai-project-files-organizer-agent/discussions)
