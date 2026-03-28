#!/usr/bin/env python3
"""Generate a Markdown report for the shared extension test workflow."""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import manage_progress


REPORT_FILE_NAME = "testing-spec-kit-canon-extension-report.md"
REPORT_STEP_ID = "generate_test_report"
DEFAULT_HISTORY_DIR = Path("tests") / "history"
MAX_HISTORY_REPORTS = 10
TIMESTAMPED_REPORT_PATTERN = re.compile(r"^\d{8}T\d{4}Z-testing-spec-kit-canon-extension-report\.md$")
CHECK_STARTERS = {
    "added",
    "canonized",
    "committed",
    "completed",
    "confirmed",
    "created",
    "generated",
    "hardened",
    "implemented",
    "patched",
    "passed",
    "produced",
    "reinstalled",
    "rendered",
    "reset",
    "seeded",
    "smoke-tested",
    "updated",
    "validated",
    "verified",
    "wrote",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a Markdown report from the shared test workflow progress file."
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        help="Workspace root that contains spec-kit, spec-kit-canon, and spec-kit-canon-test.",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        help="Project directory to report on. Defaults to <workspace-root>/spec-kit-canon-test.",
    )
    parser.add_argument(
        "--progress-file",
        type=Path,
        help="Explicit progress file path. Defaults to <project-dir>/.specify/tmp/testing-spec-kit-canon-extension-progress.json.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Markdown report path. Defaults to <project-dir>/.specify/tmp/testing-spec-kit-canon-extension-report.md.",
    )
    parser.add_argument(
        "--history-dir",
        type=Path,
        help=(
            "Directory for archived report copies. Defaults to "
            "<spec-kit-canon>/tests/history."
        ),
    )
    parser.add_argument(
        "--complete-step",
        action="store_true",
        help="Complete the final generate_test_report step before rendering the report.",
    )
    parser.add_argument(
        "--note",
        help="Completion note to record when --complete-step is used.",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Skip auto-opening the archived developer-history report copy after it is written.",
    )
    return parser.parse_args()


def resolve_output_path(project_dir: Path, progress_file: Path, output: Path | None) -> Path:
    if output is not None:
        return output.resolve()
    return (progress_file.parent if progress_file.parent.exists() else project_dir / ".specify" / "tmp") / REPORT_FILE_NAME


def resolve_history_dir(history_dir: Path | None, project_dir: Path) -> Path:
    if history_dir is not None:
        return history_dir.resolve()
    return (Path(__file__).resolve().parents[3] / DEFAULT_HISTORY_DIR).resolve()


def relative_path(path: Path, base_dir: Path) -> str:
    try:
        return os.path.relpath(path.resolve(), base_dir.resolve()).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def duration_seconds(started_at: str | None, ended_at: str | None) -> int | None:
    start_dt = parse_timestamp(started_at)
    end_dt = parse_timestamp(ended_at)
    if start_dt is None or end_dt is None:
        return None
    return max(0, int((end_dt - start_dt).total_seconds()))


def humanize_elapsed(total_seconds: int) -> str:
    total_seconds = max(0, total_seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def format_elapsed(started_at: str | None, completed_at: str | None) -> str:
    elapsed_seconds = duration_seconds(started_at, completed_at)
    if elapsed_seconds is None:
        return "-"
    return humanize_elapsed(elapsed_seconds)


def format_elapsed_seconds(total_seconds: int | None) -> str:
    if total_seconds is None:
        return "-"
    return humanize_elapsed(total_seconds)


def format_timestamp(value: str | None) -> str:
    return value if value else "-"


def report_timestamp(value: str | None) -> str:
    parsed = parse_timestamp(value)
    if parsed is None:
        parsed = datetime.now(timezone.utc)
    elif parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)
    return parsed.strftime("%Y%m%dT%H%MZ")


def select_timestamp(values: list[str], *, latest: bool) -> str | None:
    parsed_values: list[tuple[datetime, str]] = []
    for value in values:
        parsed = parse_timestamp(value)
        if parsed is None:
            continue
        parsed_values.append((parsed, value))

    if not parsed_values:
        return None
    selected = max(parsed_values, key=lambda item: item[0]) if latest else min(parsed_values, key=lambda item: item[0])
    return selected[1]


