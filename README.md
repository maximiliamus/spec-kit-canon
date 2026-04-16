# ![Latest Release](https://img.shields.io/github/v/release/maximiliamus/spec-kit-canon?logo=github&label=spec-kit-canon) ![Spec Kit Version](https://img.shields.io/badge/spec--kit-v0.6.1-blue?logo=github) 

# Spec Kit Canon

## What is "Canon"?

**Canon** is a body of work, rules, or descriptions that are considered
authoritative and official. The same way a book series has a "canon"
storyline that is considered official, a codebase can have a **canonical
specification** — one agreed-upon description of how the system is supposed to
work.

Spec Kit Canon uses this idea: you maintain a set of Markdown files (the
**canon**) as the official, long-lived source of truth for your project's
design. The canon is not meant to be a single file — it can be organized into
nested areas or folders, each with its own `_toc.md` table-of-contents index,
and can include domain, business, architecture, terminology, workflow, or other
project-specific details.

## Why Spec Kit Canon?

Spec Kit Canon adds canon-driven (baseline-driven) workflows to
[Spec Kit](https://github.com/github/spec-kit).

In practice, code drifts from its specification — through feature work, bug
fixes, or quick vibecoding sessions. Spec Kit Canon gives you structured
workflows to detect that drift and bring canon and code back in sync, whether
you start from a spec or jump straight into implementation.

Use it when you want canon to remain the authoritative baseline as the team
moves between spec-first work, post-implementation drift repair, and
low-ceremony vibecoding.

This repository publishes two packages that are meant to be installed together:

- `canon` extension: adds `/speckit.canon.*` namespaced commands for canon drift management in spec-first (original Spec Kit) and code-first (new vibecoding) workflows
- `canon-core` preset: adapts core `/speckit.*` commands for
  canon-driven workflows and replaces the default constitution/bootstrap behavior

## Install and Upgrade

Install both packages together from the current release. For step-by-step
release installation commands, see
[INSTALL.md](./docs/INSTALL.md).

For existing projects, upgrade the Spec Kit CLI and refresh the target
project before reinstalling `canon` and `canon-core` from the same version.
The full upgrade procedure is in [UPGRADE.md](./docs/UPGRADE.md).

If you install only the extension, you get the namespaced
`/speckit.canon.*` commands. The full canon-driven workflow documented here
assumes the `canon-core` preset is also installed.

For a focused reference covering the available workflows, step commands, and
handoff behavior for `speckit.canon.*`, see [WORKFLOWS.md](./docs/WORKFLOWS.md). The
end-to-end orchestrator commands are documented in
[WORKFLOW-ORCHESTRATORS.md](./docs/WORKFLOW-ORCHESTRATORS.md), and the workflow
diagrams are collected in [WORKFLOW-DIAGRAMS.md](./docs/WORKFLOW-DIAGRAMS.md).

The preset adapts these core commands to work together with the extension:

- `speckit.specify`
- `speckit.clarify`
- `speckit.checklist`
- `speckit.plan`
- `speckit.tasks`
- `speckit.analyze`
- `speckit.implement`
- `speckit.constitution`

## First-Time Setup

After installing both packages, the project-level canon config lives at:

```text
.specify/extensions/canon/canon-config.yml
```

Edit it to define:

- the project name
- the repo-relative canon root directory
- the base branch used to start vibecoding and for drift comparisons
- branch type to classification mappings
- branch scope codes and descriptions

The shipped default branch type taxonomy includes:

- `feature`
- `behavior`
- `breaking`
- `bugfix`
- `refactor`
- `deprecat`
- `perform`
- `security`
- `devops`
- `document`
- `nonfunc`

Use `nonfunc` as the broad fallback for non-functional work that does not fit
cleanly under `perform`, `security`, `devops`, or `document`.

Example:

```yaml
project:
  name: Example Platform

canon:
  root: specs/000-canon

branching:
  base: main
  types:
    - code: feature
      classification: Feature
    - code: bugfix
      classification: Bug Fix
  scopes:
    - code: api
      description: Public API
    - code: worker
      description: Background jobs
    - code: web
      description: Web application
```

`branching.types` defines the allowed branch type codes for the project. A
branch type describes what kind of change the branch represents, such as a
feature, bug fix, refactor, breaking change, or non-functional work.

`branching.scopes` defines the allowed branch scope codes for the project. A
branch scope describes which system area, domain area, or application surface
the change is focused on, such as the API, worker layer, or web app.

After you run `/speckit.constitution`, these definitions are rendered into
the project constitution and both `/speckit.specify` and
`/speckit.canon.vibecode-specify` will use that branch strategy when they create
branch suffix automatically.

Branch suffix format:

```text
<type>-<scope>-<short-description>
```

With the default Spec Kit sequential numbering, actual branch names become:

```text
(###|YYYYMMDD-HHMMSS)-<type>-<scope>-<short-description>
```

`<type>` must come from `branching.types`, `<scope>` must come from
`branching.scopes`, and `<short-description>` is the generated slug for the
requested change.

After updating the configuration, run:

```text
/speckit.constitution
```

That initializes or repairs the canon-driven project baseline using:

- [extension/canon-config.yml](./extension/canon-config.yml)
- [preset/templates/constitution-template.md](./preset/templates/constitution-template.md)
- [preset/templates/canon-toc-template.md](./preset/templates/canon-toc-template.md)

It writes or refreshes:

- `.specify/memory/constitution.md`
- `.specify/templates/constitution-template.md`
- `<canon.root>/_toc.md` and any nested canon area structure that hangs off it

After generation, review `.specify/memory/constitution.md` and confirm the
rendered project name, branch strategy, and canon structure match your
configuration.

## Which Workflow To Use

- All workflows below assume both the `canon` extension and the `canon-core`
  preset are installed.
- Use the canon-driven standard Spec Kit workflow when you want the normal
  lifecycle to stay canon-driven end to end.
- Use the standard drift workflow when implementation already changed and you
  want a reviewed path back to canon.
- Use the vibecoding workflow when you want to start coding immediately and sync
  canon afterward.
- Optional orchestration commands are available when you want the extension to
  run a full multi-step drift pipeline for you. See
  [WORKFLOW-ORCHESTRATORS.md](./WORKFLOW-ORCHESTRATORS.md).

## Workflow 1: Canon-Driven Standard Spec Kit / Spec-First

Use the normal Spec Kit flow to evolve canon alongside implementation.
Run the familiar core commands in order:

```text
/speckit.specify "Add bulk user import"
/speckit.clarify
/speckit.checklist
/speckit.plan
/speckit.tasks
/speckit.analyze (optional)
/speckit.implement
```

Compared with stock Spec Kit:

- branch rules, allowed type/scope codes, and examples come from
  `canon-config.yml`, so generated branch names stay aligned with project
  conventions
- the constitution and canon TOC are initialized from canon-specific templates
- prompts treat canon as a first-class reference during specification,
  planning, task generation, analysis, and implementation
- drift workflows compare against the configured `branching.base` branch

## Workflow 2: Standard Spec Kit Canon Drift Recovery / Standard Spec-Drift

Use this when implementation already changed on a feature branch and you want
to bring canon back in sync.

Run the step commands in order:

- `/speckit.canon.drift-reverse`
- `/speckit.canon.drift-detect`
- `/speckit.canon.drift-resolve`
- `/speckit.canon.drift-implement` (when `tasks.alignment.md` is created)
- `/speckit.canon.drift-reconcile`
- `/speckit.canon.drift-analyze` (optional)
- `/speckit.canon.drift-canonize`

`/speckit.canon.drift-resolve` is the manual decision and re-verification
step command. Zero-touch implementation-authoritative resolution belongs to
the automatic `/speckit.canon.drift` orchestrator, not to
`/speckit.canon.drift-resolve` itself.

An orchestration command is available to automate this pipeline end to end.
See [WORKFLOW-ORCHESTRATORS.md](./docs/WORKFLOW-ORCHESTRATORS.md).

## Workflow 3: Canon-Driven Vibecoding / Code-First

Start this workflow from the configured `branching.base` branch.

Ad-hoc session:

```text
/speckit.canon.vibecode-specify
```

Named session:

```text
/speckit.canon.vibecode-specify api-cleanup
```

Intent-driven session:

```text
/speckit.canon.vibecode-specify "Polish the admin dashboard and fix sidebar bugs"
```

This command:

- creates a Git feature branch and Spec Kit feature directory using the
  project's sequential or timestamp prefix mode
- writes `vibecode.md` to capture intent and notes
- skips `spec.md`, `plan.md`, and `tasks.md` at the start

After running this command, start implementing whatever you need on the newly created feature branch.

## Workflow 4: Vibecoding Canon Drift Recovery / Vibecoding Spec-Drift

After a vibecoding session, run the step commands in order to bring canon back
in sync with the code on your feature branch:

- `/speckit.canon.vibecode-drift-reverse`
- `/speckit.canon.vibecode-drift-detect`
- `/speckit.canon.vibecode-drift-reconcile`
- `/speckit.canon.vibecode-drift-analyze` (optional)
- `/speckit.canon.vibecode-drift-canonize`

Orchestration command is available to automate this pipeline end to end.
See [WORKFLOW-ORCHESTRATORS.md](./docs/WORKFLOW-ORCHESTRATORS.md).

- `speckit.canon.vibecode-drift-express` is the fast path for small, straightforward
changes that combines the full vibecoding drift pipeline into one command, skipping
the separate analyze step before canonize.

Run the vibecoding sync commands from the feature branch created for the session,
not from the configured base branch.

## Notes

- Standard spec-drift never rewrites the original `spec.md` or `tasks.md`;
  they remain read-only baseline artifacts.
- The extension expects the standard Spec Kit commands referenced by the canon
  workflows, especially `speckit.specify`, `speckit.tasks`, and
  `speckit.implement`.
- The extension commands stay namespaced under `speckit.canon.*`.
- Successful use of this extension assumes the `canon-core` preset is also
  installed, because the workflows rely on the preset's canon-driven core
  commands and constitution initialization.

## Development

See [DEVELOPMENT.md](./docs/DEVELOPMENT.md) for the workspace layout, local
install/test loop, and release packaging details.
