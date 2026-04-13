---
description: Pre-canon analysis for vibecoding drift — verify draft `canon.drift.md` against the full drift state and current canon before canonize, and emit concrete remediation items without modifying files.
handoffs: []
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-prerequisites.sh --json --require-tasks-drift --require-spec-drift --require-canon-drift --canon
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasksDrift -RequireSpecDrift -RequireCanonDrift -Canon
---

## Pre-conditions (execute before any other step)

Before producing any output:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to all subsequent steps:
   - **Section 1.2 — Rules for Canon**: do not compress, duplicate, or invent content; always reference canon sections by exact file path
   - **Section 3 — Separation of Abstraction Levels**: canon operates at WHAT level only
   - **Section 8 — No Hallucinated Requirements**: only report issues that are directly observable in the drift artifacts, implementation evidence, or current canon; never infer undocumented behavior
   - **Section 10 — Terminology**: use Canon terminology exactly and flag terminology drift as its own issue category

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Goal

Analyze draft `canon.drift.md` after `/speckit.canon.vibecode-drift-reconcile`
and before canonize. Review the entire vibecoding drift chain —
`tasks.drift.md`, `spec.drift.md`, draft `canon.drift.md`, current canon files,
and `CANON_TOC` — and identify every actionable issue in `canon.drift.md`
before canon is modified.

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured
analysis report with concrete remediation items, but do not apply edits
automatically and do not re-run the analysis in the same command.

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON
for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `TASKS_DRIFT`, `FEATURE_SPEC`,
`SPEC_DRIFT`, `CANON_DRIFT`, `CANON_ROOT`, and `CANON_TOC`. All paths must be
absolute.

Check `CANON_DRIFT`:

- If `Status` is `applied` → stop: _"`canon.drift.md` is already applied.
  `/speckit.canon.vibecode-drift-analyze` only analyzes draft canon plans
  before canonize. Re-run `/speckit.canon.vibecode-drift-reconcile` to
  generate a new draft plan if further analysis is needed."_
- If `Status` is not `draft` → stop: _"`canon.drift.md` must be in `draft`
  status before `/speckit.canon.vibecode-drift-analyze` can run."_

Check `SPEC_DRIFT`:

- If `Resolution Status` is not `resolved` → stop: _"`spec.drift.md` is not
  fully resolved. Run `/speckit.canon.vibecode-drift-detect` first."_

---

## Step 1 — Load context

- **REQUIRED**: Read `TASKS_DRIFT` for the implementation-task evidence and
  TD-XXX references behind the spec drift findings
- **REQUIRED**: Read `SPEC_DRIFT` for the resolved SD-XXX outcomes and the
  authoritative drift state used to justify canon updates
- **REQUIRED**: Read `CANON_DRIFT` for the draft canon plan, all CD-XXX
  entries, entry statuses, target files/sections, and proposed canon text
- **IF EXISTS**: Read `FEATURE_SPEC` (`spec.md`) only when needed to interpret
  a resolved drift decision or confirm the original feature boundary
- **REQUIRED**: Read `CANON_TOC` for canon structure and TOC coverage checks
- **REQUIRED**: Read every canon file targeted by an `ACCEPTED` entry in
  `CANON_DRIFT`
- **IF NEEDED**: Read adjacent or cross-referenced canon files in `CANON_ROOT`
  to verify cross-reference integrity, duplication risk, and contradiction risk

---

## Step 2 — Verify the canon plan

For each `ACCEPTED` entry in `CANON_DRIFT`, verify all of the following:

### A. Traceability and scope

- The CD-XXX entry traces to a valid resolved SD-XXX item
- The cited SD-XXX item traces to the relevant TD-XXX evidence
- The proposed canon change is still within the resolved drift scope and does
  not introduce unrelated canon edits

### B. Canon target correctness

- The target canon file and section are correct for the concept being updated
- The entry does not target a wrong or overly low-level section
- The entry does not duplicate existing canon already present at the correct
  abstraction level

### C. Content accuracy

- The proposed canon text accurately reflects the authoritative state from
  `SPEC_DRIFT` and supporting `TASKS_DRIFT`
- Field names, behaviors, entities, constraints, and terminology match the
  authoritative drift state
- The text is authoritative present-tense canon, not proposal language
- The text stays at the WHAT level and does not leak HOW-level implementation
  details

### D. Cross-reference and TOC integrity

- Required cross-references to related canon sections are present or explicitly
  noted
- `CANON_TOC` updates are included when new files or sections are introduced
- Related canon sections stay internally consistent with the proposed change

