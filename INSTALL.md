# Install Spec Kit Canon

Spec Kit Canon ships as two packages that are usually installed together:

- `canon` extension: adds the namespaced `speckit.canon.*` commands
- `canon-core` preset: adapts core `speckit.*` commands to the canon-driven workflow

Install both packages from the current published release:

```bash
specify extension add canon --from https://github.com/maximiliamus/spec-kit-canon/releases/download/v0.2.0/spec-kit-canon-v0.2.0.zip
specify preset add canon-core --from https://github.com/maximiliamus/spec-kit-canon/releases/download/v0.2.0/spec-kit-canon-core-v0.2.0.zip
```

## Extension-Only Install

If you install only the extension, you get the namespaced
`/speckit.canon.*` commands, but not the canon-driven overrides for the core
`/speckit.*` workflow.

```bash
specify extension add canon --from https://github.com/maximiliamus/spec-kit-canon/releases/download/v0.2.0/spec-kit-canon-v0.2.0.zip
```

## Next Step

After installation, configure `.specify/extensions/canon/canon-config.yml` and
run:

```text
/speckit.constitution
```

The full setup and workflow guide is in [README.md](./README.md). For existing
projects, use the release upgrade flow in [UPGRADE.md](./UPGRADE.md). For local
development installs, see [DEVELOPMENT.md](./DEVELOPMENT.md).

## Related Docs

- [README.md](./README.md)
- [UPGRADE.md](./UPGRADE.md)
