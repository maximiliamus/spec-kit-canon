---
name: committing-bulk-modifications
description: Group already-staged files from a bulk operation into meaningful commits and propose the message and file list for each commit. Use when a large batch of staged changes spans multiple logical concerns and must be split into well-scoped conventional commits before pushing. Only staged files are considered — unstaged changes are ignored.
---

# Committing Bulk Modifications

Use this skill when many files have already been staged at once — for example
after a preset sync, a version bump across multiple manifests, or a large
refactor — and the staged changes must be split into focused, logically
coherent commits rather than pushed as a single undifferentiated blob.

**Only staged files are in scope.** Unstaged changes in the working tree are
not considered and must not be included in any commit.

## Workflow

1. **Inspect the staging area.**
   Run `git diff --cached --stat` to list every staged file and understand
   the overall scope. Ignore anything that appears only in `git status` as
   unstaged.

2. **Group files by logical concern.**
   Cluster the files into candidate commit groups. Each group must represent a
   single coherent change — for example: manifest bumps, changelog updates,
   documentation fixes, script changes, test additions. Do not mix unrelated
   concerns in one group.

3. **Draft a commit plan.**
   For each group, produce:
   - the **files** that belong to it (relative paths)
   - a **commit message** in Conventional Commits format

   Only output the plan — do **not** run `git add` or `git commit` unless
   explicitly asked.

4. **Apply the commit plan** (only when asked).
   Commit each group in dependency order — foundational changes (build config,
   manifests) before derived changes (docs, changelogs). Use `git restore
   --staged` to temporarily unstage files that belong to later commits, commit
   the current group, then re-stage them:

   ```bash
   # Unstage files not in this commit
   git restore --staged <other-files...>

   # Commit only the files for this group (already staged)
   git commit -m "<subject>" -m "<body>"

   # Re-stage files for subsequent commits
   git add <other-files...>
   ```

   Never run `git add` on files that were not already staged before this
   skill was invoked.

## Commit Message Rules

- Use **Conventional Commits** format: `<type>(<scope>): <subject>`
  - Common types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`
  - Scope is optional but recommended when it narrows the change clearly
- Write the subject as a **complete, syntactically correct English sentence**
  ending with a period only when required for clarity; keep it under 72
  characters.
- Add a **body** when the subject alone does not explain the motivation or
  impact. Separate body from subject with a blank line.
- Use **ASCII only** — no Unicode characters, emoji, or curly quotes.

## Example Plan Output

```
Commit 1 — manifest version bump
  Files: extension/extension.yml, preset/preset.yml
  Message: chore(release): bump version to 0.4.0

Commit 2 — release documentation
  Files: docs/INSTALL.md, docs/UPGRADE.md, README.md
  Message: docs(release): update pinned release commands and badge for 0.4.0

Commit 3 — changelog
  Files: CHANGELOG.md
  Message: docs(changelog): add 0.4.0 release notes
```
