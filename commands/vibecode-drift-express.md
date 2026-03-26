---
description: Express drift-to-canon pipeline — runs the entire vibecode drift workflow (reverse → detect → reconcile → canonize) in a single invocation. Use for fast, low-ceremony canon updates.
handoffs:
  - label: Verify Canon
    agent: speckit.canon.drift-analyze
    prompt: Verify the applied canonization entries against canon files and produce repair candidates if needed.
    send: true
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-drift-prerequisites.sh --json --canon
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-drift-prerequisites.ps1 -Json -Canon
agent_scripts:
  sh: bash .specify/extensions/canon/scripts/bash/update-agent-context.sh
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/update-agent-context.ps1
---

## Pre-conditions (execute before any other step)

Before analyzing anything:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to **all** subsequent phases:
   - **Section 1.2 — Rules for Canon**: do not compress, duplicate, or invent content; always reference canon sections by exact file path
   - **Section 3 — Separation of Abstraction Levels**: tasks.drift.md records HOW-level groupings; spec.drift.md records WHAT-level drift; canon operates at WHAT level only
   - **Section 8 — No Hallucinated Requirements**: only report drift that is directly observable in the codebase; never infer or assume undocumented behavior
   - **Section 9 — Definition of Done**: canonize only when all prior phases have completed
   - **Section 10 — Terminology**: use Canon terminology exactly; no synonyms

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `TASKS_DRIFT`, `SPEC_DRIFT`, `CANONIZATION`, `CANON_ROOT`, and `CANON_TOC`. All paths must be absolute.

Check for existing drift artifacts in `FEATURE_DIR`:

- If `TASKS_DRIFT`, `SPEC_DRIFT`, or `CANONIZATION` exist, list which ones are present and ask the operator: _"Existing drift artifacts found: [list]. Express mode will overwrite them. Proceed? (yes / no)"_
  - **no** → stop

---

## Phase 1 — Reverse-engineer tasks

### 1.1 Collect changes

- Run `git diff main...HEAD --name-status` to identify all files added, modified, or deleted on this branch
- Run `git log main..HEAD --oneline` to understand the commit history
- If there are uncommitted worktree changes, also run `git diff --name-status` and `git diff --cached --name-status`
- Combine all sources into a single deduplicated file list

### 1.2 Read and understand each changed file

- Read every changed file (or the relevant changed portions for large files)
- For deleted files, note the deletion and check git history for what was removed
- Understand the purpose and behavior of each change

### 1.3 Group into logical tasks

- Cluster related file changes into coherent implementation tasks
- Each task should represent a single logical unit of work
- A file may appear in more than one task if it contains changes for multiple logical purposes
- Order tasks by logical dependency (foundational changes first)

### 1.4 Write `TASKS_DRIFT`

Load `.specify/extensions/canon/templates/tasks-drift-template.md` and use it as the structural guide. All tasks are classified as `ADDED` (vibecode — no original tasks.md). Set `**Resolution Status**: classified`.

### 1.5 Early exit check

If zero tasks were identified: stop and report _"No implementation changes detected on this branch. Canon is up to date."_

---

## Phase 2 — Detect spec drift

### 2.1 Scan implementation through tasks

For each task in the just-written `TASKS_DRIFT`:

- Use the source files already read in Phase 1 (no redundant reads)
- Map each task's behavior to spec-level concerns (WHAT/WHY, not HOW)

### 2.2 Detect spec drift

Identify spec-level findings across five categories. If `spec.md` exists, compare against it; otherwise derive findings purely from observed implementation behavior.

**a.** Undocumented features
**b.** Behavioral deviations (only if spec.md exists)
**c.** New entities or fields
**d.** Removed / skipped requirements (only if spec.md exists)
**e.** Terminology drift (only if spec.md exists)

**CRITICAL**: Only report spec items with actual drift or undocumented behavior. Exclude pure implementation details.

### 2.3 Auto-classify all findings as ACCEPTED

All discovered drift is treated as intentional implementation.

### 2.4 Write `SPEC_DRIFT`

