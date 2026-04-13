# Analyze Handoff Proposal

## Problem

`speckit.canon.vibecode-drift-analyze` was using `handoffs` as an internal
implementation jump to `speckit.canon.drift-analyze`.

That creates two problems:

- `handoffs` are better treated as user-visible next actions after a command
  finishes, not as an internal alias/include mechanism
- the standalone analyze commands are read-only, so using `handoffs` to fake an
  internal delegation conflicts with the intended UX and command contract

## Fix Applied Now

The current fix keeps the design conservative:

- `speckit.canon.vibecode-drift-analyze` is now a standalone command file
- `handoffs: []` is restored
- the command remains strictly read-only
- the command now points to vibecoding-specific follow-up wording:
  `/speckit.canon.vibecode-drift-canonize`

This matches the existing orchestrator behavior, where remediation decisions
already belong to:

- `/speckit.canon.drift`
- `/speckit.canon.vibecode-drift`

## Desired Future UX

Desired standalone flow after analyze:

1. Run analyze
2. Show possible next actions
3. If issues exist:
   - remediate now
   - continue anyway to canonize
   - stop
4. If remediation succeeds:
   - show canonize as the remaining next action

Goal:

- no extra dedicated "fix analyze findings" command if possible
- preserve clean manual workflow
- keep orchestrators and standalone commands aligned

## Constraint

Static `handoffs` frontmatter cannot fully model this flow.

Why:

- `handoffs` are static, but the desired actions are state-dependent
- the UI cannot naturally hide `remediate` after a clean verification pass
- the UI cannot show `canonize` only when the draft is ready unless the runtime
  itself interprets command output dynamically

## Option A — Keep Current Model

Summary:

- standalone analyze commands stay read-only
- `handoffs` stay empty
- remediation choices stay in orchestrators or in plain conversational follow-up

Pros:

- preserves sharp command semantics
- matches upstream `speckit.analyze` read-only style
- no hidden state machine inside analyze
- simplest and least fragile across agent runtimes

Cons:

- no visible post-analyze action buttons in standalone mode

Recommendation:

- best default

## Option B — Add Static Handoffs To Analyze

Summary:

- add two handoffs to analyze:
  - `Remediate Draft Canon Plan`
  - `Canonize Draft Canon Plan`
- make the analyze command inspect `$ARGUMENTS`
- default invocation performs read-only analysis
- remediation invocation edits only `canon.drift.md` using the last reported
  remediation items
- canonize invocation proceeds to canonize

Pros:

- gives users visible buttons
- no extra public command name required

Cons:

- analyze is no longer truly read-only
- `handoffs` remain visible even when not applicable
- command behavior becomes mode-dependent and harder to reason about
- likely more brittle across different agents/runtimes

Recommendation:

- possible, but not preferred

## Option C — Add Explicit Remediation Commands

Summary:

- keep analyze read-only
- add:
  - `speckit.canon.drift-remediate`
  - `speckit.canon.vibecode-drift-remediate`
- analyze can then expose handoffs to remediation and canonize

Pros:

- clean command contracts
- visible buttons map to explicit behavior
- easier to document and test

Cons:

- adds command surface area
- more files and docs to maintain

Recommendation:

- best option if explicit standalone handoff UX becomes important

## Option D — Use Manifest Aliases For True Alias Cases

Summary:

- use extension manifest `aliases` only for true same-body commands
- do not use `handoffs` to simulate aliases

Pros:

- semantically correct aliasing mechanism
- avoids conflating implementation reuse with next-step UX

Cons:

- only helps when two names truly should share one behavior
- does not solve dynamic remediation handoff UX by itself

Recommendation:

- use for real aliasing only

## Recommended Direction

Short term:

- keep the current fix
- leave standalone analyze commands with empty `handoffs`
- continue to let orchestrators own remediation decisions

If later you want visible standalone action buttons:

- prefer **Option C** over **Option B**
- only choose **Option B** if avoiding new commands is more important than
  keeping analyze strictly read-only

## Notes For Future Implementation

If Option B is attempted later, the command would need explicit argument-mode
handling such as:

- default: analyze only
- `remediate`
- `canonize`

That would require:

- reading the current `canon.drift.md`
- applying all reported CR-XXX items without touching canon files
- re-running verification once
- refusing canonize if the draft is not in a valid state

This is implementable, but it effectively turns analyze into a small
stateful workflow command rather than a pure analysis command.
