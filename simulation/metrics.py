"""Metrics computation for scheduling evaluation."""

from dataclasses import dataclass
from typing import List, Optional

from models.job import Job


@dataclass
class SimulationMetrics:
    """Aggregated metrics from a simulation run."""

    avg_turnaround_time: float
    avg_response_time: float
    tail_latency_p95: float  # 95th percentile turnaround time
    starvation_rate: float  # fraction of jobs with wait_time > threshold
    total_jobs: int
    completed_jobs: int


def compute_metrics(
    completed_jobs: List[Job],
    starvation_threshold: int = 100,
) -> SimulationMetrics:
    """
    Compute all evaluation metrics from completed jobs.
    """
    if not completed_jobs:
        return SimulationMetrics(
            avg_turnaround_time=0.0,
            avg_response_time=0.0,
            tail_latency_p95=0.0,
            starvation_rate=0.0,
            total_jobs=0,
            completed_jobs=0,
        )

    turnaround_times = []
    response_times = []
    for j in completed_jobs:
        if j.turnaround_time is not None:
            turnaround_times.append(j.turnaround_time)
        if j.response_time is not None:
            response_times.append(j.response_time)

    avg_tt = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0.0
    avg_rt = sum(response_times) / len(response_times) if response_times else 0.0

    sorted_tt = sorted(turnaround_times) if turnaround_times else [0]
    p95_idx = int(len(sorted_tt) * 0.95)
    p95_idx = min(p95_idx, len(sorted_tt) - 1)
    tail_p95 = sorted_tt[p95_idx] if sorted_tt else 0.0

    # Starvation: jobs with wait_time > threshold. Wait = first_run_time - arrival.
    starvation_count = 0
    for j in completed_jobs:
        if j.first_run_time is not None:
            wait = j.first_run_time - j.arrival_time
            if wait > starvation_threshold:
                starvation_count += 1
    starvation_rate = starvation_count / len(completed_jobs) if completed_jobs else 0.0

    return SimulationMetrics(
        avg_turnaround_time=avg_tt,
        avg_response_time=avg_rt,
        tail_latency_p95=tail_p95,
        starvation_rate=starvation_rate,
        total_jobs=len(completed_jobs),
        completed_jobs=len(completed_jobs),
    )
