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
- require code changes in places that already expect canon-config.yml, such as check-drift-prerequisites.ps1

So this is mostly convention plus compatibility, not just style.

---
