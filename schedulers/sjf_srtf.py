"""SJF (Shortest Job First) and SRTF (Shortest Remaining Time First) schedulers."""

import heapq
from typing import Optional

from models.job import Job
from .base import Scheduler


def _key_remaining(job: Job) -> int:
    return job.remaining_time


class SJFScheduler(Scheduler):
    """Shortest Job First - non-preemptive. Uses burst_time at arrival."""

    name = "SJF"
    preempts_on_quantum = False  # non-preemptive: run to completion once started

    def __init__(self) -> None:
        self.ready_queue: list[tuple[int, int, Job]] = []  # (burst_time, job_id, job)

    def add_job(self, job: Job, current_time: int) -> None:
        heapq.heappush(self.ready_queue, (job.burst_time, job.job_id, job))

    def get_next_job(self, current_time: int) -> Optional[Job]:
        if not self.ready_queue:
            return None
        _, _, job = heapq.heappop(self.ready_queue)
        return job

    def has_ready_jobs(self) -> bool:
        return len(self.ready_queue) > 0


class SRTFScheduler(Scheduler):
    """Shortest Remaining Time First - preemptive on job arrival."""

    name = "SRTF"

    preempts_on_arrival = True

    def __init__(self) -> None:
        self.ready_queue: list[tuple[int, int, Job]] = []  # (remaining_time, job_id, job)

    def add_job(self, job: Job, current_time: int) -> None:
        heapq.heappush(self.ready_queue, (job.remaining_time, job.job_id, job))

    def get_next_job(self, current_time: int) -> Optional[Job]:
        if not self.ready_queue:
            return None
        _, _, job = heapq.heappop(self.ready_queue)
        return job

    def has_ready_jobs(self) -> bool:
        return len(self.ready_queue) > 0

    def should_preempt(self, current: Job, new_arrival: Job) -> bool:
        return new_arrival.remaining_time < current.remaining_time

    def on_job_preempted(self, job: Job, current_time: int) -> None:
        heapq.heappush(self.ready_queue, (job.remaining_time, job.job_id, job))
