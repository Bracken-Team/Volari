from PyQt6.QtCore import QObject, pyqtSignal
from typing import List, Dict, Any, Callable
from enum import Enum
import logging

vollog = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a queued task."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class InvestigationTask:
    """Represents a single investigation task."""

    def __init__(self, task_id: str, name: str, plugin_name: str, func: Callable, *args, **kwargs):
        self.task_id = task_id
        self.name = name
        self.plugin_name = plugin_name
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.progress = 0

    def __repr__(self):
        return f"InvestigationTask({self.name}, {self.status.value})"


class InvestigationQueue(QObject):
    """Manages a queue of investigation tasks."""

    # Signals
    task_added = pyqtSignal(str)  # task_id
    task_started = pyqtSignal(str)  # task_id
    task_completed = pyqtSignal(str, object)  # task_id, result
    task_failed = pyqtSignal(str, str)  # task_id, error
    task_progress = pyqtSignal(str, int, str)  # task_id, percentage, message
    queue_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.tasks: Dict[str, InvestigationTask] = {}
        self.task_order: List[str] = []
        self.active_task_ids = set()

    def add_task(self, task: InvestigationTask):
        """Add a task to the queue."""
        self.tasks[task.task_id] = task
        self.task_order.append(task.task_id)
        self.task_added.emit(task.task_id)
        vollog.info(f"Added task to queue: {task.name}")

    def get_task(self, task_id: str) -> InvestigationTask:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[InvestigationTask]:
        """Get all tasks in order."""
        return [self.tasks[tid] for tid in self.task_order if tid in self.tasks]

    def get_pending_tasks(self) -> List[InvestigationTask]:
        """Get all pending tasks."""
        return [task for task in self.get_all_tasks() if task.status == TaskStatus.PENDING]

    def get_completed_tasks(self) -> List[InvestigationTask]:
        """Get all completed tasks."""
        return [task for task in self.get_all_tasks() if task.status == TaskStatus.COMPLETED]

    def mark_started(self, task_id: str):
        """Mark a task as started."""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.RUNNING
            self.active_task_ids.add(task_id)
            self.task_started.emit(task_id)
            vollog.info(f"Task started: {self.tasks[task_id].name}")

    def mark_completed(self, task_id: str, result: Any):
        """Mark a task as completed."""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.COMPLETED
            # Don't store large results - they're emitted via signal immediately
            # This prevents memory bloat from accumulated results
            self.tasks[task_id].result = None  # Result is passed via signal, don't cache
            self.tasks[task_id].progress = 100
            if task_id in self.active_task_ids:
                self.active_task_ids.remove(task_id)
            self.task_completed.emit(task_id, result)
            vollog.info(f"Task completed: {self.tasks[task_id].name}")

            # Check if all tasks are done
            if all(task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                   for task in self.get_all_tasks()):
                self.queue_completed.emit()
                vollog.info("All investigation tasks completed")

    def clear_completed_tasks(self):
        """Remove completed tasks from the queue to free memory."""
        import gc
        completed_ids = [tid for tid, task in self.tasks.items()
                        if task.status == TaskStatus.COMPLETED]
        for tid in completed_ids:
            if tid in self.task_order:
                self.task_order.remove(tid)
            del self.tasks[tid]
        gc.collect()
        vollog.info(f"Cleared {len(completed_ids)} completed tasks")

    def mark_failed(self, task_id: str, error: str):
        """Mark a task as failed."""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.FAILED
            self.tasks[task_id].error = error
            if task_id in self.active_task_ids:
                self.active_task_ids.remove(task_id)
            self.task_failed.emit(task_id, error)
            vollog.error(f"Task failed: {self.tasks[task_id].name} - {error}")

            # Check if all tasks are done
            if all(task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                   for task in self.get_all_tasks()):
                self.queue_completed.emit()

    def update_progress(self, task_id: str, percentage: int, message: str = ""):
        """Update task progress."""
        if task_id in self.tasks:
            # Clamp percentage to valid range (0-100)
            clamped_percentage = max(0, min(100, percentage)) if percentage != -1 else -1
            self.tasks[task_id].progress = clamped_percentage
            self.task_progress.emit(task_id, clamped_percentage, message)

    def pause_task(self, task_id: str):
        """Pause a task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.RUNNING:
                task.status = TaskStatus.PAUSED
                if task_id in self.active_task_ids:
                    self.active_task_ids.remove(task_id)
                vollog.info(f"Task paused: {task.name}")
                self.task_started.emit(task_id)  # Trigger UI update

    def resume_task(self, task_id: str):
        """Resume a paused task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PAUSED:
                task.status = TaskStatus.PENDING
                vollog.info(f"Task resumed: {task.name}")
                self.task_started.emit(task_id)  # Trigger UI update

    def remove_task(self, task_id: str):
        """Remove a task from the queue."""
        if task_id in self.tasks:
            task_name = self.tasks[task_id].name
            if task_id in self.active_task_ids:
                self.active_task_ids.remove(task_id)
            del self.tasks[task_id]
            if task_id in self.task_order:
                self.task_order.remove(task_id)
            vollog.info(f"Task removed: {task_name}")
            self.task_started.emit(task_id)  # Trigger UI update

    def prioritize_task(self, task_id: str):
        """Move a task to the front of the queue."""
        if task_id in self.tasks and task_id in self.task_order:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PENDING:
                self.task_order.remove(task_id)
                # Find first pending task position
                first_pending_idx = 0
                for idx, tid in enumerate(self.task_order):
                    if self.tasks[tid].status == TaskStatus.PENDING:
                        first_pending_idx = idx
                        break
                self.task_order.insert(first_pending_idx, task_id)
                vollog.info(f"Task prioritized: {task.name}")
                self.task_started.emit(task_id)  # Trigger UI update

    def retry_task(self, task_id: str):
        """Retry a failed task by resetting it to pending."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.FAILED:
                task.status = TaskStatus.PENDING
                task.error = None
                task.progress = 0
                vollog.info(f"Task retry: {task.name}")
                self.task_started.emit(task_id)  # Trigger UI update

    def clear_queue(self):
        """Clear all tasks from the queue."""
        self.tasks.clear()
        self.task_order.clear()
        self.active_task_ids.clear()
        vollog.info("Investigation queue cleared")

    def get_summary(self) -> Dict[str, int]:
        """Get a summary of task statuses."""
        summary = {
            "total": len(self.tasks),
            "pending": 0,
            "running": 0,
            "paused": 0,
            "completed": 0,
            "failed": 0
        }

        for task in self.get_all_tasks():
            if task.status == TaskStatus.PENDING:
                summary["pending"] += 1
            elif task.status == TaskStatus.RUNNING:
                summary["running"] += 1
            elif task.status == TaskStatus.PAUSED:
                summary["paused"] += 1
            elif task.status == TaskStatus.COMPLETED:
                summary["completed"] += 1
            elif task.status == TaskStatus.FAILED:
                summary["failed"] += 1

        return summary
