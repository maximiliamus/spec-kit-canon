# Codex Integration

This folder contains repo-local helpers for Codex.

## Registered Skill

The registration scripts manage one Codex skill entry:

- `testing-spec-kit-canon-extension`

They link the repo skill source at:

```text
skills/testing-spec-kit-canon-extension
```

into the Codex skill registry under:

```text
$CODEX_HOME/skills/testing-spec-kit-canon-extension
```

If `CODEX_HOME` is unset, the scripts default to:

```text
~/.codex/skills/testing-spec-kit-canon-extension
```

## Register

Bash:

```bash
bash .codex/register-skill.sh
```

PowerShell:

```powershell
pwsh -NoProfile -File .codex/register-skill.ps1
```

Behavior:

- creates the Codex skills directory if needed
- registers the repo skill under the canonical name
- leaves the registration unchanged if it already points at this repo
- replaces an existing target only when the script allows it

On PowerShell, use `-Force` if the target path already exists and must be replaced:

```powershell
pwsh -NoProfile -File .codex/register-skill.ps1 -Force
```

## Unregister

Bash:

```bash
bash .codex/unregister-skill.sh
```

PowerShell:

```powershell
pwsh -NoProfile -File .codex/unregister-skill.ps1
```

Behavior:

- removes the registered skill only if it matches this repo-linked entry
- refuses to remove an unexpected target unless PowerShell `-Force` is used
- reports success when the skill is already absent

PowerShell force removal:

```powershell
pwsh -NoProfile -File .codex/unregister-skill.ps1 -Force
```

## Prompt Shortcut

The Codex prompt entrypoint for this repo is:

```text
.codex/prompts/testing-spec-kit-canon-extension.md
```

That prompt should stay thin and point back to the shared skill instead of
duplicating the workflow.
