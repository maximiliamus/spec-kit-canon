---
name: updating-spec-kit-canon-core-presets
description: Claude skill entrypoint for syncing `presets/canon-core` with the latest released upstream `spec-kit` core commands. Use when Claude needs to verify the real latest release tag against `../spec-kit` `origin`, export the upstream release snapshot, rebase the regular command preconditions, and manually merge the `speckit.constitution` and constitution template files.
---

# Updating Spec-Kit Canon Core Presets

This is the Claude skill entrypoint for the shared skill source in
`skills/updating-spec-kit-canon-core-presets`.

Before doing any work:

1. Read `skills/updating-spec-kit-canon-core-presets/SKILL.md`.
2. Read `skills/updating-spec-kit-canon-core-presets/references/sync-rules.md`.
3. Run
   `skills/updating-spec-kit-canon-core-presets/scripts/export_upstream_release.py`
   before editing `presets/canon-core`.

## Wrapper Rules

- Treat the shared skill folder as the canonical workflow.
- Use the export script before comparing or editing preset files.
- Keep Claude-specific behavior limited to invocation concerns.
- Do not duplicate the sync workflow in this entrypoint.
