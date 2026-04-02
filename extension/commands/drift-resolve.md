---
description: Resolve outstanding `UNRESOLVED` and `IMPL-REJECTED` drift items in `spec.drift.md` in manual review mode, including re-verification after deferred alignment work, so canon updates can proceed.
handoffs:
  - label: Plan Canonization
    agent: speckit.canon.drift-reconcile
    prompt: Infer canon gaps from the resolved `spec.drift.md` once alignment work is complete.
    send: false
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-prerequisites.sh --json --require-spec-drift
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-prerequisites.ps1 -Json -RequireSpecDrift
---

## Pre-conditions (execute before any other step)

Before making any changes:

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

Treat non-empty input only as operator context for this manual resolve pass.
It may clarify intent for the current work, but it must NOT switch this command
into an automatic mode or suppress required item-level prompts.

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `TASKS`, `TASKS_ALIGNMENT`, and `SPEC_DRIFT`. All paths must be absolute.

Check `Resolution Status`:

- If `resolved` → stop and report: "`spec.drift.md` is already fully resolved. Run /speckit.canon.drift-reconcile to proceed."
- If `unresolved` → continue.
- If `TASKS_ALIGNMENT` exists and any unchecked TA-XXX tasks remain, treat the alignment queue as still active regardless of the top-level file `Status` (`pending`, `in-progress`, or stale `implemented`); carry those unchecked tasks into Step 4 as deferred alignment context, do NOT re-prompt already deferred linked items, and include the remaining unchecked TA-XXX tasks in the final partial report.

---

## Step 1 — Load context

- **REQUIRED**: Read `SPEC_DRIFT` for the authoritative list of SD-XXX items, current statuses, evidence, and file-order traversal
- **REQUIRED**: Read `FEATURE_SPEC` for the original feature baseline used to decide whether the spec or implementation should be authoritative
- **REQUIRED**: Read `FEATURE_DIR/plan.md` for intended architecture and design context used when evaluating whether a deviation looks intentional
- **IF EXISTS**: Read `TASKS_ALIGNMENT` for deferred alignment context and linked TA-XXX tasks for pending implementation follow-up

---

## Step 2 — Check for outstanding items

If no `UNRESOLVED` or `IMPL-REJECTED` items exist → skip to Step 5.

---

## Step 3 — Resolve outstanding drift items in file order

Traverse `SPEC_DRIFT` top to bottom and process each existing
`UNRESOLVED` or `IMPL-REJECTED` item in the order it appears in the file.
Resolve the current item before moving to the next one.

Rules for the traversal:

- Never batch items.
- Never regroup items by status.
- For each item, follow the matching resolution rule in Step 4.

---

## Step 4 — Apply the matching rule for the current item

If the current item is `UNRESOLVED`:

- Re-read the relevant section of `FEATURE_SPEC`
- Re-read the source file(s) cited in the drift item
- Present the discrepancy and ask the user: _"SD-XXX ([title]): spec says [X], implementation does [Y]. Which should be authoritative? **I** = treat the implemented behavior as authoritative / **S** = treat the spec expectation as authoritative"_ — accept `i`/`I` or `s`/`S`
  - **I** → update the drift item status in `SPEC_DRIFT` to `IMPL-ACCEPTED`; keep the observed implementation behavior as the authoritative truth for downstream reconcile; continue to next item
  - **S** → continue with the spec-authoritative handling flow below for this same item

If either of the following is true:

- the current item is `IMPL-REJECTED`
- the user just chose **S** for an `UNRESOLVED` item

Then continue with the spec-authoritative handling flow:

