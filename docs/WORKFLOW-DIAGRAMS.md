# Workflow Diagrams

This file summarizes the main Spec Kit Canon workflows as Mermaid diagrams.

## Legend

- Blue nodes mark user-facing review steps. In the manual path, these are the points where user action is needed.
- Green nodes mark successful resolved or canon-updated outcomes.
- Amber nodes mark where implementation drift occurs and the workflow enters drift recovery.

## Standard Spec-First Workflow

This is the normal canon-driven Spec Kit path. It keeps the familiar core
Spec Kit sequence and uses canon-aware configuration, constitution, and prompt
behavior throughout.

```mermaid
flowchart TD
    A["Configure canon and run<br/>/speckit.constitution"] --> B["/speckit.specify"]
    B --> C["spec.md"]
    C --> D["/speckit.clarify"]
    D --> E["/speckit.plan"]
    E --> F["plan.md"]
    F --> G["/speckit.checklist"]
    G --> H["/speckit.tasks"]
    H --> I["tasks.md"]
    I --> J["/speckit.analyze"]
    J --> K["/speckit.implement"]
    K --> L["Implementation updated<br/>(spec-drift occurs here)"]
    L --> M{"Still aligned with<br/>spec-first artifacts?"}
    M -- Yes --> N["Continue normal development"]
    M -- No --> O["Enter standard spec-drift workflow"]

    X["Constitution + canon context"] -. canon-aware context .-> B
    X -. canon-aware context .-> D
    X -. canon-aware context .-> E
    X -. canon-aware context .-> H
    X -. canon-aware context .-> J
    X -. canon-aware context .-> K

    classDef driftRisk fill:#fef3c7,stroke:#b45309,stroke-width:3px,color:#78350f
    class L driftRisk
```

## Standard Spec-Drift Workflow

This is the recovery path when implementation has diverged from the original
`spec.md` and `tasks.md` baseline. This diagram shows the standard manual
user-facing flow at a high level: the main commands, the main drift artifacts,
and the primary handoff points between them. If `drift-detect` produces a
fully resolved `spec.drift.md`, the workflow goes straight to reconcile;
otherwise it shows the manual resolve/alignment path in simplified form, with
`drift-implement` as a separate follow-up command before returning to
`drift-resolve`. A detailed resolve/alignment diagram appears later in this
file. The shared analyze review cycle used by both
`/speckit.canon.drift-analyze` and `/speckit.canon.vibecode-drift-analyze`
is shown later as a separate diagram. Orchestration-specific automatic
behavior is shown later in `Orchestration Commands`.

```mermaid
flowchart TD
    R["/speckit.canon.drift-implement"]
    TA["tasks.alignment.md"]
    A["Feature branch with code changes<br/>plus spec.md and tasks.md baseline"] --> B["/speckit.canon.drift-reverse"]
    B --> C["tasks.drift.md"]
    C --> D["/speckit.canon.drift-detect"]
    D --> E["spec.drift.md"]
    E --> E1{"Already resolved?"}
    E1 -- Yes --> J["/speckit.canon.drift-reconcile"]
    E1 -- No --> F["/speckit.canon.drift-resolve"]
    R --> F
    F --> H{"Items resolved?"}

    H -- No --> TA
    TA --> R
    H -- Yes --> J["/speckit.canon.drift-reconcile"]
    J --> K["canon.drift.md"]
    K --> L["/speckit.canon.drift-analyze"]
    L --> P["/speckit.canon.drift-canonize"]
    P --> S["Canon updated"]
    TA --- J

    classDef canonUpdated fill:#dcfce7,stroke:#166534,stroke-width:3px,color:#14532d
    class S canonUpdated
    linkStyle 16 stroke-opacity:0
```

## Vibecoding Code-First Workflow

This starts from the configured base branch, creates a feature branch and
feature directory, writes `vibecode.md`, and moves straight into coding.

