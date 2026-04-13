---
description: Apply a draft `canon.drift.md` plan to canon files — reads `ACCEPTED` entries from the draft canon plan and modifies the configured canon root.
handoffs: []
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-prerequisites.sh --json --require-canon-drift --canon
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-prerequisites.ps1 -Json -RequireCanonDrift -Canon
agent_scripts:
  sh: bash .specify/extensions/canon/scripts/bash/update-agent-context.sh __AGENT__
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__
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

- **REQUIRED**: Read `CANON_DRIFT` for the canon change plan, entry statuses, target files, and exact canon edits proposed for application
- **REQUIRED**: Check the top-level `Status` field in `CANON_DRIFT`
  - If `applied` → stop and report: "`canon.drift.md` is already marked as `applied`. Delete it and re-run `/speckit.canon.drift-reconcile` to re-infer, or check canon files for the applied changes."
  - If not `draft` → stop and report: "`canon.drift.md` must be in `draft` status before `/speckit.canon.drift-canonize` can run."
- **REQUIRED**: Read `SPEC_DRIFT` for the resolved spec-level drift outcomes that justify each canon change
- **IF EXISTS**: Read `FEATURE_SPEC` for the original feature baseline used only as background context when interpreting the canon changes
- **REQUIRED**: Read `CANON_TOC` for canon structure and entry points used to locate the target canon sections
- **REQUIRED**: Read all canon files targeted by `ACCEPTED` entries in `CANON_DRIFT` for the current wording and structure that will be updated

---

## Step 2 — Gate check

Scan all entries in `CANON_DRIFT`. If any entry has a status other than `ACCEPTED` or `REJECTED`, stop and report: "canon.drift.md contains `unresolved` entries — edit the file to assign valid statuses (`ACCEPTED` or `REJECTED`) before proceeding."

---

## Step 3 — Build apply summary

Before modifying canon, compile the apply set for this run:

- List each `ACCEPTED` entry with its target canon file, section, and change type (add / modify / remove)
- List `REJECTED` entries that will be skipped
- Treat every `ACCEPTED` entry as already approved for application; do **not** ask for a final confirmation prompt

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

## Step 7 — Mark canon.drift.md as `applied`

Update the top-level `Status` field in `CANON_DRIFT` to `applied`.

---

## Step 8 — Update agent context

Run `{AGENT_SCRIPT}` to refresh the current agent-specific context after canon updates.

---

## Step 9 — Report

- List all modified canon files with a summary of changes per section
- List all `REJECTED` items that were skipped
- "Canon updated successfully."
- "If you later revise `canon.drift.md`, consider running /speckit.canon.drift-analyze again before canonizing the new draft."

---

## Canon Rules

- Do NOT compress canon into a single file.
- Do NOT copy the entire incremental spec into canon.
- Do NOT invent content not in `CANON_DRIFT`, `SPEC_DRIFT`, or directly observable in the implementation.
- Canon must read as authoritative present-tense truth.
- Use Canon terminology exactly; avoid synonyms.
- Only modify `CANON_ROOT/**` and `CANON_TOC`. Do not modify `FEATURE_SPEC`.
- This command applies only — no inference or classification is performed.
- Do not add a separate final confirmation gate; `ACCEPTED` entries are the confirmed outcomes to apply.
