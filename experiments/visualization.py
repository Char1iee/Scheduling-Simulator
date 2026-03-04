"""Workload-focused visualization helpers for scheduler experiment results."""

import importlib
from pathlib import Path
from typing import List

from .runner import ExperimentResult


def generate_visualizations(
    results: List[ExperimentResult],
    output_dir: str = "results",
) -> List[Path]:
    """
    Generate workload-focused metric charts and save them as PNG files.

    Returns a list of output file paths.
    """
    try:
        plt = importlib.import_module("matplotlib.pyplot")
    except ImportError as exc:  # pragma: no cover - runtime environment dependent
        raise RuntimeError(
            "matplotlib is required for visualization. Install with: pip install matplotlib"
        ) from exc

    if not results:
        return []

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    workloads = sorted({r.workload_name for r in results})
    schedulers = sorted({r.scheduler_name for r in results})
    image_paths: List[Path] = []

    for workload in workloads:
        wl_results = [r for r in results if r.workload_name == workload]
        by_sched = {r.scheduler_name: r for r in wl_results}

        if workload == "batch":
            metric_defs = [
                ("avg_turnaround_time", "Avg Turnaround Time", 1.0),
            ]
            title = "Batch (turnaround-focused)"
        elif workload == "interactive":
            metric_defs = [
                ("avg_response_time", "Avg Response Time", 1.0),
            ]
            title = "Interactive (latency-focused)"
        else:
            metric_defs = [
                ("starvation_rate", "Starvation Rate (%)", 100.0),
                ("avg_response_time", "Avg Response Time", 1.0),
            ]
            title = "Mixed (fair vs. responsive)"

        fig, axes = plt.subplots(1, len(metric_defs), figsize=(6 * len(metric_defs), 5))
        if len(metric_defs) == 1:
            axes = [axes]

        for ax, (metric_attr, metric_label, scale) in zip(axes, metric_defs):
            values = []
            for sched in schedulers:
                result = by_sched.get(sched)
                if result is None:
                    values.append(0.0)
                    continue
                values.append(getattr(result.metrics, metric_attr) * scale)

            ax.bar(schedulers, values, color="#1f5f8b")
            ax.set_title(metric_label, fontsize=11)
            ax.tick_params(axis="x", labelrotation=35)
            ax.grid(axis="y", linestyle="--", alpha=0.3)

        fig.suptitle(title, fontsize=14, fontweight="bold")
        fig.tight_layout(rect=(0, 0, 1, 0.93))

        out_path = out_dir / f"{workload}.png"
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        image_paths.append(out_path)

    return image_paths
