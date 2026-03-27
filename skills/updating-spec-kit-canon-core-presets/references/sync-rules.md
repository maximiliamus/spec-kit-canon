# Sync Rules

## Release Resolution

- Treat the latest release as the highest semantic-version tag visible on
  `../spec-kit` `origin`.
- Do not trust the local clone's tag list by itself.
- If that resolved tag already matches the recorded
  `presets/canon-core/spec-kit-release.json` `spec_kit_release.resolved_tag`,
  stop the sync before export. No `.tmp` workspace or finalize step is needed.
- If the chosen tag is missing locally, fetch that tag before reading source
  files from it.

## Source Map

Regular command overlays:

| Upstream release source | Canon target |
| --- | --- |
| `templates/commands/specify.md` | `presets/canon-core/commands/speckit.specify.md` |
| `templates/commands/clarify.md` | `presets/canon-core/commands/speckit.clarify.md` |
| `templates/commands/checklist.md` | `presets/canon-core/commands/speckit.checklist.md` |
| `templates/commands/plan.md` | `presets/canon-core/commands/speckit.plan.md` |
| `templates/commands/tasks.md` | `presets/canon-core/commands/speckit.tasks.md` |
| `templates/commands/analyze.md` | `presets/canon-core/commands/speckit.analyze.md` |
| `templates/commands/implement.md` | `presets/canon-core/commands/speckit.implement.md` |

Special-case merges:

| Upstream release source | Canon target |
| --- | --- |
| `templates/commands/constitution.md` | `presets/canon-core/commands/speckit.constitution.md` |
| `templates/constitution-template.md` | `presets/canon-core/templates/constitution-template.md` |

Canon-owned files:

- `presets/canon-core/templates/canon-toc-template.md`
- `presets/canon-core/templates/root-gitattributes-template.txt`
- `presets/canon-core/preset.yml`

## Allowed Deltas

Regular commands:

- Keep the canon `## Pre-conditions (execute before any other step)` block.
- Keep preset-ready path normalization:
  - `.specify/templates/...`
  - `.specify/scripts/...`
- Keep markdown argument placeholder normalization as `$ARGUMENTS`.
- Keep the existing `speckit.<name>.md` filenames.

Everything else in the regular command bodies should track the upstream release
as closely as possible.

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

- Review `git diff -- presets/canon-core`.
- For the seven regular commands, make sure any body delta after the
  preconditions block is either:
  - a direct upstream release change, or
  - a required preset normalization described above.
- For `speckit.constitution.md` and `constitution-template.md`, verify that the
  canon-specific workflow still references:
  - `.specify/extensions/canon/canon-config.yml`
  - `.specify/templates/constitution-template.md`
  - `.specify/presets/canon-core/templates/canon-toc-template.md`
  - `.specify/presets/canon-core/templates/root-gitattributes-template.txt`
- Update
  `presets/canon-core/spec-kit-release.json`
  only after the preset rebase is complete and validated.
- Remove `.tmp/updating-spec-kit-canon-core-presets/<tag>/` at the end of the
  workflow unless you intentionally kept it for extra inspection.
- If the constitution workflow changes materially, re-run the shared extension
  validation workflow after finishing the rebase.

## Merge Metadata

Persist the last completed upstream preset merge in:

```text
presets/canon-core/spec-kit-release.json
```

Minimum tracked fields:

- merge timestamp
- resolved upstream release tag
- upstream release commit

Do not update that file during the export step. Update it only after:

1. the preset files were actually rebased
2. validation passed
3. you are ready to delete the temporary sync workspace
