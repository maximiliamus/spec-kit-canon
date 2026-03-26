---
description: Post-canonization analysis — verify that canon changes were applied correctly, check for contradictions and missing cross-references, and produce structured repair candidates for /speckit.canon.drift-repair.
handoffs:
  - label: Repair Canon
    agent: speckit.canon.drift-repair
    prompt: Read the repair candidates from the analysis and apply corrections to canon files.
    send: true
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-drift-prerequisites.sh --json --require-canonization --canon
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-drift-prerequisites.ps1 -Json -RequireCanonization -Canon
---

## Pre-conditions (execute before any other step)

Before producing any output:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to all subsequent steps:
   - **Section 1.2 — Rules for Canon**: do not compress, duplicate, or invent content; always reference canon sections by exact file path
   - **Section 3 — Separation of Abstraction Levels**: canon operates at WHAT level only
   - **Section 8 — No Hallucinated Requirements**: only report issues that are directly observable; never infer undocumented behavior
   - **Section 10 — Terminology**: use Canon terminology when describing issues; flag terminology drift as its own category

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Goal

Verify the integrity of canon after `/speckit.canon.drift-canonize` (or `/speckit.canon.vibecode-drift-canonize`) has applied changes. Produce a structured analysis report with actionable repair candidates that can be consumed by `/speckit.canon.drift-repair`.

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured analysis report only.

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `SPEC_DRIFT`, `CANONIZATION`, `CANON_ROOT`, and `CANON_TOC`. All paths must be absolute.

Check `CANONIZATION`:

- If `Status` is not `applied` → stop: _"canonization.md has not been applied. Run /speckit.canon.drift-canonize first, then re-run /speckit.canon.drift-analyze."_

---

## Step 1 — Load context

- Read `CANONIZATION` — the applied canonization plan with all entries
- Read `SPEC_DRIFT` — resolved spec drift items with task drift references
- Read `FEATURE_SPEC` (spec.md) if it exists
- Read `CANON_TOC` and all canon files targeted by ACCEPTED canonization entries
- Read any additional canon files in `CANON_ROOT` that are adjacent to or cross-referenced by modified sections
- Read `.specify/memory/constitution.md` for principle validation

---

## Step 2 — Canonization Verification

For each ACCEPTED entry in `CANONIZATION`:

### A. Application verification

- Verify the proposed canon text was actually applied to the target canon file and section
- Check for partial application (text was added but incomplete or truncated)
- Check for incorrect placement (text applied to wrong section or file)

### B. Content accuracy

- Verify the applied canon text accurately reflects the spec.drift.md source
- Check for field name mismatches, incorrect terminology, or distorted phrasing
- Verify authoritative present-tense language (no proposal language remaining)

### C. Cross-reference integrity

- Check for missing cross-references between newly canonized sections and pre-existing canon
- Verify that related canon sections (e.g., data model references from API sections) are consistent
- Check that `CANON_TOC` was updated if new sections or files were added

### D. Contradiction detection

- Check for contradictions between newly applied canon sections and pre-existing canon from other features
- Check for contradictions between updated canon and the current `spec.md`
- Flag any canon sections where the same concept is now defined differently in two places

### E. REJECTED entry review

- For each REJECTED entry in `CANONIZATION`: verify the rejection rationale still holds given the final canon state
- Flag any REJECTED entries that may need revisiting (e.g., if a related ACCEPTED entry introduced a dependency on the rejected content)

---

## Step 3 — Constitution Alignment

- Verify all applied canon changes comply with constitution principles
- Check that Canon terminology is used exactly (constitution Section 10)
- Verify no HOW-level details leaked into canon (constitution Section 3)

---

## Step 4 — Generate Repair Candidates

For every actionable issue found in Steps 2–3, generate a structured repair candidate entry. Classify each into one of:

- `CANON-FIX`: Canon text needs correction — wrong content was applied, field name mismatch, incorrect phrasing
- `CANON-GAP`: Missing cross-reference or section that should have been added during canonization
- `CANON-CONFLICT`: Contradiction between a newly canonized section and a pre-existing canon section

Issues that are informational only (e.g., style suggestions, minor wording preferences) should NOT be included as repair candidates.

Each repair candidate must specify:

- **ID**: R-XXX (globally incrementing)
- **Category**: CANON-FIX | CANON-GAP | CANON-CONFLICT
- **Canon Target**: exact file path and section heading (e.g., `CANON_ROOT/api.md § Endpoints`)
- **Action**: add | modify | remove
- **Description**: concise explanation of what is wrong and what the correction should be
- **Canonization ref**: C-XXX from canonization.md (if traceable to a specific entry)

---

## Step 5 — Produce Analysis Report

Output a Markdown report (no file writes) with the following structure:

### Drift Canonization Analysis Report

**Branch**: `BRANCH`
**Canonization**: `CANONIZATION` (Status: applied)
**Canon files analyzed**: [list of files]

#### Verification Summary

| C-XXX | Target | Status | Verified | Issues |
|-------|--------|--------|----------|--------|
| C-001 | CANON_ROOT/api.md § Endpoints | ACCEPTED | Yes/No | [brief issue or "OK"] |

#### Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|

Severity levels:
- **CRITICAL**: Canon contradiction, missing required section, constitution violation
- **HIGH**: Incorrect content applied, missing cross-reference affecting other features
- **MEDIUM**: Minor content inaccuracy, missing optional cross-reference
- **LOW**: Style/wording that doesn't affect correctness

#### Repair Candidates

If any repair candidates were generated in Step 4, include this table:

| ID  | Category       | Canon Target                         | Action | Canonization Ref | Description                         |
|-----|---------------|--------------------------------------|--------|------------------|-------------------------------------|
| R-1 | CANON-FIX     | CANON_ROOT/api.md § Endpoints   | modify | C-003            | Wrong field name; should be ...     |
| R-2 | CANON-GAP     | CANON_ROOT/data.md § Models     | add    | —                | Missing cross-ref to new entity ... |

If zero repair candidates: _"Canonization verified — no repairs needed."_

#### Metrics

- Total canonization entries: N (ACCEPTED: N, REJECTED: N)
- Entries verified OK: N
- Entries with issues: N
- Repair candidates generated: N
- Constitution violations: N

---

## Step 6 — Next Actions

- If zero repair candidates: _"Canon is consistent. No further action needed."_
- If repair candidates exist: _"Run /speckit.canon.drift-repair with the above candidates to apply corrections."_
- If CRITICAL issues: _"CRITICAL issues found — resolve before proceeding with further development."_

---

## Rules

- **STRICTLY READ-ONLY** — do NOT modify any files
- This command analyzes canon state AFTER canonization. It does NOT re-run drift detection or reconciliation.
- Only report issues that are directly observable by comparing `CANONIZATION` entries against actual canon file contents.
- Do NOT propose new canon content beyond what was in the original canonization plan or spec.drift.md.
- This command works for both the full pipeline and the vibecode pipeline — it operates post-canonization regardless of which pipeline produced the canonization.

