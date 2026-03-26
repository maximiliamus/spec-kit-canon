# Spec-Kit Canon

Spec-Kit Canon packages a canon-driven workflow as:

- a Spec-Kit extension for `speckit.canon.*` commands
- an optional preset for overriding core `speckit.*` commands with canon-driven variants

## Included Commands

- `speckit.canon.drift`
- `speckit.canon.drift-analyze`
- `speckit.canon.drift-canonize`
- `speckit.canon.drift-detect`
- `speckit.canon.drift-reconcile`
- `speckit.canon.drift-repair`
- `speckit.canon.drift-resolve`
- `speckit.canon.drift-reverse`
- `speckit.canon.vibecode-drift`
- `speckit.canon.vibecode-drift-canonize`
- `speckit.canon.vibecode-drift-detect`
- `speckit.canon.vibecode-drift-express`
- `speckit.canon.vibecode-drift-reconcile`
- `speckit.canon.vibecode-drift-reverse`
- `speckit.canon.vibecode-specify`

All commands are currently exposed only under their canonical extension names.

## Install

Extension:

```bash
specify extension add --dev /path/to/spec-kit-canon
```

Optional preset for core command overrides:

```bash
specify preset add --dev /path/to/spec-kit-canon/presets/canon-core
```

## Development

See [DEVELOPMENT.md](./DEVELOPMENT.md) for the local extension and preset
development workflow. At minimum, keep the upstream `spec-kit` repository in
the same workspace as this repo so you can validate against the real local
`specify` CLI.

## Project Config

After installing the extension, project-specific canon settings live in:

```text
.specify/extensions/canon/canon-config.yml
```

Edit `project.name`, `canon.root`, `branching.types`, or `branching.areas`, then rerun
`/speckit.constitution` to regenerate constitution metadata and the Section 6
branch strategy tables.

Example:

```yaml
project:
  name: Example Platform

canon:
  root: specs/000-canon

branching:
  types:
    - code: feature
      classification: Feature
    - code: bugfix
      classification: Bug Fix
  areas:
    - code: api
      description: Public API
    - code: worker
      description: Background jobs
    - code: web
      description: Web application
```

## Notes

- The extension expects the standard Spec-Kit core commands referenced by the imported workflows: `speckit.implement`, `speckit.specify`, and `speckit.tasks`.
- The extension bundles mirrored helper scripts under `scripts/bash/` and `scripts/powershell/`. Commands now select the appropriate variant through frontmatter `scripts` / `agent_scripts`.
- The extension ships `canon-config.yml`, which becomes `.specify/extensions/canon/canon-config.yml` in the project and acts as the source of truth for project name, canon root, branch type codes, and branch area codes.
- Install the `presets/canon-core` preset if you want `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`, `/speckit.constitution`, and related core commands to use the canon-driven prompt variants.
- The `canon-core` preset also ships a canon constitution baseline with limited metadata placeholders plus a starter canon TOC template, and `/speckit.constitution` initializes `<canon.root>/_toc.md`, preserves the constitution placeholders in `.specify/templates/constitution-template.md`, and resolves them into `.specify/memory/constitution.md`.
