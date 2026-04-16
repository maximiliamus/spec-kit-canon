---
name: syncing-spec-kit-canon-core-preset
description: Sync `preset/` with the latest released upstream `spec-kit` core command sources. Use when rebasing `preset/commands/*.md` or `preset/templates/constitution-template.md` onto the newest upstream release tag, verifying the real latest release against `../spec-kit` `origin`, fetching a missing release tag locally, exporting upstream source snapshots, preserving or intentionally retiring canon-owned HTML comment overlay blocks in the regular upstream-tracking commands, handling the larger `speckit.constitution` merge, and keeping the visible upstream-baseline notes in the README files aligned with the recorded sync metadata.
---

# Syncing Spec Kit Canon Core Preset

Use this skill to refresh `preset/` from the latest released
upstream `spec-kit` sources without losing the canon-specific overlays or the
small preset-only normalizations.

Read [references/sync-rules.md](./references/sync-rules.md) before editing
`preset/`.
Also read the `Marked Local Overlays` section in
[`DEVELOPMENT.md`](../../docs/DEVELOPMENT.md) before touching the regular command
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
A preset sync is not complete until the finalize step has updated
`preset/spec-kit-release.json` from the exported manifest for the merged
upstream release.
The same resolved upstream release must also be reflected in the visible
upstream-baseline notes in [README.md](../../README.md) and
[preset/README.md](../../preset/README.md).

## Workflow

### 1. Export the upstream release snapshot

Run [scripts/export_upstream_release.py](./scripts/export_upstream_release.py)
first.

Default behavior:

- Resolve the true latest release tag from `../spec-kit` `origin`, not from the
  local tag list alone when `origin` advertises semver tags.
- If `origin` advertises no semantic-version tags at all, fetch tags from
  `origin`, fall back to the highest local semantic-version tag, and report
  that fallback explicitly.
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
- Confirm the visible upstream-baseline notes in
  [README.md](../../README.md) and [preset/README.md](../../preset/README.md)
  either already match the resolved upstream release tag or are updated in the
  same sync.
- Run the skill validator:

```bash
python C:/Users/maxs/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/syncing-spec-kit-canon-core-preset
```

- If the preset behavior changed materially, run the shared extension test skill
  afterward instead of trusting prompt diffs alone.

Complete this explicit end-of-run validation checklist before moving to the
finalize step:

- Regular command sync:
  - `preset/commands/speckit.specify.md`
  - `preset/commands/speckit.clarify.md`
  - `preset/commands/speckit.checklist.md`
  - `preset/commands/speckit.plan.md`
  - `preset/commands/speckit.tasks.md`
  - `preset/commands/speckit.analyze.md`
  - `preset/commands/speckit.implement.md`
  - Confirm each regular command was either intentionally updated from the
    exported upstream release or intentionally left unchanged because the
    resolved release already matched local content.
  - Confirm each retained `spec-kit-canon` marker block still has a matching
    start/end pair and sits in a coherent section after the merge.
  - Confirm non-marker changes in those files are limited to upstream deltas
    plus required preset normalization.

- Special-case manual merge review:
  - `preset/commands/speckit.constitution.md`
  - `preset/templates/constitution-template.md`
  - Confirm those files were reviewed against the exported upstream release and
    that canon-owned behavior was re-applied deliberately rather than carried
    forward blindly.

- Canon-owned preset files:
  - `preset/templates/canon-toc-template.md`
  - `preset/templates/root-gitattributes-template.txt`
  - `preset/preset.yml`
  - Confirm each file was checked for required updates caused by the new
    upstream baseline or intentionally left unchanged.
  - If the sync changes the minimum supported upstream baseline in practice,
    update `preset/preset.yml` `requires.speckit_version` accordingly.

- Merge metadata:
  - Confirm `preset/spec-kit-release.json` is ready to be updated from the
    exported manifest for the merged release.
  - Confirm the resolved upstream release tag and commit you plan to record
    match the export workspace manifest exactly.

- Visible README baseline notes:
  - Confirm the visible upstream-baseline notes in `README.md` and
    `preset/README.md` match the same resolved release tag that will be written
    to `preset/spec-kit-release.json`.
  - Confirm those README notes still point readers to
    `preset/spec-kit-release.json` as the source of truth for the exact tag and
    commit.

- Visible README command inventory:
  - Confirm the command lists in `README.md` and `preset/README.md` still match
    the actually overridden core commands in `preset/commands/`.
  - Confirm no README still advertises a command override that is missing from
    `preset/commands/`, and no shipped override is omitted from the README
    lists.

- Final workspace hygiene:
  - Confirm the export workspace manifest was read during the sync.
  - Confirm no temporary or inspection-only edits remain outside the intended
    preset sync scope.

### 5. Record the merged version and clean up the sync workspace

After validation passes, finalize the sync:

- Update
  [spec-kit-release.json](../../preset/spec-kit-release.json)
  from the manifest of the workspace you just merged.
- Update the visible upstream-baseline notes in
  [README.md](../../README.md) and [preset/README.md](../../preset/README.md)
  so they match the same resolved upstream release recorded in
  `preset/spec-kit-release.json`.
- Remove `.tmp/syncing-spec-kit-canon-core-preset/<tag>/`.
- If that leaves `.tmp/syncing-spec-kit-canon-core-preset/` empty, remove it.
- If that also leaves `.tmp/` empty, remove `.tmp/`.

Recommended command:

```bash
python skills/syncing-spec-kit-canon-core-preset/scripts/finalize_preset_sync.py
```

If you need to inspect the exported workspace longer, use `--keep-temp` and
delete it only after you are done.

### 6. Output the completion report

At the end of the workflow, output a short human-readable completion report.
This report is required and must confirm that the sync was actually finished,
not just edited partway through.

Report requirements:

- Use a flat checklist-style summary with green check marks: `✅`.
- Include one line for each validation area from the end-of-run checklist.
- Mark an item with `✅` only if it was actually verified during the run.
- If something was intentionally skipped or still pending, do not mark it green.
  Call it out explicitly instead.
- Keep the report concise, but specific enough that a reviewer can see which
  files and validation categories were covered.

Minimum required report sections:

- `✅ Regular command sync reviewed`
- `✅ Special-case constitution merge reviewed`
- `✅ Canon-owned preset files reviewed`
- `✅ Merge metadata updated`
- `✅ README upstream-baseline notes updated`
- `✅ README command inventory verified`
- `✅ Workspace cleanup completed`

Recommended format:

```md
Preset sync completion report

✅ Regular command sync reviewed
   Files: `preset/commands/speckit.specify.md`, `preset/commands/speckit.clarify.md`, `preset/commands/speckit.checklist.md`, `preset/commands/speckit.plan.md`, `preset/commands/speckit.tasks.md`, `preset/commands/speckit.analyze.md`, `preset/commands/speckit.implement.md`

✅ Special-case constitution merge reviewed
   Files: `preset/commands/speckit.constitution.md`, `preset/templates/constitution-template.md`

✅ Canon-owned preset files reviewed
   Files: `preset/templates/canon-toc-template.md`, `preset/templates/root-gitattributes-template.txt`, `preset/preset.yml`

✅ Merge metadata updated
   File: `preset/spec-kit-release.json`

✅ README upstream-baseline notes updated
   Files: `README.md`, `preset/README.md`

✅ README command inventory verified

✅ Workspace cleanup completed
   Removed: `.tmp/syncing-spec-kit-canon-core-preset/<tag>/`
```

If the workflow stopped early because the recorded upstream release already
matched the latest resolved release, output a shorter report that clearly says
no sync was required and do not emit the full green checklist.

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
