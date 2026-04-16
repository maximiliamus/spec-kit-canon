# Commit Bulk Modifications

Use the Claude skill at `.claude/skills/committing-bulk-modifications`.

Default behavior:

- inspect only staged files with `git diff --cached --stat`
- group staged files by logical concern into candidate commit groups
- propose a commit plan with message and file list for each group
- use Conventional Commits format for all messages
- do not run `git add` on any file that was not already staged
- use `git restore --staged` to temporarily unstage files when splitting
  staged changes across multiple commits
- apply the plan only when explicitly asked

Follow that skill exactly.

Do not duplicate the workflow in this command file.
