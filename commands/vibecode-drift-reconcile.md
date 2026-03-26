---
description: Infer canon gaps — compare the resolved spec.drift.md against canon and write a canonization plan to canonization.md. Vibecode variant — all entries auto-ACCEPTED.
handoffs:
  - label: Apply Canonization
    agent: speckit.canon.vibecode-drift-canonize
    prompt: Apply the canonization plan to canon files.
    send: true
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-drift-prerequisites.sh --json --require-spec-drift --canon
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-drift-prerequisites.ps1 -Json -RequireSpecDrift -Canon
---

## Pre-conditions (execute before any other step)

Before analyzing anything:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to all subsequent steps:
   - **Section 1.2 — Rules for Canon**: do not compress, duplicate, or invent content; always reference canon sections by exact file path
   - **Section 3 — Separation of Abstraction Levels**: canonization.md proposes WHAT-level canon changes only
   - **Section 8 — No Hallucinated Requirements**: only report gaps that are directly observable by comparing spec.drift.md against canon; never infer undocumented behavior
   - **Section 10 — Terminology**: use Canon terminology when describing canon gaps; flag terminology drift as its own canonization entry

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `SPEC_DRIFT`, `CANONIZATION`, `CANON_ROOT`, and `CANON_TOC`. All paths must be absolute.

Check `Resolution Status` in `SPEC_DRIFT` header:

  - If not `resolved` → stop and report: "spec.drift.md is not fully resolved — run /speckit.canon.vibecode-drift-detect to generate a resolved spec.drift.md."

Then check `CANONIZATION`:

- If it exists, read it first and ask the operator whether to overwrite or abort.

---

## Step 1 — Load context

- Read `SPEC_DRIFT` — use the Resolution table to understand which behaviors are accepted as truth
- Read `FEATURE_SPEC` (spec.md) if it exists
- Read `CANON_TOC` and all canon files referenced by spec items or relevant to the feature area

---

## Step 2 — Identify canon gaps

Compare the ACCEPTED items in `SPEC_DRIFT` against the loaded canon files across these dimensions:

**a. Missing behavior**: requirements, behaviors, or acceptance criteria in spec.drift.md not covered by any canon section

**b. Outdated canon**: canon sections that contradict spec.drift.md (e.g., define fields, endpoints, or behaviors that have since been revised)

**c. Missing entities or fields**: data models, API response shapes, or state structures defined in spec.drift.md but absent from canon

**d. Terminology gaps**: terms used in spec.drift.md not defined or aligned in canon

**Classification guidance**:

- Canon operates at the WHAT level — behavior, contracts, data shapes, terminology. Do NOT add HOW (framework choices, internal patterns, file layouts).
- If a spec.drift.md item is already covered by existing canon at the right abstraction level, do NOT create a duplicate entry — skip it.
- If in doubt whether something belongs in canon, include it — it is safer.

---

## Step 3 — Determine canon changes

For each identified gap:

- Identify the target canon file and exact section (path and heading)
- Specify the change type: `add`, `modify`, or `remove`
- Write the proposed canon text at the correct abstraction level (WHAT, not HOW)
- If no existing canon section fits, propose a new section with a suggested heading

---

## Step 4 — Write `CANONIZATION`

Load `.specify/extensions/canon/templates/canonization-template.md` and use it as the structural guide. Fill in entries from Steps 2–3, replacing placeholders with concrete data. Set `**Status**: draft`. Set `**Drift source**` to `[SPEC_DRIFT]`.

**All entries MUST have `**Status**: ACCEPTED`**. This is a vibecoding workflow — all discovered canon gaps are treated as intentional implementation that canon must reflect.

---

## Step 5 — Validate canonization.md

- Every canon-relevant spec.drift.md item should map to at least one canonization entry
- All entries are ACCEPTED
- Proposed canon text is written in authoritative present-tense language
- No implementation details (file paths, framework names) in proposed canon text unless they are part of the canonical project structure
- Canon terminology is used exactly (constitution Section 10)

---

## Report

After completing all steps, output:

1. **Canonization summary**: path to `CANONIZATION`, total entry count, list of target canon files with change types
2. **Next step**: "Review the canonization plan, then run /speckit.canon.vibecode-drift-canonize to apply canon changes."

---

## Rules

- This is a single-pass, non-interactive workflow. Do NOT ask the operator for classification decisions.
- All canonization entries are ACCEPTED — this workflow assumes all spec items reflect intentional implementation.
- Do NOT modify any canon files. Only write to `CANONIZATION`.
- Ensure the output file follows the canonization-template format exactly.

