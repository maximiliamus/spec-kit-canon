# Shared Workflow

Use this skill from the `spec-kit-canon` repo root when testing local extension
or preset changes against the real `specify` CLI. Keep the sandbox
intentionally small and deterministic so the workflow itself is what gets
tested.

Read [test-flow.md](./test-flow.md) before starting the first command
sequence. It contains the exact prompts and verification targets for the
baseline API, the drift update, and the web UI vibecode pass.

## Progress Tracking

Track the workflow in:

```text
spec-kit-canon-test/.specify/tmp/test-speckit-canon-extension-progress.json
```

Initialize or inspect the state before doing any step:

```powershell
python skills/test-speckit-canon-extension/scripts/manage_progress.py init
python skills/test-speckit-canon-extension/scripts/manage_progress.py show
```

If the run must start from a fully clean sandbox, initialize with the clear
flag:

```powershell
python skills/test-speckit-canon-extension/scripts/manage_progress.py init --clear-test-project
```

That flag resets the progress file to step 1 and records that the sandbox
should be fully cleared when `reset_test_project.py` is run for the first
step. If the progress file already exists and the clear flag is not passed,
resume from `current_step` and do not redo completed steps.

Use these step ids when updating progress:

- `reset_sandbox`
- `initialize_canon`
- `standard_feature_workflow`
- `api_drift`
- `merge_to_master`
- `web_ui_vibecode`
- `verify_final_canon`

Before beginning the current step, mark it in progress:

```powershell
python skills/test-speckit-canon-extension/scripts/manage_progress.py start <step-id>
```

After a step finishes and its verification passes, mark it complete:

```powershell
python skills/test-speckit-canon-extension/scripts/manage_progress.py complete <step-id>
```

If the workflow is interrupted, run `show` again and continue from the stored
`current_step`.

## Workflow

### 1. Reset the sandbox project (`reset_sandbox`)

Run:

```powershell
python skills/test-speckit-canon-extension/scripts/reset_test_project.py --project-name "Spec Kit Canon Test"
```

If the progress file says `clear_test_project` is `true`, add
`--clear-test-project` to that command.

Use the script output as the source of truth for `workspace_root`,
`test_project_dir`, and the installed config paths.

After the script finishes, verify:

- `spec-kit`, `spec-kit-canon`, and `spec-kit-canon-test` were resolved as sibling directories
- `spec-kit-canon-test/.specify/extensions/canon` exists
- `spec-kit-canon-test/.specify/presets/canon-core` exists

When the reset and verification are done, run:

```powershell
python skills/test-speckit-canon-extension/scripts/manage_progress.py complete reset_sandbox
```

### 2. Initialize the canon baseline (`initialize_canon`)

From `spec-kit-canon-test`:

1. Open `.specify/extensions/canon/canon-config.yml` and confirm
   `project.name` is `Spec Kit Canon Test`.
2. Run `/speckit.constitution` with no arguments.
3. Switch back to the `spec-kit-canon` repo root and copy the bundled canon
   template:

```powershell
python skills/test-speckit-canon-extension/scripts/seed_canon_template.py
```

4. Verify the copied baseline from [test-flow.md](./test-flow.md):
   - `_toc.md` remains the canon entry point
   - `overview.md` defines the Todo entity
   - `architecture.md` captures the baseline structure
   - `api.md` documents exactly two starting API capabilities: list todos and fetch one todo

When the baseline is seeded and verified, run:

```powershell
python skills/test-speckit-canon-extension/scripts/manage_progress.py complete initialize_canon
```

### 3. Run the standard feature workflow (`standard_feature_workflow`)

Use the standard feature prompt from [test-flow.md](./test-flow.md).

Execute the following commands in order:

1. `/speckit.specify ...`
2. `/speckit.clarify` only if the generated spec still contains unresolved
   clarification markers
3. `/speckit.plan`
4. `/speckit.tasks`
5. `/speckit.analyze`
6. `/speckit.implement`

