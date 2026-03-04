"""Streamlit platform UI for custom scheduling experiments."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

# Ensure repo root is importable when launched from platform_ui/.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.job import Job
from platform_ui.experiment_service import (
    PlatformRunResult,
    available_scheduler_names,
    run_platform_experiment,
)
from platform_ui.workload_io import parse_workload_text, parse_workload_upload
from workloads.generator import (
    generate_batch_workload,
    generate_interactive_workload,
    generate_mixed_workload,
)


DEFAULT_TEMPLATE = """job_id,arrival_time,burst_time,priority
0,0,12,0
1,1,4,2
2,3,8,1
"""
SESSION_RESULTS_KEY = "platform_results"


def main() -> None:
    st.set_page_config(page_title="Scheduling Simulator Platform", layout="wide")
    st.title("Scheduling Simulator Platform")
    st.caption("Define or upload your own workload, then compare scheduling policies.")
    if SESSION_RESULTS_KEY not in st.session_state:
        st.session_state[SESSION_RESULTS_KEY] = None

    with st.sidebar:
        st.header("Experiment Settings")
        quantum = st.number_input("Global quantum", min_value=1, value=4, step=1)
        starvation_threshold = st.number_input(
            "Starvation threshold", min_value=1, value=100, step=1
        )
        lottery_seed = st.number_input("Lottery seed", min_value=0, value=42, step=1)

        scheduler_names = st.multiselect(
            "Schedulers",
            options=available_scheduler_names(),
            default=available_scheduler_names(),
        )

    input_mode = st.radio(
        "Workload input",
        options=["Preset generator", "Upload file", "Manual definition"],
        horizontal=True,
    )

    jobs: list[Job] | None = None
    source_label = ""

    if input_mode == "Preset generator":
        jobs, source_label = render_preset_input()
    elif input_mode == "Upload file":
        jobs, source_label = render_upload_input()
    else:
        jobs, source_label = render_manual_input()

    if jobs:
        st.subheader("Workload Preview")
        st.caption(source_label)
        st.dataframe(_jobs_to_table(jobs), use_container_width=True)

    run_clicked = st.button("Run Experiment", type="primary", use_container_width=True)
    if run_clicked:
        if not jobs:
            st.error("Please provide a valid workload before running the experiment.")
            return

        try:
            results = run_platform_experiment(
                jobs=jobs,
                scheduler_names=scheduler_names,
                quantum=quantum,
                starvation_threshold=starvation_threshold,
                lottery_seed=lottery_seed,
            )
        except ValueError as err:
            st.error(str(err))
            return

        st.success("Experiment complete")
        st.session_state[SESSION_RESULTS_KEY] = results

    if st.session_state[SESSION_RESULTS_KEY] is not None:
        render_results(st.session_state[SESSION_RESULTS_KEY])


def render_preset_input() -> tuple[list[Job], str]:
    preset = st.selectbox("Preset workload", options=["batch", "interactive", "mixed"])
    seed = st.number_input("Seed", min_value=0, value=42, step=1)

    if preset == "batch":
        num_jobs = st.number_input("Number of jobs", min_value=1, value=20, step=1)
        jobs = generate_batch_workload(num_jobs=int(num_jobs), seed=int(seed))
    elif preset == "interactive":
        num_jobs = st.number_input("Number of jobs", min_value=1, value=50, step=1)
        jobs = generate_interactive_workload(num_jobs=int(num_jobs), seed=int(seed))
    else:
        num_batch = st.number_input("Batch jobs", min_value=1, value=10, step=1)
        num_interactive = st.number_input("Interactive jobs", min_value=1, value=30, step=1)
        jobs = generate_mixed_workload(
            num_batch=int(num_batch),
            num_interactive=int(num_interactive),
            seed=int(seed),
        )

    return jobs, f"Generated preset: {preset} ({len(jobs)} jobs)"


def render_upload_input() -> tuple[list[Job] | None, str]:
    uploaded = st.file_uploader("Upload .csv or .json workload", type=["csv", "json"])
    if uploaded is None:
        st.info("Required columns/fields: arrival_time, burst_time. Optional: job_id, priority")
        return None, ""

    try:
        parsed = parse_workload_upload(uploaded.name, uploaded.getvalue())
    except ValueError as err:
        st.error(str(err))
        return None, ""

    return parsed.jobs, f"Uploaded: {uploaded.name} ({parsed.source_summary})"


def render_manual_input() -> tuple[list[Job] | None, str]:
    fmt = st.selectbox("Manual format", options=["CSV", "JSON"])
    default_payload = DEFAULT_TEMPLATE if fmt == "CSV" else _default_json_template()
    payload = st.text_area(
        "Enter workload payload",
        value=default_payload,
        height=220,
        help="Required: arrival_time, burst_time. Optional: job_id, priority",
    )

    try:
        parsed = parse_workload_text(payload, fmt)
    except ValueError as err:
        st.error(str(err))
        return None, ""

    return parsed.jobs, f"Manual {fmt}: {parsed.source_summary}"


def render_results(results: list[PlatformRunResult]) -> None:
    st.subheader("Metrics")
    scheduler_order = sorted({r.scheduler_name for r in results})
    order_map = {name: idx for idx, name in enumerate(scheduler_order)}
    rows = []
    for result in results:
        m = result.metrics
        rows.append(
            {
                "scheduler": result.scheduler_name,
                "avg_turnaround": round(m.avg_turnaround_time, 1),
                "avg_response": round(m.avg_response_time, 1),
                "tail_p95": m.tail_latency_p95,
                "starvation_first (%)": round(m.starvation_rate * 100, 2),
                "starvation_lifetime (%)": round(m.lifetime_starvation_rate * 100, 2),
                "completed_jobs": m.completed_jobs,
            }
        )

    metrics_df = pd.DataFrame(rows)
    metrics_df["__scheduler_order"] = metrics_df["scheduler"].map(
        lambda x: order_map.get(str(x), 9999)
    )
    metrics_df = metrics_df.sort_values("__scheduler_order").drop(
        columns=["__scheduler_order"]
    )
    st.dataframe(
        metrics_df.set_index("scheduler"),
        use_container_width=True,
        column_config={
            "avg_turnaround": st.column_config.NumberColumn(format="%.1f"),
            "avg_response": st.column_config.NumberColumn(format="%.1f"),
            "tail_p95": st.column_config.NumberColumn(format="%g"),
            "starvation_first_%": st.column_config.NumberColumn(format="%.1f"),
            "starvation_lifetime_%": st.column_config.NumberColumn(format="%.1f"),
        },
    )
    metric_options = {
        "Average Turnaround Time": "avg_turnaround",
        "Average Response Time": "avg_response",
        "Tail Latency (p95)": "tail_p95",
        "Starvation First Run (%)": "starvation_first_%",
        "Starvation Lifetime (%)": "starvation_lifetime_%",
    }
    selected_metric_label = st.selectbox(
        "Metric to visualize",
        options=list(metric_options.keys()),
        index=1,
    )
    selected_metric_key = metric_options[selected_metric_label]
    metric_format = "~g" if selected_metric_key == "tail_p95" else ".1f"
    chart = (
        alt.Chart(metrics_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "scheduler:N",
                sort=scheduler_order,
                title="Scheduler",
                axis=alt.Axis(labelAngle=0),
            ),
            y=alt.Y(
                f"{selected_metric_key}:Q",
                title=selected_metric_label,
                axis=alt.Axis(format=metric_format),
            ),
            tooltip=[
                alt.Tooltip("scheduler:N", title="Scheduler"),
                alt.Tooltip(
                    f"{selected_metric_key}:Q",
                    title=selected_metric_label,
                    format=metric_format,
                ),
            ],
        )
    )
    st.altair_chart(chart, use_container_width=True)

    download_csv = metrics_df.to_csv(index=False)
    st.download_button(
        "Download metrics as CSV",
        data=download_csv,
        file_name="results.csv",
        mime="text/csv",
    )


def _jobs_to_table(jobs: list[Job]) -> list[dict[str, int]]:
    return [
        {
            "job_id": job.job_id,
            "arrival_time": job.arrival_time,
            "burst_time": job.burst_time,
            "priority": job.priority,
        }
        for job in jobs
    ]


def _default_json_template() -> str:
    sample = [
        {"job_id": 0, "arrival_time": 0, "burst_time": 12, "priority": 0},
        {"job_id": 1, "arrival_time": 1, "burst_time": 4, "priority": 2},
        {"job_id": 2, "arrival_time": 3, "burst_time": 8, "priority": 1},
    ]
    return json.dumps(sample, indent=2)


if __name__ == "__main__":
    main()
