# Development

This repository is developed and tested against a local checkout of the
original Spec Kit repository.

## Minimum Workspace Layout

At minimum, keep both repositories in the same workspace:

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

- Python 3.11+
- `uv`
- Git
- A test Spec Kit project where the extension and preset can be installed

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

This verifies the local CLI environment is usable.

### 2. Create or reuse a test project

Recommended test project: `../spec-kit-canon-test`

From that sandbox project directory:

```bash
uv run --project ../spec-kit specify init . --ai codex --force
```

If you prefer, run the same command from inside the `spec-kit` repo and point
it at the target project directory explicitly.

### 3. Install this extension and preset from source

From `../spec-kit-canon-test`:

```bash
uv run --project ../spec-kit specify extension add --dev ../spec-kit-canon
uv run --project ../spec-kit specify preset add --dev ../spec-kit-canon/presets/canon-core
```

Use only the extension install if you are testing `speckit.canon.*` commands
without the core-command overrides.

### 4. Reinstall after changes

Re-run the relevant `specify ... add --dev` command after changing:

- `extension.yml`
- `preset.yml`
- command markdown files
- bundled templates
- bundled scripts
- `.extensionignore`

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

- `commands/`
- `templates/`
- `scripts/`
- `extension.yml`

Minimum test:

```bash
uv run --project ../spec-kit specify extension add --dev ../spec-kit-canon
```

Then exercise the affected `speckit.canon.*` command in a test project.

### Preset-only changes

Examples:

- `presets/canon-core/commands/`
- `presets/canon-core/templates/`
- `presets/canon-core/preset.yml`

Minimum test:

```bash
uv run --project ../spec-kit specify preset add --dev ../spec-kit-canon/presets/canon-core
```

Then exercise the affected core command override in a test project.

### Changes that depend on upstream CLI behavior

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

## Script Validation

Before reinstalling into a test project, validate bundled scripts locally. Use
the bash checks as the default documented path and the PowerShell parser check
when you specifically need the Windows variant.

For repo docs, skills, prompts, and other developer-facing examples, default
to bash-based script examples. Add PowerShell examples only as an explicit
alternative or when the Windows-specific variant is the thing being discussed.

### Bash

```bash
bash -n scripts/bash/check-drift-prerequisites.sh
```

### PowerShell Alternative

```powershell
$null = [System.Management.Automation.Language.Parser]::ParseFile(
  (Resolve-Path 'scripts/powershell/check-drift-prerequisites.ps1'),
  [ref]$null,
  [ref]$null
)
```

Add similar checks for other modified scripts as needed.

## Recommended Rule

If a change touches anything that depends on how Spec Kit installs, resolves,
or executes extensions and presets, treat `../spec-kit` as required, not
optional.

All test steps that work with `/speckit.*` commands must not take longer than
5-10 minutes. If a step trends longer than that, tighten the prompt boundaries or
reduce scope before treating the workflow as acceptable.

## Shared Agent Skills

The shared skill sources for this repo stay in:

```text
skills/testing-spec-kit-canon-extension
skills/updating-spec-kit-canon-core-presets
```

These skills are not Codex-specific. The shared workflows, prompts, scripts,
references, and template assets live under those shared skill folders.
Project-local entrypoints and shortcuts live in agent-specific repo folders:

```text
.claude/skills/testing-spec-kit-canon-extension/SKILL.md
.claude/commands/test-spec-kit-canon-extension.md
.codex/prompts/testing-spec-kit-canon-extension.md
.claude/skills/updating-spec-kit-canon-core-presets/SKILL.md
.claude/commands/update-spec-kit-canon-core-presets.md
.codex/prompts/updating-spec-kit-canon-core-presets.md
```

The agent entrypoints stay thin and should only point at the shared material.
The Claude commands and Codex prompts are only shortcuts that invoke the actual
skills.

The testing workflow stores resumable run state in:

```text
../spec-kit-canon-test/.specify/tmp/testing-spec-kit-canon-extension-progress.json
```

Initialize or reset that state with `skills/testing-spec-kit-canon-extension/scripts/manage_progress.py`.
Use `--clear-test-project` there when the next run should fully wipe
`spec-kit-canon-test` before reinstalling the extension and preset.

Copilot is intentionally not part of this setup.

Codex uses a global skill registry. Register or unregister the repo-local skill
sources with the scripts in `.codex`. Use the bash helpers by default:

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

These scripts keep the repository as the single source of truth for the shared
skill sources while creating or removing the Codex registry entries.
