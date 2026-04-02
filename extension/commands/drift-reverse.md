---
description: Reverse-engineer tasks from implementation and identify task-level drift against the original `tasks.md` — write only drifted tasks to `tasks.drift.md`.
handoffs:
  - label: Detect Spec Drift
    agent: speckit.canon.drift-detect
    prompt: Scan `tasks.drift.md` and detect spec-level drift against `spec.md`.
    send: false
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-prerequisites.sh --json --require-tasks
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks
---

## Pre-conditions (execute before any other step)

Before analyzing anything:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to all subsequent steps:
   - **Section 3 — Separation of Abstraction Levels**: `tasks.drift.md` records granular implementation groupings at the task level; do not elevate to spec-level concerns here
   - **Section 8 — No Hallucinated Requirements**: only report tasks that are directly observable in the codebase; never infer or assume undocumented behavior
   - **Section 10 — Terminology**: use Canon terminology when describing task items

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `TASKS`, `TASKS_DRIFT`, and `BASE_BRANCH`. All path values must be absolute.

Then check `TASKS_DRIFT`:

- If it exists, read it first and ask the user whether to overwrite or abort.

---

## Step 1 — Load context

- **REQUIRED**: Read `TASKS` for the original planned task list used as the comparison baseline
- **REQUIRED**: Read `FEATURE_SPEC` for the feature requirements baseline used to interpret the intent of implemented work
- **IF EXISTS**: Read `FEATURE_DIR/plan.md` for intended architecture and file structure used to group and scope reverse-engineered tasks
- **IF EXISTS**: Read `FEATURE_DIR/data-model.md` for intended entity definitions used to understand data-shape changes in implementation
- **IF EXISTS**: Read `FEATURE_DIR/research.md` for confirmed decisions and rationale that may explain why implementation diverged from the original task plan

---

## Step 2 — Scan implementation

### 2.1 Collect changes

- Run `git diff <BASE_BRANCH>...HEAD --name-status` to identify all files added, modified, or deleted on this branch
- Run `git log <BASE_BRANCH>..HEAD --oneline` to understand the commit history on this branch
- If there are uncommitted worktree changes, also run `git diff --name-status` and `git diff --cached --name-status` to capture staged and unstaged changes
- Combine all sources into a single deduplicated file list

### 2.2 Read and understand each changed file

- Read every changed file (or the relevant changed portions for large files)
- For deleted files, note the deletion and check git history for what was removed
- Understand the purpose and behavior of each change

### 2.3 Group into logical tasks

- Cluster related file changes into coherent implementation tasks
- Each task should represent a single logical unit of work
- A file may appear in more than one task if it contains changes for multiple logical purposes — note this when it occurs
- Order tasks by logical dependency (foundational changes first)

---

## Step 3 — Compare against original `tasks.md`

For each reverse-engineered task from Step 2, compare it against the original `tasks.md`:

### 3.1 Identify `ADDED` Tasks

Tasks that exist in the implementation but have **no corresponding task** in the original `tasks.md`:

- Net-new work done outside the original plan
- Features or fixes that emerged during development
- Assign drift kind `ADDED`

### 3.2 Identify `UPDATED` Tasks

Tasks that map to an original `tasks.md` entry but where the **implementation differs** from what was planned:

- Different files changed than planned
- Different behavior implemented than described
- Broader or narrower scope than the original task
- Assign drift kind `UPDATED`
- Record the original task ID (T0XX) for traceability

### 3.3 Identify `CANCELED` Tasks

Tasks defined in the original `tasks.md` that have **no corresponding implementation**:

- Scan every task in `tasks.md` that is not matched by any reverse-engineered task
- The task was either skipped entirely or explicitly removed during development
- Assign drift kind `CANCELED`
- Record the original task ID (T0XX) for traceability

### 3.4 Filter — keep only drifted tasks

**CRITICAL**: Do NOT include tasks where the implementation matches the original `tasks.md` exactly. Only write tasks with drift kind `ADDED`, `UPDATED`, or `CANCELED`. Tasks that were implemented as planned are not drift and must be excluded.

---

## Step 4 — Write `TASKS_DRIFT`

Load `.specify/extensions/canon/templates/tasks-drift-template.md` and use it as the structural guide. Fill in findings from Steps 2–3, replacing placeholders with concrete data. Set `**Resolution Status**` to `classified`.

- Use globally incrementing IDs (TD-001, TD-002, ...) across all sections
- Include file-level evidence for each task
- For `UPDATED` and `CANCELED` tasks, reference the original task ID from `tasks.md`

---

## Step 5 — Validate

- Confirm every `ADDED` task has at least one changed file as evidence
- Confirm every `UPDATED` task references a valid original task ID from `tasks.md`
- Confirm every `CANCELED` task references a valid original task ID from `tasks.md`
- Confirm no task that was implemented as planned is included (zero drift = excluded)

---

## Step 6 — Report

After completing all steps, output:

1. **Summary**: path to `TASKS_DRIFT`, counts per drift kind (Added / Updated / Canceled)
2. **Task list**: list each TD-XXX with its title and drift kind
3. **Coverage**: "N of M original tasks matched implementation exactly (no drift)" — where M is total tasks in `tasks.md`
4. **Next step**: "Review `tasks.drift.md`, then run /speckit.canon.drift-detect to detect spec-level drift."

---

## Rules

- This is a single-pass, non-interactive workflow (except for the overwrite prompt if `tasks.drift.md` exists).
- Do NOT modify `TASKS`, `FEATURE_SPEC`, canon files, or any other file. Only write `TASKS_DRIFT`.
- Do NOT include tasks that were implemented exactly as planned — only drifted tasks.
- Do NOT classify at the spec level — that is done by /speckit.canon.drift-detect.
- Ensure each output task follows the tasks-drift-template format exactly.
