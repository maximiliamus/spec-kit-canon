---
description: Infer canon gaps for vibecoding workflows — compare the resolved `spec.drift.md` against canon and write a canon plan to `canon.drift.md`. Vibecoding variant — all entries auto-`ACCEPTED`.
handoffs:
  - label: Analyze Canon Plan
    agent: speckit.canon.vibecode-drift-analyze
    prompt: Analyze the draft `canon.drift.md` against the drift artifacts and current canon before canonize.
    send: true
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-prerequisites.sh --json --require-spec-drift --canon
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-prerequisites.ps1 -Json -RequireSpecDrift -Canon
---

## Pre-conditions (execute before any other step)

Before analyzing anything:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to all subsequent steps:
   - **Section 1.2 — Rules for Canon**: do not compress, duplicate, or invent content; always reference canon sections by exact file path
   - **Section 3 — Separation of Abstraction Levels**: `canon.drift.md` proposes WHAT-level canon changes only
   - **Section 8 — No Hallucinated Requirements**: only report gaps that are directly observable by comparing `spec.drift.md` against canon; never infer undocumented behavior
   - **Section 10 — Terminology**: use Canon terminology when describing canon gaps; flag terminology drift as its own canon entry

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `SPEC_DRIFT`, `CANON_DRIFT`, `CANON_ROOT`, and `CANON_TOC`. All paths must be absolute.

Check `Resolution Status` in `SPEC_DRIFT` header:

  - If not `resolved` → stop and report: "`spec.drift.md` is not fully resolved — run /speckit.canon.vibecode-drift-detect to generate a resolved `spec.drift.md`."

Then check `CANON_DRIFT`:

- If it exists, read it first and ask the user whether to overwrite or abort.

---

## Step 1 — Load context

- **REQUIRED**: Read `SPEC_DRIFT` for the accepted spec-level drift findings and Resolution table entries that define which behaviors canon must now reflect
- **REQUIRED**: Read `CANON_TOC` for the current canon structure and file organization so canon gaps are mapped to the correct canon files and sections
- **REQUIRED**: Read all canon files referenced by accepted spec drift items, or otherwise relevant to the affected feature area, for existing section structure, surrounding context, and overlap checks before proposing canon changes
- **IF EXISTS**: Read `FEATURE_DIR/vibecode.md` for the original vibecoding intent, goals, and session notes that help interpret the scope and purpose of accepted implementation behavior
- **IF EXISTS**: Read `FEATURE_DIR/plan.md` for intended architecture, constraints, or planned structure that may help choose the correct canon target section at the WHAT level
- **IF EXISTS**: Read `FEATURE_DIR/data-model.md` for entity definitions, fields, and relationships that help identify missing or outdated canon coverage
- **IF EXISTS**: Read `FEATURE_DIR/research.md` for confirmed decisions and rationale that help distinguish deliberate canon-worthy behavior from incidental implementation detail

---

## Step 2 — Identify canon gaps

Compare the `ACCEPTED` items in `SPEC_DRIFT` against the loaded canon files across these dimensions:

**a. Missing behavior**: requirements, behaviors, or acceptance criteria in `spec.drift.md` not covered by any canon section

**b. Outdated canon**: canon sections that contradict `spec.drift.md` (e.g., define fields, endpoints, or behaviors that have since been revised)

**c. Missing entities or fields**: data models, API response shapes, or state structures defined in `spec.drift.md` but absent from canon

**d. Terminology gaps**: terms used in `spec.drift.md` not defined or aligned in canon

**Classification guidance**:

- Canon operates at the WHAT level — behavior, contracts, data shapes, terminology. Do NOT add HOW (framework choices, internal patterns, file layouts).
- If a `spec.drift.md` item is already covered by existing canon at the right abstraction level, do NOT create a duplicate entry — skip it.
- If in doubt whether something belongs in canon, include it — it is safer.

---

## Step 3 — Determine canon changes

For each identified gap:

- Identify the target canon file and exact section (path and heading)
- Specify the change type: `add`, `modify`, or `remove`
- Write the proposed canon text at the correct abstraction level (WHAT, not HOW)
- If no existing canon section fits, propose a new section with a suggested heading

---

## Step 4 — Write `CANON_DRIFT`

Load `.specify/extensions/canon/templates/canon-drift-template.md` and use it as the structural guide. Fill in entries from Steps 2–3, replacing placeholders with concrete data. Set `**Status**` to `draft`. Set `**Drift source**` to `[SPEC_DRIFT]`.

**Every entry MUST have status `ACCEPTED`.** This is a vibecoding workflow — all discovered canon gaps are treated as intentional implementation that canon must reflect.

---

## Step 5 — Validate `canon.drift.md`

- Every canon-relevant `spec.drift.md` item should map to at least one canon entry
- All entries are `ACCEPTED`
- Proposed canon text is written in authoritative present-tense language
- No implementation details (file paths, framework names) in proposed canon text unless they are part of the canonical project structure
- Canon terminology is used exactly (constitution Section 10)

---

## Report

After completing all steps, output:

1. **Canon summary**: path to `CANON_DRIFT`, total entry count, list of target canon files with change types
2. **Next step**: "Review the canon plan, optionally run /speckit.canon.vibecode-drift-analyze for a read-only verification report and remediation items, then run /speckit.canon.vibecode-drift-canonize when you are ready to apply canon changes."

---

## Rules

- This is a single-pass, non-interactive workflow. Do NOT ask the user for classification decisions.
- All canon entries are `ACCEPTED` — this workflow assumes all spec items reflect intentional implementation.
- Do NOT modify any canon files. Only write to `CANON_DRIFT`.
- Ensure the output file follows the canon-drift-template format exactly.
