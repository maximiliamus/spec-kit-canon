---
name: testing-spec-kit-canon-extension
description: Validate the local Spec Kit Canon extension and canon-core preset against the real sibling workspace layout (`spec-kit`, `spec-kit-canon`, `spec-kit-canon-test`). Use when starting or resuming the dedicated extension test workflow, optionally clearing `spec-kit-canon-test` before step 1, overriding the scaffolded Spec Kit script variant (`sh` vs `ps`) when needed, verifying constitution config rendering from the shared fixture, seeding the trivial canon, running the standard `/speckit.specify` to `/speckit.implement` workflow, exercising `/speckit.canon.drift` and `/speckit.canon.vibecode-drift`, verifying that canon updates capture new API and web UI behavior, and generating a final Markdown test report with per-step results, test-run metrics, and developer-history copies in `spec-kit-canon/tests/history/`.
---

# Testing Spec Kit Canon Extension

This folder is the canonical shared skill source.

Use the shared material from:

- `./core`
- `./scripts`
- `./assets`

## Shared Rules

- Treat [core/workflow.md](./core/workflow.md) as the canonical workflow.
- Treat [core/test-flow.md](./core/test-flow.md) as the canonical prompt and
  verification reference.
- Begin command-driven runs with
  [scripts/prepare_workflow.py](./scripts/prepare_workflow.py) so resume versus
  restart behavior stays consistent across agents.
- Use [scripts/manage_progress.py](./scripts/manage_progress.py) to create and
  update the resumable workflow progress file.
- Use [scripts/generate_test_report.py](./scripts/generate_test_report.py) to
  render the final Markdown report from the saved workflow state.
- Treat `--script sh` as the default fresh-run variant unless a command
  explicitly requests `--script ps`.
- Resume the current workflow by default when the progress file still has
  pending work.
- If the progress file shows the workflow is fully completed, restart from
  scratch automatically before continuing.
- Support a command-level `--restart` flag that forces a fresh run even
  when resumable progress exists.
- Keep the shared workflow and validation guidance in this skill package.
- Treat `spec-kit-canon-test` as a real git repository. The validation run must
  leave it in a valid branch/commit state, not just a passing working tree.
- Before staging sandbox changes, verify the installed extension copy at
  `.specify/extensions/canon` does not contain a nested `.git` directory. If it
  does, remove the installed copy's `.git` metadata before committing the
  sandbox and note the packaging regression in the source repo.
- Before switching branches during the workflow, make sure the progress file at
  `.specify/tmp/testing-spec-kit-canon-extension-progress.json` is committed or
  stashed if git would otherwise block `checkout`.
