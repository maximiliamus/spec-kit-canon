# Test Flow

## Workspace Assumptions

- Run the skill from `spec-kit-canon`.
- Use the sibling layout from `DEVELOPMENT.md`:
  - `../spec-kit`
  - `../spec-kit-canon`
  - `../spec-kit-canon/extension`
  - `../spec-kit-canon/preset`
  - `../spec-kit-canon-test`
- Track workflow state in `spec-kit-canon-test/.specify/tmp/testing-spec-kit-canon-extension-progress.json`.
- Write the final report to `spec-kit-canon-test/.specify/tmp/testing-spec-kit-canon-extension-report.md`.
- Archive developer-history copies under `spec-kit-canon/tests/history/`.
- Keep only the newest 10 timestamped archived reports in that history folder.
- Use `manage_progress.py init --script sh --clear-test-project` as the
  default documented setup, especially on Windows. Use `--script ps` only when
  you intentionally want to validate the PowerShell column.
- Resume from the `current_step` stored in that file unless the run was reinitialized with `--clear-test-project`.

## Shared Constitution Config Fixture

Use the shared config fixture at:

```text
skills/testing-spec-kit-canon-extension/assets/constitution-config-fixture.json
```

The fixture values under test are:

- `project.name`: `Spec Kit Canon Config Test`
- `canon.root`: `docs/canon`
- `branching.base`: `master`
- `branching.types`:
  - `feature` -> `Feature`
  - `fix` -> `Bug Fix`
  - `polish` -> `Non-Functional`
  - `document` -> `Documentation Only`
- `branching.scopes`:
  - `api` -> `Todo API surface`
  - `web` -> `Todo browser UI`
  - `ops` -> `Operational tooling`

After `/speckit.constitution`, verify that:

- `.specify/extensions/canon/canon-config.yml` matches the fixture exactly
- `.specify/memory/constitution.md` uses `docs/canon/_toc.md` and `docs/canon/**`
- `.specify/templates/constitution-template.md` also uses the configured canon root while preserving only the approved metadata placeholders
- `.gitattributes` exists at the project root and encodes the bash-first line-ending policy
- the Section 6 type and scope tables in both constitution files match the fixture order and values exactly
- the Section 6 example branch names use only the configured type and scope codes
- `docs/canon/_toc.md` exists and its H1 matches `Spec Kit Canon Config Test`
- `bash -lc 'git status --short'` remains clean before feature work so drift steps do not see line-ending-only noise

## Canon Seed

After `/speckit.constitution`, return to the `spec-kit-canon` repo root and
seed the canon by copying the bundled template:

```bash
python skills/testing-spec-kit-canon-extension/scripts/seed_canon_template.py
```

The copied baseline must contain:

- `_toc.md` links to `overview.md`, `architecture.md`, and `api.md`
- `overview.md` defines the project as a trivial Todo service used for extension testing
- `overview.md` defines one entity, `Todo`, with `id`, `title`, and `completed`
- `architecture.md` defines the baseline components and interactions at the WHAT level
- `api.md` defines exactly two starting behaviors:
  - list all todos
  - fetch one todo by id

Keep the writing authoritative and technology-agnostic.
The seed script must copy the baseline into the configured canon root from the
shared config fixture, which is `docs/canon` for the shared test flow.

## Standard Feature Prompt

Use this with `/speckit.specify`:

```text
Implement the smallest possible Todo API that conforms to canon.

Thin boundaries:
- support only two behaviors in this first pass: list all todos and fetch one todo by id
- include only a tiny starter dataset
- no write capabilities yet: no create, update, delete, toggle, or bulk operations
- no extra functionality: no filtering, sorting, pagination, search, auth, sessions, roles, audit trail, notifications, background jobs, admin features, or frontend
- no extra non-functional work beyond what is required to make the flow run

Success criteria:
- the API can list the starter todos
- the API can fetch one todo by id
- the implementation stays intentionally minimal so step 5 can add update todo as the first drift change
```

## Direct Drift Addition

Implement this directly on the first feature branch before running
`/speckit.canon.drift`:

```text
Add a third API capability: update an existing todo. Preserve the list and get behavior. Allow changing the todo title and completed state, and keep the change minimal enough that the resulting drift should canonize cleanly.
```

## Web UI Vibecoding Prompt

Use this with `/speckit.canon.vibecode-specify` from `master`:

```text
Create the smallest possible web UI for the existing Todo API.

Hard limits:
- plain HTML, CSS, and vanilla JavaScript only
- serve exactly one page at `/`
- keep existing API behavior unchanged
- no frontend framework
- no extra polish, animations, accessibility work, refactors, or security hardening unless required to make the flow work
- no new features beyond: list todos, load selected todo into editor, save title/completed via existing update API

Success criteria:
- page shows todo list
- clicking a todo loads it into the editor
- saving updates the todo through the existing API
- keep implementation intentionally minimal
```

## Verification Targets

After `/speckit.canon.drift`, verify canon evidence for:

- a Todo update capability in the API canon
- the Todo fields needed by that update behavior
- `_toc.md` still linking all canon files
- the orchestrator completed the full pipeline including the analyze step
  before canonize (either clean or with remediation applied)
- `tasks.alignment.md` was not created (the update-todo drift is simple
  enough that no alignment work should be needed)

After `/speckit.canon.vibecode-drift`, verify canon evidence for:

- a web UI page or section in canon
- list, load, and update behavior described for the UI
- any new canon file linked from `_toc.md`
- the orchestrator completed the analyze step before canonize

Do not stop at grep matches. Open the canon files and confirm the text is
actually authoritative canon content.

## Final Report

At the end of the workflow, run:

```bash
python skills/testing-spec-kit-canon-extension/scripts/generate_test_report.py --complete-step --note "Generated the final Markdown report with overall summary tables, test run metrics, and per-step results."
```

The report must include:

- an overall summary table with the selected script, workflow status,
  current step, and completed, in-progress, and pending counts
- a test run metrics table with pass rate, recorded errors, total active elapsed time, and wall-clock span
- a step summary table with one row per workflow step, a short result note, and the recorded error count
- a per-step result section that explains the outcome or evidence recorded for
  each step
- a developer-history copy written under
  `spec-kit-canon/tests/history/`
  using a timestamped filename like
  `<YYYYMMDDTHHMMZ>-testing-spec-kit-canon-extension-report.md`

The report generator should automatically copy the rendered report into the
extension-repo history folder, prune the timestamped history to the newest 10
files, and open the archived copy unless `--no-open` is used explicitly.
