---
name: syncing-spec-kit-canon-core-preset
description: Sync `preset/` with the latest released upstream `spec-kit` core command sources. Use when rebasing `preset/commands/*.md` or `preset/templates/constitution-template.md` onto the newest upstream release tag, verifying the real latest release against `../spec-kit` `origin`, fetching a missing release tag locally, exporting upstream source snapshots, preserving or intentionally retiring canon-owned HTML comment overlay blocks in the regular upstream-tracking commands, and handling the larger `speckit.constitution` merge.
---

# Syncing Spec Kit Canon Core Preset

Use this skill to refresh `preset/` from the latest released
upstream `spec-kit` sources without losing the canon-specific overlays or the
small preset-only normalizations.

Read [references/sync-rules.md](./references/sync-rules.md) before editing
`preset/`.
Also read the `Marked Local Overlays` section in
[`DEVELOPMENT.md`](../../DEVELOPMENT.md) before touching the regular command
files, because that section defines when the
`<!-- spec-kit-canon:start ... -->` / `<!-- spec-kit-canon:end ... -->`
markup should exist and what it is allowed to wrap.

For the seven regular upstream-tracking commands, treat the named HTML comment
blocks in the current local file as the primary canon-owned delta. Those
markers exist specifically to make upstream rebases easier: rebuild the file
from the exported upstream release, restore the still-needed marked overlay
blocks, and then reapply only the routine preset normalization that stays
unmarked.

The last merged upstream release is tracked in
[spec-kit-release.json](../../preset/spec-kit-release.json).
If the newly resolved upstream release tag matches that recorded tag, stop the
workflow immediately and do not create a new sync workspace.
Update that file only after the preset rebase is finished and validated.

## Workflow

### 1. Export the upstream release snapshot

Run [scripts/export_upstream_release.py](./scripts/export_upstream_release.py)
first.

Default behavior:

- Resolve the true latest release tag from `../spec-kit` `origin`, not from the
  local tag list alone.
- Compare that resolved tag against
  `preset/spec-kit-release.json`.
- If the resolved tag is already recorded there, stop immediately with no
  export, rebase, or finalize step.
- Fetch the release tag locally if the clone does not have it yet.
- Export the upstream release sources and the current local `canon-core` files
  into `.tmp/syncing-spec-kit-canon-core-preset/<tag>/`.
- Write `manifest.json` with the resolved tag, commit, and file map.

Recommended command:

```bash
python skills/syncing-spec-kit-canon-core-preset/scripts/export_upstream_release.py
```

If the script reports that the recorded release already matches the latest
upstream release, stop here. There is nothing to merge.

Read the generated `manifest.json` before editing so the source and target file
paths are explicit.

### 2. Rebase the regular core commands

Treat these files as the regular upstream-tracking command set:

- `preset/commands/speckit.specify.md`
- `preset/commands/speckit.clarify.md`
- `preset/commands/speckit.checklist.md`
- `preset/commands/speckit.plan.md`
- `preset/commands/speckit.tasks.md`
- `preset/commands/speckit.analyze.md`
- `preset/commands/speckit.implement.md`

For each regular command:

- Start from the exported upstream release file named in
  [references/sync-rules.md](./references/sync-rules.md).
- Inventory the named local overlay blocks from the current canon file before
  you rewrite it. Use the current file as the source of truth for which
  `spec-kit-canon` blocks exist today.
- Rebuild the target file from the upstream release text first.
- Restore each named overlay block that still belongs in the file, keeping the
  marker names and block contents intact when the overlay is still needed.
- If the upstream release absorbed, superseded, or invalidated a marked local
  overlay, remove that overlay instead of blindly re-inserting it. Keep that
  choice explicit in the diff and review notes.
- If upstream section movement makes the old insertion point invalid, relocate
  the retained overlay to the nearest coherent section while keeping the block
  itself clearly bounded by the same markers.
- Keep only preset-specific path and placeholder normalization needed for
  installed preset commands:
  - `.specify/templates/...` instead of raw upstream `templates/...`
  - `.specify/scripts/...` command paths instead of raw upstream repo-relative
    script paths
  - `$ARGUMENTS` placeholder style in markdown command content
- Do not add markers around routine preset normalization, and do not preserve
  any other stale local drift outside the retained marker blocks.
- Remove any other drift unless the new upstream release makes the local delta
  necessary.

If the release changed script semantics or template paths, port that semantic
change into the local preset form instead of reverting to the raw upstream path
layout.

### 3. Handle the constitution files as a manual merge

Treat these files as the special-case manual merge:

- `preset/commands/speckit.constitution.md`
- `preset/templates/constitution-template.md`

Do not treat these like the regular precondition-only overlays.

Start from the exported upstream release sources, then reapply the canon-owned
behavior:

- canon config as the branch taxonomy source of truth
- canon root and TOC initialization
- project template synchronization
- repo-root `.gitattributes` bootstrap and repair
- canon-specific terminology and workflow rules

Keep these files canon-owned unless upstream changes clearly require
adaptation:

- `preset/templates/canon-toc-template.md`
- `preset/templates/root-gitattributes-template.txt`

### 4. Validate before finalizing

After editing:

- Review `git diff -- preset`.
- For each regular command, compare the final named overlay-block inventory
  against the pre-merge local file. Every retained block must still have a
  matching start/end marker pair.
- Confirm any removed marker block was intentionally retired because the new
  upstream release now covers it or because the canon-only behavior changed.
- Confirm non-marker diffs in the regular commands are limited to the preset
  normalization described in
  [references/sync-rules.md](./references/sync-rules.md).
- Confirm the regular commands still keep the expected canon-specific overlay
  behavior, especially the leading `preconditions` block where applicable.
- Run the skill validator:

```bash
python C:/Users/maxs/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/syncing-spec-kit-canon-core-preset
```

- If the preset behavior changed materially, run the shared extension test skill
  afterward instead of trusting prompt diffs alone.

### 5. Record the merged version and clean up the sync workspace

After validation passes, finalize the sync:

- Update
  [spec-kit-release.json](../../preset/spec-kit-release.json)
  from the manifest of the workspace you just merged.
- Remove `.tmp/syncing-spec-kit-canon-core-preset/<tag>/`.
- If that leaves `.tmp/syncing-spec-kit-canon-core-preset/` empty, remove it.
- If that also leaves `.tmp/` empty, remove `.tmp/`.

Recommended command:

```bash
python skills/syncing-spec-kit-canon-core-preset/scripts/finalize_preset_sync.py
```

If you need to inspect the exported workspace longer, use `--keep-temp` and
delete it only after you are done.

## Resources

- [scripts/export_upstream_release.py](./scripts/export_upstream_release.py):
  resolve the latest release tag, stop early when that tag is already recorded
  in `spec-kit-release.json`, otherwise fetch it when needed and export the
  upstream plus local sync workspace.
- [scripts/finalize_preset_sync.py](./scripts/finalize_preset_sync.py):
  record the merged upstream release in JSON and remove the temporary sync
  workspace.
- [spec-kit-release.json](../../preset/spec-kit-release.json):
  checked-in metadata for the last upstream `spec-kit` release merged into
  `preset/`.
- [references/sync-rules.md](./references/sync-rules.md): file map, allowed
  deltas, marker-aware rebase rules, and validation rules.
