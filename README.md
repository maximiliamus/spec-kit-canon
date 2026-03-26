# Spec-Kit Canon

Spec-Kit Canon adds canon-driven workflows to Spec-Kit.

Use it when you want canon (baseline) files to stay the long-lived source of truth, even
when your team works in different styles:

- spec-first delivery with canon woven into the normal Spec-Kit flow
- canon drift recovery after implementation moved ahead of spec
- low-ceremony, code-first vibecoding that still ends with canon updated

The repository ships two packages that are meant to be installed together for
successful use:

- `canon` extension: adds `/speckit.canon.*` namespaced commands
- `canon-core` preset: required companion preset that overrides core
  `/speckit.*` commands with
  canon-driven instructions in their preconditions, while leaving the rest of
  each command prompt original

## Install

Install both packages:

```bash
specify extension add --dev /path/to/spec-kit-canon
specify preset add --dev /path/to/spec-kit-canon/presets/canon-core
```

The extension is not documented as a standalone install. The workflows in this
repo assume the `canon` extension and the `canon-core` preset are both active
in the project.

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
- branch type to change-classification mappings
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
cleanly under `perform`, `security`, `devops` or `document`.

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

Then run:

```text
/speckit.constitution
```

That initializes or repairs the canon-driven project baseline:

- `.specify/memory/constitution.md`
- `.specify/templates/constitution-template.md`
- `<canon.root>/_toc.md`

## Which Workflow To Use

- All workflows below assume both the `canon` extension and the `canon-core`
  preset are installed.
- Use the canon-driven standard Spec-Kit workflow when you want the normal
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
- `/speckit.canon.drift` is the standard drift orchestrator. It runs the full
  drift pipeline, but `/speckit.canon.drift-resolve` always stays interactive
  so the developer can validate rejected items.
- `/speckit.canon.vibecode-drift` is the zero-touch orchestrator for the full
  vibecode sync path.
- `/speckit.canon.vibecode-drift-express` is the all-in-one express command
  for smaller, contained codebase changes when you want to avoid the longer
  drift path used for more complex changes.

## Workflow 1: Canon-Driven Standard Spec-Kit / Spec-First Start

Purpose:
Use the normal Spec-Kit flow to evolve canon alongside implementation.
After implementation is complete, you may still make small follow-up changes
in the codebase to polish the result, and those changes can introduce canon drift.

How to use it:
Run the familiar core commands in the normal Spec-Kit workflow, for example:

```text
/speckit.specify "Add bulk user import"
/speckit.clarify
/speckit.plan
/speckit.checklist
/speckit.tasks
/speckit.analyze
/speckit.implement
```

What changes compared with stock Spec-Kit:

- branch rules and examples come from `canon-config.yml`
- the constitution and canon TOC are initialized from canon-specific templates
- the prompts treat canon as a first-class reference during specification,
  planning, task generation, analysis, and implementation
- drift workflows compare the feature branch against the configured
  `branching.base` branch

## Workflow 2: Standard Canon Drift Recovery

Purpose:
Bring canon back in sync after code changed on a feature branch.

Use this path for a normal Spec-Kit feature that already has the standard
artifacts from the usual flow: `spec.md`, `plan.md`, and `tasks.md`.
`tasks.md` is required by the drift pipeline, and `plan.md` is used as review
context during drift handling. If you started with
`/speckit.canon.vibecode-specify`, use the vibecode sync workflow instead.

Recommended entry point is the orchestration command:

```text
/speckit.canon.drift
```

What the orchestrator does:

1. Reverse-engineers implementation work into `tasks.drift.md`
2. Detects spec-level drift into `spec.drift.md`
3. Stops for developer review during `/speckit.canon.drift-resolve`
4. Reconciles accepted drift into `canon.drift.md`
5. Applies canon updates
6. Analyzes canon consistency and repairs it if needed

If you want to run the phases yourself, use the individual commands:

- `/speckit.canon.drift-reverse`: create `tasks.drift.md` from code changes
- `/speckit.canon.drift-detect`: create `spec.drift.md` from `tasks.drift.md`
- `/speckit.canon.drift-resolve`: resolve open items in `spec.drift.md`
- `/speckit.canon.drift-reconcile`: create `canon.drift.md` from accepted drift
- `/speckit.canon.drift-canonize`: apply `canon.drift.md` to canon files
- `/speckit.canon.drift-analyze`: check applied canon changes for issues
- `/speckit.canon.drift-repair`: write and apply `canon.repair.md`

