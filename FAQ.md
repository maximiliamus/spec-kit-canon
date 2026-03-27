# FAQ

Q:
Why in the presets folder a folder named canon-core not just canon.

A:
Because this repo ships two different packages with different roles:

The extension is the main canon package. Its id is canon in extension.yml (line 4), and it owns the speckit.canon.* command namespace plus .specify/extensions/canon/....
The preset is optional and only overrides core speckit.* commands. Its id is canon-core in preset.yml (line 4), and its README explicitly describes it as “Canon Core Overrides” in README.md (line 1).
So canon-core means “the canon-flavored preset for core commands,” not “the canon extension itself.” If the preset folder/id were just canon, it would blur the distinction between:

extension package: canon
preset package: canon-core
That separation is also reflected in the top-level docs: the repo has “a Spec-Kit extension for speckit.canon.* commands” and “an optional preset for overriding core speckit.* commands” in README.md (line 3).

One small inference from that structure: the -core suffix also leaves room for additional canon-related presets later, without colliding with the main extension name.

---

Q:
Why config file named canon-config, not just config?

A:
Because Spec-Kit’s extension system is built around extension-specific config filenames, not a generic shared config.yml.

The rule in upstream docs is .specify/extensions/{extension-id}/{extension-id}-config.yml, shown in EXTENSION-API-REFERENCE.md and reinforced in the naming guidance in EXTENSION-DEVELOPMENT-GUIDE.md. The runtime loader also reads exactly f"{extension_id}-config.yml" in extensions.py.

So for extension id canon, the expected file is canon-config.yml. Using just config.yml would:

- break the upstream convention
- make the file less self-describing inside .specify/extensions/canon/
- require code changes in places that already expect canon-config.yml, such as `check-drift-prerequisites.sh` and its PowerShell counterpart

So this is mostly convention plus compatibility, not just style.

---

Q: Explain functionality related to gitattributes.

A:
The `gitattributes` functionality here is bootstrap-and-repair logic for projects that use the `canon-core` preset.

- The rule is defined in the `speckit.constitution` prompt, not in a separate script. That prompt explicitly tells the agent to load the bundled `.gitattributes` template, create the repo-root `.gitattributes` if it is missing, repair it if it drifted, and treat a bad line-ending policy as project drift that must be fixed before continuing. See speckit.constitution.md, speckit.constitution.md, speckit.constitution.md, speckit.constitution.md, speckit.constitution.md, speckit.constitution.md.

- The bundled template is root-gitattributes-template.txt. Its policy is simple:
  - `* text=auto eol=lf`: general text files normalize to LF.
  - `*.ps1`, `*.psm1`, `*.psd1`, `*.bat`, `*.cmd`: PowerShell and batch entrypoints stay CRLF.

- The purpose is Windows cross-shell stability. This repo uses both bash and PowerShell, and the prompt explicitly says the template exists so both shells see the same clean Git working tree. Without that, line-ending-only changes can make `git status` and `git diff` noisy and interfere with drift workflows. The test workflow treats this as a required verification point and specifically checks that `.gitattributes` exists and that `bash -lc 'git status --short'` stays clean before feature work. See test-flow.md.

- The repo also dogfoods the same policy in its own root file: .gitattributes matches the bundled template exactly.

The main nuance is that this is prompt-driven behavior. There is no dedicated enforcement script in this repo; `/speckit.constitution` is expected to perform the create/repair step when the preset is installed in a target project.

Cross-shell stability means the repo behaves the same whether commands are run from bash or PowerShell, especially on Windows.

In this repo, that mostly means line endings stay predictable:
- general text files use LF
- PowerShell and batch entrypoints use CRLF

That policy is defined in root-gitattributes-template.txt and enforced by the `/speckit.constitution` workflow in speckit.constitution.md.

Without this functionality, Git falls back to each machine's global settings like `core.autocrlf`. Then behavior becomes machine-specific. Typical problems are:
- `git status` shows lots of modified files even when content did not really change
- `git diff` shows line-ending-only noise
- bash-based drift checks treat false file changes as real drift
- switching between bash and PowerShell can keep flipping files back and forth
- commits may contain useless CRLF/LF churn

So it does not add product behavior. It prevents false modifications and flaky workflow behavior.