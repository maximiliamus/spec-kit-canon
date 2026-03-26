---
description: Detect spec-level drift — scan tasks.drift.md and derive spec discrepancies against spec.md/canon, writing findings to spec.drift.md. Vibecode variant — all items auto-ACCEPTED, no resolve step needed.
handoffs:
  - label: Plan Canonization
    agent: speckit.canon.vibecode-drift-reconcile
    prompt: Compare spec.drift.md against canon and generate canonization.md.
    send: true
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-drift-prerequisites.sh --json --require-tasks-drift
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-drift-prerequisites.ps1 -Json -RequireTasksDrift
---

## Pre-conditions (execute before any other step)

Before analyzing anything:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to all subsequent steps:
   - **Section 3 — Separation of Abstraction Levels**: spec.drift.md records WHAT diverged and WHY it matters for canon; never include implementation details beyond what is needed to identify the discrepancy
   - **Section 8 — No Hallucinated Requirements**: only report drift that is directly observable in the codebase; never infer or assume undocumented behavior
   - **Section 10 — Terminology**: use Canon terminology when describing discrepancies; flag terminology drift as its own category

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `TASKS_DRIFT`, and `SPEC_DRIFT`. All paths must be absolute.

Then check `SPEC_DRIFT`:

- If it exists, read it first and ask the operator whether to overwrite or abort.

---

## Step 1 — Load context

- **REQUIRED**: Read `TASKS_DRIFT` for the task inventory
- **REQUIRED**: Read `.specify/memory/constitution.md` for governing canon constraints and terminology rules
- **IF EXISTS**: Read `FEATURE_SPEC` for existing feature requirements (may not exist in vibecode workflow)
- **IF EXISTS**: Read `FEATURE_DIR/plan.md` for intended architecture and data model
- **IF EXISTS**: Read `FEATURE_DIR/data-model.md` for intended entity definitions

---

## Step 2 — Scan implementation through tasks

For each task in `tasks.drift.md`:

- Read the source files referenced in the task's changed files list
- Understand the actual implemented behavior
- Map the task's behavior to spec-level concerns (WHAT/WHY, not HOW)

---

## Step 3 — Detect spec drift

Identify spec-level findings from `tasks.drift.md` across five categories. If `spec.md` exists, compare against it; otherwise derive findings purely from observed implementation behavior.

**a. Undocumented features**: spec-level behavior present in code with no corresponding requirement in `spec.md` (or all behavior if spec.md does not exist)

**b. Behavioral deviations**: spec-level behavior implemented differently from what `spec.md` requires (only applicable if spec.md exists)

**c. New entities or fields**: data structures, models, or attributes in code not defined in `spec.md` or `data-model.md`

**d. Removed / skipped requirements**: requirements in `spec.md` with no corresponding implementation (only applicable if spec.md exists)

**e. Terminology drift**: concepts named differently in code vs `spec.md` (only applicable if spec.md exists)

**CRITICAL**: Only report spec items with actual drift or undocumented behavior. If a task has no spec-level impact (pure implementation detail), exclude it.

---

## Step 4 — Auto-classify all findings as ACCEPTED

This is a vibecode workflow — all discovered drift is treated as intentional implementation. Assign `ACCEPTED` to every D-XXX item. Do NOT use `REJECTED`, `IMPL-REJECTED`, or `SPEC-REJECTED`.

---

## Step 5 — Write `SPEC_DRIFT`

Load `.specify/extensions/canon/templates/spec-drift-template.md` and use it as the structural guide. Fill in findings from Steps 3–4, replacing placeholders with concrete data.

- Set `**Resolution Status**: resolved` in the header (vibecode skips the resolve step)
- Include a `## Resolution` section with a Resolution table mapping each D-XXX to its TD-XXX reference, all with status `ACCEPTED`
- Each finding **MUST** include a task drift reference (TD-XXX) linking back to the originating task drift item from `tasks.drift.md`

---

## Step 6 — Report

- Output path to `SPEC_DRIFT`, finding count per category
- If zero findings: "No spec-level drift detected — drift workflow complete."
- Otherwise: "All items auto-ACCEPTED — run /speckit.canon.vibecode-drift-reconcile to plan canon updates."

Do NOT modify canon files, tasks.drift.md, or any other file.

---

## Rules

- This is a single-pass, non-interactive workflow. Do NOT ask the operator for classification decisions.
- All findings are auto-ACCEPTED — this workflow assumes all implementation is intentional.
- Do NOT modify canon files, `TASKS_DRIFT`, or any other file. Only write `SPEC_DRIFT`.
- Only report spec items with actual drift — exclude pure implementation details.
- Every finding must trace back to a task drift item (TD-XXX) in tasks.drift.md.

