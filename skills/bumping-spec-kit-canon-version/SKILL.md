---
name: bumping-spec-kit-canon-version
description: Bump the shared release version in both publishable Spec Kit Canon manifests, update the version-pinned release commands in `INSTALL.md` and `UPGRADE.md`, keep any documented base Spec Kit version in sync with `preset/spec-kit-release.json`, and automatically update the repo changelog. Use when preparing the next release, aligning `extension/extension.yml` and `preset/preset.yml`, defaulting to the next minor version when the prompt just asks to bump the extension version, bumping only patch or major when that scope is explicitly requested, or applying an exact `X.Y.Z` or `vX.Y.Z` version only when the user explicitly asks for a specific version.
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
   - `INSTALL.md`
   - `UPGRADE.md`
   - the Spec Kit version badge in `README.md`, using
     `preset/spec-kit-release.json`
   - `CHANGELOG.md`
4. Generate the changelog deterministically from local git history using the
   Conventional Commits subjects:
   - resolve the previous reachable semver tag lower than the target version
   - collect rolling commit subjects from that tag to `HEAD`
   - group the matching Conventional Commit subjects by type into titled
     sections and list them under `CHANGELOG.md`
   - format each release heading as `## [X.Y.Z] - YYYY-MM-DD` to match
     Keep a Changelog
   - prepend the new entry after the file header, before any existing sections,
     so the changelog is in reverse chronological order (newest release first)
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

5. Verify the manifests, pinned release docs, readme badge, and changelog:

```bash
rg -n '^  version: "' extension/extension.yml preset/preset.yml
rg -n 'spec-kit-canon-v|spec-kit-canon-core-v' INSTALL.md UPGRADE.md
rg -n 'spec--kit-v' README.md
rg -n '^## \\[[0-9]+\\.[0-9]+\\.[0-9]+\\] - ' CHANGELOG.md
```

6. Confirm each output matches expectations and report success or failure:

- **Manifests**: both `extension/extension.yml` and `preset/preset.yml` must
  show `version: "<new_version>"` — if either is missing or still shows the
  old version, the bump failed; stop and report which manifest was not updated.
- **Release docs**: `INSTALL.md` and `UPGRADE.md` must contain release URLs
  ending in the new version tag (`v<new_version>`) — if no matches are found,
  the pinned commands were not updated; stop and report.
- **README badge**: `README.md` must contain the Spec Kit badge with the tag
  from `preset/spec-kit-release.json`, i.e.
  `spec--kit-v<spec_kit_tag>` in the badge URL — if the badge is missing or
  still shows an old tag, stop and report the exact line found and the
  expected tag.
- **Changelog**: `CHANGELOG.md` must have a section heading for the new
  version in the form `## [<new_version>] - YYYY-MM-DD` — if absent, stop and
  report.
- Only report success once all four checks pass. If any check fails, do not
  report the overall bump as complete.

## Rules

- Update `extension/extension.yml`, `preset/preset.yml`, `INSTALL.md`,
  `UPGRADE.md`, and the Spec Kit version badge in `README.md` by default, keep
  the Spec Kit version badge aligned with `preset/spec-kit-release.json`, plus
  update `CHANGELOG.md` unless the user explicitly asks to skip the changelog.
- Keep the two manifest versions identical.
- Default to the next minor version when the prompt does not specify a bump
  type or an exact version.
- When bumping `major`, reset `minor` and `patch` to zero.
- When bumping `minor`, reset `patch` to zero.
- When bumping `patch`, increment only the patch component.
- Do not write the leading `v` into either manifest.
- If the user is preparing a publish, remind them that the release tag still
  needs the `v` prefix expected by `.github/workflows/release-packages.yml`.
- Do not guess the base Spec Kit version for the badge or docs; read it from
  `preset/spec-kit-release.json` `spec_kit_release.resolved_tag`.
- Generate changelog entries from git commit subjects, not invented summaries or
  GitHub release-note APIs.
- Do not include a commit count footer (e.g. `*Total: N commit(s)*`) in changelog entries.
- Use square-bracketed Keep a Changelog release headings in the form
  `## [X.Y.Z] - YYYY-MM-DD`.
- Always prepend new changelog entries after the file header so the changelog
  remains in reverse chronological order (newest release first).
- If the current manifest versions do not match and the user asks for a
  relative bump, stop and resolve that mismatch before guessing a base version.
- If an explicit version is requested and it is not valid semver, stop and ask
  for a corrected version instead of guessing.

## Resources

- `scripts/set_manifest_versions.py`: read the current manifest versions,
  default to the next minor version, support explicit patch or major bumps,
  accept an explicit version override, update `INSTALL.md` and `UPGRADE.md`
  release commands to the same version, update the Spec Kit version badge in
  `README.md` from `preset/spec-kit-release.json`, update `CHANGELOG.md` from
  local git history, and report what changed.
