# Spec Kit Canon Extension

This package is the `canon` extension for Spec Kit.

It adds the namespaced `speckit.canon.*` commands used for canon drift and
vibecoding workflows. For the full canon-driven core workflow, install the
companion `canon-core` preset from the same repository.

## Install

Install from a release asset:

```bash
specify extension add canon --from https://github.com/maximiliamus/spec-kit-canon/releases/download/<tag>/spec-kit-canon-<tag>.zip
```

Install from a local checkout:

```bash
specify extension add --dev /path/to/spec-kit-canon/extension
```

Install the companion preset for the full workflow:

```bash
specify preset add canon-core --from https://github.com/maximiliamus/spec-kit-canon/releases/download/<tag>/spec-kit-canon-core-<tag>.zip
```

## Commands

- `speckit.canon.drift`
- `speckit.canon.drift-analyze`
- `speckit.canon.drift-canonize`
- `speckit.canon.drift-detect`
- `speckit.canon.drift-implement`
- `speckit.canon.drift-reconcile`
- `speckit.canon.drift-resolve`
- `speckit.canon.drift-reverse`
- `speckit.canon.vibecode-drift`
- `speckit.canon.vibecode-drift-analyze`
- `speckit.canon.vibecode-drift-canonize`
- `speckit.canon.vibecode-drift-detect`
- `speckit.canon.vibecode-drift-express`
- `speckit.canon.vibecode-drift-reconcile`
- `speckit.canon.vibecode-drift-reverse`
- `speckit.canon.vibecode-specify`

See the repository root [README.md](../README.md) for the combined extension +
preset workflow guide. For a more focused reference on workflows, step
commands, and command behavior, see [WORKFLOWS.md](../WORKFLOWS.md). The
end-to-end orchestrator commands are documented in
[WORKFLOW-ORCHESTRATORS.md](../WORKFLOW-ORCHESTRATORS.md).