def archive_path(history_dir: Path, workflow_end: str | None) -> Path:
    stamp = report_timestamp(workflow_end)
    return history_dir / f"{stamp}-{REPORT_FILE_NAME}"


def list_timestamped_history_reports(history_dir: Path) -> list[Path]:
    if not history_dir.exists():
        return []
    return sorted(
        [
            path
            for path in history_dir.iterdir()
            if path.is_file() and TIMESTAMPED_REPORT_PATTERN.fullmatch(path.name)
        ],
        key=lambda path: path.name,
    )


def prune_history_reports(history_dir: Path, keep: int = MAX_HISTORY_REPORTS) -> None:
    reports = list_timestamped_history_reports(history_dir)
    if len(reports) <= keep:
        return
    for stale_report in reports[: len(reports) - keep]:
        stale_report.unlink(missing_ok=True)


def copy_report_to_history(output_path: Path, archived_path: Path) -> None:
    archived_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output_path, archived_path)
    prune_history_reports(archived_path.parent)


def auto_open_report(path: Path) -> str | None:
    try:
        if os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as exc:
        return str(exc)
    return None


def collect_step_history(state: dict) -> dict[str, dict[str, object]]:
    history_by_step: dict[str, dict[str, object]] = {
        step_id: {
            "first_started_at": None,
            "open_attempt_started_at": None,
            "completed_at": None,
            "start_note": None,
            "completion_note": None,
            "errors": [],
            "attempts": [],
        }
        for step_id in manage_progress.STEP_IDS
    }

    for entry in state.get("history", []):
        if not isinstance(entry, dict):
            continue
        step_id = entry.get("step_id")
        if step_id not in history_by_step:
            continue

        event = entry.get("event")
        timestamp = entry.get("timestamp") if isinstance(entry.get("timestamp"), str) else None
        note = entry.get("note") if isinstance(entry.get("note"), str) and entry.get("note", "").strip() else None
        step_history = history_by_step[step_id]
        attempts = step_history["attempts"]
        errors = step_history["errors"]

        if event == "started":
            if step_history["first_started_at"] is None:
                step_history["first_started_at"] = timestamp
            step_history["open_attempt_started_at"] = timestamp
            step_history["start_note"] = note
        elif event == "resumed":
            open_attempt_started_at = step_history.get("open_attempt_started_at")
            previous_updated_at = (
                entry.get("previous_updated_at")
                if isinstance(entry.get("previous_updated_at"), str)
                else None
            )
            if (
                isinstance(attempts, list)
                and isinstance(open_attempt_started_at, str)
                and previous_updated_at is not None
            ):
                attempts.append(
                    {
                        "started_at": open_attempt_started_at,
                        "ended_at": previous_updated_at,
                    }
                )
            step_history["open_attempt_started_at"] = timestamp
        elif event == "error":
            open_attempt_started_at = step_history.get("open_attempt_started_at")
            if (
                isinstance(attempts, list)
                and isinstance(open_attempt_started_at, str)
                and timestamp is not None
            ):
                attempts.append(
                    {
                        "started_at": open_attempt_started_at,
                        "ended_at": timestamp,
                    }
                )
            step_history["open_attempt_started_at"] = None
            if isinstance(errors, list):
                errors.append({"timestamp": timestamp, "note": note})
        elif event == "completed":
            open_attempt_started_at = step_history.get("open_attempt_started_at")
            if (
                isinstance(attempts, list)
                and isinstance(open_attempt_started_at, str)
                and timestamp is not None
            ):
                attempts.append(
                    {
                        "started_at": open_attempt_started_at,
                        "ended_at": timestamp,
                    }
                )
            step_history["open_attempt_started_at"] = None
            step_history["completed_at"] = timestamp
            step_history["completion_note"] = note

    return history_by_step


def text_value(step_history: dict[str, object], key: str) -> str | None:
    value = step_history.get(key)
    if isinstance(value, str) and value.strip():
        return value
    return None


def attempt_entries(step_history: dict[str, object]) -> list[dict[str, str]]:
    attempts = step_history.get("attempts")
    if isinstance(attempts, list):
        return [attempt for attempt in attempts if isinstance(attempt, dict)]
    return []


