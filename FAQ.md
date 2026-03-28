# FAQ

Q:
Why is the preset named `canon-core` instead of just `canon`?

A:
Because this repo ships two different packages with different roles.

- the extension package id is `canon` in `extension/extension.yml`
- the preset package id is `canon-core` in `preset/preset.yml`

So `canon-core` means "the canon-flavored preset for core commands," not "the
canon extension itself." If both packages used `canon`, the distinction between
the namespaced extension commands and the core-command overrides would be
needlessly blurred.

---

Q:
Why is the config file named `canon-config.yml`, not just `config.yml`?

A:
Because Spec Kit’s extension system uses extension-specific config filenames.

For extension id `canon`, the expected project config file is:

```text
.specify/extensions/canon/canon-config.yml
```

Using a generic `config.yml` would break the upstream naming convention and the
repo logic that already expects `canon-config.yml`, including the drift
prerequisite scripts.

---

Q:
Explain the `.gitattributes` functionality.

A:
The `.gitattributes` behavior is part of the `canon-core` preset bootstrap and
repair logic.

- `/speckit.constitution` loads the preset's bundled
  `root-gitattributes-template.txt`
- it creates or repairs the target project's repo-root `.gitattributes`
- it keeps text files LF by default while leaving PowerShell and batch
  entrypoints on CRLF

The purpose is cross-shell stability, especially on Windows. Without that
bootstrap, Git may follow machine-specific defaults such as `core.autocrlf`,
which can create noisy diffs, false drift, and file-flipping between bash and
PowerShell workflows.
