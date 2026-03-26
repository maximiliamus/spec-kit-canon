---
name: test-speckit-canon-extension
description: Claude skill entrypoint for the shared Spec-Kit Canon extension test workflow. Use when Claude needs to start or resume the local extension validation run against the real sibling workspace layout (`spec-kit`, `spec-kit-canon`, `spec-kit-canon-test`), optionally clear `spec-kit-canon-test` before step 1, seed the trivial canon baseline, run the standard `/speckit.specify` to `/speckit.implement` workflow, exercise `/speckit.canon.drift` and `/speckit.canon.vibecode-drift`, and verify canon updates.
---

# Test Speckit Canon Extension

This is the Claude skill entrypoint for the shared skill source in
`skills/test-speckit-canon-extension`.

Before doing any work:

1. Read `skills/test-speckit-canon-extension/core/workflow.md`.
2. Read `skills/test-speckit-canon-extension/core/test-flow.md`.
3. Use shared scripts from `skills/test-speckit-canon-extension/scripts`.
4. Use shared assets from `skills/test-speckit-canon-extension/assets`.

## Wrapper Rules

- Treat `skills/test-speckit-canon-extension/core/workflow.md` as the canonical workflow.
- Treat `skills/test-speckit-canon-extension/core/test-flow.md` as the canonical prompt and verification reference.
- Use `skills/test-speckit-canon-extension/scripts/manage_progress.py` to store and resume workflow state.
- Do not duplicate or fork the workflow in this entrypoint.
- Keep Claude-specific behavior limited to skill invocation concerns.
