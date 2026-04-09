# Development

The monorepo keeps the two publishable packages in separate first-level
directories: `extension` and `preset`.

## Package Layout

```text
spec-kit-canon/
├── extension/
├── preset/
├── skills/
└── tests/
```

- `extension/` is the install root for the `canon` extension package
- `preset/` is the install root for the `canon-core` preset package
- `skills/` and `tests/` stay repo-local and are not part of the published
  package roots

## Minimum Workspace Layout

At minimum, keep following directories in the same workspace:

```text
workspace/
├── spec-kit/
├── spec-kit-canon/
└── spec-kit-canon-test/
```

This repo assumes the upstream CLI source is available at `../spec-kit`
relative to `spec-kit-canon`.

The workspace currently includes `../spec-kit-canon-test` as the dedicated
local test project for validating extension and preset installs.

## Prerequisites

- Python 3.14+
- `uv`
- Git
- a test Spec Kit project where the extension and preset can be installed

## Why The Upstream Repo Is Needed

`spec-kit-canon` is not a standalone CLI. It depends on the upstream
`specify` command for:

- extension installation and loading
- preset installation and override resolution
- project initialization
- command registration behavior
- validation rules and runtime path conventions

If you change extension manifests, command naming, preset behavior, template
resolution assumptions, or script contracts, you need the upstream `spec-kit`
repo available to validate the real runtime behavior.

## Local Development Loop

### 1. Prepare the upstream CLI

From `../spec-kit`:

```bash
uv sync
uv run specify --help
```

### 2. Create or reuse a test project

Recommended test project: `../spec-kit-canon-test`

From that sandbox project directory:

```bash
uv run --project ../spec-kit specify init . --ai codex --force
```

### 3. Install this extension and preset from source

From `../spec-kit-canon-test`:

```bash
uv run --project ../spec-kit specify extension add --dev ../spec-kit-canon/extension
uv run --project ../spec-kit specify preset add --dev ../spec-kit-canon/preset
```

Use only the extension install if you are testing `speckit.canon.*` commands
without the core-command overrides.

### 4. Reinstall after changes

Re-run the relevant `specify ... add --dev` command after changing:

- `extension/extension.yml`
- `preset/preset.yml`
- `extension/commands/`
- `preset/commands/`
- `extension/templates/`
- `preset/templates/`
- `extension/scripts/`
- `extension/.extensionignore`

Installed extension and preset files are copied into the target project's
`.specify/` directory. Editing this repo does not automatically refresh an
already installed copy.

### 5. Validate behavior in the test project

Typical checks:

- confirm commands are registered
- run `/speckit.constitution`
- verify `.specify/extensions/canon/canon-config.yml`
- verify canon root and TOC initialization
- run drift workflow commands on a feature branch
- confirm preset overrides are active for `/speckit.specify`, `/speckit.plan`,
  `/speckit.tasks`, `/speckit.implement`, and `/speckit.constitution`

## What To Test Depending On The Change

### Extension-only changes

Examples:

- `extension/commands/`
- `extension/templates/`
- `extension/scripts/`
- `extension/extension.yml`

Minimum test:

```bash
uv run --project ../spec-kit specify extension add --dev ../spec-kit-canon/extension
```

Then exercise the affected `speckit.canon.*` command in a test project.

### Preset-only changes

Examples:

- `preset/commands/`
- `preset/templates/`
- `preset/preset.yml`

Minimum test:

```bash
uv run --project ../spec-kit specify preset add --dev ../spec-kit-canon/preset
```

Then exercise the affected core command override in a test project.

### Changes That Depend On Upstream CLI Behavior

Examples:

- command naming constraints
- extension ID assumptions
- preset resolution behavior
- script/path rewriting assumptions
- install-time file copying behavior

For these, inspect and test against `../spec-kit` directly, especially under:

- `../spec-kit/src/specify_cli/`
- `../spec-kit/templates/`
- `../spec-kit/scripts/`

## Workflow Terminology And Naming

Use the following naming rule consistently across docs, prompts, templates, and
user-facing command descriptions:

- Use `vibecoding` for the human-facing workflow or process name.
- Use `vibecoding` in prose such as `vibecoding workflow`,
  `vibecoding session`, `vibecoding path`, and `vibecoding drift`.
