---
name: bumping-spec-kit-canon-version
description: Bump the shared release version in both publishable Spec Kit Canon manifests. Use when preparing the next release, aligning `extension/extension.yml` and `preset/preset.yml`, defaulting to the next minor version when the prompt just asks to bump the extension version, bumping only patch or major when that scope is explicitly requested, or applying an exact `X.Y.Z` or `vX.Y.Z` version only when the user explicitly asks for a specific version.
---

# Bumping Spec Kit Canon Version

Use this skill when one release version change must be applied to both
publishable package manifests and no broader release-preparation edits were
requested.

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
3. Run the bundled script from the repo root.

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

PowerShell alternative for the default bump:

```powershell
python skills/bumping-spec-kit-canon-version/scripts/set_manifest_versions.py
```

4. Verify both manifests now match:

```bash
rg -n '^  version: "' extension/extension.yml preset/preset.yml
```

## Rules

- Update only `extension/extension.yml` and `preset/preset.yml` unless the user
  explicitly asks for a wider release-preparation change.
- Keep the two manifest versions identical.
- Default to the next minor version when the prompt does not specify a bump
  type or an exact version.
- When bumping `major`, reset `minor` and `patch` to zero.
- When bumping `minor`, reset `patch` to zero.
- When bumping `patch`, increment only the patch component.
- Do not write the leading `v` into either manifest.
- If the user is preparing a publish, remind them that the release tag still
  needs the `v` prefix expected by `.github/workflows/release-packages.yml`.
- If the current manifest versions do not match and the user asks for a
  relative bump, stop and resolve that mismatch before guessing a base version.
- If an explicit version is requested and it is not valid semver, stop and ask
  for a corrected version instead of guessing.

## Resources

- `scripts/set_manifest_versions.py`: read the current manifest versions,
  default to the next minor version, support explicit patch or major bumps,
  accept an explicit version override, and report what changed.
