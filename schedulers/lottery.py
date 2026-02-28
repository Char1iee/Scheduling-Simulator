"""Lottery Scheduling - CPU time allocated probabilistically via tickets."""

import random
from typing import Optional

from models.job import Job
from .base import Scheduler


class LotteryScheduler(Scheduler):
    """Probabilistic scheduling based on tickets. Jobs get tickets = 1 + priority."""

    name = "Lottery"

    def __init__(self, seed: Optional[int] = None) -> None:
        self.ready_queue: list[Job] = []
        self.rng = random.Random(seed)

    def add_job(self, job: Job, current_time: int) -> None:
        self.ready_queue.append(job)

    def get_next_job(self, current_time: int) -> Optional[Job]:
        if not self.ready_queue:
            return None
        total_tickets = sum(max(1, j.priority + 1) for j in self.ready_queue)
        if total_tickets <= 0:
            return self.ready_queue.pop(0)
        r = self.rng.randint(1, total_tickets)
        acc = 0
        for i, j in enumerate(self.ready_queue):
            acc += max(1, j.priority + 1)
            if r <= acc:
                return self.ready_queue.pop(i)
        return self.ready_queue.pop(-1)

    def has_ready_jobs(self) -> bool:
        return len(self.ready_queue) > 0