```mermaid
flowchart TD
    A["Start on configured base branch"] --> B{"Input to<br/>/speckit.canon.vibecode-specify"}
    B -- "No arguments" --> C["Ad-hoc session<br/>slug = vibecode"]
    B -- "Single slug" --> D["Named session<br/>slug kept as-is"]
    B -- "Descriptive text" --> E["Intent-driven session<br/>slug derived from text"]

    C --> F["/speckit.canon.vibecode-specify"]
    D --> F
    E --> F

    F --> G["Create feature branch<br/>and feature directory"]
    G --> H["Write vibecode.md"]
    H --> I["Delete scaffolded spec.md"]
    I --> J["Implement immediately<br/>(spec-drift occurs here)"]
    J --> K["Enter vibecoding spec-drift workflow"]

    N1["Lightweight artifact only:<br/>intent, notes, optional mini-plan"]
    N2["No retained spec.md,<br/>plan.md, or tasks.md"]

    H -.-> N1
    N1 -.-> J
    I -.-> N2
    N2 -.-> J

    classDef driftRisk fill:#fef3c7,stroke:#b45309,stroke-width:3px,color:#78350f
    class J driftRisk
```

## Vibecoding Spec-Drift Workflow

This is the canon-sync path after a code-first session. There is no resolve
phase because vibecoding treats implementation as intentional by default. The
diagram stays mode-agnostic after analyze; orchestration-specific branching is
shown later in `Orchestration Commands`. The shared analyze review cycle is
shown later as a separate diagram.

```mermaid
flowchart TD
    A["Vibecoding feature branch<br/>with implementation changes"] --> B["/speckit.canon.vibecode-drift-reverse"]
    B --> C["tasks.drift.md<br/>all TD items = ADDED"]
    C --> D["/speckit.canon.vibecode-drift-detect"]
    D --> E["spec.drift.md<br/>all SD items = ACCEPTED<br/>Resolution Status = resolved"]
    E --> F["/speckit.canon.vibecode-drift-reconcile"]
    F --> G["canon.drift.md<br/>all CD items = ACCEPTED<br/>Status = draft"]
    G --> H["/speckit.canon.vibecode-drift-analyze"]
    H --> L["/speckit.canon.vibecode-drift-canonize"]
    L --> P["canon.drift.md<br/>all CD items = ACCEPTED<br/>Status = applied"]
    P --> Q["Canon updated"]

    M["No resolve step:<br/>implementation is treated as intentional truth"] -.-> E

    classDef canonUpdated fill:#dcfce7,stroke:#166534,stroke-width:3px,color:#14532d
    class Q canonUpdated
```

## Orchestration Commands

These are the two multi-step orchestrators. The standard drift orchestrator
owns both the resolve and analyze review steps directly; the vibecoding
orchestrator delegates reverse, detect, reconcile, and canonize but still runs
analyze directly before canonize. In both orchestrators, analyze stays
read-only and hands remediation items back to the orchestrator. This section
keeps the standard drift orchestrator intentionally high level; detailed manual
resolve and alignment follow-up behavior appears later in
`Drift-Resolve / Alignment Cycle`.

### `/speckit.canon.drift`

```mermaid
flowchart TD
    User["User"] --> S0["/speckit.canon.drift"]
    S0 --> S1["Delegate reverse"]
    S1 --> S2["Delegate detect"]
    S2 --> S3["Resolve directly<br/>in manual mode or<br/>automatic resolve as IMPL-ACCEPTED"]
    S3 --> S5["Delegate reconcile"]
    S5 --> S6["Analyze directly<br/>in manual mode or automatic remediate + re-analyze"]
    S6 --> S8["Delegate canonize"]
    S8 --> S9["Canon updated"]

    S3 -. resolve can pause<br/>for user decisions<br/>in manual mode .-> User
    S6 -. analyze can pause<br/>for user decisions<br/>in manual mode .-> User

    classDef canonUpdated fill:#dcfce7,stroke:#166534,stroke-width:3px,color:#14532d
    classDef reviewChoice fill:#dbeafe,stroke:#1d4ed8,stroke-width:3px,color:#1e3a8a
    class S9 canonUpdated
    class S3,S6 reviewChoice
```