def error_entries(step_history: dict[str, object]) -> list[dict[str, str | None]]:
    errors = step_history.get("errors")
    if isinstance(errors, list):
        return [entry for entry in errors if isinstance(entry, dict)]
    return []


def step_elapsed_seconds(step_history: dict[str, object], fallback_end: str | None = None) -> int | None:
    total_seconds = 0
    has_duration = False

    for attempt in attempt_entries(step_history):
        elapsed_seconds = duration_seconds(
            attempt.get("started_at"),
            attempt.get("ended_at"),
        )
        if elapsed_seconds is None:
            continue
        total_seconds += elapsed_seconds
        has_duration = True

    open_attempt_started_at = step_history.get("open_attempt_started_at")
    if isinstance(open_attempt_started_at, str) and fallback_end is not None:
        elapsed_seconds = duration_seconds(open_attempt_started_at, fallback_end)
        if elapsed_seconds is not None:
            total_seconds += elapsed_seconds
            has_duration = True

    if not has_duration:
        return None
    return total_seconds


def count_step_errors(step_history: dict[str, object]) -> int:
    return len(error_entries(step_history))


def workflow_resume_gap_seconds(state: dict) -> int:
    total_seconds = 0
    for entry in state.get("history", []):
        if not isinstance(entry, dict) or entry.get("event") != "resumed":
            continue
        resumed_at = entry.get("timestamp") if isinstance(entry.get("timestamp"), str) else None
        previous_updated_at = (
            entry.get("previous_updated_at")
            if isinstance(entry.get("previous_updated_at"), str)
            else None
        )
        gap_seconds = duration_seconds(previous_updated_at, resumed_at)
        if gap_seconds is None:
            continue
        total_seconds += gap_seconds
    return total_seconds


def workflow_active_elapsed_seconds(
    state: dict,
    workflow_start: str | None,
    workflow_end: str | None,
) -> int | None:
    wall_clock_seconds = duration_seconds(workflow_start, workflow_end)
    if wall_clock_seconds is None:
        return None
    return max(0, wall_clock_seconds - workflow_resume_gap_seconds(state))


def latest_step_timestamp(state: dict, history_by_step: dict[str, dict[str, object]]) -> str | None:
    timestamps: list[str] = []
    for step_history in history_by_step.values():
        first_started_at = text_value(step_history, "first_started_at")
        completed_at = text_value(step_history, "completed_at")
        open_attempt_started_at = text_value(step_history, "open_attempt_started_at")
        if first_started_at is not None:
            timestamps.append(first_started_at)
        if completed_at is not None:
            timestamps.append(completed_at)
        if open_attempt_started_at is not None:
            timestamps.append(open_attempt_started_at)
        for error in error_entries(step_history):
            error_timestamp = error.get("timestamp")
            if isinstance(error_timestamp, str):
                timestamps.append(error_timestamp)

    selected = select_timestamp(timestamps, latest=True)
    if selected is not None:
        return selected
    updated_at = state.get("updated_at")
    return updated_at if isinstance(updated_at, str) else None


def workflow_start_timestamp(history_by_step: dict[str, dict[str, object]]) -> str | None:
    started_at_values = [
        started_at
        for step_history in history_by_step.values()
        if (started_at := text_value(step_history, "first_started_at")) is not None
    ]
    return select_timestamp(started_at_values, latest=False)


def summarize_result_text(
    step_id: str,
    status: str,
    step_history: dict[str, object],
    current_step: str | None,
) -> str:
    completion_note = text_value(step_history, "completion_note")
    if completion_note:
        return completion_note

    start_note = text_value(step_history, "start_note")
    if status == "completed":
        return "Completed with no result note recorded."
    if status == "in_progress":
        return start_note or "Currently in progress."
    if current_step == step_id:
        if count_step_errors(step_history):
            return "Ready to retry after a recorded error."
        return "Ready to resume from this step."
    return "Not started yet."


