---
applyTo: "python-code/**/*.py"
---

# Python-Specific Custom Instructions

When writing Python code in this directory, always:

## Documentation
- Use type hints for all function parameters and return values
- Write docstrings in Google style format
- Include parameter descriptions, return types, and usage examples

## Code Style
- Follow PEP 8 naming conventions strictly
- Use descriptive variable names (no single letters except in comprehensions)
- Prefer explicit over implicit

## Modern Python Practices
- Use `pathlib.Path` instead of `os.path` for file operations
- Use list/dict comprehensions where they improve readability
- Use context managers (`with` statements) for resource management
- Prefer f-strings over `.format()` or `%` formatting

## Error Handling
- Use specific exception types
- Always include descriptive error messages
- Use early returns to avoid deep nesting

## Example Function Format

```python
from pathlib import Path
from typing import List, Optional

def process_files(directory: Path, pattern: str = "*.txt") -> List[str]:
    """Process all matching files in the given directory.
    
    Args:
        directory: Path to the directory to scan
        pattern: Glob pattern for file matching (default: "*.txt")
        
    Returns:
        List of processed file paths as strings
        
    Raises:
        ValueError: If directory doesn't exist
        
    Example:
        >>> process_files(Path("/tmp"), "*.log")
        ['/tmp/app.log', '/tmp/error.log']
    """
    if not directory.exists():
        raise ValueError(f"Directory not found: {directory}")
        
    return [str(f) for f in directory.glob(pattern)]
```
