#!/usr/bin/env python3
"""Record the last merged upstream spec-kit release and clean the sync workspace."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SYNC_WORKSPACE_DIRNAME = "updating-spec-kit-canon-core-presets"
DEFAULT_METADATA_RELATIVE = (
    "presets/canon-core/spec-kit-release.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Finalize a canon-core preset sync by recording the merged upstream "
            "release and deleting the temporary sync workspace."
        )
    )
    parser.add_argument(
        "--canon-dir",
        default=".",
        help="Path to the spec-kit-canon repository root (default: current directory).",
    )
    parser.add_argument(
        "--manifest",
        default=None,
        help=(
            "Explicit manifest.json path to finalize. Defaults to the newest "
            "manifest under .tmp/updating-spec-kit-canon-core-presets/."
        ),
    )
    parser.add_argument(
        "--metadata-file",
        default=None,
        help=(
            "JSON file to update with the last merged upstream release. Defaults "
            "to presets/canon-core/spec-kit-release.json."
        ),
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Do not delete the resolved sync workspace after writing the metadata file.",
    )
    return parser.parse_args()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_generated_at(manifest_path: Path) -> datetime:
    manifest = load_json(manifest_path)
    generated_at = manifest.get("generated_at_utc")
    if not isinstance(generated_at, str):
        raise SystemExit(f"Manifest is missing generated_at_utc: {manifest_path}")
    try:
        return datetime.fromisoformat(generated_at)
    except ValueError as exc:
        raise SystemExit(f"Invalid generated_at_utc in {manifest_path}: {generated_at}") from exc


def resolve_manifest(sync_root: Path, explicit_manifest: str | None) -> Path:
    if explicit_manifest:
        manifest_path = Path(explicit_manifest).resolve()
        if not manifest_path.is_file():
            raise SystemExit(f"Manifest not found: {manifest_path}")
        return manifest_path

    candidates = sorted(sync_root.glob("*/manifest.json"))
    if not candidates:
        raise SystemExit(
            "No sync manifests were found under "
            f"{sync_root}. Run export_upstream_release.py first."
        )

    return max(candidates, key=parse_generated_at)


def ensure_within(path: Path, root: Path, *, label: str) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise SystemExit(f"{label} must stay within {root}, got {path}") from exc


def build_metadata(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "updated_at_utc": now_iso(),
        "preset_target": "presets/canon-core",
        "spec_kit_release": {
            "requested_tag": manifest["requested_tag"],
            "resolved_tag": manifest["resolved_tag"],
            "release_commit": manifest["release_commit"],
            "export_generated_at_utc": manifest["generated_at_utc"],
        },
        "sync_scope": {
            "regular_commands": manifest["regular_commands"],
            "special_commands": manifest["special_commands"],
            "canon_owned_files": manifest["canon_owned_files"],
        },
    }


def remove_sync_workspace(output_dir: Path, *, sync_root: Path) -> list[Path]:
    ensure_within(output_dir, sync_root, label="Sync workspace")
    removed: list[Path] = []

    if output_dir.exists():
        shutil.rmtree(output_dir)
        removed.append(output_dir)

    if sync_root.exists() and not any(sync_root.iterdir()):
        sync_root.rmdir()
        removed.append(sync_root)

    tmp_root = sync_root.parent
    if tmp_root.exists() and not any(tmp_root.iterdir()):
        tmp_root.rmdir()
        removed.append(tmp_root)

    return removed


def main() -> int:
    args = parse_args()

    canon_dir = Path(args.canon_dir).resolve()
    sync_root = canon_dir / ".tmp" / SYNC_WORKSPACE_DIRNAME
    metadata_file = (
        Path(args.metadata_file).resolve()
        if args.metadata_file
        else canon_dir / DEFAULT_METADATA_RELATIVE
    )
    manifest_path = resolve_manifest(sync_root, args.manifest)
    manifest = load_json(manifest_path)

    manifest_canon_dir = Path(manifest.get("canon_dir", "")).resolve()
    if manifest_canon_dir != canon_dir:
        raise SystemExit(
            "Manifest canon_dir does not match the requested repo root: "
            f"{manifest_canon_dir} != {canon_dir}"
        )

    output_dir = Path(manifest["output_dir"]).resolve()
    ensure_within(output_dir, canon_dir, label="Manifest output_dir")

    metadata = build_metadata(manifest)
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    metadata_file.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote merge metadata: {metadata_file}")
    print(
        "Recorded upstream release: "
        f"{metadata['spec_kit_release']['resolved_tag']} "
        f"({metadata['spec_kit_release']['release_commit']})"
    )

    if args.keep_temp:
        print(f"Kept sync workspace: {output_dir}")
        return 0

    removed = remove_sync_workspace(output_dir, sync_root=sync_root)
    if removed:
        for path in removed:
            print(f"Removed: {path}")
    else:
        print(f"Sync workspace was already absent: {output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
