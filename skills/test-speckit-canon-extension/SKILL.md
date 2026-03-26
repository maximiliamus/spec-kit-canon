---
name: test-speckit-canon-extension
description: Validate the local Spec-Kit Canon extension and canon-core preset against the real sibling workspace layout (`spec-kit`, `spec-kit-canon`, `spec-kit-canon-test`). Use when starting or resuming the dedicated extension test workflow, optionally clearing `spec-kit-canon-test` before step 1, seeding the trivial canon, running the standard `/speckit.specify` to `/speckit.implement` workflow, exercising `/speckit.canon.drift` and `/speckit.canon.vibecode-drift`, and verifying that canon updates capture new API and web UI behavior.
---

# Test Speckit Canon Extension

This folder is the canonical shared skill source.

Use the shared material from:

- `./core`
- `./scripts`
- `./assets`

## Shared Rules

- Treat [core/workflow.md](./core/workflow.md) as the canonical workflow.
- Treat [core/test-flow.md](./core/test-flow.md) as the canonical prompt and
  verification reference.
- Use [scripts/manage_progress.py](./scripts/manage_progress.py) to create and
  update the resumable workflow progress file.
- Keep the shared workflow and validation guidance in this skill package.