Keep the implementation deliberately small. When the repo is otherwise blank,
prefer a minimal Python HTTP service with in-memory or tiny JSON-backed todos
because the workspace already depends on Python and `uv`.

After implementation, run the project's automated checks if they exist. If the
implementation created a runnable app, perform one quick smoke check that
proves the list and get behaviors exist.

When the feature workflow and smoke check pass, run:

```powershell
python skills/test-speckit-canon-extension/scripts/manage_progress.py complete standard_feature_workflow
```

### 4. Add the third API method directly, then run standard drift (`api_drift`)

Stay on the same feature branch. Do not start a new spec workflow for this
step.

Implement the direct code-first change from [test-flow.md](./test-flow.md):
add the third API capability, `update todo`, while preserving the existing list
and get behavior.

Then run `/speckit.canon.drift`.

If `/speckit.canon.drift` reaches interactive resolve prompts, act as the
operator and keep the pipeline moving:

- approve spec updates for `SPEC-REJECTED` items when the code is the intended
  new truth
- prefer `F` fix-now over deferring tasks for `IMPL-REJECTED` items unless the
  fix is clearly outside the trivial scope
- overwrite generated drift artifacts when prompted

After the orchestrator finishes, inspect the canon root and confirm it now
captures the update behavior at the WHAT level, not just in implementation
files.

When the drift pass finishes and the canon evidence is confirmed, run:

```powershell
python skills/test-speckit-canon-extension/scripts/manage_progress.py complete api_drift
```

### 5. Merge the first branch back to `master` (`merge_to_master`)

The vibecode entry command must start from `master`.

Before starting the second pass:

1. ensure the feature branch worktree is clean
2. create a local commit for the first feature
3. `git checkout master`
4. `git merge --ff-only <first-feature-branch>`

When `master` contains the first feature and the worktree is clean, run:

```powershell
python skills/test-speckit-canon-extension/scripts/manage_progress.py complete merge_to_master
```

### 6. Run the vibecode web UI pass (`web_ui_vibecode`)

From `master`, run `/speckit.canon.vibecode-specify` with the web UI prompt
from [test-flow.md](./test-flow.md).

Let the command create the branch, write `vibecode.md`, and implement the
change. After the UI exists, run `/speckit.canon.vibecode-drift`.

When the UI implementation and vibecode drift pass finish, run:

```powershell
python skills/test-speckit-canon-extension/scripts/manage_progress.py complete web_ui_vibecode
```

### 7. Verify the final canon (`verify_final_canon`)

Confirm the final canon documents now cover:

- the list, get, and update todo API behavior
- the web UI surface that lists todos, loads a single todo, and updates a todo
- `_toc.md` links for every canon file introduced during the test

Use `rg -n "todo|update|web|html|javascript|ui" specs/000-canon` or
equivalent to find the updated canon sections, then inspect the actual files
instead of relying on the grep output alone.

When the final canon evidence is confirmed, run:

```powershell
python skills/test-speckit-canon-extension/scripts/manage_progress.py complete verify_final_canon
```

## Shared Rules

- Use the exact sibling workspace layout from `DEVELOPMENT.md`; do not point
  the script at any other project.
- Keep the sandbox feature scope intentionally trivial. The point is to
  validate the workflow, not to build a production app.
- Use slash commands exactly as shipped by this repo:
  `/speckit.constitution`, `/speckit.specify`, `/speckit.plan`,
  `/speckit.tasks`, `/speckit.analyze`, `/speckit.implement`,
  `/speckit.canon.drift`, `/speckit.canon.vibecode-specify`, and
  `/speckit.canon.vibecode-drift`.
- Keep canon content at the WHAT level. Do not copy implementation details,
  file layouts, or framework choices into canon unless they are already part of
  the canonical project structure.
- Report the evidence for each verification step: which canon files changed and
  which sections prove the new API or UI behavior is now canonical.