In explicit automatic orchestration mode, the orchestrator does not run
`/speckit.canon.drift-resolve`. Instead, it traverses remaining
`UNRESOLVED` and `IMPL-REJECTED` items in `spec.drift.md`, resolves them as
`IMPL-ACCEPTED`, treats the observed implementation as authoritative truth,
and then proceeds directly to `/speckit.canon.drift-reconcile` once the drift
file is fully resolved.

In explicit automatic orchestration mode, analyze still runs as a direct
read-only review step, but the orchestrator handles the remediation follow-up
itself. If analyze reports remediation items, the orchestrator applies every
reported item to `canon.drift.md`, re-runs analyze once for verification, and
continues to canonize only if that verification pass is clean; otherwise it
stops and preserves the revised draft for manual review.

### `/speckit.canon.vibecode-drift`

```mermaid
flowchart TD
    User["User"] --> V0["/speckit.canon.vibecode-drift"]
    V0 --> V1["Delegate reverse"]
    V1 --> V2["Delegate detect"]
    V2 --> V3["Delegate reconcile"]
    V3 --> V4["Analyze directly<br/>in manual mode or automatic remediate + re-analyze"]
    V4 --> V6["Delegate canonize"]
    V6 --> V7["Canon updated"]

    V4 -. analyze can pause<br/>for user decisions<br/>in manual mode .-> User

    classDef canonUpdated fill:#dcfce7,stroke:#166534,stroke-width:3px,color:#14532d
    classDef reviewChoice fill:#dbeafe,stroke:#1d4ed8,stroke-width:3px,color:#1e3a8a
    class V7 canonUpdated
    class V4 reviewChoice
```

In explicit automatic orchestration mode, analyze still runs as a direct
read-only review step, but the orchestrator handles the remediation follow-up
itself. If analyze reports remediation items, the orchestrator applies every
reported item to `canon.drift.md`, re-runs analyze once for verification, and
continues to canonize only if that verification pass is clean; otherwise it
stops and preserves the revised draft for manual review.

## Express Vibecoding Spec-Drift

`/speckit.canon.vibecode-drift-express` is the low-ceremony single-invocation
path. It writes all drift artifacts, skips the separate draft canon analysis
pass, and asks only for final apply confirmation.

```mermaid
flowchart TD
    A["Run /speckit.canon.vibecode-drift-express"] --> B{"Existing drift<br/>artifacts found?"}
    B -- Yes --> Z1["Stop: existing drift artifacts<br/>must be reviewed or deleted first"]
    B -- No --> D["Reverse-engineer tasks<br/>write tasks.drift.md"]

    D --> E{"Tasks identified?"}
    E -- No --> Z2["Stop: no implementation changes detected"]
    E -- Yes --> F["Write spec.drift.md<br/>all items ACCEPTED"]

    F --> G{"Spec-level drift<br/>findings detected?"}
    G -- No --> Z3["Stop: no spec-level drift above canon level"]
    G -- Yes --> H["Write canon.drift.md<br/>all entries ACCEPTED<br/>Status = draft"]

    H --> I{"Canon gaps found?"}
    I -- No --> Z4["Stop: all drift already reflected in canon"]
    I -- Yes --> O["Show canon apply summary"]

    O --> P{"Proceed with<br/>canon updates?"}
    P -- No --> Z5["Stop and preserve artifacts<br/>canon not modified"]
    P -- Yes --> Q["Apply canon changes<br/>update _toc.md if needed<br/>mark canon.drift.md as applied"]
    Q --> R["Canon updated"]

    classDef canonUpdated fill:#dcfce7,stroke:#166534,stroke-width:3px,color:#14532d
    class R canonUpdated
```

