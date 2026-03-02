"""Priority with Aging scheduler - prevents starvation by aging waiting jobs."""

import heapq
from typing import Optional

from models.job import Job
from .base import Scheduler


class PriorityAgingScheduler(Scheduler):
    """Priority-based with aging. Effective priority = base_priority + age_bonus.

    Aging tracks actual ready-queue wait time (excludes time spent running).
    Each ready-queue stint accumulates wait; when a job runs and is preempted,
    the wait from the previous stint is frozen, and a new stint begins.
    """

    name = "Priority+Aging"

    def __init__(self, age_interval: int = 5, max_age_bonus: int = 10) -> None:
        self.age_interval = age_interval
        self.max_age_bonus = max_age_bonus
        # (neg_effective_priority, enqueue_time, job_id, job) - negate for max-heap
        self.ready_queue: list[tuple[int, int, int, Job]] = []
        self.job_enqueue_time: dict[int, int] = {}   # job_id -> last enqueue timestamp
        self.job_accumulated_wait: dict[int, int] = {}  # job_id -> frozen total wait

    def add_job(self, job: Job, current_time: int) -> None:
        self.job_enqueue_time[job.job_id] = current_time
        if job.job_id not in self.job_accumulated_wait:
            self.job_accumulated_wait[job.job_id] = 0
        effective = self._effective_priority(job, current_time)
        heapq.heappush(
            self.ready_queue,
            (-effective, current_time, job.job_id, job),
        )

    def _effective_priority(self, job: Job, current_time: int) -> int:
        enqueue = self.job_enqueue_time.get(job.job_id, current_time)
        current_wait = current_time - enqueue  # wait during this queue stint
        total_wait = self.job_accumulated_wait.get(job.job_id, 0) + current_wait
        age_bonus = min(
            self.max_age_bonus,
            (total_wait // self.age_interval) * 2,
        )
        return job.priority + age_bonus

    def get_next_job(self, current_time: int) -> Optional[Job]:
        if not self.ready_queue:
            return None
        # Refresh all effective priorities to account for accumulated aging.
        updated = []
        for _, _, _, job in self.ready_queue:
            eff = self._effective_priority(job, current_time)
            updated.append((-eff, self.job_enqueue_time[job.job_id], job.job_id, job))
        heapq.heapify(updated)
        self.ready_queue = updated
        _, _, _, job = heapq.heappop(self.ready_queue)
        # Freeze the wait accumulated during this ready-queue stint before running.
        enqueue = self.job_enqueue_time.get(job.job_id, current_time)
        self.job_accumulated_wait[job.job_id] = (
            self.job_accumulated_wait.get(job.job_id, 0) + (current_time - enqueue)
        )
        return job

    def has_ready_jobs(self) -> bool:
        return len(self.ready_queue) > 0

    def on_job_preempted(self, job: Job, current_time: int) -> None:
        # Re-enter queue. New wait stint starts from now;
        # accumulated_wait already has frozen wait from previous stints.
        self.job_enqueue_time[job.job_id] = current_time
        effective = self._effective_priority(job, current_time)
        heapq.heappush(
            self.ready_queue,
            (-effective, current_time, job.job_id, job),
        )
