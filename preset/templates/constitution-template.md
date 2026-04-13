# [PROJECT_NAME] Constitution

> Version: [CONSTITUTION_VERSION] | Ratified: [RATIFICATION_DATE] | Last Amended: [LAST_AMENDED_DATE]

## 0. Authority

This constitution defines the core principles for maintaining and updating the system specification.

If any document conflicts with this constitution, this constitution prevails.

---

## 1. Canonical Baseline Specification

### Source of Truth

The canonical system specification baseline consists of:

- `CANON_TOC` (entry point)
- all documents linked under `CANON_ROOT/**`

This structure represents the full system definition.

Spec Kit must treat `CANON_TOC` as the root of the system specification graph.

In this document and in Spec Kit artifacts, refer to this canonical system
specification as "Canon" or "the canon".

---

### Rules for Canon

- Do NOT compress the canon into a single file.
- Do NOT duplicate the canon into feature specs.
- Do NOT invent requirements not present in the canon.
- Do NOT include code examples in any programming language (Python, JavaScript,
  SQL, etc.).
- Do NOT include implementation details, class names, module paths, or
  low-level HOW-level content that describes how a feature is built in a
  specific technology. Canon answers WHAT the system is and does, not HOW it
  is coded.
- System-level architectural decisions that define structure, boundaries, or
  protocols across the whole system ARE part of canon.
- Abstract algorithmic pseudocode that captures core domain logic or know-how
  (e.g., a risk-calculation formula or a key classification rule) IS permitted
  when that logic is itself the essential WHAT of the system, provided it uses
  language-neutral notation and contains no references to specific technologies,
  libraries, or implementation constructs.
- Always reference the canon sections by exact file path.

Canon is the "System Bible".

---

## 2. Roles of Spec Kit

### Evolution of the system

Spec Kit is used ONLY for:

- incremental features
- modifications
- refactors
- deprecations
- bug fixes
- performance improvements
- security improvements
- operational improvements
- documentation improvements
- other non-functional improvements

These correspond to the change classifications defined in Section 5, with
performance, security, and operational work typically classified as
Non-Functional.

### Bootstrap delivery of the canon baseline

If a project has canon but does not yet have a runnable implementation for that
canon-defined baseline, Spec Kit MAY be used to deliver that baseline into the
codebase as a one-time bootstrap increment.

For that bootstrap path:

- canon remains the source of truth for the behavior being delivered
- spec.md MUST describe the delivery increment, scope boundary, and exclusions
  for the bootstrap rather than copying canon prose into feature artifacts
- any transport, route, protocol, or error-format choice that canon does not
  define MUST be recorded as an explicit assumption or incremental requirement
  before implementation

### Support for canon integrity

- Spec Kit does NOT replace the canon.
- Canon defines the system.
- Spec Kit defines the system's evolution.
- Spec Kit updates the canon if specification drift is determined.

### Support for spec-first and code-first workflows

Spec Kit workflows can follow one of two patterns:

- Standard workflow. A full spec-first workflow using standard Spec Kit
  commands for incremental spec development.
- Vibecoding workflow. A simplified code-first workflow with a few additional
  vibecoding-related commands for making quick changes in the codebase and
  reflecting them in the canon.

Note: Each workflow must be performed on a separate branch. No workflow
command may be run on the base branch configured in
`.specify/extensions/canon/canon-config.yml` under `branching.base`. The
exceptions are `/speckit.specify` and `/speckit.canon.vibecode-specify`, which
start the corresponding workflows from that configured base branch.

---

## 3. Separation of Abstraction Levels

Strict separation must be maintained in the canon and each workflow.

### Canon

Describes:

- WHAT the system does (behavior, capabilities, constraints)
- system-level architectural decisions that affect the whole system (e.g., service boundaries, communication protocols, data flow)
- observable data shapes, contracts, and invariants expressed in prose
- system-level requirements and rules

Must NOT include:

