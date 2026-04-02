---
description: Express drift-to-canon pipeline — runs the small-change vibecoding drift workflow in one invocation, skipping the separate draft canon analysis pass and canonizing directly after confirmation.
handoffs: []
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/check-prerequisites.sh --json --canon
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/check-prerequisites.ps1 -Json -Canon
agent_scripts:
  sh: bash .specify/extensions/canon/scripts/bash/update-agent-context.sh __AGENT__
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__
---

## Pre-conditions (execute before any other step)

Before proceeding:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to **all** subsequent phases:
   - **Section 1.2 — Rules for Canon**: do not compress, duplicate, or invent content; always reference canon sections by exact file path
   - **Section 3 — Separation of Abstraction Levels**: `tasks.drift.md` records HOW-level groupings, `spec.drift.md` records WHAT-level drift, and canon stays at the WHAT level only
   - **Section 8 — No Hallucinated Requirements**: only report drift directly observable in the codebase; never invent undocumented behavior
   - **Section 9 — Definition of Done**: do not canonize until prior phases complete; express mode assumes the reconciled draft canon plan is small and straightforward enough to canonize without a separate analyze pass
   - **Section 10 — Terminology**: use Canon terminology exactly; no synonyms

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Setup

**Before doing anything else**, run `{SCRIPT}` from repo root and parse JSON for `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `TASKS_DRIFT`, `SPEC_DRIFT`, `CANON_DRIFT`, `CANON_ROOT`, `CANON_TOC`, and `BASE_BRANCH`. All path values must be absolute.

Check for existing drift artifacts in `FEATURE_DIR`:

- If `TASKS_DRIFT`, `SPEC_DRIFT`, or `CANON_DRIFT` exist, stop and report: _"Existing drift artifacts found: [list]. `/speckit.canon.vibecode-drift-express` does not overwrite existing drift artifacts. Review or delete them before re-running express mode."_

---

## Phase 1 — Reverse-engineer tasks

### 1.1 Collect changes

- Run `git diff <BASE_BRANCH>...HEAD --name-status`
- Run `git log <BASE_BRANCH>..HEAD --oneline`
- If there are uncommitted worktree changes, also run `git diff --name-status` and `git diff --cached --name-status`
- Combine all sources into a single deduplicated file list

### 1.2 Read and understand each changed file

- Read every changed file or the relevant changed portions
- For deleted files, note the deletion and inspect git history as needed
- Understand the purpose and behavior of each change

### 1.3 Group into logical tasks

- Cluster related file changes into coherent implementation tasks
- Order tasks by logical dependency

### 1.4 Write `TASKS_DRIFT`

Load `.specify/extensions/canon/templates/tasks-drift-template.md` and use it as the structural guide. All tasks are classified as `ADDED`. Set `**Resolution Status**` to `classified`.

### 1.5 Early exit check

If zero tasks were identified: stop and report _"No implementation changes detected on this branch. Canon is up to date."_

---

## Phase 2 — Detect spec drift

### 2.1 Scan implementation through tasks

For each task in `TASKS_DRIFT`, use the already-read source files and map the behavior to WHAT-level concerns only.

### 2.2 Detect spec drift

Identify only canon-relevant findings across:

- new or undocumented behaviors
- behavior changes or workflow shifts
- new entities or fields
- removed or replaced behavior
- terminology drift

### 2.3 Auto-classify all findings as `ACCEPTED`

All discovered drift is treated as intentional implementation truth.

### 2.4 Write `SPEC_DRIFT`

Load `.specify/extensions/canon/templates/spec-drift-template.md` and use it as the structural guide. Set `**Spec Source**: -`. Set `**Resolution Status**` to `resolved`. Include a `## Resolution` section with all items `ACCEPTED`. Each finding **MUST** trace back to a TD-XXX reference.

### 2.5 Early exit check

If zero spec-level findings: stop and report _"No spec-level drift detected — all implementation changes are below canon abstraction level. Canon is up to date."_

---

## Phase 3 — Reconcile against canon

### 3.1 Load canon context

Read `CANON_TOC` and all canon files relevant to the accepted spec drift findings.

### 3.2 Identify canon gaps

Compare `ACCEPTED` items in `SPEC_DRIFT` against canon for:

- missing behavior
- outdated canon
- missing entities or fields
- terminology gaps

Keep the canon at the WHAT level only.

### 3.3 Determine canon changes

For each gap, identify target canon file and section, change type, and proposed canon text.

### 3.4 Write `CANON_DRIFT`

Load `.specify/extensions/canon/templates/canon-drift-template.md` and use it as the structural guide. Set `**Status**` to `draft`. Set every generated entry to `ACCEPTED`.

### 3.5 Early exit check

If zero canon gaps: stop and report _"All drift is already reflected in canon. No canon changes needed."_

---

## Phase 4 — Canonize

### 4.1 Final confirmation gate

Display a summary of all changes that will be applied:

- total tasks reverse-engineered
- total spec drift findings
- each canon change entry with its target file, section, and change type

Ask: _"Express pipeline complete. [N] canon changes will be applied to [M] files. Proceed? (yes / no)"_
  - **no** → stop; artifacts are preserved but canon is NOT modified

### 4.2 Apply changes

For each `ACCEPTED` entry in `CANON_DRIFT`:

- apply the specified change to the target canon file
- write in authoritative present-tense language only
- preserve structure and avoid duplication
- use Canon terminology exactly

### 4.3 Update TOC

If new sections or files were added to canon, update `CANON_TOC`.

### 4.4 Add traceability comments

In each updated canon section, append: `<!-- Canonicalized from specs/<BRANCH>/spec.drift.md -->`

### 4.5 Mark `CANON_DRIFT` as `applied`

Update the top-level `Status` field in `CANON_DRIFT` to `applied`.

### 4.6 Update agent context

Run `{AGENT_SCRIPT}` to refresh the current agent-specific context after canon updates.

---

## Report

Output a combined report:

```text
Express Pipeline Summary
========================
Phase 1 — Reverse:    [N] tasks identified
Phase 2 — Detect:     [N] spec drift findings (all ACCEPTED)
Phase 3 — Reconcile:  [N] canon change entries
Phase 4 — Canonize:   [N] canon files modified

Artifacts written:
  - TASKS_DRIFT
  - SPEC_DRIFT
  - CANON_DRIFT

Canon updated successfully.
```

---

## Rules

- This is a single-invocation pipeline. User interaction is limited to the final canonize confirmation.
- Express mode intentionally skips the separate draft canon analysis/remediation loop and canonizes within this command. Use `/speckit.canon.vibecode-drift` or the manual analyze command when you want a read-only review and remediation items for `canon.drift.md` before canonize.
- All drift findings are auto-`ACCEPTED`; this workflow assumes implementation is intentional.
- All intermediate artifacts are written to disk for traceability.
- Only drift artifacts and canon files may be written by this command.
