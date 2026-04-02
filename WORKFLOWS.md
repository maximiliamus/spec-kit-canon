# Workflows

`canon` is the Spec Kit extension package from this repository. This document
is the focused workflows-and-commands reference for the extension entry points;
the root [README.md](./README.md) covers the broader extension + preset
workflow.

For visual workflow maps, see [WORKFLOW-DIAGRAMS.md](./WORKFLOW-DIAGRAMS.md).

Most extension commands also read `.specify/memory/constitution.md` and operate
inside the current feature directory plus the configured canon root.

## Standard Spec-First Workflow

For spec-first development, use the original Spec Kit workflow commands such as
`speckit.specify`, `speckit.clarify`, `speckit.plan`, `speckit.checklist`,
`speckit.tasks`, `speckit.analyze`, and `speckit.implement`. The standard drift
commands below are for bringing canon back in sync after implementation has
already diverged from that workflow.

## Standard Spec-Drift Workflow

### Standard Drift Steps

| Command | Short description | Reads / ingests | Writes / produces |
| --- | --- | --- | --- |
| `speckit.canon.drift-reverse` | Reverse-engineers implementation changes into task-level drift against the original plan. | Git diff and worktree state, `tasks.md`, optional `plan.md`, related changed source files. | `tasks.drift.md`. |
| `speckit.canon.drift-detect` | Converts task drift into spec-level drift findings and auto-classifies them as `ACCEPTED`, `REJECTED`, or `UNRESOLVED`. | `tasks.drift.md`, `spec.md`, optional `plan.md`, `data-model.md`, `research.md`, related source files. | `spec.drift.md` with `unresolved` or `resolved` resolution status, depending on whether any items remain unresolved. |
| `speckit.canon.drift-resolve` | Walks `spec.drift.md` and resolves each `UNRESOLVED` or `IMPL-REJECTED` item in manual review mode, including re-verification after deferred alignment work. | `spec.drift.md`, `spec.md`, optional `tasks.alignment.md`, `plan.md`, relevant implementation files. | Updated `spec.drift.md`; may fix implementation files and may write `tasks.alignment.md`. |
| `speckit.canon.drift-implement` | Executes deferred implementation-alignment work created by `drift-resolve`. | `tasks.alignment.md`, `spec.drift.md`, `spec.md`, `plan.md`, related implementation files. | Updated implementation files and `tasks.alignment.md` with task completion state. |
| `speckit.canon.drift-reconcile` | Maps resolved spec drift to concrete canon gaps and proposed canon changes. | Resolved `spec.drift.md`, optional `spec.md` as baseline context, relevant canon files, `<canon.root>/_toc.md`. | `canon.drift.md` with draft canon entries. |
| `speckit.canon.drift-analyze` | Analyzes draft `canon.drift.md` against the full drift state and current canon before canonize. | `tasks.drift.md`, resolved `spec.drift.md`, draft `canon.drift.md`, optional `spec.md` as baseline context, affected canon files, adjacent canon files, `<canon.root>/_toc.md`. | Read-only analysis report with remediation items; never modifies files. |
| `speckit.canon.drift-canonize` | Applies accepted canon entries from the current draft canon plan to the canon tree. | Draft `canon.drift.md`, relevant canon files, `<canon.root>/_toc.md`. | Updated canon files, updated `_toc.md` when needed, and `canon.drift.md` marked `applied`. |

`tasks.alignment.md` uses three progress states at both the top level and the
per-SD task-group level:

- `pending`: no TA-XXX tasks in scope are complete yet
- `in-progress`: some TA-XXX tasks in scope are complete, but unchecked tasks remain
- `implemented`: every TA-XXX task in scope is complete, but `speckit.canon.drift-resolve` still must re-verify the code before reconcile can continue

### Resolve And Reconcile Handoff

Before this handoff:

- `spec.drift.md` starts with `Resolution Status: unresolved` after
  `speckit.canon.drift-detect` when any `UNRESOLVED` items remain.
