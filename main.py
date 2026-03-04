#!/usr/bin/env python3
"""Main entry point for Workload-Driven Scheduling Evaluation."""

import argparse

from experiments.runner import run_experiments, print_results_table
from experiments.visualization import generate_visualizations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run workload-driven scheduler experiments."
    )
    parser.add_argument("--quantum", type=int, default=4, help="Base time quantum.")
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for workload generation."
    )
    parser.add_argument(
        "--starvation-threshold",
        type=int,
        default=100,
        help="Threshold for Starv(1st) and Starv(life).",
    )
    parser.add_argument(
        "--batch-num-jobs",
        type=int,
        default=20,
        help="Number of jobs in batch workload.",
    )
    parser.add_argument(
        "--interactive-num-jobs",
        type=int,
        default=50,
        help="Number of jobs in interactive workload.",
    )
    parser.add_argument(
        "--mixed-num-batch",
        type=int,
        default=10,
        help="Number of batch jobs in mixed workload.",
    )
    parser.add_argument(
        "--mixed-num-interactive",
        type=int,
        default=30,
        help="Number of interactive jobs in mixed workload.",
    )
    parser.add_argument(
        "--no-viz",
        action="store_true",
        help="Skip visualization generation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("Workload-Driven Scheduling Evaluation")
    print("Running schedulers: Round Robin, SJF, SRTF, Priority+Aging, Lottery, MLFQ")
    print("Workloads: batch, interactive, mixed\n")

    results = run_experiments(
        quantum=args.quantum,
        workload_seed=args.seed,
        starvation_threshold=args.starvation_threshold,
        batch_num_jobs=args.batch_num_jobs,
        interactive_num_jobs=args.interactive_num_jobs,
        mixed_num_batch=args.mixed_num_batch,
        mixed_num_interactive=args.mixed_num_interactive,
    )

    print_results_table(results)

    if not args.no_viz:
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
