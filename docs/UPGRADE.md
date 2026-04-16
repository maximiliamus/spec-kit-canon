# Upgrade Spec Kit Canon

Use this sequence for an existing project:

1. Upgrade the global `specify` CLI.
2. Refresh the target project's core Spec Kit files.
3. Reinstall `canon` and `canon-core` from the same version.
4. Re-render the canon baseline with `/speckit.constitution`.

This keeps the base Spec Kit installation and the canon packages aligned.

## 1. Upgrade The Spec Kit CLI

```bash
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git@v0.6.1
```

## 2. Refresh The Target Project

Run `specify init --here --force` once for each AI integration you use in that
repository.

```bash
specify init --here --force --ai claude
specify init --here --force --ai gemini
specify init --here --force --ai copilot
specify init --here --force --ai qwen
specify init --here --force --ai codex --ai-skills
```

`specify init --here --force` can overwrite `.specify/memory/constitution.md`
and customized files under `.specify/templates/`, so back them up first if the
project already has local edits there.

## 3. Reinstall `canon` And `canon-core`

The safest upgrade path is to remove both packages and reinstall both from the
current published release.

```bash
specify extension remove canon --keep-config
specify preset remove canon-core
```

Install the current release assets:

```bash
specify extension add canon --from https://github.com/maximiliamus/spec-kit-canon/releases/download/v0.2.0/spec-kit-canon-v0.2.0.zip
specify preset add canon-core --from https://github.com/maximiliamus/spec-kit-canon/releases/download/v0.2.0/spec-kit-canon-core-v0.2.0.zip
```

`--keep-config` preserves `.specify/extensions/canon/canon-config.yml`.

## 4. Re-Render The Canon Baseline

After reinstalling both packages, run:

```text
/speckit.constitution
```

This repairs or re-renders the canon baseline and constitution from the
installed canon config.

## Optional: Refresh Agent Context Files

Reinstalling the extension and preset registers commands into detected agent
directories automatically. If you also want to refresh the agent context files
for all existing providers in the project, run one of the installed updater
scripts:

```bash
bash .specify/extensions/canon/scripts/bash/update-agent-context.sh
```

PowerShell alternative:

```powershell
pwsh -NoProfile -File .specify/extensions/canon/scripts/powershell/update-agent-context.ps1
```

These scripts update all existing agent context files in the repository. If no
agent files exist yet, they create the default Claude file.

## Related Docs

- [README.md](./README.md)
- [INSTALL.md](./INSTALL.md)
- [extension/scripts/powershell/update-agent-context.ps1](./extension/scripts/powershell/update-agent-context.ps1)
- [extension/scripts/bash/update-agent-context.sh](./extension/scripts/bash/update-agent-context.sh)
