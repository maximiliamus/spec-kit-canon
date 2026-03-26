---
description: Fully autonomous vibecode drift orchestrator — spawns each drift command as a subagent in sequence with zero operator interaction. All decisions are made by the agent on behalf of the operator.
handoffs: []
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Autonomy Principle

This is a **fully autonomous** orchestrator. Do NOT ask the operator any questions at any point during the pipeline. Instruct each subagent to apply the same principle:

- Existing artifact overwrite prompts → answer **yes** (overwrite)
- Confirmation gates before applying → answer **yes** (proceed)
- Ambiguous classification choices → use best judgment and proceed
- Any yes/no prompt → answer **yes**

The only reason to stop is a hard error (script failure, not on a feature branch) or an early exit (no changes detected).

---

## Pipeline

Execute the following steps **in order**. Each step spawns a subagent via the Agent tool that runs the corresponding command. Wait for each subagent to complete before spawning the next — each step depends on artifacts produced by the previous one.

When spawning each subagent, include in the prompt:

1. The command to execute (e.g., `/speckit.canon.vibecode-drift-reverse`)
2. The Autonomy Principle: _"Do NOT ask the operator any questions. If a prompt asks for confirmation or a yes/no choice, answer yes and proceed. If asked about overwriting existing artifacts, overwrite them."_
3. Any user input from `$ARGUMENTS` if relevant

### Step 1 — Reverse

Spawn subagent: `/speckit.canon.vibecode-drift-reverse`

Parse result. If zero tasks reported → stop. Report: _"No implementation changes detected. Canon is up to date."_

### Step 2 — Detect

Spawn subagent: `/speckit.canon.vibecode-drift-detect`

Parse result. If zero findings reported → stop. Report: _"No spec-level drift. Canon is up to date."_

### Step 3 — Reconcile

Spawn subagent: `/speckit.canon.vibecode-drift-reconcile`

Parse result. If zero canon gaps reported → stop. Report: _"All drift already reflected in canon."_

### Step 4 — Canonize

Spawn subagent: `/speckit.canon.vibecode-drift-canonize`

### Step 5 — Analyze

Spawn subagent: `/speckit.canon.drift-analyze`

Parse result. If zero repair candidates → skip to Report.

### Step 6 — Repair (only if Step 5 found issues)

Spawn subagent: `/speckit.canon.drift-repair`

Then spawn `/speckit.canon.drift-analyze` once more. If issues still remain, log them as warnings — do not loop further.

---

## Report

After all steps complete, output a single combined summary:

```
Vibecode Drift Pipeline — Complete
===================================
Step 1 — Reverse:    [N] tasks
Step 2 — Detect:     [N] spec drift findings
Step 3 — Reconcile:  [N] canon entries
Step 4 — Canonize:   [N] canon files modified
Step 5 — Analyze:    [OK | N repair candidates]
Step 6 — Repair:     [skipped | N repairs applied | N warnings remaining]

Artifacts:
  - FEATURE_DIR/tasks.drift.md
  - FEATURE_DIR/spec.drift.md
  - FEATURE_DIR/canonization.md
  [- FEATURE_DIR/canonization-repair.md]  (if repairs were needed)

Canon updated successfully.
```

If warnings remain after repair: _"Manual review recommended for the remaining issues listed above."_

---

## Rules

- **Zero operator interaction.** Every decision is made autonomously.
- **Delegate via subagents.** Each step spawns a subagent that executes the corresponding command. This orchestrator only controls sequencing, decision-making between steps, and the final report.
- **Sequential execution.** Each subagent must complete before the next is spawned — later steps depend on artifacts from earlier ones.
- Maximum one repair iteration (Step 6). If issues persist, report warnings and stop.

