# Spec Kit Canon

Spec Kit Canon adds canon-driven (baseline-driven) workflows to Spec Kit.

Use it when you want canon files to remain the long-lived source of truth even
when the team moves between spec-first work, post-implementation drift repair,
and low-ceremony vibecoding.

Canon is the canonical system specification for your project: a set of
Markdown files that fully describes your system. The canon is not meant to be
a single file. It can be organized into nested areas or folders, each with its
own `_toc.md` table-of-contents index, and it can include additional domain,
business, architecture, terminology, workflow, or other project-specific
details that define how the system is supposed to work.

This repository publishes two packages that are meant to be installed together:

- `canon` extension: adds `/speckit.canon.*` namespaced commands for canon drift management in spec-first (original Spec Kit) and code-first (new vibecoding) workflows
- `canon-core` preset: overrides core `/speckit.*` commands with
  canon-driven variants and replaces the default constitution/bootstrap behavior

## Install

Install both packages from a release:

```bash
specify extension add --from https://github.com/maximiliamus/spec-kit-canon/releases/download/<tag>/spec-kit-canon-<tag>.zip
specify preset add --from https://github.com/maximiliamus/spec-kit-canon/releases/download/<tag>/spec-kit-canon-core-<tag>.zip
```

Example for `v0.1.0`:

```bash
specify extension add --from https://github.com/maximiliamus/spec-kit-canon/releases/download/v0.1.0/spec-kit-canon-v0.1.0.zip
specify preset add --from https://github.com/maximiliamus/spec-kit-canon/releases/download/v0.1.0/spec-kit-canon-core-v0.1.0.zip
```

Install both packages from a local checkout:

```bash
specify extension add --dev /path/to/spec-kit-canon/extension
specify preset add --dev /path/to/spec-kit-canon/preset
```

If you install only the extension, you get the namespaced
`/speckit.canon.*` commands. The full canon-driven workflow documented here
assumes the `canon-core` preset is also installed.

The preset overrides these core commands:

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

Then run:

```text
/speckit.constitution
```

That initializes or repairs the canon-driven project baseline:

- `.specify/memory/constitution.md`
- `.specify/templates/constitution-template.md`
- `<canon.root>/_toc.md` and any nested canon area structure that hangs off it

After generation, read `.specify/memory/constitution.md` in full. It contains
the detailed project-specific rules, branch strategy, canon structure, and
workflow expectations that make the canon-driven process easier to understand
and follow.

## Which Workflow To Use

- All workflows below assume both the `canon` extension and the `canon-core`
  preset are installed.
- Use the canon-driven standard Spec Kit workflow when you want the normal
  lifecycle to stay canon-driven end to end.
- Use the standard drift workflow when implementation already changed and you
  want a reviewed path back to canon.
- Use the vibecode workflow when you want to start coding immediately and sync
  canon afterward.
- Use the individual step commands when you need to inspect or edit
  intermediate drift artifacts manually.
- Optional orchestration commands are available when you want the extension to
  run a full multi-step drift pipeline for you instead of invoking each phase
  manually.
- `/speckit.canon.drift` is the standard drift orchestrator.
- `/speckit.canon.vibecode-drift` is the zero-touch vibecode sync orchestrator.
- `/speckit.canon.vibecode-drift-express` is the shorter all-in-one path for
  smaller codebase changes.

## Workflow 1: Canon-Driven Standard Spec Kit / Spec-First

Use the normal Spec Kit flow to evolve canon alongside implementation.
Run the familiar core commands in order:

```text
/speckit.specify "Add bulk user import"
/speckit.clarify
/speckit.plan
/speckit.checklist
/speckit.tasks
/speckit.analyze
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

## Workflow 2: Standard Spec Kit Canon Drift Recovery / Spec-Drift

Use this when implementation already changed on a feature branch and you want
to bring canon back in sync.

Recommended entry point:

```text
/speckit.canon.drift
```

The orchestrator:

1. reverse-engineers implementation work into `tasks.drift.md`
2. detects spec-level drift into `spec.drift.md`
3. stops for developer review during `/speckit.canon.drift-resolve`
4. reconciles accepted drift into `canon.drift.md`
5. applies canon updates
6. analyzes canon consistency and repairs it if needed

Manual phases:

- `/speckit.canon.drift-reverse`
- `/speckit.canon.drift-detect`
- `/speckit.canon.drift-resolve`
- `/speckit.canon.drift-reconcile`
- `/speckit.canon.drift-canonize`
- `/speckit.canon.drift-analyze`
- `/speckit.canon.drift-repair`

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

## Workflow 4: Vibecoding Canon Drift Recovery / Spec-Drift

After a vibecoding session, use one of these paths to bring canon back in sync
with the code on your feature branch.

Fast path:

```text
/speckit.canon.vibecode-drift-express
```

Zero-touch path:

```text
/speckit.canon.vibecode-drift
```

Manual path:

- `/speckit.canon.vibecode-drift-reverse`
- `/speckit.canon.vibecode-drift-detect`
- `/speckit.canon.vibecode-drift-reconcile`
- `/speckit.canon.vibecode-drift-canonize`
- `/speckit.canon.drift-analyze`
- `/speckit.canon.drift-repair`

Run the vibecode sync commands from the feature branch created for the session,
not from the configured base branch.

## Files And Artifacts

The main files introduced by these packages are:

- `.specify/extensions/canon/canon-config.yml`: project canon settings
- `.specify/memory/constitution.md`: active constitution used by Spec Kit
- `<canon.root>/_toc.md`: root canon entry point and top-level table of
  contents
- `<feature>/vibecode.md`: lightweight intent file for code-first sessions
- `<feature>/tasks.drift.md`: reverse-engineered implementation tasks
- `<feature>/spec.drift.md`: spec-level drift findings
- `<feature>/canon.drift.md`: proposed or applied canon updates
- `<feature>/canon.repair.md`: optional repair artifact when analysis finds
  canon issues after canon apply

There is intentionally no separate analyze artifact file.
`/speckit.canon.drift-analyze`, like `/speckit.analyze`, outputs a report only.

## Development

See [DEVELOPMENT.md](./DEVELOPMENT.md) for the workspace layout, local
install/test loop, and release packaging details.

## Notes

- The extension expects the standard Spec Kit commands referenced by the canon
  workflows, especially `speckit.specify`, `speckit.tasks`, and
  `speckit.implement`.
- The extension commands stay namespaced under `speckit.canon.*`.
- Successful use of this extension assumes the `canon-core` preset is also
  installed, because the workflows rely on the preset's canon-driven core
  commands and constitution initialization.
