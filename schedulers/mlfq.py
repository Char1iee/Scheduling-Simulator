"""Multi-Level Feedback Queue scheduler."""

from collections import deque
from typing import Optional

from models.job import Job
from .base import Scheduler


class MLFQScheduler(Scheduler):
    """Multiple queues with dynamic priority. Top queue = highest priority."""

    name = "MLFQ"

    def __init__(
        self,
        num_queues: int = 3,
        quanta: Optional[list[int]] = None,
    ) -> None:
        self.num_queues = num_queues
        self.quanta = quanta or [1, 2, 4]  # quantum per level
        while len(self.quanta) < num_queues:
            self.quanta.append(self.quanta[-1] * 2)
        self.queues: list[deque[Job]] = [deque() for _ in range(num_queues)]
        self.job_level: dict[int, int] = {}  # job_id -> queue level
        self.job_used: dict[int, int] = {}  # job_id -> time used in current level

    def add_job(self, job: Job, current_time: int) -> None:
        self.job_level[job.job_id] = 0
        self.job_used[job.job_id] = 0
        self.queues[0].append(job)

    def get_next_job(self, current_time: int) -> Optional[Job]:
        for q in self.queues:
            if q:
                return q.popleft()
        return None

    def has_ready_jobs(self) -> bool:
        return any(q for q in self.queues)

    def get_quantum(self, job: Job) -> int:
        """Return the time slice for this job based on its current MLFQ level."""
        level = self.job_level.get(job.job_id, 0)
        return self.quanta[min(level, len(self.quanta) - 1)]

    def on_job_preempted(self, job: Job, current_time: int) -> None:
        # A preemption means the job used its full quantum at the current level.
        # Demote it to the next lower-priority queue (or stay at the bottom).
        level = self.job_level.get(job.job_id, 0)
        new_level = min(level + 1, self.num_queues - 1)
        self.job_level[job.job_id] = new_level
        self.job_used[job.job_id] = 0
        self.queues[new_level].append(job)  # back of lower-priority queue
