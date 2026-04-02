# Workflow Orchestrators

`canon` provides orchestrator commands that drive the step commands in
[WORKFLOWS.md](./WORKFLOWS.md) end-to-end. This document covers those
orchestrators only; for the individual step commands, artifact formats, and
resolve/reconcile handoff semantics, see [WORKFLOWS.md](./WORKFLOWS.md). For
visual workflow maps, see [WORKFLOW-DIAGRAMS.md](./WORKFLOW-DIAGRAMS.md).

## Standard Spec-Drift Orchestrator

`speckit.canon.drift` is the full standard spec-first orchestrator for the
drift step commands. It runs reverse and detect as delegated autonomous steps.
Detect writes `spec.drift.md` with items automatically resolved into
`ACCEPTED`, `REJECTED`, and `UNRESOLVED` statuses.

Basic invocation:

```text
/speckit.canon.drift
```

Explicit automatic implementation-authoritative mode:

```text
/speckit.canon.drift "fully autonomous"
/speckit.canon.drift "auto"
```

`speckit.canon.drift` supports two orchestration modes:

- Default manual mode
- Explicit automatic implementation-authoritative mode, enabled only when user
  input clearly includes `auto`, `fully autonomous`, `autonomous resolve`,
  `automatic resolve`, `automatic mode`, `implementation authoritative`, or
  `implementation prevails`

`speckit.canon.drift-resolve` stays the manual decision-making and
re-verification step command. Zero-touch implementation-authoritative
resolution belongs only to the orchestrator.

### Manual Mode End-to-End Flow

1. **Reverse** — delegated run of `speckit.canon.drift-reverse`.
2. **Detect** — delegated run of `speckit.canon.drift-detect`. If detect finds
   only terminal `ACCEPTED` or `REJECTED` items, it writes
   `Resolution Status: resolved` with the Resolution table immediately and the
   orchestrator skips directly to reconcile. Otherwise detect leaves the file
   `unresolved`.
3. **Resolve** — `speckit.canon.drift-resolve` runs directly in the
   orchestrator (not as a delegated subagent) so user-facing prompts stay
   concentrated in one place. For each `UNRESOLVED` or `IMPL-REJECTED` item
   that needs user intent, the orchestrator asks the user, applies the answer,
   and continues in `spec.drift.md` order.
4. **Alignment cycle (conditional)** — if resolve creates
   `tasks.alignment.md`, the orchestrator runs `speckit.canon.drift-implement`
   once and then re-runs `speckit.canon.drift-resolve` once to verify the
   completed alignment work. This cycle runs at most once per orchestrator
   invocation.
5. **Resolve gate** — if `spec.drift.md` is still `unresolved` after the
   single alignment cycle (for example, because `IMPL-REJECTED` items still
   carry unchecked TA-XXX tasks), the orchestrator stops and reports the
   remaining work. `spec.drift.md` is left `unresolved` with its current
   item-level statuses so a follow-up manual run of
   `speckit.canon.drift-implement` and `speckit.canon.drift-resolve`, or a
   fresh `speckit.canon.drift` invocation, can resume from the same state.
6. **Reconcile** — delegated run of `speckit.canon.drift-reconcile`, only
   once `spec.drift.md` is fully `resolved`.
7. **Analyze** — `speckit.canon.drift-analyze` runs directly in the
   orchestrator and stays read-only. If it reports zero remediation items, the
   orchestrator continues to canonize. If it reports remediation items, the
   orchestrator asks the user whether to remediate now, continue with the
   current draft, or stop:
   - **remediate now** updates only `canon.drift.md` from the reported CR-XXX
     items and then re-runs analyze once for verification. If the verification
     pass is clean, the orchestrator continues to canonize; if remediation
     items still remain, it stops and preserves the revised draft canon plan
     for further manual review.
   - **continue with current draft** proceeds directly to canonize.
   - **stop** preserves the draft canon plan and ends the run.
8. **Canonize** — delegated run of `speckit.canon.drift-canonize`.

### Automatic Mode End-to-End Flow

Automatic mode refuses to start if `tasks.alignment.md` already exists for the
feature. Continue the manual alignment cycle to completion, or delete
`tasks.alignment.md` and restart the orchestrator from scratch.

1. **Reverse** and **Detect** — same delegated steps as manual mode.
2. **Resolve** — the orchestrator resolves `spec.drift.md` itself in a
   zero-touch implementation-authoritative pass. Every outstanding
   `UNRESOLVED` item becomes `IMPL-ACCEPTED`, implementation prevails spec, no
   implementation code is changed, and no `tasks.alignment.md` is created or
   updated. If a recovery edge case leaves `IMPL-REJECTED` items in
   `spec.drift.md` without an alignment file (for example, the file was
   deleted between runs), the orchestrator also promotes those items to
   `IMPL-ACCEPTED` in the same pass. `speckit.canon.drift-resolve` is never
   invoked in automatic mode.
3. **Reconcile** — delegated run of `speckit.canon.drift-reconcile`.
4. **Analyze** — `speckit.canon.drift-analyze` runs directly in the
   orchestrator and stays read-only. If it reports remediation items, the
   orchestrator applies every CR-XXX item to `canon.drift.md`, re-runs analyze
   once, and canonizes only if the verification pass is clean. If the
   verification pass still reports remediation items, the orchestrator stops
   with a report explaining the remaining issues and preserves the revised
   draft canon plan for manual review.
5. **Canonize** — delegated run of `speckit.canon.drift-canonize`.

## Vibecoding Spec-Drift Orchestrator

`speckit.canon.vibecode-drift` is the full vibecoding drift orchestrator for
the vibecoding step commands. It defaults to manual review mode and also
supports an explicit automatic remediation mode. It runs reverse, detect, and
reconcile automatically, then runs analyze as a read-only draft canon review
before canonize.

Basic invocation:

```text
/speckit.canon.vibecode-drift
```

Explicit automatic-remediation mode:

```text
/speckit.canon.vibecode-drift "fully autonomous"
/speckit.canon.vibecode-drift "auto"
```

In manual review mode, if analyze reports remediation items, the orchestrator
asks whether to remediate now, continue with the current draft, or stop. A
remediation choice updates only `canon.drift.md` from the reported CR-XXX
items, then re-runs analyze once for verification.

In explicit automatic mode, if analyze reports remediation items, the
orchestrator applies those CR-XXX items to `canon.drift.md`, re-runs analyze
once, and canonizes only if the verification pass is clean; otherwise it stops
with a report explaining the remaining issues. Use this command when you want
the full canon sync flow handled end to end.

## Vibecoding Express Fast Path

`speckit.canon.vibecode-drift-express` is the fast path for small, non-complex
changes. Invocation:

```text
/speckit.canon.vibecode-drift-express
``` Use it when you want a quick low-ceremony drift sync and the change
set is straightforward enough that you do not need the fuller orchestrated
flow. Express intentionally skips the separate
`speckit.canon.vibecode-drift-analyze` pass and goes from reconcile directly
to the final canonize confirmation, then canonizes within its own command body
rather than invoking `speckit.canon.vibecode-drift-canonize` as a separate
step.
