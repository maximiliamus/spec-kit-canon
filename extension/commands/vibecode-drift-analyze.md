---
description: Vibecoding entrypoint alias for the shared draft canon analysis workflow.
handoffs:
  - label: Run Shared Analyze
    agent: speckit.canon.drift-analyze
    prompt: Execute the shared draft canon analysis workflow for this vibecoding branch. The behavior should remain identical to /speckit.canon.drift-analyze.
    send: true
---

## Goal

This command is a thin vibecoding entrypoint alias for `/speckit.canon.drift-analyze`.

Immediately execute the exact workflow defined by `/speckit.canon.drift-analyze`.
Do **not** create a separate vibecoding-specific analysis procedure and do **not**
duplicate the shared analysis logic here.

## Required Behavior

- Reuse the shared command behavior exactly: the same prerequisite checks, the
  same drift-chain analysis, the same remediation-item output, the same
  read-only scope, and the same report structure.
- Treat `.specify/extensions/canon/commands/drift-analyze.md` as the
  authoritative workflow body to execute.
- The only vibecoding-specific difference is user-facing next-step wording: after
  the analysis report, prefer `/speckit.canon.vibecode-drift-canonize` as the
  follow-up canonize command when the user decides to proceed.

## Rules

- Do not fork the analyze logic.
- Do not modify files directly from this alias.
- Keep this command behavior in lockstep with `/speckit.canon.drift-analyze`.