- code examples in any specific programming language (Python, JavaScript, SQL, etc.)
- implementation details (class names, module paths, library calls, language-specific constructs)
- low-level architectural details that are internal to a single component and do not affect the rest of the system
- tool-specific configuration syntax

MAY include:

- abstract algorithmic pseudocode in language-neutral notation when the algorithm
  itself is core domain know-how (e.g., a risk formula, a classification rule)
  and contains no references to specific technologies or implementation constructs

### Standard Workflow

#### spec.md

Describes:

- WHAT changes
- WHY the change is needed
- Acceptance criteria
- Impacted canon sections

Must NOT include:

- implementation details
- low-level architecture
- code design

#### plan.md

Describes:

- HOW the change will be implemented
- architectural decisions
- tradeoffs

#### tasks.md

Describes:

- granular executable steps
- independently verifiable work units

#### tasks.drift.md

Describes:

- reverse-engineered implementation tasks derived from actual implementation
  changes
- HOW-level drift grouped into granular, independently reviewable work units
- input for /speckit.canon.drift-detect

#### tasks.alignment.md

Describes:

- deferred implementation-alignment work created from unresolved
  `IMPL-REJECTED` spec drift items
- executable corrective tasks that bring implementation back into line with
  the accepted feature truth
- input for /speckit.canon.drift-implement

#### spec.drift.md

Describes:

- discrepancies between specified and implemented behavior
- WHAT-level observable deviations only; never invented or inferred behavior
- input for /speckit.canon.drift-resolve and, once resolved,
  /speckit.canon.drift-reconcile to identify canon gaps

#### canon.drift.md

Describes:

- canon gaps between the incremental spec and the canon
- proposed canon text to be applied to the canon
- input for /speckit.canon.drift-analyze to verify the draft canon plan and,
  if needed, suggest remediation before /speckit.canon.drift-canonize updates
  canon accurately

If abstraction levels are mixed, fix structure before proceeding.

### Vibecoding Workflow

#### vibecode.md

Describes:

- the session intent
- high-level notes and constraints captured at the start
- lightweight context for the code-first session

#### tasks.drift.md

Describes:

- reverse-engineered implementation tasks derived from actual implementation
  changes
- HOW-level groupings of the work actually performed
- input for /speckit.canon.vibecode-drift-detect

#### spec.drift.md

Describes:

- reverse-engineered WHAT-level behavior and drift relevant to canon
- observable deviations only; never invented or inferred behavior
- input for /speckit.canon.vibecode-drift-reconcile

All findings are auto-ACCEPTED in the vibecoding workflow.

#### canon.drift.md

Describes:

- canon gaps between the incremental spec and the canon
- proposed canon text to be applied to the canon
- input for /speckit.canon.vibecode-drift-analyze when you want a reviewed
  draft canon pass before /speckit.canon.vibecode-drift-canonize
- direct canonize plan for /speckit.canon.vibecode-drift-express when the change
  is small and straightforward enough to skip the separate analyze step

If abstraction levels are mixed, fix structure before proceeding.

---

## 4. Mandatory Change Declaration

Every incremental spec must include:

- Canon references (exact canon paths)
- Primary change classification
- Impact analysis
- Acceptance criteria
- Migration notes (required for Breaking Change; recommended for Behavioral Change; not required otherwise)
- Explicit Assumptions section (for any behavior not covered by Canon; see Section 8)

---

## 5. Change Classification (Required)

Each spec must declare exactly one primary change classification from the
project-configured taxonomy. The default classification set is:

- Feature
- Behavioral Change
- Breaking Change
- Bug Fix
- Refactor
- Deprecation
- Non-Functional: Performance
- Non-Functional: Security
- Non-Functional: DevOps
- Non-Functional: Documentation
- Non-Functional: Other

Section 6 defines the allowed branch type codes that map to these
classifications. The spec declares the classification; the branch name uses the
configured branch type code.

