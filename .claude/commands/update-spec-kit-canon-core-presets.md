# Update Spec-Kit Canon Core Presets

Use the Claude skill at
`.claude/skills/updating-spec-kit-canon-core-presets`.

Default behavior:

- verify the latest upstream release tag against `../spec-kit` `origin`
- fetch the release tag locally if it is missing
- export the upstream release snapshot before editing `presets/canon-core`
- rebase the seven regular command overlays and manually merge the constitution
  files

Follow that skill exactly.

Do not duplicate the workflow in this command file.
