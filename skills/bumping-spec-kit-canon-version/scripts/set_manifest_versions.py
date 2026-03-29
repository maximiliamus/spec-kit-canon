#!/usr/bin/env python3
"""Bump or set the same normalized version in both Spec Kit Canon manifests."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SEMVER_RE = re.compile(
    r"^v?(?P<version>\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?)$"
)
VERSION_LINE_RE = re.compile(r'^(?P<indent>\s*)version: "(?P<version>[^"]+)"\s*$')
BUMP_KINDS = ("major", "minor", "patch")


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


def bump_version(version: str, kind: str) -> str:
    major, minor, patch = parse_semver_parts(version)

    if kind == "major":
        return f"{major + 1}.0.0"

    if kind == "minor":
        return f"{major}.{minor + 1}.0"

    if kind == "patch":
        return f"{major}.{minor}.{patch + 1}"

    raise ValueError(f"Unsupported bump kind '{kind}'.")


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bump or set the same normalized version in both package manifests."
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

    try:
        extension_current = read_manifest_version(extension_manifest, "extension")
        preset_current = read_manifest_version(preset_manifest, "preset")

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
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1

    action = "Would update" if args.dry_run else "Updated"
    already = "Would keep" if args.dry_run else "Already at"

    print(f"Resolved target: {resolution_label}")
    print(f"Normalized version: {normalized_version}")

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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
