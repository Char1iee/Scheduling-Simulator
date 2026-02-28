"""Abstract base scheduler interface."""

from abc import ABC, abstractmethod
from typing import Optional

from models.job import Job


class Scheduler(ABC):
    """Base class for all schedulers."""

    name: str = "Base"

    @abstractmethod
    def add_job(self, job: Job, current_time: int) -> None:
        """Add a ready job to the scheduler's queue."""
        pass

    @abstractmethod
    def get_next_job(self, current_time: int) -> Optional[Job]:
        """Get the next job to run. Returns None if queue is empty."""
        pass

    @abstractmethod
    def has_ready_jobs(self) -> bool:
        """Return True if there are jobs ready to run."""
        pass

    def on_job_preempted(self, job: Job, current_time: int) -> None:
        """Called when a job is preempted (e.g., quantum expired). Override if needed."""
        self.add_job(job, current_time)
