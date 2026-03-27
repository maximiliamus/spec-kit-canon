#!/usr/bin/env python3
"""Verify that /speckit.constitution applied the shared config fixture."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_DIRS = ("spec-kit", "spec-kit-canon", "spec-kit-canon-test")
DEFAULT_CONFIG_FIXTURE = Path("assets") / "constitution-config-fixture.json"
DEFAULT_CANON_ROOT = "specs/000-canon"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that constitution generation applied the shared config fixture."
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        help="Workspace root that contains spec-kit, spec-kit-canon, and spec-kit-canon-test.",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        help="Project directory to verify. Defaults to <workspace-root>/spec-kit-canon-test.",
    )
    parser.add_argument(
        "--config-fixture",
        type=Path,
        help="JSON fixture that defines the expected constitution-driven canon config.",
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

    base_branch = branching.get("base")
    branch_types = branching.get("types")
    branch_scopes = branching.get("scopes")
    if branch_scopes is None:
        branch_scopes = branching.get("areas")
    if not isinstance(branch_types, list) or not isinstance(branch_scopes, list):
        raise SystemExit("Constitution config fixture branching.types and branching.scopes must be lists.")
    if base_branch is not None and (not isinstance(base_branch, str) or not base_branch.strip()):
        raise SystemExit(
            "Constitution config fixture branching.base must be a non-empty string when provided."
        )

    raw["branching"]["base"] = base_branch.strip() if isinstance(base_branch, str) else None
    raw["branching"]["scopes"] = branch_scopes
    raw["branching"].pop("areas", None)
    return raw


def strip_quotes(value: str) -> str:
    trimmed = value.strip()
    if len(trimmed) >= 2 and trimmed[0] == trimmed[-1] and trimmed[0] in {'"', "'"}:
        return trimmed[1:-1]
    return trimmed


def parse_canon_config(config_path: Path) -> dict:
    lines = config_path.read_text(encoding="utf-8").splitlines()
    result = {
        "project": {"name": ""},
        "canon": {"root": ""},
        "branching": {"base": None, "types": [], "scopes": []},
    }

    section: str | None = None
    list_name: str | None = None
    current_item: dict[str, str] | None = None

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if not raw_line.startswith(" ") and stripped.endswith(":"):
            section = stripped[:-1]
            list_name = None
            current_item = None
            continue

        if section == "project" and stripped.startswith("name:"):
            result["project"]["name"] = strip_quotes(stripped.split(":", 1)[1])
            continue

        if section == "canon" and stripped.startswith("root:"):
            result["canon"]["root"] = strip_quotes(stripped.split(":", 1)[1])
            continue

        if section != "branching":
            continue

        if stripped in {"types:", "scopes:", "areas:"}:
            list_name = stripped[:-1]
            if list_name == "areas":
                list_name = "scopes"
            current_item = None
            continue

        if stripped.startswith("base:"):
            result["branching"]["base"] = strip_quotes(stripped.split(":", 1)[1])
            continue

        if stripped.startswith("- code:"):
            if list_name is None:
                raise SystemExit(f"Unexpected list item outside branching.types/scopes in {config_path}")
            current_item = {"code": strip_quotes(stripped.split(":", 1)[1])}
            result["branching"][list_name].append(current_item)
            continue

        if current_item is None:
            continue

        if stripped.startswith("classification:"):
            current_item["classification"] = strip_quotes(stripped.split(":", 1)[1])
        elif stripped.startswith("description:"):
            current_item["description"] = strip_quotes(stripped.split(":", 1)[1])

    return result


def read_required(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"Missing required file: {path}")
    return path.read_text(encoding="utf-8")


def first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def parse_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    cells: list[str] = []
    for cell in stripped.strip("|").split("|"):
        normalized = cell.strip()
        if len(normalized) >= 2 and normalized[0] == normalized[-1] == "`":
            normalized = normalized[1:-1]
        cells.append(normalized)
    return cells


def extract_markdown_table(text: str, expected_headers: list[str]) -> list[list[str]]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if parse_markdown_row(line) != expected_headers:
            continue

        rows: list[list[str]] = []
        cursor = index + 1
        if cursor < len(lines) and lines[cursor].strip().startswith("|"):
            cursor += 1

        while cursor < len(lines):
            row = parse_markdown_row(lines[cursor])
            if not row:
                break
            rows.append(row)
            cursor += 1

        return rows

    raise ValueError(f"Could not find markdown table with headers {expected_headers!r}")


def extract_examples(text: str) -> list[str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != "Examples:":
            continue

        cursor = index + 1
        while cursor < len(lines) and lines[cursor].strip() != "```":
            cursor += 1
        if cursor >= len(lines):
            break

        cursor += 1
        examples: list[str] = []
        while cursor < len(lines) and lines[cursor].strip() != "```":
            if lines[cursor].strip():
                examples.append(lines[cursor].strip())
            cursor += 1
        return examples

    raise ValueError("Could not find the Examples code block in the constitution.")


def validate_example_codes(examples: list[str], allowed_types: set[str], allowed_scopes: set[str]) -> None:
    if not examples:
        raise ValueError("Examples block is empty.")

    for example in examples:
        branch_name = re.sub(r"^\d+-", "", example)
        parts = branch_name.split("-")
        if len(parts) < 3:
            raise ValueError(f"Example branch name is malformed: {example}")
        branch_type, branch_scope = parts[0], parts[1]
        if branch_type not in allowed_types:
            raise ValueError(
                f"Example branch name uses a type code not present in config: {example}"
            )
        if branch_scope not in allowed_scopes:
            raise ValueError(
                f"Example branch name uses a scope code not present in config: {example}"
            )


def main() -> int:
    args = parse_args()
    workspace_root = find_workspace_root(args.workspace_root)
    project_dir = args.project_dir.resolve() if args.project_dir else workspace_root / "spec-kit-canon-test"
    config_fixture = args.config_fixture.resolve() if args.config_fixture else default_config_fixture_path()
    expected = load_config_fixture(config_fixture)

    expected_project_name = expected["project"]["name"]
    expected_canon_root = expected["canon"]["root"]
    expected_type_rows = [
        [item["code"], item["classification"]] for item in expected["branching"]["types"]
    ]
    expected_scope_rows = [
        [item["code"], item["description"]] for item in expected["branching"]["scopes"]
    ]

    canon_config_path = project_dir / ".specify" / "extensions" / "canon" / "canon-config.yml"
    template_path = project_dir / ".specify" / "templates" / "constitution-template.md"
    constitution_path = project_dir / ".specify" / "memory" / "constitution.md"
    toc_path = project_dir / expected_canon_root / "_toc.md"

    actual_config = parse_canon_config(canon_config_path)
    template_text = read_required(template_path)
    constitution_text = read_required(constitution_path)
    toc_text = read_required(toc_path)

    failures: list[str] = []

    if actual_config != expected:
        failures.append(
            "Installed canon-config.yml does not match the shared config fixture."
        )

    expected_title = f"# {expected_project_name} Constitution"
    if first_non_empty_line(constitution_text) != expected_title:
        failures.append(
            f"Concrete constitution title does not match expected project name: {expected_title}"
        )

    expected_template_title = "# [PROJECT_NAME] Constitution"
    if first_non_empty_line(template_text) != expected_template_title:
        failures.append(
            "Project-local constitution template no longer preserves the approved PROJECT_NAME placeholder."
        )

    expected_toc_title = f"# {expected_project_name}"
    if first_non_empty_line(toc_text) != expected_toc_title:
        failures.append(
            f"Configured canon TOC title does not match expected project name: {expected_toc_title}"
        )

    for file_label, text in {
        "constitution": constitution_text,
        "template": template_text,
    }.items():
        if "CANON_ROOT" in text or "CANON_TOC" in text:
            failures.append(f"{file_label} still contains unresolved CANON_ROOT/CANON_TOC tokens.")
        if f"`{expected_canon_root}/_toc.md`" not in text:
            failures.append(f"{file_label} does not reference the configured canon TOC path.")
        if f"`{expected_canon_root}/**`" not in text:
            failures.append(f"{file_label} does not reference the configured canon root path.")
        if expected_canon_root != DEFAULT_CANON_ROOT and DEFAULT_CANON_ROOT in text:
            failures.append(
                f"{file_label} still contains the default canon root {DEFAULT_CANON_ROOT!r}."
            )

        try:
            actual_type_rows = extract_markdown_table(
                text, ["Type", "Map to Change Classification"]
            )
        except ValueError as exc:
            failures.append(f"{file_label} is missing the Section 6 type table: {exc}")
            actual_type_rows = []

        try:
            actual_scope_rows = extract_markdown_table(text, ["Scope", "Description"])
        except ValueError as exc:
            failures.append(f"{file_label} is missing the Section 6 scope table: {exc}")
            actual_scope_rows = []

        if actual_type_rows != expected_type_rows:
            failures.append(
                f"{file_label} Section 6 type table does not match the config fixture."
            )
        if actual_scope_rows != expected_scope_rows:
            failures.append(
                f"{file_label} Section 6 scope table does not match the config fixture."
            )

        try:
            examples = extract_examples(text)
            validate_example_codes(
                examples,
                {item["code"] for item in expected["branching"]["types"]},
                {item["code"] for item in expected["branching"]["scopes"]},
            )
        except ValueError as exc:
            failures.append(f"{file_label} Examples block failed validation: {exc}")

    summary = {
        "workspace_root": str(workspace_root),
        "project_dir": str(project_dir),
        "config_fixture": str(config_fixture),
        "canon_config": str(canon_config_path),
        "template_path": str(template_path),
        "constitution_path": str(constitution_path),
        "toc_path": str(toc_path),
        "expected_project_name": expected_project_name,
        "expected_canon_root": expected_canon_root,
        "expected_type_rows": expected_type_rows,
        "expected_scope_rows": expected_scope_rows,
        "status": "passed" if not failures else "failed",
        "failures": failures,
    }
    print(json.dumps(summary, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