## Drift-Resolve / Alignment Cycle

This expands the manual black-box resolve step from the main standard
spec-drift diagram. It shows how `/speckit.canon.drift-resolve` walks
outstanding items, may fix implementation immediately, may defer work into
`tasks.alignment.md`, and then branches directly to the next command:
reconcile when everything is resolved, resolve again when unresolved
decisions remain, or implement when only alignment work remains. While
unchecked TA tasks remain, the alignment queue stays `pending` or
`in-progress`, so `drift-implement` loops on itself until the queue is fully
`implemented` and can be re-verified by `drift-resolve`.

```mermaid
flowchart TD
    A["spec.drift.md with outstanding<br/>UNRESOLVED or IMPL-REJECTED items"] --> B["/speckit.canon.drift-resolve"]
    B --> H["Walk items in file order"]
    H --> I{"Current item?"}
    I -- UNRESOLVED --> J["Ask [I]mplementation- or<br/>[S]pecification-authoritative"]
    J -- "[I]" --> K["Mark IMPL-ACCEPTED<br/>continue traversal"]
    J -- "[S]" --> L["Enter spec-authoritative flow"]
    I -- IMPL-REJECTED --> L

    L --> M{"Fix already observable<br/>in code?"}
    M -- Yes --> N["Mark SPEC-ACCEPTED<br/>continue traversal"]
    M -- No --> O{"Linked unchecked TA tasks<br/>already exist?"}
    O -- Yes --> P["Keep IMPL-REJECTED<br/>continue traversal"]
    O -- No --> Q["Ask [F]ix now or create<br/>alignment [T]ask"]
    Q -- "[F]" --> R["Edit code minimally<br/>mark SPEC-ACCEPTED<br/>continue traversal"]
    Q -- "[T]" --> S["Create or update tasks.alignment.md<br/>keep IMPL-REJECTED<br/>continue traversal"]

    K --> T{"Any UNRESOLVED or<br/>IMPL-REJECTED left after traversal?"}
    N --> T
    P --> T
    R --> T
    S --> T

    T -- "No items left" --> F["/speckit.canon.drift-reconcile"]
    T -- "Any UNRESOLVED remain" --> V["/speckit.canon.drift-resolve"]
    T -- "Only IMPL-REJECTED remain" --> W["/speckit.canon.drift-implement"]
    W --> X{"All remaining TA tasks<br/>completed?"}
    X -- No --> W
    X -- Yes --> V

    classDef reviewChoice fill:#dbeafe,stroke:#1d4ed8,stroke-width:3px,color:#1e3a8a
    class J,Q reviewChoice
```

## Shared Drift-Analyze Review Cycle

This expands the shared analyze review step used by both the standard
spec-drift and vibecoding spec-drift workflows. The logic is identical for
`/speckit.canon.drift-analyze` and `/speckit.canon.vibecode-drift-analyze`;
only the entrypoint and follow-up canonize command names differ.

```mermaid
flowchart TD
    A["canon.drift.md<br/>Status = draft"] --> B["Run shared analyze review<br/>/speckit.canon.drift-analyze or<br/>/speckit.canon.vibecode-drift-analyze"]
    B --> C{"Issues found?"}
    C -- No --> F["Run canonize<br/>/speckit.canon.drift-canonize or<br/>/speckit.canon.vibecode-drift-canonize"]
    C -- Yes --> D{"Review choice"}
    D -- "Remediate now" --> E["Update canon.drift.md<br/>in current context"]
    E -- "Re-run analyze" --> B
    D -- "Continue with <br/>current draft" --> F
    F --> G["canon.drift.md<br/>Status = applied"]

    classDef reviewChoice fill:#dbeafe,stroke:#1d4ed8,stroke-width:3px,color:#1e3a8a
    class D,E reviewChoice
```
