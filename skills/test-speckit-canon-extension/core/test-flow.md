# Test Flow

## Workspace Assumptions

- Run the skill from `spec-kit-canon`.
- Use the sibling layout from `DEVELOPMENT.md`:
  - `../spec-kit`
  - `../spec-kit-canon`
  - `../spec-kit-canon-test`
- Track workflow state in `spec-kit-canon-test/.specify/tmp/test-speckit-canon-extension-progress.json`.
- Resume from the `current_step` stored in that file unless the run was reinitialized with `--clear-test-project`.

## Canon Seed

After `/speckit.constitution`, return to the `spec-kit-canon` repo root and
seed the canon by copying the bundled template:

```powershell
python skills/test-speckit-canon-extension/scripts/seed_canon_template.py
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

## Standard Feature Prompt

Use this with `/speckit.specify`:

```text
Implement a trivial Todo API that conforms to canon. Users can list all todos and fetch one todo by id. Keep the scope intentionally small for extension testing, include a tiny starter dataset, and avoid adding write capabilities in this first pass.
```

## Direct Drift Addition

Implement this directly on the first feature branch before running
`/speckit.canon.drift`:

```text
Add a third API capability: update an existing todo. Preserve the list and get behavior. Allow changing the todo title and completed state, and keep the change minimal enough that the resulting drift should canonize cleanly.
```

## Web UI Vibecode Prompt

Use this with `/speckit.canon.vibecode-specify` from `master`:

```text
Create a trivial web UI for the Todo API using plain HTML, CSS, and vanilla JavaScript. The page must list todos, load one todo into a simple editor, and update a todo through the existing API. Keep the styling minimal and do not introduce a frontend framework.
```

## Verification Targets

After `/speckit.canon.drift`, verify canon evidence for:

- a Todo update capability in the API canon
- the Todo fields needed by that update behavior
- `_toc.md` still linking all canon files

After `/speckit.canon.vibecode-drift`, verify canon evidence for:

- a web UI page or section in canon
- list, load, and update behavior described for the UI
- any new canon file linked from `_toc.md`

Do not stop at grep matches. Open the canon files and confirm the text is
actually authoritative canon content.
