# Commit Bulk Modifications

Use `$committing-bulk-modifications`.

Default behavior:

- inspect only staged files with `git diff --cached --stat`
- group staged files by logical concern into candidate commit groups
- propose a commit plan with message and file list for each group
- use Conventional Commits format for all messages
- do not run `git add` on any file that was not already staged
- use `git restore --staged` to temporarily unstage files when splitting
  staged changes across multiple commits
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
