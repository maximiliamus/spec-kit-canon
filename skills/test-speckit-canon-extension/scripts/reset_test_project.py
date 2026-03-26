#!/usr/bin/env python3
"""Reset and reinstall the Spec-Kit Canon test sandbox."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REQUIRED_DIRS = ("spec-kit", "spec-kit-canon", "spec-kit-canon-test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reset spec-kit-canon-test and reinstall the local extension and preset."
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        help="Workspace root that contains spec-kit, spec-kit-canon, and spec-kit-canon-test.",
    )
    parser.add_argument(
        "--project-name",
        default="Spec Kit Canon Test",
        help="Value to write into .specify/extensions/canon/canon-config.yml after install.",
    )
    parser.add_argument(
        "--clear-test-project",
        action="store_true",
        help="Delete the contents of spec-kit-canon-test before reinstalling the local extension and preset.",
    )
    return parser.parse_args()


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


def clear_directory(target: Path, workspace_root: Path) -> None:
    if target.name != "spec-kit-canon-test":
        raise SystemExit(f"Refusing to clear unexpected directory: {target}")
    if target.parent.resolve() != workspace_root.resolve():
        raise SystemExit(f"Refusing to clear directory outside the workspace root: {target}")

    target.mkdir(parents=True, exist_ok=True)
    for child in target.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def run(command: list[str], cwd: Path) -> None:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if result.returncode != 0:
        raise SystemExit(
            f"Command failed in {cwd}:\n"
            f"{' '.join(command)}\n\n"
            f"stdout:\n{result.stdout}\n\n"
            f"stderr:\n{result.stderr}"
        )


def update_canon_config(config_path: Path, project_name: str) -> None:
    text = config_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    for index, line in enumerate(lines):
        if line.strip() == "project:":
            next_index = index + 1
            if next_index >= len(lines) or not lines[next_index].lstrip().startswith("name:"):
                raise SystemExit(f"Unexpected canon config structure in {config_path}")
            escaped = project_name.replace('"', '\\"')
            indent = lines[next_index][: len(lines[next_index]) - len(lines[next_index].lstrip())]
            lines[next_index] = f'{indent}name: "{escaped}"'
            config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return

    raise SystemExit(f"Could not find project.name in {config_path}")


def main() -> int:
    args = parse_args()
    workspace_root = find_workspace_root(args.workspace_root)
    spec_kit_dir = workspace_root / "spec-kit"
    extension_dir = workspace_root / "spec-kit-canon"
    test_project_dir = workspace_root / "spec-kit-canon-test"

    if args.clear_test_project:
        clear_directory(test_project_dir, workspace_root)
    else:
        test_project_dir.mkdir(parents=True, exist_ok=True)

    run(
        [
            "uv",
            "run",
            "--project",
            "../spec-kit",
            "specify",
            "init",
            ".",
            "--ai",
            "codex",
            "--ai-skills",
            "--force",
        ],
        cwd=test_project_dir,
    )
    run(
        ["uv", "run", "--project", "../spec-kit", "specify", "extension", "add", "--dev", "../spec-kit-canon"],
        cwd=test_project_dir,
    )
    run(
        [
            "uv",
            "run",
            "--project",
            "../spec-kit",
            "specify",
            "preset",
            "add",
            "--dev",
            "../spec-kit-canon/presets/canon-core",
        ],
        cwd=test_project_dir,
    )

    canon_config = test_project_dir / ".specify" / "extensions" / "canon" / "canon-config.yml"
    update_canon_config(canon_config, args.project_name)

    summary = {
        "workspace_root": str(workspace_root),
        "spec_kit_dir": str(spec_kit_dir),
        "extension_dir": str(extension_dir),
        "test_project_dir": str(test_project_dir),
        "canon_config": str(canon_config),
        "constitution_path": str(test_project_dir / ".specify" / "memory" / "constitution.md"),
        "cleared_test_project": args.clear_test_project,
        "status": "ready_for_constitution",
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
