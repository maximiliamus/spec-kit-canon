---
name: testing-spec-kit-canon-extension
description: Claude skill entrypoint for the shared Spec Kit Canon extension test workflow. Use when Claude needs to start or resume the local extension validation run against the real sibling workspace layout (`spec-kit`, `spec-kit-canon`, `spec-kit-canon-test`), optionally clear `spec-kit-canon-test` before step 1, seed the trivial canon baseline, run the standard `/speckit.specify` to `/speckit.implement` workflow, exercise `/speckit.canon.drift` (with manual resolve and analyze gates) and `/speckit.canon.vibecode-drift` (with analyze gate before canonize), verify canon updates, and generate the final validation report.
---

# Testing Spec Kit Canon Extension

This is the Claude skill entrypoint for the shared skill source in
`skills/testing-spec-kit-canon-extension`.

Before doing any work:

1. Read `skills/testing-spec-kit-canon-extension/core/workflow.md`.
2. Read `skills/testing-spec-kit-canon-extension/core/test-flow.md`.
3. Use shared scripts from `skills/testing-spec-kit-canon-extension/scripts`.
4. Use shared assets from `skills/testing-spec-kit-canon-extension/assets`.
5. Preserve any command flags such as `--script sh|ps` or `--restart`
   when preparing the workflow.

## Wrapper Rules

- Treat `skills/testing-spec-kit-canon-extension/core/workflow.md` as the canonical workflow.
- Treat `skills/testing-spec-kit-canon-extension/core/test-flow.md` as the canonical prompt and verification reference.
- Start command-driven runs with `skills/testing-spec-kit-canon-extension/scripts/prepare_workflow.py`.
- Use `skills/testing-spec-kit-canon-extension/scripts/manage_progress.py` to store and resume workflow state.
- Do not duplicate or fork the workflow in this entrypoint.
- Keep Claude-specific behavior limited to skill invocation concerns.
