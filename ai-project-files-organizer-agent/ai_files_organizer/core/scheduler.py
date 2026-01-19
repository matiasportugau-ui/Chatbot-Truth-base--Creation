"""
Scheduler for periodic tasks
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional


class ScheduledTask:
    """Represents a scheduled task"""

    def __init__(
        self,
        name: str,
        task_func: Callable,
        interval_hours: float,
        last_run: Optional[datetime] = None,
    ):
        """
        Initialize scheduled task.

        Args:
            name: Task name
            task_func: Function to execute
            interval_hours: Hours between executions
            last_run: Last execution time
        """
        self.name = name
        self.task_func = task_func
        self.interval_hours = interval_hours
        self.last_run = last_run
        self.next_run = self._calculate_next_run()

    def _calculate_next_run(self) -> datetime:
        """Calculate next run time"""
        if self.last_run:
            return self.last_run + timedelta(hours=self.interval_hours)
        else:
            return datetime.now()

    def should_run(self) -> bool:
        """Check if task should run now"""
        return datetime.now() >= self.next_run

    def execute(self):
        """Execute task and update run time"""
        try:
            self.task_func()
            self.last_run = datetime.now()
            self.next_run = self._calculate_next_run()
        except Exception as e:
            print(f"Error executing task {self.name}: {e}")


class Scheduler:
    """
    Scheduler for periodic file organization tasks
    """

    def __init__(self):
        """Initialize scheduler"""
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def add_task(
        self,
        name: str,
        task_func: Callable,
        interval_hours: float,
    ):
        """
        Add a scheduled task.

        Args:
            name: Task name
            task_func: Function to execute
            interval_hours: Hours between executions
        """
        task = ScheduledTask(name, task_func, interval_hours)
        self.tasks[name] = task

    def remove_task(self, name: str):
        """Remove a scheduled task"""
        if name in self.tasks:
            del self.tasks[name]

    def start(self, check_interval_seconds: int = 3600):
        """
        Start scheduler.

        Args:
            check_interval_seconds: How often to check for tasks to run
        """
        if self.running:
            return

        self.running = True

        def run_scheduler():
            while self.running:
                for task in self.tasks.values():
                    if task.should_run():
                        task.execute()
                time.sleep(check_interval_seconds)

        self.thread = threading.Thread(target=run_scheduler, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def get_task_status(self) -> List[Dict]:
        """Get status of all tasks"""
        status = []
        for task in self.tasks.values():
            status.append(
                {
                    "name": task.name,
                    "last_run": task.last_run.isoformat() if task.last_run else None,
                    "next_run": task.next_run.isoformat(),
                    "interval_hours": task.interval_hours,
                }
            )
        return status
