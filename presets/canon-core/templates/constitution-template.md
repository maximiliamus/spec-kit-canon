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

Spec-Kit must treat `CANON_TOC` as the root of the system specification graph.

Let's name and reference this canonical system specification in this document and Spec-Kit's artefacts as "Canon" or "the canon".

---

### Rules for Canon

- Do NOT compress the canon into a single file.
- Do NOT duplicate the canon into feature specs.
- Do NOT invent requirements not present in the canon.
- Always reference the canon sections by exact file path.

Canon is the "System Bible".

---

## 2. Roles of Spec-Kit

### Evolution of the system

Spec-Kit is used ONLY for:

- incremental features
- modifications
- refactors
- deprecations
- bug fixes
- non-functional improvements

These correspond directly to the change types defined in §5.

### Support of the canon integrity

- Spec-Kit does NOT replace the canon.
- Canon defines the system.
- Spec-Kit defines system evolution.
- Spec-Kit updates the canon if specification drift is determined.

### Support of spec-first and code-first development workflows

Spec-Kit workflow could be of two types:

- Standard workflow. Full spec-first workflow with standard Spec-Kit commands for the incremental spec development.
- Vibecoding workflow. Simplified code-first workflow with few additional vibecoding-related commands for making quick changes into the codebase and reflecting them into the canon.

Note: Each workflow must be performed only in a separate branch. Any workflow (i.e. any command execution) is NOT allowed in the master branch. Exceptions are /speckit.specify and /speckit.vibecode commands that start the corresponding workflows from the master branch (i.e. they are in turn allowed to be executed only from the master branch).

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
- input for /speckit.drift.reconcile to identify canon gaps

#### canonization.md

Describes:

- canon gaps between the incremental spec and the canon
- proposed canon text to be applied to canon
- input for /speckit.drift.canonize to update canon accurately

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

#### canonization.md

Describes:

- canon gaps between the incremental spec and the canon
- proposed canon text to be applied to canon
- input for /speckit.vibecode.drift.canonize to update canon accurately

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

If compatibility is reduced → Breaking.
If runtime behavior changes → Behavioral.

---

## 6. Git Branching Strategy

### Branch Name

Template for branch name:

```
<type>-<area>-<short-description>
```

IMPORTANT:
This template does not discard Spec-Kit numbering of branches in kind of "###-"!
Template only defines what goes after numeric prefix!

`<type>` MUST be one of the project-configured branch type codes. The type
table below is the source of truth for allowed values and change-classification
mapping.

`<area>` MUST be one of the project-configured branch area codes. The area
table below is the source of truth for allowed values.

| Type       | Map to Change Classification |
| ---------- | ---------------------------- |
| `feature`  | Feature                      |
| `behavior` | Behavioral Change            |
| `breaking` | Breaking Change              |
| `bugfix`   | Bug Fix                      |
| `refactor` | Refactor                     |
| `deprecat` | Deprecation                  |
| `nonfunc`  | Non-Functional               |
| `document` | Documentation Only           |

| Area     | Description     |
| -------- | --------------- |
| `api`    | Public API      |
| `worker` | Background jobs |
| `web`    | Web application |

Examples:

```
feature-api-add-capability
behavior-worker-change-runtime-rule
breaking-web-remove-legacy-contract
document-api-update-project-docs
```

---

## 7. Workflow Enforcement

### Standard Workflow

Required order:

1. /speckit.specify
2. /speckit.clarify (repeated as needed, zero or more times)
3. /speckit.checklist
4. /speckit.plan
5. /speckit.tasks
6. /speckit.analyze
7. /speckit.implement
8. /speckit.drift.detect
9. /speckit.drift.resolve
10. /speckit.drift.reconcile
11. /speckit.drift.canonize

A step is **successful** when it produces zero violations or blocking issues. Warnings may be noted but do not block progression.

No /speckit.plan before successful checklist.
No /speckit.implement before successful analyze.
No /speckit.drift.detect before /speckit.implement is complete (all tasks checked off).
No /speckit.drift.resolve before /speckit.drift.detect is complete.
No /speckit.drift.reconcile before /speckit.drift.resolve is complete.
No /speckit.drift.canonize before /speckit.drift.reconcile is complete.
No Canon edits before /speckit.drift.canonize is complete.

Note: The /speckit.drift.detect → /speckit.drift.resolve → /speckit.drift.reconcile chain is strongly recommended. If drift detection and resolution are skipped, undocumented implementation changes may not be reflected in canon.

### Vibecoding Workflow

Required order:

1. /speckit.vibecode
2. /speckit.vibecode.drift.detect
3. /speckit.vibecode.drift.reconcile
4. /speckit.vibecode.drift.canonize

A step is **successful** when it produces zero violations or blocking issues. Warnings may be noted but do not block progression.

No /speckit.vibecode.drift.reconcile before /speckit.vibecode.drift.detect is complete.
No /speckit.vibecode.drift.canonize before /speckit.vibecode.drift.reconcile is complete.

Note: /speckit.vibecode.drift.detect is required before /speckit.vibecode.drift.reconcile and hard-blocks it.

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
- /speckit.drift.detect and /speckit.drift.resolve have been run and drift.md reviewed for unintended deviations
- Canon `CANON_ROOT/**` is updated via /speckit.drift.reconcile and /speckit.drift.canonize when the change introduces new behavior, modifies existing behavior, or deprecates a component described in canon
- Migration steps documented (if breaking)

### Vibecoding flow

A change is complete only when:

- /speckit.vibecode.drift.detect has been run and tasks.md and spec.md reviewed for unintended deviations
- Canon `CANON_ROOT/**` is updated via /speckit.vibecode.drift.reconcile and /speckit.vibecode.drift.canonize when the change introduces new behavior, modifies existing behavior, or deprecates a component described in canon
- Migration steps documented (if breaking)

---

## 10. Terminology

Terminology must match Canon exactly.

No synonyms that create semantic drift.

All references must use file paths, not vague language.
