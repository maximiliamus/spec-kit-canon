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
This is Spec Kit Canon-related functionality, not behavior inherited from the
current upstream `spec-kit` sources.

More specifically, the implementation currently lives in the `canon-core`
preset rather than in the `canon` extension package itself.

- `/speckit.constitution` in `preset/commands/speckit.constitution.md` loads
  the bundled `preset/templates/root-gitattributes-template.txt`
- it initializes or repairs the target project's repo-root `.gitattributes`
- it keeps text files LF by default while preserving CRLF for PowerShell and
  batch entrypoints

The purpose is cross-shell stability, especially on Windows. Without that
bootstrap, Git may follow machine-specific defaults such as `core.autocrlf`,
which can create noisy diffs, false drift, and file-flipping between bash and
PowerShell workflows.

---

Q:
Why does the extension bundle local scripts such as
`check-prerequisites.sh` and `update-agent-context.sh` instead of always
calling the original Spec Kit scripts under `.specify/scripts/`?

A:
Because those two cases are different, and the extension needs to stay
self-contained when installed under `.specify/extensions/canon/`.

- `check-prerequisites.*` is extension-owned logic. It is not just a copy
  of a core Spec Kit script. It adds canon-specific artifact handling such as
  `canon.drift.md`, `CANON_ROOT`, and `CANON_TOC`.
- `update-agent-context.*` is closer to a fork of the upstream Spec Kit script.
  The extension keeps a local copy because the canon workflows currently depend
  on behavior that is not safely interchangeable with the upstream version.
- The main example is the vibecoding workflow. The canon vibecoding workflow intentionally does
  not keep `plan.md`, but the extension-local updater tolerates missing
  `plan.md` while the current upstream updater treats it as an error.
- The extension also carries local helper-script behavior that does not match
  upstream exactly on every platform yet, especially in the PowerShell
  `common.ps1` path-resolution flow.

So yes, some extension scripts are copies or forks of core scripts, but they
are kept locally on purpose. The extension can reference core scripts only when
the required behavior is truly identical. Today that is not yet true for the
agent-context update path.

The long-term cleanup target is still to remove unnecessary forks. Once the
upstream script behavior matches the canon workflow requirements, the extension
can switch to `.specify/scripts/...` and delete the local copy.

---

Q:
Why doesn’t Spec Kit Canon add a separate automatic drift-resolve command?

A:
Because automatic resolve is a policy choice inside the existing standard
drift workflow, not a separate artifact pipeline.

- `/speckit.canon.drift` stays the standard orchestrator
- `/speckit.canon.drift-resolve` stays the standard resolve step
- manual resolve remains the default behavior
- explicit user input such as `fully autonomous`,
  `autonomous resolve`, or `implementation authoritative` switches resolve into
  implementation-authoritative automatic mode

Keeping one command pair avoids duplicating the standard drift documentation,
handoff logic, and artifacts.

The only hard boundary is `tasks.alignment.md`: if that file already exists,
automatic mode is blocked for the feature branch. At that point the branch is
already on the manual spec-authoritative alignment path, so you should either
finish that cycle or delete the artifact and restart drift from scratch.
