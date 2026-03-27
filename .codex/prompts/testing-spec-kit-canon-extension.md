# Testing Spec-Kit Canon Extension

Use `$testing-spec-kit-canon-extension`.

Supported command flags:

- `--script sh`
- `--script ps`
- `--restart`

Default behavior:

- continue the existing workflow when the saved progress is not complete
- restart from scratch automatically when the saved workflow is already complete
- restart from scratch immediately when `--restart` is passed

Pass any provided flags through to the shared skill and let the skill prepare
the workflow state before executing the current step.

If the skill is not registered yet, run the bash helper by default:

```bash
bash .codex/register-skill.sh
```

PowerShell alternative:

```powershell
pwsh -NoProfile -File .codex/register-skill.ps1
```

After that, use `$testing-spec-kit-canon-extension`.

Do not duplicate the workflow in this prompt file.
