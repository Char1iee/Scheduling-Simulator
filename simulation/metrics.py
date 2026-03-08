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
    starvation_rate: float  # fraction of jobs with first-run wait > factor * burst
    lifetime_starvation_rate: float  # fraction of jobs with total wait > factor * burst
    total_jobs: int
    completed_jobs: int


def _median(values: List[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    mid = len(s) // 2
    return (s[mid] + s[mid - 1]) / 2 if len(s) % 2 == 0 else s[mid]


def compute_metrics(
    completed_jobs: List[Job],
    starvation_factor: float = 2.0,
) -> SimulationMetrics:
    """
    Compute all evaluation metrics from completed jobs.

    Starvation uses a median-relative, scale-invariant definition: a job is
    starved if its wait ratio (wait/burst) exceeds factor × the median ratio.
    This distinguishes unfair schedulers (some jobs wait much longer than
    typical) from fair ones (everyone waits similarly).
    """
    if not completed_jobs:
        return SimulationMetrics(
            avg_turnaround_time=0.0,
            avg_response_time=0.0,
            tail_latency_p95=0.0,
            starvation_rate=0.0,
            lifetime_starvation_rate=0.0,
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

    # First-run wait ratios: wait_before_first_run / burst
    first_run_ratios = []
    for j in completed_jobs:
        if j.first_run_time is not None and j.burst_time > 0:
            wait = j.first_run_time - j.arrival_time
            first_run_ratios.append(wait / j.burst_time)
    median_first = _median(first_run_ratios) if first_run_ratios else 0.0
    threshold_first = max(starvation_factor * median_first, 1.0)  # at least 1x burst
    starvation_count = sum(
        1 for j in completed_jobs
        if j.first_run_time is not None and j.burst_time > 0
        and (j.first_run_time - j.arrival_time) / j.burst_time > threshold_first
    )
    starvation_rate = starvation_count / len(completed_jobs) if completed_jobs else 0.0

    # Lifetime: total_wait/burst ratios. Starved if ratio > factor × median.
    lifetime_ratios = []
    for j in completed_jobs:
        if j.turnaround_time is not None and j.burst_time > 0:
            total_wait = j.turnaround_time - j.burst_time
            lifetime_ratios.append(total_wait / j.burst_time)
    median_lifetime = _median(lifetime_ratios) if lifetime_ratios else 0.0
    threshold_lifetime = max(starvation_factor * median_lifetime, 1.0)
    lifetime_starve_count = sum(
        1 for j in completed_jobs
        if j.turnaround_time is not None and j.burst_time > 0
        and (j.turnaround_time - j.burst_time) / j.burst_time > threshold_lifetime
    )
    lifetime_starvation_rate = (
        lifetime_starve_count / len(completed_jobs) if completed_jobs else 0.0
    )

    return SimulationMetrics(
        avg_turnaround_time=avg_tt,
        avg_response_time=avg_rt,
        tail_latency_p95=tail_p95,
        starvation_rate=starvation_rate,
        lifetime_starvation_rate=lifetime_starvation_rate,
        total_jobs=len(completed_jobs),
        completed_jobs=len(completed_jobs),
    )
