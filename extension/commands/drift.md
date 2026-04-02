---
description: Standard drift orchestrator — runs the full drift-to-canon pipeline in default manual or explicit fully autonomous mode; manual resolve and analyze stay direct, and automatic resolve plus analyze remediation are handled by the orchestrator before canonize.
handoffs: []
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-prerequisites.sh --json
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-prerequisites.ps1 -Json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Mode Selection

Classify `$ARGUMENTS` into exactly one orchestration mode for this run:

- **Automatic orchestration mode** only when the user input explicitly requests full implementation-authoritative autonomy with a phrase such as `auto`, `fully autonomous`, `autonomous resolve`, `automatic resolve`, `automatic mode`, `implementation authoritative`, or `implementation prevails`
- **Manual orchestration mode** for all other input, including empty input

Carry this mode through the entire pipeline. In manual mode, Step 3 uses
`/speckit.canon.drift-resolve` directly. In automatic mode, Step 3 resolves
`spec.drift.md` directly in the orchestrator.

---

## Autonomy Principle

This orchestrator is autonomous for delegated steps, but two steps must remain
direct and user-visible:

- **Manual resolve**: because it may require item-level user decisions
- **Analyze**: because draft canon review is read-only, user-visible, and the
  remediation follow-up belongs to the orchestrator rather than the analyze
  command itself

For delegated steps, instruct each subagent:

- Existing artifact overwrite prompts → answer **yes** (overwrite)
- Confirmation gates before applying canon → answer **yes** (proceed)
- Classification choices → use best judgment and proceed
- Any yes/no prompt that belongs only to delegated operational flow → answer **yes**

The only reasons to stop are a hard error, an early exit (no changes detected),
an analyze-review stop choice, a failed analyze verification pass, or
unresolved drift after the single follow-up alignment cycle.

---

## Setup

Before starting Step 1, run `{SCRIPT}` from repo root and parse JSON for
`REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `SPEC_DRIFT`, `TASKS_ALIGNMENT`, and
`CANON_DRIFT`. All paths must be absolute.

If automatic orchestration mode is selected and `TASKS_ALIGNMENT` already exists →
stop and report: "`tasks.alignment.md` already exists for this feature.
Automatic orchestration mode is only allowed on a clean drift branch. Continue
the manual alignment cycle with /speckit.canon.drift-implement then
/speckit.canon.drift-resolve, or delete tasks.alignment.md and restart
/speckit.canon.drift from scratch."

---

## Pipeline

Execute the following steps **in order**. Delegated steps spawn a subagent via
the Agent tool. Direct steps run in the orchestrator itself so user-facing
manual prompts stay interactive and the advisory canon review can surface
issues before canonize. Wait for each step to complete before moving to the
next.

When spawning each subagent, include in the prompt:

1. The command to execute (e.g., `/speckit.canon.drift-reverse`)
2. The delegated-step autonomy instruction: _"Do NOT ask the user any delegated operational questions. If a prompt asks for overwrite confirmation or whether to proceed with canon apply, answer yes and continue."_
3. Any user input from `$ARGUMENTS` if relevant

### Step 1 — Reverse

Spawn subagent: `/speckit.canon.drift-reverse`

Parse result. If zero tasks reported → stop. Report: _"No implementation changes detected. Canon is up to date."_

### Step 2 — Detect

Spawn subagent: `/speckit.canon.drift-detect`

Parse result. If zero findings reported → stop. Report: _"No spec-level drift. Canon is up to date."_

### Step 3 — Resolve / Alignment Cycle

If manual orchestration mode is selected:

- **Do NOT spawn as a subagent.** Execute `/speckit.canon.drift-resolve`
  directly.
- Walk `UNRESOLVED` and `IMPL-REJECTED` items in file order
- Ask the user directly whenever the current item requires authoritative intent
- If alignment work is created, run one follow-up alignment cycle exactly once:
  1. Spawn `/speckit.canon.drift-implement`
  2. Re-run `/speckit.canon.drift-resolve` directly for verification

If automatic orchestration mode is selected:

- Do NOT invoke `/speckit.canon.drift-resolve`
- Read the current `SPEC_DRIFT`
- If `Resolution Status` is already `resolved`, skip Step 3 edits and continue to Step 4
- Traverse `SPEC_DRIFT` top to bottom in file order
- For each outstanding `UNRESOLVED` or `IMPL-REJECTED` item:
  - Re-read the source file(s) cited in the drift item
  - Update the drift item status in `SPEC_DRIFT` to `IMPL-ACCEPTED`
  - Keep the observed implementation behavior as the authoritative truth for downstream reconcile
- Leave existing terminal `ACCEPTED`, `REJECTED`, `SPEC-ACCEPTED`, and `IMPL-ACCEPTED` items unchanged
- No implementation files are edited
- `tasks.alignment.md` must not be created or updated
- If no `UNRESOLVED` or `IMPL-REJECTED` items remain after the automatic pass, append a `## Resolution` section to `SPEC_DRIFT` using the Resolution table format from `.specify/extensions/canon/templates/spec-drift-template.md` and update `Resolution Status` to `resolved`

