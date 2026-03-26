#!/usr/bin/env python3
"""Copy the bundled canon template into the test project's canon root."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_DIRS = ("spec-kit", "spec-kit-canon", "spec-kit-canon-test")
PLACEHOLDER_PROJECT = "[PROJECT_NAME]"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy the shared canon template into the configured canon root."
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        help="Workspace root that contains spec-kit, spec-kit-canon, and spec-kit-canon-test.",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        help="Project directory to seed. Defaults to <workspace-root>/spec-kit-canon-test.",
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


def read_config_value(lines: list[str], section: str, key: str) -> str | None:
    in_section = False
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and stripped.endswith(":"):
            in_section = stripped[:-1] == section
            continue
        if in_section and stripped.startswith(f"{key}:"):
            value = stripped.split(":", 1)[1].strip().strip('"')
            return value
    return None


def load_project_settings(project_dir: Path) -> tuple[str, Path]:
    config_path = project_dir / ".specify" / "extensions" / "canon" / "canon-config.yml"
    if not config_path.is_file():
        raise SystemExit(f"Missing canon config: {config_path}")

    lines = config_path.read_text(encoding="utf-8").splitlines()
    project_name = read_config_value(lines, "project", "name") or project_dir.name
    canon_root_value = read_config_value(lines, "canon", "root") or "specs/000-canon"
    canon_root_path = Path(canon_root_value)
    canon_root = canon_root_path if canon_root_path.is_absolute() else project_dir / canon_root_path

    return project_name, canon_root


def main() -> int:
    args = parse_args()
    workspace_root = find_workspace_root(args.workspace_root)
    project_dir = args.project_dir.resolve() if args.project_dir else workspace_root / "spec-kit-canon-test"
    skill_dir = Path(__file__).resolve().parent.parent
    template_dir = skill_dir / "assets" / "canon-template"

    if not template_dir.is_dir():
        raise SystemExit(f"Missing canon template directory: {template_dir}")

    project_name, canon_root = load_project_settings(project_dir)
    canon_root.mkdir(parents=True, exist_ok=True)

    written_files: list[str] = []
    for source_path in sorted(template_dir.glob("*.md")):
        target_path = canon_root / source_path.name
        rendered = source_path.read_text(encoding="utf-8").replace(PLACEHOLDER_PROJECT, project_name)
        target_path.write_text(rendered, encoding="utf-8")
        written_files.append(str(target_path))

    print(
        json.dumps(
            {
                "project_dir": str(project_dir),
                "project_name": project_name,
                "canon_root": str(canon_root),
                "written_files": written_files,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
