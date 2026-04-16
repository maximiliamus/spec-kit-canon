---
name: committing-bulk-modifications
description: Claude skill entrypoint for grouping staged files into meaningful conventional commits. Use when Claude needs to inspect the staging area, cluster staged files by logical concern, propose a commit plan with messages and file lists, and apply that plan one group at a time without staging anything that was not already staged.
---

# Committing Bulk Modifications

This is the Claude skill entrypoint for the shared skill source in
`skills/committing-bulk-modifications`.

Before doing any work:

1. Read `skills/committing-bulk-modifications/SKILL.md`.
2. Use `git diff --cached --stat` to inspect staged files — do not look at
   unstaged changes.
3. Only output a commit plan unless explicitly asked to apply it.

## Wrapper Rules

- Treat `skills/committing-bulk-modifications/SKILL.md` as the canonical
  workflow.
- Never run `git add` on files that were not already staged before the skill
  was invoked. Re-staging originally-staged files during the split process is
  permitted.
- Use `git restore --staged` to temporarily move files out of the index when
  splitting staged changes across multiple commits — **except** when the
  staging area contains renames. In that case, reset the entire index with
  `git restore --staged .` and re-stage each group from scratch to avoid
  breaking rename detection.
- Do not duplicate the commit workflow in this entrypoint.
