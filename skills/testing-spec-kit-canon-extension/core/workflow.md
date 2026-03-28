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
spec-kit-canon-test/.specify/tmp/testing-spec-kit-canon-extension-progress.json
```

Generate the final report in:

```text
spec-kit-canon-test/.specify/tmp/testing-spec-kit-canon-extension-report.md
```

Archive developer-history copies in the extension repo:

```text
spec-kit-canon/tests/history/
```

Keep only the newest 10 timestamped report files in that folder. When a new
archived report is written and the count would exceed 10, remove the oldest
timestamped file.

If the workflow is started through an agent command wrapper, prepare the
workflow state with the shared helper first. That helper resumes in-progress
work by default, restarts automatically when the previous run already
completed, and supports an explicit `--restart` override:

```bash
python skills/testing-spec-kit-canon-extension/scripts/prepare_workflow.py
python skills/testing-spec-kit-canon-extension/scripts/prepare_workflow.py --script ps
python skills/testing-spec-kit-canon-extension/scripts/prepare_workflow.py --restart
python skills/testing-spec-kit-canon-extension/scripts/prepare_workflow.py --restart --script sh
```

Initialize or inspect the state before doing any step. The bash-first
documented path sets `--script sh` explicitly so the selected script column is
unambiguous on every platform:

```bash
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py init --script sh
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py show
```

If the run must start from a fully clean sandbox, initialize with the clear
flag. Keep `--script sh` unless you intentionally need PowerShell coverage:

```bash
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py init --clear-test-project --script sh
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py init --clear-test-project --script ps
```

That flag resets the progress file to step 1 and records that the sandbox
should be fully cleared when `reset_test_project.py` is run for the first
step. `--script sh|ps` records which Spec Kit script column the sandbox
must scaffold with. If it is omitted, the workflow still uses the host default:
`ps` on Windows and `sh` elsewhere. The examples in this workflow set `sh`
explicitly so the documented flow stays bash-first across platforms. If the
progress file already exists and the clear flag is not passed, resume from
`current_step` and do not redo completed steps.

Use these step ids when updating progress:

- `reset_sandbox`
- `verify_constitution_config`
- `initialize_canon`
- `standard_feature_workflow`
- `api_drift`
- `merge_to_master`
- `web_ui_vibecode`
- `verify_final_canon`
- `generate_test_report`

Before beginning the current step, mark it in progress:

```bash
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py start <step-id>
```

After a step finishes and its verification passes, mark it complete:

```bash
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py complete <step-id> --note "<result and evidence summary>"
```

Always provide a short `--note` that captures what passed and what evidence was
checked. The final report generator uses these completion notes as the per-step
result explanations.

If a step fails and must be retried, record the failed attempt before starting
it again:

```bash
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py error <step-id> --note "<failure summary>"
```

This keeps the workflow on the same step, increments the report error metrics,
and leaves the step ready to start again.

If the workflow is interrupted, run `show` again and continue from the stored
`current_step`.

## Git Notes

- `spec-kit-canon-test` is part of the test surface. Branch creation, commits,
  and the fast-forward merge back to `master` are required workflow steps, not
  optional cleanup.
- The progress file at
  `.specify/tmp/testing-spec-kit-canon-extension-progress.json` changes throughout
  the run. If `git checkout master` is blocked, commit or stash that file
  before switching branches.
- Before `git add -A` or any sandbox commit, confirm
  `.specify/extensions/canon/.git` is absent. Never commit nested git metadata
  from the installed extension copy. If it appears, remove it from the sandbox
  and treat it as an extension packaging bug to fix in `spec-kit-canon`.
- Keep transient Python artifacts such as `__pycache__/` and `*.pyc` out of the
  sandbox commits so the merge step tests real project state, not local cache
  noise.

## Workflow

### 1. Reset the sandbox project (`reset_sandbox`)

Run:

```bash
python skills/testing-spec-kit-canon-extension/scripts/reset_test_project.py
```

If the progress file says `clear_test_project` is `true`, add
`--clear-test-project` to that command.

`reset_test_project.py` reads the stored `script` from the progress file.
Pass `--script sh` or `--script ps` only when you intentionally need
to override the saved workflow setting for this reset.

Use the script output as the source of truth for `workspace_root`,
`test_project_dir`, `config_fixture`, `script`, and the installed config
paths.

After the script finishes, verify:

- `spec-kit`, `spec-kit-canon`, and `spec-kit-canon-test` were resolved as sibling directories
- `spec-kit-canon-test/.specify/extensions/canon` exists
- `spec-kit-canon-test/.specify/presets/canon-core` exists
- the reported `script` matches the workflow setting you intended to test
- the reported `applied_config` matches the shared constitution config fixture

When the reset and verification are done, run:

```bash
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py complete reset_sandbox --note "Reset spec-kit-canon-test, reinstalled the local extension and preset, and confirmed the shared config fixture was applied."
```

### 2. Verify constitution config rendering (`verify_constitution_config`)

From `spec-kit-canon-test`:

1. Open the shared config fixture from [test-flow.md](./test-flow.md) and the
   installed `.specify/extensions/canon/canon-config.yml`.
2. Confirm the installed config matches the fixture values for:
   - `project.name`
   - `canon.root`
   - `branching.types`
   - `branching.scopes`
3. Run `/speckit.constitution` with no arguments.
4. Switch back to the `spec-kit-canon` repo root and run:

```bash
python skills/testing-spec-kit-canon-extension/scripts/verify_constitution_config.py
```

5. Verify the script reports success for the config-driven constitution checks
   from [test-flow.md](./test-flow.md), including the rendered Section 6 type
   and scope tables, the configured canon root, and the generated `_toc.md`
   location.

When the constitution verification passes, run:

```bash
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py complete verify_constitution_config --note "Ran /speckit.constitution and verified the configured canon root plus the Section 6 branch tables rendered from the shared fixture."
```

### 3. Initialize the canon baseline (`initialize_canon`)

Switch back to the `spec-kit-canon` repo root and copy the bundled canon
   template:

```bash
python skills/testing-spec-kit-canon-extension/scripts/seed_canon_template.py
```

Verify the copied baseline from [test-flow.md](./test-flow.md):
   - `_toc.md` remains the canon entry point
   - `overview.md` defines the Todo entity
   - `architecture.md` captures the baseline structure
   - `api.md` documents exactly two starting API capabilities: list todos and fetch one todo

When the baseline is seeded and verified, run:

```bash
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py complete initialize_canon --note "Seeded the configured canon root with the baseline _toc.md, overview.md, architecture.md, and api.md files."
```

### 4. Run the standard feature workflow (`standard_feature_workflow`)

Use the standard feature prompt from [test-flow.md](./test-flow.md).
Keep that prompt thin-boundaried when you run `/speckit.specify`: no extra
functionality, no early write behavior, and no optional hardening work beyond
the minimum needed to make the flow pass.

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
If the generated spec, plan, or tasks expand beyond the step 4 boundaries,
trim them back before implementing so the run only covers list-todos and
get-todo behavior.

After implementation, run the project's automated checks if they exist. If the
implementation created a runnable app, perform one quick smoke check that
proves the list and get behaviors exist.

When the feature workflow and smoke check pass, run:

```bash
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py complete standard_feature_workflow --note "Completed the standard feature flow through /speckit.implement and smoke-tested the list and get todo behavior."
```

### 5. Add the third API method directly, then run standard drift (`api_drift`)

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

```bash
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py complete api_drift --note "Added update todo directly in code, ran /speckit.canon.drift, and confirmed canon now documents the update behavior."
```

### 6. Merge the first branch back to `master` (`merge_to_master`)

The vibecode entry command must start from `master`.

Before starting the second pass:

1. ensure the feature branch worktree is clean; if the progress file was just
   updated, commit or stash it before `git checkout master`
2. create a local commit for the first feature
3. `git checkout master`
4. `git merge --ff-only <first-feature-branch>`

When `master` contains the first feature and the worktree is clean, run:

```bash
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py complete merge_to_master --note "Committed the first feature branch and fast-forward merged it back into master."
```

### 7. Run the vibecode web UI pass (`web_ui_vibecode`)

From `master`, run `/speckit.canon.vibecode-specify` with the web UI prompt
from [test-flow.md](./test-flow.md).

Let the command create the branch, write `vibecode.md`, and implement the
change. After the UI exists, run `/speckit.canon.vibecode-drift`.

When the UI implementation and vibecode drift pass finish, run:

```bash
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py complete web_ui_vibecode --note "Ran the vibecode UI flow and confirmed canon drift captured the list, load, and update UI behavior."
```

### 8. Verify the final canon (`verify_final_canon`)

Confirm the final canon documents now cover:

- the list, get, and update todo API behavior
- the web UI surface that lists todos, loads a single todo, and updates a todo
- `_toc.md` links for every canon file introduced during the test

Use `rg -n "todo|update|web|html|javascript|ui" docs/canon` or equivalent to
find the updated canon sections, then inspect the actual files instead of
relying on the grep output alone. If the shared config fixture changes the
canon root in the future, use that configured root instead.

When the final canon evidence is confirmed, run:

```bash
python skills/testing-spec-kit-canon-extension/scripts/manage_progress.py complete verify_final_canon --note "Verified the final canon covers list, get, and update API behavior, the web UI surface, and complete _toc.md links."
```

### 9. Generate the final test report (`generate_test_report`)

Run the final report step from the `spec-kit-canon` repo root:

```bash
python skills/testing-spec-kit-canon-extension/scripts/generate_test_report.py --complete-step --note "Generated the final Markdown report with overall summary tables, test run metrics, and per-step results."
```

Verify the report at
`spec-kit-canon-test/.specify/tmp/testing-spec-kit-canon-extension-report.md`
includes:

- an overall summary table with the selected script plus workflow status
  and completed, in-progress, and pending step counts
- a test run metrics table with total steps, passed steps, pass rate,
  recorded errors, total active elapsed time, and wall-clock span
- a step summary table with every workflow step, status, elapsed timing, and
  result note, plus the recorded error count for each step
- a per-step results section that explains the outcome of each step
- a developer-history copy under
  `spec-kit-canon/tests/history/`
  named like
  `<YYYYMMDDTHHMMZ>-testing-spec-kit-canon-extension-report.md`

The report generator automatically copies the rendered Markdown report into the
extension-repo history folder, prunes the timestamped history to the newest 10
files, and opens the archived copy for review. Use `--no-open` only when you
intentionally want to skip that behavior.

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
- Any test step that works with `/speckit.*` commands must finish within
  5 minutes. If it trends longer, tighten prompt boundaries or reduce scope
  before treating the flow as acceptable.
- Keep canon content at the WHAT level. Do not copy implementation details,
  file layouts, or framework choices into canon unless they are already part of
  the canonical project structure.
- Report the evidence for each verification step: which canon files changed and
  which sections prove the new API or UI behavior is now canonical.
- Avoid empty report rows by providing a meaningful `--note` on every
  `manage_progress.py complete` call.
