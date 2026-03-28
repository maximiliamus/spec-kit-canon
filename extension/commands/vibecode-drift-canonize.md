---
description: Apply a fully-ACCEPTED canon plan to canon files — vibecode shortcut that skips inference (canon.drift.md must already exist with all entries ACCEPTED).
handoffs:
  - label: Analyze Canon
    agent: speckit.canon.drift-analyze
    prompt: Verify the applied canon entries against canon files and produce repair candidates if needed.
    send: true
  - label: Repair Canon
    agent: speckit.canon.drift-repair
    prompt: Read the analyze report and apply corrections to canon files.
    send: false
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
   - **Section 9 — Definition of Done**: canonize only when spec, plan, tasks, and drift are complete or when the canon plan was already prepared in phase 1
   - **Section 10 — Terminology**: all canon edits must use Canon terminology exactly; no synonyms

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `SPEC_DRIFT`, `CANON_DRIFT`, `CANON_ROOT`, and `CANON_TOC`. All paths must be absolute.

---

## Step 1 — Load context

- Read `CANON_DRIFT`
- Check top-level `Status` field:
  - If `applied` → stop and report: "canon.drift.md is already marked as applied. Delete it and re-run /speckit.canon.vibecode-drift-reconcile to re-generate, or check canon files for the applied changes."
- Read `SPEC_DRIFT`, `CANON_TOC`, and all canon files targeted by ACCEPTED entries

---

## Step 2 — Gate check

Scan all entries in canon.drift.md. Every entry **MUST** have status `ACCEPTED`. If any entry has a status other than `ACCEPTED`, stop and report: "canon.drift.md contains non-ACCEPTED entries — this vibecode workflow expects all entries to be ACCEPTED. Edit the file or re-run /speckit.canon.vibecode-drift-reconcile."

---

## Step 3 — Final confirmation

Display a summary of all changes that will be applied:

- List each `ACCEPTED` entry with its target canon file, section, and change type (add / modify / remove)
- Ask: _"[N] canon changes will be applied to [files]. Proceed? (yes / no)"_
  - **no** → stop; no files are modified

---

## Step 4 — Apply canon changes

For each `ACCEPTED` entry:

- Apply the specified change to the target canon file
- Write in authoritative present-tense language only
- Preserve existing structure; avoid duplication; remove proposal language
- Use Canon terminology exactly (constitution §10)

---

## Step 5 — Update TOC

If new sections or files were added to canon, update `CANON_TOC` accordingly.

---

## Step 6 — Add traceability comments

In each updated canon section, append: `<!-- Canonicalized from specs/<BRANCH>/spec.drift.md -->`

---

## Step 7 — Mark canon.drift.md as applied

Update the top-level `Status` field in `CANON_DRIFT` to `applied`.

---

## Step 8 — Update agent context

Run `{AGENT_SCRIPT} codex` to refresh context after canon updates.

---

## Step 9 — Report

- List all modified canon files with a summary of changes per section
- "Canon updated successfully."
- "Run /speckit.canon.drift-analyze to verify canon consistency. If issues are found, run /speckit.canon.drift-repair to apply corrections."

---

## Canon Rules

- Do NOT compress canon into a single file.
- Do NOT copy the entire incremental spec into canon.
- Do NOT invent content not in `SPEC_DRIFT` or directly observable in the implementation.
- Canon must read as authoritative present-tense truth.
- Use Canon terminology exactly; avoid synonyms.
- Only modify `CANON_ROOT/**` and `CANON_TOC`. Do not modify `SPEC_DRIFT`.
- This is the apply-only vibecode workflow. All entries must be ACCEPTED — no inference or classification is performed.