- Re-read the source file(s) cited in the drift item
- If `TASKS_ALIGNMENT` exists, use any linked TA-XXX tasks as supporting context, but do NOT trust alignment status labels by themselves without verifying the code
- **If the fix is observable in code** (implementation now matches the spec requirement): automatically mark `SPEC-ACCEPTED`; report what was detected; continue to next item
- **If the fix is NOT observable and the current item is already `IMPL-REJECTED` with linked unchecked TA-XXX tasks**: leave the item as `IMPL-REJECTED`; do NOT ask `F/T` again; continue to next item and include the remaining unchecked TA-XXX tasks in the final partial report
- **If the fix is NOT observable and there are no linked unchecked TA-XXX tasks**: present the discrepancy and ask the user: _"SD-XXX ([title]) — [spec requirement] is not met. **F** = fix it now (agent edits code) / **T** = create task for later implementation"_ — accept `f`/`F` or `t`/`T`
  - **F** → apply the minimal correct fix to the implementation file(s); add an inline comment at the change site: `// Fixed: SD-XXX — see [SPEC_DRIFT]`; update the drift item status in `SPEC_DRIFT` to `SPEC-ACCEPTED`; continue to next item
  - **T** → create or update `TASKS_ALIGNMENT` using `.specify/extensions/canon/templates/tasks-alignment-template.md`; if a task group for the current SD-XXX item already exists, update that group with the remaining implementation work; otherwise add a new TA-XXX task group linked to the current SD-XXX item; then set that task group's `Status` to `pending` if none of its TA-XXX tasks are checked yet, otherwise `in-progress`; set top-level `Status` to `pending` if no TA-XXX tasks in the file are checked yet, otherwise `in-progress`; leave item status as `IMPL-REJECTED` in `SPEC_DRIFT`; continue to next item

Never stop the traversal on an `IMPL-REJECTED` item when the answer is **T**.
Create or update alignment work, then continue to the next item in file order.

---

## Step 5 — Gate check

- If any item still has status `UNRESOLVED` or `IMPL-REJECTED` → `spec.drift.md` stays `unresolved`; do NOT append a Resolution section; do NOT mark as `resolved`. Proceed to Step 7 (partial report).
- If all items are resolved (no `UNRESOLVED` or `IMPL-REJECTED` remain) → proceed to Step 6.

---

## Step 6 — Update `spec.drift.md`

Append a `## Resolution` section to `SPEC_DRIFT` using the Resolution table format from `.specify/extensions/canon/templates/spec-drift-template.md`. Update `Resolution Status` in the header to `resolved`.

---

## Step 7 — Report

- Count per terminal status (`ACCEPTED`, `REJECTED`, `SPEC-ACCEPTED`, `IMPL-ACCEPTED`)
- List of any implementation files edited (with SD-XXX references)
- List of any drift items accepted as authoritative implementation truth (with SD-XXX references)
- **If fully resolved**: "All items resolved — run `/speckit.canon.drift-reconcile` to plan canon updates"
- **If partially resolved** (alignment tasks were created or remain active for `IMPL-REJECTED` items): list each remaining `IMPL-REJECTED` item with its unchecked TA-XXX tasks; if an item has no linked unchecked tasks, say that it still needs an `F/T` choice on the next resolve pass; then: "Tasks added to or remaining in `tasks.alignment.md`. In the step-by-step workflow, run /speckit.canon.drift-implement, then run `/speckit.canon.drift-resolve` again to re-verify and finish resolution. If you started from `/speckit.canon.drift`, the orchestrator will run that alignment cycle next."

---

## Rules

- This command is manual-only. Do NOT treat user input as an automatic-mode switch.
- This command resolves items only — it does NOT re-discover.
- Do NOT add new SD-XXX items. Only process existing `UNRESOLVED` and `IMPL-REJECTED` items.
- Do NOT modify canon files, `FEATURE_SPEC`, or `TASKS`.
- You may edit implementation files (for `IMPL-REJECTED` fixes) and may create or update `TASKS_ALIGNMENT` (for deferred alignment work).
- Only modify `SPEC_DRIFT`, implementation files (`IMPL-REJECTED` fixes only), and `TASKS_ALIGNMENT` (deferred alignment work only).