`/speckit.canon.drift-analyze` works like the original `/speckit.analyze`:
it does not write an artifact file and only prints a report in command output.
If issues are found, `/speckit.canon.drift-repair` turns them into
`canon.repair.md` and applies the fixes.

## Workflow 3: Canon-Driven Vibecoding / Code-First Start

Purpose:
Create a feature branch and start coding with minimal ceremony.

Start this workflow from the configured `branching.base` branch.

How to start a vibecoding session:

Ad-hoc session:

```text
/speckit.canon.vibecode-specify
```

Use this when you want to start a vibecode session without providing any
intent up front. The command creates a generic vibecode branch and records an
ad-hoc session in `vibecode.md`.

Named session:

```text
/speckit.canon.vibecode-specify api-cleanup
```

Use this when you already know the short name you want for the session. The
command uses that identifier as the branch slug and starts vibecoding without a
longer written intent.

Intent-driven session:

```text
/speckit.canon.vibecode-specify "Polish the admin dashboard and fix sidebar bugs"
```

Use this when you want to describe the work in natural language. The command
derives a slug from the text and records the full intent in `vibecode.md`.

What it does:

- creates a Git feature branch and Spec-Kit feature directory
- writes `vibecode.md` to capture intent and notes
- skips `spec.md`, `plan.md`, and `tasks.md` at the start

This is the entry point for code-first work when you do not want to run the
full spec-first pipeline before implementation.

## Workflow 4: Vibecoding Canon Drift Recovery

After a vibecoding session, use one of these paths to bring canon back in sync
with the code on your feature branch.

Fastest path for smaller codebase changes:

```text
/speckit.canon.vibecode-drift-express
```

This runs reverse -> detect -> reconcile -> canonize in one pass, writes the
drift artifacts, may prompt before overwriting existing drift artifacts, and
asks for confirmation before applying canon changes. Use it for smaller,
contained changes when you want a short all-in-one update path instead of the
longer drift workflow used for more complex work.

Zero-touch path:

```text
/speckit.canon.vibecode-drift
```

This runs the full autonomous vibecoding pipeline, including analyze and repair.

Run either vibecoding sync path from the feature branch created for the
vibecoding session, not from the configured base branch.

Manual path:

- `/speckit.canon.vibecode-drift-reverse`: create `tasks.drift.md` from code changes
- `/speckit.canon.vibecode-drift-detect`: create `spec.drift.md` from `tasks.drift.md`
- `/speckit.canon.vibecode-drift-reconcile`: create `canon.drift.md` from accepted drift
- `/speckit.canon.vibecode-drift-canonize`: apply `canon.drift.md` to canon files
- `/speckit.canon.drift-analyze`: check applied canon changes for issues
- `/speckit.canon.drift-repair`: write and apply `canon.repair.md`

Use the manual path when you want to inspect intermediate artifacts before
canon is updated. After `vibecode-drift-canonize`, the workflow reuses the
standard `drift-analyze` and `drift-repair` commands.
`drift-analyze` does not create a file; it prints a report in command output
only, and `drift-repair` uses that report or regenerates repair candidates.

## Files And Artifacts

The main files introduced by this extension are:

- `.specify/extensions/canon/canon-config.yml`: project canon settings
- `.specify/memory/constitution.md`: active constitution used by Spec-Kit
- `<canon.root>/_toc.md`: canon entry point
- `<feature>/vibecode.md`: lightweight intent file for code-first sessions
- `<feature>/tasks.drift.md`: reverse-engineered implementation tasks
- `<feature>/spec.drift.md`: spec-level drift findings
- `<feature>/canon.drift.md`: proposed or applied canon updates
- `<feature>/canon.repair.md`: optional repair artifact when analysis
  finds canon issues after canon apply

There is intentionally no separate analyze artifact file.
`/speckit.canon.drift-analyze`, like `/speckit.analyze`, outputs a report only.

## Development

See [DEVELOPMENT.md](./DEVELOPMENT.md) for the local extension and preset
development workflow. At minimum, keep the upstream `spec-kit` repository in
the same workspace as this repo so you can validate against the real local
`specify` CLI.

## Notes

- The extension expects the standard Spec-Kit commands referenced by the canon
  workflows, especially `speckit.specify`, `speckit.tasks`, and
  `speckit.implement`.
- The extension commands stay namespaced under `speckit.canon.*`.
- Successful use of this extension assumes the `canon-core` preset is also
  installed, because the workflows rely on the preset's canon-driven core
  commands and constitution initialization.
