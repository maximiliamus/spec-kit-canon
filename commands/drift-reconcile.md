---
description: Infer canon gaps — compare the resolved spec.drift.md against canon and write a canonization plan to canonization.md.
handoffs:
  - label: Apply Canonization
    agent: speckit.canon.drift-canonize
    prompt: Apply the ACCEPTED canonization entries to canon files.
    send: false
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-drift-prerequisites.sh --json --require-spec-drift --canon
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-drift-prerequisites.ps1 -Json -RequireSpecDrift -Canon
---

## Pre-conditions (execute before any other step)

Before making any changes to canon:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to all subsequent steps:
   - **Section 1.2 — Rules for Canon**: do not compress, duplicate, or invent content; always reference canon sections by exact file path
   - **Section 9 — Definition of Done**: canonize only when spec, plan, tasks, and drift are complete or when canonization already prepared on phase 1
   - **Section 10 — Terminology**: all canon edits must use Canon terminology exactly; no synonyms

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `SPEC_DRIFT`, `CANONIZATION`, `CANON_ROOT`, and `CANON_TOC`. All paths must be absolute.
- Check `Resolution Status` in spec.drift.md header:
  - If not `resolved` → stop and report: "spec.drift.md is not fully resolved — run /speckit.canon.drift-resolve to complete resolution before reconciling."
- `CANONIZATION` must NOT exist — if it exists:
  - Check top-level `Status`:
    - If `draft` → stop and report: "canonization.md already exists. Review it and run /speckit.canon.drift-canonize to apply, or delete it and re-run /speckit.canon.drift-reconcile."
    - If `applied` → stop and report: "canonization.md is already applied. Delete it and re-run /speckit.canon.drift-reconcile to re-infer."

---

## Step 1 — Load context

- Read `SPEC_DRIFT` — use the Resolution table to understand which behaviors are accepted as truth
- Read `FEATURE_SPEC` (spec.md) — the updated spec after drift resolution
- Read `CANON_TOC` and all canon files referenced by `FEATURE_SPEC`

---

## Step 2 — Identify canon gaps

Compare the resolved `SPEC_DRIFT` and updated `FEATURE_SPEC` against the loaded canon files across these dimensions:

**a. Missing behavior**: requirements, behaviors, or acceptance criteria reflected in the resolved drift items not covered by any canon section

**b. Outdated canon**: canon sections that contradict the resolved drift state (e.g., define fields, endpoints, or behaviors that have since been revised per drift resolution)

**c. Missing entities or fields**: data models, API response shapes, or state structures introduced or changed per the drift resolution but absent from canon

**d. Terminology gaps**: terms established or changed by the drift resolution not defined or aligned in canon

Use the spec.drift.md Resolution table to calibrate:

- Items with terminal status `ACCEPTED`, `SPEC-ACCEPTED`, or `IMPL-ACCEPTED` represent the authoritative state — use them as signals when spec and canon diverge
- Items with status `REJECTED` require no canon change; skip them

---

## Step 3 — Classify each gap

For every identified gap, assign exactly one status:

| Status     | When to assign                                                                                                         |
| ---------- | ---------------------------------------------------------------------------------------------------------------------- |
| `ACCEPTED` | spec.drift.md describes behavior that is absent from or outdated in canon; canon must be updated to reflect it         |
| `REJECTED` | Gap is below the canon abstraction level (implementation detail, internal helper, compat shim); no canon change needed |

**Classification guidance**:

- Canon operates at the WHAT level — behavior, contracts, data shapes, terminology. Do NOT add HOW (framework choices, internal patterns, file layouts).
- If a requirement is already covered by existing canon at the right abstraction level, do NOT create a duplicate entry — classify as `REJECTED`.
- If in doubt between `ACCEPTED` and `REJECTED`, prefer `ACCEPTED` — it is safer.

---

## Step 4 — For each ACCEPTED gap, determine the canon change

- Identify the target canon file and exact section (path and heading)
- Specify the change type: `add`, `modify`, or `remove`
- Write the proposed canon text at the correct abstraction level (WHAT, not HOW)
- If no existing canon section fits, propose a new section with a suggested heading

---

## Step 5 — Write `CANONIZATION`

Load `.specify/extensions/canon/templates/canonization-template.md` and use it as the structural guide. Fill in entries from Steps 2–4, replacing placeholders with concrete data. Set `**Status**: draft`. Set `**Drift source**` to `[SPEC_DRIFT]`.

---

## Step 6 — Report

Output:

- Count of items per status (ACCEPTED, REJECTED)
- Any classification decisions that required significant judgment (flag for operator review)
- Instruction: "Review `CANONIZATION`, edit any misclassifications or proposed text, then run /speckit.canon.drift-canonize to apply."

Do NOT modify any canon file or spec.md.

---

## Rules

- This command infers canon gaps only — it does NOT modify canon files.
- Do NOT modify any canon file, spec.md, spec.drift.md, or tasks.drift.md.
- Only write `CANONIZATION`.
- Do NOT compress canon into a single file.
- Do NOT copy the entire incremental spec into canon.
- Do NOT invent content not in `FEATURE_SPEC`, `SPEC_DRIFT`, or directly observable in the implementation.

