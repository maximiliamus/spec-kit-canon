# Spec Drift Report

**Branch**: `[branch]`
**Source Task Drift**: `[FEATURE_DIR]/tasks.drift.md`
**Spec Source**: `[FEATURE_DIR]/spec.md`
**Resolution Status**: `[classified|resolved]`

Use globally incrementing `D-XXX` identifiers across all sections. Every finding must reference its originating `TD-XXX` item.

## Undocumented Features

### D-001 - [undocumented feature title]
- Status: `ACCEPTED`
- Category: `Undocumented feature`
- Task Drift Ref: `TD-001`
- Spec Reference: `-`
- Implementation Evidence:
  - `[path/to/file]` - [observable behavior]
- Spec Expectation: [what spec.md currently says, or that it is silent]
- Observed Behavior: [what the implementation actually does]
- Canon Impact: [why this matters at canon level]

## Behavioral Deviations

### D-002 - [behavioral deviation title]
- Status: `IMPL-REJECTED|SPEC-REJECTED|ACCEPTED`
- Category: `Behavioral deviation`
- Task Drift Ref: `TD-002`
- Spec Reference: `[FEATURE_DIR]/spec.md § [section]`
- Implementation Evidence:
  - `[path/to/file]` - [observable behavior]
- Spec Expectation: [what spec.md requires]
- Observed Behavior: [what the implementation actually does]
- Canon Impact: [why the deviation matters for canon]

## New Entities Or Fields

### D-003 - [new entity or field title]
- Status: `ACCEPTED`
- Category: `New entity or field`
- Task Drift Ref: `TD-003`
- Spec Reference: `[FEATURE_DIR]/data-model.md § [section]` or `-`
- Implementation Evidence:
  - `[path/to/file]` - [new model, field, or data shape]
- Spec Expectation: [what the current spec or data model defines]
- Observed Behavior: [what new entity or field exists in implementation]
- Canon Impact: [why canon should capture it]

## Removed Or Skipped Requirements

### D-004 - [removed or skipped requirement title]
- Status: `IMPL-REJECTED|SPEC-REJECTED|REJECTED`
- Category: `Removed or skipped requirement`
- Task Drift Ref: `TD-004`
- Spec Reference: `[FEATURE_DIR]/spec.md § [section]`
- Implementation Evidence:
  - `[path/to/file]` - [absence, deletion, or contradictory behavior]
- Spec Expectation: [what spec.md still requires]
- Observed Behavior: [what is missing or no longer implemented]
- Canon Impact: [why this changes canon or why it is out of scope]

## Terminology Drift

### D-005 - [terminology drift title]
- Status: `ACCEPTED|IMPL-REJECTED|SPEC-REJECTED`
- Category: `Terminology drift`
- Task Drift Ref: `TD-005`
- Spec Reference: `[FEATURE_DIR]/spec.md § [section]`
- Implementation Evidence:
  - `[path/to/file]` - [current term in code]
- Spec Expectation: [term used in spec]
- Observed Behavior: [term used in implementation]
- Canon Impact: [why terminology alignment matters]

## Resolution

Include this section only when the file is fully resolved, or immediately for vibecode workflows that skip the resolve step.

| Drift ID | Task Drift Ref | Terminal Status | Resolution Action | Updated Spec / Code | Notes |
|----------|----------------|-----------------|-------------------|---------------------|-------|
| D-001 | TD-001 | ACCEPTED | Retain as authoritative behavior | `-` | No further action |
| D-002 | TD-002 | SPEC-ACCEPTED | Implementation corrected to match spec | `[path/to/file]` | Fixed in code |
| D-003 | TD-003 | IMPL-ACCEPTED | spec.md updated to match implementation | `[FEATURE_DIR]/spec.md § [section]` | Spec corrected |
| D-004 | TD-004 | REJECTED | Excluded from canon consideration | `-` | Below canon abstraction level |
