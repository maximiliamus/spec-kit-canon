# Sync Rules

## Release Resolution

- Treat the latest release as the highest semantic-version tag visible on
  `../spec-kit` `origin`.
- Do not trust the local clone's tag list by itself while `origin` is
  advertising semantic-version tags normally.
- If `origin` advertises no semantic-version tags at all, run
  `git fetch --tags origin`, fall back to the highest local semantic-version
  tag, and record that fallback explicitly in the sync output.
- If that resolved tag already matches the recorded
  `preset/spec-kit-release.json` `spec_kit_release.resolved_tag`,
  stop the sync before export. No `.tmp` workspace or finalize step is needed.
- If the chosen tag is missing locally, fetch that tag before reading source
  files from it.

## Source Map

Regular upstream-tracking commands:

| Upstream release source | Canon target |
| --- | --- |
| `templates/commands/specify.md` | `preset/commands/speckit.specify.md` |
| `templates/commands/clarify.md` | `preset/commands/speckit.clarify.md` |
| `templates/commands/checklist.md` | `preset/commands/speckit.checklist.md` |
| `templates/commands/plan.md` | `preset/commands/speckit.plan.md` |
| `templates/commands/tasks.md` | `preset/commands/speckit.tasks.md` |
| `templates/commands/analyze.md` | `preset/commands/speckit.analyze.md` |
| `templates/commands/implement.md` | `preset/commands/speckit.implement.md` |

Special-case merges:

| Upstream release source | Canon target |
| --- | --- |
| `templates/commands/constitution.md` | `preset/commands/speckit.constitution.md` |
| `templates/constitution-template.md` | `preset/templates/constitution-template.md` |

Canon-owned files:

- `preset/templates/canon-toc-template.md`
- `preset/templates/root-gitattributes-template.txt`
- `preset/preset.yml`

Documentation files that must stay aligned with the recorded upstream baseline:

- `README.md`
- `preset/README.md`

## Allowed Deltas

Regular commands:

- Preserve or intentionally retire the named
  `<!-- spec-kit-canon:start <name> --> ... <!-- spec-kit-canon:end <name> -->`
  overlay blocks from the current local file.
- Keep preset-ready path normalization:
  - `.specify/templates/...`
  - `.specify/scripts/...`
- Keep markdown argument placeholder normalization as `$ARGUMENTS`.
- Keep the existing `speckit.<name>.md` filenames.

Outside those marker blocks and the routine preset normalization, the regular
command bodies should track the upstream release as closely as possible.

## Marker-Aware Rebase Workflow

For the seven regular commands:

1. Inventory the named `spec-kit-canon` overlay blocks from the current local
   canon file.
2. Start from the exported upstream release text for that command.
3. Restore each local overlay block that still belongs in the command, keeping
   the marker names and block contents intact when retained.
4. If the upstream release absorbed or invalidated an overlay, remove that
   overlay instead of re-inserting it.
5. If the upstream release moved the surrounding section, relocate the retained
   overlay to the nearest coherent section rather than preserving stale
   placement mechanically.
6. Reapply only the routine preset normalization for installed preset paths and
   `$ARGUMENTS`.
7. Do not add markers around routine path or placeholder normalization.

Current regular-command overlay inventory:

| Canon target | Named overlay blocks |
| --- | --- |
| `preset/commands/speckit.specify.md` | `preconditions`, `bootstrap-delta-framing`, `bootstrap-delta-guideline` |
| `preset/commands/speckit.clarify.md` | `preconditions` |
| `preset/commands/speckit.checklist.md` | `preconditions` |
| `preset/commands/speckit.plan.md` | `preconditions`, `canon-visible-assumptions` |
| `preset/commands/speckit.tasks.md` | `preconditions`, `post-implementation-canon-drift-note`, `post-implementation-canon-drift-guideline` |
| `preset/commands/speckit.analyze.md` | `preconditions`, `canon-bootstrap-exception` |
| `preset/commands/speckit.implement.md` | `preconditions` |

If a future local command contains an additional named overlay block, treat it
the same way as long as it still satisfies the overlay rules in
`docs/DEVELOPMENT.md`.

Constitution files:

- Reapply canon-specific behavior deliberately.
- Rebase onto the newest upstream release text instead of preserving stale local
  wording by default.
- Re-check every repo path, config key, and workflow rule after the merge.

## Normalization Notes

When the upstream release changes raw repo-source references, port those changes
into the local preset form instead of copying the raw path literally.

Examples:

- Upstream `templates/spec-template.md` becomes
  `.specify/templates/spec-template.md`.
- Upstream repo-source script references should remain runnable for installed
  preset commands under `.specify/scripts/...`.
- Upstream `{ARGS}` usage in markdown command prose should appear as
  `$ARGUMENTS` in the preset source.

If the upstream release changes script flags or command semantics, update the
local frontmatter or prose to preserve that behavior in preset-installed form.

## Validation Checklist

- Review `git diff -- preset`.
- For the seven regular commands, compare the final marker inventory against
  the pre-merge local file. Each retained marker block must have a matching
  start/end pair, and there must be no orphan markers.
- If a previously existing marker block was removed, confirm the removal was
  intentional because upstream now covers that behavior or the local overlay is
  no longer valid.
- For the seven regular commands, make sure any body delta outside the retained
  marker blocks is either:
  - a direct upstream release change, or
  - a required preset normalization described above.
- Confirm the leading `preconditions` overlay still exists in every regular
  command where it existed before unless you intentionally retired it.
- For `speckit.constitution.md` and `constitution-template.md`, verify that the
  canon-specific workflow still references:
  - `.specify/extensions/canon/canon-config.yml`
  - `.specify/templates/constitution-template.md`
  - `.specify/presets/canon-core/templates/canon-toc-template.md`
  - `.specify/presets/canon-core/templates/root-gitattributes-template.txt`
- Verify that the visible upstream-baseline notes in `README.md` and
  `preset/README.md` match the release recorded in
  `preset/spec-kit-release.json`.
- Verify that the command-inventory lists in `README.md` and `preset/README.md`
  still match the actual core-command overrides shipped in `preset/commands/`.
- Verify that `preset/preset.yml` was reviewed for any required
  `requires.speckit_version` update implied by the new upstream baseline.
- Update
  `preset/spec-kit-release.json`
  only after the preset rebase is complete and validated.
- Remove `.tmp/syncing-spec-kit-canon-core-preset/<tag>/` at the end of the
  workflow unless you intentionally kept it for extra inspection.
- If the constitution workflow changes materially, re-run the shared extension
  validation workflow after finishing the rebase.

## Merge Metadata

Persist the last completed upstream preset merge in:

```text
preset/spec-kit-release.json
```

Minimum tracked fields:

- merge timestamp
- resolved upstream release tag
- upstream release commit

The same resolved upstream release tag must also be reflected in the visible
upstream-baseline notes in `README.md` and `preset/README.md`.

Do not update that file during the export step. Update it only after:

1. the preset files were actually rebased
2. validation passed
3. you are ready to delete the temporary sync workspace
