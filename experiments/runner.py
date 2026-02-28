"""Experiment runner: run all schedulers on all workloads and compare."""

from dataclasses import dataclass, field
from typing import List, Type, Any

from models.job import Job
from schedulers.base import Scheduler
from schedulers.round_robin import RoundRobinScheduler
from schedulers.sjf_srtf import SJFScheduler, SRTFScheduler
from schedulers.priority_aging import PriorityAgingScheduler
from schedulers.lottery import LotteryScheduler
from schedulers.mlfq import MLFQScheduler
from simulation.engine import SimulationEngine
from simulation.metrics import SimulationMetrics, compute_metrics
from workloads.generator import (
    generate_batch_workload,
    generate_interactive_workload,
    generate_mixed_workload,
)


@dataclass
class ExperimentResult:
    scheduler_name: str
    workload_name: str
    metrics: SimulationMetrics
    completed_jobs: List[Job] = field(default_factory=list)


# Default schedulers to compare
DEFAULT_SCHEDULERS: List[Type[Scheduler]] = [
    RoundRobinScheduler,
    SJFScheduler,
    SRTFScheduler,
    PriorityAgingScheduler,
    LotteryScheduler,
    MLFQScheduler,
]


def run_experiments(
    schedulers: List[Type[Scheduler]] | None = None,
    quantum: int = 4,
    workload_seed: int = 42,
    starvation_threshold: int = 100,
) -> List[ExperimentResult]:
    """
    Run each scheduler on batch, interactive, and mixed workloads.
    Returns list of ExperimentResult for comparison.
    """
    schedulers = schedulers or DEFAULT_SCHEDULERS

    workloads = {
        "batch": generate_batch_workload(num_jobs=20, seed=workload_seed),
        "interactive": generate_interactive_workload(num_jobs=50, seed=workload_seed),
        "mixed": generate_mixed_workload(seed=workload_seed),
    }

    results: List[ExperimentResult] = []

    for wl_name, jobs in workloads.items():
        for SchedulerClass in schedulers:
            scheduler = SchedulerClass()
            engine = SimulationEngine(scheduler=scheduler, quantum=quantum)
            completed = engine.run(jobs)
            metrics = compute_metrics(completed, starvation_threshold=starvation_threshold)
            results.append(
                ExperimentResult(
                    scheduler_name=scheduler.name,
                    workload_name=wl_name,
                    metrics=metrics,
                    completed_jobs=completed,
                )
            )

    return results


def print_results_table(results: List[ExperimentResult]) -> None:
    """Print a formatted comparison table."""
    print("\n" + "=" * 90)
    print("SCHEDULING EXPERIMENT RESULTS")
    print("=" * 90)

    workloads = sorted(set(r.workload_name for r in results))
    schedulers = sorted(set(r.scheduler_name for r in results))

    for wl in workloads:
        print(f"\n--- Workload: {wl.upper()} ---\n")
        print(f"{'Scheduler':<20} {'Avg TT':>10} {'Avg RT':>10} {'Tail p95':>10} {'Starvation':>12}")
        print("-" * 65)

        for sched in schedulers:
            r = next((x for x in results if x.workload_name == wl and x.scheduler_name == sched), None)
            if r is None:
                continue
            m = r.metrics
            print(f"{sched:<20} {m.avg_turnaround_time:>10.1f} {m.avg_response_time:>10.1f} "
                  f"{m.tail_latency_p95:>10.1f} {m.starvation_rate*100:>11.1f}%")

    print("\n" + "=" * 90)