- If detect finds only terminal `ACCEPTED` or `REJECTED` items, it can write
  `Resolution Status: resolved` immediately and include the Resolution table
  (defined in `extension/templates/spec-drift-template.md`).
- `speckit.canon.drift-resolve` works through item-level statuses such as
  `ACCEPTED`, `REJECTED`, `UNRESOLVED`, `IMPL-REJECTED`,
  `IMPL-ACCEPTED`, and `SPEC-ACCEPTED`.
- `Resolution Status` stays `unresolved` while any `IMPL-REJECTED` item is
  still waiting on deferred alignment work. Resolve only flips the file to
  `resolved` and appends the Resolution section once every item is in a
  terminal state (`ACCEPTED`, `REJECTED`, `IMPL-ACCEPTED`, or
  `SPEC-ACCEPTED`).
- `speckit.canon.drift-reconcile` should run only after `spec.drift.md`
  reaches `Resolution Status: resolved`.

**Table 1 — Command handoff**

| Step | Role | Handoff condition |
| --- | --- | --- |
| `speckit.canon.drift-resolve` | Finishes the decision-making work in `spec.drift.md` by resolving items where spec and implementation disagree. | When `spec.drift.md` reaches `Resolution Status: resolved`, the accepted outcomes are ready for reconcile. |
| `speckit.canon.drift-reconcile` | Converts the resolved accepted outcomes into concrete canon gaps and proposed canon changes. | Produces `canon.drift.md` in `draft` status for review and later apply. |

**Table 2 — `spec.drift.md` item statuses**

| Status | Provenance | Interpretation | What happens next |
| --- | --- | --- | --- |
| `ACCEPTED` | Assigned by detect. | The implementation is already fine as-is for spec-level purposes (net-new valid behavior or deviation justified by `plan.md`/`spec.md`). | Carry it forward into reconcile as authoritative behavior. |
| `REJECTED` | Assigned by detect. | The item is out of scope for spec/canon or too low-level to matter. | Stop here for that item; reconcile skips it. |
| `UNRESOLVED` | Assigned by detect. | Detect found a canon-relevant conflict between spec and implementation but deferred the authoritative decision to resolve. | `drift-resolve` asks the user whether the implemented behavior or the spec expectation should be authoritative. See [WORKFLOW-ORCHESTRATORS.md](./WORKFLOW-ORCHESTRATORS.md) for how `speckit.canon.drift` handles this status in automatic mode. |
| `IMPL-REJECTED` | Assigned by resolve. | Resolve determined the spec is still authoritative, but the implementation still needs follow-up work. | `drift-resolve` either fixes the code now (transitioning the item to `SPEC-ACCEPTED` in the same pass) or records follow-up work in `tasks.alignment.md` and leaves the item `IMPL-REJECTED`; reconcile remains blocked until `drift-implement` runs the follow-up work and a re-verification `drift-resolve` pass promotes the item to `SPEC-ACCEPTED`. |
| `SPEC-ACCEPTED` | Assigned by resolve. | Resolve finished by accepting the spec as the source of truth and bringing the implementation back into line, either by an immediate fix or after a deferred `drift-implement` cycle. | Reconcile treats the corrected spec state as canon-relevant truth. |
| `IMPL-ACCEPTED`\* | Assigned by resolve. | Resolve finished by accepting the implementation as the source of truth and recording that accepted truth in `spec.drift.md`. | Reconcile treats this as canon-relevant truth. |

\* The symmetric `SPEC-REJECTED` status ("spec rejected, implementation accepted as truth") was not retained as a live status; resolve promotes directly to `IMPL-ACCEPTED` without an intermediate rejection marker.

