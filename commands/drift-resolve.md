---
description: Resolve outstanding IMPL-REJECTED and SPEC-REJECTED drift items in spec.drift.md — finalize so canon updates can proceed.
handoffs:
  - label: Plan Canonization
    agent: speckit.canon.drift-reconcile
    prompt: Infer canon gaps from the resolved spec.drift.md and spec.md.
    send: false
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-drift-prerequisites.sh --json --require-spec-drift
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-drift-prerequisites.ps1 -Json -RequireSpecDrift
---

## Pre-conditions (execute before any other step)

Before making any changes:

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

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `TASKS`, and `SPEC_DRIFT`. All paths must be absolute.

Check `Resolution Status`:

- If `resolved` → stop and report: "spec.drift.md is already fully resolved. Run /speckit.canon.drift-reconcile to proceed."

---

## Step 1 — Load context

- Read `SPEC_DRIFT`
- Read `FEATURE_SPEC`
- Read `FEATURE_DIR/plan.md`

---

## Step 2 — Check for outstanding items

If no `SPEC-REJECTED` or `IMPL-REJECTED` items exist → skip to Step 5.

---

## Step 3 — Resolve SPEC-REJECTED items — one by one

For each `SPEC-REJECTED` item, process individually (never batch):

- Re-read the relevant section of `FEATURE_SPEC`
- Display the proposed spec.md correction (show exact before/after text)
- Ask the operator: _"D-XXX ([title]): classified SPEC-REJECTED — spec.md will be updated to match the implementation. Approve? (yes / no)"_
  - **yes** → apply the change to `FEATURE_SPEC`; add an inline annotation at the exact point of change:
    `<!-- Updated: D-XXX — impl-accepted; see [SPEC_DRIFT] -->`
    then mark the item `IMPL-ACCEPTED` in the Resolution table
  - **no** → stop; operator must manually resolve (reclassify the item or fix spec.md) before proceeding

Stop entirely if any SPEC-REJECTED item is declined. Do not proceed to the next item or step.

---

## Step 4 — Resolve IMPL-REJECTED items — one by one

For each `IMPL-REJECTED` item, process individually (never batch):

- Re-read the source file(s) cited in the drift item
- **If the fix is observable in code** (implementation now matches the spec requirement): automatically mark `SPEC-ACCEPTED`; report what was detected; continue to next item
- **If the fix is NOT observable**: present the discrepancy and ask the operator: _"D-XXX ([title]) — [spec requirement] is not met. **F** = fix it now (agent edits code) / **T** = create task for later implementation"_ — accept `f`/`F` or `t`/`T`
  - **F** → apply the minimal correct fix to the implementation file(s); add an inline comment at the change site: `// Fixed: D-XXX — see [SPEC_DRIFT]`; mark item `SPEC-ACCEPTED` in the Resolution table; continue to next item
  - **T** → append a structured task to `TASKS` with the drift item ID and spec requirement as rationale; leave item status as `IMPL-REJECTED` in `SPEC_DRIFT`; continue to next item

Process all `IMPL-REJECTED` items before moving to Step 5. Never stop mid-loop on a **T** answer.

---

## Step 5 — Gate check

- If any item still has status `IMPL-REJECTED` or `SPEC-REJECTED` → spec.drift.md stays `classified`; do NOT append a Resolution section; do NOT mark as `resolved`. Proceed to Step 7 (partial report).
- If all items are resolved (no `IMPL-REJECTED` or `SPEC-REJECTED` remain) → proceed to Step 6.

---

## Step 6 — Update spec.drift.md

Append a `## Resolution` section to `SPEC_DRIFT` using the Resolution table format from `.specify/extensions/canon/templates/spec-drift-template.md`. Update `Resolution Status` in the header to `resolved`.

---

## Step 7 — Report

- Count per terminal status (ACCEPTED, REJECTED, SPEC-ACCEPTED, IMPL-ACCEPTED)
- List of any implementation files edited (with D-XXX references)
- List of any spec.md sections updated (with D-XXX references)
- **If fully resolved**: "All items resolved — run /speckit.canon.drift-reconcile to plan canon updates"
- **If partially resolved** (tasks created for remaining IMPL-REJECTED items): list each pending item with its task description, then: "Tasks added to tasks.md. Run /speckit.implement to complete them, then run /speckit.canon.drift-resolve again to auto-resolve remaining items."

---

## Rules

- This command resolves items only — it does NOT re-discover or re-classify drift.
- Do NOT add new D-XXX items. Only process existing IMPL-REJECTED and SPEC-REJECTED items.
- Do NOT modify canon files. Only modify `SPEC_DRIFT`, `FEATURE_SPEC` (for SPEC-REJECTED resolutions), implementation files (for IMPL-REJECTED fixes), and `TASKS` (for deferred tasks).

