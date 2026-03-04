"""Workload parsing and validation helpers for the platform UI."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from typing import Any

from models.job import Job


@dataclass
class WorkloadParseResult:
    jobs: list[Job]
    source_summary: str


REQUIRED_COLUMNS = {"arrival_time", "burst_time"}


def parse_workload_text(content: str, fmt: str) -> WorkloadParseResult:
    """Parse workload data from text in CSV or JSON format."""
    fmt = fmt.lower().strip()
    if fmt == "csv":
        rows = _parse_csv_rows(content)
    elif fmt == "json":
        rows = _parse_json_rows(content)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    jobs = _rows_to_jobs(rows)
    return WorkloadParseResult(jobs=jobs, source_summary=f"{len(jobs)} jobs from {fmt.upper()}")


def parse_workload_upload(filename: str, payload: bytes) -> WorkloadParseResult:
    """Parse uploaded workload file based on extension."""
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix not in {"csv", "json"}:
        raise ValueError("Upload must be a .csv or .json file")

    text = payload.decode("utf-8")
    return parse_workload_text(text, suffix)


def _parse_csv_rows(content: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        raise ValueError("CSV appears to be empty")

    columns = {c.strip() for c in reader.fieldnames if c is not None}
    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise ValueError(
            "CSV is missing required columns: " + ", ".join(sorted(missing))
        )

    rows: list[dict[str, Any]] = []
    for row in reader:
        rows.append({(k.strip() if k else ""): (v.strip() if isinstance(v, str) else v) for k, v in row.items()})
    if not rows:
        raise ValueError("CSV has a header but no rows")
    return rows


def _parse_json_rows(content: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as err:
        raise ValueError(f"Invalid JSON: {err.msg}") from err

    if not isinstance(payload, list) or not payload:
        raise ValueError("JSON must be a non-empty array of job objects")

    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"JSON entry {idx} must be an object")
        rows.append(item)

    columns = set().union(*(row.keys() for row in rows))
    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise ValueError(
            "JSON is missing required fields: " + ", ".join(sorted(missing))
        )
    return rows


def _rows_to_jobs(rows: list[dict[str, Any]]) -> list[Job]:
    jobs: list[Job] = []
    used_job_ids: set[int] = set()

    for idx, row in enumerate(rows):
        arrival = _read_int(row, "arrival_time", idx, minimum=0)
        burst = _read_int(row, "burst_time", idx, minimum=1)

        has_job_id = "job_id" in row and str(row["job_id"]).strip() != ""
        if has_job_id:
            job_id = _read_int(row, "job_id", idx, minimum=0)
        else:
            job_id = idx

        if job_id in used_job_ids:
            raise ValueError(f"Duplicate job_id={job_id} at row {idx + 1}")
        used_job_ids.add(job_id)

        if "priority" in row and str(row["priority"]).strip() != "":
            priority = _read_int(row, "priority", idx)
        else:
            priority = 0

        jobs.append(
            Job(
                job_id=job_id,
                arrival_time=arrival,
                burst_time=burst,
                priority=priority,
            )
        )

    jobs.sort(key=lambda j: (j.arrival_time, j.job_id))
    return jobs


def _read_int(
    row: dict[str, Any],
    key: str,
    row_idx: int,
    minimum: int | None = None,
) -> int:
    value = row.get(key)
    if value is None or str(value).strip() == "":
        raise ValueError(f"Missing '{key}' in row {row_idx + 1}")

    try:
        value_int = int(str(value).strip())
    except ValueError as err:
        raise ValueError(f"Invalid integer for '{key}' in row {row_idx + 1}") from err

    if minimum is not None and value_int < minimum:
        raise ValueError(
            f"'{key}' in row {row_idx + 1} must be >= {minimum}"
        )

    return value_int
