# Update Spec-Kit Canon Core Presets

Use `$updating-spec-kit-canon-core-presets`.

Default behavior:

- verify the latest upstream release tag against `../spec-kit` `origin`
- fetch the release tag locally if it is missing
- export the upstream release snapshot before editing `preset/`
- rebase the seven regular command overlays and manually merge the constitution
  files

If the repo-local skills are not registered yet, run the bash helper by
default:

```bash
bash .codex/register-skills.sh
```

PowerShell alternative:

```powershell
pwsh -NoProfile -File .codex/register-skills.ps1
```

After that, use `$updating-spec-kit-canon-core-presets`.

Do not duplicate the workflow in this prompt file.