def split_result_checks(text: str) -> list[str]:
    normalized = " ".join(text.strip().split())
    if not normalized:
        return []

    items: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+", normalized):
        sentence = sentence.strip().rstrip(".")
        if not sentence:
            continue
        current_item = ""
        for clause in sentence.split(","):
            cleaned = clause.strip()
            if not cleaned:
                continue

            lower_cleaned = cleaned.lower()
            if lower_cleaned.startswith("and "):
                cleaned = cleaned[4:].strip()
                lower_cleaned = cleaned.lower()

            if lower_cleaned.startswith("also "):
                cleaned = cleaned[5:].strip()
                lower_cleaned = cleaned.lower()

            first_word = lower_cleaned.split(maxsplit=1)[0]
            starts_new_check = (
                not current_item
                or first_word in CHECK_STARTERS
                or first_word.endswith("ed")
                or first_word.endswith("ing")
            )

            if starts_new_check:
                if current_item:
                    items.append(current_item)
                current_item = cleaned
            else:
                current_item = f"{current_item}, {cleaned}"

        if current_item:
            items.append(current_item)

    return items or [normalized.rstrip(".")]


def summarize_result_items(
    step_id: str,
    status: str,
    step_history: dict[str, object],
    current_step: str | None,
) -> list[str]:
    return split_result_checks(summarize_result_text(step_id, status, step_history, current_step))


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def format_result_cell(items: list[str]) -> str:
    if not items:
        return "-"
    return "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in items) + "</ul>"


def format_result_section(items: list[str]) -> list[str]:
    if not items:
        return ["- No checks recorded."]
    return [f"- {item}" for item in items]


def format_error_section(entries: list[dict[str, str | None]]) -> list[str]:
    if not entries:
        return ["- No recorded errors."]
    lines: list[str] = []
    for entry in entries:
        timestamp = entry.get("timestamp") if isinstance(entry.get("timestamp"), str) else None
        note = entry.get("note") if isinstance(entry.get("note"), str) and entry.get("note", "").strip() else None
        lines.append(f"- `{format_timestamp(timestamp)}`: {note or 'Error recorded with no note.'}")
    return lines


