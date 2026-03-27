---
name: updating-spec-kit-canon-core-presets
description: Sync `presets/canon-core` with the latest released upstream `spec-kit` core command sources. Use when rebasing `presets/canon-core/commands/*.md` or `presets/canon-core/templates/constitution-template.md` onto the newest upstream release tag, verifying the real latest release against `../spec-kit` `origin`, fetching a missing release tag locally, exporting upstream source snapshots, preserving canon-only preconditions for the regular core commands, and handling the larger `speckit.constitution` merge.
---

# Updating Spec-Kit Canon Core Presets

Use this skill to refresh `presets/canon-core` from the latest released
upstream `spec-kit` sources without losing the canon-specific overlay.

Read [references/sync-rules.md](./references/sync-rules.md) before editing
`presets/canon-core`.

The last merged upstream release is tracked in
[spec-kit-release.json](../../presets/canon-core/spec-kit-release.json).
Update that file only after the preset rebase is finished and validated.

## Workflow

### 1. Export the upstream release snapshot

Run [scripts/export_upstream_release.py](./scripts/export_upstream_release.py)
first.

Default behavior:

- Resolve the true latest release tag from `../spec-kit` `origin`, not from the
  local tag list alone.
- Fetch the release tag locally if the clone does not have it yet.
- Export the upstream release sources and the current local `canon-core` files
  into `.tmp/updating-spec-kit-canon-core-presets/<tag>/`.
- Write `manifest.json` with the resolved tag, commit, and file map.

Recommended command:

```bash
python skills/updating-spec-kit-canon-core-presets/scripts/export_upstream_release.py
```

Read the generated `manifest.json` before editing so the source and target file
paths are explicit.

### 2. Rebase the regular core commands

Treat these files as the regular command set:

- `presets/canon-core/commands/speckit.specify.md`
- `presets/canon-core/commands/speckit.clarify.md`
- `presets/canon-core/commands/speckit.checklist.md`
- `presets/canon-core/commands/speckit.plan.md`
- `presets/canon-core/commands/speckit.tasks.md`
- `presets/canon-core/commands/speckit.analyze.md`
- `presets/canon-core/commands/speckit.implement.md`

For each regular command:

- Start from the exported upstream release file named in
  [references/sync-rules.md](./references/sync-rules.md).
- Keep the canon `## Pre-conditions (execute before any other step)` block at
  the top of the body.
- Keep only preset-specific path and placeholder normalization needed for
  installed preset commands:
  - `.specify/templates/...` instead of raw upstream `templates/...`
  - `.specify/scripts/...` command paths instead of raw upstream repo-relative
    script paths
  - `$ARGUMENTS` placeholder style in markdown command content
- Remove any other drift unless the new upstream release makes the local delta
  necessary.

If the release changed script semantics or template paths, port that semantic
change into the local preset form instead of reverting to the raw upstream path
layout.

### 3. Handle the constitution files as a manual merge

Treat these files as the special-case manual merge:

- `presets/canon-core/commands/speckit.constitution.md`
- `presets/canon-core/templates/constitution-template.md`

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

- `presets/canon-core/templates/canon-toc-template.md`
- `presets/canon-core/templates/root-gitattributes-template.txt`

### 4. Validate before finalizing

After editing:

- Review `git diff -- presets/canon-core`.
- Confirm every regular command still contains exactly one leading
  `## Pre-conditions` block.
- Confirm non-precondition diffs in the regular commands are limited to the
  preset normalization described in
  [references/sync-rules.md](./references/sync-rules.md).
- Run the skill validator:

```bash
python C:/Users/maxs/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/updating-spec-kit-canon-core-presets
```

- If the preset behavior changed materially, run the shared extension test skill
  afterward instead of trusting prompt diffs alone.

### 5. Record the merged version and clean up the sync workspace

After validation passes, finalize the sync:

- Update
  [spec-kit-release.json](../../presets/canon-core/spec-kit-release.json)
  from the manifest of the workspace you just merged.
- Remove `.tmp/updating-spec-kit-canon-core-presets/<tag>/`.
- If that leaves `.tmp/updating-spec-kit-canon-core-presets/` empty, remove it.
- If that also leaves `.tmp/` empty, remove `.tmp/`.

Recommended command:

```bash
python skills/updating-spec-kit-canon-core-presets/scripts/finalize_preset_sync.py
```

If you need to inspect the exported workspace longer, use `--keep-temp` and
delete it only after you are done.

## Resources

- [scripts/export_upstream_release.py](./scripts/export_upstream_release.py):
  resolve the latest release tag, fetch it when needed, and export the upstream
  plus local sync workspace.
- [scripts/finalize_preset_sync.py](./scripts/finalize_preset_sync.py):
  record the merged upstream release in JSON and remove the temporary sync
  workspace.
- [spec-kit-release.json](../../presets/canon-core/spec-kit-release.json):
  checked-in metadata for the last upstream `spec-kit` release merged into
  `presets/canon-core`.
- [references/sync-rules.md](./references/sync-rules.md): file map, allowed
  deltas, and validation rules.
