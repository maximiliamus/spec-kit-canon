---
description: Repair canon after post-canon analysis — reads analyze findings, generates correction entries, and applies fixes to canon files. Closes the feedback loop between canonize and analyze.
handoffs:
  - label: Verify Repairs
    agent: speckit.canon.drift-analyze
    prompt: Verify the repaired canon for contradictions and missing links. This is a post-repair verification — check that all repair corrections were applied correctly.
    send: true
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-drift-prerequisites.sh --json --require-canon-drift --canon
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-drift-prerequisites.ps1 -Json -RequireCanonDrift -Canon
agent_scripts:
  sh: bash .specify/extensions/canon/scripts/bash/update-agent-context.sh
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/update-agent-context.ps1
---

## Pre-conditions (execute before any other step)

Before making any changes to canon:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to all subsequent steps:
   - **Section 1.2 — Rules for Canon**: do not compress, duplicate, or invent content; always reference canon sections by exact file path
   - **Section 3 — Separation of Abstraction Levels**: repairs operate at WHAT level only
   - **Section 8 — No Hallucinated Requirements**: only repair issues that are directly observable; never infer undocumented behavior
   - **Section 10 — Terminology**: all canon edits must use Canon terminology exactly; no synonyms

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user input should contain or reference the analyze report with Repair Candidates. If the user provides repair candidates inline, use those directly.

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `SPEC_DRIFT`, `CANON_DRIFT`, `CANON_REPAIR`, `CANON_ROOT`, and `CANON_TOC`. All paths must be absolute.

---

## Step 1 — Load context

- Read `CANON_DRIFT` — confirm `Status` is `applied` (repair only runs after canonize)
  - If `Status` is not `applied` → stop: _"canon.drift.md has not been applied yet. Run /speckit.canon.drift-canonize (or /speckit.canon.vibecode-drift-canonize) first."_
- Read `SPEC_DRIFT` for drift context
- Read `CANON_TOC` and all canon files targeted by the applied canon entries
- Check if `CANON_REPAIR` already exists:
  - If it exists with `Status: applied` → stop: _"A repair has already been applied. Run /speckit.canon.drift-analyze to verify, or delete canon.repair.md to re-run repair."_
  - If it exists with `Status: draft` → ask operator whether to overwrite or abort

---

## Step 2 — Parse repair candidates

Extract repair candidates from the user input or analyze report. Each candidate must have:

- **ID**: R-XXX identifier
- **Category**: `CANON-FIX`, `CANON-GAP`, or `CANON-CONFLICT`
- **Canon Target**: file path and section
- **Action**: add, modify, or remove
- **Description**: what needs to be corrected

If no repair candidates are provided or parseable, re-read the canon files modified by canon apply and independently verify against `spec.drift.md`:

- Check that each ACCEPTED canon entry was correctly applied
- Check for contradictions between newly applied sections and pre-existing canon
- Check for missing cross-references
- Generate repair candidates from any issues found

If zero issues found after independent verification: stop and report _"No repair needed — canon is consistent."_

---

## Step 3 — Generate correction entries

For each repair candidate:

- **CANON-FIX** (wrong content applied):
  - Read the target canon section
  - Read the original spec.drift.md item and canon entry
  - Generate a `modify` entry with the corrected text

- **CANON-GAP** (missing cross-reference or section):
  - Identify what is missing and where it should go
  - Generate an `add` entry with the new content

- **CANON-CONFLICT** (contradiction with existing canon):
  - Read both the new section and the conflicting existing section
  - Determine which is authoritative (spec.drift.md is the source of truth for the feature; pre-existing canon is authoritative for other features)
  - Generate a `modify` entry resolving the contradiction

---

## Step 4 — Write `CANON_REPAIR`

Load `.specify/extensions/canon/templates/canon-repair-template.md` and use it as the structural guide. Fill in entries from Step 3.

- Use CR-XXX IDs (Canon Repair) to distinguish from original C-XXX entries
- Set `**Status**: draft`
- Set `**Source**: Post-canon analysis repair`
- Each entry references the original R-XXX repair candidate and, where applicable, the original C-XXX canon entry

---

## Step 5 — Confirmation gate

Display a summary of all corrections:

- List each CR-XXX entry with its target canon file, section, change type, and brief description
- Reference the original R-XXX repair candidate for each
- Ask: _"[N] canon corrections will be applied to [M] files. Proceed? (yes / no)"_
  - **no** → stop; `CANON_REPAIR` is preserved as draft for manual review

---

## Step 6 — Apply corrections

For each entry in `CANON_REPAIR`:

- Apply the specified change to the target canon file
- Write in authoritative present-tense language only
- Preserve existing structure; avoid duplication; remove proposal language
- Use Canon terminology exactly (constitution Section 10)

---

## Step 7 — Update TOC

If new sections or files were added to canon, update `CANON_TOC`.

---

## Step 8 — Add traceability comments

In each corrected canon section, append: `<!-- Repaired from specs/<BRANCH>/canon.repair.md -->`

---

## Step 9 — Mark `CANON_REPAIR` as applied

Update the top-level `Status` field to `applied`.

---

## Step 10 — Update agent context

Run `{AGENT_SCRIPT} codex` to refresh context after canon updates.

---

## Step 11 — Report

- List all corrected canon files with a summary of changes per section
- Reference original R-XXX and CR-XXX IDs
- _"Canon repairs applied successfully. Run /speckit.canon.drift-analyze to verify."_

---

## Loop Termination Guidance

The expected feedback loop is: `canonize → drift.analyze → repair → drift.analyze → done`.

- If `/speckit.canon.drift-analyze` finds no issues after repair → the loop is complete
- If `/speckit.canon.drift-analyze` still finds issues after repair → the operator should either:
  - Run `/speckit.canon.drift-repair` again (maximum 2 automated repair iterations recommended)
  - Manually edit canon files if the issues are complex or require human judgment
- After 2 repair iterations, if issues persist, report: _"Two repair iterations completed but drift.analyze still reports issues. Manual review recommended — the remaining issues may require human judgment to resolve."_

---

## Rules

- This command only corrects canon files. It does NOT re-run drift detection or reconciliation.
- Do NOT modify `spec.drift.md`, `tasks.drift.md`, `canon.drift.md`, `spec.md`, or any implementation files.
- Only write `CANON_REPAIR` and modify `CANON_ROOT/**` and `CANON_TOC`.
- This command works for both the full pipeline and the vibecode pipeline — it operates after canon apply regardless of which pipeline produced the canon plan.
- If the operator provides repair candidates inline (rather than from an analyze report), use them directly without requiring a formal report format.