def format_percentage(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "-"
    return f"{(numerator / denominator) * 100:.1f}%"


def build_assessment(state: dict, error_count: int) -> str:
    status = state.get("status")
    current_step = state.get("current_step")
    error_suffix = ""
    if error_count:
        error_suffix = f" Recorded errors so far: {error_count}."

    if status == "completed":
        return (
            "The workflow is fully completed and the report reflects the full validation run."
            f"{error_suffix}"
        )
    if status == "in_progress":
        title = manage_progress.STEP_TITLES.get(current_step, current_step or "unknown step")
        return f"The workflow is still running. Current step: {title}.{error_suffix}"
    if current_step:
        title = manage_progress.STEP_TITLES.get(current_step, current_step)
        return f"The workflow is paused and ready to resume from {title}.{error_suffix}"
    return f"The workflow state is incomplete.{error_suffix}"


def build_report(
    state: dict,
    project_dir: Path,
    progress_file: Path,
    output_path: Path,
    archived_path: Path,
) -> str:
    history_by_step = collect_step_history(state)
    steps = state["steps"]
    current_step = state.get("current_step")
    script = state.get("script", "-")
    relative_progress_file = relative_path(progress_file, project_dir)
    relative_output_path = relative_path(output_path, project_dir)
    relative_archived_path = relative_path(archived_path, project_dir)

    completed_count = sum(1 for step in steps if step["status"] == "completed")
    in_progress_count = sum(1 for step in steps if step["status"] == "in_progress")
    pending_count = sum(1 for step in steps if step["status"] == "pending")
    total_steps = len(steps)
    error_count = sum(count_step_errors(history_by_step[step["id"]]) for step in steps)
    steps_with_errors = sum(1 for step in steps if count_step_errors(history_by_step[step["id"]]) > 0)
    current_step_title = manage_progress.STEP_TITLES.get(current_step, current_step) if current_step else "None"
    workflow_start = workflow_start_timestamp(history_by_step)
    workflow_end = latest_step_timestamp(state, history_by_step)
    workflow_wall_clock = format_elapsed(workflow_start, workflow_end)
    workflow_active_elapsed = format_elapsed_seconds(
        workflow_active_elapsed_seconds(state, workflow_start, workflow_end)
    )

    lines = [
        "# Testing Spec-Kit Canon Extension Report",
        "",
        f"Generated from `{relative_progress_file}`.",
        f"Start time: `{format_timestamp(workflow_start)}`",
        f"End time: `{format_timestamp(workflow_end)}`",
        "",
        "| Workflow | Script | Status | Completed | In Progress | Pending | Current Step | Active Elapsed |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        (
            f"| `{state['workflow']}` | `{script}` | `{state['status']}` | {completed_count}/{total_steps} | "
            f"{in_progress_count} | {pending_count} | {escape_cell(current_step_title)} | "
            f"{workflow_active_elapsed} |"
        ),
        "",
        build_assessment(state, error_count),
        "",
        "Elapsed metrics count workflow wall-clock time minus explicit idle gaps recorded when a run is resumed.",
        "",
        "## Test Run Metrics",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Total steps | {total_steps} |",
        f"| Passed steps | {completed_count} |",
        f"| Pass rate | {format_percentage(completed_count, total_steps)} |",
        f"| Recorded errors | {error_count} |",
        f"| Steps with errors | {steps_with_errors} |",
        f"| Total active elapsed | {workflow_active_elapsed} |",
        f"| Wall-clock span | {workflow_wall_clock} |",
        "",
        "## Step Summary",
        "",
        "| # | Step | Status | Errors | Elapsed | Result |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for index, step in enumerate(steps, start=1):
        step_history = history_by_step[step["id"]]
        result_items = summarize_result_items(step["id"], step["status"], step_history, current_step)
        elapsed = format_elapsed_seconds(step_elapsed_seconds(step_history, workflow_end))
        lines.append(
            "| "
            + " | ".join(
                [
                    str(index),
                    escape_cell(f"{step['title']} (`{step['id']}`)"),
                    escape_cell(step["status"]),
                    str(count_step_errors(step_history)),
                    elapsed,
                    format_result_cell(result_items),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Step Results",
            "",
        ]
    )

    for index, step in enumerate(steps, start=1):
        step_history = history_by_step[step["id"]]
        result_items = summarize_result_items(step["id"], step["status"], step_history, current_step)
        errors = error_entries(step_history)
        lines.extend(
            [
                f"### {index}. {step['title']} (`{step['id']}`)",
                "",
                f"Status: `{step['status']}`",
                f"Elapsed: {format_elapsed_seconds(step_elapsed_seconds(step_history, workflow_end))}",
                f"Errors: {len(errors)}",
            ]
        )
        if errors:
            lines.extend(
                [
                    "Recorded errors:",
                    *format_error_section(errors),
                ]
            )
        lines.extend(
            [
                "Checks:",
                *format_result_section(result_items),
                "",
            ]
        )

    lines.extend(
        [
            "## Report Artifact",
            "",
            f"The rendered Markdown report is stored at `{relative_output_path}`.",
            f"A developer-history copy is stored at `{relative_archived_path}`.",
            f"History keeps up to the newest {MAX_HISTORY_REPORTS} timestamped archived copies.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    _workspace_root, project_dir, progress_file = manage_progress.resolve_paths(args)
    output_path = resolve_output_path(project_dir, progress_file, args.output)
    history_dir = resolve_history_dir(args.history_dir, project_dir)

    if args.complete_step:
        state = manage_progress.handle_complete(progress_file, REPORT_STEP_ID, args.note)
    else:
        state = manage_progress.load_state(progress_file)

    history_by_step = collect_step_history(state)
    workflow_end = latest_step_timestamp(state, history_by_step)
    archived_path = archive_path(history_dir, workflow_end)
    report = build_report(state, project_dir, progress_file, output_path, archived_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report + "\n", encoding="utf-8")
    copy_report_to_history(output_path, archived_path)

    print(f"Wrote report to {output_path}")
    print(f"Archived report to {archived_path}")

    if not args.no_open:
        open_error = auto_open_report(archived_path)
        if open_error is not None:
            print(f"Could not open archived report automatically: {open_error}")
        else:
            print(f"Opened archived report {archived_path}")

    print()
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