Reconcile treats `ACCEPTED` and `IMPL-ACCEPTED` identically — both are
implementation-authoritative truth carried forward into the canon plan. The two
statuses exist only to preserve provenance: `ACCEPTED` records that detect could
justify the deviation against `plan.md`/`spec.md` without user input, while
`IMPL-ACCEPTED` records that resolve accepted implementation as truth after the
decision was escalated out of detect. Similarly, `SPEC-ACCEPTED` and the
corrected spec state carry forward as canon-relevant truth but preserve the
provenance that resolve chose spec over implementation.

After this handoff:

- `speckit.canon.drift-reconcile` writes `canon.drift.md` with top-level
  `Status: draft`.
- `canon.drift.md` entries use `ACCEPTED` when canon should be updated and
  `REJECTED` when no canon change is needed.
- The next steps are to review `canon.drift.md`, optionally run
  `speckit.canon.drift-analyze` for a read-only verification report with
  remediation items, revise the draft when needed, and then canonize when you
  are ready to proceed.

**Table 3 — `canon.drift.md` item statuses**

| Status | Interpretation | What happens next |
| --- | --- | --- |
| `ACCEPTED` | Canon is missing or outdated for this resolved drift item and should be updated. | `speckit.canon.drift-analyze` reviews the draft entry and may emit CR-XXX remediation items; see [WORKFLOW-ORCHESTRATORS.md](./WORKFLOW-ORCHESTRATORS.md) for how the orchestrators handle those items. |
| `REJECTED` | No canon update is needed because the item is already covered or still below canon level. | Leave canon unchanged for that item. |

## Vibecoding Code-First Workflow

`speckit.canon.vibecode-specify` starts a code-first session from the
configured base branch with minimal ceremony. It reads user input plus branch
numbering config and base branch state, then creates a new feature branch and
directory and writes `vibecode.md`.

It is the vibecoding entry point for starting work before creating standard Spec
Kit artifacts. The command creates the branch and feature directory using the
same numbering and naming rules as `/speckit.specify`, writes
`<feature>/vibecode.md`, deletes the scaffolded `spec.md`, and does not keep
`spec.md`, `plan.md`, or `tasks.md` in the vibecoding workflow.

### Ways To Run `speckit.canon.vibecode-specify`

| Invocation | Input shape | How it is interpreted | Branch slug behavior | What `vibecode.md` contains | Typical use |
| --- | --- | --- | --- | --- | --- |
| `/speckit.canon.vibecode-specify` | No arguments | Ad-hoc vibecoding session | Uses the default slug `vibecode` | Branch metadata, generic ad-hoc intent text, notes section | Start coding without pre-stating scope |
| `/speckit.canon.vibecode-specify api-cleanup` | Single identifier with no spaces | Self-descriptive slug | Uses the identifier directly after branch-name cleaning | Branch metadata, generic ad-hoc intent text, notes section | Start a focused session when the slug already says enough |
| `/speckit.canon.vibecode-specify "Polish the admin dashboard and fix sidebar bugs"` | Natural-language descriptive text with spaces | Intent-driven session | Derives a short slug from the text using the same slugging logic as `/speckit.specify` | Branch metadata, full intent text, lightweight high-level plan, notes section | Start a session with explicit goals captured up front |

### `speckit.canon.vibecode-specify` Behavior

| Behavior area | What happens |
| --- | --- |
| Branch requirement | Must be run from the base branch configured in `.specify/extensions/canon/canon-config.yml` under `branching.base`. |
| Branch numbering | Uses the project's Spec Kit numbering mode from `.specify/init-options.json`: sequential by default, or timestamp when configured. |
| Feature directory | Creates the same style of feature directory as `/speckit.specify`. |
| Main artifact | Writes `<feature>/vibecode.md` as the session's lightweight intent-and-notes file. |
| Standard artifacts | The helper may scaffold `spec.md`, but the command deletes it; the vibecoding workflow does not keep `spec.md`, `plan.md`, or `tasks.md`. |
| Intent handling | Empty or single-slug input produces an ad-hoc session; descriptive text is preserved as intent and expanded into a minimal plan. |
| Next step | After the branch and `vibecode.md` are created, implementation starts immediately; canon sync happens later through the vibecoding spec-drift workflow. |

