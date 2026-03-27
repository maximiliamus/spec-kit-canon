# Codex Integration

This folder contains repo-local helpers for Codex.

## Registered Skills

The registration scripts manage every repo-local skill under `skills/`.

Current shared skill sources:

- `skills/testing-spec-kit-canon-extension`
- `skills/updating-spec-kit-canon-core-presets`

They link each repo skill source into the Codex skill registry under:

```text
$CODEX_HOME/skills/<skill-name>
```

If `CODEX_HOME` is unset, the scripts default to:

```text
~/.codex/skills/<skill-name>
```

## Register

Bash:

```bash
bash .codex/register-skills.sh
```

PowerShell:

```powershell
pwsh -NoProfile -File .codex/register-skills.ps1
```

Behavior:

- creates the Codex skills directory if needed
- registers each repo-local skill under its canonical name
- leaves the registration unchanged if it already points at this repo
- replaces an existing target only when the script allows it

On PowerShell, use `-Force` if the target path already exists and must be replaced:

```powershell
pwsh -NoProfile -File .codex/register-skills.ps1 -Force
```

## Unregister

Bash:

```bash
bash .codex/unregister-skills.sh
```

PowerShell:

```powershell
pwsh -NoProfile -File .codex/unregister-skills.ps1
```

Behavior:

- removes each registered skill only if it matches this repo-linked entry
- refuses to remove an unexpected target unless PowerShell `-Force` is used
- reports success when the skill is already absent

PowerShell force removal:

```powershell
pwsh -NoProfile -File .codex/unregister-skills.ps1 -Force
```

## Prompt Shortcuts

The Codex prompt entrypoints for this repo are:

```text
.codex/prompts/testing-spec-kit-canon-extension.md
.codex/prompts/updating-spec-kit-canon-core-presets.md
```

Those prompts should stay thin and point back to the shared skills instead of
duplicating the workflows.
