#!/usr/bin/env python3
"""Main entry point for Workload-Driven Scheduling Evaluation."""

from experiments.runner import run_experiments, print_results_table
from experiments.visualization import generate_visualizations


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

    try:
        images = generate_visualizations(results, output_dir="results")
        if images:
            print("\nSaved visualization files:")
            for path in images:
                print(f"  - {path}")
    except RuntimeError as err:
        print(f"\nVisualization skipped: {err}")


if __name__ == "__main__":
    main()
