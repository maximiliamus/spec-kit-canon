#!/usr/bin/env python3
"""Track resumable progress for the test-speckit-canon-extension workflow."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_DIRS = ("spec-kit", "spec-kit-canon", "spec-kit-canon-test")
WORKFLOW_NAME = "test-speckit-canon-extension"
PROGRESS_FILE_NAME = "test-speckit-canon-extension-progress.json"
STEP_DEFINITIONS = (
    ("reset_sandbox", "Reset the sandbox project"),
    ("verify_constitution_config", "Run constitution and verify config-driven rendering"),
    ("initialize_canon", "Initialize the canon baseline"),
    ("standard_feature_workflow", "Run the standard feature workflow"),
    ("api_drift", "Add update todo and run standard drift"),
    ("merge_to_master", "Merge the first branch back to master"),
    ("web_ui_vibecode", "Run the vibecode web UI pass"),
    ("verify_final_canon", "Verify the final canon"),
)
STEP_IDS = {step_id for step_id, _title in STEP_DEFINITIONS}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create, inspect, and update the shared test workflow progress file."
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        help="Workspace root that contains spec-kit, spec-kit-canon, and spec-kit-canon-test.",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        help="Project directory to track. Defaults to <workspace-root>/spec-kit-canon-test.",
    )
    parser.add_argument(
        "--progress-file",
        type=Path,
        help="Explicit progress file path. Defaults to <project-dir>/.specify/tmp/test-speckit-canon-extension-progress.json.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create or refresh the workflow progress file.")
    init_parser.add_argument(
        "--clear-test-project",
        action="store_true",
        help="Reset the progress file to step 1 and record that the sandbox should be fully cleared.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite any existing progress file even without --clear-test-project.",
    )

    subparsers.add_parser("show", help="Print the current workflow progress state.")

    start_parser = subparsers.add_parser("start", help="Mark the current step as in progress.")
    start_parser.add_argument("step_id", choices=sorted(STEP_IDS), help="Step identifier to start.")
    start_parser.add_argument("--note", help="Optional note to append to the history entry.")

    complete_parser = subparsers.add_parser("complete", help="Mark the current step as completed.")
    complete_parser.add_argument("step_id", choices=sorted(STEP_IDS), help="Step identifier to complete.")
    complete_parser.add_argument("--note", help="Optional note to append to the history entry.")

    return parser.parse_args()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def find_workspace_root(explicit_root: Path | None) -> Path:
    candidates: list[Path] = []
    if explicit_root is not None:
        candidates.append(explicit_root)
    cwd = Path.cwd().resolve()
    candidates.extend([cwd, cwd.parent])

    for candidate in candidates:
        resolved = candidate.resolve()
        if all((resolved / name).is_dir() for name in REQUIRED_DIRS):
            return resolved

    joined = ", ".join(REQUIRED_DIRS)
    raise SystemExit(
        f"Could not find a workspace root containing {joined}. "
        "Run this script from spec-kit-canon or pass --workspace-root."
    )


def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    workspace_root = find_workspace_root(args.workspace_root)
    project_dir = args.project_dir.resolve() if args.project_dir else workspace_root / "spec-kit-canon-test"
    progress_file = args.progress_file.resolve() if args.progress_file else project_dir / ".specify" / "tmp" / PROGRESS_FILE_NAME
    return workspace_root, project_dir, progress_file


def build_steps() -> list[dict[str, str]]:
    return [{"id": step_id, "title": title, "status": "pending"} for step_id, title in STEP_DEFINITIONS]


def build_state(workspace_root: Path, project_dir: Path, progress_file: Path, clear_test_project: bool) -> dict:
    current_step = STEP_DEFINITIONS[0][0]
    timestamp = now_iso()
    return {
        "workflow": WORKFLOW_NAME,
        "version": 2,
        "workspace_root": str(workspace_root),
        "project_dir": str(project_dir),
        "progress_file": str(progress_file),
        "clear_test_project": clear_test_project,
        "status": "ready",
        "current_step": current_step,
        "steps": build_steps(),
        "history": [
            {
                "event": "initialized",
                "timestamp": timestamp,
                "clear_test_project": clear_test_project,
            }
        ],
        "updated_at": timestamp,
    }


def ensure_step_structure(state: dict) -> None:
    steps = state.get("steps")
    if not isinstance(steps, list):
        raise SystemExit("Invalid progress file: missing steps list.")
    known = {item.get("id") for item in steps if isinstance(item, dict)}
    if known != STEP_IDS:
        raise SystemExit(
            "Invalid progress file: step ids do not match the current workflow. "
            "Re-run manage_progress.py init --force to refresh the state for the current step set."
        )


def load_state(progress_file: Path) -> dict:
    if not progress_file.is_file():
        raise SystemExit(
            f"Missing progress file: {progress_file}\n"
            "Run manage_progress.py init before attempting to resume the workflow."
        )
    state = json.loads(progress_file.read_text(encoding="utf-8"))
    if state.get("workflow") != WORKFLOW_NAME:
        raise SystemExit(f"Unexpected workflow name in {progress_file}")
    ensure_step_structure(state)
    return state


def write_state(progress_file: Path, state: dict) -> None:
    progress_file.parent.mkdir(parents=True, exist_ok=True)
    state["progress_file"] = str(progress_file)
    state["updated_at"] = now_iso()
    progress_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def set_step_statuses(state: dict, *, current_step: str | None, active_status: str | None = None) -> None:
    for step in state["steps"]:
        if step["status"] == "completed":
            continue
        if step["id"] == current_step:
            step["status"] = active_status or "pending"
        else:
            step["status"] = "pending"
    state["current_step"] = current_step


def find_next_pending_step(state: dict) -> str | None:
    for step_id, _title in STEP_DEFINITIONS:
        for step in state["steps"]:
            if step["id"] == step_id and step["status"] != "completed":
                return step_id
    return None


def get_step(state: dict, step_id: str) -> dict:
    for step in state["steps"]:
        if step["id"] == step_id:
            return step
    raise SystemExit(f"Unknown step id: {step_id}")


def append_history(state: dict, event: str, step_id: str | None = None, note: str | None = None) -> None:
    entry: dict[str, object] = {"event": event, "timestamp": now_iso()}
    if step_id is not None:
        entry["step_id"] = step_id
    if note:
        entry["note"] = note
    state["history"].append(entry)


def handle_init(args: argparse.Namespace, workspace_root: Path, project_dir: Path, progress_file: Path) -> dict:
    if progress_file.exists() and not args.force and not args.clear_test_project:
        state = load_state(progress_file)
        state["workspace_root"] = str(workspace_root)
        state["project_dir"] = str(project_dir)
        write_state(progress_file, state)
        return state

    state = build_state(workspace_root, project_dir, progress_file, args.clear_test_project)
    write_state(progress_file, state)
    return state


def handle_show(progress_file: Path) -> dict:
    return load_state(progress_file)


def handle_start(progress_file: Path, step_id: str, note: str | None) -> dict:
    state = load_state(progress_file)
    current_step = state.get("current_step")
    if current_step is None:
        raise SystemExit("Workflow is already completed. Re-run init --force to start over.")
    if current_step != step_id:
        raise SystemExit(
            f"Cannot start step {step_id!r}; current resumable step is {current_step!r}."
        )

    step = get_step(state, step_id)
    if step["status"] == "completed":
        raise SystemExit(f"Step {step_id!r} is already completed.")

    set_step_statuses(state, current_step=step_id, active_status="in_progress")
    state["status"] = "in_progress"
    append_history(state, "started", step_id=step_id, note=note)
    write_state(progress_file, state)
    return state


def handle_complete(progress_file: Path, step_id: str, note: str | None) -> dict:
    state = load_state(progress_file)
    current_step = state.get("current_step")
    if current_step != step_id:
        raise SystemExit(
            f"Cannot complete step {step_id!r}; current resumable step is {current_step!r}."
        )

    step = get_step(state, step_id)
    if step["status"] == "completed":
        raise SystemExit(f"Step {step_id!r} is already completed.")

    step["status"] = "completed"
    next_step = find_next_pending_step(state)
    if next_step is None:
        state["current_step"] = None
        state["status"] = "completed"
    else:
        set_step_statuses(state, current_step=next_step)
        state["status"] = "ready"

    append_history(state, "completed", step_id=step_id, note=note)
    write_state(progress_file, state)
    return state


def main() -> int:
    args = parse_args()
    workspace_root, project_dir, progress_file = resolve_paths(args)

    if args.command == "init":
        state = handle_init(args, workspace_root, project_dir, progress_file)
    elif args.command == "show":
        state = handle_show(progress_file)
    elif args.command == "start":
        state = handle_start(progress_file, args.step_id, args.note)
    elif args.command == "complete":
        state = handle_complete(progress_file, args.step_id, args.note)
    else:
        raise SystemExit(f"Unsupported command: {args.command}")

    print(json.dumps(state, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
