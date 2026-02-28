# Workload-Driven Scheduling Evaluation

CS214 project: evaluate CPU scheduling policies across batch, interactive, and mixed workloads.

## Project Structure

```
Scheduling-Simulator/
├── models/           # Job, Event data structures
├── schedulers/       # Round Robin, SJF, SRTF, Priority+Aging, Lottery, MLFQ
├── simulation/       # Engine + metrics
├── workloads/        # Batch, interactive, mixed workload generators
├── experiments/      # Runner + comparison
├── main.py
└── requirements.txt
```

## Quick Start

```bash
python main.py
```

Runs all 6 schedulers on batch, interactive, and mixed workloads and prints a comparison table.

## Metrics

- **Avg TT** – Average turnaround time
- **Avg RT** – Average response time  
- **Tail p95** – 95th percentile turnaround time
- **Starvation** – Fraction of jobs waiting > threshold before first run

## Extending

- Add schedulers in `schedulers/` (subclass `Scheduler`)
- Add workloads in `workloads/generator.py`
- Tune parameters in `experiments/runner.py` (quantum, starvation threshold, etc.)
