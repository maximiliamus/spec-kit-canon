# Sync Spec-Kit Canon Core Preset

Use the Claude skill at
`.claude/skills/syncing-spec-kit-canon-core-preset`.

Default behavior:

- verify the latest upstream release tag against `../spec-kit` `origin`
- fetch the release tag locally if it is missing
- export the upstream release snapshot before editing `preset/`
- rebase the seven regular upstream-tracking commands by restoring named
  `spec-kit-canon` overlay blocks plus required preset normalization, and
  manually merge the constitution files

Follow that skill exactly.

Do not duplicate the workflow in this command file.
