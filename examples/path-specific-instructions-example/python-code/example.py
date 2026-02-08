"""
Example Python file demonstrating path-specific custom instructions.

This file follows the Python-specific guidelines defined in python.instructions.md
"""

from pathlib import Path
from typing import List, Optional, Dict
import json


def read_config_file(config_path: Path) -> Dict[str, any]:
    """Read and parse a JSON configuration file.
    
    Args:
        config_path: Path to the JSON configuration file
        
    Returns:
        Dictionary containing the parsed configuration
        
    Raises:
        ValueError: If file doesn't exist or is not valid JSON
        
    Example:
        >>> config = read_config_file(Path("config.json"))
        >>> print(config['app_name'])
        'MyApp'
    """
    if not config_path.exists():
        raise ValueError(f"Configuration file not found: {config_path}")
    
    try:
        with config_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")


def find_files_by_extension(
    directory: Path, 
    extension: str,
    recursive: bool = True
) -> List[Path]:
    """Find all files with the given extension in a directory.
    
    Uses pathlib for modern, cross-platform file operations.
    
    Args:
        directory: Directory to search
        extension: File extension to match (e.g., '.py', '.txt')
        recursive: Whether to search subdirectories (default: True)
        
    Returns:
        List of Path objects for matching files
        
    Raises:
        ValueError: If directory doesn't exist
        
    Example:
        >>> python_files = find_files_by_extension(Path("src"), ".py")
        >>> len(python_files)
        42
    """
    if not directory.exists():
        raise ValueError(f"Directory not found: {directory}")
    
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    
    # Use pathlib's glob with appropriate pattern
    pattern = f"**/*{extension}" if recursive else f"*{extension}"
    return [f for f in directory.glob(pattern) if f.is_file()]


def calculate_average(numbers: List[float]) -> Optional[float]:
    """Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numbers to average
        
    Returns:
        The average value, or None if list is empty
        
    Example:
        >>> calculate_average([1, 2, 3, 4, 5])
        3.0
        
        >>> calculate_average([])
        None
    """
    if not numbers:
        return None
    
    return sum(numbers) / len(numbers)


def format_file_size(size_bytes: int) -> str:
    """Convert file size in bytes to human-readable format.
    
    Uses modern Python f-strings for formatting.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB", "342 KB")
        
    Example:
        >>> format_file_size(1536)
        '1.5 KB'
        
        >>> format_file_size(2097152)
        '2.0 MB'
    """
    # Define size units using dict comprehension
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    
    size = float(size_bytes)
    for unit in units:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    
    return f"{size:.1f} PB"


if __name__ == "__main__":
    # Example usage demonstrating the functions
    print("Python Custom Instructions Example")
    print("=" * 40)
    
    # Test calculate_average
    numbers = [10, 20, 30, 40, 50]
    avg = calculate_average(numbers)
    print(f"Average of {numbers}: {avg}")
    
    # Test format_file_size
    sizes = [500, 1536, 1048576, 1073741824]
    print("\nFile size formatting:")
    for size in sizes:
        print(f"  {size} bytes = {format_file_size(size)}")
    
    # Test find_files_by_extension (current directory)
    current_dir = Path(".")
    py_files = find_files_by_extension(current_dir, ".py", recursive=False)
    print(f"\nPython files in current directory: {len(py_files)}")
