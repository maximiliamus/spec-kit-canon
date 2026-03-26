# Canon Core Overrides

This preset overrides the core Spec Kit commands with canon-driven variants.

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

## Install

```bash
specify preset add --dev /path/to/spec-kit-canon/presets/canon-core
```

For the full canon workflow, install this preset together with the extension:

```bash
specify extension add --dev /path/to/spec-kit-canon
specify preset add --dev /path/to/spec-kit-canon/presets/canon-core
```

## Notes

- The preset overrides core command prompts and ships a `constitution-template` baseline inside the preset package with only four metadata placeholders: `PROJECT_NAME`, `CONSTITUTION_VERSION`, `RATIFICATION_DATE`, and `LAST_AMENDED_DATE`.
- The preset also ships a starter `canon-toc-template` used to initialize the configured canon TOC.
- Canon drift workflows remain in the extension under `speckit.canon.*`.
- Project name, canon root, branch type codes, and branch area codes are sourced from the installed canon extension config at `.specify/extensions/canon/canon-config.yml`.
- The command overrides were normalized to use Spec Kit `scripts` / `agent_scripts` frontmatter for shell-aware script selection.
- `/speckit.constitution` is rewritten to initialize the configured canon root and TOC, use `.specify/presets/canon-core/templates/constitution-template.md` as the bundled constitution source, regenerate the Section 6 type and area tables from `.specify/extensions/canon/canon-config.yml`, preserve the four metadata placeholders in `.specify/templates/constitution-template.md`, and write resolved values into `.specify/memory/constitution.md`.