If compatibility is reduced -> Breaking Change.
If runtime behavior changes without reducing compatibility -> Behavioral Change.

---

## 6. Git Branching Strategy

### Branch Name

Branch name template:

```
<type>-<scope>-<short-description>
```

IMPORTANT:
This template does not replace the Spec Kit branch prefix, whether it is a
numeric prefix such as `###-` or a timestamp prefix such as
`YYYYMMDD-HHMMSS-`. It defines only the portion that comes after that prefix.

`<type>` MUST be one of the project-configured branch type codes. The type
table below is the source of truth for allowed values and change-classification
mapping.

`<scope>` MUST be one of the project-configured branch scope codes. The scope
table below is the source of truth for allowed values.

| Type       | Map to Change Classification  |
| ---------- | ----------------------------- |
| `feature`  | Feature                       |
| `behavior` | Behavioral Change             |
| `breaking` | Breaking Change               |
| `bugfix`   | Bug Fix                       |
| `refactor` | Refactor                      |
| `deprecat` | Deprecation                   |
| `perform`  | Non-Functional: Performance   |
| `security` | Non-Functional: Security      |
| `devops`   | Non-Functional: DevOps        |
| `document` | Non-Functional: Documentation |
| `nonfunc`  | Non-Functional: Other         |

| Scope    | Description     |
| -------- | --------------- |
| `api`    | Public API      |
| `worker` | Background jobs |
| `web`    | Web application |

Examples:

```
feature-api-add-capability
behavior-worker-change-runtime-rule
breaking-web-remove-legacy-contract
perform-api-reduce-response-latency
security-api-harden-access-checks
devops-worker-improve-job-observability
document-api-update-project-docs
nonfunc-web-improve-accessibility-baseline
```

---

## 7. Workflow Enforcement

### Standard Workflow / Spec-First + Conditional Spec-Drift

Spec-First command order:

1. /speckit.specify
2. /speckit.clarify (repeated as needed, zero or more times)
3. /speckit.checklist
4. /speckit.plan
5. /speckit.tasks
6. /speckit.analyze (optional pre-implementation consistency check)
7. /speckit.implement

After implementation in the standard workflow, follow-up development MAY
continue for bug fixes, solution polishing, or more substantial changes based
on the implemented result. Such follow-up work increases the likelihood of
specification drift. If those follow-up changes introduce observable
deviations or canon-impacting changes not already captured in the accepted
`spec.md`, `plan.md`, and `tasks.md`, the Spec-Drift workflow MUST be used to
synchronize those additional changes with the canon.

Spec-Drift command order:

8. /speckit.canon.drift-reverse
9. /speckit.canon.drift-detect
10. /speckit.canon.drift-resolve
11. /speckit.canon.drift-implement (only when tasks.alignment.md is created)
12. /speckit.canon.drift-reconcile
13. /speckit.canon.drift-analyze (optional pre-canonization consistency check)
14. /speckit.canon.drift-canonize

Optional orchestrator command:

15. /speckit.canon.drift (orchestrator for steps 8-14)

Standard Spec-Drift path: steps 8-14, with step 11 required only when
`tasks.alignment.md` is created by resolve. This path becomes required only
when implementation work introduces additional observable behavior,
implementation drift, or canon-impacting changes that are not already fully
captured in the accepted `spec.md`, `plan.md`, and `tasks.md`, or when the
team explicitly chooses to reconcile canon on the branch.
`/speckit.analyze` MAY be run after `/speckit.tasks` and before
`/speckit.implement` to check cross-artifact consistency and coverage.
`/speckit.canon.drift-analyze` MAY be run after
`/speckit.canon.drift-reconcile` as a read-only verification pass before
`/speckit.canon.drift-canonize`.
`/speckit.canon.drift` MAY be used as the orchestrated form of that path and
includes the analyze step automatically.

A step is **successful** when it produces zero violations or blocking issues.
Warnings may be noted but do not block progression.

