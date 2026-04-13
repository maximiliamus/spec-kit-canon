---
description: Vibecoding drift orchestrator — runs the full vibecoding drift-to-canon pipeline in default manual review mode or explicit automatic remediation mode; analyze stays direct, and analyze remediation is handled by the orchestrator before canonize.
handoffs: []
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-prerequisites.sh --json --canon
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-prerequisites.ps1 -Json -Canon
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Mode Selection

Classify `$ARGUMENTS` into exactly one orchestration mode for this run:

- **Automatic orchestration mode** only when the user input explicitly requests zero-touch analyze remediation with implementation-authoritative behavior, using a phrase such as `auto`, `fully autonomous`, `automatic mode`, `auto-remediate`, `automatic remediation`, `implementation authoritative`, or `implementation prevails`
- **Manual orchestration mode** for all other input, including empty input

Carry this mode through the entire pipeline.

---

## Autonomy Principle

This orchestrator is autonomous for reverse, detect, reconcile, and canonize
in the vibecoding workflow. Vibecoding still has no Resolve-style human
decision phase because all spec drift findings are auto-accepted.

However, `/speckit.canon.vibecode-drift-analyze` now acts as the draft canon
review step before canonize. It must run directly in the orchestrator because
the analyze report is read-only and any remediation follow-up belongs to the
orchestrator rather than the analyze command itself.

This command does **not** include `/speckit.canon.vibecode-drift-express`.
`/speckit.canon.vibecode-drift-express` remains the manual low-ceremony
shortcut that skips the separate analyze pass for small, straightforward
changes and applies canon within its own command flow.

For delegated steps in this pipeline only:

- overwrite prompts → answer **yes** (overwrite)
- non-user-intent ambiguities → use best judgment and proceed

The only reasons to stop are a hard error, an early exit, an analyze-review
stop choice, or a failed analyze verification pass.

---

## Setup

Before starting Step 1, run `{SCRIPT}` from repo root and parse JSON for
`REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `CANON_DRIFT`, `CANON_ROOT`, and
`CANON_TOC`. All path values must be absolute.

---

## Pipeline

Execute the following steps **in order**. Delegated steps spawn a subagent via
the Agent tool. Analyze runs directly in the orchestrator because it is the
user-visible draft canon review step.

When spawning each subagent, include in the prompt:

1. The command to execute (e.g., `/speckit.canon.vibecode-drift-reverse`)
2. The delegated-step autonomy instruction: _"Do not surface delegated operational prompts to the user. If asked whether to overwrite an existing artifact or another delegated yes/no operational question, answer yes and continue."_
3. Any user input from `$ARGUMENTS` if relevant

### Step 1 — Reverse

Spawn subagent: `/speckit.canon.vibecode-drift-reverse`

Parse result. If zero tasks reported → stop. Report: _"No implementation changes detected. Canon is up to date."_

### Step 2 — Detect

Spawn subagent: `/speckit.canon.vibecode-drift-detect`

Parse result. If zero findings reported → stop. Report: _"No spec-level drift. Canon is up to date."_

### Step 3 — Reconcile

Spawn subagent: `/speckit.canon.vibecode-drift-reconcile`

Parse result. If zero canon gaps reported → stop. Report: _"All drift already reflected in canon."_

### Step 4 — Analyze Draft Canon Plan

**Do NOT spawn as a subagent.** Execute `/speckit.canon.vibecode-drift-analyze`
directly. Treat its `Remediation Items` table as the authoritative read-only
remediation output for this step.

If analyze reports zero remediation items → continue to Step 5.

If any Step 4 branch updates `canon.drift.md`, re-run
`/speckit.canon.vibecode-drift-analyze` directly once for verification before
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
- If the verification pass reports zero remediation items → continue to Step 5
- If the verification pass still reports remediation items → stop and report
  that the revised draft canon plan was preserved for manual review

If manual orchestration mode is selected and remediation items exist, ask the
user directly: _"Analyze found issues in `canon.drift.md`. Choose: remediate now / continue with current draft / stop"_

- **remediate now** → read the current `CANON_DRIFT` file first, then update
  `canon.drift.md` in the current orchestrator
  context using **every** reported CR-XXX remediation item; modify only
  `canon.drift.md`; stay bounded to the reported CR-XXX items and their cited
  refs
  - If the verification pass reports zero remediation items → continue to Step 5
  - If the verification pass still reports remediation items → stop and report
    that the revised draft canon plan was preserved for manual review
- **continue with current draft** → continue to Step 5
- **stop** → stop and report that the draft canon plan was preserved for further review

### Step 5 — Canonize

Spawn subagent: `/speckit.canon.vibecode-drift-canonize`

---

## Report

After all steps complete, output a single combined summary:

```text
Vibecoding Drift Pipeline — Complete
===================================
Step 1 — Reverse:    [N] tasks
Step 2 — Detect:     [N] spec drift findings
Step 3 — Reconcile:  [N] canon entries
Step 4 — Analyze:    [OK | N remediated and verified | N issues reported, continued by user choice]
Step 5 — Canonize:   [N] canon files modified

Artifacts:
  - FEATURE_DIR/tasks.drift.md
  - FEATURE_DIR/spec.drift.md
  - FEATURE_DIR/canon.drift.md

Canon updated successfully.
```

- If the user chose **continue with current draft** in manual mode: append
  _"Analyze reported [N] issue(s); canonize proceeded by explicit user choice."_
- If automatic orchestration mode was used: _"Automatic orchestration mode was
requested, so any analyze remediation items were applied to `canon.drift.md`
automatically when the verification pass succeeded."_
- If the pipeline stops in Step 4 without canonize: output `Vibecoding Drift
  Pipeline — Stopped` instead of `Complete`, summarize the last completed step,
  state whether the draft canon plan was preserved for review, and list the
  same artifact paths.

---

## Rules

- **Default to manual orchestration mode.** Only explicit user input switches the run into automatic orchestration mode with automatic analyze remediation.
- **Autonomous until the canon review step.** Reverse, Detect, Reconcile, and Canonize are delegated; Analyze runs directly.
- **No Resolve phase in vibecoding.** All spec drift findings are treated as intentional implementation truth.
- **Sequential execution.** Each step must complete before the next begins.
- **Analyze is read-only.** The analysis report may surface remediation items, but any follow-up edits to `canon.drift.md` belong to the orchestrator.
- **Remediation passes are bounded.** Any remediation pass in Step 4 may modify only `canon.drift.md` and only according to the reported CR-XXX items and cited refs.
