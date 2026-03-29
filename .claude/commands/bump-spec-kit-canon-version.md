# Bump Spec-Kit Canon Version

Use the Claude skill at `.claude/skills/bumping-spec-kit-canon-version`.

Default behavior:

- default to the next minor version
- bump `major` or `patch` only when explicitly requested
- accept an exact `0.1.1` or `v0.1.1` only when explicitly requested
- update only `extension/extension.yml` and `preset/preset.yml`
- use `--kind patch|minor|major` for explicit relative bumps
- reset less significant components when bumping a more significant one
- write manifests without the `v` prefix when an exact tag-style version is provided
- verify the two manifest versions match after the edit

Pass the requested bump intent through to the shared skill and follow that
skill exactly.

Accept natural phrasing like `bump extension version`, optional
`major`/`minor`/`patch`, or `to v1.2.3` for an exact version.

Do not duplicate the workflow in this command file.