- Keep `vibecode` only for stable identifiers and artifact names such as
  `/speckit.canon.vibecode-specify`, `/speckit.canon.vibecode-drift`,
  `vibecode.md`, and the default slug `vibecode`.
- Do not rename command IDs, filenames, or slugs from `vibecode` to
  `vibecoding` unless you are intentionally making a breaking interface change.
- In headings and labels, prefer `Vibecoding` for workflow names and `Vibecode`
  only when you are showing the exact identifier or artifact title.

Examples:

- Correct prose: `Use the vibecoding workflow when you want to start coding immediately.`
- Correct identifier usage: `Run /speckit.canon.vibecode-drift after implementation changes.`
- Correct artifact usage: `The session writes vibecode.md.`
- Avoid in prose: `vibecode workflow`, `vibecode session`, `vibecode path`.

## Command Markdown Formatting

There does not currently appear to be a dedicated upstream formatting-rules
document for command Markdown, so follow the prevailing style in the upstream
command sources themselves.

Use the local upstream checkout as the reference point, especially:

- `../spec-kit/templates/commands/analyze.md`
- `../spec-kit/templates/commands/checklist.md`

Those upstream command files keep prefixed identifiers as plain text in prose,
for example FR-###, SC-###, CHK###, and similar task or finding IDs.

For this repo's command docs, follow these rules:

- Do not wrap prefixed identifiers in backticks when they appear as prose or in tables.
- This applies to both upstream-style IDs such as FR-###, SC-###, CHK###, T###, Q#, and A#, and canon-specific IDs such as TD-XXX, SD-XXX, TA-XXX, CD-XXX, and CR-XXX.
- Do wrap filenames, artifact names, commands, config paths, and other literal file-or-command references in backticks.
- Examples that should stay backticked: `spec.md`, `tasks.drift.md`, `canon.drift.md`, `.specify/extensions/canon/canon-config.yml`, and `/speckit.canon.drift`.
- If a prefixed identifier appears inside a larger inline code example or fenced code block, keep the code example intact; do not add extra identifier-only backticks in surrounding prose.

## Marked Local Overlays

For regular preset core command overrides that still track upstream `spec-kit`
command bodies, wrap local overlay blocks in named HTML comment markers:

```md
<!-- spec-kit-canon:start <name> -->
...
<!-- spec-kit-canon:end <name> -->
```

Use these markers only for the regular upstream-tracking preset command
overlays in `preset/commands/` when the underlying command body still comes
primarily from the upstream `spec-kit` repository and this repo adds local
overlay behavior on top of it.

Mark coherent local overlay blocks such as:

- inserted `## Pre-conditions` sections
- canon-specific guidance blocks
- local workflow constraints or exceptions that do not exist upstream

Do not try to mark routine preset normalization line by line. Leave these
unmarked unless they are part of a larger coherent overlay block:

- `.specify/...` path rewrites
- preset script-path normalization in frontmatter
- `$ARGUMENTS` placeholder normalization

Do not use these markers in:

- `extension/commands/`
- canon-owned preset files
- `preset/templates/`
- special-case manual merges such as `preset/commands/speckit.constitution.md`
  and `preset/templates/constitution-template.md`

Those files are owned directly by this repo and should be edited directly
without overlay markers.

## Script Validation

Before reinstalling into a test project, validate bundled scripts locally. Use
the bash checks as the default documented path and the PowerShell parser check
when you specifically need the Windows variant.

### Bash

```bash
bash -n extension/scripts/bash/check-prerequisites.sh
```

### PowerShell Alternative

```powershell
$null = [System.Management.Automation.Language.Parser]::ParseFile(
  (Resolve-Path 'extension/scripts/powershell/check-prerequisites.ps1'),
  [ref]$null,
  [ref]$null
)
```

Add similar checks for other modified scripts as needed.

## Release Packaging

The release workflow builds two GitHub Release assets from the package roots:

- `spec-kit-canon-<tag>.zip` from `extension/`
- `spec-kit-canon-core-<tag>.zip` from `preset/`

Expected asset URLs:

- `https://github.com/maximiliamus/spec-kit-canon/releases/download/<tag>/spec-kit-canon-<tag>.zip`
- `https://github.com/maximiliamus/spec-kit-canon/releases/download/<tag>/spec-kit-canon-core-<tag>.zip`

Each ZIP is built so its package manifest sits at the archive root:

- `extension.yml` for the extension package
- `preset.yml` for the preset package