No /speckit.plan before successful checklist.
No /speckit.implement before /speckit.tasks is complete.
When the Standard Spec-Drift path is invoked:

- No /speckit.canon.drift before /speckit.implement is complete (all tasks
  checked off).
- No /speckit.canon.drift-reverse before /speckit.implement is complete (all
  tasks checked off).
- No /speckit.canon.drift-detect before /speckit.implement is complete (all
  tasks checked off).
- No /speckit.canon.drift-resolve before /speckit.canon.drift-detect is
  complete.
- No /speckit.canon.drift-implement before /speckit.canon.drift-resolve
  creates `tasks.alignment.md`.
- No /speckit.canon.drift-reconcile before /speckit.canon.drift-resolve is
  complete and any `tasks.alignment.md` queue is fully implemented and
  re-verified.
- No /speckit.canon.drift-analyze before /speckit.canon.drift-reconcile is
  complete.
- No /speckit.canon.drift-canonize before /speckit.canon.drift-reconcile is
  complete.
- If /speckit.canon.drift-analyze is run, no /speckit.canon.drift-canonize
  before its report has been reviewed and any reported issues were either
  addressed manually or consciously accepted.
- No Canon edits before /speckit.canon.drift-canonize is complete.

Note: The `/speckit.canon.drift-reverse` -> `/speckit.canon.drift-detect` ->
`/speckit.canon.drift-resolve` -> `/speckit.canon.drift-reconcile` chain is
the step-by-step form of the Standard Spec-Drift path when no deferred
alignment work is needed. `/speckit.canon.drift-analyze` is an optional
read-only review step between reconcile and canonize. When
`/speckit.canon.drift-resolve` creates `tasks.alignment.md`,
`/speckit.canon.drift-implement` MUST be run and then
`/speckit.canon.drift-resolve` MUST be run again before reconcile.
`/speckit.canon.drift` is the orchestrated form of that path and includes one
automatic `/speckit.canon.drift-implement` ->
`/speckit.canon.drift-resolve` follow-up cycle when alignment work is created,
plus the analyze step before canonize. If drift remains unresolved after that
follow-up resolve pass, reverse engineering, detection, and resolution are
skipped, and undocumented implementation changes may not be reflected in
canon.

### Vibecoding Workflow / Code-First + Required Spec-Drift

Code-First command order:

1. /speckit.canon.vibecode-specify

Spec-Drift command order:

2. /speckit.canon.vibecode-drift-reverse
3. /speckit.canon.vibecode-drift-detect
4. /speckit.canon.vibecode-drift-reconcile
5. /speckit.canon.vibecode-drift-analyze (optional pre-canonization consistency check)
6. /speckit.canon.vibecode-drift-canonize

Optional orchestrator command:

7. /speckit.canon.vibecode-drift (orchestrator for steps 2-6)

Optional express shortcut command:

8. /speckit.canon.vibecode-drift-express (express shortcut for steps 2-4 plus
   direct canonize)

After implementation changes exist in the vibecoding workflow, completion MUST
proceed through reverse, detect, reconcile, and canonize.
`/speckit.canon.vibecode-drift-analyze` MAY be run after reconcile as an
optional read-only review step before standalone canonize.
`/speckit.canon.vibecode-drift` MAY be used as the orchestrated form of that
required path and includes the analyze step automatically.
`/speckit.canon.vibecode-drift-express` MAY be used only for small, narrowly
scoped changes; in that case, it replaces the reviewed path with its own
reverse -> detect -> reconcile -> direct canonize flow, and no standalone
canonize command is used.

A step is **successful** when it produces zero violations or blocking issues.
Warnings may be noted but do not block progression.

