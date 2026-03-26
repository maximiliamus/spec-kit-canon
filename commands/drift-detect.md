---
description: Detect spec-level drift — scan tasks.drift.md and reverse-engineer spec discrepancies against spec.md, writing only drifted items to spec.drift.md.
handoffs:
  - label: Resolve Drift
    agent: speckit.canon.drift-resolve
    prompt: Resolve outstanding IMPL-REJECTED and SPEC-REJECTED items in spec.drift.md.
    send: false
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

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `TASKS`, `TASKS_DRIFT`, and `SPEC_DRIFT`. All paths must be absolute.

Then verify `SPEC_DRIFT` does NOT already exist. If it exists:

- Check `Resolution Status`:
  - If `classified` → stop and report: "spec.drift.md already exists with status `classified`. Run /speckit.canon.drift-resolve to resolve outstanding items, or delete spec.drift.md and re-run /speckit.canon.drift-detect to re-discover."
  - If `resolved` → stop and report: "spec.drift.md is already fully resolved. Run /speckit.canon.drift-reconcile to proceed."

---

## Step 1 — Load context

- **REQUIRED**: Read `TASKS_DRIFT` for the drifted task inventory
- **REQUIRED**: Read `FEATURE_SPEC` for authoritative feature requirements and expected behavior
- **REQUIRED**: Read `.specify/memory/constitution.md` for governing canon constraints and terminology rules
- **IF EXISTS**: Read `FEATURE_DIR/plan.md` for intended architecture and data model
- **IF EXISTS**: Read `TASKS` for original intended implementation scope (needed to understand context of drifted tasks)
- **IF EXISTS**: Read `FEATURE_DIR/data-model.md` for intended entity definitions
- **IF EXISTS**: Read `FEATURE_DIR/research.md` for confirmed decisions and rationale; use it to distinguish intentional design choices from genuine deviations when classifying drift items

---

## Step 2 — Scan implementation through drifted tasks

For each drifted task in `tasks.drift.md`:

- Read the source files referenced in the task's changed files list
- Understand the actual implemented behavior
- Map the task's behavior to spec-level concerns (WHAT/WHY, not HOW)

Focus on tasks with drift kinds:

- **ADDED tasks**: may introduce undocumented features or new entities not in spec.md
- **UPDATED tasks**: may cause behavioral deviations, new entities, or terminology drift
- **CANCELED tasks**: may result in removed/skipped requirements from spec.md

---

## Step 3 — Detect spec drift

Compare the behavior revealed by `tasks.drift.md` against `spec.md` across five categories:

**a. Undocumented features**: spec-level behavior present in code (from ADDED tasks) with no corresponding requirement in `spec.md`

**b. Behavioral deviations**: spec-level behavior implemented differently from what `spec.md` requires (from UPDATED tasks)

**c. New entities or fields**: data structures, models, or attributes in code not defined in `spec.md` or `data-model.md` (from ADDED or UPDATED tasks)

**d. Removed / skipped requirements**: requirements in `spec.md` with no corresponding implementation (from CANCELED tasks, or spec requirements whose implementing task was CANCELED)

**e. Terminology drift**: concepts named differently in code vs `spec.md` (from UPDATED tasks where naming diverges)

**CRITICAL**: Only report spec items that are drifted. Do NOT include spec items where the implementation matches the spec exactly. If a drifted task has no spec-level impact (pure implementation detail), exclude it.

---

## Step 4 — Classify each finding

For each D-XXX item found, assign exactly one status before writing spec.drift.md:

| Status                             | Assignment                                                                                                                                                                                   |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ACCEPTED`                         | **Agent assigns automatically**: as-built behavior is correct and intentional — net-new valid behavior with no spec conflict, or deviation explicitly justified by plan.md/spec.md rationale |
| `REJECTED`                         | **Agent assigns automatically**: pure implementation detail below canon abstraction level; predates this feature; explicitly out-of-scope                                                    |
| `IMPL-REJECTED` or `SPEC-REJECTED` | **Ask the operator** — when spec and implementation differ and neither plan.md nor spec.md provides clear justification                                                                      |

**Classification rules**:

- `REJECTED` is for things invisible at the spec/canon abstraction level (internal helpers, compat shims, implementation patterns). If in doubt between `REJECTED` and asking the operator, ask the operator — it is safer.
- When spec and implementation diverge without documented justification: present the discrepancy and ask the operator: _"D-XXX ([title]): spec says [X], implementation does [Y]. Which should be authoritative? **I** = implementation must be fixed (IMPL-REJECTED) / **S** = spec must be corrected (SPEC-REJECTED)"_ — accept `i`/`I` or `s`/`S`.
- **Process each ambiguous item one at a time. Never ask about multiple items at once.**
- Do NOT assign `ACCEPTED` to a behavioral deviation that directly contradicts a spec acceptance criterion unless plan.md or spec.md provides documented rationale.

---

## Step 5 — Write `SPEC_DRIFT`

Load `.specify/extensions/canon/templates/spec-drift-template.md` and use it as the structural guide. Fill in findings from Steps 3–4, replacing placeholders with concrete data. Set `**Resolution Status**: classified` in the header. Do NOT include a `## Resolution` section — that is added by /speckit.canon.drift-resolve.

Each finding **MUST** include a task drift reference (TD-XXX) linking back to the originating task drift item from `tasks.drift.md`.

---

## Step 6 — Report

- Output path to `SPEC_DRIFT`, finding count per category, and count per status
- If zero findings: "No spec-level drift detected from task drift — run /speckit.canon.drift-resolve to finalize resolution status, then /speckit.canon.drift-reconcile to plan canon updates"
- If IMPL-REJECTED or SPEC-REJECTED items exist: "Run /speckit.canon.drift-resolve to resolve outstanding items, then run /speckit.canon.drift-reconcile"
- If all items are ACCEPTED or REJECTED: "All items classified with no conflicts — run /speckit.canon.drift-resolve to finalize, then run /speckit.canon.drift-reconcile"

Do NOT modify spec.md, canon files, tasks.md, tasks.drift.md, or any other file.

---

## Rules

- This is a single-pass workflow. Do NOT resolve items — only discover and classify.
- Do NOT modify `FEATURE_SPEC`, canon files, `TASKS`, `TASKS_DRIFT`, or any other file. Only write `SPEC_DRIFT`.
- Do NOT include a `## Resolution` section in the output.
- Only report spec items with actual drift — exclude items where implementation matches spec.
- Every finding must trace back to a task drift item (TD-XXX) in tasks.drift.md.

