# Canon Core Overrides

This package is the `canon-core` preset for Spec Kit.

It overrides selected core Spec Kit commands with canon-driven variants while
leaving the `speckit.canon.*` workflow commands in the separate `canon`
extension package.

## Install

Install from a release asset:

```bash
specify preset add --from https://github.com/maximiliamus/spec-kit-canon/releases/download/<tag>/spec-kit-canon-core-<tag>.zip
```

Install from a local checkout:

```bash
specify preset add --dev /path/to/spec-kit-canon/preset
```

For the full canon workflow, install this preset together with the extension:

```bash
specify extension add --from https://github.com/maximiliamus/spec-kit-canon/releases/download/<tag>/spec-kit-canon-<tag>.zip
specify preset add --from https://github.com/maximiliamus/spec-kit-canon/releases/download/<tag>/spec-kit-canon-core-<tag>.zip
```

## Included Overrides

- `canon-toc-template`
- `constitution-template`
- `speckit.specify`
- `speckit.clarify`
- `speckit.checklist`
- `speckit.plan`
- `speckit.tasks`
- `speckit.analyze`
- `speckit.implement`
- `speckit.constitution`

## Notes

- The preset overrides core command prompts and ships a
  `constitution-template` baseline with only four metadata placeholders:
  `PROJECT_NAME`, `CONSTITUTION_VERSION`, `RATIFICATION_DATE`, and
  `LAST_AMENDED_DATE`.
- The preset also ships a starter `canon-toc-template` used to initialize the
  configured canon TOC.
- Canon drift workflows remain in the extension under `speckit.canon.*`.
- Project name, canon root, base branch, branch type codes, and branch scope
  codes are sourced from the installed extension config at
  `.specify/extensions/canon/canon-config.yml`.
- `/speckit.constitution` is rewritten to initialize the configured canon root
  and TOC, use `.specify/presets/canon-core/templates/constitution-template.md`
  as the bundled constitution source, regenerate the Section 6 type and scope
  tables from `.specify/extensions/canon/canon-config.yml`, preserve the four
  metadata placeholders in `.specify/templates/constitution-template.md`, and
  write resolved values into `.specify/memory/constitution.md`.
