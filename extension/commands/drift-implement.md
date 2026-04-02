---
description: Implement deferred alignment tasks from `tasks.alignment.md` and update queue progress state to `pending`, `in-progress`, or `implemented` according to task completion.
handoffs:
  - label: Re-Resolve Drift
    agent: speckit.canon.drift-resolve
    prompt: Re-verify the implementation against `spec.drift.md` after alignment tasks were completed.
    send: false
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-prerequisites.sh --json --require-spec-drift --require-tasks-alignment
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-prerequisites.ps1 -Json -RequireSpecDrift -RequireTasksAlignment
---

## Pre-conditions (execute before any other step)

Before writing any code or making any changes:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to all subsequent steps:
   - **Section 1.2 — Rules for Canon**: do not modify canon files during alignment implementation; always reference canon sections by exact file path
   - **Section 3 — Separation of Abstraction Levels**: `tasks.alignment.md` contains executable implementation work only; do not rewrite drift analysis here
   - **Section 8 — No Hallucinated Requirements**: implement only what is required by `SPEC_DRIFT`, `TASKS_ALIGNMENT`, and supporting implementation context
   - **Section 10 — Terminology**: use Canon terminology exactly in code comments, tests, and docs

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `SPEC_DRIFT`, and `TASKS_ALIGNMENT`. All paths must be absolute.

Read `TASKS_ALIGNMENT` and inspect its top-level `Status` plus TA-XXX checkbox state:

- If every TA-XXX task is already `- [X]` → update any stale task-group or top-level `Status` values to `implemented`, then stop and report: "`tasks.alignment.md` is already fully implemented. Run /speckit.canon.drift-resolve to re-verify drift resolution."
- If top-level `Status` is `implemented` but any TA-XXX task is still unchecked → treat the file as `in-progress` and continue.
- If top-level `Status` is `pending` or `in-progress` and unchecked tasks remain → continue.

---

## Step 1 — Load context

- **REQUIRED**: Read `TASKS_ALIGNMENT` for the deferred alignment queue, pending TA-XXX tasks, target file paths, and dependency order that define the implementation work to complete
- **REQUIRED**: Read `SPEC_DRIFT` for the unresolved or partially resolved spec drift items that explain why each deferred alignment task exists and what behavior must be re-verified afterward
- **REQUIRED**: Read `FEATURE_SPEC` for the authoritative feature requirements and expected behavior that the alignment work must preserve or restore
- **IF EXISTS**: Read `FEATURE_DIR/plan.md` for intended architecture, constraints, and planned implementation structure needed to execute alignment tasks correctly
- **IF EXISTS**: Read `FEATURE_DIR/data-model.md` for entity definitions and field expectations referenced by alignment work that changes data structures
- **IF EXISTS**: Read `FEATURE_DIR/research.md` for prior decisions and rationale needed to avoid re-opening already settled design choices during implementation
- **IF EXISTS**: Read `FEATURE_DIR/contracts/**` for interface and API contracts that alignment tasks may require the implementation to satisfy

---

## Step 2 — Execute pending alignment tasks

- Execute only the unchecked TA-XXX tasks in `TASKS_ALIGNMENT`
- Follow their file paths and dependency order
- If a task is completed successfully, mark it `- [X]`
- If a task cannot be completed, leave it unchecked and continue only when it is safe to do so

Do NOT edit the task definitions themselves except to update checkbox completion state or the top-level and group `Status` fields.

---

## Step 3 — Finalize group and queue status

- For each deferred-alignment group:
  - If every TA-XXX task in the group is `- [X]`, update its `Status` to `implemented`
  - If at least one TA-XXX task in the group is `- [X]` and at least one remains unchecked, update its `Status` to `in-progress`
  - If no TA-XXX task in the group is `- [X]` and at least one remains unchecked, update its `Status` to `pending`
- Then apply the same rule across all TA-XXX tasks in the file for the top-level `**Status**`

---

## Step 4 — Report

- List completed TA-XXX tasks
- List any unchecked tasks that remain
- Report the final top-level queue status
- If the queue is fully implemented: "Run /speckit.canon.drift-resolve next to verify the implementation and finish resolving the linked drift items."
- If the queue is `in-progress`: "Alignment work is in progress. Complete the remaining alignment tasks, then run /speckit.canon.drift-implement again."
- If the queue is still `pending`: "No alignment tasks were completed in this pass. Address the blockers or re-run /speckit.canon.drift-implement when work can proceed."

---

## Rules

- This command implements only the deferred alignment queue.
- Do NOT modify `tasks.md`, `tasks.drift.md`, `canon.drift.md`, or canon files.
- Do NOT change the meaning of any drift item; only implement the pending alignment work and update `tasks.alignment.md`.
- `Status: implemented` must not be trusted by itself. `/speckit.canon.drift-resolve` must re-verify code before the standard drift pipeline can continue.
