---
name: bumping-spec-kit-canon-version
description: Bump the shared release version in both publishable Spec Kit Canon manifests and automatically update the repo changelog. Use when preparing the next release, aligning `extension/extension.yml` and `preset/preset.yml`, defaulting to the next minor version when the prompt just asks to bump the extension version, bumping only patch or major when that scope is explicitly requested, or applying an exact `X.Y.Z` or `vX.Y.Z` version only when the user explicitly asks for a specific version.
---

# Bumping Spec Kit Canon Version

Use this skill when one release version change must be applied to both
publishable package manifests and the release changelog should be updated from
local git history in the same step.

## Workflow

1. Interpret the prompt using these defaults:
   - `Let's bump extension version` means bump the next minor version.
   - treat explicit type variants like `Let's bump extension version minor`,
     `Let's bump extension minor version`, `Let's bump extension patch version`,
     and `Let's bump extension major version` as the corresponding bump kind.
   - `Let's bump extension version to v1.2.3` means use that exact version.
2. Normalize an explicit version by stripping one leading `v` before writing
   the manifests. The release workflow expects tags like `v0.1.1`, but the
   manifests store `0.1.1`.
3. Run the bundled script from the repo root. By default it updates:
   - `extension/extension.yml`
   - `preset/preset.yml`
   - `CHANGELOG.md`
4. Generate the changelog deterministically from local git history using the
   Conventional Commits subjects:
   - resolve the previous reachable semver tag lower than the target version
   - collect rolling commit subjects from that tag to `HEAD`
   - group the matching Conventional Commit subjects by type into titled
     sections and list them under `CHANGELOG.md`
   - if there are no commits since the previous tag, write a short note
     instead of inventing entries

Default minor bump:

```bash
python skills/bumping-spec-kit-canon-version/scripts/set_manifest_versions.py
```

Explicit patch bump:

```bash
python skills/bumping-spec-kit-canon-version/scripts/set_manifest_versions.py --kind patch
```

Explicit major bump:

```bash
python skills/bumping-spec-kit-canon-version/scripts/set_manifest_versions.py --kind major
```

Exact version override:

```bash
python skills/bumping-spec-kit-canon-version/scripts/set_manifest_versions.py --version v0.1.1
```

Skip changelog generation only when explicitly requested:

```bash
python skills/bumping-spec-kit-canon-version/scripts/set_manifest_versions.py --skip-changelog
```

PowerShell alternative for the default bump:

```powershell
python skills/bumping-spec-kit-canon-version/scripts/set_manifest_versions.py
```

5. Verify the manifests and changelog:

```bash
rg -n '^  version: "' extension/extension.yml preset/preset.yml
rg -n '^## v' CHANGELOG.md
```

## Rules

- Update `extension/extension.yml`, `preset/preset.yml`, and `CHANGELOG.md` by
  default unless the user explicitly asks to skip the changelog.
- Keep the two manifest versions identical.
- Default to the next minor version when the prompt does not specify a bump
  type or an exact version.
- When bumping `major`, reset `minor` and `patch` to zero.
- When bumping `minor`, reset `patch` to zero.
- When bumping `patch`, increment only the patch component.
- Do not write the leading `v` into either manifest.
- If the user is preparing a publish, remind them that the release tag still
  needs the `v` prefix expected by `.github/workflows/release-packages.yml`.
- Generate changelog entries from git commit subjects, not invented summaries or
  GitHub release-note APIs.
- If the current manifest versions do not match and the user asks for a
  relative bump, stop and resolve that mismatch before guessing a base version.
- If an explicit version is requested and it is not valid semver, stop and ask
  for a corrected version instead of guessing.

## Resources

- `scripts/set_manifest_versions.py`: read the current manifest versions,
  default to the next minor version, support explicit patch or major bumps,
  accept an explicit version override, update `CHANGELOG.md` from local git
  history, and report what changed.
