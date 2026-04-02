---
description: Detect spec-level drift for vibecoding workflows — scan `tasks.drift.md`, derive WHAT-level behavior from the implementation, and write accepted findings to `spec.drift.md`.
handoffs:
  - label: Plan Canonization
    agent: speckit.canon.vibecode-drift-reconcile
    prompt: Compare `spec.drift.md` against canon and generate `canon.drift.md`.
    send: true
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-prerequisites.sh --json --require-tasks-drift
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasksDrift
---

## Pre-conditions (execute before any other step)

Before analyzing anything:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to all subsequent steps:
   - **Section 3 — Separation of Abstraction Levels**: `spec.drift.md` records WHAT diverged and WHY it matters for canon; never include implementation details beyond what is needed to identify the discrepancy
   - **Section 8 — No Hallucinated Requirements**: only report drift that is directly observable in the codebase; never infer or assume undocumented behavior
   - **Section 10 — Terminology**: use Canon terminology when describing discrepancies; flag terminology drift as its own category

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `TASKS_DRIFT`, and `SPEC_DRIFT`. All paths must be absolute.

Then check `SPEC_DRIFT`:

- If it exists, read it first and ask the user whether to overwrite or abort.

---

## Step 1 — Load context

- **REQUIRED**: Read `TASKS_DRIFT` for the drifted task inventory and TD-XXX source references for every spec finding derived from the implementation
- **IF EXISTS**: Read `FEATURE_DIR/vibecode.md` for the original vibecoding intent, goals, and session notes that help interpret implemented behavior at the WHAT level
- **IF EXISTS**: Read `FEATURE_DIR/plan.md` for intended architecture, constraints, or planned structure that help explain why the implementation behaves the way it does
- **IF EXISTS**: Read `FEATURE_DIR/data-model.md` for entity definitions and field expectations used when identifying new entities, attributes, or relationships
- **IF EXISTS**: Read `FEATURE_DIR/research.md` for confirmed decisions and rationale that help distinguish deliberate behavior from incidental implementation detail

---

## Step 2 — Scan implementation through tasks

For each task in `tasks.drift.md`:

- Read the source files referenced in the task's changed files list
- Understand the actual implemented behavior
- Map the task's behavior to spec-level concerns (WHAT/WHY, not HOW)

---

## Step 3 — Detect spec drift

Identify spec-level findings from `tasks.drift.md` across five categories. Derive them directly from observed implementation behavior.

**a. New or undocumented behaviors**: spec-level behavior that now exists in the implementation and should be captured as authoritative WHAT-level behavior

**b. Behavior changes or workflow shifts**: changes in user-visible flow, validation, state transitions, outputs, or interaction patterns that materially affect expected behavior

**c. New entities or fields**: data structures, domain concepts, models, attributes, or relationships introduced by the implementation

**d. Removed or replaced behavior**: prior or implied behavior that the changed implementation has dropped, superseded, or made unreachable

**e. Terminology drift**: names and concepts used in the implementation that canon will need to standardize

**CRITICAL**: Only report spec items with actual drift or undocumented behavior. If a task has no spec-level impact (pure implementation detail), exclude it.

---

## Step 4 — Auto-classify All Findings as `ACCEPTED`

This is a vibecoding workflow — all discovered drift is treated as intentional implementation. Assign `ACCEPTED` to every SD-XXX item. Do NOT use `REJECTED`, `UNRESOLVED`, or `IMPL-REJECTED`.

---

## Step 5 — Write `SPEC_DRIFT`

Load `.specify/extensions/canon/templates/spec-drift-template.md` and use it as the structural guide. Fill in findings from Steps 3–4, replacing placeholders with concrete data.

- Set `**Spec Source**: -` in the header because vibecoding does not produce `spec.md`
- Set `**Resolution Status**` to `resolved` in the header (vibecoding skips the resolve step)
- Include a `## Resolution` section with a Resolution table mapping each SD-XXX to its TD-XXX reference, all with status `ACCEPTED`
- Each finding **MUST** include a task drift reference (TD-XXX) linking back to the originating task drift item from `tasks.drift.md`
- When template fields mention `Spec Reference` or `Spec Expectation`, use `-` or explicitly note that vibecoding has no prior spec artifact and the finding was derived from implementation evidence alone

---

## Step 6 — Report

- Output path to `SPEC_DRIFT`, finding count per category
- If zero findings: "No spec-level drift detected — drift workflow complete."
- Otherwise: "All items auto-`ACCEPTED` — run /speckit.canon.vibecode-drift-reconcile to plan canon updates."

Do NOT modify canon files, `tasks.drift.md`, or any other file.

---

## Rules

- This is a single-pass, non-interactive workflow. Do NOT ask the user for classification decisions.
- All findings are auto-`ACCEPTED` — this workflow assumes all implementation is intentional.
- Do NOT modify canon files, `TASKS_DRIFT`, or any other file. Only write `SPEC_DRIFT`.
- Only report spec items with actual drift — exclude pure implementation details.
- Every finding must trace back to a task drift item (TD-XXX) in `tasks.drift.md`.
