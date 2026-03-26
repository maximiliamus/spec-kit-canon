#!/usr/bin/env python3
"""Reset and reinstall the Spec-Kit Canon test sandbox."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path


REQUIRED_DIRS = ("spec-kit", "spec-kit-canon", "spec-kit-canon-test")
PROGRESS_FILE_RELATIVE = Path(".specify") / "tmp" / "test-speckit-canon-extension-progress.json"
DEFAULT_CONFIG_FIXTURE = Path("assets") / "constitution-config-fixture.json"


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
        "--config-fixture",
        type=Path,
        help="JSON fixture that defines the canon config values to write after install.",
    )
    parser.add_argument(
        "--project-name",
        help="Optional override for project.name from the config fixture.",
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

    preserved_progress: str | None = None
    progress_file = target / PROGRESS_FILE_RELATIVE
    if progress_file.is_file():
        preserved_progress = progress_file.read_text(encoding="utf-8")

    target.mkdir(parents=True, exist_ok=True)
    for child in target.iterdir():
        if child.is_dir():
            shutil.rmtree(child, onexc=handle_remove_readonly)
        else:
            child.unlink()

    if preserved_progress is not None:
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_file.write_text(preserved_progress, encoding="utf-8")


def handle_remove_readonly(function, path: str, excinfo) -> None:
    os.chmod(path, stat.S_IWRITE)
    function(path)


def default_config_fixture_path() -> Path:
    return Path(__file__).resolve().parent.parent / DEFAULT_CONFIG_FIXTURE


def load_config_fixture(config_fixture: Path) -> dict:
    try:
        raw = json.loads(config_fixture.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing constitution config fixture: {config_fixture}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in constitution config fixture {config_fixture}: {exc}") from exc

    if not isinstance(raw, dict):
        raise SystemExit(f"Constitution config fixture must contain a JSON object: {config_fixture}")

    project = raw.get("project")
    canon = raw.get("canon")
    branching = raw.get("branching")
    if not isinstance(project, dict) or not isinstance(canon, dict) or not isinstance(branching, dict):
        raise SystemExit(
            "Constitution config fixture must contain project, canon, and branching objects."
        )

    project_name = project.get("name")
    canon_root = canon.get("root")
    branch_types = branching.get("types")
    branch_scopes = branching.get("scopes")
    if branch_scopes is None:
        branch_scopes = branching.get("areas")

    if not isinstance(project_name, str) or not project_name.strip():
        raise SystemExit("Constitution config fixture project.name must be a non-empty string.")
    if not isinstance(canon_root, str) or not canon_root.strip():
        raise SystemExit("Constitution config fixture canon.root must be a non-empty string.")
    if not isinstance(branch_types, list) or not branch_types:
        raise SystemExit("Constitution config fixture branching.types must be a non-empty list.")
    if not isinstance(branch_scopes, list) or not branch_scopes:
        raise SystemExit(
            "Constitution config fixture branching.scopes must be a non-empty list."
        )

    normalized_types: list[dict[str, str]] = []
    for item in branch_types:
        if not isinstance(item, dict):
            raise SystemExit("Each branching.types entry in the config fixture must be an object.")
        code = item.get("code")
        classification = item.get("classification")
        if not isinstance(code, str) or not code.strip():
            raise SystemExit("Each branching.types entry must define a non-empty code.")
        if not isinstance(classification, str) or not classification.strip():
            raise SystemExit("Each branching.types entry must define a non-empty classification.")
        normalized_types.append(
            {"code": code.strip(), "classification": classification.strip()}
        )

    normalized_scopes: list[dict[str, str]] = []
    for item in branch_scopes:
        if not isinstance(item, dict):
            raise SystemExit("Each branching.scopes entry in the config fixture must be an object.")
        code = item.get("code")
        description = item.get("description")
        if not isinstance(code, str) or not code.strip():
            raise SystemExit("Each branching.scopes entry must define a non-empty code.")
        if not isinstance(description, str) or not description.strip():
            raise SystemExit("Each branching.scopes entry must define a non-empty description.")
        normalized_scopes.append({"code": code.strip(), "description": description.strip()})

    return {
        "project": {"name": project_name.strip()},
        "canon": {"root": canon_root.strip()},
        "branching": {"types": normalized_types, "scopes": normalized_scopes},
    }


def quote_yaml(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


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


def initialize_test_project(spec_kit_dir: Path, test_project_dir: Path) -> None:
    script_type = "ps" if os.name == "nt" else "sh"
    inline_script = f"""
