"""Service layer for running scheduler experiments from the platform UI."""

from __future__ import annotations

from dataclasses import dataclass

from models.job import Job
from schedulers.base import Scheduler
from schedulers.lottery import LotteryScheduler
from schedulers.mlfq import MLFQScheduler
from schedulers.priority_aging import PriorityAgingScheduler
from schedulers.round_robin import RoundRobinScheduler
from schedulers.sjf_srtf import SJFScheduler, SRTFScheduler
from simulation.engine import SimulationEngine
from simulation.metrics import SimulationMetrics, compute_metrics


@dataclass
class PlatformRunResult:
    scheduler_name: str
    metrics: SimulationMetrics
    completed_jobs: list[Job]


def available_scheduler_names() -> list[str]:
    return [
        "Round Robin",
        "SJF",
        "SRTF",
        "Priority+Aging",
        "Lottery",
        "MLFQ",
    ]


def build_scheduler(name: str, lottery_seed: int | None = None) -> Scheduler:
    if name == "Round Robin":
        return RoundRobinScheduler()
    if name == "SJF":
        return SJFScheduler()
    if name == "SRTF":
        return SRTFScheduler()
    if name == "Priority+Aging":
        return PriorityAgingScheduler()
    if name == "Lottery":
        return LotteryScheduler(seed=lottery_seed)
    if name == "MLFQ":
        return MLFQScheduler()
    raise ValueError(f"Unknown scheduler: {name}")


def run_platform_experiment(
    jobs: list[Job],
    scheduler_names: list[str],
    quantum: int,
    starvation_threshold: int,
    lottery_seed: int,
) -> list[PlatformRunResult]:
    if not jobs:
        raise ValueError("Workload is empty")
    if not scheduler_names:
        raise ValueError("At least one scheduler must be selected")

    results: list[PlatformRunResult] = []
    for scheduler_name in scheduler_names:
        scheduler = build_scheduler(scheduler_name, lottery_seed=lottery_seed)
        engine = SimulationEngine(scheduler=scheduler, quantum=quantum)
        completed_jobs = engine.run(jobs)
        metrics = compute_metrics(completed_jobs, starvation_threshold=starvation_threshold)
        results.append(
            PlatformRunResult(
                scheduler_name=scheduler.name,
                metrics=metrics,
                completed_jobs=completed_jobs,
            )
        )

    return results
