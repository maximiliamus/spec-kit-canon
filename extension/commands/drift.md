---
description: Standard drift orchestrator — spawns each drift command as a subagent in sequence. Autonomous except for the Resolve step, which always requires operator validation.
handoffs: []
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Autonomy Principle

This orchestrator is **autonomous for all steps except Resolve**. For non-resolve steps, instruct each subagent:

- Existing artifact overwrite prompts → answer **yes** (overwrite)
- Confirmation gates before applying → answer **yes** (proceed)
- Classification choices → use best judgment and proceed
- Any yes/no prompt → answer **yes**

### Resolve step exception

Step 3 (Resolve) is **always interactive**. The operator must validate every SPEC-REJECTED and IMPL-REJECTED decision. Do NOT answer on their behalf. Run `/speckit.canon.drift-resolve` directly (not as a subagent) so the operator sees each prompt and responds themselves. Once resolve completes, resume autonomous execution for the remaining steps.

The only reason to stop is a hard error (script failure, not on a feature branch) or an early exit (no changes detected).

---

## Pipeline

Execute the following steps **in order**. Each step spawns a subagent via the Agent tool that runs the corresponding command. Wait for each subagent to complete before spawning the next — each step depends on artifacts produced by the previous one.

When spawning each subagent (all steps except Step 3), include in the prompt:

1. The command to execute (e.g., `/speckit.canon.drift-reverse`)
2. The Autonomy Principle: _"Do NOT ask the operator any questions. If a prompt asks for confirmation or a yes/no choice, answer yes and proceed. If asked about overwriting existing artifacts, overwrite them."_
3. Any user input from `$ARGUMENTS` if relevant

### Step 1 — Reverse

Spawn subagent: `/speckit.canon.drift-reverse`

Parse result. If zero tasks reported → stop. Report: _"No implementation changes detected. Canon is up to date."_

### Step 2 — Detect

Spawn subagent: `/speckit.canon.drift-detect`

Parse result. If zero findings reported → stop. Report: _"No spec-level drift. Canon is up to date."_

### Step 3 — Resolve (interactive — operator required)

**Do NOT spawn as a subagent.** Execute `/speckit.canon.drift-resolve` directly so the operator can see and respond to each prompt in real time.

The operator will validate each item:

- SPEC-REJECTED items: approve or decline the spec.md correction
- IMPL-REJECTED items: choose F (fix now) or T (create task for later)

Wait for resolve to complete fully before proceeding. If resolve cannot fully complete (e.g., tasks were created for deferred IMPL-REJECTED items), proceed to Step 4 anyway — reconcile and canonize will work with whatever items are resolved.

### Step 4 — Reconcile

Spawn subagent: `/speckit.canon.drift-reconcile`

Parse result. If zero canon gaps reported → stop. Report: _"All drift already reflected in canon."_

### Step 5 — Canonize

Spawn subagent: `/speckit.canon.drift-canonize`

### Step 6 — Analyze

Spawn subagent: `/speckit.canon.drift-analyze`

Parse result. If zero repair candidates → skip to Report.

### Step 7 — Repair (only if Step 6 found issues)

Spawn subagent: `/speckit.canon.drift-repair`

Then spawn `/speckit.canon.drift-analyze` once more. If issues still remain, log them as warnings — do not loop further.

---

## Report

After all steps complete, output a single combined summary:

```
Standard Drift Pipeline — Complete
====================================
Step 1 — Reverse:    [N] tasks
Step 2 — Detect:     [N] spec drift findings
Step 3 — Resolve:    [N] resolved ([N] SPEC-ACCEPTED, [N] IMPL-ACCEPTED, [N] deferred)
Step 4 — Reconcile:  [N] canon entries
Step 5 — Canonize:   [N] canon files modified
Step 6 — Analyze:    [OK | N repair candidates]
Step 7 — Repair:     [skipped | N repairs applied | N warnings remaining]

Artifacts:
  - FEATURE_DIR/tasks.drift.md
  - FEATURE_DIR/spec.drift.md
  - FEATURE_DIR/canon.drift.md
  [- FEATURE_DIR/canon.repair.md]  (if repairs were needed)

Canon updated successfully.
```

If warnings remain after repair: _"Manual review recommended for the remaining issues listed above."_

If deferred IMPL-REJECTED items exist: _"[N] items deferred to tasks.md. Run /speckit.implement to complete them."_

---

## Rules

- **Autonomous except Resolve.** All steps run without operator input, except Step 3 (Resolve) which is always interactive.
- **Delegate via subagents.** Each step (except Resolve) spawns a subagent that executes the corresponding command. Resolve runs directly so the operator can interact with prompts.
- **Sequential execution.** Each step must complete before the next begins — later steps depend on artifacts from earlier ones.
- Maximum one repair iteration (Step 7). If issues persist, report warnings and stop.

