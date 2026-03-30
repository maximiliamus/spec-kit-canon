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

These correspond to the change classifications defined in §5, with
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

Strict separation must be maintained in each workflow.

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
- input for /speckit.canon.drift-canonize to update canon accurately

#### canon.repair.md

Describes:

- an optional post-canon repair plan and trace artifact created only when
  `/speckit.canon.drift-analyze` finds canon issues after canon apply
- targeted WHAT-level corrections to canon content, placement,
  cross-references, or contradictions
- input for /speckit.canon.drift-repair

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
- input for /speckit.canon.vibecode-drift-canonize to update canon accurately

#### canon.repair.md

Describes:

- an optional post-canon repair plan and trace artifact created only when
  `/speckit.canon.drift-analyze` finds canon issues after canon apply in the
  vibecoding flow
- targeted WHAT-level corrections to canon content, placement,
  cross-references, or contradictions
- input for /speckit.canon.drift-repair

If abstraction levels are mixed, fix structure before proceeding.

---

## 4. Mandatory Change Declaration

Every incremental spec must include:

- Canon references (exact canon paths)
- Primary change classification
- Impact analysis
- Acceptance criteria
- Migration notes (required for Breaking Change; recommended for Behavioral Change; not required otherwise)
- Explicit Assumptions section (for any behavior not covered by Canon; see §8)

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

If compatibility is reduced → Breaking Change.
If runtime behavior changes without reducing compatibility → Behavioral Change.

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

| Type       | Maps to Change Classification |
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

### Standard Workflow / Spec-First + Spec-Drift

Spec-First command order:

1. /speckit.specify
2. /speckit.clarify (repeated as needed, zero or more times)
3. /speckit.checklist
4. /speckit.plan
5. /speckit.tasks
6. /speckit.analyze
7. /speckit.implement

Spec-Drift command order:

8. /speckit.canon.drift (optional orchestrator for steps 9-15)
9. /speckit.canon.drift-reverse
10. /speckit.canon.drift-detect
11. /speckit.canon.drift-resolve
12. /speckit.canon.drift-reconcile
13. /speckit.canon.drift-canonize
14. /speckit.canon.drift-analyze
15. /speckit.canon.drift-repair (only when analysis reports repair candidates)

Required standard path after implementation: steps 9-13. Use step 8 instead when you want the extension to orchestrate the full drift pipeline automatically. Run step 14 after canon updates are applied. Run step 15 only when step 14 finds issues.

A step is **successful** when it produces zero violations or blocking issues. Warnings may be noted but do not block progression.

No /speckit.plan before successful checklist.
No /speckit.implement before successful analyze.
No /speckit.canon.drift before /speckit.implement is complete (all tasks checked off).
No /speckit.canon.drift-reverse before /speckit.implement is complete (all tasks checked off).
No /speckit.canon.drift-detect before /speckit.implement is complete (all tasks checked off).
No /speckit.canon.drift-resolve before /speckit.canon.drift-detect is complete.
No /speckit.canon.drift-reconcile before /speckit.canon.drift-resolve is complete.
No /speckit.canon.drift-canonize before /speckit.canon.drift-reconcile is complete.
No /speckit.canon.drift-analyze before /speckit.canon.drift-canonize is complete.
No /speckit.canon.drift-repair before /speckit.canon.drift-analyze identifies repair candidates.
No Canon edits before /speckit.canon.drift-canonize is complete.

Note: The `/speckit.canon.drift-reverse` → `/speckit.canon.drift-detect` →
`/speckit.canon.drift-resolve` → `/speckit.canon.drift-reconcile` chain is the
step-by-step flow. `/speckit.canon.drift` runs that pipeline for you. If
reverse engineering, detection, and resolution are skipped, undocumented
implementation changes may not be reflected in canon.

### Vibecoding Workflow / Code-First + Spec-Drift

Code-First command order:

1. /speckit.canon.vibecode-specify

Spec-Drift command order:

2. /speckit.canon.vibecode-drift (optional orchestrator for steps 4-7)
3. /speckit.canon.vibecode-drift-express (optional express shortcut for steps 4-7)
4. /speckit.canon.vibecode-drift-reverse
5. /speckit.canon.vibecode-drift-detect
6. /speckit.canon.vibecode-drift-reconcile
7. /speckit.canon.vibecode-drift-canonize
8. /speckit.canon.drift-analyze
9. /speckit.canon.drift-repair (only when analysis reports repair candidates)

Required vibecoding path after implementation changes: steps 4-7. Step 2 is
the full orchestrated vibecode drift pipeline. Step 3 is the express path for
small, narrowly scoped codebase changes where only a few aspects changed and
the full workflow would be too long and time-consuming; it provides a faster
way to sync those small changes back into the canon.

A step is **successful** when it produces zero violations or blocking issues. Warnings may be noted but do not block progression.

No /speckit.canon.vibecode-drift, /speckit.canon.vibecode-drift-express, or /speckit.canon.vibecode-drift-reverse before implementation changes exist on the branch.
No /speckit.canon.vibecode-drift-detect before /speckit.canon.vibecode-drift-reverse is complete.
No /speckit.canon.vibecode-drift-reconcile before /speckit.canon.vibecode-drift-detect is complete.
No /speckit.canon.vibecode-drift-canonize before /speckit.canon.vibecode-drift-reconcile is complete.

Note: /speckit.canon.vibecode-drift-reverse → /speckit.canon.vibecode-drift-detect → /speckit.canon.vibecode-drift-reconcile is the step-by-step vibecode flow. /speckit.canon.vibecode-drift orchestrates that path, while /speckit.canon.vibecode-drift-express is the low-ceremony shortcut.

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
- /speckit.canon.drift-reverse, /speckit.canon.drift-detect, and /speckit.canon.drift-resolve have been run, and tasks.drift.md and spec.drift.md have been reviewed for unintended deviations
- Canon `CANON_ROOT/**` is updated via /speckit.canon.drift-reconcile and /speckit.canon.drift-canonize when the change introduces new behavior, modifies existing behavior, or deprecates a component described in the canon
- Migration steps documented (if breaking)

### Vibecoding flow

A change is complete only when:

- /speckit.canon.vibecode-drift-reverse and /speckit.canon.vibecode-drift-detect have been run, and tasks.drift.md and spec.drift.md have been reviewed for unintended deviations
- Canon `CANON_ROOT/**` is updated via /speckit.canon.vibecode-drift-reconcile and /speckit.canon.vibecode-drift-canonize when the change introduces new behavior, modifies existing behavior, or deprecates a component described in the canon
- Migration steps documented (if breaking)

---

## 10. Terminology

Terminology must match Canon exactly.

No synonyms that create semantic drift.

All references must use file paths, not vague language.
