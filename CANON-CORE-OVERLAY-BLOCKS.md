# Canon Overlay Blocks

Non-precondition `<!-- spec-kit-canon -->` blocks that extend upstream spec-kit
commands with canon-specific behavior. Each block is wrapped in
`<!-- spec-kit-canon:start <name> -->` / `<!-- spec-kit-canon:end <name> -->`
markers and does not exist in the upstream `spec-kit/templates/commands/`.

---

## Precondition Blocks

`<!-- spec-kit-canon:start preconditions -->` blocks are present in **every**
preset command (analyze, checklist, clarify, implement, plan, specify, tasks)
and are always mandatory. They share a uniform structure:

1. Read `.specify/memory/constitution.md` in full before producing any output.
2. Apply a command-specific subset of constitution sections to all subsequent
   steps (e.g. §3 Separation of Abstraction Levels, §7 Workflow Enforcement,
   §9 Definition of Done).

The sections cited differ per command to reflect each command's role in the
workflow, but the pattern is identical across all commands. Precondition blocks
are not listed individually below.

---

## speckit.analyze.md

### `canon-bootstrap-exception`

**Location**: Operating Constraints section, after the "Constitution Authority"
paragraph.

**Purpose**: Prevents `/speckit.analyze` from flagging valid canon bootstrap
delivery as duplication. When a spec references canon as the source of truth
for baseline behavior being delivered into an empty codebase, that is not
duplication — it is the intended bootstrap pattern from §2 of the constitution.

**Without it**: Analyze would report false-positive duplication findings for
every bootstrap spec that references canon-defined behavior, making the
bootstrap workflow unusable.

**Constitution basis**: §2 — Bootstrap delivery of the canon baseline.

---

## speckit.plan.md

### `canon-visible-assumptions`

**Location**: Key rules section, between "Use absolute paths" and "ERROR on
gate failures".

**Purpose**: Prevents plan.md from inventing externally-visible assumptions
(identifier typing, error response semantics, user-visible data constraints)
that are not already in spec.md or canon. Also prevents inventing vague
performance goals when none are specified.

**Without it**: Plan generation tends to invent things like "IDs will be UUIDs",
"errors return 500 with JSON body", or "response time under 200ms" when
canon/spec are silent, creating hallucinated requirements that propagate into
tasks and implementation.

**Constitution basis**: §8 — No Hallucinated Requirements; §3 — Separation of
Abstraction Levels.

---

## speckit.specify.md

### `bootstrap-delta-framing`

**Location**: Execution flow, step 2.5 (inserted between "Extract key concepts"
and "For unclear aspects").

**Purpose**: When the requested work is delivery of behavior already defined in
canon, instructs spec generation to frame the spec as an incremental delivery
delta against canon — referencing existing canon files directly instead of
duplicating entity definitions, baseline API semantics, or system facts.

**Without it**: Spec generation restates canon content as if it were new product
behavior, creating large redundant specs that drift from canon over time.

**Constitution basis**: §2 — "spec.md MUST describe the delivery increment,
scope boundary, and exclusions for the bootstrap rather than copying canon
prose into feature artifacts."

### `bootstrap-delta-guideline`

**Location**: Quick Guidelines section, after "Written for business
stakeholders, not developers."

**Purpose**: Concise quick-reference reminder of the same §2 rule: don't
duplicate canon content into spec.md. Placed in the guidelines section that
agents scan for short behavioral rules.

**Without it**: The framing instruction in step 2.5 may be overlooked when
agents jump to the quick guidelines for a summary of spec-writing rules.

**Constitution basis**: §2 — Bootstrap delivery of the canon baseline.

---

## speckit.tasks.md

### `post-implementation-canon-drift-note`

**Location**: Generate tasks.md step (step 4), final bullet in the output
content list.

**Purpose**: Makes tasks.md output include a visible note that the
constitution-mandated post-implementation canon drift workflow still happens
after coding and is outside the implementation checklist.

**Without it**: Agents completing `/speckit.implement` declare the feature
"done" without mentioning the required §7/§9 post-implementation drift steps
(reverse → detect → resolve → reconcile → analyze → canonize).

**Constitution basis**: §7 — Workflow Enforcement; §9 — Definition of Done.

### `post-implementation-canon-drift-guideline`

**Location**: Phase Structure subsection, after "Final Phase: Polish &
Cross-Cutting Concerns."

**Purpose**: Phase structure reference reinforcement — keep tasks.md focused on
implementation work, but explicitly note when constitution-required follow-up
workflow remains required before the feature is truly done.

**Without it**: Same gap as above, but in the structural reference that guides
phase organization rather than output content.

**Constitution basis**: §7 — Workflow Enforcement; §9 — Definition of Done.
