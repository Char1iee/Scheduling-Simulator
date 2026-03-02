# Workload-Driven Scheduling Evaluation

CS214 project: evaluate CPU scheduling policies across batch, interactive, and mixed workloads.

## Quick Start

```bash
python main.py
```

Runs all 6 schedulers on batch, interactive, and mixed workloads and prints a comparison table.

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

## Metrics

| Metric | Definition |
|---|---|
| **Avg Turnaround Time** | Mean of (completion_time - arrival_time) across all jobs. Measures batch efficiency. |
| **Avg Response Time** | Mean of (first_run_time - arrival_time). Measures interactive responsiveness. |
| **Tail Latency (p95)** | 95th percentile turnaround time. Captures worst-case user experience. |
| **Starvation Rate** | Fraction of jobs whose wait before first run exceeds a threshold. Measures long-wait risk. |

## Schedulers

### Round Robin
- Fixed time quantum shared equally among all jobs.
- FIFO ready queue; preempted jobs go to the back.

### SJF (Shortest Job First)
- Non-preemptive. Picks the job with the shortest burst time.
- Once a job starts, it runs to completion.

### SRTF (Shortest Remaining Time First)
- Preemptive variant of SJF. Preempts the running job when a new arrival has shorter remaining time.
- Sorts by remaining time, not original burst.

### Priority + Aging
- Highest effective priority runs first. Effective priority = base priority + aging bonus.
- Aging accumulates actual ready-queue wait time (excludes time spent running) to prevent starvation.
- Aging bonus: `min(max_bonus, (total_wait // interval) * 2)`.

### Lottery Scheduling
- Probabilistic selection. Each job holds `priority + 1` tickets.
- A random ticket is drawn each quantum; more tickets = higher chance of running.

### MLFQ (Multi-Level Feedback Queue)
- Rule 1: Higher-priority queue always runs first.
- Rule 2: Within a queue, jobs run in round-robin order.
- Rule 3: New jobs enter at the topmost queue (queue 0).
- Rule 4: After using its time allotment at a level, a job is demoted to the next lower queue.
- Rule 5: Periodic priority boost moves all jobs back to queue 0 to prevent starvation.
- Per-level quanta: [1, 2, 4] time units.

## Expected Results

Based on theoretical analysis from the project proposal:

| Scheduler | Turnaround Time | Response Time | Tail Latency | Starvation Rate |
|---|---|---|---|---|
| Round Robin | Medium | Medium | Medium | Low |
| Priority+Aging | Medium | Medium | Medium-High | Low |
| MLFQ | Medium | **Low** | Low | Medium |
| SJF / SRTF | **Low** | Medium | High | High |
| Lottery | Medium | Medium | Medium | Low |

**Batch workloads**: SJF/SRTF expected to achieve best turnaround. Round Robin and Lottery provide more stable fairness at higher turnaround cost.

**Interactive workloads**: MLFQ expected to perform best on response time. SJF/SRTF may harm responsiveness under frequent arrivals.

**Mixed workloads**: MLFQ protects interactive response time. Lottery and Priority+Aging allow explicit control over starvation. SJF/SRTF may improve average turnaround at the cost of fairness.

## Extending

- Add schedulers in `schedulers/` (subclass `Scheduler`)
- Add workloads in `workloads/generator.py`
- Tune parameters in `experiments/runner.py` (quantum, starvation threshold, etc.)