No /speckit.canon.vibecode-drift, /speckit.canon.vibecode-drift-express, or
/speckit.canon.vibecode-drift-reverse before implementation changes exist on
the branch.
No /speckit.canon.vibecode-drift-detect before
/speckit.canon.vibecode-drift-reverse is complete.
No /speckit.canon.vibecode-drift-reconcile before
/speckit.canon.vibecode-drift-detect is complete.
No /speckit.canon.vibecode-drift-analyze before
/speckit.canon.vibecode-drift-reconcile is complete.
No standalone /speckit.canon.vibecode-drift-canonize before
/speckit.canon.vibecode-drift-reconcile is complete.
If /speckit.canon.vibecode-drift-analyze is run, no standalone
/speckit.canon.vibecode-drift-canonize before its report has been reviewed and
any reported issues were either addressed manually or consciously accepted.
`/speckit.canon.vibecode-drift-express` is the only vibecoding shortcut
command. It always skips the separate analyze step and applies canon within its
own command flow rather than by invoking the standalone canonize command in the
vibecoding workflow.

Note: /speckit.canon.vibecode-drift-reverse ->
/speckit.canon.vibecode-drift-detect ->
/speckit.canon.vibecode-drift-reconcile is the step-by-step prefix of the
required vibecoding path. `/speckit.canon.vibecode-drift-analyze` is an
optional read-only review step before standalone canonize. `/speckit.canon.
vibecode-drift` is the orchestrated form of the required path and includes the
analyze step automatically, while `/speckit.canon.vibecode-drift-express` is
the only shortcut command and skips the separate analyze step.

---

## 8. No Hallucinated Requirements

If Canon is silent:

- mark as explicit assumption
- OR create a separate Canon clarification spec

Never invent implicit system behavior.

Explicit assumptions must be recorded in a dedicated **Assumptions** section within spec.md, using the format:

```
**Assumption <ID>**: <statement of assumed behavior>
*Reason*: Canon is silent on <topic>; assumed based on <rationale>.
```

---

## 9. Definition of Done

### Standard flow

A change is complete only when:

- Spec, Plan, and Tasks are consistent
- Implementation matches spec
- Tests validate acceptance criteria
- If post-implementation review identifies additional implementation actions,
  observable deviations from the accepted feature artifacts, or canon-impacting
  changes not already captured in `spec.md`, `plan.md`, and `tasks.md`, the
  optional `/speckit.canon.drift*` workflow has been run as needed and the
  resulting drift artifacts have been reviewed
- If `tasks.alignment.md` was created by the optional drift workflow, it has
  been completed via /speckit.canon.drift-implement and the linked drift items
  have been re-verified by /speckit.canon.drift-resolve
- If `canon.drift.md` was created by the optional drift workflow, it has been
  reviewed before canonize; if /speckit.canon.drift-analyze was run, any
  reported issues were either addressed manually or consciously accepted
- Canon `CANON_ROOT/**` is updated via the optional drift workflow only
  when that workflow was invoked and canon updates were confirmed to be needed
- Migration steps documented (if breaking)

### Vibecoding flow

A change is complete only when:

- /speckit.canon.vibecode-drift-reverse and
  /speckit.canon.vibecode-drift-detect have been run, and tasks.drift.md and
  spec.drift.md have been reviewed for unintended deviations
- Draft `canon.drift.md` has either been reviewed directly before standalone
  canonize, reviewed via /speckit.canon.vibecode-drift-analyze before
  standalone canonize, or applied through
  /speckit.canon.vibecode-drift-express on the small-change shortcut path
- Canon `CANON_ROOT/**` is updated either through the reviewed
  `/speckit.canon.vibecode-drift-reconcile` +
  `/speckit.canon.vibecode-drift-canonize` path or directly through
  `/speckit.canon.vibecode-drift-express` on the small-change shortcut path
  when the change introduces new behavior, modifies existing behavior, or
  deprecates a component described in the canon
- Migration steps documented (if breaking)

---

## 10. Terminology

Terminology must match Canon exactly.

No synonyms that create semantic drift.

All references must use file paths, not vague language.