## Vibecoding Spec-Drift Workflow

| Command | Short description | Reads / ingests | Writes / produces |
| --- | --- | --- | --- |
| `speckit.canon.vibecode-drift-reverse` | Reverse-engineers implementation changes into vibecoding task drift without comparing to an original `tasks.md`. | Git diff and worktree state, optional `plan.md`, related changed source files. | `tasks.drift.md` with all tasks treated as `ADDED`. |
| `speckit.canon.vibecode-drift-detect` | Converts vibecoding task drift into WHAT-level spec findings and auto-accepts them. | `tasks.drift.md`, related source files. | `spec.drift.md` with all items `ACCEPTED` and resolution status `resolved`. |
| `speckit.canon.vibecode-drift-reconcile` | Maps accepted vibecoding spec drift to canon gaps and proposed canon changes. | Resolved `spec.drift.md`, relevant canon files, `<canon.root>/_toc.md`. | `canon.drift.md` with all entries `ACCEPTED` and overall status `draft`. |
| `speckit.canon.vibecode-drift-analyze` | Vibecoding entrypoint alias for the shared draft canon analysis workflow before canonize. | Same inputs as `speckit.canon.drift-analyze`. | Same read-only report and remediation-item output as `speckit.canon.drift-analyze`. |
| `speckit.canon.vibecode-drift-canonize` | Applies a fully accepted vibecoding canon plan from the current draft. | Draft `canon.drift.md` with only `ACCEPTED` entries, relevant canon files, `<canon.root>/_toc.md`. | Updated canon files, updated `_toc.md` when needed, and `canon.drift.md` marked `applied`. |

## Orchestrators

For the end-to-end orchestrator commands that chain the step commands in the
workflows above — `speckit.canon.drift`, `speckit.canon.vibecode-drift`, and
`speckit.canon.vibecode-drift-express`, including their manual and automatic
modes — see [WORKFLOW-ORCHESTRATORS.md](./WORKFLOW-ORCHESTRATORS.md).

## Files And Artifacts

| Artifact | Purpose |
| --- | --- |
| `.specify/extensions/canon/canon-config.yml` | Project canon settings. |
| `.specify/memory/constitution.md` | Active constitution used by Spec Kit. |
| `<canon.root>/_toc.md` | Canon table of contents; updated when canon files or sections are added or reorganized. |
| `<feature>/vibecode.md` | Lightweight intent and notes file for a code-first session. |
| `<feature>/tasks.drift.md` | Task-level reverse-engineering of implementation drift. |
| `<feature>/spec.drift.md` | Spec-level findings derived from task drift. |
| `<feature>/tasks.alignment.md` | Deferred implementation-alignment queue created only by manual resolve when `IMPL-REJECTED` items remain spec-authoritative. |
| `<feature>/canon.drift.md` | Draft canon update plan before canonize, then the applied canon plan after canonize. |
| `<feature>/spec.md` | Feature spec from the standard Spec Kit workflow; standard drift reads it as the original feature baseline and keeps it unchanged. |
| `<feature>/tasks.md` | Original implementation task list; standard drift uses it as the baseline and keeps it unchanged. |

`tasks.alignment.md` uses `pending`, `in-progress`, and `implemented` statuses:
no TA tasks complete yet, partially complete, and fully complete respectively.
Even after `implemented`, `speckit.canon.drift-resolve` still re-verifies the
code before the standard drift pipeline can continue.

There is intentionally no separate analyze artifact file.
`speckit.canon.drift-analyze` produces a read-only report with remediation
items and never modifies `canon.drift.md` directly. Users may apply those
remediation items to the draft canon plan, but analyze itself always stays
read-only. `speckit.canon.vibecode-drift-analyze` is a thin alias for that
same shared workflow.
