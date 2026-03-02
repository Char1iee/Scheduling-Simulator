"""Discrete-event simulation engine for CPU scheduling."""

import heapq
from typing import List, Optional

from models.job import Job
from models.event import Event, EventType
from schedulers.base import Scheduler


class SimulationEngine:
    """Runs a scheduling simulation with discrete events."""

    def __init__(
        self,
        scheduler: Scheduler,
        quantum: int = 4,
        use_preemptive_quantum: bool = True,
    ) -> None:
        self.scheduler = scheduler
        self.quantum = quantum
        self.use_preemptive_quantum = use_preemptive_quantum
        self.current_time = 0
        self.completed_jobs: List[Job] = []
        self.all_jobs: List[Job] = []

    def run(self, jobs: List[Job]) -> List[Job]:
        """
        Run simulation on the given jobs.
        Returns list of completed jobs with turnaround/response times filled.
        """
        self.completed_jobs = []
        self.current_time = 0
        self.all_jobs = [j.copy_for_simulation() for j in jobs]

        arrivals: List[Event] = [
            Event(job.arrival_time, EventType.ARRIVAL, job) for job in self.all_jobs
        ]
        heapq.heapify(arrivals)

        current_job: Optional[Job] = None
        job_run_start: int = 0

        # Whether this scheduler supports quantum-based preemption.
        preempts_on_quantum = getattr(self.scheduler, "preempts_on_quantum", True)
        # Optional per-job quantum hook (e.g. MLFQ per-level quanta).
        get_quantum = getattr(self.scheduler, "get_quantum", None)

        while arrivals or current_job or self.scheduler.has_ready_jobs():
            next_arrival_time = arrivals[0].time if arrivals else float("inf")

            if current_job is not None:
                effective_quantum = get_quantum(current_job) if get_quantum else self.quantum
                if preempts_on_quantum:
                    run_duration = min(effective_quantum, current_job.remaining_time)
                else:
                    run_duration = current_job.remaining_time  # run to completion
                next_completion = job_run_start + run_duration
            else:
                next_completion = float("inf")

            next_time = min(next_arrival_time, next_completion)
            if next_time == float("inf"):
                break

            self.current_time = int(next_time)

            # Completion or quantum expire
            if current_job is not None and next_completion <= next_arrival_time:
                elapsed = self.current_time - job_run_start
                current_job.remaining_time -= elapsed
                if current_job.remaining_time <= 0:
                    current_job.state = "done"
                    current_job.completion_time = self.current_time
                    self.completed_jobs.append(current_job)
                else:
                    current_job.state = "ready"
                    self.scheduler.on_job_preempted(current_job, self.current_time)
                current_job = None

            # Process all arrivals at current_time
            while arrivals and arrivals[0].time == self.current_time:
                ev = heapq.heappop(arrivals)
                job = ev.job
                if job is None:
                    continue
                job.state = "ready"
                self.scheduler.add_job(job, self.current_time)

                # Preemption on arrival (e.g., for SRTF)
                if (
                    current_job is not None
                    and getattr(self.scheduler, "preempts_on_arrival", False)
                    and self.scheduler.should_preempt(current_job, job)
                ):
                    elapsed = self.current_time - job_run_start
                    current_job.remaining_time -= elapsed
                    current_job.state = "ready"
                    self.scheduler.on_job_preempted(current_job, self.current_time)
                    current_job = None

            # Pick next job
            if current_job is None and self.scheduler.has_ready_jobs():
                next_job = self.scheduler.get_next_job(self.current_time)
                if next_job is not None:
                    current_job = next_job
                    current_job.state = "running"
                    if current_job.first_run_time is None:
                        current_job.first_run_time = self.current_time
                    job_run_start = self.current_time

        return self.completed_jobs
