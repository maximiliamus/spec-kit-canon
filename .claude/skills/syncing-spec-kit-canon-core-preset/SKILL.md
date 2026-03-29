---
name: syncing-spec-kit-canon-core-preset
description: Claude skill entrypoint for syncing `preset/` with the latest released upstream `spec-kit` core commands. Use when Claude needs to verify the real latest release tag against `../spec-kit` `origin`, export the upstream release snapshot, rebase the regular upstream-tracking commands by preserving or intentionally retiring named `spec-kit-canon` overlay blocks, and manually merge the `speckit.constitution` and constitution template files.
---

# Syncing Spec-Kit Canon Core Preset

This is the Claude skill entrypoint for the shared skill source in
`skills/syncing-spec-kit-canon-core-preset`.

Before doing any work:

1. Read `skills/syncing-spec-kit-canon-core-preset/SKILL.md`.
2. Read `skills/syncing-spec-kit-canon-core-preset/references/sync-rules.md`.
3. Read the `Marked Local Overlays` section in `DEVELOPMENT.md`.
4. Run
   `skills/syncing-spec-kit-canon-core-preset/scripts/export_upstream_release.py`
   before editing `preset/`.

## Wrapper Rules

- Treat the shared skill folder as the canonical workflow.
- Use the export script before comparing or editing preset files.
- Keep Claude-specific behavior limited to invocation concerns.
- Do not duplicate the sync workflow in this entrypoint.
