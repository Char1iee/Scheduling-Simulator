#!/usr/bin/env python3
"""Main entry point for Workload-Driven Scheduling Evaluation."""

from experiments.runner import run_experiments, print_results_table


def main() -> None:
    print("Workload-Driven Scheduling Evaluation")
    print("Running schedulers: Round Robin, SJF, SRTF, Priority+Aging, Lottery, MLFQ")
    print("Workloads: batch, interactive, mixed\n")

    results = run_experiments(
        quantum=4,
        workload_seed=42,
        starvation_threshold=100,
    )

    print_results_table(results)


if __name__ == "__main__":
    main()
