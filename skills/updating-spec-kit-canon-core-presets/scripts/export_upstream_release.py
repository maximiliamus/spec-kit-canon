#!/usr/bin/env python
"""Export the latest released upstream spec-kit sources for canon-core sync work."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REGULAR_COMMANDS = [
    "specify",
    "clarify",
    "checklist",
    "plan",
    "tasks",
    "analyze",
    "implement",
]
SPECIAL_COMMANDS = ["constitution"]
ALL_COMMANDS = REGULAR_COMMANDS + SPECIAL_COMMANDS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve the latest released upstream spec-kit tag, fetch it when needed, "
            "and export the relevant canon-core sync files."
        )
    )
    parser.add_argument(
        "--spec-kit-dir",
        default="../spec-kit",
        help="Path to the sibling spec-kit repository (default: ../spec-kit).",
    )
    parser.add_argument(
        "--canon-dir",
        default=".",
        help="Path to the spec-kit-canon repository root (default: current directory).",
    )
    parser.add_argument(
        "--tag",
        default="latest",
        help="Release tag to export, or 'latest' to resolve from origin (default: latest).",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help=(
            "Output directory. Defaults to "
            ".tmp/updating-spec-kit-canon-core-presets/<resolved-tag> inside canon-dir."
        ),
    )
    return parser.parse_args()


def run_git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return completed.stdout


def parse_semver_tag(tag: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", tag)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def resolve_latest_remote_tag(spec_kit_dir: Path) -> str:
    output = run_git(spec_kit_dir, "ls-remote", "--tags", "--refs", "origin", "v*")
    tags: list[str] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        _, ref = line.split("\t", 1)
        tag = ref.rsplit("/", 1)[-1]
        if parse_semver_tag(tag) is not None:
            tags.append(tag)

    if not tags:
        raise RuntimeError("No semantic-version release tags were found on origin.")

    return max(tags, key=lambda value: parse_semver_tag(value) or (-1, -1, -1))


def ensure_local_tag(spec_kit_dir: Path, tag: str) -> None:
    try:
        run_git(spec_kit_dir, "rev-parse", "--verify", f"refs/tags/{tag}")
        return
    except subprocess.CalledProcessError:
        pass

    try:
        run_git(spec_kit_dir, "fetch", "origin", f"refs/tags/{tag}:refs/tags/{tag}")
    except subprocess.CalledProcessError:
        run_git(spec_kit_dir, "fetch", "--tags", "origin")

    run_git(spec_kit_dir, "rev-parse", "--verify", f"refs/tags/{tag}")


def git_show_to_file(spec_kit_dir: Path, tag: str, repo_path: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    content = run_git(spec_kit_dir, "show", f"{tag}:{repo_path}")
    destination.write_text(content, encoding="utf-8")


def copy_if_exists(source: Path, destination: Path) -> bool:
    if not source.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return True


def main() -> int:
    args = parse_args()

    canon_dir = Path(args.canon_dir).resolve()
    spec_kit_dir = Path(args.spec_kit_dir).resolve()

    if not spec_kit_dir.exists():
        raise SystemExit(f"spec-kit repository not found: {spec_kit_dir}")

    requested_tag = args.tag
    resolved_tag = requested_tag if requested_tag != "latest" else resolve_latest_remote_tag(spec_kit_dir)
    ensure_local_tag(spec_kit_dir, resolved_tag)

    output_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else canon_dir / ".tmp" / "updating-spec-kit-canon-core-presets" / resolved_tag
    )
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    upstream_root = output_dir / "upstream-release"
    current_root = output_dir / "canon-core-current"

    file_map: list[dict[str, str]] = []

    for command in ALL_COMMANDS:
        upstream_path = f"templates/commands/{command}.md"
        upstream_destination = upstream_root / "templates" / "commands" / f"{command}.md"
        git_show_to_file(spec_kit_dir, resolved_tag, upstream_path, upstream_destination)

        canon_path = canon_dir / "presets" / "canon-core" / "commands" / f"speckit.{command}.md"
        current_destination = current_root / "commands" / f"speckit.{command}.md"
        copy_if_exists(canon_path, current_destination)

        file_map.append(
            {
                "kind": "command",
                "upstream": upstream_path,
                "canon_target": str(canon_path.relative_to(canon_dir)).replace("\\", "/"),
            }
        )

    upstream_template_path = "templates/constitution-template.md"
    git_show_to_file(
        spec_kit_dir,
        resolved_tag,
        upstream_template_path,
        upstream_root / "templates" / "constitution-template.md",
    )
    file_map.append(
        {
            "kind": "template",
            "upstream": upstream_template_path,
            "canon_target": "presets/canon-core/templates/constitution-template.md",
        }
    )

    local_files = [
        "presets/canon-core/templates/constitution-template.md",
        "presets/canon-core/templates/canon-toc-template.md",
        "presets/canon-core/templates/root-gitattributes-template.txt",
        "presets/canon-core/preset.yml",
    ]
    for relative_path in local_files:
        source = canon_dir / relative_path
        destination = current_root / relative_path
        copy_if_exists(source, destination)

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "spec_kit_dir": str(spec_kit_dir),
        "canon_dir": str(canon_dir),
        "requested_tag": requested_tag,
        "resolved_tag": resolved_tag,
        "release_commit": run_git(spec_kit_dir, "rev-parse", resolved_tag).strip(),
        "output_dir": str(output_dir),
        "regular_commands": REGULAR_COMMANDS,
        "special_commands": SPECIAL_COMMANDS,
        "canon_owned_files": [
            "presets/canon-core/templates/canon-toc-template.md",
            "presets/canon-core/templates/root-gitattributes-template.txt",
            "presets/canon-core/preset.yml",
        ],
        "file_map": file_map,
    }

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Resolved release tag: {resolved_tag}")
    print(f"Exported sync workspace: {output_dir}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        if exc.stderr:
            sys.stderr.write(exc.stderr)
        raise