For each `REJECTED` entry in `CANON_DRIFT`, verify the rejection rationale
still holds given the final draft plan and current canon state.

---

## Step 3 — Constitution alignment

- Verify every proposed canon change complies with constitution principles
- Check that Canon terminology is used exactly
- Verify no HOW-level details leaked into `canon.drift.md`
- Verify no proposed canon text invents requirements not supported by resolved
  drift evidence

---

## Step 4 — Generate findings and remediation items

For every actionable issue found in Steps 2–3, generate a remediation item.
Include **all actionable issues**; do not stop at a top subset.

Classify each remediation item into one of:

- `CANON-TRACE`: incorrect or missing SD-XXX / TD-XXX / scope traceability in
  `canon.drift.md`
- `CANON-FIX`: proposed canon text or classification needs correction
- `CANON-GAP`: a required canon entry, cross-reference, TOC note, or
  supporting detail is missing from `canon.drift.md`
- `CANON-CONFLICT`: the proposed canon change conflicts with current canon and
  the conflict must be resolved in `canon.drift.md`

Each remediation item must specify:

- **ID**: CR-XXX (globally incrementing, zero-padded)
- **Category**: `CANON-TRACE` | `CANON-FIX` | `CANON-GAP` |
  `CANON-CONFLICT`
- **Severity**: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW`
- **Canon Drift Target**: exact location in `CANON_DRIFT` to change (header,
  Accepted Entries, Rejected Entries, or specific CD-XXX entry)
- **Canon Target**: exact canon file path and section heading affected, if
  applicable
- **Action**: add | modify | remove | reclassify
- **Description**: concise explanation of what is wrong and what
  `canon.drift.md` must say instead
- **Refs**: relevant CD-XXX, SD-XXX, and TD-XXX references

Issues that are informational only should not be included as remediation items.

---

## Step 5 — Produce analysis report

Output a Markdown report (no file writes) with the following structure:

### Drift Canon Analysis Report

**Branch**: `BRANCH`
**Canon Drift**: `CANON_DRIFT` (`Status`: `draft`)
**Canon files analyzed**: [list of files]

#### Verification Summary

| CD-XXX | Target | Status | Reviewed | Issues |
|--------|--------|--------|----------|--------|
| CD-001 | `CANON_ROOT/api.md § Endpoints` | `ACCEPTED` | Yes/No | [brief issue or "OK"] |

#### Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|

Severity levels:
- **CRITICAL**: wrong canon section, canon contradiction, missing required
  canon entry, constitution violation
- **HIGH**: incorrect proposed canon text, bad classification, missing required
  cross-reference or TOC change
- **MEDIUM**: minor content inaccuracy, terminology drift, incomplete notes
  needed for correct canonize
- **LOW**: wording cleanup that does not affect canon correctness

#### Remediation Items

If any remediation items were generated in Step 4, include this table:

| ID | Category | Severity | Canon Drift Target | Canon Target | Action | Refs | Description |
|----|----------|----------|--------------------|--------------|--------|------|-------------|
| CR-001 | `CANON-FIX` | HIGH | `CANON_DRIFT § Accepted Entries / CD-003` | `CANON_ROOT/api.md § Endpoints` | modify | CD-003, SD-004, TD-002 | Wrong field name in proposed canon text; update to authoritative name. |

If zero remediation items: _"Canon drift plan review found no actionable issues."_

#### Metrics

- Total canon entries: N (`ACCEPTED`: N, `REJECTED`: N)
- Entries checked OK: N
- Entries with issues: N
- Remediation items generated: N
- Constitution violations: N

---

## Step 6 — Next actions

- If zero remediation items: _"`canon.drift.md` can be canonized as-is."_
- If remediation items exist: recommend revising `canon.drift.md` according to
  the `Remediation Items` table before canonize, then re-running
  `/speckit.canon.vibecode-drift-analyze`, and then running
  `/speckit.canon.vibecode-drift-canonize` when the verification pass is clean.
- If this analysis was invoked from `/speckit.canon.vibecode-drift`, the
  orchestrator owns the next decision after this report. In manual mode it may
  ask whether to remediate, continue, or stop. In automatic mode it may apply
  the reported remediation items to `canon.drift.md` and re-run analyze once.

---

## Rules

- **NEVER modify files.** This command is always read-only.
- Include **all actionable issues** in the report. Do not limit remediation to
  a top subset.
- The `Remediation Items` table is the authoritative remediation output for
  both direct user review and orchestrator follow-up.
- This command analyzes the full vibecoding drift chain before canonize. It
  does **not** apply canon changes and does not by itself block later
  canonize.