If `spec.drift.md` is not fully `resolved` after Step 3, stop and report that
manual follow-up is required before reconcile can continue.

### Step 4 — Reconcile

Spawn subagent: `/speckit.canon.drift-reconcile`

Parse result. If zero canon gaps reported → stop. Report: _"All drift already reflected in canon."_

### Step 5 — Analyze Draft Canon Plan

**Do NOT spawn as a subagent.** Execute `/speckit.canon.drift-analyze`
directly. Treat its `Remediation Items` table as the authoritative read-only
remediation output for this step.

If analyze reports zero remediation items → continue to Step 6.

If any Step 5 branch updates `canon.drift.md`, re-run
`/speckit.canon.drift-analyze` directly once for verification before
continuing.

If automatic orchestration mode is selected and remediation items exist:

- Read the current `CANON_DRIFT` file first and keep the constitution-aligned
  draft canon constraints in force during this remediation pass
- Update `canon.drift.md` in the current orchestrator context using **every**
  reported CR-XXX remediation item
- Modify only `canon.drift.md` in this remediation pass; do **not** modify
  canon files yet
- Stay bounded to the reported CR-XXX items and their cited refs; do **not**
  invent additional canon changes
- If the verification pass reports zero remediation items → continue to Step 6
- If the verification pass still reports remediation items → stop and report
  that the revised draft canon plan was preserved for manual review

If manual orchestration mode is selected and remediation items exist, ask the
user directly: _"Analyze found issues in `canon.drift.md`. Choose: remediate now / continue with current draft / stop"_

- **remediate now** → read the current `CANON_DRIFT` file first, then update
  `canon.drift.md` in the current orchestrator context using **every**
  reported CR-XXX remediation item; modify only `canon.drift.md`; stay
  bounded to the reported CR-XXX items and their cited refs
  - If the verification pass reports zero remediation items → continue to Step 6
  - If the verification pass still reports remediation items → stop and report
    that the revised draft canon plan was preserved for manual review
- **continue with current draft** → continue to Step 6
- **stop** → stop and report that the draft canon plan was preserved for further review

### Step 6 — Canonize

Spawn subagent: `/speckit.canon.drift-canonize`

---

## Report

After all steps complete, output a single combined summary:

```text
Standard Drift Pipeline — Complete
====================================
Step 1 — Reverse:    [N] tasks
Step 2 — Detect:     [N] spec drift findings
Step 3 — Resolve:    [N] resolved ([N] SPEC-ACCEPTED, [N] IMPL-ACCEPTED)
Step 4 — Reconcile:  [N] canon entries
Step 5 — Analyze:    [OK | N remediated and verified | N issues reported, continued by user choice]
Step 6 — Canonize:   [N] canon files modified

Artifacts:
  - FEATURE_DIR/tasks.drift.md
  - FEATURE_DIR/spec.drift.md
  [- FEATURE_DIR/tasks.alignment.md]  (if alignment work was deferred)
  - FEATURE_DIR/canon.drift.md

Canon updated successfully.
```

If alignment work was created during manual resolve: _"[N] items were routed
through `tasks.alignment.md`, implemented via `/speckit.canon.drift-implement`,
and re-verified by `/speckit.canon.drift-resolve` before reconcile continued."_

If the user chose **continue with current draft** in manual mode: _"Analyze
reported [N] issue(s); canonize proceeded by explicit user choice."_

If automatic orchestration mode was used: _"Automatic orchestration mode was
requested, so the orchestrator itself converted all remaining spec conflicts to
`IMPL-ACCEPTED`, and any analyze remediation items were applied to
`canon.drift.md` automatically when the verification pass succeeded."_

If the pipeline stops in Step 5 without canonize: output `Standard Drift
Pipeline — Stopped` instead of `Complete`, summarize the last completed step,
state whether the draft canon plan was preserved for review, and list the same
artifact paths.

---

## Rules

- **Default to manual orchestration mode.** Only explicit user input switches the run into fully autonomous implementation-authoritative mode.
- **Delegate only non-interactive steps.** Reverse, Detect, Reconcile, Canonize, and manual alignment implementation may run via subagents. Manual resolve and Analyze run directly in the orchestrator.
- **Sequential execution.** Each step must complete before the next begins.
- **Resolve ownership is mode-dependent.** Manual Step 3 uses `/speckit.canon.drift-resolve`; automatic Step 3 resolves `spec.drift.md` in the orchestrator by converting remaining conflicts to `IMPL-ACCEPTED`.
- **Manual alignment cycle only.** If manual Step 3 creates `tasks.alignment.md`, the orchestrator may run exactly one `/speckit.canon.drift-implement` follow-up and one re-verification `/speckit.canon.drift-resolve` pass.
- **Analyze is read-only.** The analysis report may surface remediation items, but any follow-up edits to `canon.drift.md` belong to the orchestrator.
- **Automatic mode never creates alignment work.** In automatic orchestration mode, implementation always prevails spec during Step 3, so `tasks.alignment.md` must not be created or updated.
- **Remediation passes are bounded.** Any remediation pass in Step 5 may modify only `canon.drift.md` and only according to the reported CR-XXX items and cited refs.
