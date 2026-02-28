"""Round Robin scheduler - fixed time slices shared equally."""

from collections import deque
from typing import Optional

from models.job import Job
from .base import Scheduler


class RoundRobinScheduler(Scheduler):
    """Fixed quantum, FIFO queue, equal share of CPU."""

    name = "Round Robin"

    def __init__(self) -> None:
        self.ready_queue: deque[Job] = deque()

    def add_job(self, job: Job, current_time: int) -> None:
        self.ready_queue.append(job)

    def get_next_job(self, current_time: int) -> Optional[Job]:
        if not self.ready_queue:
            return None
        return self.ready_queue.popleft()

    def has_ready_jobs(self) -> bool:
        return len(self.ready_queue) > 0
