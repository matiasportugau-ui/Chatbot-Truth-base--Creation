"""
File Watcher for real-time monitoring of file system changes
"""

from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class FileChangeHandler(FileSystemEventHandler):
    """Handler for file system events"""

    def __init__(self, callback: Callable[[str, str, Path], None]):
        """
        Initialize handler.

        Args:
            callback: Callback function(event_type, file_path)
        """
        self.callback = callback

    def on_created(self, event: FileSystemEvent):
        """Handle file creation"""
        if not event.is_directory:
            self.callback("created", str(Path(event.src_path)))

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification"""
        if not event.is_directory:
            self.callback("modified", str(Path(event.src_path)))

    def on_moved(self, event: FileSystemEvent):
        """Handle file move"""
        if not event.is_directory:
            self.callback("moved", str(Path(event.src_path)))

    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion"""
        if not event.is_directory:
            self.callback("deleted", str(Path(event.src_path)))


class FileWatcher:
    """
    Real-time file system watcher using watchdog
    """

    def __init__(self, workspace_path: str, callback: Callable[[str, str, Path], None]):
        """
        Initialize file watcher.

        Args:
            workspace_path: Path to watch
            callback: Callback function(event_type, file_path)
        """
        self.workspace_path = Path(workspace_path).resolve()
        self.callback = callback
        self.observer: Optional[Observer] = None
        self.handler: Optional[FileChangeHandler] = None

    def start(self, recursive: bool = True):
        """Start watching for file changes"""
        if self.observer and self.observer.is_alive():
            return

        self.handler = FileChangeHandler(self.callback)
        self.observer = Observer()
        self.observer.schedule(
            self.handler, str(self.workspace_path), recursive=recursive
        )
        self.observer.start()

    def stop(self):
        """Stop watching for file changes"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

    def is_running(self) -> bool:
        """Check if watcher is running"""
        return self.observer is not None and self.observer.is_alive()
