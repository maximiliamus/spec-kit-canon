---
description: Start a vibecoding session — create a feature branch with minimal ceremony. Accepts a slug, descriptive text, or nothing at all.
handoffs:
  - label: Drift Express
    agent: speckit.canon.vibecode-drift-express
    prompt: Run the express drift-to-canon pipeline for this branch.
    send: false
  - label: Reverse Tasks
    agent: speckit.canon.vibecode-drift-reverse
    prompt: Reverse-engineer tasks from implementation.
    send: false
scripts:
  sh: bash .specify/extensions/canon/scripts/bash/create-new-feature.sh
  ps: pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/create-new-feature.ps1
---

## Pre-conditions (execute before any other step)

Before doing anything:

1. Read `.specify/memory/constitution.md` in full.
2. Apply the following from the constitution to all subsequent steps:
   - **Section 6 — Git Branching Strategy**: the branch prefix follows the project's Spec Kit numbering mode (`###-` by default or `YYYYMMDD-HHMMSS-` in timestamp mode); the suffix for this vibecoding workflow is the slug
   - **Section 3 — Separation of Abstraction Levels**: `vibecode.md` captures intent at WHAT level — no implementation details beyond what the user provided

## User Input

```text
$ARGUMENTS
```

---

## Step 1 — Classify input

Examine `$ARGUMENTS` and classify into exactly one category:

### A. Empty (no arguments)

- Slug = `vibecode`
- Intent = none (session started for ad-hoc work)

### B. Single identifier string

A single token or hyphenated identifier with **no spaces** (e.g., `webui-improve`, `backend-polish-service`, `fix-auth`).

- Slug = the identifier as-is (cleaned via the script's `clean_branch_name`)
- Intent = none (slug is self-descriptive enough)

### C. Descriptive text

Anything that contains spaces or reads as natural language (e.g., `"Add retry logic to the signal processor"`, `"Polish the channel management UI and fix sidebar bugs"`).

- Slug = derived from the text (2-4 meaningful words, same logic as `/speckit.specify`)
- Intent = the full text (will be recorded in vibecode.md)

---

## Step 2 — Create feature branch

Run the create-new-feature helper to create the branch and feature directory. Use the slug from Step 1 as `--short-name`. Pass the slug itself as the feature description argument (the script requires a non-empty description).

**Branch numbering mode**: Before running the script, check if `.specify/init-options.json` exists and read the `branch_numbering` value.

- If `"timestamp"`, add `--timestamp` (Bash) or `-Timestamp` (PowerShell) to the script invocation
- If `"sequential"` or absent, do not add any extra flag (default behavior)

Examples:

- Bash example: `{SCRIPT} --json --short-name "api-cleanup" "api-cleanup"`
- Bash (timestamp): `{SCRIPT} --json --timestamp --short-name "api-cleanup" "api-cleanup"`
- PowerShell example: `{SCRIPT} -Json -ShortName "api-cleanup" "api-cleanup"`
- PowerShell (timestamp): `{SCRIPT} -Json -Timestamp -ShortName "api-cleanup" "api-cleanup"`

**IMPORTANT**:

- Do NOT pass `--number` — the script determines the correct next number automatically
- Always include `--json` so the output can be parsed reliably
- Parse JSON output for `BRANCH_NAME`, `SPEC_FILE`, `FEATURE_NUM`
- Derive `FEATURE_DIR` from `SPEC_FILE` (its parent directory)

---

## Step 3 — Write vibecode.md

Create `FEATURE_DIR/vibecode.md` with the following content:

### If category A or B (no intent text):

```markdown
# Vibecode: <BRANCH_NAME>

**Branch**: `<BRANCH_NAME>`
**Created**: <DATE>
**Workflow**: vibecoding (code-first)

## Intent

Ad-hoc vibecoding session. No specific requirements captured at start.

## Notes

_Record observations, decisions, or scope changes here during the session._
```

### If category C (descriptive text):

```markdown
# Vibecode: <BRANCH_NAME>

**Branch**: `<BRANCH_NAME>`
**Created**: <DATE>
**Workflow**: vibecoding (code-first)

## Intent

<user's full descriptive text verbatim>

## Plan

<minimal bullet-point plan derived from the intent — 3-7 items max, high-level>

## Notes

_Record observations, decisions, or scope changes here during the session._
```

For the Plan section: extract the key tasks/goals from the user's text and list them as concise bullet points. Do not over-specify — this is a lightweight plan for intent traceability, not a full spec.

---

## Step 4 — Delete spec.md template

The create-new-feature helper copies `spec-template.md` into the feature directory as `spec.md`. This is not needed for the vibecoding workflow. Delete `FEATURE_DIR/spec.md`.

---

## Step 5 — Report

Output:

```
Vibecoding session started.
Branch: <BRANCH_NAME>
Directory: <FEATURE_DIR>
Artifact: <FEATURE_DIR>/vibecode.md

> Switch to the default development agent now before making any code changes.
> This agent (vibecode-specify) is for session setup only.
```

### If category C (descriptive text):

After the report, proceed to accomplish the user's tasks described in the intent. You are free to write
code, create files, and make changes as needed. The vibecoding workflow is code-first — no further spec
ceremony is required before implementation.

### If category A or B:

After the report: _"Ready for vibecoding. Switch to the default development agent, make your changes, then
run /speckit.canon.vibecode-drift-express (or /speckit.canon.vibecode-drift-reverse) to sync with canon."_

---

## Rules

- This command MUST be run from the base branch configured in `.specify/extensions/canon/canon-config.yml` under `branching.base`.
- Do NOT create spec.md, plan.md, tasks.md, or any other standard spec artifacts. The only artifact is vibecode.md.
- Do NOT run the full specify/clarify/plan/tasks pipeline. This is the vibecoding entry point — minimal ceremony by design.
- The branch and feature directory are created the same way as `/speckit.specify`, including honoring the project's sequential or timestamp prefix mode — the only difference is what goes inside.
- For category C: after creating the branch and vibecode.md, proceed directly to implementation. Do not ask for confirmation or additional requirements gathering.
