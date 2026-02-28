"""Workload generators: batch, interactive, and mixed."""

import random
from typing import List

from models.job import Job


def generate_batch_workload(
    num_jobs: int = 20,
    burst_min: int = 10,
    burst_max: int = 100,
    arrival_min: int = 0,
    arrival_max: int = 50,
    seed: int = 42,
) -> List[Job]:
    """
    Batch: long, CPU-bound jobs, infrequent arrivals.
    Long burst times, sparse arrivals.
    """
    rng = random.Random(seed)
    jobs = []
    for i in range(num_jobs):
        burst = rng.randint(burst_min, burst_max)
        arrival = rng.randint(arrival_min, arrival_max) if arrival_max > 0 else 0
        jobs.append(Job(job_id=i, arrival_time=arrival, burst_time=burst, priority=0))
    jobs.sort(key=lambda j: j.arrival_time)
    return jobs


def generate_interactive_workload(
    num_jobs: int = 50,
    burst_min: int = 1,
    burst_max: int = 10,
    arrival_min: int = 0,
    arrival_max: int = 100,
    seed: int = 42,
) -> List[Job]:
    """
    Interactive/Streaming: short jobs, frequent arrivals.
    Short burst times, dense arrivals, latency-sensitive.
    """
    rng = random.Random(seed)
    jobs = []
    for i in range(num_jobs):
        burst = rng.randint(burst_min, burst_max)
        arrival = rng.randint(arrival_min, arrival_max) if arrival_max > 0 else 0
        jobs.append(Job(job_id=i, arrival_time=arrival, burst_time=burst, priority=1))
    jobs.sort(key=lambda j: j.arrival_time)
    return jobs


def generate_mixed_workload(
    num_batch: int = 10,
    num_interactive: int = 30,
    batch_burst_min: int = 20,
    batch_burst_max: int = 80,
    interactive_burst_min: int = 1,
    interactive_burst_max: int = 15,
    arrival_range: int = 120,
    seed: int = 42,
) -> List[Job]:
    """
    Mixed: batch + interactive jobs coexisting.
    Interactive jobs get higher priority by default.
    """
    rng = random.Random(seed)
    jobs = []
    jid = 0
    for _ in range(num_batch):
        burst = rng.randint(batch_burst_min, batch_burst_max)
        arrival = rng.randint(0, arrival_range)
        jobs.append(Job(job_id=jid, arrival_time=arrival, burst_time=burst, priority=0))
        jid += 1
    for _ in range(num_interactive):
        burst = rng.randint(interactive_burst_min, interactive_burst_max)
        arrival = rng.randint(0, arrival_range)
        jobs.append(Job(job_id=jid, arrival_time=arrival, burst_time=burst, priority=2))
        jid += 1
    jobs.sort(key=lambda j: (j.arrival_time, j.job_id))
    return jobs