import importlib
import json
from pathlib import Path

cli = importlib.import_module("specify_cli.__init__")
project = Path.cwd()

ok = cli.scaffold_from_core_pack(project, "codex", "{script_type}", True)
if not ok:
    raise SystemExit("scaffold_from_core_pack failed")

cli.ensure_executable_scripts(project)
cli.ensure_constitution_from_template(project)

if not cli._has_bundled_skills(project, "codex"):
    if not cli.install_ai_skills(project, "codex", overwrite_existing=True):
        raise SystemExit("install_ai_skills failed")

success, error = cli.init_git_repo(project, quiet=True)
if not success:
    raise SystemExit(error or "init_git_repo failed")

cli.save_init_options(
    project,
    {{
        "ai": "codex",
        "ai_skills": True,
        "ai_commands_dir": None,
        "branch_numbering": "sequential",
        "here": True,
        "preset": None,
        "offline": True,
        "script": "{script_type}",
        "speckit_version": cli.get_speckit_version(),
    }},
)

print(json.dumps({{"project_dir": str(project), "status": "ready_for_extension_install"}}, indent=2))
"""

    run(
        [
            "uv",
            "run",
            "--project",
            str(spec_kit_dir),
            "python",
            "-c",
            inline_script,
        ],
        cwd=test_project_dir,
    )


def write_canon_config(config_path: Path, config: dict) -> None:
    lines = [
        "# Project-level canon extension configuration.",
        "#",
        "# Edit project.name, canon.root, branching.types, or branching.scopes for the",
        "# target project, then rerun /speckit.constitution to regenerate constitution",
        "# metadata and the Section 6 branch strategy tables.",
        "project:",
        f'  name: {quote_yaml(config["project"]["name"])}',
        "",
        "canon:",
        f'  root: {quote_yaml(config["canon"]["root"])}',
        "",
        "branching:",
        "  types:",
    ]

    for item in config["branching"]["types"]:
        lines.append(f'    - code: {quote_yaml(item["code"])}')
        lines.append(f'      classification: {quote_yaml(item["classification"])}')

    lines.extend(["  scopes:"])
    for item in config["branching"]["scopes"]:
        lines.append(f'    - code: {quote_yaml(item["code"])}')
        lines.append(f'      description: {quote_yaml(item["description"])}')

    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    workspace_root = find_workspace_root(args.workspace_root)
    spec_kit_dir = workspace_root / "spec-kit"
    extension_dir = workspace_root / "spec-kit-canon"
    test_project_dir = workspace_root / "spec-kit-canon-test"
    config_fixture = args.config_fixture.resolve() if args.config_fixture else default_config_fixture_path()
    config = load_config_fixture(config_fixture)

    if args.project_name:
        config["project"]["name"] = args.project_name

    if args.clear_test_project:
        clear_directory(test_project_dir, workspace_root)
    else:
        test_project_dir.mkdir(parents=True, exist_ok=True)

    initialize_test_project(spec_kit_dir, test_project_dir)
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
    write_canon_config(canon_config, config)

    summary = {
        "workspace_root": str(workspace_root),
        "spec_kit_dir": str(spec_kit_dir),
        "extension_dir": str(extension_dir),
        "test_project_dir": str(test_project_dir),
        "config_fixture": str(config_fixture),
        "canon_config": str(canon_config),
        "applied_config": config,
        "constitution_path": str(test_project_dir / ".specify" / "memory" / "constitution.md"),
        "cleared_test_project": args.clear_test_project,
        "status": "ready_for_constitution",
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
