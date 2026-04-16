# Commit Bulk Modifications

Use `$committing-bulk-modifications`.

Default behavior:

- inspect only staged files with `git diff --cached --name-status` to capture
  change types, including renames (`R`)
- group staged files by logical concern into candidate commit groups; always
  keep both paths of a rename in the same group
- propose a commit plan with message and file list for each group
- use Conventional Commits format for all messages
- do not run `git add` on any file that was not already staged; re-staging
  originally-staged files during the split process is permitted
- when no renames are present, use `git restore --staged` to temporarily
  unstage files not in the current commit group
- when renames are present, reset the entire index with
  `git restore --staged .` and re-stage each group from scratch to avoid
  breaking rename detection
- apply the plan only when explicitly asked

If the repo-local skills are not registered yet, run the bash helper by
default:

```bash
bash .codex/register-skills.sh
```

PowerShell alternative:

```powershell
pwsh -NoProfile -File .codex/register-skills.ps1
```

After that, use `$committing-bulk-modifications`.

Do not duplicate the workflow in this prompt file.