Load `.specify/extensions/canon/templates/spec-drift-template.md` and use it as the structural guide. Set `**Resolution Status**: resolved`. Include a `## Resolution` section with all items `ACCEPTED`. Each finding **MUST** trace back to a TD-XXX reference.

### 2.5 Early exit check

If zero spec-level findings: stop and report _"No spec-level drift detected — all implementation changes are below canon abstraction level. Canon is up to date."_

---

## Phase 3 — Reconcile against canon

### 3.1 Load canon context

Read `CANON_TOC` and all canon files relevant to the spec drift findings. Use `FEATURE_SPEC` (spec.md) if it exists.

### 3.2 Identify canon gaps

Compare ACCEPTED items in `SPEC_DRIFT` against canon across:

**a.** Missing behavior — requirements not covered by any canon section
**b.** Outdated canon — sections contradicting spec.drift.md
**c.** Missing entities or fields — data models absent from canon
**d.** Terminology gaps — terms not defined or aligned in canon

Classification guidance:
- Canon operates at the WHAT level only. Do NOT add HOW details.
- If an item is already covered by canon at the right abstraction level, skip it.

### 3.3 Determine canon changes

For each gap: identify target canon file and section, change type (add / modify / remove), and write proposed canon text.

### 3.4 Write `CANONIZATION`

Load `.specify/extensions/canon/templates/canonization-template.md` and use it as the structural guide. Set `**Status**: draft`. All entries have `**Status**: ACCEPTED`.

### 3.5 Early exit check

If zero canon gaps: stop and report _"All drift is already reflected in canon. No canon changes needed."_

---

## Phase 4 — Apply canon changes

### 4.1 Confirmation gate

Display a summary of all changes that will be applied:

- Total tasks reverse-engineered (Phase 1)
- Total spec drift findings (Phase 2)
- Each canon change entry with its target file, section, and change type

Ask: _"Express pipeline complete. [N] canon changes will be applied to [M] files. Proceed? (yes / no)"_
  - **no** → stop; artifacts are preserved but canon is NOT modified. Report: _"Artifacts written (tasks.drift.md, spec.drift.md, canonization.md) but canon not updated. You can review the artifacts and run /speckit.canon.vibecode-drift-canonize to apply later."_

### 4.2 Apply changes

For each `ACCEPTED` entry in `CANONIZATION`:

- Apply the specified change to the target canon file
- Write in authoritative present-tense language only
- Preserve existing structure; avoid duplication; remove proposal language
- Use Canon terminology exactly (constitution Section 10)

### 4.3 Update TOC

If new sections or files were added to canon, update `CANON_TOC`.

### 4.4 Add traceability comments

In each updated canon section, append: `<!-- Canonicalized from specs/<BRANCH>/spec.drift.md -->`

### 4.5 Mark `CANONIZATION` as applied

Update the top-level `Status` field in `CANONIZATION` to `applied`.

### 4.6 Update agent context

Run `{AGENT_SCRIPT} codex` to refresh context after canon updates.

---

## Report

Output a combined report:

```
Express Pipeline Summary
========================
Phase 1 — Reverse:    [N] tasks identified
Phase 2 — Detect:     [N] spec drift findings (all ACCEPTED)
Phase 3 — Reconcile:  [N] canon change entries
Phase 4 — Canonize:   [N] canon files modified

Artifacts written:
  - TASKS_DRIFT
  - SPEC_DRIFT
  - CANONIZATION

Canon updated successfully.
```

Then: _"Run /speckit.canon.drift-analyze to verify canon consistency."_

---

## Rules

- This is a single-invocation pipeline. The only operator interaction is the overwrite prompt (if artifacts exist) and the final confirmation gate before canon apply.
- All findings are auto-ACCEPTED at every phase — this workflow assumes all implementation is intentional.
- All intermediate artifacts are written to disk for traceability. No artifacts are skipped.
- Constitution pre-conditions are loaded once and applied throughout all phases.
- Reuse in-memory context across phases — do not redundantly re-read files already loaded in a prior phase.
- Do NOT modify any source files, spec.md, or tasks.md. Only write drift artifacts and canon files.
- This command does NOT replace the individual step-by-step commands. Users who need granular control or want to inspect/edit intermediate artifacts should use the individual commands.

