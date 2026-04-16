#!/usr/bin/env python3
"""Bump package versions and update the repo changelog."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


SEMVER_RE = re.compile(
    r"^v?(?P<version>\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?)$"
)
TAG_RE = re.compile(r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")
VERSION_LINE_RE = re.compile(r'^(?P<indent>\s*)version: "(?P<version>[^"]+)"\s*$')
BUMP_KINDS = ("major", "minor", "patch")
CONVENTIONAL_RE = re.compile(
    r"^(?P<type>[a-z]+)(?:\([^\)]*\))?(?P<breaking>!)?: (?P<description>.+)$"
)
CONVENTIONAL_SECTIONS = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "docs": "Documentation",
    "chore": "Chores",
    "refactor": "Refactors",
    "perf": "Performance",
    "test": "Testing",
    "ci": "CI/CD",
    "build": "Build",
}
SECTION_ORDER = [
    "Features",
    "Bug Fixes",
    "Documentation",
    "Performance",
    "Refactors",
    "Testing",
    "CI/CD",
    "Build",
    "Chores",
    "Miscellaneous",
]
CANON_RELEASE_URL_RE = re.compile(
    r"https://github\.com/maximiliamus/spec-kit-canon/releases/download/"
    r"(?:<tag>|vX\.Y\.Z|v\d+\.\d+\.\d+)/"
    r"spec-kit-canon-(?:<tag>|vX\.Y\.Z|v\d+\.\d+\.\d+)\.zip"
)
CANON_CORE_RELEASE_URL_RE = re.compile(
    r"https://github\.com/maximiliamus/spec-kit-canon/releases/download/"
    r"(?:<tag>|vX\.Y\.Z|v\d+\.\d+\.\d+)/"
    r"spec-kit-canon-core-(?:<tag>|vX\.Y\.Z|v\d+\.\d+\.\d+)\.zip"
)
SPEC_KIT_GIT_URL_RE = re.compile(
    r"git\+https://github\.com/github/spec-kit\.git@(?:vX\.Y\.Z|v\d+\.\d+\.\d+)"
)
README_SPEC_KIT_BADGE_RE = re.compile(
    r"!\[Spec Kit Version\]\(https://img\.shields\.io/badge/spec--kit-v\d+\.\d+\.\d+-blue\?logo=github\)"
)


@dataclass
class ChangelogPlan:
    path: Path
    previous_tag: str | None
    entries_by_section: dict[str, list[str]]
    commit_count: int
    original_text: str
    updated_text: str
    line_ending: str


def normalize_version(raw_value: str) -> str:
    match = SEMVER_RE.fullmatch(raw_value.strip())
    if match is None:
        raise ValueError(
            f"Invalid version '{raw_value}'. Use semver like 0.1.1 or v0.1.1."
        )
    return match.group("version")


def parse_semver_parts(version: str) -> tuple[int, int, int]:
    normalized = normalize_version(version)
    core = normalized.split("+", 1)[0].split("-", 1)[0]
    major_text, minor_text, patch_text = core.split(".")
    return int(major_text), int(minor_text), int(patch_text)


def parse_release_tag(tag: str) -> tuple[int, int, int] | None:
    match = TAG_RE.fullmatch(tag.strip())
    if match is None:
        return None
    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
    )


def bump_version(version: str, kind: str) -> str:
    major, minor, patch = parse_semver_parts(version)

    if kind == "major":
        return f"{major + 1}.0.0"

    if kind == "minor":
        return f"{major}.{minor + 1}.0"

    if kind == "patch":
        return f"{major}.{minor}.{patch + 1}"

    raise ValueError(f"Unsupported bump kind '{kind}'.")


def run_git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise OSError(completed.stderr.strip() or f"git {' '.join(args)} failed.")
    return completed.stdout


def format_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def read_manifest_version(path: Path, section_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    section_header = f"{section_name}:"
    in_section = False

    for line in lines:
        if line.strip() == section_header:
            in_section = True
            continue

        if in_section and line and not line.startswith((" ", "\t")):
            in_section = False

        if not in_section:
            continue

        version_match = VERSION_LINE_RE.match(line)
        if version_match is not None:
            return version_match.group("version")

    raise ValueError(f"Could not find version under '{section_name}' in {path}.")


def replace_manifest_version(
    path: Path,
    section_name: str,
    new_version: str,
    dry_run: bool,
) -> tuple[str, bool]:
    text = path.read_text(encoding="utf-8")
    line_ending = "\r\n" if "\r\n" in text else "\n"
    had_trailing_newline = text.endswith(("\r", "\n"))
    lines = text.splitlines()

    current_version: str | None = None
    changed = False
    in_section = False

    for index, line in enumerate(lines):
        if line.strip() == f"{section_name}:":
            in_section = True
            continue

        if in_section and line and not line.startswith((" ", "\t")):
            in_section = False

        if not in_section:
            continue

        version_match = VERSION_LINE_RE.match(line)
        if version_match is None:
            continue

        current_version = version_match.group("version")
        if current_version != new_version:
            lines[index] = f'{version_match.group("indent")}version: "{new_version}"'
            changed = True
        break

    if current_version is None:
        raise ValueError(f"Could not find version under '{section_name}' in {path}.")

    if changed and not dry_run:
        updated_text = line_ending.join(lines)
        if had_trailing_newline:
            updated_text += line_ending
        path.write_text(updated_text, encoding="utf-8")

    return current_version, changed


def replace_release_doc_versions(
    path: Path,
    new_version: str,
    spec_kit_tag: str,
    dry_run: bool,
) -> bool:
    text = path.read_text(encoding="utf-8")
    line_ending = "\r\n" if "\r\n" in text else "\n"
    had_trailing_newline = text.endswith(("\r", "\n"))
    target_tag = f"v{new_version}"

    updated_text = CANON_RELEASE_URL_RE.sub(
        "https://github.com/maximiliamus/spec-kit-canon/releases/download/"
        f"{target_tag}/spec-kit-canon-{target_tag}.zip",
        text,
    )
    updated_text = CANON_CORE_RELEASE_URL_RE.sub(
        "https://github.com/maximiliamus/spec-kit-canon/releases/download/"
        f"{target_tag}/spec-kit-canon-core-{target_tag}.zip",
        updated_text,
    )
    updated_text = SPEC_KIT_GIT_URL_RE.sub(
        f"git+https://github.com/github/spec-kit.git@{spec_kit_tag}",
        updated_text,
    )

    changed = updated_text != text
    if changed and not dry_run:
        if line_ending != "\n":
            updated_text = updated_text.replace("\n", line_ending)
        elif had_trailing_newline and not updated_text.endswith("\n"):
            updated_text += "\n"
        path.write_text(updated_text, encoding="utf-8")

    return changed


def replace_readme_spec_kit_badge(
    path: Path,
    spec_kit_tag: str,
    dry_run: bool,
) -> bool:
    text = path.read_text(encoding="utf-8")
    line_ending = "\r\n" if "\r\n" in text else "\n"
    had_trailing_newline = text.endswith(("\r", "\n"))

    updated_text = README_SPEC_KIT_BADGE_RE.sub(
        f"![Spec Kit Version](https://img.shields.io/badge/spec--kit-{spec_kit_tag}-blue?logo=github)",
        text,
    )

    changed = updated_text != text
    if changed and not dry_run:
        if line_ending != "\n":
            updated_text = updated_text.replace("\n", line_ending)
        elif had_trailing_newline and not updated_text.endswith("\n"):
            updated_text += "\n"
        path.write_text(updated_text, encoding="utf-8")

    return changed


def read_spec_kit_release_tag(path: Path) -> str:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Missing Spec Kit release metadata file: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in Spec Kit release metadata file: {path}") from error

    resolved_tag = (
        payload.get("spec_kit_release", {}).get("resolved_tag")
        if isinstance(payload, dict)
        else None
    )
    if not isinstance(resolved_tag, str) or not resolved_tag.strip():
        raise ValueError(
            "Missing spec_kit_release.resolved_tag in "
            f"Spec Kit release metadata file: {path}"
        )

    normalized_tag = resolved_tag.strip()
    if parse_release_tag(normalized_tag) is None:
        raise ValueError(
            "Invalid spec_kit_release.resolved_tag in "
            f"Spec Kit release metadata file: {path}: {normalized_tag}"
        )

    return normalized_tag


def resolve_previous_release_tag(repo_root: Path, target_version: str) -> str | None:
    target_parts = parse_semver_parts(target_version)
    output = run_git(repo_root, "tag", "--merged", "HEAD", "--list", "v*")
    candidates: list[tuple[tuple[int, int, int], str]] = []

    for line in output.splitlines():
        tag = line.strip()
        if not tag:
            continue
        tag_parts = parse_release_tag(tag)
        if tag_parts is None:
            continue
        if tag_parts < target_parts:
            candidates.append((tag_parts, tag))

    if not candidates:
        return None

    candidates.sort()
    return candidates[-1][1]


def collect_conventional_commits(
    repo_root: Path,
    previous_tag: str | None,
) -> tuple[dict[str, list[str]], int]:
    revision = f"{previous_tag}..HEAD" if previous_tag is not None else "HEAD"
    output = run_git(repo_root, "log", "--no-merges", "--pretty=%s", revision)
    sections: dict[str, list[str]] = {}
    subjects = [line.strip() for line in output.splitlines() if line.strip()]

    for subject in subjects:
        match = CONVENTIONAL_RE.match(subject)
        if match:
            commit_type = match.group("type")
            section_title = CONVENTIONAL_SECTIONS.get(commit_type, "Miscellaneous")
            entry = match.group("description")
            if match.group("breaking"):
                entry = entry + " ⚠️ Breaking change"
        else:
            section_title = "Miscellaneous"
            entry = subject

        sections.setdefault(section_title, []).append(entry)

    return sections, len(subjects)


def load_changelog_text(path: Path) -> tuple[str, str]:
    if not path.exists():
        return "# Changelog\n", "\n"

    text = path.read_text(encoding="utf-8")
    if text and not text.lstrip().startswith("# Changelog"):
        raise ValueError(
            f"{path} exists but does not start with '# Changelog'. "
            "Refusing to rewrite it automatically."
        )

    line_ending = "\r\n" if "\r\n" in text else "\n"
    return text or "# Changelog\n", line_ending


def strip_existing_version_section(text: str, target_version: str) -> str:
    lines = text.splitlines()
    if not lines:
        return "# Changelog"

    header_lines: list[str] = []
    sections: list[list[str]] = []
    current_section: list[str] | None = None

    for line in lines:
        if line.startswith("## "):
            if current_section is not None:
                sections.append(current_section)
            current_section = [line]
            continue

        if current_section is None:
            header_lines.append(line)
        else:
            current_section.append(line)

    if current_section is not None:
        sections.append(current_section)

    if not header_lines:
        header_lines = ["# Changelog"]

    filtered_sections = [
        section
        for section in sections
        if not (
            section[0].startswith(f"## v{target_version}")
            or section[0].startswith(f"## [{target_version}]")
        )
    ]

    chunks = ["\n".join(header_lines).strip()]
    chunks.extend("\n".join(section).rstrip() for section in filtered_sections if section)
    return "\n\n".join(chunk for chunk in chunks if chunk).rstrip()


def build_changelog_entry(
    target_version: str,
    previous_tag: str | None,
    entries_by_section: dict[str, list[str]],
    commit_count: int,
) -> str:
    lines = [f"## [{target_version}] - {date.today().isoformat()}", ""]
    added_section = False

    for section in SECTION_ORDER:
        entries = entries_by_section.get(section)
        if not entries:
            continue

        if added_section:
            lines.append("")
        lines.append(f"### {section}")
        lines.extend(f"- {entry}" for entry in entries)
        added_section = True

    if not added_section:
        if previous_tag is not None:
            lines.append(f"- No recorded changes since {previous_tag}.")
        else:
            lines.append("- No recorded changes available from git history.")

    return "\n".join(lines).rstrip()


def plan_changelog_update(
    repo_root: Path,
    changelog_path: Path,
    target_version: str,
) -> ChangelogPlan:
    previous_tag = resolve_previous_release_tag(repo_root, target_version)
    entries_by_section, commit_count = collect_conventional_commits(
        repo_root,
        previous_tag,
    )
    original_text, line_ending = load_changelog_text(changelog_path)
    stripped_text = strip_existing_version_section(original_text, target_version)
    entry_text = build_changelog_entry(
        target_version,
        previous_tag,
        entries_by_section,
        commit_count,
    )
    # Insert new entry after the header preamble, before any existing sections,
    # so the changelog is always in reverse chronological order (newest first).
    first_section_idx = stripped_text.find("\n\n## ")
    if first_section_idx == -1:
        updated_text = f"{stripped_text}\n\n{entry_text}\n"
    else:
        preamble = stripped_text[:first_section_idx]
        rest = stripped_text[first_section_idx:]
        updated_text = f"{preamble}\n\n{entry_text}{rest}\n"

    return ChangelogPlan(
        path=changelog_path,
        previous_tag=previous_tag,
        entries_by_section=entries_by_section,
        commit_count=commit_count,
        original_text=original_text,
        updated_text=updated_text,
        line_ending=line_ending,
    )


def write_changelog(plan: ChangelogPlan, dry_run: bool) -> bool:
    changed = plan.updated_text != plan.original_text
    if changed and not dry_run:
        normalized_text = plan.updated_text.replace("\n", plan.line_ending)
        plan.path.write_text(normalized_text, encoding="utf-8")
    return changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bump package versions and update the repo changelog."
    )
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument(
        "--version",
        help="Set an explicit semver version, with or without a leading 'v'.",
    )
    target_group.add_argument(
        "--kind",
        dest="kind",
        choices=BUMP_KINDS,
        help="Relative bump kind. Defaults to minor when omitted.",
    )
    parser.add_argument(
        "--extension-manifest",
        type=Path,
        help="Override the extension manifest path.",
    )
    parser.add_argument(
        "--preset-manifest",
        type=Path,
        help="Override the preset manifest path.",
    )
    parser.add_argument(
        "--changelog-path",
        type=Path,
        help="Override the changelog path. Defaults to <repo>/CHANGELOG.md.",
    )
    parser.add_argument(
        "--install-doc",
        type=Path,
        help="Override the install doc path. Defaults to <repo>/docs/INSTALL.md.",
    )
    parser.add_argument(
        "--upgrade-doc",
        type=Path,
        help="Override the upgrade doc path. Defaults to <repo>/docs/UPGRADE.md.",
    )
    parser.add_argument(
        "--readme",
        type=Path,
        help="Override the README path. Defaults to <repo>/README.md.",
    )
    parser.add_argument(
        "--spec-kit-release-metadata",
        type=Path,
        help="Override the Spec Kit release metadata path. Defaults to <repo>/preset/spec-kit-release.json.",
    )
    parser.add_argument(
        "--skip-changelog",
        action="store_true",
        help="Skip automatic CHANGELOG.md generation.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the changes without writing the files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[3]
    extension_manifest = (
        args.extension_manifest.resolve()
        if args.extension_manifest is not None
        else repo_root / "extension" / "extension.yml"
    )
    preset_manifest = (
        args.preset_manifest.resolve()
        if args.preset_manifest is not None
        else repo_root / "preset" / "preset.yml"
    )
    changelog_path = (
        args.changelog_path.resolve()
        if args.changelog_path is not None
        else repo_root / "CHANGELOG.md"
    )
    install_doc = (
        args.install_doc.resolve()
        if args.install_doc is not None
        else repo_root / "docs" / "INSTALL.md"
    )
    upgrade_doc = (
        args.upgrade_doc.resolve()
        if args.upgrade_doc is not None
        else repo_root / "docs" / "UPGRADE.md"
    )
    readme = (
        args.readme.resolve()
        if args.readme is not None
        else repo_root / "README.md"
    )
    spec_kit_release_metadata = (
        args.spec_kit_release_metadata.resolve()
        if args.spec_kit_release_metadata is not None
        else repo_root / "preset" / "spec-kit-release.json"
    )

    try:
        extension_current = read_manifest_version(extension_manifest, "extension")
        preset_current = read_manifest_version(preset_manifest, "preset")
        spec_kit_tag = read_spec_kit_release_tag(spec_kit_release_metadata)

        if args.version is not None:
            normalized_version = normalize_version(args.version)
            resolution_label = f"exact version {normalized_version}"
        else:
            bump_kind = args.kind or "minor"
            if extension_current != preset_current:
                raise ValueError(
                    "Current manifest versions do not match: "
                    f"{extension_current} vs {preset_current}. "
                    "Resolve that mismatch before using a relative bump."
                )
            normalized_version = bump_version(extension_current, bump_kind)
            resolution_label = f"{bump_kind} bump from {extension_current}"

        changelog_plan = None
        if not args.skip_changelog:
            changelog_plan = plan_changelog_update(
                repo_root,
                changelog_path,
                normalized_version,
            )

        extension_previous, extension_changed = replace_manifest_version(
            extension_manifest,
            "extension",
            normalized_version,
            args.dry_run,
        )
        preset_previous, preset_changed = replace_manifest_version(
            preset_manifest,
            "preset",
            normalized_version,
            args.dry_run,
        )
        install_doc_changed = replace_release_doc_versions(
            install_doc,
            normalized_version,
            spec_kit_tag,
            args.dry_run,
        )
        upgrade_doc_changed = replace_release_doc_versions(
            upgrade_doc,
            normalized_version,
            spec_kit_tag,
            args.dry_run,
        )
        readme_badge_changed = replace_readme_spec_kit_badge(
            readme,
            spec_kit_tag,
            args.dry_run,
        )

        changelog_changed = False
        if changelog_plan is not None:
            changelog_changed = write_changelog(changelog_plan, args.dry_run)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1

    action = "Would update" if args.dry_run else "Updated"
    already = "Would keep" if args.dry_run else "Already at"

    print(f"Resolved target: {resolution_label}")
    print(f"Normalized version: {normalized_version}")
    print(f"Resolved Spec Kit base tag: {spec_kit_tag}")

    extension_label = format_path(extension_manifest, repo_root)
    if extension_changed:
        print(
            f"{action} {extension_label}: "
            f"{extension_previous} -> {normalized_version}"
        )
    else:
        print(f"{already} {extension_label}: {normalized_version}")

    preset_label = format_path(preset_manifest, repo_root)
    if preset_changed:
        print(
            f"{action} {preset_label}: "
            f"{preset_previous} -> {normalized_version}"
        )
    else:
        print(f"{already} {preset_label}: {normalized_version}")

    install_doc_label = format_path(install_doc, repo_root)
    if install_doc_changed:
        print(f"{action} {install_doc_label}: release commands -> v{normalized_version}")
    else:
        print(f"{already} {install_doc_label}: release commands at v{normalized_version}")

    upgrade_doc_label = format_path(upgrade_doc, repo_root)
    if upgrade_doc_changed:
        print(f"{action} {upgrade_doc_label}: release commands -> v{normalized_version}")
    else:
        print(f"{already} {upgrade_doc_label}: release commands at v{normalized_version}")

    readme_label = format_path(readme, repo_root)
    if readme_badge_changed:
        print(f"{action} {readme_label}: Spec Kit badge -> {spec_kit_tag}")
    else:
        print(f"{already} {readme_label}: Spec Kit badge at {spec_kit_tag}")

    if args.skip_changelog:
        print("Skipped CHANGELOG.md generation.")
    else:
        changelog_label = format_path(changelog_path, repo_root)
        commit_count = changelog_plan.commit_count
        if changelog_changed:
            print(
                f"{action} {changelog_label}: "
                f"entry for v{normalized_version} from "
                f"{changelog_plan.previous_tag or 'full history'} "
                f"with {commit_count} commit(s)"
            )
        else:
            print(f"{already} {changelog_label}: entry for v{normalized_version}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
