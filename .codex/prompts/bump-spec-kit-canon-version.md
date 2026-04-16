# Bump Spec Kit Canon Version

Use `$bumping-spec-kit-canon-version`.

Default behavior:

- default to the next minor version
- bump `major` or `patch` only when explicitly requested
- accept an exact `0.1.1` or `v0.1.1` only when explicitly requested
- update `extension/extension.yml`, `preset/preset.yml`, `docs/INSTALL.md`, and `docs/UPGRADE.md`
- keep any documented base Spec Kit version aligned with `preset/spec-kit-release.json`
- update `CHANGELOG.md` automatically from local git history
- update `CHANGELOG.md` automatically from Conventional Commit subjects
- use `--kind patch|minor|major` for explicit relative bumps
- reset less significant components when bumping a more significant one
- write manifests without the `v` prefix when an exact tag-style version is provided
- allow `--skip-changelog` only when the user explicitly asks not to update it
- verify the manifests and changelog after the edit

Pass the requested bump intent through to the shared skill.

Accept natural phrasing like `bump extension version`, optional
`major`/`minor`/`patch`, or `to v1.2.3` for an exact version.

If the repo-local skills are not registered yet, run the bash helper by
default:

```bash
bash .codex/register-skills.sh
```

PowerShell alternative:

```powershell
pwsh -NoProfile -File .codex/register-skills.ps1
```

After that, use `$bumping-spec-kit-canon-version`.

Do not duplicate the workflow in this prompt file.
