"""Priority with Aging scheduler - prevents starvation by aging waiting jobs."""

import heapq
from typing import Optional

from models.job import Job
from .base import Scheduler


class PriorityAgingScheduler(Scheduler):
    """Priority-based with aging. Effective priority = base_priority + age_bonus."""

    name = "Priority+Aging"

    def __init__(self, age_interval: int = 5, max_age_bonus: int = 10) -> None:
        self.age_interval = age_interval
        self.max_age_bonus = max_age_bonus
        # (neg_effective_priority, arrival_time, job_id, job) - negate for max-heap
        self.ready_queue: list[tuple[int, int, int, Job]] = []
        self.job_arrival: dict[int, int] = {}  # job_id -> arrival time in ready queue

    def add_job(self, job: Job, current_time: int) -> None:
        self.job_arrival[job.job_id] = current_time
        effective = self._effective_priority(job, current_time)
        heapq.heappush(
            self.ready_queue,
            (-effective, current_time, job.job_id, job),
        )

    def _effective_priority(self, job: Job, current_time: int) -> int:
        arrival = self.job_arrival.get(job.job_id, current_time)
        wait_time = current_time - arrival
        age_bonus = min(
            self.max_age_bonus,
            (wait_time // self.age_interval) * 2,
        )
        return job.priority + age_bonus

    def get_next_job(self, current_time: int) -> Optional[Job]:
        if not self.ready_queue:
            return None
        _, _, _, job = heapq.heappop(self.ready_queue)
        self.job_arrival.pop(job.job_id, None)
        return job

    def has_ready_jobs(self) -> bool:
        return len(self.ready_queue) > 0

    def on_job_preempted(self, job: Job, current_time: int) -> None:
        self.add_job(job, current_time)
