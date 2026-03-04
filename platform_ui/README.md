# Platform UI Extension

This directory is an extension layer for running scheduling experiments from a browser UI.
It reuses the existing simulator engine and scheduler implementations without changing their APIs.

## Features

- Define a workload manually (CSV or JSON in a text editor).
- Upload a workload file (`.csv` or `.json`).
- Use generated presets (`batch`, `interactive`, `mixed`) for quick baselines.
- Select one or more schedulers to compare in one run.
- Visualize results as a bar chart and choose which metric to plot.
- Export experiment metrics as CSV.

## Input Schema

Required fields:

- `arrival_time` (integer, `>= 0`)
- `burst_time` (integer, `>= 1`)

Optional fields:

- `job_id` (integer, unique; auto-assigned if omitted)
- `priority` (integer; defaults to `0`)

## Run

From the project root:

```bash
streamlit run platform_ui/app.py
```

Open the local Streamlit URL shown in terminal (usually `http://localhost:8501`).
