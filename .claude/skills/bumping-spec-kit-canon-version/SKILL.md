---
name: bumping-spec-kit-canon-version
description: Claude skill entrypoint for the shared Spec Kit Canon version bump workflow. Use when Claude needs to default to the next minor version in `extension/extension.yml` and `preset/preset.yml`, update the pinned release commands in `INSTALL.md` and `UPGRADE.md`, keep documented base Spec Kit versions aligned with `preset/spec-kit-release.json`, update `CHANGELOG.md` automatically from Conventional Commit subjects, bump only patch or major when that scope is explicitly requested, or apply an exact version only when the user explicitly provides one.
---

# Bumping Spec Kit Canon Version

This is the Claude skill entrypoint for the shared skill source in
`skills/bumping-spec-kit-canon-version`.

Before doing any work:

1. Read `skills/bumping-spec-kit-canon-version/SKILL.md`.
2. Use `skills/bumping-spec-kit-canon-version/scripts/set_manifest_versions.py`.
3. Treat an unspecified bump as `minor`, and use `patch`, `major`, or an exact
   version only when the prompt explicitly asks for that behavior. Accept both
   `bump extension version patch` and `bump extension patch version` style
   phrasing for explicit bump kinds.
4. Update `CHANGELOG.md` unless the prompt explicitly asks to skip it.

## Wrapper Rules

- Treat `skills/bumping-spec-kit-canon-version/SKILL.md` as the canonical
  workflow.
- Start version updates with
  `skills/bumping-spec-kit-canon-version/scripts/set_manifest_versions.py`.
- Preserve the exact bump intent from the prompt instead of upgrading or
  downgrading it implicitly.
- Treat changelog generation as part of the default workflow, not an optional
  follow-up step.
- Do not duplicate or fork the workflow in this entrypoint.
- Keep Claude-specific behavior limited to skill invocation concerns.
