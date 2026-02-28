"""Job/Task model for scheduling simulation."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Job:
    """A single job/task in the scheduling simulation."""

    job_id: int
    arrival_time: int
    burst_time: int
    priority: int = 0  # Higher = higher priority; used by Priority, MLFQ, Lottery

    # Runtime state (mutated during simulation)
    remaining_time: int = field(default=0, init=False)
    state: str = "new"  # new, ready, running, done
    first_run_time: Optional[int] = None  # When job first got CPU (for response time)
    completion_time: Optional[int] = None  # When job finished

    def __post_init__(self) -> None:
        self.remaining_time = self.burst_time

    def reset(self) -> None:
        """Reset job state for re-running simulation."""
        self.remaining_time = self.burst_time
        self.state = "new"
        self.first_run_time = None
        self.completion_time = None

    def copy_for_simulation(self) -> "Job":
        """Create a fresh copy for a simulation run (preserves original params)."""
        j = Job(
            job_id=self.job_id,
            arrival_time=self.arrival_time,
            burst_time=self.burst_time,
            priority=self.priority,
        )
        return j

    @property
    def turnaround_time(self) -> Optional[int]:
        if self.completion_time is None:
            return None
        return self.completion_time - self.arrival_time

    @property
    def response_time(self) -> Optional[int]:
        if self.first_run_time is None:
            return None
        return self.first_run_time - self.arrival_time

    def __repr__(self) -> str:
        return f"Job({self.job_id}, arr={self.arrival_time}, burst={self.burst_time})"
