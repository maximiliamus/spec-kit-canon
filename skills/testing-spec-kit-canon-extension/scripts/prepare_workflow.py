#!/usr/bin/env python3
"""Prepare the shared test workflow for resume or restart."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import manage_progress


DOCUMENTED_DEFAULT_SCRIPT = "sh"
REPORT_FILE_NAME = "testing-spec-kit-canon-extension-report.md"
COMPLETED_REPORT_MARKER = "The workflow is fully completed and the report reflects the full validation run."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Resume the existing testing workflow by default, or initialize a fresh "
            "run when no progress exists, the workflow already completed, or "
            "--restart is requested."
        )
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
        help=(
            "Explicit progress file path. Defaults to "
            "<project-dir>/.specify/tmp/testing-spec-kit-canon-extension-progress.json."
        ),
    )
    parser.add_argument(
        "--script",
        choices=sorted(manage_progress.VALID_SCRIPT_TYPES),
        help="Persist or restart with the requested Spec Kit script variant: sh or ps.",
    )
    parser.add_argument(
        "--restart",
        action="store_true",
        help="Force a fresh run even when the workflow already has resumable progress.",
    )
    return parser.parse_args()


def build_init_args(script: str, *, from_scratch: bool) -> SimpleNamespace:
    return SimpleNamespace(
        command="init",
        workspace_root=None,
        project_dir=None,
        progress_file=None,
        clear_test_project=from_scratch,
        force=from_scratch,
        script=script,
    )


def pick_fresh_script(args: argparse.Namespace, existing_state: dict | None) -> str:
    if args.script:
        return args.script
    if existing_state:
        existing_script = existing_state.get("script")
        if existing_script in manage_progress.VALID_SCRIPT_TYPES:
            return existing_script
    return DOCUMENTED_DEFAULT_SCRIPT


def build_resume_args(args: argparse.Namespace) -> SimpleNamespace:
    return SimpleNamespace(
        command="init",
        workspace_root=None,
        project_dir=None,
        progress_file=None,
        clear_test_project=False,
        force=False,
        script=args.script,
    )


def report_path_for_project(project_dir: Path) -> Path:
    return project_dir / ".specify" / "tmp" / REPORT_FILE_NAME


def newer_completed_report_exists(project_dir: Path, progress_file: Path) -> bool:
    report_file = report_path_for_project(project_dir)
    if not report_file.is_file() or not progress_file.is_file():
        return False

    try:
        if report_file.stat().st_mtime <= progress_file.stat().st_mtime:
            return False
        report_text = report_file.read_text(encoding="utf-8")
    except OSError:
        return False

    return COMPLETED_REPORT_MARKER in report_text


def main() -> int:
    args = parse_args()
    workspace_root, project_dir, progress_file = manage_progress.resolve_paths(args)
    existing_state = manage_progress.load_state(progress_file) if progress_file.exists() else None
    stale_completed_report = (
        existing_state is not None
        and existing_state.get("status") != "completed"
        and newer_completed_report_exists(project_dir, progress_file)
    )

    if args.restart:
        state = manage_progress.handle_init(
            build_init_args(pick_fresh_script(args, existing_state), from_scratch=True),
            workspace_root,
            project_dir,
            progress_file,
        )
        result = {
            "action": "started_from_scratch",
            "reason": "Explicit --restart flag requested a fresh run.",
            "state": state,
        }
    elif existing_state is None:
        state = manage_progress.handle_init(
            build_init_args(pick_fresh_script(args, None), from_scratch=True),
            workspace_root,
            project_dir,
            progress_file,
        )
        result = {
            "action": "initialized_new_run",
            "reason": "No progress file existed, so the workflow was initialized from scratch.",
            "state": state,
        }
    elif stale_completed_report:
        state = manage_progress.handle_init(
            build_init_args(pick_fresh_script(args, existing_state), from_scratch=True),
            workspace_root,
            project_dir,
            progress_file,
        )
        result = {
            "action": "restarted_stale_run",
            "reason": (
                "A newer completed report exists for this workflow, so the unfinished progress file "
                "was treated as stale and a fresh run was initialized."
            ),
            "state": state,
        }
    elif existing_state.get("status") == "completed":
        state = manage_progress.handle_init(
            build_init_args(pick_fresh_script(args, existing_state), from_scratch=True),
            workspace_root,
            project_dir,
            progress_file,
        )
        result = {
            "action": "restarted_completed_run",
            "reason": "The previous workflow was fully completed, so a fresh run was initialized.",
            "state": state,
        }
    else:
        if existing_state.get("status") == "in_progress":
            manage_progress.handle_resume(
                progress_file,
                note="Recorded a resumed workflow session so elapsed-time reporting excludes the prior idle gap.",
            )
        state = manage_progress.handle_init(
            build_resume_args(args),
            workspace_root,
            project_dir,
            progress_file,
        )
        result = {
            "action": "resumed_existing_run",
            "reason": "Existing workflow progress is still active, so execution should continue from the current step.",
            "state": state,
        }

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
