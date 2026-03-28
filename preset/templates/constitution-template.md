# [PROJECT_NAME] Constitution

> Version: [CONSTITUTION_VERSION] | Ratified: [RATIFICATION_DATE] | Last Amended: [LAST_AMENDED_DATE]

## 0. Authority

This constitution defines the core principles for maintaining and updating the system specification.

If any document conflicts with this constitution, this constitution prevails.

---

## 1. Canonical Baseline Specification

### Source of Truth

The canonical system specification baseline is located at:

- `CANON_TOC` (entry point)
- and all documents linked under `CANON_ROOT/**`

This structure represents the full system definition.

Spec Kit must treat `CANON_TOC` as the root of the system specification graph.

Let's name and reference this canonical system specification in this document and Spec Kit's artefacts as "Canon" or "the canon".

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

### Support of the canon integrity

- Spec Kit does NOT replace the canon.
- Canon defines the system.
- Spec Kit defines system evolution.
- Spec Kit updates the canon if specification drift is determined.

### Support of spec-first and code-first development workflows

Spec Kit workflow could be of two types:

- Standard workflow. Full spec-first workflow with standard Spec Kit commands for the incremental spec development.
- Vibecoding workflow. Simplified code-first workflow with few additional vibecoding-related commands for making quick changes into the codebase and reflecting them into the canon.

Note: Each workflow must be performed only in a separate branch. Any workflow (i.e. any command execution) is NOT allowed in the base branch configured in `.specify/extensions/canon/canon-config.yml` under `branching.base`. Exceptions are /speckit.specify and /speckit.canon.vibecode-specify, which start the corresponding workflows from that configured base branch.

---

## 3. Separation of Abstraction Levels

Strict separation must be maintained in each workflow.

### Standard Workflow

#### spec.md

Describes:

- WHAT changes
- WHY changes
- Acceptance criteria
- Impacted canon sections

Must NOT include:

- implementation details
- low-level architecture
- code design

#### plan.md

Describes:

- HOW change will be implemented
- architectural decisions
- tradeoffs

#### tasks.md

Describes:

- granular executable steps
- independently verifiable work units

#### drift.md

Describes:

- discrepancies between what was specified and what was actually implemented
- observable deviations only; never invented or inferred behavior
- input for /speckit.canon.drift-reconcile to identify canon gaps

#### canon.drift.md

Describes:

- canon gaps between the incremental spec and the canon
- proposed canon text to be applied to canon
- input for /speckit.canon.drift-canonize to update canon accurately

If abstraction levels are mixed, fix structure before proceeding.

### Vibecoding Workflow

#### spec.md

Describes:

- WHAT changes
- WHY changes
- Acceptance criteria
- Impacted canon sections

Must NOT include:

- implementation details
- low-level architecture
- code design

Spec is reverse engineered from tasks.

#### plan.md

Not required because in vibecoding workflow no plan is reverse-engineered.
Spec is directly reverse-engineered from tasks.

#### tasks.md

Describes:

- granular executable steps
- independently verifiable work units

Tasks are reverse engineered from actual implementation.

#### drift.md

Not required because in vibecoding workflow implementation always prevails over the spec.

#### canon.drift.md

Describes:

- canon gaps between the incremental spec and the canon
- proposed canon text to be applied to canon
- input for /speckit.canon.vibecode-drift-canonize to update canon accurately

If abstraction levels are mixed, fix structure before proceeding.

---

## 4. Mandatory Change Declaration

Every incremental spec must include:

- Canon references (exact canon paths)
- Primary change type
- Impact analysis
- Acceptance criteria
- Migration notes (required for Breaking Change; recommended for Behavioral Change; not required otherwise)
- Explicit Assumptions section (for any behavior not covered by Canon — see §8)

---

## 5. Change Classification (Required)

Each spec must declare exactly one primary change type:

- Feature
- Behavioral Change
- Breaking Change
- Bug Fix
- Refactor
- Deprecation
- Non-Functional
- Documentation Only

Performance, Security, and Operations branch types may all map to
Non-Functional when the project branch taxonomy needs more specific branch
codes than the classification taxonomy. The broader `nonfunc` branch type may
still be used for non-functional work that does not fit one of those narrower
codes cleanly.

If compatibility is reduced → Breaking.
If runtime behavior changes → Behavioral.

---

## 6. Git Branching Strategy

### Branch Name

Template for branch name:

```
<type>-<scope>-<short-description>
```

IMPORTANT:
This template does not discard Spec Kit numbering of branches in kind of "###-"!
Template only defines what goes after numeric prefix!

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

### Standard Workflow

Command order:

1. /speckit.specify
2. /speckit.clarify (repeated as needed, zero or more times)
3. /speckit.checklist
4. /speckit.plan
5. /speckit.tasks
6. /speckit.analyze
7. /speckit.implement
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

Note: The /speckit.canon.drift-reverse → /speckit.canon.drift-detect → /speckit.canon.drift-resolve → /speckit.canon.drift-reconcile chain is the step-by-step flow. /speckit.canon.drift runs that pipeline for you. If reverse, detection, and resolution are skipped, undocumented implementation changes may not be reflected in canon.

### Vibecoding Workflow

Command order:

1. /speckit.canon.vibecode-specify
2. /speckit.canon.vibecode-drift (optional orchestrator for steps 4-7)
3. /speckit.canon.vibecode-drift-express (optional express shortcut for steps 4-7)
4. /speckit.canon.vibecode-drift-reverse
5. /speckit.canon.vibecode-drift-detect
6. /speckit.canon.vibecode-drift-reconcile
7. /speckit.canon.vibecode-drift-canonize

Required vibecoding path after implementation changes: steps 4-7. Use step 2 instead when you want the extension to orchestrate the full vibecode drift pipeline automatically. Use step 3 when you want the express single-invocation variant.

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
- OR create separate Canon clarification spec

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
- /speckit.canon.drift-detect and /speckit.canon.drift-resolve have been run and drift.md reviewed for unintended deviations
- Canon `CANON_ROOT/**` is updated via /speckit.canon.drift-reconcile and /speckit.canon.drift-canonize when the change introduces new behavior, modifies existing behavior, or deprecates a component described in canon
- Migration steps documented (if breaking)

### Vibecoding flow

A change is complete only when:

- /speckit.canon.vibecode-drift-detect has been run and tasks.md and spec.md reviewed for unintended deviations
- Canon `CANON_ROOT/**` is updated via /speckit.canon.vibecode-drift-reconcile and /speckit.canon.vibecode-drift-canonize when the change introduces new behavior, modifies existing behavior, or deprecates a component described in canon
- Migration steps documented (if breaking)

---

## 10. Terminology

Terminology must match Canon exactly.

No synonyms that create semantic drift.

All references must use file paths, not vague language.
