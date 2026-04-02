---
description: Reverse-engineer tasks from implementation — group worktree changes into logical tasks and write tasks.drift.md. Vibecoding variant — no original tasks.md required; all tasks classified as `ADDED`.
handoffs:
  - label: Detect Spec Drift
    agent: speckit.canon.vibecode-drift-detect
    prompt: Scan tasks.drift.md and detect spec-level drift against canon.
    send: true
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-prerequisites.sh --json
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-prerequisites.ps1 -Json
---

## Pre-conditions (execute before any other step)

Before analyzing anything:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to all subsequent steps:
   - **Section 3 — Separation of Abstraction Levels**: tasks.drift.md records granular implementation groupings at the task level; do not elevate to spec-level concerns here
   - **Section 8 — No Hallucinated Requirements**: only report tasks that are directly observable in the codebase; never infer or assume undocumented behavior
   - **Section 10 — Terminology**: use Canon terminology when describing task items

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `TASKS_DRIFT`, and `BASE_BRANCH`. All path values must be absolute.

Then check `TASKS_DRIFT`:

- If it exists, read it first and ask the user whether to overwrite or abort.

---

## Step 1 — Load context

- **REQUIRED**: Read `FEATURE_SPEC` for feature requirements context (if it exists)
- **IF EXISTS**: Read `FEATURE_DIR/plan.md` for intended architecture and file structure
- **IF EXISTS**: Read `FEATURE_DIR/data-model.md` for intended entity definitions

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

## Step 3 — Classify All Tasks as `ADDED`

This is a vibecoding workflow — there is no original `tasks.md` to compare against. All reverse-engineered tasks are classified as drift kind `ADDED`.

---

## Step 4 — Write `TASKS_DRIFT`

Load `.specify/extensions/canon/templates/tasks-drift-template.md` and use it as the structural guide. Fill in findings from Steps 2–3, replacing placeholders with concrete data. Set `**Resolution Status**` to `classified`.

- Use globally incrementing IDs (TD-001, TD-002, ...) across all sections
- Include file-level evidence for each task
- All tasks go under the `## Added Tasks` section with drift kind `ADDED`

---

## Step 5 — Validate

- Confirm every changed file appears in at least one task
- Confirm every task has at least one changed file as evidence
- Confirm task descriptions are specific enough to understand the change without reading the code

---

## Step 6 — Report

After completing all steps, output:

1. **Summary**: path to `TASKS_DRIFT`, total task count
2. **Task list**: list each TD-XXX with its title
3. **Next step**: "Review tasks.drift.md, then run /speckit.canon.vibecode-drift-detect to detect spec-level drift."

---

## Rules

- This is a single-pass, non-interactive workflow (except for the overwrite prompt if tasks.drift.md exists).
- Do NOT modify `FEATURE_SPEC`, canon files, or any other file. Only write `TASKS_DRIFT`.
- Do NOT classify at the spec level — that is done by /speckit.canon.vibecode-drift-detect.
- Ensure each output task follows the tasks-drift-template format exactly.
