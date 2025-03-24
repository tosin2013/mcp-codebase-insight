"""Task tracking and management for async operations."""

import asyncio
import logging
from typing import Set, Optional
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger(__name__)

class TaskTracker:
    """Tracks and manages async tasks with improved error handling and logging."""
    
    def __init__(self):
        """Initialize the task tracker."""
        self._tasks: Set[asyncio.Task] = set()
        self._loop = asyncio.get_event_loop()
        self._loop_id = id(self._loop)
        self._start_time = datetime.utcnow()
        logger.debug(f"TaskTracker initialized with loop ID: {self._loop_id}")
    
    def track_task(self, task: asyncio.Task) -> None:
        """Track a new task and set up completion handling.
        
        Args:
            task: The asyncio.Task to track
        """
        if id(asyncio.get_event_loop()) != self._loop_id:
            logger.warning(
                f"Task created in different event loop context. "
                f"Expected: {self._loop_id}, Got: {id(asyncio.get_event_loop())}"
            )
        
        self._tasks.add(task)
        task.add_done_callback(self._handle_task_completion)
        logger.debug(f"Tracking new task: {task.get_name()}")
    
    def _handle_task_completion(self, task: asyncio.Task) -> None:
        """Handle task completion and cleanup.
        
        Args:
            task: The completed task
        """
        self._tasks.discard(task)
        if task.exception():
            logger.error(
                f"Task {task.get_name()} failed with error: {task.exception()}",
                exc_info=True
            )
        else:
            logger.debug(f"Task {task.get_name()} completed successfully")
    
    async def cancel_all_tasks(self, timeout: float = 5.0) -> None:
        """Cancel all tracked tasks and wait for completion.
        
        Args:
            timeout: Maximum time to wait for tasks to cancel
        """
        if not self._tasks:
            logger.debug("No tasks to cancel")
            return
        
        logger.debug(f"Cancelling {len(self._tasks)} tasks")
        for task in self._tasks:
            if not task.done() and not task.cancelled():
                task.cancel()
        
        try:
            await asyncio.wait_for(
                asyncio.gather(*self._tasks, return_exceptions=True),
                timeout=timeout
            )
            logger.debug("All tasks cancelled successfully")
        except asyncio.TimeoutError:
            logger.warning(f"Task cancellation timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Error during task cancellation: {e}", exc_info=True)
    
    def get_active_tasks(self) -> Set[asyncio.Task]:
        """Get all currently active tasks.
        
        Returns:
            Set of active asyncio.Task objects
        """
        return self._tasks.copy()
    
    def get_task_count(self) -> int:
        """Get the number of currently tracked tasks.
        
        Returns:
            Number of active tasks
        """
        return len(self._tasks)
    
    def get_uptime(self) -> float:
        """Get the uptime of the task tracker in seconds.
        
        Returns:
            Uptime in seconds
        """
        return (datetime.utcnow() - self._start_time).total_seconds()
    
    def __del__(self):
        """Cleanup when the tracker is destroyed."""
        if self._tasks:
            logger.warning(
                f"TaskTracker destroyed with {len(self._tasks)} "
                "unfinished tasks"
            ) 