That is the shape required by the upstream Spec Kit installers for
`specify extension add --from ...` and `specify preset add --from ...`.

## Shared Agent Skills

The shared skill sources for this repo stay in:

```text
skills/bumping-spec-kit-canon-version
skills/testing-spec-kit-canon-extension
skills/syncing-spec-kit-canon-core-preset
```

These skills are shared for any agent. The shared workflows, prompts, scripts,
references, and template assets live under those shared skill folders.
Project-local entrypoints and shortcuts live in agent-specific repo folders:

```text
.claude/skills/bumping-spec-kit-canon-version/SKILL.md
.claude/commands/bump-spec-kit-canon-version.md
.codex/prompts/bumping-spec-kit-canon-version.md
.claude/skills/testing-spec-kit-canon-extension/SKILL.md
.claude/commands/test-spec-kit-canon-extension.md
.codex/prompts/testing-spec-kit-canon-extension.md
.claude/skills/syncing-spec-kit-canon-core-preset/SKILL.md
.claude/commands/sync-spec-kit-canon-core-preset.md
.codex/prompts/syncing-spec-kit-canon-core-preset.md
```

The testing workflow stores resumable run state in:

```text
../spec-kit-canon-test/.specify/tmp/testing-spec-kit-canon-extension-progress.json
```

Initialize or reset that state with
`skills/testing-spec-kit-canon-extension/scripts/manage_progress.py`.
Use `--clear-test-project` there when the next run should fully wipe
`spec-kit-canon-test` before reinstalling the extension and preset.

For any agent that has these repo-local skills available, the normal way to
start the shared workflows is simply to ask:

- `Let's test the extension`
- `Let's bump extension version`
- `Let's sync preset`

After the repo-local skills are available, those prompts are enough to start
the corresponding workflows. For the version bump workflow, the default bump is
the next minor version. Ask for `major` or `patch` only when that exact bump is
intended, and provide an exact version only when you explicitly want to pin it.
That workflow also updates `CHANGELOG.md` automatically from local git history
unless you explicitly ask to skip it. Use explicit flags only when needed, for
example when you want to force a fresh test run or validate the PowerShell
script column.

Codex uses a global skill registry. Register or unregister the repo-local skill
sources with the scripts in `.codex`.

### Bash

```bash
bash .codex/register-skills.sh
bash .codex/unregister-skills.sh
```

### PowerShell Alternative

```powershell
pwsh -NoProfile -File .codex/register-skills.ps1
pwsh -NoProfile -File .codex/unregister-skills.ps1
```

## Identifier Prefix Reference

The tables below summarize the identifier families used by original Spec Kit
and by the canon extension workflows in this repository.

### Original Spec Kit Prefixes

| Prefix | Used for | Typical artifact or context | Notes |
| --- | --- | --- | --- |
| `FR-###` | Functional requirement identifiers | `spec.md` | Example: `FR-001`. |
| `SC-###` | Success criteria identifiers | `spec.md` | Example: `SC-001`. |
| `CHK###` | Checklist item identifiers | Checklist files | Example: `CHK001`. No hyphen. |
| `T###` | Implementation task identifiers | `tasks.md` | Example: `T001`. No hyphen. |
| `US#` | User story labels | `tasks.md`, task-generation guidance | Example: `US1`. Story grouping label, not a standalone task ID. |
| `Q#` | Question labels | Clarification and checklist questioning flows | Example: `Q1`. Used for interactive prompts. |
| `A#` | Analysis finding labels | Compact analysis reports | Example: `A1`. Used in report output, not feature artifacts. |

### Canon Extension Prefixes

| Prefix | Used for | Typical artifact or context | Notes |
| --- | --- | --- | --- |
| `TD-###` | Task drift item identifiers | `tasks.drift.md` | Example: `TD-001`. |
| `SD-###` | Spec drift finding identifiers | `spec.drift.md` | Example: `SD-001`. |
| `TA-###` | Deferred alignment task identifiers | `tasks.alignment.md` | Example: `TA-001`. |
| `CD-###` | Canon drift entry identifiers | `canon.drift.md` | Example: `CD-001`. |
| `CR-###` | Canon remediation item identifiers | `speckit.canon.drift-analyze` report output | Example: `CR-001`. Zero-padded. |

Note: bare `C-XXX` is reserved for future native canon entry references that
may later be cited directly from specs or other canon-aware artifacts.
