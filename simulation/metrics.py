"""Metrics computation for scheduling evaluation."""

from dataclasses import dataclass
from typing import List

from models.job import Job


@dataclass
class SimulationMetrics:
    """Aggregated metrics from a simulation run."""

    avg_turnaround_time: float
    avg_response_time: float
    tail_latency_p95: float  # 95th percentile turnaround time
    starvation_rate: float  # starvation inequality index on first-run waits
    lifetime_starvation_rate: float  # starvation inequality index on lifetime waits
    total_jobs: int
    completed_jobs: int


def _gini(values: List[float]) -> float:
    """
    Gini coefficient in [0, 1] for non-negative values.

    0 means perfectly equal waits; larger values indicate stronger starvation
    concentration (a subset of jobs waiting disproportionately longer).
    """
    if not values:
        return 0.0
    s = sorted(float(v) for v in values)
    n = len(s)
    total = sum(s)
    if total <= 0:
        return 0.0
    weighted_sum = 0.0
    for i, value in enumerate(s, start=1):
        weighted_sum += i * value
    return (2.0 * weighted_sum) / (n * total) - (n + 1) / n


def compute_metrics(
    completed_jobs: List[Job],
) -> SimulationMetrics:
    """
    Compute all evaluation metrics from completed jobs.

    Starvation uses a distributional fairness metric: Gini coefficient of wait
    times.
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

    first_run_waits: List[float] = []
    for j in completed_jobs:
        if j.first_run_time is not None:
            wait = j.first_run_time - j.arrival_time
            first_run_waits.append(float(wait))
    starvation_rate = _gini(first_run_waits)

    lifetime_waits: List[float] = []
    for j in completed_jobs:
        if j.turnaround_time is not None:
            total_wait = j.turnaround_time - j.burst_time
            lifetime_waits.append(float(total_wait))
    lifetime_starvation_rate = _gini(lifetime_waits)

    return SimulationMetrics(
        avg_turnaround_time=avg_tt,
        avg_response_time=avg_rt,
        tail_latency_p95=tail_p95,
        starvation_rate=starvation_rate,
        lifetime_starvation_rate=lifetime_starvation_rate,
        total_jobs=len(completed_jobs),
        completed_jobs=len(completed_jobs),
    )
