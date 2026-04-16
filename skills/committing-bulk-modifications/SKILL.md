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
   Run `git diff --cached --name-status` to list every staged file with its
   change type (`M`, `A`, `D`, `R`). Note any rename entries (`R`) — these
   require special handling during application. Ignore anything that appears
   only in `git status` as unstaged.

2. **Group files by logical concern.**
   Cluster the files into candidate commit groups. Each group must represent a
   single coherent change — for example: manifest bumps, changelog updates,
   documentation fixes, script changes, test additions. Do not mix unrelated
   concerns in one group.

   When renames (`R`) are present, always keep both the old and new path of a
   rename in the same commit group. Never split a rename across groups.

3. **Draft a commit plan.**
   For each group, produce:
   - the **files** that belong to it (relative paths)
   - a **commit message** in Conventional Commits format

   Only output the plan — do **not** run `git add` or `git commit` unless
   explicitly asked.

4. **Apply the commit plan** (only when asked).
   Commit each group in dependency order — foundational changes (build config,
   manifests) before derived changes (docs, changelogs).

   **When no renames are present** — use `git restore --staged` to temporarily
   unstage files that belong to later commits, commit the current group, then
   re-stage them:

   ```bash
   # Unstage files not in this commit
   git restore --staged <other-files...>

   # Commit only the files for this group (already staged)
   git commit -m "<subject>"

   # Re-stage files for subsequent commits
   git add <other-files...>
   ```

   **When renames are present** — `git restore --staged` on a renamed file's
   old path breaks rename detection and splits it into separate add+delete
   entries, corrupting the commit. Use a full index reset instead:

   ```bash
   # Reset the entire index to HEAD (no working tree changes)
   git restore --staged .

   # Re-stage only the files for this commit group
   # (including both old and new paths for any renames in the group)
   git add <files-for-this-commit...>
   git add -u <deleted-old-paths-for-renames...>

   # Commit
   git commit -m "<subject>"

   # Repeat for each subsequent group
   ```

   Re-staging files that were originally staged is always permitted — the
   restriction is against pulling in files that were **not** staged before
   this skill was invoked.

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
