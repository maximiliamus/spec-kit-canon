# Development

This repository is developed and tested against a local checkout of the
upstream `spec-kit` repository.

## Package Layout

The monorepo keeps the two publishable packages in separate first-level
directories:

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
bash -n extension/scripts/bash/check-drift-prerequisites.sh
```

### PowerShell Alternative

```powershell
$null = [System.Management.Automation.Language.Parser]::ParseFile(
  (Resolve-Path 'extension/scripts/powershell/check-drift-prerequisites.ps1'),
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
skills/testing-spec-kit-canon-extension
skills/syncing-spec-kit-canon-core-preset
```

These skills are not Codex-specific. The shared workflows, prompts, scripts,
references, and template assets live under those shared skill folders.
Project-local entrypoints and shortcuts live in agent-specific repo folders:

```text
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
start the shared extension test workflow is simply to ask:
`Let's test the extension`.

After the repo-local skills are available, that prompt is enough to start the
dedicated testing workflow and wait for it to complete. Use explicit flags only
when needed, for example when you want to force a fresh run or validate the
PowerShell script column.

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
